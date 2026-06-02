# backend/test_mcp_tool.py
from app.tools.mcp_client import search_symptom_mcp

def test_tool():
    print("--- Test de l'outil MCP (Simulation) ---")
    result = search_symptom_mcp.invoke({"symptom": "fièvre"})
    print(f"Résultat pour 'fièvre' : {result}")
    
    result_inconnu = search_symptom_mcp.invoke({"symptom": "licorne"})
    print(f"Résultat pour 'licorne' : {result_inconnu}")

if __name__ == "__main__":
    test_tool()