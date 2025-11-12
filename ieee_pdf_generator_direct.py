#!/usr/bin/env python3
"""
IEEE Direct PDF Generator - 100% Identical to Word Document
Uses EXACT same specifications as ieee_generator_fixed.py
"""

import sys
import os
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Frame, PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table as RLTable, TableStyle
from reportlab.platypus import Image as RLImage

# IEEE EXACT SPECIFICATIONS (from ieee_generator_fixed.py)
IEEE_SPECS = {
    # Page margins (exact IEEE LaTeX: 0.75" all sides)
    "margin": 0.75 * inch,
    
    # Two-column layout (exact IEEE LaTeX specifications)
    "column_count": 2,
    "column_width": 3.3125 * inch,  # 4770 twips = 3.3125"
    "column_gap": 0.25 * inch,      # 360 twips = 0.25"
    
    # Typography (exact IEEE LaTeX)
    "font_family": "Times-Roman",
    "font_size_body": 10,
    "font_size_title": 14,
    "font_size_author": 11,
    "font_size_affiliation": 10,
    "font_size_section": 10,
    "font_size_caption": 9,
    
    # Spacing (exact IEEE LaTeX)
    "line_spacing": 12,  # 12pt line spacing
    "paragraph_spacing": 0,  # No extra paragraph spacing
    "section_spacing_before": 12,  # 12pt before sections
    "section_spacing_after": 6,   # 6pt after sections
}

class IEEETwoColumnDocTemplate(BaseDocTemplate):
    """Custom document template for IEEE two-column layout"""
    
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        
        # Page dimensions
        page_width, page_height = letter
        margin = IEEE_SPECS["margin"]
        
        # Calculate frame dimensions
        frame_width = IEEE_SPECS["column_width"]
        frame_height = page_height - 2 * margin
        
        # Title page frame (full width)
        title_frame = Frame(
            margin, margin, 
            page_width - 2 * margin, frame_height,
            id='title', leftPadding=0, rightPadding=0, 
            topPadding=0, bottomPadding=0
        )
        
        # Two-column frames
        left_frame = Frame(
            margin, margin,
            frame_width, frame_height,
            id='left', leftPadding=0, rightPadding=0,
            topPadding=0, bottomPadding=0
        )
        
        right_frame = Frame(
            margin + frame_width + IEEE_SPECS["column_gap"], margin,
            frame_width, frame_height, 
            id='right', leftPadding=0, rightPadding=0,
            topPadding=0, bottomPadding=0
        )
        
        # Page templates
        title_template = PageTemplate(id='title', frames=[title_frame])
        two_col_template = PageTemplate(id='twocol', frames=[left_frame, right_frame])
        
        self.addPageTemplates([title_template, two_col_template])

def create_ieee_styles():
    """Create IEEE paragraph styles matching Word document exactly"""
    styles = getSampleStyleSheet()
    
    # IEEE Title Style (14pt Times Bold, centered)
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
    
    # IEEE Author Style (11pt Times Roman, centered)
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
    
    # IEEE Affiliation Style (10pt Times Italic, centered)
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
    
    # IEEE Body Text (10pt Times Roman, justified)
    styles.add(ParagraphStyle(
        name='IEEEBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=IEEE_SPECS["font_size_body"],
        leading=IEEE_SPECS["line_spacing"],
        alignment=TA_JUSTIFY,
        spaceAfter=0,
        spaceBefore=0,
        firstLineIndent=0.125 * inch  # IEEE paragraph indent
    ))
    
    # IEEE Section Heading (10pt Times Bold, left aligned)
    styles.add(ParagraphStyle(
        name='IEEESection',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=IEEE_SPECS["font_size_section"],
        leading=IEEE_SPECS["font_size_section"] + 2,
        alignment=TA_LEFT,
        spaceAfter=IEEE_SPECS["section_spacing_after"],
        spaceBefore=IEEE_SPECS["section_spacing_before"],
        keepWithNext=True
    ))
    
    # IEEE Abstract Style (10pt Times Roman, justified, with "Abstract—" prefix)
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
    
    # IEEE Keywords Style (10pt Times Roman, justified, with "Index Terms—" prefix)
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

def generate_ieee_pdf_direct(document_data):
    """Generate IEEE PDF directly using exact Word document specifications with proper two-column layout"""
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Use SimpleDocTemplate with custom page layout
    from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame, NextPageTemplate, PageBreak
    
    # Page dimensions
    page_width, page_height = letter
    margin = IEEE_SPECS["margin"]
    
    # Create document
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          leftMargin=margin, rightMargin=margin,
                          topMargin=margin, bottomMargin=margin)
    
    # Calculate frame dimensions for two-column layout
    frame_width = IEEE_SPECS["column_width"]
    frame_height = page_height - 2 * margin
    
    # Create frames for two-column layout
    left_frame = Frame(
        margin, margin, frame_width, frame_height,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='left'
    )
    
    right_frame = Frame(
        margin + frame_width + IEEE_SPECS["column_gap"], margin,
        frame_width, frame_height,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='right'
    )
    
    # Create page templates
    title_template = PageTemplate(id='title', frames=[Frame(margin, margin, 
                                                           page_width - 2*margin, frame_height,
                                                           leftPadding=0, rightPadding=0, 
                                                           topPadding=0, bottomPadding=0)])
    
    two_col_template = PageTemplate(id='twocol', frames=[left_frame, right_frame])
    
    # Add templates to document
    doc.addPageTemplates([title_template, two_col_template])
    
    # Get IEEE styles
    styles = create_ieee_styles()
    
    # Story (content) list
    story = []
    
    # TITLE SECTION (Single column, centered) - Use title template
    if document_data.get('title'):
        title_text = document_data['title'].strip()
        story.append(Paragraph(title_text, styles['IEEETitle']))
    
    # AUTHORS SECTION (Single column, centered)
    authors = document_data.get('authors', [])
    if authors:
        # Group authors by affiliation for proper IEEE formatting
        author_groups = {}
        for author in authors:
            affiliation = author.get('affiliation', '').strip()
            if affiliation not in author_groups:
                author_groups[affiliation] = []
            author_groups[affiliation].append(author.get('name', '').strip())
        
        # Add authors with affiliations
        for affiliation, author_names in author_groups.items():
            # Author names
            authors_text = ', '.join(author_names)
            story.append(Paragraph(authors_text, styles['IEEEAuthor']))
            
            # Affiliation
            if affiliation:
                story.append(Paragraph(affiliation, styles['IEEEAffiliation']))
    
    # Add space before switching to two-column
    story.append(Spacer(1, 24))
    
    # SWITCH TO TWO-COLUMN LAYOUT - Force new page with two-column template
    story.append(NextPageTemplate('twocol'))
    story.append(PageBreak())
    
    # ABSTRACT (Two-column layout) - Add immediately after template switch
    abstract = document_data.get('abstract', '').strip()
    if abstract:
        abstract_text = f"<b>Abstract—</b>{abstract}"
        story.append(Paragraph(abstract_text, styles['IEEEAbstract']))
    
    # KEYWORDS (Two-column layout)
    keywords = document_data.get('keywords', '').strip()
    if keywords:
        keywords_text = f"<b>Index Terms—</b>{keywords}"
        story.append(Paragraph(keywords_text, styles['IEEEKeywords']))
    
    # SECTIONS (Two-column layout)
    sections = document_data.get('sections', [])
    for i, section in enumerate(sections, 1):
        section_title = section.get('title', '').strip()
        if section_title:
            # Section heading with Roman numeral
            section_heading = f"{roman_numeral(i)}. {section_title.upper()}"
            story.append(Paragraph(section_heading, styles['IEEESection']))
        
        # Section content blocks
        content_blocks = section.get('content_blocks', [])
        for block in content_blocks:
            block_type = block.get('type', 'paragraph')
            
            if block_type == 'paragraph':
                text = block.get('text', '').strip()
                if text:
                    story.append(Paragraph(text, styles['IEEEBody']))
                    story.append(Spacer(1, 6))  # Small space between paragraphs
            
            elif block_type == 'subsection':
                subsection_title = block.get('title', '').strip()
                if subsection_title:
                    story.append(Paragraph(f"<b>{subsection_title}</b>", styles['IEEEBody']))
                
                subsection_text = block.get('text', '').strip()
                if subsection_text:
                    story.append(Paragraph(subsection_text, styles['IEEEBody']))
                    story.append(Spacer(1, 6))
            
            elif block_type == 'table':
                # Handle interactive tables from UI
                print(f"🔧 Processing inline table: {block.get('caption', 'No caption')}", file=sys.stderr)
                add_ieee_table_to_pdf(story, block, styles)
            
            elif block_type == 'image':
                # Handle images from UI
                print(f"🔧 Processing inline image: {block.get('caption', 'No caption')}", file=sys.stderr)
                add_ieee_image_to_pdf(story, block, styles)
    
    # TABLES (Two-column layout) - Handle tables at document level
    tables = document_data.get('tables', [])
    for table in tables:
        add_ieee_table_to_pdf(story, table, styles)
    
    # REFERENCES (Two-column layout)
    references = document_data.get('references', [])
    if references:
        story.append(Paragraph("REFERENCES", styles['IEEESection']))
        
        for i, ref in enumerate(references, 1):
            ref_text = f"[{i}] {ref.strip()}"
            story.append(Paragraph(ref_text, styles['IEEEBody']))
            story.append(Spacer(1, 3))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def add_ieee_table_to_pdf(story, table_data, styles):
    """Add interactive table to PDF with IEEE formatting"""
    try:
        # Get table type and data
        table_type = table_data.get('type', 'interactive')
        
        if table_type == 'interactive':
            # Get table data from UI
            headers = table_data.get('headers', [])
            rows_data = table_data.get('tableData', [])
            
            if not headers or not rows_data:
                return  # Skip empty tables
            
            # Prepare table data for ReportLab
            table_content = [headers]  # Header row
            table_content.extend(rows_data)  # Data rows
            
            # Create ReportLab table with IEEE column width
            max_col_width = IEEE_SPECS["column_width"] / len(headers)
            col_widths = [max_col_width] * len(headers)
            
            rl_table = RLTable(table_content, colWidths=col_widths)
            
            # Apply IEEE table styling
            rl_table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), IEEE_SPECS["font_size_body"]),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 1), (-1, -1), IEEE_SPECS["font_size_body"]),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                
                # Grid lines
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            ]))
            
            # Add table to story
            story.append(Spacer(1, 12))  # Space before table
            story.append(rl_table)
            story.append(Spacer(1, 12))  # Space after table
            
            # Add caption if provided
            caption = table_data.get('caption', '').strip()
            if caption:
                caption_style = ParagraphStyle(
                    'TableCaption',
                    fontName='Times-Roman',
                    fontSize=IEEE_SPECS["font_size_caption"],
                    alignment=TA_CENTER,
                    spaceAfter=6
                )
                story.append(Paragraph(f"TABLE I. {caption.upper()}", caption_style))
                story.append(Spacer(1, 6))
        
    except Exception as e:
        print(f"Error adding table to PDF: {e}", file=sys.stderr)

def add_ieee_image_to_pdf(story, image_data, styles):
    """Add image to PDF with IEEE formatting and proper sizing"""
    try:
        # Get image data
        img_data = image_data.get('data', '')
        if not img_data:
            return  # Skip if no image data
        
        # Decode base64 image
        if "," in img_data:
            img_data = img_data.split(",")[1]
        
        img_bytes = base64.b64decode(img_data)
        img_stream = BytesIO(img_bytes)
        
        # Get image size from UI
        size = image_data.get('size', 'medium')
        size_mapping = {
            'small': 2.0 * inch,
            'medium': 2.5 * inch,
            'large': IEEE_SPECS["column_width"]  # Full column width
        }
        max_width = size_mapping.get(size, 2.5 * inch)
        
        # Create ReportLab image with proper sizing constraints
        # Set maximum height to prevent overflow in two-column layout
        max_height = 4.0 * inch  # Maximum height for images
        
        rl_image = RLImage(img_stream, width=max_width)
        
        # Check if image height exceeds maximum and scale down if needed
        if hasattr(rl_image, 'drawHeight') and rl_image.drawHeight > max_height:
            # Calculate scale factor to fit within height constraint
            scale_factor = max_height / rl_image.drawHeight
            new_width = max_width * scale_factor
            rl_image = RLImage(img_stream, width=new_width, height=max_height)
        
        # Add image to story
        story.append(Spacer(1, 12))  # Space before image
        story.append(rl_image)
        story.append(Spacer(1, 6))   # Space after image
        
        # Add caption if provided
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
            story.append(Spacer(1, 6))
        
    except Exception as e:
        print(f"Error adding image to PDF: {e}", file=sys.stderr)

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
    """Test the direct PDF generator"""
    test_document = {
        "title": "Direct IEEE PDF Generation Test",
        "authors": [
            {
                "name": "Dr. Test Author",
                "affiliation": "Test University\nComputer Science Department",
                "email": "test@university.edu"
            }
        ],
        "abstract": "This paper demonstrates direct IEEE PDF generation using ReportLab with exact specifications from the Word document generator. The layout maintains perfect two-column formatting with proper typography and spacing.",
        "keywords": "IEEE format, PDF generation, two-column layout, direct conversion",
        "sections": [
            {
                "title": "Introduction",
                "content_blocks": [
                    {
                        "type": "paragraph",
                        "text": "This test demonstrates that we can generate IEEE-formatted PDFs directly using the same specifications as our Word document generator."
                    }
                ]
            }
        ],
        "references": [
            "IEEE Editorial Style Manual, IEEE, 2021.",
            "ReportLab User Guide, ReportLab Inc., 2023."
        ]
    }
    
    try:
        pdf_bytes = generate_ieee_pdf_direct(test_document)
        
        with open('test_direct_ieee_pdf.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ Direct IEEE PDF generated successfully!")
        print(f"📄 File size: {len(pdf_bytes)} bytes")
        print(f"💾 Saved as: test_direct_ieee_pdf.pdf")
        
    except Exception as e:
        print(f"❌ Direct PDF generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()