import streamlit as st
import requests
import time

# URL de l'API backend
API_URL = 'http://localhost:8000'

# ─── Configuration de la page ───
st.set_page_config(
    page_title='ClinicalAI - Assistant',
    page_icon='🏥',
    layout='centered',
    initial_sidebar_state='expanded'
)

# ─── DESIGN & CSS PROFESSIONNEL ───
st.markdown("""
    <style>
    /* 1. VERROUILLAGE TOTAL DU SCROLL (SPA) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main .block-container {
        overflow: hidden !important;
        height: 100vh !important;
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }

    /* 2. THÈME DE COULEURS MÉDICALES */
    :root {
        --primary: #004e92;
        --secondary: #00b4d8;
        --bg: #ffffff;
    }

    /* 3. SIDEBAR PROFESSIONNELLE */
    [data-testid="stSidebarContent"] {
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 2rem;
        border-right: 1px solid #e0e0e0;
    }

    /* Avatar Doctoresse (Animation Style) */
    .doctor-avatar {
        width: 130px;
        margin-bottom: 15px;
    }

    /* Centrage du texte sidebar */
    .sidebar-text {
        text-align: center;
        color: #1c2e4a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 4. BOUTONS PROFESSIONNELS */
    .stButton>button {
        border-radius: 6px;
        background-color: #004e92;
        color: white;
        border: none;
        height: 3rem;
        font-weight: 500;
        transition: background 0.3s;
    }
    .stButton>button:hover {
        background-color: #003a6d;
    }

    /* 5. TITRES */
    h1 { color: #004e92; font-weight: 700 !important; }
    h3 { color: #1c2e4a; }

    /* 6. CHAT & CONTAINERS (Scroll interne seulement) */
    [data-testid="stExpander"], .stChatMessageContainer {
        border-radius: 10px;
    }
            






          
    </style>
    """, unsafe_allow_html=True)

# ─── Initialisation de session_state ───
if 'current_screen' not in st.session_state:
    st.session_state.update({
        'thread_id': None, 'current_screen': 'accueil',
        'question_count': 0, 'current_question': '',
        'diagnostic_summary': '', 'interim_care': '',
        'final_report': '', 'answers_given': [], 'patient_case': ''
    })

# ─── SIDEBAR FIXE ───
with st.sidebar:
    # Illustration Animée (Doctoresse)
    st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/3304/3304567.png" class="doctor-avatar">', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-text"><h3>Clinical AI</h3><p>Assistant d\'orientation</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Indicateur de progression épuré
    steps = {'accueil': 1, 'questions': 2, 'medecin': 3, 'rapport': 4}
    current_step = steps.get(st.session_state.current_screen, 1)
    st.write(f"Phase {current_step} sur 4")
    st.progress(current_step / 4)
    
    # Bouton Réinitialiser en bas
    for _ in range(10): st.sidebar.write("") # Espaceur
    if st.button('Réinitialiser la session'):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ─── ZONE PRINCIPALE (CONTENUS) ───
# On utilise un container pour chaque écran pour garder la structure SPA

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.current_screen == 'accueil':
    st.markdown("<h2 style='margin-top: -60px; margin-bottom: 10px; color: #004e92; font-weight: 700;'> Dossier Patient</h2>", unsafe_allow_html=True)
    st.markdown("##### Analyse initiale")
    
    case_input = st.text_area(
        "Description", 
        placeholder="Décrivez ici les symptômes majeurs et l'historique récent du patient...", 
        height=320,
        label_visibility="collapsed"
    )
    
    st.write("") # Petit espace
    
    if st.button('Démarrer l\'analyse clinique', type='primary', use_container_width=True):
        if not case_input.strip():
            # Notification épurée sans emoji manuel
            st.toast("Le champ de description est vide", icon="⚠️")
        else:
            msg_placeholder = st.empty()
            msg_placeholder.info("Initialisation de la session...")
            try:
                session_resp = requests.post(f'{API_URL}/sessions/start').json()
                st.session_state.thread_id = session_resp['thread_id']
                
                start_resp = requests.post(
                    f'{API_URL}/consultation/start',
                    json={'thread_id': st.session_state.thread_id, 'patient_case': case_input}
                ).json()
                
                st.session_state.patient_case = case_input
                st.session_state.question_count = start_resp.get('question_count', 0)
                st.session_state.current_question = start_resp.get('current_question', '')
                st.session_state.current_screen = 'questions'
                st.rerun()
            except:
                st.toast("Erreur de communication avec l'API", icon="🚨")




# --- ÉCRAN 2 : QUESTIONS ---
elif st.session_state.current_screen == 'questions':
    st.markdown("<h2 style='margin-top: -60px; margin-bottom: 10px; color: #004e92; font-weight: 700;'> Interrogatoire Patient</h2>", unsafe_allow_html=True)    
    # On ajuste la hauteur pour laisser de la place au bouton à la fin
    container_height = 400 if not st.session_state.diagnostic_summary else 400

    with st.container(height=container_height, border=True):
        st.caption(f"Cas : {st.session_state.patient_case[:80]}...")
        
        for qa in st.session_state.answers_given:
            with st.chat_message("assistant", avatar="👩‍⚕️"): st.write(qa['question'])
            with st.chat_message("user"): st.write(qa['answer'])
        
        # Si la synthèse est arrivée, on l'affiche directement dans le chat
        if st.session_state.diagnostic_summary:
            with st.chat_message("assistant", avatar="👩‍⚕️"):
                st.success("✅ Analyse terminée. Voici ma synthèse :")
                st.markdown(st.session_state.diagnostic_summary)
                st.info(f"💡 **Conseil :** {st.session_state.interim_care}")

        # Si on est encore en train de poser des questions
        elif st.session_state.question_count <= 5:
            with st.chat_message("assistant", avatar="👩‍⚕️"): 
                st.write(st.session_state.current_question)

    # Zone d'action en bas
    if not st.session_state.diagnostic_summary:
        # Input de chat classique tant qu'on n'a pas fini
        if answer := st.chat_input("Saisissez votre réponse..."):
            resp = requests.post(f'{API_URL}/consultation/answer', json={
                'thread_id': st.session_state.thread_id, 
                'question_number': st.session_state.question_count, 
                'answer': answer}).json()
            
            st.session_state.answers_given.append({'question': st.session_state.current_question, 'answer': answer})
            st.session_state.question_count = resp.get('question_count', 0)
            st.session_state.current_question = resp.get('current_question', '')
            st.session_state.diagnostic_summary = resp.get('diagnostic_summary', '')
            st.session_state.interim_care = resp.get('interim_care', '')
            st.rerun()
    else:
        # Si fini, on affiche le gros bouton pour passer à la phase suivante
        st.write("")
        if st.button('  Transmettre au médecin traitant pour validation', type='primary', use_container_width=True):
            st.session_state.current_screen = 'medecin'
            st.rerun()


# --- ÉCRAN 3 : REVUE MÉDECIN ---
elif st.session_state.current_screen == 'medecin':
    # On utilise un titre plus compact
    st.markdown("<h2 style='margin-top: -60px; margin-bottom: 10px; color: #004e92; font-weight: 700;'> Évaluation Médicale</h2>", unsafe_allow_html=True)    # On réduit la hauteur à 300 pour laisser de la place au bouton en bas
    with st.container(height=380, border=True):
        c1, c2 = st.columns(2)
        with c1: 
            st.markdown("**Synthèse clinique**")
            st.caption(st.session_state.diagnostic_summary)
        with c2: 
            st.markdown("**Conseils d'orientation**")
            st.caption(st.session_state.interim_care)
    
    # On réduit la hauteur du texte area de 120 à 90
    treatment = st.text_area(
        "Prescription finale", 
        placeholder="Traitement ou conduite à tenir...", 
        height=90,
        label_visibility="collapsed" # On cache le label pour gagner une ligne
    )
    
    # Le bouton sera maintenant bien plus haut
    if st.button('Valider et générer le rapport final', type='primary', use_container_width=True):
        if treatment:
            with st.spinner("Rédaction..."):
                resp = requests.post(f'{API_URL}/consultation/resume', json={
                    'thread_id': st.session_state.thread_id, 'physician_treatment': treatment}).json()
                st.session_state.final_report = resp.get('final_report', '')
                st.session_state.current_screen = 'rapport'
                st.rerun()
        else:
            st.toast("L'avis médical est requis", icon="⚠️")

# --- ÉCRAN 4 : RAPPORT FINAL ---
elif st.session_state.current_screen == 'rapport':
    st.markdown("<h2 style='margin-top: -60px; margin-bottom: 10px; color: #004e92; font-weight: 700;'> Rapport d'Orientation</h2>", unsafe_allow_html=True)    # Hauteur réduite à 350 pour laisser de la place au bouton
    with st.container(height=380, border=True):
        if st.session_state.final_report:
            st.markdown(st.session_state.final_report)
        else:
            st.warning("Le rapport n'a pas pu être récupéré.")

    st.write("") # Petit espace

    # BOUTON BIEN VISIBLE
    if st.button(' Nouvelle Consultation', type='primary', use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()