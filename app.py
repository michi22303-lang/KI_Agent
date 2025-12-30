import streamlit as st
from crewai import Agent, Task, Crew, LLM
import sys
import re
import time

st.set_page_config(page_title="KI-Strategie Agentur Pro", page_icon="🏢", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden.")
    st.stop()

# Robustes Log-System
class StreamlitRedirect:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.output = ""
    def write(self, text):
        text = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', text)
        if text.strip():
            self.output += text + "\n"
            lines = self.output.split("\n")
            self.placeholder.code("\n".join(lines[-10:]))
    def flush(self): pass

st.title("🏢 Strategie-Agentur (Stabilitäts-Modus)")

topic = st.text_input("Thema:", "KI-Transformation 2026")

if st.button("Analyse starten"):
    col_status, col_logs = st.columns([1, 1])
    with col_status:
        progress_bar = st.progress(0)
        status_update = st.empty()
    with col_logs:
        log_placeholder = st.empty()

    sys.stdout = StreamlitRedirect(log_placeholder)

    # Wir nutzen hier eine stabilere Konfiguration für das LLM
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.3, # Niedrigere Temperatur = stabilere Antworten
        max_tokens=4000
    )
    
    # Agenten mit reduzierter Komplexität für höhere Stabilität
    analyst = Agent(
        role='Technologie-Analyst',
        goal=f'Analysiere {topic} technisch auf Deutsch.',
        backstory="Du lieferst Fakten. Sei präzise und kurz angebunden.",
        llm=gemini_llm, allow_delegation=False, verbose=True, max_iter=2
    )
    strategist = Agent(
        role='Business-Stratege',
        goal='Entwickle Business-Cases auf Deutsch.',
        backstory="Du bist der Strategiekopf.",
        llm=gemini_llm, allow_delegation=True, verbose=True, max_iter=2
    )
    marketing = Agent(
        role='Marketing-Direktor',
        goal='Schreibe das Dossier und die Slides auf Deutsch.',
        backstory="Du fasst alles zusammen. Du darfst Rückfragen an den Strategen stellen.",
        llm=gemini_llm, allow_delegation=True, verbose=True, max_iter=2
    )

    t1 = Task(description=f"Technik-Analyse {topic}.", agent=analyst, expected_output="Faktenbericht.")
    t2 = Task(description=f"Business-Strategie für {topic}.", agent=strategist, expected_output="Strategieplan.")
    t3 = Task(description="Erstelle ein Dossier und 6 Slides. Trenne mit '---'.", agent=marketing, expected_output="Finales Dokument.")

    # Crew mit Prozess-Optimierung
    crew = Crew(
        agents=[analyst, strategist, marketing], 
        tasks=[t1, t2, t3], 
        max_rpm=2,
        cache=True # Cache aktivieren, um leere Re-Calls zu vermeiden
    )
    
    try:
        status_update.info("Agenten arbeiten... Bitte Fenster nicht schließen.")
        progress_bar.progress(20)
        
        # Den Kickoff in einer stabilen Umgebung ausführen
        result = crew.kickoff()
        full_result = str(result)
        
        progress_bar.progress(100)
        status_update.success("Analyse erfolgreich!")
        
        tab1, tab2 = st.tabs(["📄 Dossier", "🖥️ Slides"])
        if "---" in full_result:
            parts = full_result.split("---")
            tab1.markdown(parts[0])
            tab2.markdown(parts[1])
        else:
            tab1.markdown(full_result)

    except Exception as e:
        st.error(f"LLM Fehler: Das Modell hat keine Antwort geliefert. Ursache: {e}")
        st.info("Tipp: Versuche ein simpleres Thema oder warte 30 Sekunden.")
    finally:
        sys.stdout = sys.__stdout__
