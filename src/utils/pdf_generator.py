import os
import tempfile
from fpdf import FPDF
from io import BytesIO
import pandas as pd

def generate_pdf_report(stats_df: pd.DataFrame, ai_text: str = None, chart_image: BytesIO = None) -> BytesIO:
    """
    Generate a PDF report with statistics, AI analysis, and charts.
    
    Args:
        stats_df (pd.DataFrame): Statistics DataFrame
        ai_text (str, optional): AI analysis text
        chart_image (BytesIO, optional): Chart image buffer
        
    Returns:
        BytesIO: Buffer containing the PDF
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.cell(200, 10, txt="BuySideAI Financial Report", ln=True, align='C')
    pdf.ln(10)
    
    # Add statistics table
    pdf.set_fill_color(230, 230, 250)
    
    # Add table header
    for col in stats_df.columns:
        pdf.cell(40, 10, col, border=1, fill=True)
    pdf.ln()
    
    # Add table rows
    for idx, row in stats_df.iterrows():
        for val in row:
            text = str(val) if val is not None else "-"
            pdf.cell(40, 10, text[:15], border=1)
        pdf.ln()
    
    # Add AI analysis if provided
    if ai_text:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="AI Analysis:", ln=True)
        pdf.set_font("Arial", size=11)
        for line in ai_text.split('\n'):
            pdf.multi_cell(0, 10, line)
    
    # Add chart if provided
    if chart_image:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_file.write(chart_image.getvalue())
            tmp_file.flush()
            tmp_path = tmp_file.name
            
        pdf.add_page()
        pdf.image(tmp_path, x=10, y=30, w=180)
        os.remove(tmp_path)
    
    # Return PDF as BytesIO
    pdf_output = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_output) 