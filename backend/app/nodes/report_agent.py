# backend/app/nodes/report_agent.py
# Agent rapport : génère le rapport final structuré.
# Rassemble toutes les informations de l'état partagé.

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from app.state import MedicalState
import os

load_dotenv(override=True)

llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.2, max_tokens=2000)


def report_agent_node(state: MedicalState) -> dict:
    """
    Agent rapport : génère le rapport final structuré.
    """
    diagnostic_summary = state.get('diagnostic_summary', 'Non disponible')
    interim_care = state.get('interim_care', 'Non disponible')
    physician_treatment = state.get('physician_treatment', 'Non disponible')
    patient_case = state.get('patient_case', 'Non spécifié')
    patient_answers = state.get('patient_answers', 'Non disponible')

    print('[REPORT] Génération du rapport final...')

    report_prompt = f"""
Génère un rapport médical final structuré basé sur les informations suivantes :

CAS INITIAL : {patient_case}
RÉPONSES PATIENT : {patient_answers}
SYNTHÈSE CLINIQUE PRÉLIMINAIRE : {diagnostic_summary}
RECOMMANDATION INTERMÉDIAIRE : {interim_care}
TRAITEMENT PROPOSÉ PAR LE MÉDECIN : {physician_treatment}

Format du rapport :
# RAPPORT D'ORIENTATION CLINIQUE PRÉLIMINAIRE
## 1. Résumé du cas
## 2. Synthèse clinique
## 3. Recommandations intermédiaires
## 4. Avis et traitement du médecin traitant
## 5. Conduite à tenir

⚠️ Ce système ne remplace pas une consultation médicale."""

    response = llm.invoke([HumanMessage(content=report_prompt)])
    final_report = response.content

    return {
        'final_report': final_report,
        'messages': [AIMessage(content=final_report)],
    }
