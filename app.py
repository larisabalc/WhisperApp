import os
import streamlit as st
from utils.whisper.whisper_service import transcribe, translate
from utils.media_helpers import media_to_base64
from utils.state_helpers import reset_session_state
from components import (
    media_player, live_transcript, editable_transcript, translation_panel
)

UPLOAD_DIR = "assets/temp_uploads/"

st.set_page_config(layout="wide")
st.title("Whisper Transcription & Translation App")

# -----------------------------
# Top menu
# -----------------------------
mode = st.selectbox("Select mode:", ["Transcribe", "Translate"])

if "mode_selected" not in st.session_state:
    st.session_state["mode_selected"] = mode
elif st.session_state["mode_selected"] != mode:
    reset_session_state(keys=["transcript", "translation", "media_path"])
    st.session_state["mode_selected"] = mode

# -----------------------------
# Conditional columns
# -----------------------------
if mode == "Transcribe":
    col_media, col_live, col_edit = st.columns([3, 4, 5])
else:
    col_media, col_live, col_edit, col_translation = st.columns([3, 3, 3, 3])

# -----------------------------
# Media upload & player
# -----------------------------
with col_media:
    media_placeholder = st.empty() 
    uploaded_file = st.file_uploader(
        "Upload a video or audio file",
        type=["mp4", "mov", "mkv", "wav", "mp3", "m4a"],
        key="uploader"
    )

    if uploaded_file is None:
        reset_session_state(["media_path", "transcript", "translation"])
        media_placeholder.empty()

    if uploaded_file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        media_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(media_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["media_path"] = media_path

    if "media_path" in st.session_state:
        media_player.render(st.session_state["media_path"])

        if st.button("Send / Process"):
            with st.spinner(f"Running Whisper {mode.lower()}..."):
                result = transcribe(st.session_state["media_path"])
                st.session_state["transcript"] = result
                if mode == "Translate" and result.get("language") != "en":
                    st.session_state["translation"] = translate(st.session_state["media_path"])
            st.success(f"{mode} complete!")

# -----------------------------
# After processing
# -----------------------------
if "transcript" in st.session_state:
    result = st.session_state["transcript"]

    # Live transcript
    with col_live:
        live_transcript.render(result)

    # Editable transcript
    with col_edit:
        editable_transcript.render(result)

    # Translation panel (Translate mode)
    if mode == "Translate" and "translation" in st.session_state:
        with col_translation:
            translation_panel.render(st.session_state["translation"])