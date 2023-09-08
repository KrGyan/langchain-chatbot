import streamlit as st
from utils import add_logo
st.set_page_config(
    page_title="Marcel Chatbot",
    page_icon='💬',
    layout='wide'
)
add_logo()
st.header("Marcel Chat over Documents..")