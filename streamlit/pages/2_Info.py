import streamlit as st

st.set_page_config(
    page_title="RAG-Chatbot ",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
## ℹ️ Weitere Informationen

### Features

- **Single/Mulit-Modus:** Ermöglicht es den gesamten Chatverlauf bei einer Anfrage mitzugeben. Falls dies nicht gegwünscht, sollte der Modus Single ausgewählt werden
- **Grafikerstelllung (Preview):** Ermöglicht es dass auf Basis der Anfrage Grafiken erstellt werden. Dieses Feature ist noch in Bearbeitung und kann zu Fehlern führen.
""")
