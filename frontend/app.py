# frontend/app.py
# Interface Streamlit pour le système diagnostic médical.
# 4 écrans : cas initial, questions/réponses, revue médecin, rapport final.

import streamlit as st
import requests
import time

# URL de l'API backend
API_URL = 'http://localhost:8000'


# ─── Configuration de la page ───
st.set_page_config(
    page_title='Diagnostic Médical — Système Multi-Agents',
    page_icon='🏥',
    layout='wide'
)


# ─── Initialisation de session_state ───
# session_state garde les données entre les interactions Streamlit
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'accueil'
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = ''
if 'diagnostic_summary' not in st.session_state:
    st.session_state.diagnostic_summary = ''
if 'interim_care' not in st.session_state:
    st.session_state.interim_care = ''
if 'final_report' not in st.session_state:
    st.session_state.final_report = ''
if 'answers_given' not in st.session_state:
    st.session_state.answers_given = []


# ─── Sidebar (navigation) ───
with st.sidebar:
    st.image('https://img.icons8.com/color/96/medical-doctor.png', width=80)
    st.title('🏥 Diagnostic Médical')
    st.markdown('**Système multi-agents académique**')
    st.divider()
    st.caption('⚠️ Ce système ne remplace pas une consultation médicale.')
    st.divider()

    # Indicateur d'étape
    steps = {
        'accueil': '1️⃣ Saisie du cas',
        'questions': '2️⃣ Questions patient',
        'medecin': '3️⃣ Revue médecin',
        'rapport': '4️⃣ Rapport final',
    }
    for key, label in steps.items():
        if st.session_state.current_screen == key:
            st.markdown(f'**→ {label}**')
        else:
            st.markdown(f'   {label}')


# ─── ÉCRAN 1 : Saisie du cas initial ───
if st.session_state.current_screen == 'accueil':
    st.title('🏥 Système de Diagnostic Médical Multi-Agents')
    st.markdown('### Écran 1 — Saisie du cas patient')
    st.info('Décrivez le cas patient initial. Le système posera ensuite 5 questions pour affiner l\'orientation clinique.')

    patient_case = st.text_area(
        'Description du cas patient :',
        placeholder='Ex: Patient de 45 ans présentant de la fièvre et une toux sèche depuis 3 jours...',
        height=200
    )

    if st.button('🚀 Démarrer la consultation', type='primary', use_container_width=True):
        if not patient_case.strip():
            st.error('Veuillez décrire le cas patient avant de démarrer.')
        else:
            with st.spinner('Démarrage de la consultation...'):
                try:
                    # Créer une session
                    session_resp = requests.post(f'{API_URL}/sessions/start').json()
                    st.session_state.thread_id = session_resp['thread_id']

                    # Démarrer le workflow
                    start_resp = requests.post(
                        f'{API_URL}/consultation/start',
                        json={
                            'thread_id': st.session_state.thread_id,
                            'patient_case': patient_case,
                        }
                    ).json()

                    st.session_state.question_count = start_resp.get('question_count', 0)
                    st.session_state.current_question = start_resp.get('current_question', '')
                    st.session_state.current_screen = 'questions'
                    st.rerun()

                except Exception as e:
                    st.error(f'Erreur de connexion à l\'API : {e}')
                    st.info('Vérifie que le backend tourne sur http://localhost:8000')


# ─── ÉCRAN 2 : Questions/Réponses patient ───
elif st.session_state.current_screen == 'questions':
    st.title('💬 Questions de l\'Agent Diagnostic')
    st.markdown('### Écran 2 — Interrogatoire patient')
    st.progress(st.session_state.question_count / 5, text=f'Question {st.session_state.question_count}/5')

    # Afficher les réponses précédentes
    if st.session_state.answers_given:
        with st.expander('📋 Réponses précédentes', expanded=False):
            for i, qa in enumerate(st.session_state.answers_given):
                st.markdown(f'**Q{i+1}:** {qa["question"]}')
                st.markdown(f'*R:* {qa["answer"]}')
                st.divider()

    # Si toutes les questions sont posées
    if st.session_state.question_count >= 5 and st.session_state.diagnostic_summary:
        st.success('✅ Toutes les questions ont été posées !')
        st.markdown('### 🔬 Synthèse clinique préliminaire')
        st.markdown(st.session_state.diagnostic_summary)
        st.markdown('### 💊 Recommandations intermédiaires')
        st.info(st.session_state.interim_care)
        st.caption('⚠️ Ces recommandations sont générales et ne remplacent pas un avis médical.')

        if st.button('➡️ Envoyer au médecin traitant', type='primary', use_container_width=True):
            st.session_state.current_screen = 'medecin'
            st.rerun()

    else:
        # Afficher la question courante
        st.markdown(f'### Question {st.session_state.question_count} :')
        st.markdown(f'**{st.session_state.current_question}**')

        patient_answer = st.text_area(
            'Votre réponse :',
            placeholder='Décrivez vos symptômes...',
            height=100,
            key=f'answer_{st.session_state.question_count}'
        )

        if st.button('✅ Soumettre la réponse', type='primary', use_container_width=True):
            if not patient_answer.strip():
                st.warning('Veuillez entrer une réponse.')
            else:
                with st.spinner('Traitement en cours...'):
                    try:
                        resp = requests.post(
                            f'{API_URL}/consultation/answer',
                            json={
                                'thread_id': st.session_state.thread_id,
                                'question_number': st.session_state.question_count,
                                'answer': patient_answer,
                            }
                        ).json()

                        # Sauvegarder la réponse
                        st.session_state.answers_given.append({
                            'question': st.session_state.current_question,
                            'answer': patient_answer,
                        })

                        st.session_state.question_count = resp.get('question_count', 0)
                        st.session_state.current_question = resp.get('current_question', '')
                        st.session_state.diagnostic_summary = resp.get('diagnostic_summary', '')
                        st.session_state.interim_care = resp.get('interim_care', '')
                        st.rerun()

                    except Exception as e:
                        st.error(f'Erreur : {e}')


# ─── ÉCRAN 3 : Revue médecin ───
elif st.session_state.current_screen == 'medecin':
    st.title('👨‍⚕️ Revue du Médecin Traitant')
    st.markdown('### Écran 3 — Human-in-the-Loop')
    st.warning('⏸️ Le workflow est en attente de l\'avis du médecin traitant.')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### 🔬 Synthèse clinique préliminaire')
        st.markdown(st.session_state.diagnostic_summary)
    with col2:
        st.markdown('#### 💊 Recommandations intermédiaires')
        st.info(st.session_state.interim_care)

    st.divider()
    st.markdown('#### ✍️ Traitement et conduite à tenir proposés par le médecin')

    physician_treatment = st.text_area(
        'Traitement médical et conduite à tenir :',
        placeholder='Ex: Antibiothérapie adaptée, repos 5 jours, réévaluation si aggravation...',
        height=200
    )

    if st.button('✅ Valider et générer le rapport final', type='primary', use_container_width=True):
        if not physician_treatment.strip():
            st.error('Veuillez entrer le traitement proposé.')
        else:
            with st.spinner('Génération du rapport final...'):
                try:
                    resp = requests.post(
                        f'{API_URL}/consultation/resume',
                        json={
                            'thread_id': st.session_state.thread_id,
                            'physician_treatment': physician_treatment,
                        }
                    ).json()

                    st.session_state.final_report = resp.get('final_report', '')
                    st.session_state.current_screen = 'rapport'
                    st.rerun()

                except Exception as e:
                    st.error(f'Erreur : {e}')


# ─── ÉCRAN 4 : Rapport final ───
elif st.session_state.current_screen == 'rapport':
    st.title('📄 Rapport Final')
    st.markdown('### Écran 4 — Rapport d\'orientation clinique')
    st.success('✅ Consultation terminée ! Voici le rapport final.')

    st.markdown(st.session_state.final_report)
    st.divider()
    st.error('⚠️ Ce système ne remplace pas une consultation médicale.')

    if st.button('🔄 Nouvelle consultation', use_container_width=True):
        # Réinitialise tout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
