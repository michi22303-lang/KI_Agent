import streamlit as st
from crewai import Agent, Task, Crew, LLM
import os

st.set_page_config(page_title="Digital-Strategie Team", page_icon="🚀")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte GOOGLE_API_KEY in den Streamlit Secrets hinterlegen.")
    st.stop()

st.title("🤖 Strategie-Team (Rate-Limit optimiert)")
topic = st.text_input("Thema:", "KI im Gesundheitswesen 2026")

if st.button("Analyse starten"):
    # Gemini 2.0 mit Sicherheits-Fallback
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.7
    )
    
    # Agenten mit max_iter=1 um API-Calls zu sparen
    analyst = Agent(
        role='Tech-Analyst',
        goal=f'Fakten zu {topic} finden',
        backstory="Experte für Technologietrends.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    strategist = Agent(
        role='Business-Stratege',
        goal=f'Use-Cases für {topic} entwickeln',
        backstory="Experte für digitale Geschäftsmodelle.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    creator = Agent(
        role='Bericht-Autor',
        goal=f'Management-Summary zu {topic} schreiben',
        backstory="Experte für prägnante Zusammenfassungen.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )

    t1 = Task(description=f"Analyse {topic}.", agent=analyst, expected_output="Technik-Liste.")
    t2 = Task(description=f"Business-Cases für {topic}.", agent=strategist, expected_output="3 Szenarien.")
    t3 = Task(description=f"Bericht schreiben.", agent=creator, expected_output="Markdown Bericht.")

    # DIE WICHTIGSTE ÄNDERUNG: max_rpm=2
    # Das zwingt die Crew, zwischen den Anfragen kurz zu warten.
    crew = Crew(
        agents=[analyst, strategist, creator],
        tasks=[t1, t2, t3],
        max_rpm=2, 
        verbose=True
    )
    
    with st.spinner('Die Agenten arbeiten (mit Pausen gegen das Rate-Limit)...'):
        try:
            result = crew.kickoff()
            st.success("Erfolgreich erstellt!")
            st.markdown(str(result))
        except Exception as e:
            if "429" in str(e):
                st.error("Google-Limit erreicht (429). Bitte warte 60 Sekunden und versuche es erneut.")
            else:
                st.error(f"Fehler: {e}")
