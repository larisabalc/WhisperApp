import streamlit as st
from streamlit_ace import st_ace
import io
from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter

def render(transcript: dict, font_family="DejaVu", font_size=16, line_height=1.5):
    """
    Editable Transcript panel using ACE editor.
    Fixes Ctrl+F search bar visibility inside Streamlit column.
    Allows export to TXT and PDF with selected font, size, and line height.
    """

    # --- Combine transcript segments into a single text ---
    segments = transcript["segments"]
    original_text = "\n".join(seg["text"].strip() for seg in segments)

    # --- Persistent edited text in session state ---
    if "edited_text" not in st.session_state:
        st.session_state["edited_text"] = original_text

    st.subheader("Edit Transcript (CTRL + F to search)")

    # --- CSS fixes for ACE editor ---
    st.markdown("""
    <style>
    [data-testid="stAce"], .ace_editor, .ace_scroller, .ace_content {
        width: 100% !important;
        max-width: 100% !important;
    }
    .ace_editor {
        overflow: visible !important;
        position: relative !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- ACE Editor ---
    new_text = st_ace(
        value=st.session_state["edited_text"],
        language="text",
        theme="chrome",
        height=400,
        font_size=font_size,
        wrap=True,
        show_gutter=False,
        show_print_margin=False,
        key="editable_ace"
    )
    if new_text is not None:
        st.session_state["edited_text"] = new_text

    # --- PDF export function ---
    def make_pdf(text, font_family=font_family, font_size=font_size, line_height=line_height):
        buffer = io.BytesIO()

        # Map font family to system font paths
        font_map = {
            "Arial": "C:/Windows/Fonts/arial.ttf",
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

        font_path = font_map.get(font_family, font_map["DejaVu"])
        font_name = f"{font_family}_Custom"

        # Register the font
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception as e:
            print("Font registration failed:", e)
            font_name = "Helvetica"  # fallback

        # Setup PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=40,
            bottomMargin=40,
            leftMargin=50,
            rightMargin=50
        )

        # Preformatted style preserves line breaks and spacing
        style = ParagraphStyle(
            "TranscriptStyle",
            fontName=font_name,
            fontSize=font_size,
            leading=font_size * line_height
        )

        story = [Preformatted(text, style)]
        doc.build(story)
        buffer.seek(0)
        return buffer

    # --- Export buttons ---
    st.subheader("Export Edited Transcript")

    st.download_button(
        "Download TXT",
        st.session_state["edited_text"],
        file_name="edited_transcript.txt",
        mime="text/plain"
    )

    st.download_button(
        "Download PDF",
        make_pdf(st.session_state["edited_text"]),
        file_name="edited_transcript.pdf",
        mime="application/pdf"
    )
