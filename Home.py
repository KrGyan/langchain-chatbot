import streamlit as st
import utils
st.set_page_config(
    page_title="Langchain Chatbot",
    page_icon='💬',
    layout='wide'
)

st.header("Marcel Chat over Documents..")

@utils.add_logo