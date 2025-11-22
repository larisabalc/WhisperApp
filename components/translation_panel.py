import streamlit as st

def render(translation: dict):
    """
    Display the translated text in a scrollable panel.
    """
    with st.expander("Translated Text", expanded=True):
        html = ""
        if "segments" in translation:
            for seg in translation["segments"]:
                t = seg["text"].strip()
                if t:
                    html += f"<div style='margin-bottom:5px'>{t}</div>"
        else:
            for line in translation["text"].split("\n"):
                if line.strip():
                    html += f"<div style='margin-bottom:5px'>{line}</div>"

        st.markdown(f"""
            <div style="height:450px; overflow-y:auto; border:1px solid #ccc; padding:10px;">
                {html}
            </div>
        """, unsafe_allow_html=True)
