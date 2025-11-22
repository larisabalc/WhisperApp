import streamlit as st
import json

def render(transcript: dict):
    """
    Display the live transcript with highlighting synced to media playback.
    """
    segments = transcript["segments"]
    json_segments = json.dumps([
        {"index": i, "start": seg["start"], "end": seg["end"], "text": seg["text"].strip()}
        for i, seg in enumerate(segments)
    ])

    with st.expander("Live Transcript", expanded=True):
        st.components.v1.html(f"""
        <style>
        .segment {{
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin-bottom: 0.25rem;
            font-family: "Source Sans Pro", sans-serif;
            font-size: 16px;
            line-height: 1.5;
        }}
        .active {{
            background-color: #ffe08a;
            transition: background 0.2s ease-in-out;
        }}
        #live_transcript {{
            font-family: "Source Sans Pro", sans-serif;
            font-size: 16px;
            line-height: 1.5;
            height: 450px;
            overflow-y: auto;
            padding: 0.5rem 1rem;
            border: 1px solid #eee;
            border-radius: 4px;
            background-color: white;
        }}
        </style>

        <div id="live_transcript"></div>

        <script>
        const segments = {json_segments};
        const container = document.getElementById('live_transcript');
        for (const seg of segments) {{
            const d = document.createElement('div');
            d.id = 'seg_' + seg.index;
            d.className = 'segment';
            d.innerText = seg.text;
            container.appendChild(d);
        }}

        const bc = new BroadcastChannel('media_sync');
        let lastActive = null;

        function setActive(index) {{
            if (lastActive !== null && lastActive !== index) {{
                const prev = document.getElementById('seg_' + lastActive);
                if (prev) prev.classList.remove('active');
            }}
            const el = document.getElementById('seg_' + index);
            if (el) {{
                el.classList.add('active');
                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
            lastActive = index;
        }}

        bc.onmessage = (ev) => {{
            try {{
                const msg = ev.data;
                if (!msg || msg.type !== 'time') return;
                const t = msg.currentTime;
                const idx = segments.findIndex(s => t >= s.start && t <= s.end);
                if (idx !== -1) setActive(idx);
            }} catch (err) {{
                console.error(err);
            }}
        }};
        </script>
        """, height=520)
