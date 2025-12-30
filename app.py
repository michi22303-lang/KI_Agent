import streamlit as st
from crewai import Agent, Task, Crew, LLM
import streamlit.components.v1 as components
import sys
import re
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Strategie Agentur V2", page_icon="📈", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden.")
    st.stop()

# Custom CSS für die Log-Konsole (Terminal-Look)
st.markdown("""
    <style>
    .terminal {
        background-color: #1e1e1e;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 10px;
        border-radius: 5px;
        height: 300px;
        overflow-y: scroll;
        font-size: 0.8rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 KI-Strategie-Agentur 2026 - Mastermind Edition")
st.markdown("Beobachte, wie deine Agenten eine umfassende Strategie und Präsentation entwickeln.")

topic = st.text_input("Digitalisierungs-Thema:", "Blockchain für Supply Chains im Mittelstand")

if st.button("Strategie & Präsentation starten"):
    
    # Workflow-Status Anzeigen
    status_box = st.container()
    with status_box:
        st.subheader("Arbeitsfortschritt")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            s1 = st.empty()
            s2 = st.empty()
            s3 = st.empty()
            s4 = st.empty() # Neuer Status für Marketingexperten
            s1.markdown("⚪ Analyst bereit...")
            s2.markdown("⚪ Stratege bereit...")
            s3.markdown("⚪ Designer bereit...")
            s4.markdown("⚪ Marketingexperte bereit...")
        
        # Die Log-Konsole
        with col_b:
            log_expander = st.expander("Live-Gedankenprotokoll (Logs)", expanded=True)
            log_output = log_expander.empty()

    # Umleitung der System-Ausgabe in die UI
    class StreamToStreamlit:
        def __init__(self, expander_obj):
            self.expander_obj = expander_obj
            self.buffer = ""
        def write(self, data):
            clean_data = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', data)
            self.buffer += clean_data
            self.expander_obj.markdown(f"```text\n{self.buffer}\n```", unsafe_allow_html=True)
            self.expander_obj.empty() # Löscht vorherigen Inhalt, um Scroll-Probleme zu vermeiden
            self.expander_obj.markdown(f"```text\n{self.buffer}\n```", unsafe_allow_html=True)

        def flush(self):
            pass

    sys.stdout = StreamToStreamlit(log_output)

    # Gemini 2.0 Setup
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.7 # Etwas höher für kreativere Texte
    )
    
    # AGENTEN (jetzt 4 Agenten)
    analyst = Agent(
        role='Senior Technologie-Analyst',
        goal=f'Detaillierte technische Analyse zu {topic} auf Deutsch.',
        backstory="IT-Experte für Zukunftstrends und technische Machbarkeit.",
        llm=gemini_llm, verbose=True, max_iter=2
    )
    strategist = Agent(
        role='Strategischer Unternehmensberater',
        goal=f'Entwickle eine robuste Roadmap und ROI-Analyse für {topic} auf Deutsch.',
        backstory="Berater für Business-Transformation, spezialisiert auf Implementierungsstrategien.",
        llm=gemini_llm, verbose=True, max_iter=1
    )
    # Designer bleibt, aber jetzt für ein Konzept, nicht SVG-Code
    designer = Agent(
        role='Konzeptioneller Infografik-Designer',
        goal=f'Erstelle ein detailliertes Konzept für eine Infografik zu {topic} auf Deutsch.',
        backstory="""Du bist Experte für visuelle Kommunikation. Anstatt SVG-Code zu schreiben, 
        beschreibe präzise, wie eine Infografik die Kernaussagen visuell darstellen sollte (Layout, Farben, Elemente).""",
        llm=gemini_llm, verbose=True, max_iter=1
    )
    # NEUER AGENT: Marketingexperte für ausformulierten Text und Präsentation
    marketing_expert = Agent(
        role='Senior Marketing- & Kommunikationsberater',
        goal=f'Formuliere einen ausführlichen Bericht aus und erstelle ein Präsentations-Outline für {topic} auf Deutsch.',
        backstory="""Du bist ein Meister der Kommunikation. Du verwandelst technische und strategische Informationen 
        in überzeugende, flüssige Texte und gliederst diese für eine Management-Präsentation (Folie für Folie).""",
        llm=gemini_llm, verbose=True, max_iter=2
    )

    # TASKS (Anpassung der Aufgaben)
    t1 = Task(description=f"Führe eine technische Tiefenanalyse zu {topic} durch.", agent=analyst, expected_output="Technischer Detailbericht.")
    t2 = Task(description=f"Entwickle eine Strategie und Business-Cases für {topic}.", agent=strategist, expected_output="Strategiedokument.")
    # Designer erstellt nur noch ein Konzept
    t3 = Task(
        description=f"""Basierend auf Analyse und Strategie: Erstelle ein detailliertes Konzept für eine Infografik (Beschreibung von Layout, Farben, Schlüssel-Elementen) auf Deutsch.
        Gib KEINEN SVG-Code aus.""",
        agent=designer,
        expected_output="Ein ausführliches Infografik-Konzept."
    )
    # NEUE AUFGABE für Marketingexperten
    t4 = Task(
        description=f"""Nimm alle vorherigen Informationen (Analyse, Strategie, Infografik-Konzept).
        1. Formuliere einen finalen, ausformulierten und gut strukturierten Management-Bericht auf Deutsch. Der Bericht sollte mindestens 800 Wörter umfassen und flüssig lesbar sein.
        2. Erstelle zusätzlich ein Gliederung für eine 5-7 Folien umfassende Management-Präsentation (PowerPoint-Outline-Stil) zu {topic}. Jede Folie muss einen Titel und 3-5 Bulletpoints enthalten.""",
        agent=marketing_expert,
        expected_output="Ein ausführlicher Management-Bericht und ein Präsentations-Outline (beides in Markdown)."
    )

    crew = Crew(agents=[analyst, strategist, designer, marketing_expert], tasks=[t1, t2, t3, t4], max_rpm=2)
    
    try:
        s1.markdown("🔵 Analyst arbeitet...")
        
        # Da CrewAI im Ganzen läuft, können wir hier nur einen ungefähren Fortschritt simulieren
        # Die Live-Logs geben aber den genauen Einblick
        result_obj = crew.kickoff() 
        full_result = str(result_obj)
        
        s1.markdown("✅ Analyst fertig")
        s2.markdown("✅ Stratege fertig")
        s3.markdown("✅ Designer fertig (Konzept)")
        s4.markdown("✅ Marketingexperte fertig (Bericht & Präsentation)")
        
        st.divider()
        st.success("Analyse, Strategie und Präsentation erfolgreich erstellt!")

        # Ausgabe der Ergebnisse
        st.subheader("📊 Infografik-Konzept (als Text)")
        st.markdown("---")
        # Hier könnten wir versuchen, das Konzept zu extrahieren, aber für den ersten Schritt ist der Gesamtoutput OK
        
        st.subheader("📄 Ausführlicher Management-Bericht")
        st.markdown(full_result) # Der Marketingexperte fasst alles zusammen
        
        st.download_button("Vollständiges Dossier herunterladen", full_result, file_name="Strategie_Präsentation_
