import streamlit as st

def reset_session_state(keys: list):
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
