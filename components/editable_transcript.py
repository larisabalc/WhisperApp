import streamlit as st
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT


def render(transcript: dict, font_family="DejaVu", font_size=16, line_height=1.5):

    # Raw whisper segments
    segments = transcript["segments"]
    original_text = "\n".join(seg["text"].strip() for seg in segments)

    # Keep edited text persistent
    if "edited_text" not in st.session_state:
        st.session_state["edited_text"] = original_text

    edited_text = st.session_state["edited_text"]

    # SEARCH BAR 

    search_query = st.text_input(
        "Search in Editable Transcript:",
        key="edit_search"
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
   
    with st.expander("Editable Transcript", expanded=True):

        # --- Scrollable processed text ---
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

        # --- Editable text area ---
        new_text = st.text_area(
            "Edit transcript:",
            value=edited_text,
            height=250,
            key="editable_text_box"
        )

        st.session_state["edited_text"] = new_text

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
 
    st.subheader("Export Edited Transcript")

    st.download_button(
        "Download as TXT",
        new_text,
        file_name="edited_transcript.txt",
        mime="text/plain"
    )

    st.download_button(
        "Download as PDF",
        make_pdf(new_text),
        file_name="edited_transcript.pdf",
        mime="application/pdf"
    )
