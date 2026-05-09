# backend/app/tools/care_tools.py
# Tool pour générer une recommandation intermédiaire prudente.
# IMPORTANT : Ce système ne remplace pas une consultation médicale.

from langchain.tools import tool


@tool
def recommend_interim_care(diagnostic_summary: str) -> str:
    """
    Génère une recommandation intermédiaire générale basée sur la synthèse.
    Cette recommandation est prudente et ne remplace pas l'avis médical.
    Recommandations possibles : repos, hydratation, surveillance, consultation urgente.
    """
    print('[TOOL] recommend_interim_care appelé')
    # Recommandation prudente par défaut
    care = (
        "RECOMMANDATIONS INTERMÉDIAIRES (préliminaires) :\n"
        "• Repos et hydratation adéquate.\n"
        "• Surveiller l'évolution des symptômes.\n"
        "• Consulter rapidement en cas d'aggravation.\n"
        "• Ces recommandations sont générales et ne remplacent pas un avis médical.\n"
        f"\nContexte analysé : {diagnostic_summary[:200]}..."
    )
    return care
