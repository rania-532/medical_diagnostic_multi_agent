# backend/app/graph.py
# Assemblage du graphe LangGraph complet.

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def create_medical_graph():
    """
    Crée et compile le graphe médical multi-agents.
    Retourne le graphe compilé avec checkpointer (pour Human-in-the-Loop).
    """

    # 1. Créer le graphe avec notre état partagé
    workflow = StateGraph(MedicalState)

    # 2. Ajouter tous les nœuds (agents)
    workflow.add_node('supervisor', supervisor_node)
    workflow.add_node('diagnostic_agent', diagnostic_agent_node)
    workflow.add_node('physician_review', physician_review_node)
    workflow.add_node('report_agent', report_agent_node)

    # 3. Point d'entrée du graphe
    workflow.set_entry_point('supervisor')

    # 4. Edges conditionnels depuis le supervisor
    # Le supervisor regarde state['next'] et route vers le bon agent
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

    # 5. Retour au supervisor après chaque agent
    workflow.add_edge('diagnostic_agent', 'supervisor')
    workflow.add_edge('physician_review', 'supervisor')
    workflow.add_edge('report_agent', 'supervisor')

    # 6. Checkpointer pour sauvegarder l'état (OBLIGATOIRE pour Human-in-the-Loop)
    checkpointer = InMemorySaver()

    # 7. Compiler avec interruption AVANT physician_review
    # C'est ici que LangGraph sait qu'il doit s'arrêter et attendre le médecin
    graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=['physician_review'],  # STOP ici pour le médecin
    )

    return graph


# Instance globale du graphe
medical_graph = create_medical_graph()
