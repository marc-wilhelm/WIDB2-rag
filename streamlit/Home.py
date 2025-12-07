import streamlit as st

# Seitenkonfiguration
st.set_page_config(
    page_title="WIDB2 - RAG System",
    page_icon="🏠",
    layout="wide"
)

# Hauptseite
st.title("🏠 WIDB2 RAG-System")
st.markdown("### Prototypische Implementierung eines RAG-Systems für BWA-Analyse")

st.markdown("---")

# Beschreibung
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## 👋 Willkommen!

    Dieses System ermöglicht es dir, natürlichsprachige Fragen zu Controlling-Berichten zu stellen.
    Das RAG (Retrieval-Augmented Generation) System kombiniert:

    - 📄 **Dokumenten-Retrieval**: Suche nach relevanten Textabschnitten
    - 🧠 **LLM-Generation**: Intelligente Antworten mit Claude
    - ✅ **Faktenbasiert**: Antworten nur auf Basis der verfügbaren Dokumente

    ### 🚀 So funktioniert's:

    1. Gehe zur **Chat**-Seite in der Sidebar
    2. Stelle deine Frage zu den Monatsberichten
    3. Erhalte präzise Antworten mit Quellenangaben

    ### 📊 Verfügbare Daten:

    - BWA-Musterdaten (2023-2024)
    - Monatliche Controlling-Berichte
    - Analysen zu Umsatz, Kosten und Betriebsergebnis
    """)

with col2:
    st.info("""
    ### ℹ️ Technologie-Stack

    **Backend:**
    - Python 3.12
    - ChromaDB (Vektordatenbank)
    - Sentence Transformers
    - Claude API

    **Frontend:**
    - Streamlit

    **Datenquellen:**
    - Markdown-Berichte
    - CSV-Musterdaten
    """)

    st.success("""
    ### ✨ Features

    - ✅ Mehrsprachig (Deutsch)
    - ✅ Semantische Suche
    - ✅ Quellenangaben
    - ✅ Kontextbewusstsein
    """)

st.markdown("---")

# Beispiel-Fragen
st.markdown("### 💡 Beispiel-Fragen")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Allgemeine Fragen:**
    - Welche Monate werden behandelt?
    - Gib mir eine Übersicht über die Berichte
    """)

with col2:
    st.markdown("""
    **Spezifische Analysen:**
    - Wie waren die Umsatzerlöse im Januar 2023?
    - In welchem Monat war das Betriebsergebnis am höchsten?
    """)

with col3:
    st.markdown("""
    **Vergleiche:**
    - Wie entwickelten sich die Kosten über die Monate?
    - Welche Faktoren beeinflussten das Ergebnis?
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>WIDB2 - Business Analytics Project II | THWS Business School</p>
    <p>Entwickelt als Prototyp für RAG-basierte Dokumentenanalyse</p>
</div>
""", unsafe_allow_html=True)