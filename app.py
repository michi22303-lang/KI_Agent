import streamlit as st
from crewai import Agent, Task, Crew, LLM
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="KI-Strategie & Design", page_icon="📊", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte GOOGLE_API_KEY in den Secrets hinterlegen.")
    st.stop()

st.title("🎨 Dein Digital-Strategie Team")
st.markdown("Analysen und visuelle Konzepte – komplett auf Deutsch.")

topic = st.text_input("Digitalisierungs-Thema:", "KI-Agenten im Kundenservice")

if st.button("Analyse & Infografik erstellen"):
    # Gemini 2.0 Modell mit deutschem System-Prompt-Hinweis
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.5 # Etwas niedriger für präzisere Grafik-Codes
    )
    
    # AGENTEN (Alle auf Deutsch getrimmt)
    analyst = Agent(
        role='Technologie-Analyst',
        goal=f'Analysiere {topic} und liefere technische Fakten auf Deutsch.',
        backstory="Du bist ein präziser deutscher IT-Analyst.",
        llm=gemini_llm,
        max_iter=1
    )
    
    strategist = Agent(
        role='Business-Stratege',
        goal=f'Entwickle 3 Business-Szenarien für {topic} auf Deutsch.',
        backstory="Du bist ein erfahrener Unternehmensberater.",
        llm=gemini_llm,
        max_iter=1
    )
    
    designer = Agent(
        role='Visual-Designer',
        goal='Erstelle eine Zusammenfassung auf Deutsch UND einen SVG-Code für eine Infografik.',
        backstory="""Du bist Profi für Datenvisualisierung. 
        Deine Aufgabe ist es, die Ergebnisse in ein schönes SVG-Format (Scalable Vector Graphics) 
        zu gießen, das direkt im Browser angezeigt werden kann.""",
        llm=gemini_llm,
        max_iter=1
    )

    # TASKS
    t1 = Task(description=f"Technik-Check für {topic} auf Deutsch.", agent=analyst, expected_output="Faktenliste.")
    t2 = Task(description=f"Business-Szenarien für {topic} auf Deutsch.", agent=strategist, expected_output="Szenarien-Liste.")
    t3 = Task(
        description=f"""Fasse alles auf Deutsch zusammen. 
        Erstelle am Ende des Berichts eine Infografik als SVG-Code. 
        Die Grafik soll die 3 wichtigsten Punkte von {topic} visualisieren.""",
        agent=designer,
        expected_output="Ein ausführlicher deutscher Bericht und ein sauberer <svg>...</svg> Codeblock."
    )

    crew = Crew(agents=[analyst, strategist, designer], tasks=[t1, t2, t3], max_rpm=2)
    
    with st.spinner('Das Team arbeitet...'):
        result = str(crew.kickoff())
        
        # Trennung von Text und SVG-Code
        if "<svg" in result:
            parts = result.split("<svg")
            text_part = parts[0]
            svg_part = "<svg" + parts[1].split("</svg>")[0] + "</svg>"
            
            st.success("Analyse abgeschlossen!")
            
            # Anzeige des Berichts
            st.markdown(text_part)
            
            # Anzeige der Infografik
            st.subheader("📊 Visuelle Infografik")
            components.html(svg_part, height=500, scrolling=True)
        else:
            st.markdown(result)
