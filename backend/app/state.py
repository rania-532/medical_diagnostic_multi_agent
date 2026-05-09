# backend/app/state.py
# Ce fichier définit la structure de l'état partagé entre tous les agents.
# On utilise TypedDict 

from typing import Annotated, Optional
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    """
    État partagé du graphe médical.
    Chaque agent peut lire et modifier ces champs.
    total=False signifie que tous les champs sont optionnels au départ.
    """

    # Messages de la conversation (liste automatiquement gérée par add_messages)
    # add_messages est une fonction spéciale LangGraph qui accumule les messages
    # sans écraser les anciens 
    messages: Annotated[list, add_messages]

    # Décide quel agent appeler ensuite (géré par le Supervisor)
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]

    # Compte le nombre de questions posées au patient (max 5)
    question_count: int

    # Réponses du patient sous forme de texte
    patient_answers: str

    # Recommandation intermédiaire générée par l'agent diagnostic
    interim_care: str

    # Synthèse clinique produite après les 5 questions
    diagnostic_summary: str

    # Traitement proposé par le médecin traitant (Human-in-the-Loop)
    physician_treatment: str

    # Rapport final généré par le Report Agent
    final_report: str

    # Description initiale du cas patient
    patient_case: str
