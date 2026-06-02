import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")

if key and key.startswith("sk-"):
    print(f"✅ Clé trouvée : {key[:10]}...")
else:
    print("❌ Clé non trouvée ! Vérifie l'emplacement du fichier .env")