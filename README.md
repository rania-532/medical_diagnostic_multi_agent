# Système Multi-Agents de Diagnostic Médical

## Description du Projet
Ce projet académique présente un système multi-agents conçu pour simuler un workflow d'orientation clinique préliminaire. Basé sur l'architecture LangGraph, le système orchestre plusieurs agents spécialisés pour collecter les symptômes du patient, analyser les données cliniques et intégrer une validation humaine obligatoire.

## Architecture du Système
L'application repose sur une architecture découplée comprenant :
- **Moteur de Workflow** : LangGraph pour la gestion de l'état (StateGraph) et le routage entre agents.
- **Agent Superviseur** : Orchestration centrale des transitions selon l'état de la consultation.
- **Agent de Diagnostic** : Collecte itérative de données (5 questions ciblées) et génération de synthèse.
- **Intervention Humaine (Human-in-the-Loop)** : Point d'arrêt bloquant pour la revue et la prescription du médecin.
- **Intégration MCP (Model Context Protocol)** : Accès à une base de connaissances de symptômes via un serveur externe.
- **Interface API** : FastAPI pour l'exposition des services.
- **Interface Utilisateur** : Streamlit pour la démonstration clinique.

## Technologies Utilisées
- Langage : Python 3.11 / 3.12
- Frameworks IA : LangChain, LangGraph
- Modèles : OpenAI GPT-3.5-turbo / GPT-4o
- Protocoles : MCP (Model Context Protocol)
- Serveur API : Uvicorn / FastAPI
- Gestionnaire de paquets : uv

## Procédure d'Installation
1. Cloner le dépôt :
   git clone https://github.com/[USERNAME]/medical_diagnostic.git
   cd medical_diagnostic

2. Configurer l'environnement :
   uv venv
   source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate
   uv pip install -r backend/requirements.txt

3. Configuration des variables d'environnement :
   Créer un fichier .env dans le répertoire backend/ contenant :
   OPENAI_API_KEY=votre_cle_api

## Instructions d'Exécution
1. Lancer le serveur Backend :
   cd backend && uv run uvicorn app.api:app --reload

2. Lancer l'interface Frontend :
   cd frontend && uv run streamlit run app.py

## Avertissement Légal
Ce système est un prototype académique à but éducatif. Il ne constitue pas un dispositif médical et ne remplace en aucun cas une consultation, un diagnostic ou un avis médical professionnel.