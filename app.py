import streamlit as st
from crewai import Agent, Task, Crew, LLM
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Strategie Facility Management", page_icon="🏢", layout="wide")

# Session State für Slides initialisieren
if "slides" not in st.session_state:
    st.session_state.slides = []
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte API Key in den Streamlit Secrets hinterlegen.")
    st.stop()

st.title("🏢 Strategie-Team: Facility Management Digitalisierung")

topic = st.text_input("Thema:", "KI-gestützte Gebäudeinstandhaltung 2026")

# Platzhalter für Live-Logs
log_area = st.empty()

# REPARIERTE CALLBACK FUNKTION
def step_callback(step_output):
    try:
        thought = "Analysiere nächsten Schritt..."
        if hasattr(step_output, 'thought'):
            thought = step_output.thought
        elif isinstance(step_output, dict) and 'thought' in step_output:
            thought = step_output['thought']
        log_area.info(f"🕵️ **Ein Agent ist aktiv...**\n\n*Gedanken:* {thought[:250]}...")
    except Exception:
        log_area.info("🕵️ Ein Agent plant den nächsten Schritt...")

if st.button("Analyse & Präsentation starten"):
    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.4)
    
    # Status-Monitor (jetzt 4 Spalten)
    status_cols = st.columns(4)
    s1, s2, s3, s4 = status_cols[0].empty(), status_cols[1].empty(), status_cols[2].empty(), status_cols[3].empty()
    s1.info("⚪ Analyst"); s2.info("⚪ Stratege"); s3.info("⚪ Marketing"); s4.info("⚪ Abteilungsleiter")

    # Agenten Definition
    analyst = Agent(role='Analyst', goal='Technische Fakten finden.', backstory="IT-Experte.", llm=gemini_llm, step_callback=step_callback, verbose=True)
    strategist = Agent(role='Stratege', goal='ROI planen.', backstory="Business-Experte.", llm=gemini_llm, step_callback=step_callback, verbose=True)
    marketing = Agent(role='Marketing', goal='Erstelle 6 Slides. Trenne JEDE Slide exakt mit dem Wort: NEUESLIDE', backstory="Präsentations-Profi.", llm=gemini_llm, step_callback=step_callback, verbose=True)
    
    # Der 4. Agent: Leiter Digitalisierung
    head_of_digital = Agent(
        role='Leiter Digitalisierungsabteilung', 
        goal='Prüfe die Ergebnisse auf Relevanz für das Facility Management und gib ein finales Statement ab.', 
        backstory="Du hast den Blick auf das gesamte Facility Management Unternehmen. Du stellst sicher, dass die Lösung operativ umsetzbar ist und schließt die Präsentation mit einem starken Fazit ab.", 
        llm=gemini_llm, 
        step_callback=step_callback, 
        verbose=True
    )

    t1 = Task(description=f"Technik-Analyse für {topic}", agent=analyst, expected_output="Analyse.")
    t2 = Task(description=f"Business-Strategie für {topic}", agent=strategist, expected_output="Roadmap.")
    t3 = Task(description=f"Erstelle 6 Slides für {topic}. Nutze das Trennwort NEUESLIDE zwischen den Slides.", agent=marketing, expected_output="Slide-Texte.")
    
    # Task für den Leiter
    t4 = Task(description=f"Erstelle ein finales Management-Statement (ca. 150 Wörter) aus Sicht des Facility Managements als letzte Slide. Nutze davor das Wort NEUESLIDE.", agent=head_of_digital, expected_output="Finales Statement.")

    crew = Crew(agents=[analyst, strategist, marketing, head_of_digital], tasks=[t1, t2, t3, t4], max_rpm=1)
    
    s1.warning("🔵 Aktiv...")
    with st.spinner("Das Team berät sich..."):
        result = str(crew.kickoff())
        
    s1.success("✅ Erledigt"); s2.success("✅ Erledigt"); s3.success("✅ Erledigt"); s4.success("✅ Erledigt")
    
    # Slides verarbeiten
    raw_slides = result.split("NEUESLIDE")
    st.session_state.slides = [s.strip() for s in raw_slides if len(s.strip()) > 10]
    st.session_state.current_slide = 0
    st.success("Dossier & Statement bereit!")
    log_area.empty()

# --- INTERAKTIVE SLIDE-SHOW ---
if st.session_state.slides:
    st.divider()
    
    col_nav1, col_slide, col_nav2 = st.columns([1, 4, 1])
    
    if col_nav1.button("⬅️ Zurück"):
        if st.session_state.current_slide > 0:
            st.session_state.current_slide -= 1
            st.rerun()
        
    if col_nav2.button("Vorwärts ➡️"):
        if st.session_state.current_slide < len(st.session_state.slides) - 1:
            st.session_state.current_slide += 1
            st.rerun()

    with col_slide:
        current = st.session_state.slides[st.session_state.current_slide]
        # Kennzeichnung für die letzte Slide (Statement des Leiters)
        is_last = st.session_state.current_slide == len(st.session_state.slides) - 1
        title = "Statement: Leiter Digitalisierung" if is_last else f"Folie {st.session_state.current_slide + 1}"
        
        st.markdown(f"""
            <div style="background-color: #f8f9fb; padding: 40px; border-radius: 20px; border-top: 10px solid {'#28a745' if is_last else '#007bff'}; min-height: 350px; color: #1a1a1a;">
                <h3 style="color: #333;">{title}</h3>
                <hr>
                <div style="font-family: sans-serif; font-size: 1.1em;">
                    {current}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.download_button("Strategie-Dossier speichern", "\n\n---\n\n".join(st.session_state.slides), file_name="FM_Strategie_2026.md")
