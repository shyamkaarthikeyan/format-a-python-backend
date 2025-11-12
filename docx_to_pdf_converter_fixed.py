#!/usr/bin/env python3
"""
Serverless-Compatible DOCX to PDF Converter
Uses ReportLab as fallback when docx2pdf is not available (which is the case in Vercel)
"""

import sys
import os
import tempfile
import logging
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_docx_to_pdf_direct(docx_data):
    """
    Convert DOCX to PDF with serverless compatibility
    Uses ReportLab-based conversion since docx2pdf requires MS Word/LibreOffice
    """
    try:
        logger.info("Starting serverless-compatible DOCX to PDF conversion")
        
        # Try docx2pdf first (will fail in serverless but worth trying)
        try:
            return _convert_with_docx2pdf(docx_data)
        except Exception as e:
            logger.warning(f"docx2pdf failed (expected in serverless): {e}")
            logger.info("Using ReportLab fallback for serverless compatibility...")
            return _convert_with_reportlab_fallback(docx_data)
            
    except Exception as e:
        logger.error(f"All PDF conversion methods failed: {e}")
        raise Exception(f"PDF conversion failed: {str(e)}")

def _convert_with_docx2pdf(docx_data):
    """Try conversion with docx2pdf (will fail in serverless)"""
    import docx2pdf
    
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
        temp_docx.write(docx_data)
        temp_docx_path = temp_docx.name
    
    temp_pdf_path = temp_docx_path.replace('.docx', '.pdf')
    
    try:
        docx2pdf.convert(temp_docx_path, temp_pdf_path)
        
        if os.path.exists(temp_pdf_path):
            with open(temp_pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                logger.info(f"docx2pdf conversion successful, size: {len(pdf_data)} bytes")
                return pdf_data
        else:
            raise Exception("PDF file was not created by docx2pdf")
            
    finally:
        # Clean up
        try:
            if os.path.exists(temp_docx_path):
                os.unlink(temp_docx_path)
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
        except:
            pass

def _convert_with_reportlab_fallback(docx_data):
    """Fallback conversion using ReportLab - extracts content from DOCX and recreates as PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from docx import Document
        import tempfile
        
        logger.info("Using ReportLab fallback for serverless PDF conversion...")
        
        # Parse DOCX content
        with tempfile.NamedTemporaryFile(suffix='.docx') as temp_docx:
            temp_docx.write(docx_data)
            temp_docx.flush()
            
            try:
                doc = Document(temp_docx.name)
            except Exception as e:
                logger.error(f"Failed to parse DOCX: {e}")
                # Create a simple error PDF
                return _create_error_pdf("Failed to parse DOCX document")
        
        # Create PDF with ReportLab
        buffer = BytesIO()
        
        # Use A4 page size for IEEE format
        pdf_doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles for IEEE format
        title_style = ParagraphStyle(
            'IEEETitle',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'IEEEHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'IEEEBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=4,  # Justify
            fontName='Helvetica'
        )
        
        # Process document content
        first_para = True
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            # First paragraph is likely the title
            if first_para and len(text) < 100:
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 12))
                first_para = False
            # Check if it's a heading (simple heuristic)
            elif (text.isupper() or 
                  text.startswith(('I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'VII.', 'VIII.', 'IX.', 'X.')) or
                  text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
                  text.endswith(':')) and len(text) < 80:
                story.append(Paragraph(text, heading_style))
            else:
                # Regular body text
                story.append(Paragraph(text, body_style))
                story.append(Spacer(1, 6))
        
        # If no content was found, add a placeholder
        if len(story) == 0:
            story.append(Paragraph("Document Content", title_style))
            story.append(Spacer(1, 12))
            story.append(Paragraph("The document content could not be extracted properly. Please check the original DOCX file.", body_style))
        
        # Build PDF
        try:
            pdf_doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            if len(pdf_data) > 0:
                logger.info(f"ReportLab fallback conversion successful, size: {len(pdf_data)} bytes")
                return pdf_data
            else:
                raise Exception("ReportLab produced empty PDF")
                
        except Exception as e:
            logger.error(f"ReportLab PDF building failed: {e}")
            buffer.close()
            return _create_error_pdf(f"PDF generation error: {str(e)}")
            
    except ImportError as e:
        logger.error(f"Required libraries not available: {e}")
        return _create_error_pdf("PDF conversion libraries not available")
    except Exception as e:
        logger.error(f"ReportLab fallback failed: {e}")
        return _create_error_pdf(f"PDF conversion failed: {str(e)}")

def _create_error_pdf(error_message):
    """Create a simple error PDF when conversion fails"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Add error message
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "PDF Conversion Error")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, "The document could not be converted to PDF.")
        p.drawString(100, 700, f"Error: {error_message}")
        p.drawString(100, 680, "Please try downloading as Word document instead.")
        
        p.save()
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception:
        # If even error PDF creation fails, return minimal PDF
        return b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n174\n%%EOF'

# Backward compatibility functions
def convert_docx_to_pdf(docx_data):
    """Main conversion function"""
    return convert_docx_to_pdf_direct(docx_data)

def convert_docx_file_to_pdf(input_docx_path, output_pdf_path):
    """Convert DOCX file to PDF file"""
    try:
        with open(input_docx_path, 'rb') as f:
            docx_data = f.read()
        
        pdf_data = convert_docx_to_pdf_direct(docx_data)
        
        with open(output_pdf_path, 'wb') as f:
            f.write(pdf_data)
        
        logger.info(f"File conversion successful: {input_docx_path} -> {output_pdf_path}")
        
    except Exception as e:
        logger.error(f"File conversion failed: {e}")
        raise

def main():
    """Main function for command line usage"""
    try:
        if len(sys.argv) == 3:
            # File path mode
            input_docx_path = sys.argv[1]
            output_pdf_path = sys.argv[2]
            convert_docx_file_to_pdf(input_docx_path, output_pdf_path)
            print("Conversion completed successfully")
            
        elif len(sys.argv) == 1:
            # Stdin mode
            docx_data = sys.stdin.buffer.read()
            if len(docx_data) == 0:
                sys.stderr.write("Error: No DOCX data received\n")
                sys.exit(1)
            
            pdf_data = convert_docx_to_pdf(docx_data)
            sys.stdout.buffer.write(pdf_data)
            sys.stdout.buffer.flush()
            
        else:
            sys.stderr.write("Usage: python converter.py [input.docx output.pdf] or pipe DOCX data to stdin\n")
            sys.exit(1)
        
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()