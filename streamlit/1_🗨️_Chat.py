import streamlit as st

# Creds
creds = {
    'apikey': 'OPENAI_API_KEY',
    'url': ''
}

# LLM
#llm = LangChainInterface(
#    credentials = creds,
#    model = '',
#    params = {
#        'decoding_method': 'sample',
#        'max_new_tokens': 200,
#        'temperature': 0.5,
#        'top_k': 10,
#        'top_p': 1.0,
#    },
#    project_id = ''
#)


# Generelles Layout
st.set_page_config(
    page_title="WIDB2 - RAG Chatbot",
    page_icon="🤖"
)

st.title("RAG Chatbot")
#st.sidebar.success("Select a page above.")


# Chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])


prompt = st.chat_input('Please enter your input')

# Bei User Input
if prompt:
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append({'role':'user', 'content':prompt})
    #response = llm(prompt)