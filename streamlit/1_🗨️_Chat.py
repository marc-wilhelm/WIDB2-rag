import streamlit as st

st.set_page_config(
    page_title="WIDB2 - RAG Chatbot",
    page_icon="🤖"
)

st.title("RAG Chatbot")
st.sidebar.success("Select a page above.")


if "my_input" not in st.session_state:
    st.session_state["my_input"] = None

my_input = st.text_input("Gebe hier deine Eingabe ein", st.session_state["my_input"])
submit_button = st.button("Submit")
if submit_button:
    st.session_state["my_input"] = my_input
    st.write("Du hast eingegeben: ", my_input)