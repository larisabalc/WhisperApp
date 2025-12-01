import streamlit as st
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

def render(translation: dict, font_family="DejaVu", font_size=16, line_height=1.5):
    """
    Editable Translation Panel (clean layout, no white gaps):
    - Search bar outside expander (fixes top white space)
    - Scrollable preview
    - Editable text area
    - Case-insensitive search + highlight
    - Export TXT + PDF (with auto-wrap, no text overflow)
    """

    translated_text = translation.get("text", "").strip()

    if "edited_translation" not in st.session_state:
        st.session_state["edited_translation"] = translated_text

    edited_text = st.session_state["edited_translation"]

    # SEARCH BAR 

    search_query = st.text_input(
        "Search in Translation:",
        key="translation_search"
    )

    display_text = edited_text

    if search_query:
        low = edited_text.lower()
        q = search_query.lower()

        if q in low:
            start = low.index(q)
            end = start + len(search_query)

            original = edited_text[start:end]

            display_text = edited_text.replace(
                original,
                f"<span style='color:red; font-weight:bold'>{original}</span>"
            )

    # EXPANDER 

    with st.expander("Editable Translation"):
        # Scrollable Preview
        st.markdown(
            f"""
            <div style="
                height: 450px;
                overflow-y: auto;
                border: 1px solid rgba(255,255,255,0.15);
                padding: 12px;
                border-radius: 6px;
                background: transparent;
                width: 100%;
                max-width: 100%;
                font-size: {font_size}px;
                line-height: {line_height};
                font-family: {font_family};
                color: inherit;
            ">
                {display_text.replace("\n", "<br>")}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Editable Text Area
        new_text = st.text_area(
            "Edit Translation:",
            value=edited_text,
            height=250,
            key="editable_translation_box"
        )

        st.session_state["edited_translation"] = new_text

    # FIXED PDF EXPORT (no overflow, auto-line-wrap)

    def make_pdf(text):

        buffer = io.BytesIO()

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

        font_path = font_map.get(font_family, "C:/Windows/Fonts/DejaVuSans.ttf")

        pdfmetrics.registerFont(TTFont("CustomFont", font_path))

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
        for line in text.split("\n"):
            story.append(Paragraph(line, style))

        doc.build(story)
        buffer.seek(0)
        return buffer

    # EXPORT BUTTONS
  
    st.subheader("Export Edited Translation")

    st.download_button(
        "Download as TXT",
        new_text,
        file_name="edited_translation.txt",
        mime="text/plain"
    )

    st.download_button(
        "Download as PDF",
        make_pdf(new_text),
        file_name="edited_translation.pdf",
        mime="application/pdf"
    )
