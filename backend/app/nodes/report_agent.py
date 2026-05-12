from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from app.state import MedicalState
import os

load_dotenv(override=True)

def report_agent_node(state: MedicalState) -> dict:
    # On crée le LLM à l'intérieur de la fonction pour être sûr que la clé est chargée
    llm = ChatOpenAI(
        model='gpt-3.5-turbo', 
        temperature=0.2, 
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    diagnostic_summary = state.get('diagnostic_summary', 'Non disponible')
    interim_care = state.get('interim_care', 'Non disponible')
    physician_treatment = state.get('physician_treatment', 'Non disponible')
    patient_case = state.get('patient_case', 'Non spécifié')
    patient_answers = state.get('patient_answers', 'Non disponible')

    print('[REPORT] Génération du rapport final...')

    report_prompt = f"Génère un rapport médical final basé sur : {patient_case}, {patient_answers}, {diagnostic_summary}, {physician_treatment}"

    response = llm.invoke([HumanMessage(content=report_prompt)])
    return {
        'final_report': response.content,
        'messages': [AIMessage(content=response.content)],
    }