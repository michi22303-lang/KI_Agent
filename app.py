import streamlit as st
from crewai import Agent, Task, Crew
import os

# UI Titel
st.title("🤖 Mein KI-Agenten-Team")

# Sidebar für API Key (falls du ihn nicht fest verbauen willst)
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

topic = st.text_input("Über welches Thema sollen die Agenten recherchieren?", "KI-Trends 2026")

if st.button("Crew starten"):
    if not api_key:
        st.error("Bitte gib einen API Key ein!")
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Agenten definieren
        researcher = Agent(
            role='Forscher',
            goal=f'Finde bahnbrechende Infos zu {topic}',
            backstory="Du bist ein Experte für Technologie-Analysen.",
            allow_delegation=False
        )
        
        writer = Agent(
            role='Schreiber',
            goal=f'Erstelle einen Bericht über {topic}',
            backstory="Du bist ein Profi-Journalist.",
            allow_delegation=False
        )

        # Tasks definieren
        task1 = Task(description=f"Analysiere {topic}.", agent=researcher, expected_output="3 Kernpunkte.")
        task2 = Task(description=f"Schreibe Bericht über {topic}.", agent=writer, expected_output="Ein Artikel.")

        # Crew ausführen
        crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
        
        with st.spinner('Die Agenten arbeiten...'):
            result = crew.kickoff()
            st.success("Erledigt!")
            st.markdown(result)
