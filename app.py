import streamlit as st
from crewai import Agent, Task, Crew, LLM
import os

# Seite konfigurieren
st.set_page_config(page_title="Digitalisierungs-Strategie Team", page_icon="🚀")

# Key sicher aus Streamlit Secrets laden
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY wurde nicht in den Secrets gefunden.")
    st.stop()

st.title("🚀 Digitalisierungs-Strategie Team")
st.markdown("Dieses Team aus KI-Agenten analysiert Trends und entwickelt Business-Szenarien für 2026.")

topic = st.text_input("Welches Digitalisierungs-Thema soll analysiert werden?", "Autonome Logistik-Drohnen")

if st.button("Strategie-Analyse starten"):
    # Das Gemini Modell initialisieren
    gemini_llm = LLM(
       model="gemini/models/gemini-1.5-flash", 
        api_key=google_key,
        config={
        "safety_settings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }
    )
    
    # 1. Agent: Der Analyst
    analyst = Agent(
        role='Technologie-Analyst',
        goal=f'Identifiziere technologische Fakten und Risiken zu {topic}',
        backstory="Du bist Experte für IT-Infrastruktur und erkennst technologische Hypes von echten Durchbrüchen.",
        llm=gemini_llm,
        allow_delegation=False,
        verbose=True
    )
    
    # 2. Agent: Der Stratege
    strategist = Agent(
        role='Digital-Business-Strategist',
        goal=f'Entwickle wirtschaftliche Use-Cases und ROI-Szenarien für {topic}',
        backstory="Du bist spezialisiert auf digitale Transformation und Geschäftsentwicklung im Mittelstand.",
        llm=gemini_llm,
        allow_delegation=False,
        verbose=True
    )
    
    # 3. Agent: Der Kommunikator
    creator = Agent(
        role='Executive Editor',
        goal=f'Erstelle ein überzeugendes Management-Summary über {topic}',
        backstory="Du schreibst für Vorstände und Geschäftsführer – präzise, faktenbasiert und visionär.",
        llm=gemini_llm,
        allow_delegation=False,
        verbose=True
    )

    # Tasks definieren
    t1 = Task(
        description=f"Analysiere den aktuellen Stand und die Trends von {topic} mit Fokus auf das Jahr 2026.",
        agent=analyst,
        expected_output="Eine detaillierte Liste technischer Fakten und potenzieller Risiken."
    )
    t2 = Task(
        description=f"Entwickle basierend auf der Analyse drei konkrete Business-Szenarien für Unternehmen.",
        agent=strategist,
        expected_output="Drei Use-Cases mit jeweils einem kurzen Nutzenversprechen (ROI)."
    )
    t3 = Task(
        description=f"Fasse alle Erkenntnisse in einem strukturierten Management-Summary zusammen (Markdown).",
        agent=creator,
        expected_output="Ein fertiger Bericht mit Einleitung, Technik-Check, Business-Szenarien und Fazit."
    )

    # Crew zusammenstellen
    crew = Crew(
        agents=[analyst, strategist, creator],
        tasks=[t1, t2, t3],
        verbose=True
    )
    
    with st.spinner('Die Agenten analysieren, diskutieren und schreiben...'):
        result = crew.kickoff()
        st.success("Analyse abgeschlossen!")
        st.markdown("---")
        st.markdown(str(result))
