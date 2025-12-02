import streamlit as st
from streamlit_ace import st_ace
import io
from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter

def render(translation: dict, font_family="DejaVu", font_size=16, line_height=1.5):
    """
    Editable Translation Panel:
    - ACE editor-like editable area
    - Search bar outside editor
    - Export TXT + PDF with chosen font, size, line height
    """

    if "segments" in translation:
        lines = []
        for seg in translation["segments"]:
            t = seg.get("translation") or seg.get("text", "")
            t = t.strip()
            if t:
                lines.append(t)

        # Join with newline
        output_text = "\n".join(lines)

    # If no segments, fallback to text key
    else:
        lines = []
        for line in translation.get("text", "").split("\n"):
            line = line.strip()
            if line:
                lines.append(line)

    output_text = "\n".join(lines)
    print(output_text)

    if "edited_translation" not in st.session_state:
        st.session_state["edited_translation"] = output_text

    # --- CSS for ACE editor look ---
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

    # --- Editable ACE-style editor ---

    new_text = st_ace(
        value=st.session_state["edited_translation"],
        language="text",
        theme="chrome",
        height=400,
        font_size=font_size,
        wrap=True,
        show_gutter=False,
        show_print_margin=False,
        key="editable_translation_ace"
    )

    if new_text is not None:
        st.session_state["edited_translation"] = new_text

    # --- PDF export function ---
    def make_pdf(text):
        buffer = io.BytesIO()

        # Font map
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

        # Register font
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except:
            font_name = "Helvetica"

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=40,
            bottomMargin=40,
            leftMargin=50,
            rightMargin=50
        )

        style = ParagraphStyle(
            "TranslationStyle",
            fontName=font_name,
            fontSize=font_size,
            leading=font_size * line_height
        )

        story = [Preformatted(text, style)]
        doc.build(story)
        buffer.seek(0)
        return buffer

    # --- Export buttons ---
    st.subheader("Export Edited Translation")

    st.download_button(
        "Download as TXT",
        st.session_state["edited_translation"],
        file_name="edited_translation.txt",
        mime="text/plain"
    )

    st.download_button(
        "Download as PDF",
        make_pdf(st.session_state["edited_translation"]),
        file_name="edited_translation.pdf",
        mime="application/pdf"
    )
