# backend/app/tools/patient_tools.py
# Tool pour poser des questions au patient et enregistrer ses réponses.


from langchain.tools import tool
from typing import Dict


# Liste des 5 questions médicales standard
QUESTIONS_MEDICALES = [
    "1. Quels sont vos symptômes principaux en ce moment ?",
    "2. Depuis combien de temps avez-vous ces symptômes ?",
    "3. Avez-vous de la fièvre ? Si oui, quelle température ?",
    "4. Avez-vous des antécédents médicaux ou des allergies connues ?",
    "5. Prenez-vous actuellement des médicaments ?"
]


@tool
def ask_patient(question_number: int) -> str:
    """
    Retourne la question médicale correspondant au numéro donné.
    question_number doit être entre 1 et 5.
    Ce tool est appelé par le DiagnosticAgent pour guider l'interrogatoire.
    """
    print(f'[TOOL] ask_patient appelé pour la question {question_number}')
    if 1 <= question_number <= 5:
        return QUESTIONS_MEDICALES[question_number - 1]
    return 'Toutes les questions ont été posées.'


@tool
def format_patient_qa(question: str, answer: str) -> str:
    """
    Formate une paire question/réponse pour le rapport.
    Retourne une chaîne formatée Q: ... / R: ...
    """
    return f'Q: {question}\nR: {answer}'
