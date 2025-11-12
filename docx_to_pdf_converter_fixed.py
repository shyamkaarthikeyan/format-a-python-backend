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
    Convert DOCX to PDF using ONLY docx2pdf - preserves exact Word formatting including 2-column layout
    No fallback to ensure PDF matches Word document exactly
    """
    try:
        logger.info("Starting Word→PDF conversion using docx2pdf only")
        
        # Use ONLY docx2pdf - no fallback to preserve exact formatting
        return _convert_with_docx2pdf(docx_data)
            
    except Exception as e:
        logger.error(f"docx2pdf conversion failed: {e}")
        raise Exception(f"Word→PDF conversion failed: {str(e)}. Please ensure docx2pdf and MS Word/LibreOffice are available.")

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

# ReportLab fallback removed - using ONLY docx2pdf to preserve exact Word formatting

# Error PDF creation removed - if conversion fails, throw exception instead of creating fallback PDF

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