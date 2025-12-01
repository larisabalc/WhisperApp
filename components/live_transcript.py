import streamlit as st
import json
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT


def render(transcript: dict, font_family="DejaVu", font_size=16, line_height=1.5):

    segments = transcript["segments"]
    
    
    full_text = "\n".join(seg["text"].strip() for seg in segments) 

    json_segments = json.dumps([
        {
            "index": i,
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
            
        }
        for i, seg in enumerate(segments)
    ])

    # SEARCH BAR 
    search_query = st.text_input(
        "Search in Live Transcript:",
        key="live_search"
    )
    
    search_query_encoded = json.dumps(search_query)

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
            background-color: #ffe08a; /* Sarı zemin */
            color: #111111 !important; /* DÜZELTME: Metin rengini koyu yaparak okunur hale getirir */
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
            
            if (searchQuery.trim() === "") {{
                for (const seg of segments) {{
                    const d = document.createElement('div');
                    d.id = 'seg_' + seg.index;
                    d.className = 'segment';
                    d.innerText = seg.text;
                    container.appendChild(d);
                }}
            }} else {{
                const queryLower = searchQuery.toLowerCase();
                
                // Regex oluşturma ve özel karakter kaçışı
                const regex = new RegExp('(' + queryLower.replace(/[.*+?^${{}}()|[\]\\]/g, '\\$&') + ')', 'gi');

                for (const seg of segments) {{
                    const d = document.createElement('div');
                    d.id = 'seg_' + seg.index;
                    d.className = 'segment';
                    
                    // Eşleşenleri bul ve <span> ile sar
                    const highlightedText = seg.text.replace(regex, (match) => {{
                        return `<span class="highlight">${{match}}</span>`;
                    }});
                    
                    d.innerHTML = highlightedText;
                    container.appendChild(d);
                }}
            }}
        }}
        
        renderSegments();


        const bc = new BroadcastChannel('media_sync');

        function setActive(index) {{
            if (lastActive !== null && lastActive !== index) {{
                const prev = document.getElementById('seg_' + lastActive);
                if (prev) {{
                    prev.classList.remove('active');
                }}
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
        
    # PDF EXPORT — overflow fix + auto-wrap

    def make_pdf(text):

        buffer = io.BytesIO()

        # Map Streamlit-selected font to a Windows system font
        font_map = {
            "Arial": "C:/Windows/Fonts/arial.ttf",
            "Helvetica": "C:/Windows/Fonts/arial.ttf",
            "Verdana": "C:/Windows/Fonts/verdana.ttf",
            "Tahoma": "C:/Windows/Fonts/tahoma.ttf",
            "Trebuchet MS": "C:/Windows/Fonts/trebuc.ttf",
            "Segoe UI": "C:/Windows/Fonts/segoeui.ttf",
            "Calibri": "C:/Windows/Fonts/calibri.ttf",
            "Century Gothic": "C:/Windows/Fonts/gothic.ttf",
            "Times New Roman": "C:/Windows/Fonts/times.ttf",
            "Georgia": "C:/Windows/Fonts/georgia.ttf",
            "Garamond": "C:/Windows/Fonts/garamond.ttf",
            "Cambria": "C:/Windows/Fonts/cambria.ttf",
            "Palatino Linotype": "C:/Windows/Fonts/pala.ttf",
            "Courier New": "C:/Windows/Fonts/cour.ttf",
            "Consolas": "C:/Windows/Fonts/consola.ttf",
            "Lucida Console": "C:/Windows/Fonts/lucon.ttf",
            "DejaVu": "C:/Windows/Fonts/DejaVuSans.ttf"
        }

        chosen_font = font_map.get(font_family, "C:/Windows/Fonts/DejaVuSans.ttf")

        # Register chosen font
        pdfmetrics.registerFont(TTFont("CustomFont", chosen_font))

        # Create PDF document with proper margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=40,
            bottomMargin=40,
            leftMargin=50,
            rightMargin=50
        )

        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "CustomFont"
        style.fontSize = font_size
        style.leading = font_size * line_height
        style.alignment = TA_LEFT

        story = []

        # Convert every line to an auto-wrapped Paragraph
        for line in text.split("\n"):
            story.append(Paragraph(line, style))

        doc.build(story)
        buffer.seek(0)
        return buffer

    # EXPORT BUTTONS 
 
    st.subheader("Export Live Transcript")

    st.download_button(
        "Download as TXT",
        full_text,
        file_name="live_transcript.txt",
        mime="text/plain"
    )

    st.download_button(
        "Download as PDF",
        make_pdf(full_text),
        file_name="live_transcript.pdf",
        mime="application/pdf"
    )
