# backend/app/api.py
# API FastAPI exposant le graphe LangGraph.
# Tous les endpoints demandés par le prof.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid

from app.graph import medical_graph

# Initialisation FastAPI
app = FastAPI(
    title="Système Diagnostic Médical Multi-Agents",
    description="API LangGraph pour l'orientation clinique preliminaire.",
    version="1.0.0"
)

# CORS pour permettre au frontend Streamlit d'accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# ─── Modèles Pydantic ───
class SessionResponse(BaseModel):
    thread_id: str
    message: str

class ConsultationStartRequest(BaseModel):
    thread_id: str
    patient_case: str

class PatientAnswerRequest(BaseModel):
    thread_id: str
    question_number: int
    answer: str

class PhysicianResumeRequest(BaseModel):
    thread_id: str
    physician_treatment: str


# ─── Endpoints ───

@app.post('/sessions/start', response_model=SessionResponse)
async def start_session():
    """Crée un nouveau thread de consultation."""
    thread_id = str(uuid.uuid4())
    return SessionResponse(thread_id=thread_id, message='Session créée avec succès.')


@app.post('/consultation/start')
async def start_consultation(request: ConsultationStartRequest):
    """Démarre le workflow avec le cas patient initial."""
    config = {'configurable': {'thread_id': request.thread_id}}
    initial_state = {
        'patient_case': request.patient_case,
        'question_count': 0,
        'patient_answers': '',
        'messages': [],
    }
    try:
        # 1. On initialise l'état (s'arrête AVANT diagnostic_agent à cause de l'interrupt)
        medical_graph.invoke(initial_state, config=config)
        
        # 2. On relance immédiatement pour exécuter le DiagnosticAgent et générer la Q1
        medical_graph.invoke(None, config=config)
        
        # 3. On récupère l'état mis à jour pour lire la question
        current_state = medical_graph.get_state(config)
        values = current_state.values
        
        # On récupère le contenu du dernier message (qui est la Question 1)
        messages = values.get('messages', [])
        question_text = messages[-1].content if messages else "Pas de question générée"

        return {
            'status': 'running',
            'thread_id': request.thread_id,
            'question_count': values.get('question_count', 0),
            'current_question': question_text,
            'next': values.get('next', ''),
        }
    except Exception as e:
        print(f"Erreur lors du démarrage : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/consultation/answer')
async def submit_answer(request: PatientAnswerRequest):
    """Soumet la réponse du patient à une question."""
    config = {'configurable': {'thread_id': request.thread_id}}
    current_state = medical_graph.get_state(config)

    patient_answers = current_state.values.get('patient_answers', '')
    question = f'Q{request.question_number}'
    updated_answers = patient_answers + f'\n{question}: {request.answer}'

    medical_graph.update_state(config, {'patient_answers': updated_answers})
    new_state = medical_graph.invoke(None, config=config)

    return {
        'thread_id': request.thread_id,
        'question_count': new_state.get('question_count', 0),
        'current_question': new_state.get('messages', [{}])[-1].content if new_state.get('messages') else '',
        'diagnostic_summary': new_state.get('diagnostic_summary', ''),
        'interim_care': new_state.get('interim_care', ''),
        'next': new_state.get('next', ''),
    }


@app.post('/consultation/resume')
async def resume_consultation(request: PhysicianResumeRequest):
    """Reprend le workflow après la revue du médecin."""
    config = {'configurable': {'thread_id': request.thread_id}}
    medical_graph.update_state(config, {'physician_treatment': request.physician_treatment})
    final_state = medical_graph.invoke(None, config=config)

    return {
        'thread_id': request.thread_id,
        'status': 'completed',
        'final_report': final_state.get('final_report', ''),
    }


@app.get('/consultation/{thread_id}')
async def get_consultation(thread_id: str):
    # Recupere l'etat actuel de la consultation.
    config = {'configurable': {'thread_id': thread_id}}
    try:
        state = medical_graph.get_state(config)
        return {
            'thread_id': thread_id,
            'state': dict(state.values),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail='Thread non trouvé')


@app.get('/consultation/{thread_id}/report')
async def get_report(thread_id: str):
    # Recupere le rapport final de la consultation.
    config = {'configurable': {'thread_id': thread_id}}
    try:
        state = medical_graph.get_state(config)
        report = state.values.get('final_report', '')
        if not report:
            raise HTTPException(status_code=404, detail='Rapport non encore généré')
        return {'thread_id': thread_id, 'final_report': report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
