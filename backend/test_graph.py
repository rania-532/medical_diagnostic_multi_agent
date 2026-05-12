import os
from dotenv import load_dotenv

# 1. CHARGER LE ENV EN PREMIER, AVANT TOUT AUTRE IMPORT
load_dotenv(override=True)

import sys
sys.path.insert(0, 'app')

from app.graph import medical_graph

config = {'configurable': {'thread_id': 'test-001'}}
initial_state = {
    'patient_case': 'Le patient présente de la fièvre et de la toux depuis 3 jours.',
    'question_count': 0,
    'patient_answers': 'Fièvre 39, toux grasse, mal de gorge', # On simule des réponses pour passer l'étape 5
}

print('=== DÉMARRAGE DU WORKFLOW ===')
# On lance le workflow
result = medical_graph.invoke(initial_state, config=config)

print('--- RESULTATS ---')
if 'diagnostic_summary' in result:
    print('Synthèse réussie !')
    print('Next step:', result.get('next'))