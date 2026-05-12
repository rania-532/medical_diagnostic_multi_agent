# mcp_server/server.py
# Serveur MCP minimal exposant un outil de recherche de symptômes.
# Ce serveur tourne séparément du backend principal.

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

# Base de données de symptômes (simplifiée pour le projet)
SYMPTOM_DATABASE = {
    "fièvre": "Température > 38°C. Peut indiquer infection virale ou bactérienne.",
    "toux": "Irritation des voies respiratoires. Surveiller si productive ou sèche.",
    "dyspnée": "Difficulté respiratoire. Consultation urgente recommandée.",
    "céphalée": "Maux de tête. Évaluer intensité et localisation.",
    "nausée": "Trouble digestif. Surveillance de l'hydratation nécessaire.",
    "douleur thoracique": "ALERTE : Consultation immédiate recommandée.",
}

app = Server('medical-symptom-server')


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name='search_symptom',
            description='Recherche des informations sur un symptôme médical.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'symptom': {'type': 'string', 'description': 'Le symptôme à rechercher'},
                },
                'required': ['symptom']
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == 'search_symptom':
        symptom = arguments.get('symptom', '').lower()
        result = SYMPTOM_DATABASE.get(symptom, f'Symptôme "{symptom}" non trouvé dans la base.')
        return [TextContent(type='text', text=result)]
    return [TextContent(type='text', text='Outil inconnu')]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
