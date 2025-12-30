import streamlit as st
from crewai import Agent, Task, Crew, LLM
import os

st.set_page_config(page_title="Digital-Strategie & Design", page_icon="🎨")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte GOOGLE_API_KEY in den Streamlit Secrets hinterlegen.")
    st.stop()

st.title("🎨 Strategie & Design-Team (Gemini 2.0)")
st.markdown("Analysiert, entwickelt Strategien und erstellt Infografik-Konzepte.")

topic = st.text_input("Thema:", "Ethik in der KI-Entwicklung 2026")

if st.button("Komplette Analyse mit Design starten"):
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.7
    )
    
    # 1. Agent: Der Analyst (Fakten & Technik)
    analyst = Agent(
        role='Tech-Analyst',
        goal=f'Fakten zu {topic} finden',
        backstory="Experte für Technologietrends.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    # 2. Agent: Der Stratege (Business & Use-Cases)
    strategist = Agent(
        role='Business-Stratege',
        goal=f'Use-Cases für {topic} entwickeln',
        backstory="Experte für digitale Geschäftsmodelle.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    # 3. Agent: Der Kommunikator (Zusammenfassung)
    creator = Agent(
        role='Bericht-Autor',
        goal=f'Management-Summary zu {topic} schreiben',
        backstory="Experte für prägnante Zusammenfassungen.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )

    # 4. Agent: Der Designer (NEU!)
    designer = Agent(
        role='Visual Design Konzeptionist',
        goal=f'Entwickle eine Infografik-Struktur und ein detailliertes Textdokument für {topic}',
        backstory="Du bist Experte für visuelle Kommunikation und erstellst überzeugende Konzepte für Infografiken und präsentable Berichte.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )

    # Tasks definieren
    t1 = Task(description=f"Analysiere {topic}.", agent=analyst, expected_output="Technik-Liste.")
    t2 = Task(description=f"Business-Cases für {topic}.", agent=strategist, expected_output="3 Szenarien.")
    t3 = Task(description=f"Management-Summary für {topic}.", agent=creator, expected_output="Markdown Bericht.")
    
    # NEUE AUFGABE für den Designer
    t4 = Task(
        description=f"""Basierend auf der technischen Analyse, den Business-Cases und dem Management-Summary:
        1. Erstelle eine detaillierte Beschreibung für eine Infografik (Elemente, Layout, Farben, Botschaft).
        2. Formatiere den gesamten Inhalt des Management-Summarys in ein professionelles, ausführliches Textdokument (z.B. als erweiterter Markdown-Bericht).
        """,
        agent=designer,
        expected_output="Ein detailliertes Infografik-Konzept und ein ausführliches, professionell formatiertes Textdokument (Markdown)."
    )

    # Crew zusammenstellen (jetzt mit 4 Agenten und 4 Tasks)
    crew = Crew(
        agents=[analyst, strategist, creator, designer], # Alle 4 Agenten
        tasks=[t1, t2, t3, t4], # Alle 4 Tasks
        max_rpm=2, # Bremse bleibt drin
        verbose=True
    )
    
    with st.spinner('Das komplette Team arbeitet: Analysiert, plant, schreibt und designt Konzepte...'):
        try:
            result = crew.kickoff()
            st.success("Komplette Analyse mit Designkonzept abgeschlossen!")
            st.markdown(str(result))
            
            # Hier könntest du später einen Button einbauen, um die Infografik zu generieren
            # if st.button("Infografik generieren"):
            #    st.markdown("Platzhalter für Infografik-Generierung")
            #    # Hier würde die API zum Bild-Generator aufgerufen
            
        except Exception as e:
            if "429" in str(e):
                st.error("Google-Limit erreicht (429). Bitte warte 60 Sekunden und versuche es erneut.")
            else:
                st.error(f"Ein unbekannter Fehler ist aufgetreten: {e}")
