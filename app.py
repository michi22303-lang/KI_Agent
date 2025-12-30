import streamlit as st
from crewai import Agent, Task, Crew, LLM
import streamlit.components.v1 as components
import sys
import re

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Strategie Agentur V2", page_icon="📈", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden.")
    st.stop()

st.title("📈 KI-Strategie-Agentur: Master-Dossier & Präsentation")
st.markdown("Beobachte dein Team dabei, wie es eine komplette Strategie inklusive Slides entwickelt.")

topic = st.text_input("Digitalisierungs-Thema:", "KI-Agenten im Kundenservice 2026")

if st.button("Strategie & Präsentation erstellen"):
    
    # Workflow-Status Anzeigen
    status_box = st.container()
    with status_box:
        st.subheader("Arbeitsfortschritt")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            s1, s2, s3, s4 = st.empty(), st.empty(), st.empty(), st.empty()
            s1.markdown("⚪ Analyst bereit")
            s2.markdown("⚪ Stratege bereit")
            s3.markdown("⚪ Designer bereit")
            s4.markdown("⚪ Marketingexperte bereit")
        
        with col_b:
            log_expander = st.expander("Live-Logs (Agenten-Gedanken)", expanded=True)
            log_output = log_expander.empty()

    # Log-Umleitung
    class StreamToStreamlit:
        def __init__(self, expander_obj):
            self.expander_obj = expander_obj
            self.buffer = ""
        def write(self, data):
            clean_data = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', data)
            self.buffer += clean_data
            self.expander_obj.code(self.buffer, language="text")
        def flush(self): pass

    sys.stdout = StreamToStreamlit(log_output)

    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.7)
    
    # Agenten
    analyst = Agent(
        role='Senior Technologie-Analyst',
        goal=f'Detaillierte technische Analyse zu {topic} auf Deutsch.',
        backstory="IT-Experte für Zukunftstrends.", llm=gemini_llm, verbose=True, max_iter=1
    )
    strategist = Agent(
        role='Strategischer Unternehmensberater',
        goal=f'Roadmap und ROI-Analyse für {topic} auf Deutsch.',
        backstory="Experte für Business-Transformation.", llm=gemini_llm, verbose=True, max_iter=1
    )
    designer = Agent(
        role='Konzeptioneller Designer',
        goal=f'Visuelles Konzept für eine Infografik zu {topic} auf Deutsch.',
        backstory="Experte für visuelle Storyboards.", llm=gemini_llm, verbose=True, max_iter=1
    )
    marketing = Agent(
        role='Marketing-Direktor',
        goal=f'Erstelle einen ausformulierten Bericht und Präsentations-Slides zu {topic} auf Deutsch.',
        backstory="Du bist ein Meister der Rhetorik und erstellst hochwertige Business-Texte.",
        llm=gemini_llm, verbose=True, max_iter=1
    )

    # Tasks
    t1 = Task(description=f"Technik-Analyse {topic}.", agent=analyst, expected_output="Technik-Bericht.")
    t2 = Task(description=f"Business-Strategie {topic}.", agent=strategist, expected_output="Strategie-Bericht.")
    t3 = Task(description=f"Design-Konzept für {topic}.", agent=designer, expected_output="Infografik-Beschreibung.")
    t4 = Task(
        description=f"""Nimm alle Infos und erstelle:
        1. Einen ausführlichen, flüssigen Management-Bericht (Dossier-Stil).
        2. Eine Präsentation mit 6 Slides (Titel & Bulletpoints).
        Nutze '---' um Bericht und Präsentation zu trennen.""",
        agent=marketing,
        expected_output="Ein langes Dossier und ein Slide-Deck auf Deutsch."
    )

    crew = Crew(agents=[analyst, strategist, designer, marketing], tasks=[t1, t2, t3, t4], max_rpm=2)
    
    try:
        s1.markdown("🔵 Analyst arbeitet...")
        result = str(crew.kickoff())
        
        s1.markdown("✅ Analyst fertig"); s2.markdown("✅ Stratege fertig")
        s3.markdown("✅ Designer fertig"); s4.markdown("✅ Marketingexperte fertig")
        
        st.divider()

        # Splitten von Bericht und Slides (falls Trenner vorhanden)
        if "---" in result:
            parts = result.split("---")
            bericht = parts[0]
            slides = parts[1]
        else:
            bericht = result
            slides = "Die Slides wurden am Ende des Berichts angefügt."

        # Anzeige in Tabs für bessere Übersicht
        tab1, tab2 = st.tabs(["📄 Ausführliches Dossier", "🖥️ Präsentations-Slides"])
        
        with tab1:
            st.markdown(bericht)
        with tab2:
            st.markdown(slides)
        
        st.download_button("Dossier & Slides speichern", result, file_name="Strategie_Dossier.md")

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        sys.stdout = sys.__stdout__
