import streamlit as st
from crewai import Agent, Task, Crew, LLM
import os

# Seite konfigurieren
st.set_page_config(page_title="Digitalisierungs-Strategie 2026", page_icon="🚀")

# Key sicher aus Streamlit Secrets laden
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY wurde nicht in den Secrets gefunden. Bitte in den Streamlit Cloud Settings unter 'Secrets' hinterlegen.")
    st.stop()

st.title("🤖 Digital-Strategie Team (Gemini 2.0)")
st.markdown("Nutzt Google Gemini 2.0 Flash-Lite für ultra-schnelle Analysen.")

# Eingabefeld für das Thema
topic = st.text_input("Welches Digitalisierungs-Thema soll analysiert werden?", "KI-Agenten im Mittelstand")

if st.button("Strategie-Analyse starten"):
    # Das Gemini 2.0 Modell initialisieren
    # WICHTIG: Die Schreibweise 'gemini/...' triggert die richtige Schnittstelle
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.7
    )
    
    # 1. Agent: Der Analyst (Fakten & Technik)
    analyst = Agent(
        role='Technologie-Analyst',
        goal=f'Identifiziere technologische Fakten zu {topic} im Jahr 2026',
        backstory="Du bist Experte für IT-Infrastruktur und neue Tech-Trends.",
        llm=gemini_llm,
        verbose=True
    )
    
    # 2. Agent: Der Stratege (Business & Use-Cases)
    strategist = Agent(
        role='Digital-Business-Strategist',
        goal=f'Entwickle wirtschaftliche Use-Cases für {topic}',
        backstory="Du bist spezialisiert auf digitale Transformation und Geschäftsentwicklung.",
        llm=gemini_llm,
        verbose=True
    )
    
    # 3. Agent: Der Kommunikator (Zusammenfassung)
    creator = Agent(
        role='Executive Editor',
        goal=f'Erstelle ein Management-Summary über {topic}',
        backstory="Du schreibst präzise Berichte für die Geschäftsführung.",
        llm=gemini_llm,
        verbose=True
    )

    # Tasks definieren
    t1 = Task(
        description=f"Analysiere den Stand von {topic} für 2026.",
        agent=analyst,
        expected_output="Technische Faktenliste."
    )
    t2 = Task(
        description=f"Erstelle 3 Business-Use-Cases basierend auf der Analyse.",
        agent=strategist,
        expected_output="Drei konkrete Szenarien mit Nutzenversprechen."
    )
    t3 = Task(
        description=f"Fasse alles in einem fertigen Bericht zusammen.",
        agent=creator,
        expected_output="Ein strukturierter Bericht in Markdown."
    )

    # Crew zusammenstellen
    crew = Crew(
        agents=[analyst, strategist, creator],
        tasks=[t1, t2, t3],
        verbose=True
    )
    
    with st.spinner('Die Gemini 2.0 Agenten arbeiten...'):
        try:
            result = crew.kickoff()
            st.success("Analyse abgeschlossen!")
            st.markdown("---")
            st.markdown(str(result))
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")
            st.info("Checke bitte, ob 'litellm' in deiner requirements.txt steht.")
