import streamlit as st

def render(transcript: dict):
    """
    Display an editable transcript for manual corrections.
    """
    segments = transcript["segments"]
    editable_text = "\n".join(seg["text"].strip() for seg in segments)
    with st.expander("Editable Transcript", expanded=True):
        st.text_area("Edit here", value=editable_text, height=450)
