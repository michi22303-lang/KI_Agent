import streamlit as st
from crewai import Agent, Task, Crew, LLM
import sys
import re
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Strategie Agentur", page_icon="🏢", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden.")
    st.stop()

# Header
st.title("🏢 KI-Strategie-Zentrum")
st.markdown("Sequenzielle Verarbeitung für maximale Stabilität und Kosteneffizienz.")

topic = st.text_input("Thema für die Analyse:", "KI-gestützte Kreislaufwirtschaft 2026")

if st.button("Analyse-Prozess starten"):
    
    # UI-Bereich für die Status-Anzeige
    st.subheader("Stations-Monitor")
    status_cols = st.columns(4)
    with status_cols[0]: s1 = st.empty()
    with status_cols[1]: s2 = st.empty()
    with status_cols[2]: s3 = st.empty()
    with status_cols[3]: s4 = st.empty()

    # Initialzustand
    s1.info("🟡 Analyst\n(Wartet...)")
    s2.info("🟡 Stratege\n(Wartet...)")
    s3.info("🟡 Designer\n(Wartet...)")
    s4.info("🟡 Marketing\n(Wartet...)")

    # Log-Bereich
    st.divider()
    log_expander = st.expander("Agenten-Protokoll (Live)", expanded=True)
    log_placeholder = log_expander.empty()

    class StreamlitRedirect:
        def __init__(self, placeholder):
            self.placeholder = placeholder
            self.output = ""
        def write(self, text):
            text = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', text)
            if text.strip():
                self.output += text + "\n"
                lines = self.output.split("\n")
                self.placeholder.code("\n".join(lines[-8:]))
        def flush(self): pass

    sys.stdout = StreamlitRedirect(log_placeholder)

    # Gemini 2.0 Setup (Stabilisiert)
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.4
    )
    
    # Agenten (Delegation deaktiviert für weniger Requests)
    analyst = Agent(
        role='Analyst', goal=f'Technische Fakten zu {topic}.',
        backstory="IT-Experte.", llm=gemini_llm, verbose=True, allow_delegation=False
    )
    strategist = Agent(
        role='Stratege', goal=f'ROI-Plan für {topic}.',
        backstory="Business-Experte.", llm=gemini_llm, verbose=True, allow_delegation=False
    )
    designer = Agent(
        role='Designer', goal=f'Visualisierungs-Konzept für {topic}.',
        backstory="Design-Profi.", llm=gemini_llm, verbose=True, allow_delegation=False
    )
    marketing = Agent(
        role='Marketing', goal=f'Dossier und Slides zu {topic}.',
        backstory="Kommunikations-Profi.", llm=gemini_llm, verbose=True, allow_delegation=False
    )

    # Tasks
    t1 = Task(description=f"Analysiere {topic}.", agent=analyst, expected_output="Technik-Daten.")
    t2 = Task(description=f"Strategie für {topic}.", agent=strategist, expected_output="Business-Szenarien.")
    t3 = Task(description=f"Design für {topic}.", agent=designer, expected_output="Layout-Konzept.")
    t4 = Task(description=f"Erstelle Bericht und 6 Slides (Trenner: '---') zu {topic}.", agent=marketing, expected_output="Finales Dossier.")

    crew = Crew(agents=[analyst, strategist, designer, marketing], tasks=[t1, t2, t3, t4], max_rpm=1)
    
    try:
        # Visuelle Steuerung des Workflows
        s1.warning("🔵 Analyst\n(Aktiv)")
        
        # Start
        result = crew.kickoff()
        full_result = str(result)
        
        # Alle auf Fertig setzen (Da Kickoff am Ende alles zurückgibt)
        s1.success("✅ Analyst\n(Fertig)")
        s2.success("✅ Stratege\n(Fertig)")
        s3.success("✅ Designer\n(Fertig)")
        s4.success("✅ Marketing\n(Fertig)")
        
        st.divider()

        # Tabs für die Ausgabe
        tab1, tab2 = st.tabs(["📄 Strategie-Dossier", "🖥️ Slides / Präsentation"])
        
        if "---" in full_result:
            parts = full_result.split("---")
            tab1.markdown(parts[0])
            tab2.markdown(parts[1])
        else:
            tab1.markdown(full_result)

    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
    finally:
        sys.stdout = sys.__stdout__
