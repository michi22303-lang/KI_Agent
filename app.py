import streamlit as st
from crewai import Agent, Task, Crew, LLM
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="FM Strategie-Dossier & Mitarbeiter-Info", page_icon="🏢", layout="wide")

# Session State initialisieren
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "slides" not in st.session_state: st.session_state.slides = []
if "current_slide" not in st.session_state: st.session_state.current_slide = 0

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte API Key in den Streamlit Secrets hinterlegen.")
    st.stop()

st.title("🏢 Strategische Analyse & Interne Kommunikation")

# --- UI Layout: Status-Monitor (Fixiert oben) ---
status_container = st.container()
with status_container:
    st.subheader("Stations-Monitor")
    status_cols = st.columns(4)
    s1 = status_cols[0].empty()
    s2 = status_cols[1].empty()
    s3 = status_cols[2].empty()
    s4 = status_cols[3].empty()
    # Initialanzeige
    s1.info("⚪ Technik-Check")
    s2.info("⚪ ROI-Strategie")
    s3.info("⚪ Mitarbeiter-Info")
    s4.info("⚪ Leitungs-Statement")

st.divider()

topic = st.text_input("Thema für das Facility Management:", "Einführung von Robotik-Reinigungssystemen 2026")

log_area = st.empty()

def step_callback(step_output):
    try:
        thought = "Verarbeite Daten..."
        if hasattr(step_output, 'thought'):
            thought = step_output.thought
        elif isinstance(step_output, dict) and 'thought' in step_output:
            thought = step_output['thought']
        log_area.info(f"🕵️ **Aktueller Agenten-Gedanke:** {thought[:250]}...")
    except:
        log_area.info("🕵️ Ein Agent plant den nächsten Schritt...")

if st.button("Umfassende Analyse & Slides starten"):
    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.4)
    
    # --- Agenten-Definition ---
    analyst = Agent(
        role='Senior Technologie-Analyst', 
        goal='Erstelle eine technisch fundierte und ausführliche Analyse.', 
        backstory="Du bist ein akribischer IT-Experte für FM-Systeme. Dein Fokus liegt auf Details.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )
    strategist = Agent(
        role='Strategischer Business-Planer', 
        goal='Entwickle eine Roadmap und ROI-Rechnung für das Unternehmen.', 
        backstory="Du bist der wirtschaftliche Kopf. Du planst Budgets und Zeitabläufe.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )
    marketing = Agent(
        role='Interne Kommunikation & Marketing', 
        goal='Erstelle mitarbeiterorientierte Slides zur internen Akzeptanz.', 
        backstory="Du bist der Vermittler. Du erklärst den Mitarbeitern die Vorteile und nimmst ihnen Ängste.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )
    head_of_digital = Agent(
        role='Leiter Digitalisierungsabteilung', 
        goal='Gib ein abschließendes Statement zur operativen Relevanz ab.', 
        backstory="Du bist die finale Entscheidungsinstanz im Facility Management.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )

    # --- Tasks ---
    t1 = Task(
        description=f"Schreibe einen ausführlichen technischen Bericht (min. 500 Wörter) über {topic} auf Deutsch.", 
        agent=analyst, expected_output="Umfangreicher Technik-Bericht."
    )
    t2 = Task(
        description=f"Entwickle eine detaillierte Roadmap und ROI-Analyse (min. 400 Wörter) für {topic} auf Deutsch.", 
        agent=strategist, expected_output="Strategischer Business-Plan."
    )
    t3 = Task(
        description=f"Erstelle 6 mitarbeiterorientierte Slides, die {topic} motivierend erklären. Nutze das Wort SLIDETRENNER zwischen den Slides.", 
        agent=marketing, expected_output="Präsentationsfolien für Mitarbeiter."
    )
    t4 = Task(
        description="Fasse Technik und Strategie zu einem Dossier zusammen und ergänze am Ende ein 200-Wörter Statement zur Relevanz für unser Unternehmen.", 
        agent=head_of_digital, expected_output="Finales Dossier mit Management-Fazit."
    )

    crew = Crew(agents=[analyst, strategist, marketing, head_of_digital], tasks=[t1, t2, t3, t4], max_rpm=1)
    
    # Prozess-Visualisierung
    s1.warning("🔵 Technik aktiv...")
    with st.spinner("Das Team erstellt das Dossier..."):
        result = str(crew.kickoff())
        
    st.session_state.full_report = result
    s1.success("✅ Technik fertig"); s2.success("✅ Strategie fertig"); s3.success("✅ Marketing fertig"); s4.success("✅ Leitung fertig")
    
    # Slides verarbeiten
    if "SLIDETRENNER" in result:
        parts = result.split("SLIDETRENNER")
        st.session_state.slides = [p.strip() for p in parts if len(p.strip()) > 20]
    else:
        st.session_state.slides = [result]
    
    log_area.empty()

# --- Anzeige der Ergebnisse ---
if st.session_state.full_report:
    tab1, tab2 = st.tabs(["📄 Ausführliches Dossier (Management)", "🖥️ Mitarbeiter-Präsentation"])
    
    with tab1:
        st.subheader("Strategisches Dossier")
        # Wir zeigen das Dossier ohne die Slides an
        dossier_content = st.session_state.full_report.split("SLIDETRENNER")[0]
        st.markdown(dossier_content)

    with tab2:
        col_n1, col_s, col_n2 = st.columns([1, 4, 1])
        if col_n1.button("⬅️ Zurück"): 
            st.session_state.current_slide = max(0, st.session_state.current_slide - 1)
            st.rerun()
        if col_n2.button("Vorwärts ➡️"): 
            st.session_state.current_slide = min(len(st.session_state.slides)-1, st.session_state.current_slide + 1)
            st.rerun()
            
        with col_s:
            curr = st.session_state.current_slide
            is_last = curr == len(st.session_state.slides) - 1
            st.markdown(f"""
                <div style="background-color: #f0f4f8; padding: 40px; border-radius: 20px; border-left: 10px solid #2c3e50; min-height: 350px;">
                    <h3 style="color: #2c3e50;">{'Mitarbeiter-Info' if not is_last else 'Fazit der Leitung'}</h3>
                    <p style="color: #666; font-size: 0.9em;">Folie {curr + 1} von {len(st.session_state.slides)}</p>
                    <hr>
                    <div style="font-family: 'Segoe UI', sans-serif; font-size: 1.15em; line-height: 1.6;">
                        {st.session_state.slides[curr]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.download_button("Vollständiges Dossier speichern", st.session_state.full_report, file_name="Dossier_FM.md")
