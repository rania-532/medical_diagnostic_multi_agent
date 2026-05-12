# backend/app/tools/mcp_client.py
# Client MCP pour appeler l'outil du serveur MCP.

from langchain.tools import tool
import subprocess
import json


@tool
def search_symptom_mcp(symptom: str) -> str:
    """
    Recherche des informations sur un symptôme via le serveur MCP.
    Appelle le serveur MCP local pour obtenir des infos médicales basiques.
    """
    print(f'[MCP] Recherche du symptôme : {symptom}')
    # Dans un projet complet, on utiliserait le protocole MCP.
    # Pour la démo académique, on simule l'appel :
    symptom_db = {
        "fièvre": "Température > 38°C. Peut indiquer infection virale ou bactérienne.",
        "toux": "Irritation des voies respiratoires. Surveiller si productive.",
        "dyspnée": "Difficulté respiratoire. Consultation urgente recommandée.",
    }
    return symptom_db.get(symptom.lower(), f'Information non disponible pour : {symptom}')
