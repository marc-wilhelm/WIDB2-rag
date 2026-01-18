import streamlit as st

# Seitenkonfiguration
st.set_page_config(
    page_title="RAG-Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Hauptseite
st.title("RAG-Chatbot für BWA")
st.markdown("### Prototypische Implementierung eines dokumenten-basierten Chatbots")

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

    - Bericht zur Geschäftsentwicklung der Business Unit „Digital Solutions“ – Januar bis April 2023
    - Analyse der monatlichen Schwankungen des Betriebsergebnisses der Business Unit "Home Tech" in 2023
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>WIDB2 | Wintersemester 2025/2026 | THWS Business School</p>
    <p>Entwickelt als Prototyp für RAG-basierte Dokumentenanalyse</p>
</div>
""", unsafe_allow_html=True)