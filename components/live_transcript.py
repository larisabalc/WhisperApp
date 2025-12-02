import streamlit as st
import json

def render(transcript: dict, font_family="DejaVu", font_size=16, line_height=1.5):
    """
    Live transcript panel with search and synchronized highlighting.
    Displays transcript segments in a scrollable container with active segment highlighting.
    """

    # --- Combine transcript segments ---
    segments = transcript["segments"]
    full_text = "\n".join(seg["text"].strip() for seg in segments)

    # Prepare JSON for front-end
    json_segments = json.dumps([
        {
            "index": i,
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        }
        for i, seg in enumerate(segments)
    ])

    # --- Search bar ---
    search_query = st.text_input("Search in Live Transcript:", key="live_search")
    search_query_encoded = json.dumps(search_query)

    # --- Live Transcript Expander ---
    with st.expander("Live Transcript", expanded=True):
        st.components.v1.html(
            rf"""
            <style>
            /* --- THEME-AWARE COLORS --- */
            :root {{
                --bg-color: #ffffff;
                --text-color: #000000;
                --border-color: #e6e6e6;
            }}
            @media (prefers-color-scheme: dark) {{
                :root {{
                    --bg-color: #111111;
                    --text-color: #f2f2f2;
                    --border-color: #333333;
                }}
            }}

            #live_transcript {{
                font-family: {font_family};
                font-size: {font_size}px;
                line-height: {line_height};
                height: 450px;
                overflow-y: auto;
                padding: 0.5rem 1rem;
                border: 1px solid var(--border-color);
                border-radius: 4px;
                background-color: var(--bg-color);
                color: var(--text-color);
            }}

            .segment {{
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                margin-bottom: 0.25rem;
                font-family: {font_family};
                font-size: {font_size}px;
                line-height: {line_height};
                color: var(--text-color);
            }}

            .active {{
                background-color: #ffe08a;
                color: #111111 !important;
                transition: background 0.2s ease-in-out;
            }}

            .highlight {{
                color: red;
                font-weight: bold;
                background-color: transparent;
            }}
            </style>

            <div id="live_transcript"></div>

            <script>
            const segments = {json_segments};
            const container = document.getElementById('live_transcript');
            const searchQuery = {search_query_encoded};
            let lastActive = null;

            function renderSegments() {{
                container.innerHTML = '';
                const query = searchQuery.trim().toLowerCase();

                for (const seg of segments) {{
                    const d = document.createElement('div');
                    d.id = 'seg_' + seg.index;
                    d.className = 'segment';

                    if (query) {{
                        // Escape special regex characters
                        const regex = new RegExp('(' + query.replace(/[.*+?^${{}}()|[\]\\]/g, '\\$&') + ')', 'gi');
                        d.innerHTML = seg.text.replace(regex, (match) => `<span class="highlight">${{match}}</span>`);
                    }} else {{
                        d.innerText = seg.text;
                    }}
                    container.appendChild(d);
                }}
            }}

            renderSegments();

            const bc = new BroadcastChannel('media_sync');

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
            """,
            height=520
        )
