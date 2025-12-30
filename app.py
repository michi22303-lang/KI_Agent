import streamlit as st
from crewai import Agent, Task, Crew, LLM
import sys
import re
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Strategie Agentur Pro", page_icon="🏢", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden.")
    st.stop()

st.title("🏢 KI-Strategie Agentur: Collaborative Mode")

# 2. Log-System Setup
class StreamlitRedirect:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.output = ""
    def write(self, text):
        # Bereinigung von Terminal-Farbcodes
        text = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', text)
        if text.strip():
            self.output += text + "\n"
            # Wir zeigen nur die letzten 15 Zeilen für bessere Lesbarkeit
            lines = self.output.split("\n")
            display_text = "\n".join(lines[-15:])
            self.placeholder.code(display_text)
    def flush(self): pass

topic = st.text_input("Digitalisierungs-Thema:", "KI-Agenten in der Logistik 2026")

if st.button("Kollaborative Analyse starten"):
    
    # UI Elemente für Status und Logs
    col_status, col_logs = st.columns([1, 1])
    
    with col_status:
        st.subheader("📍 Workflow & Zeit")
        progress_bar = st.progress(0)
        timer_text = st.empty()
        status_update = st.empty()
        
    with col_logs:
        st.subheader("🕵️‍♂️ Agenten-Chat (Live-Logs)")
        log_placeholder = st.empty()

    # Umleitung starten
    sys.stdout = StreamlitRedirect(log_placeholder)

    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.7)
    
    # 3. Agenten mit DELEGATION (Erlaubt Austausch untereinander)
    analyst = Agent(
        role='Senior Technologie-Analyst',
        goal=f'Analysiere {topic} technisch.',
        backstory="Du bist die technische Instanz. Beantworte Rückfragen des Strategen präzise.",
        llm=gemini_llm, allow_delegation=True, verbose=True
    )
    strategist = Agent(
        role='Strategischer Unternehmensberater',
        goal=f'Entwickle Business-Cases. Frage beim Analysten nach, falls technische Details unklar sind.',
        backstory="Du bist der Kopf der Strategie. Du validierst deine Annahmen beim Analysten.",
        llm=gemini_llm, allow_delegation=True, verbose=True
    )
    designer = Agent(
        role='Konzeptioneller Designer',
        goal='Erstelle ein Visuelles Konzept.',
        backstory="Du arbeitest eng mit dem Marketing zusammen, um Design-Vorgaben abzustimmen.",
        llm=gemini_llm, allow_delegation=True, verbose=True
    )
    marketing = Agent(
        role='Marketing-Direktor',
        goal='Erstelle das finale Dossier und die Slides. Stimme dich mit dem Designer über die Optik ab.',
        backstory="Du bist der finale Redakteur. Du delegierst Design-Fragen an den Designer.",
        llm=gemini_llm, allow_delegation=True, verbose=True
    )

    # Tasks
    t1 = Task(description=f"Technik-Check {topic}.", agent=analyst, expected_output="Analyse.")
    t2 = Task(description=f"Strategie & ROI für {topic}.", agent=strategist, expected_output="Business-Plan.")
    t3 = Task(description=f"Visuelles Storyboard für {topic}.", agent=designer, expected_output="Design-Konzept.")
    t4 = Task(description="Erstelle das 1000-Wörter Dossier und 6 Slides. Trenne beides mit '---'.", agent=marketing, expected_output="Dossier & Slides.")

    crew = Crew(agents=[analyst, strategist, designer, marketing], tasks=[t1, t2, t3, t4], max_rpm=2)
    
    start_time = time.time()
    
    try:
        # Phase 1: Start
        status_update.info("Agenten nehmen die Arbeit auf... (Geschätzte Dauer: 90-120 Sek.)")
        progress_bar.progress(10)
        
        # Crew Ausführung
        result = str(crew.kickoff())
        
        # Phase 2: Abschluss
        end_time = time.time()
        duration = int(end_time - start_time)
        
        progress_bar.progress(100)
        status_update.success(f"Fertig! Gesamtdauer: {duration} Sekunden.")
        
        st.divider()
        
        # Tabs für Ergebnisse
        tab1, tab2 = st.tabs(["📄 Strategisches Dossier", "🖥️ Präsentations-Slides"])
        
        if "---" in result:
            parts = result.split("---")
            with tab1: st.markdown(parts[0])
            with tab2: st.markdown(parts[1])
        else:
            with tab1: st.markdown(result)

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        sys.stdout = sys.__stdout__
