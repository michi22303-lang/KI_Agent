import streamlit as st
from crewai import Agent, Task, Crew, LLM
import time

# 1. Seite konfigurieren
st.set_page_config(page_title="FM Strategie-Zentrum", page_icon="🏢", layout="wide")

# Session State initialisieren
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "slides" not in st.session_state: st.session_state.slides = []
if "current_slide" not in st.session_state: st.session_state.current_slide = 0

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Bitte API Key in den Streamlit Secrets hinterlegen.")
    st.stop()

st.title("🏢 Strategische Analyse & Interne Kommunikation")

# --- UI Layout: Status-Monitor (Fixiert oben) ---
st.subheader("Stations-Monitor")
status_cols = st.columns(4)
s1 = status_cols[0].empty()
s2 = status_cols[1].empty()
s3 = status_cols[2].empty()
s4 = status_cols[3].empty()

# Initialanzeige
s1.info("⚪ Technik-Check")
s2.info("⚪ ROI-Strategie")
s3.info("⚪ Mitarbeiter-Info")
s4.info("⚪ Leitungs-Statement")

st.divider()

topic = st.text_input("Thema für das Facility Management:", "Einführung von Robotik-Reinigungssystemen 2026")

log_area = st.empty()

# DEUTSCHER CALLBACK
def step_callback(step_output):
    try:
        # Wir übersetzen die Gedanken des Agenten ins Deutsche, falls nötig, 
        # oder geben eine deutsche Statusmeldung aus.
        log_area.warning(f"🕵️ **Der Agent denkt gerade nach:** Ich analysiere die Daten für '{topic}' und bereite den nächsten Schritt vor...")
    except:
        log_area.info("🕵️ Ein Agent plant den nächsten Schritt...")

if st.button("Umfassende Analyse & Slides starten"):
    gemini_llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=google_key, temperature=0.3)
    
    # --- Agenten-Definition ---
    analyst = Agent(
        role='Senior Technologie-Analyst', 
        goal=f'Schreibe eine extrem ausführliche technische Analyse über {topic} auf Deutsch.', 
        backstory="Du bist IT-Experte. Du schreibst lange, technische Texte ohne Abkürzungen.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )
    strategist = Agent(
        role='Strategischer Business-Planer', 
        goal=f'Erstelle eine detaillierte Roadmap und ROI-Tabelle für {topic} auf Deutsch.', 
        backstory="Du bist der Wirtschaftsexperte. Du lieferst Zahlen und Fakten.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )
    marketing = Agent(
        role='Interne Kommunikation', 
        goal='Erstelle 6 motivierende Mitarbeiter-Slides auf Deutsch.', 
        backstory="Du erklärst Technik einfach und positiv für das Team.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )
    head_of_digital = Agent(
        role='Leiter Digitalisierung', 
        goal='Fasse ALLE Berichte zusammen und schreibe das finale Statement auf Deutsch.', 
        backstory="Du stellst sicher, dass im fertigen Dokument alle Inhalte der Kollegen VOLLSTÄNDIG enthalten sind.", 
        llm=gemini_llm, step_callback=step_callback, verbose=True
    )

    # --- Tasks (Mit expliziter Anweisung zum Kopieren der Inhalte) ---
    t1 = Task(
        description=f"Analysiere {topic} technisch sehr ausführlich auf Deutsch. (Min. 500 Wörter)", 
        agent=analyst, expected_output="Technischer Bericht."
    )
    t2 = Task(
        description=f"Erstelle eine wirtschaftliche Roadmap für {topic} auf Deutsch. (Min. 400 Wörter)", 
        agent=strategist, expected_output="Strategie-Bericht."
    )
    t3 = Task(
        description=f"Erstelle 6 Slides für die Mitarbeiter. Nutze das Trennwort SLIDETRENNER zwischen den Folien.", 
        agent=marketing, expected_output="Mitarbeiter-Folien."
    )
    t4 = Task(
        description="""Kombiniere den VOLLSTÄNDIGEN technischen Bericht von Task 1 und die VOLLSTÄNDIGE Roadmap von Task 2 zu einem großen Dossier. 
        Schreibe NICHT 'siehe oben', sondern kopiere die Texte hier hinein. 
        Füge am Ende dein Statement zur Relevanz für unser Unternehmen an (200 Wörter). 
        Hänge danach alle Slides an, getrennt durch SLIDETRENNER.""", 
        agent=head_of_digital, expected_output="Das komplette Dossier inklusive aller Details und Slides."
    )

    crew = Crew(agents=[analyst, strategist, marketing, head_of_digital], tasks=[t1, t2, t3, t4], max_rpm=1)
    
    # --- Manueller Status-Wechsel ---
    s1.warning("🔵 Technik aktiv...")
    with st.spinner("Analyst arbeitet..."):
        # Da CrewAI sequenziell arbeitet, können wir die Status-Updates 
        # nur bedingt timen, aber wir setzen sie hier nacheinander.
        result = str(crew.kickoff())
        
    s1.success("✅ Technik fertig")
    s2.success("✅ Strategie fertig")
    s3.success("✅ Marketing fertig")
    s4.success("✅ Leitung fertig")
    
    st.session_state.full_report = result
    
    # Slides verarbeiten
    if "SLIDETRENNER" in result:
        parts = result.split("SLIDETRENNER")
        # Der erste Teil ist das Dossier, der Rest sind Slides
        st.session_state.slides = [p.strip() for p in parts[1:] if len(p.strip()) > 10]
    
    log_area.empty()

# --- Anzeige der Ergebnisse ---
if st.session_state.full_report:
    tab1, tab2 = st.tabs(["📄 Management-Dossier", "🖥️ Mitarbeiter-Info"])
    
    with tab1:
        # Zeige alles vor dem ersten SLIDETRENNER (Das Dossier)
        dossier = st.session_state.full_report.split("SLIDETRENNER")[0]
        st.markdown(dossier)

    with tab2:
        if st.session_state.slides:
            col_n1, col_s, col_n2 = st.columns([1, 4, 1])
            if col_n1.button("⬅️ Zurück"): 
                st.session_state.current_slide = max(0, st.session_state.current_slide - 1)
                st.rerun()
            if col_n2.button("Vorwärts ➡️"): 
                st.session_state.current_slide = min(len(st.session_state.slides)-1, st.session_state.current_slide + 1)
                st.rerun()
                
            with col_s:
                curr = st.session_state.current_slide
                st.markdown(f"""
                    <div style="background-color: #f0f4f8; padding: 40px; border-radius: 20px; border-left: 10px solid #2c3e50; min-height: 350px;">
                        <h4 style="color: #2c3e50;">Mitarbeiter-Präsentation</h4>
                        <hr>
                        <div style="font-family: sans-serif; font-size: 1.1em;">
                            {st.session_state.slides[curr]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Keine Slides gefunden. Bitte Analyse erneut starten.")

    st.download_button("Dossier & Slides speichern", st.session_state.full_report, file_name="FM_Dossier_Komplett.md")
