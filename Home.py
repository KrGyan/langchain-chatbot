import streamlit as st
from utils import add_marcel_logo
st.set_page_config(
    page_title="Marcel Chatbot",
    page_icon='💬',
    layout='wide'
)
add_marcel_logo()
st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.header("Marcel Chat over Documents..")