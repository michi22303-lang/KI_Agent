import streamlit as st
from crewai import Agent, Task, Crew, LLM
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Strategie Präsentator", page_icon="🏢", layout="wide")

if "slides" not in st.session_state:
    st.session_state.slides = []
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte API Key hinterlegen.")
    st.stop()

st.title("🏢 KI-Strategie mit interaktiven Slides")

topic = st.text_input("Thema:", "KI im Handwerk 2026")

# Platzhalter für Live-Logs
log_area = st.empty()

# Funktion, um Agenten-Aktivität live anzuzeigen
def step_callback(step_output):
    log_area.info(f"🕵️ Agent arbeitet gerade: {step_output.agent}\n\n Gedanken: {step_output.thought[:200]}...")

if st.button("Analyse & Präsentation starten"):
    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.4)
    
    # Status-Monitor
    status_cols = st.columns(3)
    s1, s2, s3 = status_cols[0].empty(), status_cols[1].empty(), status_cols[2].empty()
    s1.info("⚪ Analyst"); s2.info("⚪ Stratege"); s3.info("⚪ Marketing")

    analyst = Agent(role='Analyst', goal='Fakten finden.', backstory="IT-Experte.", llm=gemini_llm, step_callback=step_callback)
    strategist = Agent(role='Stratege', goal='ROI planen.', backstory="Business-Experte.", llm=gemini_llm, step_callback=step_callback)
    marketing = Agent(role='Marketing', goal='Erstelle 6 Slides. Trenne JEDE Slide mit dem Wort: NEUESLIDE', backstory="Präsentations-Profi.", llm=gemini_llm, step_callback=step_callback)

    t1 = Task(description=f"Technik {topic}", agent=analyst, expected_output="Analyse.")
    t2 = Task(description=f"Business {topic}", agent=strategist, expected_output="Roadmap.")
    t3 = Task(description=f"Erstelle 6 Slides für {topic}. WICHTIG: Nutze zwischen den Slides das Trennwort NEUESLIDE.", agent=marketing, expected_output="Slide-Texte.")

    crew = Crew(agents=[analyst, strategist, marketing], tasks=[t1, t2, t3], max_rpm=1)
    
    s1.warning("🔵 Analyst (Aktiv)")
    result = str(crew.kickoff())
    s1.success("✅ Analyst"); s2.success("✅ Stratege"); s3.success("✅ Marketing")
    
    # Slides verarbeiten
    raw_slides = result.split("NEUESLIDE")
    st.session_state.slides = [s.strip() for s in raw_slides if len(s.strip()) > 10]
    st.session_state.current_slide = 0
    st.success("Präsentation bereit!")

# --- Präsentations-Modus ---
if st.session_state.slides:
    st.divider()
    st.subheader("🖥️ Interaktive Präsentation")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 4, 1])
    
    if col1.button("⬅️ Zurück") and st.session_state.current_slide > 0:
        st.session_state.current_slide -= 1
        
    if col3.button("Vorwärts ➡️") and st.session_state.current_slide < len(st.session_state.slides) - 1:
        st.session_state.current_slide += 1

    # Slide-Anzeige in einer schicken Box
    with col2:
        current = st.session_state.slides[st.session_state.current_slide]
        st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #007bff; min-height: 300px;">
                <h4 style="color: #31333F;">Folie {st.session_state.current_slide + 1} von {len(st.session_state.slides)}</h4>
                <hr>
                {current}
            </div>
        """, unsafe_allow_html=True)
        
    # Download für den gesamten Text
    st.download_button("Gesamtes Dossier speichern", "\n\n---\n\n".join(st.session_state.slides), file_name="Praesentation.md")
