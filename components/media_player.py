import streamlit as st
from utils.media_helpers import media_to_base64

def render(media_path: str):
    media_base64 = media_to_base64(media_path)
    ext = media_path.split(".")[-1].lower()
    video_exts = ["mp4", "mov", "mkv"]

    if ext in video_exts:
        st.components.v1.html(f"""
        <video id="media_player" controls style="width:100%; max-height:100%;">
            <source src="{media_base64}">
            Your browser does not support the video tag.
        </video>
        <script>
        const video = document.getElementById('media_player');
        const bc = new BroadcastChannel('media_sync');
        function sendTime() {{ bc.postMessage({{ type: 'time', currentTime: video.currentTime }}); }}
        let interval = null;
        video.addEventListener('play', () => {{ sendTime(); interval = setInterval(sendTime, 150); }});
        video.addEventListener('pause', () => {{ sendTime(); if (interval) clearInterval(interval); }});
        video.addEventListener('seeking', sendTime);
        video.addEventListener('seeked', sendTime);
        </script>
        """, height=140)
    else:
        st.components.v1.html(f"""
        <audio id="media_player" controls style="width:100%; display:block;" preload="metadata">
            <source src="{media_base64}">
            Your browser does not support the audio tag.
        </audio>
        <script>
        const audio = document.getElementById('media_player');
        const bc = new BroadcastChannel('media_sync');
        function sendTime() {{ bc.postMessage({{ type: 'time', currentTime: audio.currentTime }}); }}
        let interval = null;
        audio.addEventListener('play', () => {{ sendTime(); interval = setInterval(sendTime, 150); }});
        audio.addEventListener('pause', () => {{ sendTime(); if (interval) clearInterval(interval); }});
        audio.addEventListener('seeking', sendTime);
        audio.addEventListener('seeked', sendTime);
        </script>
        """, height=70)
