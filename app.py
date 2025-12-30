import streamlit as st
from crewai import Agent, Task, Crew, LLM
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="FM Strategie-Dossier", page_icon="🏢", layout="wide")

if "full_report" not in st.session_state:
    st.session_state.full_report = ""
if "slides" not in st.session_state:
    st.session_state.slides = []
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte API Key in den Streamlit Secrets hinterlegen.")
    st.stop()

st.title("🏢 FM Digital-Strategie & Management-Dossier")

topic = st.text_input("Digitalisierungsthema für Facility Management:", "Smart Building IoT & Predictive Maintenance")

log_area = st.empty()

def step_callback(step_output):
    try:
        thought = "Verarbeite Daten..."
        if hasattr(step_output, 'thought'):
            thought = step_output.thought
        elif isinstance(step_output, dict) and 'thought' in step_output:
            thought = step_output['thought']
        log_area.info(f"🕵️ **Agenten-Status:** {thought[:200]}...")
    except:
        log_area.info("🕵️ Ein Agent plant den nächsten Schritt...")

if st.button("Umfassende Analyse starten"):
    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.3)
    
    # Status-Monitor
    status_cols = st.columns(4)
    s1, s2, s3, s4 = [c.empty() for c in status_cols]
    s1.info("⚪ Technik"); s2.info("⚪ Strategie"); s3.info("⚪ Marketing"); s4.info("⚪ Leitung")

    # Agenten
    analyst = Agent(role='Analyst', goal='Technische Fakten finden.', backstory="IT-Experte für FM-Systeme.", llm=gemini_llm, step_callback=step_callback)
    strategist = Agent(role='Stratege', goal='ROI und Roadmap planen.', backstory="Experte für FM-Business.", llm=gemini_llm, step_callback=step_callback)
    marketing = Agent(role='Marketing', goal='Erstelle Slides und formuliere das Dossier aus.', backstory="Profi für Management-Präsentationen.", llm=gemini_llm, step_callback=step_callback)
    head_of_digital = Agent(role='Leiter Digitalisierung', goal='Finales Statement zur FM-Relevanz abgeben.', backstory="Entscheidungsträger im Facility Management.", llm=gemini_llm, step_callback=step_callback)

    # Tasks
    t1 = Task(description=f"Detaillierte Analyse zu {topic}.", agent=analyst, expected_output="Technische Analyse.")
    t2 = Task(description=f"ROI-Roadmap für {topic}.", agent=strategist, expected_output="Strategie-Roadmap.")
    t3 = Task(description="Erstelle aus Analyse und Roadmap ein ausführliches Dossier UND 6 Slides (getrennt durch 'SLIDETRENNER').", agent=marketing, expected_output="Dossier und Slides.")
    t4 = Task(description="Schreibe ein finales Statement zur Relevanz für unser FM-Unternehmen am Ende des Dossiers und als letzte Slide.", agent=head_of_digital, expected_output="Finales Statement.")

    crew = Crew(agents=[analyst, strategist, marketing, head_of_digital], tasks=[t1, t2, t3, t4], max_rpm=1)
    
    s1.warning("🔵 In Arbeit...")
    with st.spinner("Das Expertenteam analysiert..."):
        result = str(crew.kickoff())
        
    st.session_state.full_report = result
    s1.success("✅ Fertig"); s2.success("✅ Fertig"); s3.success("✅ Fertig"); s4.success("✅ Fertig")
    
    # Trennung von Dossier und Slides
    if "SLIDETRENNER" in result:
        parts = result.split("SLIDETRENNER")
        st.session_state.slides = [p.strip() for p in parts if len(p.strip()) > 20]
    else:
        st.session_state.slides = [result]
    
    log_area.empty()

# Anzeige
if st.session_state.full_report:
    tab1, tab2 = st.tabs(["📄 Ausführliches Dossier", "🖥️ Interaktive Slides"])
    
    with tab1:
        st.markdown(st.session_state.full_report.split("SLIDETRENNER")[0])
        st.markdown("---")
        st.subheader("🏁 Statement der Abteilungsleitung")
        st.info(st.session_state.full_report.split("SLIDETRENNER")[-1])

    with tab2:
        col_n1, col_s, col_n2 = st.columns([1, 4, 1])
        if col_n1.button("⬅️"): 
            st.session_state.current_slide = max(0, st.session_state.current_slide - 1)
            st.rerun()
        if col_n2.button("➡️"): 
            st.session_state.current_slide = min(len(st.session_state.slides)-1, st.session_state.current_slide + 1)
            st.rerun()
            
        with col_s:
            curr = st.session_state.current_slide
            is_last = curr == len(st.session_state.slides) - 1
            st.markdown(f"""
                <div style="background-color: #f8f9fb; padding: 30px; border-radius: 15px; border-top: 8px solid {'#28a745' if is_last else '#007bff'};">
                    <h3>{'Abschluss-Statement' if is_last else f'Folie {curr + 1}'}</h3>
                    <hr>{st.session_state.slides[curr]}
                </div>
            """, unsafe_allow_html=True)

    st.download_button("Dossier & Statement (PDF/MD) speichern", st.session_state.full_report, file_name="FM_Strategie.md")
