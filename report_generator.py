import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document

def generate_pdf(summary, stats, insights, model_result):
    os.makedirs("outputs/reports", exist_ok=True)
    
    pdf_path = "outputs/reports/report.pdf"
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    elements = []

    #Title
    elements.append(Paragraph("NestInsight Report", styles['Title']))
    elements.append(Spacer(1, 20))
    #Summary
    elements.append(Paragraph("Dataset Summary:", styles['Heading2']))
    for key, value in summary.items():
        elements.append(Paragraph(f"{key}: {value}", styles['BodyText']))
    elements.append(Spacer(1, 20))

    #Statistics
    elements.append(Paragraph("Statistical Analysis:", styles['Heading2']))
    for column, value in stats.items():
        elements.append(Paragraph(f"<b>{column}</b>", styles['BodyText']))
        elements.append(Paragraph(str(value), styles['BodyText'])) 
    elements.append(Spacer(1, 10))

    #Insights
    elements.append(Paragraph("Business Insights:", styles['Heading2']))
    for insight in insights:
        elements.append(Paragraph(insight, styles['BodyText']))
    elements.append(Spacer(1, 20))

    #Model Results
    elements.append(Paragraph("Model Results:", styles['Heading2']))
    
    if model_result["status"] == "success":
        elements.append(Paragraph(f"Accuracy: {model_result['accuracy']}%", styles['BodyText']))
        elements.append(Paragraph(f"Model Path: {model_result['model_path']}", styles['BodyText']))
    else:
        elements.append(Paragraph(f"Training Failed: {model_result['message']}", styles['BodyText']))

    doc.build(elements)

    return pdf_path

# Generate DOCX report
def generate_docx(summary, stats, insights, model_result):
    os.makedirs("outputs/reports", exist_ok=True)
    
    docx_path = "outputs/reports/report.docx"
    doc = Document()
    #Title
    doc.add_heading("NestInsight Report", 0)

    #Summary
    doc.add_heading("Dataset Summary:", level=1)
    for key, value in summary.items():
        doc.add_paragraph(f"{key}: {value}")

    #Statistics
    doc.add_heading("Statistical Analysis:", level=1)
    for column, values in stats.items():
        doc.add_paragraph(f"{column}: {values}")
        
    #Insights
    doc.add_heading("Business Insights:", level=1)
    for insight in insights:
        doc.add_paragraph(insight)

    #Model Results
    doc.add_heading("Model Results:", level=1)

    if model_result["status"] == "success":
        doc.add_paragraph(f"Accuracy: {model_result['accuracy']}%")
        doc.add_paragraph(f"Model Path: {model_result['model_path']}")
    else:
        doc.add_paragraph(f"Training Failed: {model_result['message']}")

    doc.save(docx_path)
    return docx_path