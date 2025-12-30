import streamlit as st
from crewai import Agent, Task, Crew, LLM
import streamlit.components.v1 as components
import os

# Seite konfigurieren
st.set_page_config(page_title="Digital-Strategie & Interaktives Design", page_icon="🎨", layout="wide")

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY nicht gefunden.")
    st.stop()

st.title("🚀 Professionelles Strategie-Team & Interaktive Visualisierung")

topic = st.text_input("Digitalisierungs-Thema für Tiefenanalyse:", "Automatisierung im Handwerk 2026")

if st.button("Umfassende Analyse & Interaktive Grafik starten"):
    
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.6
    )
    
    # 1. Agent: Senior Analyst (Mehr Details)
    analyst = Agent(
        role='Senior Technologie-Analyst',
        goal=f'Erstelle eine tiefgreifende technische Analyse zu {topic} auf Deutsch.',
        backstory="""Du bist bekannt für extrem detaillierte Berichte. Du untersuchst nicht nur Trends, 
        sondern auch technische Hürden, notwendige Infrastruktur und Datenschutzaspekte.""",
        llm=gemini_llm,
        max_iter=2 # Darf zweimal nachdenken für mehr Tiefe
    )
    
    # 2. Agent: Business Stratege (Implementierung)
    strategist = Agent(
        role='Strategischer Unternehmensberater',
        goal=f'Entwickle eine Roadmap und ROI-Analyse für {topic} auf Deutsch.',
        backstory="""Du erstellst Business-Szenarien, die auch Budgetplanung, 
        Mitarbeiter-Umschulung und langfristige Wettbewerbsvorteile enthalten.""",
        llm=gemini_llm,
        max_iter=1
    )
    
    # 3. Agent: Visual Designer (Interaktives SVG)
    designer = Agent(
        role='Interaktiver Daten-Designer',
        goal='Erstelle ein ausführliches Management-Summary UND eine interaktive SVG-Infografik.',
        backstory="""Du beherrschst modernes UI/UX-Design. Erstelle SVG-Code mit integrierten CSS-Styles:
        - Füge <style> Blöcke hinzu für hover-Effekte (z.B. Boxen werden heller beim Drüberfahren).
        - Nutze Animationen (<animate> oder CSS transitions).
        - Die Grafik muss professionell, deutsch und interaktiv sein.""",
        llm=gemini_llm,
        max_iter=1
    )

    # TASKS (Ausführlicher formuliert)
    t1 = Task(
        description=f"Schreibe eine 500-Wörter Analyse über die technische Basis von {topic}.", 
        agent=analyst, 
        expected_output="Detaillierter technischer Bericht."
    )
    t2 = Task(
        description=f"Erstelle eine Schritt-für-Schritt Roadmap und 3 Business-Cases für {topic}.", 
        agent=strategist, 
        expected_output="Strategisches Dokument."
    )
    t3 = Task(
        description=f"""Kombiniere alle Infos zu einem umfangreichen deutschen Gesamtdokument. 
        Erstelle danach eine interaktive SVG-Grafik (800x400px). 
        Die Grafik soll CSS-Hover-Effekte enthalten (z.B. 'rect:hover {fill: #0056b3;}').""",
        agent=designer,
        expected_output="Ein sehr langer Bericht und ein interaktiver SVG-Code."
    )

    crew = Crew(agents=[analyst, strategist, designer], tasks=[t1, t2, t3], max_rpm=2)
    
    with st.spinner('Das Team erstellt ein umfassendes Dossier...'):
        try:
            full_result = str(crew.kickoff())
            
            if "<svg" in full_result:
                parts = full_result.split("<svg")
                text_part = parts[0]
                svg_part = "<svg" + parts[1].split("</svg>")[0] + "</svg>"
                
                st.success("Analyse abgeschlossen!")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📄 Ausführliches Strategie-Dossier")
                    st.markdown(text_part)
                
                with col2:
                    st.subheader("🖱️ Interaktive Infografik (Hover über die Elemente!)")
                    # Das HTML-Komponent braucht etwas mehr Höhe für interaktive SVGs
                    components.html(f"<div style='display:flex; justify-content:center;'>{svg_part}</div>", height=500)
                
                st.download_button("Vollständiges Dossier speichern", text_part, file_name="Digital_Dossier.md")
            else:
                st.markdown(full_result)
        except Exception as e:
            st.error(f"Fehler: {e}")
