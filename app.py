import os
import streamlit as st
from utils.whisper.whisper_service import transcribe, translate
from utils.state_helpers import reset_session_state
from components import (
    media_player, live_transcript, editable_transcript, translation_panel
)

UPLOAD_DIR = "assets/temp_uploads/"

st.set_page_config(layout="wide")
st.title("Whisper Transcription & Translation App")

# SIDEBAR STYLE SETTINGS

st.sidebar.subheader("Style Settings")
font_size = st.sidebar.slider("Font Size", 12, 36, 16)
line_height = st.sidebar.slider("Line Height", 1.0, 3.0, 1.5, step=0.1)
font_family = st.sidebar.selectbox(
    "Font Family",
    [
        "Arial", "Helvetica", "Verdana", "Tahoma",
        "Trebuchet MS", "Segoe UI", "Calibri", "Century Gothic",
        "Times New Roman", "Georgia", "Garamond", "Cambria",
        "Palatino Linotype", "Courier New", "Consolas", "Lucida Console"
    ]
)

# MODE SELECTION

mode = st.selectbox("Select mode:", ["Transcribe", "Translate"])

if "mode_selected" not in st.session_state:
    st.session_state["mode_selected"] = mode
elif st.session_state["mode_selected"] != mode:
    reset_session_state(keys=["transcript", "translation", "media_path"])
    st.session_state["mode_selected"] = mode

# LAYOUT

if mode == "Transcribe":
    col_media, col_live = st.columns([3, 4])
else:
    col_media, col_live= st.columns([3, 3])

# MEDIA UPLOAD

with col_media:

    # Voice recording 
    st.subheader("Record Audio")
    audio_bytes = st.audio_input("Record your voice")

    if audio_bytes:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        audio_path = os.path.join(UPLOAD_DIR, "recorded_audio.wav")


        if hasattr(audio_bytes, "getbuffer"):   # UploadedFile object
            raw_bytes = audio_bytes.getbuffer()
        else:                                   
            raw_bytes = audio_bytes

        with open(audio_path, "wb") as f:
            f.write(raw_bytes)

        st.session_state["media_path"] = audio_path
        st.success("Audio recording saved!")


    st.divider()

    # --- FILE UPLOAD ---
    uploaded_file = st.file_uploader(
        "Upload a video or audio file",
        type=["mp4", "mov", "mkv", "wav", "mp3", "m4a"],
        key="uploader"
    )

    if uploaded_file is None and audio_bytes is None:
        reset_session_state(["media_path", "transcript", "translation"])

    if uploaded_file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        media_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(media_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["media_path"] = media_path

    # --- MEDIA PLAYER ---
    if "media_path" in st.session_state:
        media_player.render(st.session_state["media_path"])

        if st.button("Send / Process"):
            with st.spinner(f"Running Whisper {mode.lower()}..."):
                result = transcribe(st.session_state["media_path"])
                st.session_state["transcript"] = result

                if mode == "Translate":
                    st.session_state["translation"] = translate(
                        st.session_state["media_path"]
                    )

            st.success(f"{mode} complete!")

# AFTER PROCESSING

if "transcript" in st.session_state:

    # LIVE PANEL 
    with col_live:
        live_transcript.render(
            st.session_state["transcript"],
            font_family=font_family,
            font_size=font_size,
            line_height=line_height
        )

    # TRANSCRIBE MODEL
    if mode == "Transcribe":
        editable_transcript.render(
            st.session_state["transcript"],
            font_family=font_family,
            font_size=font_size,
            line_height=line_height
        )


    # TRANSLATE MODE 
    if mode == "Translate" and "translation" in st.session_state:
        translation_panel.render(
            st.session_state["translation"],
            font_family=font_family,
            font_size=font_size,
            line_height=line_height
        )
