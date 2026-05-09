# backend/app/nodes/physician_review.py
# Nœud Human-in-the-Loop : le workflow s'interrompt ici.
# Le médecin peut lire la synthèse et entrer son traitement.
# LangGraph reprend ensuite depuis ce point.

from app.state import MedicalState
from langchain_core.messages import AIMessage


def physician_review_node(state: MedicalState) -> dict:
    """
    Nœud de revue médicale (Human-in-the-Loop).
    Ce nœud est interrompu AVANT son exécution par LangGraph.
    Le médecin entre son traitement via l'API /consultation/resume.
    Quand le workflow reprend, physician_treatment est déjà dans l'état.
    """
    physician_treatment = state.get('physician_treatment', '')
    diagnostic_summary = state.get('diagnostic_summary', '')

    print('[PHYSICIAN] Revue médicale...')
    print(f'[PHYSICIAN] Synthèse : {diagnostic_summary[:100]}...')
    print(f'[PHYSICIAN] Traitement : {physician_treatment}')

    # Ce nœud est simple : il lit physician_treatment qui a été
    # injecté par l'API quand le médecin a soumis son avis.
    return {
        'messages': [AIMessage(content=f'Traitement médecin : {physician_treatment}')],
    }
