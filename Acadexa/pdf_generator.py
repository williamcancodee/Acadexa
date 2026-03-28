from datetime import datetime

from fpdf import FPDF


SECTION_NAMES = {
    "books": "Books",
    "videos": "Videos",
    "articles": "Articles",
    "libraries": "Open Source Libraries / PDFs",
}


def _safe_text(value):
    text = str(value or "")
    return text.encode("latin-1", "replace").decode("latin-1")


def _truncate_text(value, max_chars=420):
    text = _safe_text(value).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _ensure_space(pdf, needed_height):
    if pdf.get_y() + needed_height > (pdf.h - pdf.b_margin):
        pdf.add_page()


def _draw_logo_badge(pdf, x, y, size=14):
    pdf.set_fill_color(30, 53, 80)
    pdf.set_draw_color(195, 138, 46)
    pdf.rect(x, y, size, size, "FD")
    pdf.set_xy(x, y + (size * 0.17))
    pdf.set_text_color(245, 233, 207)
    pdf.set_font("Arial", "B", int(size * 0.8))
    pdf.cell(size, size, _safe_text("A"), align="C")


def _draw_cover_page(pdf, grade, subjects, resource_types):
    pdf.add_page()
    pdf.set_fill_color(246, 242, 233)
    pdf.set_draw_color(216, 205, 184)
    pdf.rect(8, 8, pdf.w - 16, pdf.h - 16, "D")

    _draw_logo_badge(pdf, x=(pdf.w / 2) - 7, y=24, size=14)

    pdf.set_y(44)
    pdf.set_font("Arial", "B", 28)
    pdf.set_text_color(20, 38, 59)
    pdf.cell(0, 14, _safe_text("Acadexa"), ln=True, align="C")

    pdf.set_font("Arial", "", 14)
    pdf.set_text_color(86, 96, 108)
    pdf.cell(0, 9, _safe_text("Curated Academic Resource Pack"), ln=True, align="C")
    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(130, 93, 42)
    pdf.cell(0, 8, _safe_text("Learn deeply. Curate wisely."), ln=True, align="C")

    pdf.set_y(92)
    left = pdf.l_margin + 10
    width = pdf.w - (pdf.l_margin + pdf.r_margin) - 20
    pdf.set_fill_color(252, 248, 239)
    pdf.set_draw_color(214, 200, 173)
    pdf.rect(left, pdf.get_y(), width, 55, "DF")

    pdf.set_xy(left + 5, pdf.get_y() + 4)
    pdf.set_text_color(40, 54, 70)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, _safe_text("Grade / Level: " + str(grade)), ln=True)
    pdf.set_x(left + 5)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(width - 10, 5, _safe_text("Subjects: " + ", ".join(subjects)))
    pdf.set_x(left + 5)
    pdf.multi_cell(width - 10, 5, _safe_text("Resource Types: " + ", ".join(resource_types)))

    pdf.set_y(171)
    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(106, 106, 106)
    pdf.multi_cell(
        0,
        7,
        _safe_text(
            '"Organized discovery beats random searching. Keep this pack, annotate it, and build mastery one source at a time."'
        ),
        align="C",
    )

    pdf.set_y(pdf.h - 24)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(90, 102, 119)
    stamp = datetime.now().strftime("Generated on %b %d, %Y")
    pdf.cell(0, 8, _safe_text(stamp), ln=True, align="C")


def _draw_toc_page(pdf, section_data):
    pdf.add_page()
    _draw_logo_badge(pdf, x=pdf.w - pdf.r_margin - 12, y=pdf.t_margin - 1, size=11)
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(30, 46, 62)
    pdf.cell(0, 12, _safe_text("Table of Contents"), ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(95, 107, 122)
    pdf.multi_cell(0, 6, _safe_text("A compact summary of what is included in this curated pack."))
    pdf.ln(3)

    for idx, section in enumerate(section_data, start=1):
        _ensure_space(pdf, 12)
        fill = (248, 245, 237) if idx % 2 else (242, 236, 224)
        pdf.set_fill_color(*fill)
        pdf.set_draw_color(220, 208, 185)
        y = pdf.get_y()
        pdf.rect(pdf.l_margin, y, pdf.w - pdf.l_margin - pdf.r_margin, 9, "DF")

        pdf.set_xy(pdf.l_margin + 3, y + 1.5)
        pdf.set_text_color(39, 52, 66)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, _safe_text(f"{idx}. {section['title']}"), ln=False)

        pdf.set_font("Arial", "", 10)
        right_text = _safe_text(f"{section['count']} items")
        right_width = pdf.get_string_width(right_text)
        pdf.set_x(pdf.w - pdf.r_margin - right_width)
        pdf.cell(right_width, 5, right_text, ln=True)

        pdf.ln(2)


def _draw_section_title(pdf, title, count):
    _ensure_space(pdf, 16)
    _draw_logo_badge(pdf, x=pdf.w - pdf.r_margin - 11, y=pdf.get_y() - 1, size=10)
    pdf.set_fill_color(232, 223, 204)
    pdf.set_draw_color(204, 184, 150)
    pdf.rect(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin - pdf.r_margin, 8, "DF")

    pdf.set_text_color(53, 40, 21)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(pdf.l_margin + 3, pdf.get_y() + 1.5)
    pdf.cell(0, 5, _safe_text(f"{title} ({count})"), ln=True)
    pdf.ln(4)


def _draw_item(pdf, index, item):
    _ensure_space(pdf, 46)

    title = _truncate_text(item.get("title", "Untitled"), max_chars=140)
    author = _truncate_text(item.get("author", ""), max_chars=100)
    description = item.get("description") or item.get("summary") or ""
    description = _truncate_text(description, max_chars=350)
    link = _safe_text(item.get("link", "")).strip()

    block_top = pdf.get_y()
    block_fill = (249, 246, 240) if index % 2 else (242, 236, 225)

    # Draw alternating card-like blocks for easier visual scanning.
    pdf.set_fill_color(*block_fill)
    pdf.set_draw_color(224, 215, 197)
    pdf.rect(pdf.l_margin, block_top, pdf.w - pdf.l_margin - pdf.r_margin, 40, "FD")
    pdf.set_xy(pdf.l_margin + 3, block_top + 3)

    pdf.set_text_color(26, 43, 61)
    pdf.set_font("Arial", "B", 11)
    pdf.multi_cell(0, 6, _safe_text(f"{index}. {title}"))

    if author:
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(95, 95, 95)
        pdf.multi_cell(0, 5, _safe_text("Author: " + author))

    if description:
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(57, 66, 80)
        pdf.multi_cell(0, 5, _safe_text(description))

    if link:
        pdf.set_font("Arial", "U", 10)
        pdf.set_text_color(21, 87, 153)
        pdf.cell(0, 6, _safe_text("Open resource"), link=link, ln=True)

    end_y = pdf.get_y() + 1
    if end_y > block_top + 40:
        # Extend background block for longer wrapped descriptions.
        pdf.set_fill_color(*block_fill)
        pdf.set_draw_color(224, 215, 197)
        pdf.rect(pdf.l_margin, block_top, pdf.w - pdf.l_margin - pdf.r_margin, end_y - block_top + 1, "FD")
        pdf.set_xy(pdf.l_margin + 3, block_top + 3)
        pdf.set_text_color(26, 43, 61)
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(0, 6, _safe_text(f"{index}. {title}"))
        if author:
            pdf.set_font("Arial", "I", 9)
            pdf.set_text_color(95, 95, 95)
            pdf.multi_cell(0, 5, _safe_text("Author: " + author))
        if description:
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(57, 66, 80)
            pdf.multi_cell(0, 5, _safe_text(description))
        if link:
            pdf.set_font("Arial", "U", 10)
            pdf.set_text_color(21, 87, 153)
            pdf.cell(0, 6, _safe_text("Open resource"), link=link, ln=True)

    pdf.set_draw_color(218, 207, 184)
    pdf.line(pdf.l_margin, pdf.get_y() + 1, pdf.w - pdf.r_margin, pdf.get_y() + 1)
    pdf.ln(4)


def generate_pdf(resources, grade, subjects, resource_types, output_path="resources.pdf"):
    """Generate a clean PDF with cover page, compact TOC, and grouped resources."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(12, 12, 12)

    ordered_types = [kind for kind in resource_types if resources.get(kind)]
    section_data = [
        {
            "key": resource_type,
            "title": SECTION_NAMES.get(resource_type, resource_type.capitalize()),
            "count": len(resources.get(resource_type, [])),
        }
        for resource_type in ordered_types
    ]

    _draw_cover_page(pdf, grade, subjects, resource_types)
    _draw_toc_page(pdf, section_data)

    for section in section_data:
        pdf.add_page()
        _draw_section_title(pdf, section["title"], section["count"])

        for idx, item in enumerate(resources.get(section["key"], []), start=1):
            _draw_item(pdf, idx, item)

    if not section_data:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(45, 58, 74)
        pdf.cell(0, 10, _safe_text("No resources available for this selection."), ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(98, 108, 118)
        pdf.multi_cell(0, 7, _safe_text("Try a different combination of subjects or resource types and generate a new pack."))

    pdf.output(output_path)
