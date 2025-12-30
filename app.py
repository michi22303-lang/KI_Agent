import streamlit as st
from crewai import Agent, Task, Crew, LLM
import streamlit.components.v1 as components
import os

# 1. Seite konfigurieren (Wide Mode für bessere Übersicht)
st.set_page_config(page_title="Digital-Strategie & Interaktives Design", page_icon="🎨", layout="wide")

# 2. Key sicher aus Streamlit Secrets laden
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Fehler: GOOGLE_API_KEY wurde nicht in den Secrets gefunden.")
    st.stop()

# UI Header
st.title("🚀 Professionelles Strategie-Team & Interaktive Visualisierung")
st.markdown("Dieses Team aus 3 Agenten erstellt ein tiefgreifendes Dossier und eine interaktive Grafik.")

topic = st.text_input("Digitalisierungs-Thema für Tiefenanalyse:", "Automatisierung im Handwerk 2026")

if st.button("Umfassende Analyse & Interaktive Grafik starten"):
    
    # Gemini 2.0 Modell-Setup
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-lite", 
        api_key=google_key,
        temperature=0.6
    )
    
    # 3. Agenten-Definition (Auf Deutsch & Detailtiefe optimiert)
    analyst = Agent(
        role='Senior Technologie-Analyst',
        goal=f'Erstelle eine tiefgreifende technische Analyse zu {topic} auf Deutsch.',
        backstory="""Du bist bekannt für extrem detaillierte Berichte. Du untersuchst nicht nur Trends, 
        sondern auch technische Hürden, notwendige Infrastruktur und Datenschutzaspekte.""",
        llm=gemini_llm,
        max_iter=2,
        verbose=True
    )
    
    strategist = Agent(
        role='Strategischer Unternehmensberater',
        goal=f'Entwickle eine Roadmap und ROI-Analyse für {topic} auf Deutsch.',
        backstory="""Du erstellst Business-Szenarien, die auch Budgetplanung, 
        Mitarbeiter-Umschulung und langfristige Wettbewerbsvorteile enthalten.""",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )
    
    designer = Agent(
        role='Interaktiver Daten-Designer',
        goal='Erstelle ein ausführliches Management-Summary UND eine interaktive SVG-Infografik.',
        backstory="""Du beherrschst modernes UI/UX-Design. Erstelle SVG-Code mit integrierten CSS-Styles:
        - Nutze <style> Blöcke für hover-Effekte (Farbwechsel beim Drüberfahren).
        - Die Grafik muss professionell, deutsch und interaktiv sein.
        - Füge <title> Tags für Tooltips hinzu.""",
        llm=gemini_llm,
        max_iter=1,
        verbose=True
    )

    # 4. TASKS (Detailliert & Bug-frei)
    t1 = Task(
        description=f"Schreibe eine ausführliche Analyse über die technische Basis von {topic}.", 
        agent=analyst, 
        expected_output="Detaillierter technischer Bericht."
    )
    t2 = Task(
        description=f"Erstelle eine Schritt-für-Schritt Roadmap und 3 Business-Cases für {topic}.", 
        agent=strategist, 
        expected_output="Strategisches Dokument."
    )
    t3 = Task(
        description=f"""Kombiniere alle Informationen zu einem umfangreichen deutschen Gesamtdokument. 
        Erstelle danach eine interaktive SVG-Grafik (800x400px). 
        WICHTIG: Die Grafik muss interaktive CSS-Hover-Effekte enthalten (z.B. rect:hover {{ fill: #007bff; transition: 0.3s; }}). 
        Nutze doppelte geschweifte Klammern für CSS im f-string.""",
        agent=designer,
        expected_output="Ein sehr langer Bericht und ein interaktiver SVG-Codeblock."
    )

    # 5. Crew-Konfiguration (Mit Rate-Limit Bremse)
    crew = Crew(
        agents=[analyst, strategist, designer], 
        tasks=[t1, t2, t3], 
        max_rpm=2, 
        verbose=True
    )
    
    with st.spinner('Das Team erstellt ein umfassendes Dossier...'):
        try:
            full_result = str(crew.kickoff())
            
            # 6. Ergebnisse verarbeiten & SVG extrahieren
            if "<svg" in full_result:
                parts = full_result.split("<svg")
                text_part = parts[0]
                svg_part = "<svg" + parts[1].split("</svg>")[0] + "</svg>"
                
                st.success("Analyse abgeschlossen!")
                
                # Layout-Anzeige
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📄 Ausführliches Strategie-Dossier")
                    st.markdown(text_part)
                
                with col2:
                    st.subheader("🖱️ Interaktive Infografik")
                    st.info("Fahre mit der Maus über die Elemente, um Effekte zu sehen!")
                    # Zentriertes Rendering der SVG
                    components.html(
                        f"""<div style="display:flex; justify-content:center; align-items:center; font-family: sans-serif;">
                        {svg_part}
                        </div>""", 
                        height=500
                    )
                
                st.download_button("Vollständiges Dossier speichern", text_part, file_name="Digital_Dossier.md")
            else:
                st.markdown(full_result)
                
        except Exception as e:
            if "429" in str(e):
                st.error("Google-Limit erreicht. Bitte 60 Sekunden warten.")
            else:
                st.error(f"Ein Fehler ist aufgetreten: {e}")
