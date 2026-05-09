# backend/app/nodes/supervisor.py
# Le Supervisor orchestre le workflow.
# Il décide quel agent appeler en fonction de l'état actuel.


from app.state import MedicalState


def supervisor_node(state: MedicalState) -> dict:
    """
    Superviseur du workflow médical.
    Logique de routage :
    1. Si pas encore de synthèse → envoyer vers diagnostic_agent
    2. Si synthèse présente mais pas de traitement médecin → physician_review
    3. Si traitement médecin présent → report_agent
    4. Si rapport final présent → FINISH
    """
    print('[SUPERVISOR] Évaluation de l\'état courant...')

    diagnostic_summary = state.get('diagnostic_summary', '')
    physician_treatment = state.get('physician_treatment', '')
    final_report = state.get('final_report', '')

    if final_report:
        print('[SUPERVISOR] → FINISH')
        return {'next': 'FINISH'}

    if physician_treatment and not final_report:
        print('[SUPERVISOR] → report_agent')
        return {'next': 'report_agent'}

    if diagnostic_summary and not physician_treatment:
        print('[SUPERVISOR] → physician_review')
        return {'next': 'physician_review'}

    print('[SUPERVISOR] → diagnostic_agent')
    return {'next': 'diagnostic_agent'}
