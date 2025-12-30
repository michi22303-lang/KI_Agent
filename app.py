import streamlit as st
from crewai import Agent, Task, Crew, LLM
import streamlit.components.v1 as components
import os

# 1. Seite konfigurieren
st.set_page_config(page_title="Digital-Strategie & Design 2026", page_icon="🎨", layout="wide")

# 2. Key sicher aus Streamlit Secrets laden
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden. Bitte in den Streamlit Cloud Settings hinterlegen.")
    st.stop()

# 3. UI Header
st.title("🚀 KI-Strategie-Team mit Design-Studio")
st.markdown("""
Dieses autonome Team analysiert Trends, entwickelt Business-Cases und erstellt eine visuelle Infografik.
**Technologie:** Gemini 2.0 Flash-Lite | **Sprache:** Deutsch
""")

topic = st.text_input("Welches Thema soll das Team bearbeiten?", "KI-Agenten im deutschen Mittelstand")

if st.button("Komplette Analyse & Infografik starten"):
    
    # Modell-Konfiguration (Gemini 2.0)
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.5
    )
    
    # 4. Agenten-Definition (Alle auf Deutsch)
    analyst = Agent(
        role='Technologie-Analyst',
        goal=f'Analysiere den technologischen Stand von {topic} für das Jahr 2026 auf Deutsch.',
        backstory="Du bist IT-Experte und lieferst präzise technische Fakten und Trends.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    strategist = Agent(
        role='Digital-Business-Stratege',
        goal=f'Entwickle 3 konkrete Business-Szenarien und ROI-Vorteile für {topic} auf Deutsch.',
        backstory="Du bist Unternehmensberater und findest wirtschaftliche Potenziale in jeder Technik.",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    designer = Agent(
        role='Visual-Designer & Kommunikator',
        goal='Erstelle ein Management-Summary auf Deutsch UND eine Infografik als SVG-Code.',
        backstory="""Du bist Profi für Datenvisualisierung. 
        Nutze für das SVG: Hintergrund #f8f9fa, Akzentfarbe #007bff, abgerundete Boxen und saubere Pfeile. 
        Schreibe alle Texte innerhalb der Grafik auf Deutsch.""",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )

    # 5. Aufgaben-Definition
    t1 = Task(description=f"Recherchiere technische Trends zu {topic} auf Deutsch.", agent=analyst, expected_output="Technische Analyse.")
    t2 = Task(description=f"Entwickle Business-Modelle für {topic} auf Deutsch.", agent=strategist, expected_output="3 Business-Szenarien.")
    t3 = Task(
        description=f"""Fasse alles in einem deutschen Bericht zusammen. 
        Erzeuge am Ende zwingend einen validen SVG-Code für eine Infografik (Breite 800px), 
        die den Prozess oder die Vorteile von {topic} visualisiert.""",
        agent=designer,
        expected_output="Ein ausführlicher Bericht und ein finaler <svg>...</svg> Codeblock."
    )

    # 6. Crew-Konfiguration (Mit Rate-Limit Bremse)
    crew = Crew(
        agents=[analyst, strategist, designer],
        tasks=[t1, t2, t3],
        max_rpm=2, # Verhindert 429-Fehler
        verbose=True
    )
    
    with st.spinner('Das Team berät sich (dies dauert ca. 45-60 Sekunden)...'):
        try:
            full_result = str(crew.kickoff())
            
            # 7. Ergebnisse verarbeiten (SVG extrahieren)
            if "<svg" in full_result:
                parts = full_result.split("<svg")
                text_part = parts[0]
                svg_part = "<svg" + parts[1].split("</svg>")[0] + "</svg>"
                
                st.success("Analyse und Design abgeschlossen!")
                
                # Spalten-Layout für Bericht und Grafik
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📄 Strategie-Bericht")
                    st.markdown(text_part)
                
                with col2:
                    st.subheader("📊 Infografik")
                    components.html(svg_part, height=600, scrolling=True)
                
                # Download-Option
                st.download_button("Bericht speichern", text_part, file_name="strategie.md")
            else:
                st.markdown(full_result)
                
        except Exception as e:
            if "429" in str(e):
                st.error("Google Rate-Limit erreicht. Bitte 60 Sek. warten.")
            else:
                st.error(f"Fehler: {e}")
