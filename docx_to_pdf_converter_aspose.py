#!/usr/bin/env python3
"""
Aspose.Words-based DOCX to PDF Converter
Reliable serverless-compatible conversion that preserves formatting
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
    Convert DOCX to PDF using Aspose.Words - preserves exact Word formatting
    Serverless-compatible and reliable
    """
    try:
        logger.info("Starting Word→PDF conversion using Aspose.Words")
        
        # Import Aspose.Words
        import aspose.words as aw
        
        # Create temporary file for DOCX input
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            temp_docx.write(docx_data)
            temp_docx_path = temp_docx.name
        
        try:
            # Load the document
            logger.info(f"Loading DOCX document from {temp_docx_path}")
            doc = aw.Document(temp_docx_path)
            
            # Create temporary file for PDF output
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
            
            try:
                # Save as PDF
                logger.info(f"Converting to PDF: {temp_pdf_path}")
                doc.save(temp_pdf_path, aw.SaveFormat.PDF)
                
                # Read the PDF data
                if os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                        logger.info(f"Aspose.Words conversion successful, size: {len(pdf_data)} bytes")
                        return pdf_data
                else:
                    raise Exception("PDF file was not created by Aspose.Words")
                    
            finally:
                # Clean up PDF temp file
                try:
                    if os.path.exists(temp_pdf_path):
                        os.unlink(temp_pdf_path)
                except:
                    pass
                    
        finally:
            # Clean up DOCX temp file
            try:
                if os.path.exists(temp_docx_path):
                    os.unlink(temp_docx_path)
            except:
                pass
            
    except ImportError as e:
        logger.error(f"Aspose.Words not available: {e}")
        raise Exception(f"Aspose.Words library not available: {str(e)}")
    except Exception as e:
        logger.error(f"Aspose.Words conversion failed: {e}")
        raise Exception(f"Word→PDF conversion failed: {str(e)}")

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