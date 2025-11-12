#!/usr/bin/env python3
"""
IEEE PDF Generator - WORKING VERSION
Generates PDFs that definitely show all content including images and tables
"""

import sys
import os
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Frame, PageTemplate, BaseDocTemplate
from reportlab.platypus import Table as RLTable, TableStyle
from reportlab.platypus import Image as RLImage
from reportlab.lib import colors

# IEEE EXACT SPECIFICATIONS
IEEE_SPECS = {
    "margin": 0.75 * inch,
    "column_width": 3.3125 * inch,
    "column_gap": 0.25 * inch,
    "font_family": "Times-Roman",
    "font_size_body": 10,
    "font_size_title": 14,
    "font_size_author": 11,
    "font_size_affiliation": 10,
    "font_size_section": 10,
    "font_size_caption": 9,
    "line_spacing": 12,
}

def create_ieee_styles():
    """Create IEEE paragraph styles"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='IEEETitle',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=IEEE_SPECS["font_size_title"],
        leading=IEEE_SPECS["font_size_title"] + 2,
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=0
    ))
    
    styles.add(ParagraphStyle(
        name='IEEEAuthor',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=IEEE_SPECS["font_size_author"],
        leading=IEEE_SPECS["font_size_author"] + 2,
        alignment=TA_CENTER,
        spaceAfter=6,
        spaceBefore=6
    ))
    
    styles.add(ParagraphStyle(
        name='IEEEAffiliation',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=IEEE_SPECS["font_size_affiliation"],
        leading=IEEE_SPECS["font_size_affiliation"] + 2,
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=0
    ))
    
    styles.add(ParagraphStyle(
        name='IEEEBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=IEEE_SPECS["font_size_body"],
        leading=IEEE_SPECS["line_spacing"],
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        spaceBefore=0,
        firstLineIndent=0.125 * inch
    ))
    
    styles.add(ParagraphStyle(
        name='IEEESection',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=IEEE_SPECS["font_size_section"],
        leading=IEEE_SPECS["font_size_section"] + 2,
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=12,
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name='IEEEAbstract',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=IEEE_SPECS["font_size_body"],
        leading=IEEE_SPECS["line_spacing"],
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        spaceBefore=12,
        firstLineIndent=0
    ))
    
    styles.add(ParagraphStyle(
        name='IEEEKeywords',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=IEEE_SPECS["font_size_body"],
        leading=IEEE_SPECS["line_spacing"],
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        spaceBefore=0,
        firstLineIndent=0
    ))
    
    return styles

def add_table_to_story(story, table_data, styles):
    """Add table to PDF story"""
    try:
        table_type = table_data.get('type', 'interactive')
        
        if table_type == 'interactive':
            headers = table_data.get('headers', [])
            rows_data = table_data.get('tableData', [])
            
            if not headers or not rows_data:
                return
            
            # Prepare table data
            table_content = [headers]
            table_content.extend(rows_data)
            
            # Create table with proper column widths
            col_width = 6.5 * inch / len(headers)  # Distribute width evenly
            col_widths = [col_width] * len(headers)
            
            rl_table = RLTable(table_content, colWidths=col_widths)
            
            # Apply IEEE table styling
            rl_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), IEEE_SPECS["font_size_body"]),
                ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 1), (-1, -1), IEEE_SPECS["font_size_body"]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(Spacer(1, 12))
            story.append(rl_table)
            
            # Add caption
            caption = table_data.get('caption', '').strip()
            if caption:
                caption_style = ParagraphStyle(
                    'TableCaption',
                    fontName='Times-Roman',
                    fontSize=IEEE_SPECS["font_size_caption"],
                    alignment=TA_CENTER,
                    spaceAfter=12
                )
                story.append(Paragraph(f"TABLE I. {caption.upper()}", caption_style))
            
            story.append(Spacer(1, 12))
            
    except Exception as e:
        print(f"Error adding table: {e}", file=sys.stderr)

def add_image_to_story(story, image_data, styles):
    """Add image to PDF story"""
    try:
        img_data = image_data.get('data', '')
        if not img_data:
            return
        
        # Decode base64 image
        if "," in img_data:
            img_data = img_data.split(",")[1]
        
        img_bytes = base64.b64decode(img_data)
        img_stream = BytesIO(img_bytes)
        
        # Get size
        size = image_data.get('size', 'medium')
        size_mapping = {
            'small': 2.0 * inch,
            'medium': 2.5 * inch,
            'large': 4.0 * inch
        }
        width = size_mapping.get(size, 2.5 * inch)
        
        # Create image with size constraints and maximum height
        max_height = 3.0 * inch  # Maximum height to prevent overflow
        rl_image = RLImage(img_stream, width=width)
        
        # Check if we need to scale down the image
        if hasattr(rl_image, 'drawHeight') and rl_image.drawHeight > max_height:
            # Scale down to fit
            scale_factor = max_height / rl_image.drawHeight
            new_width = width * scale_factor
            rl_image = RLImage(img_stream, width=new_width, height=max_height)
        
        story.append(Spacer(1, 12))
        story.append(rl_image)
        
        # Add caption
        caption = image_data.get('caption', '').strip()
        if caption:
            caption_style = ParagraphStyle(
                'ImageCaption',
                fontName='Times-Roman',
                fontSize=IEEE_SPECS["font_size_caption"],
                alignment=TA_CENTER,
                spaceAfter=12
            )
            story.append(Paragraph(f"Fig. 1. {caption}", caption_style))
        
        story.append(Spacer(1, 12))
        
    except Exception as e:
        print(f"Error adding image: {e}", file=sys.stderr)

def generate_ieee_pdf_working(document_data):
    """Generate IEEE PDF that definitely shows all content"""
    
    buffer = BytesIO()
    
    # Use simple document template
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          leftMargin=IEEE_SPECS["margin"], 
                          rightMargin=IEEE_SPECS["margin"],
                          topMargin=IEEE_SPECS["margin"], 
                          bottomMargin=IEEE_SPECS["margin"])
    
    styles = create_ieee_styles()
    story = []
    
    # TITLE
    if document_data.get('title'):
        title_text = document_data['title'].strip()
        story.append(Paragraph(title_text, styles['IEEETitle']))
    
    # AUTHORS
    authors = document_data.get('authors', [])
    if authors:
        for author in authors:
            name = author.get('name', '').strip()
            if name:
                story.append(Paragraph(name, styles['IEEEAuthor']))
            
            affiliation = author.get('affiliation', '').strip()
            if affiliation:
                story.append(Paragraph(affiliation, styles['IEEEAffiliation']))
    
    story.append(Spacer(1, 24))
    
    # ABSTRACT
    abstract = document_data.get('abstract', '').strip()
    if abstract:
        abstract_text = f"<b>Abstract—</b>{abstract}"
        story.append(Paragraph(abstract_text, styles['IEEEAbstract']))
    
    # KEYWORDS
    keywords = document_data.get('keywords', '').strip()
    if keywords:
        keywords_text = f"<b>Index Terms—</b>{keywords}"
        story.append(Paragraph(keywords_text, styles['IEEEKeywords']))
    
    # DOCUMENT-LEVEL TABLES
    tables = document_data.get('tables', [])
    for table in tables:
        add_table_to_story(story, table, styles)
    
    # SECTIONS
    sections = document_data.get('sections', [])
    for i, section in enumerate(sections, 1):
        section_title = section.get('title', '').strip()
        if section_title:
            section_heading = f"{roman_numeral(i)}. {section_title.upper()}"
            story.append(Paragraph(section_heading, styles['IEEESection']))
        
        content_blocks = section.get('content_blocks', [])
        for block in content_blocks:
            block_type = block.get('type', 'paragraph')
            
            if block_type == 'paragraph':
                text = block.get('text', '').strip()
                if text:
                    story.append(Paragraph(text, styles['IEEEBody']))
                    story.append(Spacer(1, 6))
            
            elif block_type == 'table':
                add_table_to_story(story, block, styles)
            
            elif block_type == 'image':
                add_image_to_story(story, block, styles)
    
    # REFERENCES
    references = document_data.get('references', [])
    if references:
        story.append(Paragraph("REFERENCES", styles['IEEESection']))
        
        for i, ref in enumerate(references, 1):
            ref_text = f"[{i}] {ref.strip()}"
            story.append(Paragraph(ref_text, styles['IEEEBody']))
            story.append(Spacer(1, 3))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def roman_numeral(num):
    """Convert number to Roman numeral"""
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    numerals = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
    
    result = ''
    for i in range(len(values)):
        count = num // values[i]
        if count:
            result += numerals[i] * count
            num -= values[i] * count
    return result

def main():
    """Test the working PDF generator"""
    # Load TCS image
    def load_tcs_image():
        try:
            image_path = r"C:\Users\shyam\Downloads\tcs.png"
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/png;base64,{image_b64}"
        except:
            return None
    
    tcs_image = load_tcs_image()
    
    test_document = {
        "title": "Working PDF Generator Test: TCS Image and Tables",
        "authors": [
            {
                "name": "Dr. Working Generator",
                "affiliation": "TCS Research Lab\nSoftware Engineering Division\nMumbai, India"
            }
        ],
        "abstract": "This document tests the working PDF generator that ensures all content appears correctly including images and tables.",
        "keywords": "working PDF, TCS image, tables, content verification",
        "tables": [
            {
                "type": "interactive",
                "caption": "Performance metrics table",
                "headers": ["Method", "Speed", "Quality"],
                "tableData": [
                    ["Direct PDF", "Fast", "High"],
                    ["Word→PDF", "Medium", "Perfect"]
                ]
            }
        ],
        "sections": [
            {
                "title": "Introduction",
                "content_blocks": [
                    {
                        "type": "paragraph",
                        "text": "This section tests that paragraphs appear correctly in the PDF."
                    },
                    {
                        "type": "image",
                        "data": tcs_image,
                        "size": "medium",
                        "caption": "TCS Logo - Testing image integration"
                    } if tcs_image else {
                        "type": "paragraph",
                        "text": "[TCS image not found]"
                    }
                ]
            }
        ],
        "references": [
            "Working PDF Generator Documentation, 2023."
        ]
    }
    
    try:
        pdf_bytes = generate_ieee_pdf_working(test_document)
        
        with open('test_working_pdf.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ Working PDF generated successfully!")
        print(f"📄 File size: {len(pdf_bytes):,} bytes")
        print(f"💾 Saved as: test_working_pdf.pdf")
        
    except Exception as e:
        print(f"❌ Working PDF generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()