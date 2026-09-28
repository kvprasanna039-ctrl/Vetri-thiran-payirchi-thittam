from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import get_settings


def save_pdf(layout: list[dict], filename_prefix: str = "comiccraft") -> str:
    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = settings.exports_dir / f"{filename_prefix}_{timestamp}.pdf"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, f"Panel {panel['panel_number']}: {panel['title']}")
        pdf.ln(3)

        image_path = Path(panel["image_path"])
        if image_path.exists():
            pdf.image(str(image_path), x=17, y=35, w=175, h=105)

        pdf.set_y(148)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, panel["scene_description"])
        pdf.ln(2)

        if panel.get("caption"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, f"Caption: {panel['caption']}")
            pdf.ln(1)

        if panel.get("narration"):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, f"Narration: {panel['narration']}")
            pdf.ln(1)

        if panel.get("dialogue"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, f"Dialogue: {panel['dialogue']}")

    pdf.output(str(output))
    return str(output)
