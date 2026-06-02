# backend/app/graph.py
import os
import sys
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node

def create_medical_graph():
    # 1. Construction du graphe
    workflow = StateGraph(MedicalState)

    workflow.add_node('supervisor', supervisor_node)
    workflow.add_node('diagnostic_agent', diagnostic_agent_node)
    workflow.add_node('physician_review', physician_review_node)
    workflow.add_node('report_agent', report_agent_node)

    workflow.set_entry_point('supervisor')

    workflow.add_conditional_edges(
        'supervisor',
        lambda state: state.get('next', 'diagnostic_agent'),
        {
            'diagnostic_agent': 'diagnostic_agent',
            'physician_review': 'physician_review',
            'report_agent': 'report_agent',
            'FINISH': END,
        }
    )

    workflow.add_edge('diagnostic_agent', 'supervisor')
    workflow.add_edge('physician_review', 'supervisor')
    workflow.add_edge('report_agent', 'supervisor')

    # 2. DÉTECTION ULTIME DU MODE STUDIO
    # On regarde si 'langgraph' est présent dans les modules chargés par Python
    # ou si les variables d'environnement du Studio sont là.
    is_studio = (
        any("langgraph_api" in m for m in sys.modules) or 
        any("langgraph_cli" in m for m in sys.modules) or
        os.getenv("LANGGRAPH_DEV") == "true" or
        os.getenv("LANGGRAPH_API_VERSION") is not None
    )

    if is_studio:
        print(">>> [DÉTECTION] MODE LANGGRAPH STUDIO : Désactivation du checkpointer")
        # Compilation SANS checkpointer (le Studio gère sa propre base de données)
        return workflow.compile(
            interrupt_before=['diagnostic_agent', 'physician_review']
        )
    else:
        print(">>> [DÉTECTION] MODE STANDARD (FastAPI/Test) : Activation du checkpointer")
        # Compilation AVEC checkpointer pour que l'API fonctionne
        return workflow.compile(
            checkpointer=InMemorySaver(),
            interrupt_before=['diagnostic_agent', 'physician_review']
        )

# Instance globale
medical_graph = create_medical_graph()