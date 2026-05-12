# backend/app/nodes/diagnostic_agent.py
# Agent diagnostic : pose 5 questions et produit une synthèse clinique.
# Utilise ChatOpenAI et les tools @tool 

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool
from dotenv import load_dotenv
from app.state import MedicalState
from app.tools.patient_tools import ask_patient, QUESTIONS_MEDICALES
from app.tools.care_tools import recommend_interim_care
import os

load_dotenv(override=True)

def get_llm():
    """Fonction pour récupérer le LLM avec la clé explicitement passée"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("ERREUR : La clé OPENAI_API_KEY est introuvable dans l'environnement !")
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        max_tokens=1000,
        openai_api_key=api_key # On la passe explicitement ici
    )


def diagnostic_agent_node(state: MedicalState) -> dict:
    """
    Agent diagnostic :
    - Récupère la prochaine question à poser
    - Si toutes les questions sont posées, génère la synthèse
    - Appelle le tool recommend_interim_care
    """
    question_count = state.get('question_count', 0)
    patient_answers = state.get('patient_answers', '')
    patient_case = state.get('patient_case', 'Cas non spécifié')
    messages = state.get('messages', [])


    # Si on n'a pas encore posé toutes les 5 questions
    if question_count < 5:

        print(f'[DIAGNOSTIC] Question {question_count + 1}/5')

        # Appel du tool ask_patient
        question = ask_patient.invoke({'question_number': question_count + 1})

        # Simulation : dans une vraie app, on attendrait la réponse du patient
        # Ici on stocke la question dans les messages pour que le frontend puisse la récupérer
        new_message = AIMessage(content=question)

        return {
            'messages': [new_message],
            'question_count': question_count + 1,
            'patient_answers': patient_answers,
        }

    # Toutes les questions ont été posées → synthèse
    print('[DIAGNOSTIC] Génération de la synthèse clinique...')

    synthesis_prompt = f"""
Tu es un assistant médical académique. Analyse les informations suivantes
et produis une synthèse clinique PRÉLIMINAIRE.

CAS INITIAL : {patient_case}

RÉPONSES DU PATIENT : {patient_answers}

Produis une synthèse structurée avec :
1. Symptômes identifiés
2. Durée et évolution
3. Facteurs de risque éventuels
4. Orientation clinique préliminaire (prudente)

IMPORTANT : Ce n'est pas un diagnostic définitif.
Ne remplace pas la consultation médicale."""

    # On appelle le LLM ici
    try:
        llm = get_llm() # On récupère le LLM tout de suite
        response = llm.invoke([HumanMessage(content=synthesis_prompt)])
        diagnostic_summary = response.content
    except Exception as e:
        print(f"❌ Erreur critique lors de l'appel OpenAI : {e}")
        raise e

    # Appel du tool recommend_interim_care
    interim = recommend_interim_care.invoke({'diagnostic_summary': diagnostic_summary})

    return {
        'diagnostic_summary': diagnostic_summary,
        'interim_care': interim,
        'messages': [AIMessage(content=f'Synthèse : {diagnostic_summary}')],
    }
