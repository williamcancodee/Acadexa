from fpdf import FPDF

def generate_pdf(resources, grade, subjects, resource_types):
    """
    Generate a PDF with curated resources.

    Args:
        resources (dict): Dictionary of resources by type.
        grade (str): Grade level.
        subjects (list): List of subjects.
        resource_types (list): List of resource types.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Acadexa Curated Resources for Grade {grade}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Subjects: {', '.join(subjects)}", ln=True)
    pdf.cell(200, 10, txt=f"Resource Types: {', '.join(resource_types)}", ln=True)
    pdf.ln(10)
    for res_type, items in resources.items():
        if res_type == 'libraries':
            pdf.cell(200, 10, txt="Libraries / PDFs:", ln=True)
        else:
            pdf.cell(200, 10, txt=f"{res_type.capitalize()}:", ln=True)
        for item in items:
            pdf.cell(200, 10, txt=f"Title: {item['title']}", ln=True)
            if 'author' in item:
                pdf.cell(200, 10, txt=f"Author: {item['author']}", ln=True)
            if 'description' in item:
                pdf.multi_cell(200, 10, txt=f"Description: {item['description']}")
            if 'summary' in item:
                pdf.multi_cell(200, 10, txt=f"Summary: {item['summary']}")
            pdf.cell(200, 10, txt=f"Link: {item['link']}", link=item['link'], ln=True)
            pdf.ln(5)
    pdf.output("resources.pdf")
