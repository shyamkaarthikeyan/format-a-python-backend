"""
IEEE Document Generator - EXACT copy from test.py 
"""

import json
import sys
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
import re
from html.parser import HTMLParser
import unicodedata

def sanitize_text(text):
    """Sanitize text to remove invalid Unicode characters and surrogates."""
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove surrogate characters and other problematic Unicode
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove any remaining control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    return text

# IEEE EXACT LATEX PDF FORMATTING - LOW-LEVEL OPENXML SPECIFICATIONS
IEEE_CONFIG = {
    'font_name': 'Times New Roman',
    # Font sizes (exact IEEE LaTeX specifications)
    'font_size_title': Pt(24),        # Title: 24pt bold centered
    'font_size_author_name': Pt(10),  # Author names: 10pt bold
    'font_size_author_affil': Pt(10), # Author affiliations: 10pt italic
    'font_size_author_email': Pt(9),  # Author emails: 9pt
    'font_size_body': Pt(10),         # Body text: 10pt
    'font_size_abstract': Pt(9),      # Abstract/Keywords: 9pt bold
    'font_size_caption': Pt(9),       # Captions: 9pt italic
    'font_size_reference': Pt(9),     # References: 9pt
    
    # Page margins (exact IEEE LaTeX: 0.75" all sides = 1080 twips)
    'margin_twips': 1080,
    
    # Two-column layout (exact IEEE LaTeX specifications)
    'column_count': 2,
    'column_width_twips': 4770,       # 3.3125" per column
    'column_gap_twips': 360,          # 0.25" gap between columns
    'column_indent': Pt(0),           # No indent for column text
    
    # Line spacing (exact IEEE LaTeX: 12pt = 240 twips)
    'line_spacing_twips': 240,
    'line_spacing': Pt(12),  # For backward compatibility
    
    # Paragraph spacing (exact IEEE LaTeX specifications)
    'spacing_title_after': 240,       # 12pt after title
    'spacing_abstract_after': 120,    # 6pt after abstract
    'spacing_keywords_after': 240,    # 12pt after keywords
    'spacing_section_before': 240,    # 12pt before section headings
    'spacing_section_after': 0,       # 0pt after section headings
    
    # Figure specifications
    'figure_max_width_twips': 4770,   # Max 3.3125" width (column width)
    'figure_spacing': 120,             # 6pt before/after figures
    'figure_sizes': {
        'Very Small': Inches(1.5),     # 1.5" width
        'Small': Inches(2.0),          # 2.0" width  
        'Medium': Inches(2.5),         # 2.5" width
        'Large': Inches(3.3125)        # Full column width
    },
    'max_figure_height': Inches(4.0),  # Max figure height
    
    # Reference specifications
    'reference_hanging_indent': 360,  # 0.25" hanging indent
}

def set_document_defaults(doc):
    """Set document-wide defaults using EXACT IEEE LaTeX PDF specifications via OpenXML."""
    
    # 1. SET PAGE MARGINS - EXACT IEEE LaTeX: 0.75" all sides (1080 twips)
    for section in doc.sections:
        sectPr = section._sectPr
        pgMar = sectPr.xpath('./w:pgMar')[0] if sectPr.xpath('./w:pgMar') else OxmlElement('w:pgMar')
        pgMar.set(qn('w:left'), '1080')
        pgMar.set(qn('w:right'), '1080')
        pgMar.set(qn('w:top'), '1080')
        pgMar.set(qn('w:bottom'), '1080')
        if not sectPr.xpath('./w:pgMar'):
            sectPr.append(pgMar)
    
    # 2. SET HYPHENATION & COMPATIBILITY - EXACT IEEE LaTeX specifications
    settings = doc.settings
    settings_element = settings.element
    
    # Clear existing settings first
    for elem in settings_element.xpath('./w:autoHyphenation | ./w:hyphenationZone | ./w:consecutiveHyphenLimit | ./w:doNotHyphenateCaps | ./w:compat'):
        settings_element.remove(elem)
    
    # Add hyphenation settings
    autoHyphenation = OxmlElement('w:autoHyphenation')
    autoHyphenation.set(qn('w:val'), '1')
    settings_element.append(autoHyphenation)
    
    hyphenationZone = OxmlElement('w:hyphenationZone')
    hyphenationZone.set(qn('w:val'), '360')  # 0.25"
    settings_element.append(hyphenationZone)
    
    consecutiveHyphenLimit = OxmlElement('w:consecutiveHyphenLimit')
    consecutiveHyphenLimit.set(qn('w:val'), '2')
    settings_element.append(consecutiveHyphenLimit)
    
    doNotHyphenateCaps = OxmlElement('w:doNotHyphenateCaps')
    doNotHyphenateCaps.set(qn('w:val'), '1')
    settings_element.append(doNotHyphenateCaps)
    
    # Add compatibility settings
    compat = OxmlElement('w:compat')
    
    usePrinterMetrics = OxmlElement('w:usePrinterMetrics')
    usePrinterMetrics.set(qn('w:val'), '1')
    compat.append(usePrinterMetrics)
    
    doNotExpandShiftReturn = OxmlElement('w:doNotExpandShiftReturn')
    doNotExpandShiftReturn.set(qn('w:val'), '1')
    compat.append(doNotExpandShiftReturn)
    
    settings_element.append(compat)
    
    # 3. MODIFY NORMAL STYLE - EXACT IEEE LaTeX specifications via OpenXML
    styles = doc.styles
    if 'Normal' in styles:
        normal = styles['Normal']
        # Apply via OpenXML for exact control
        style_element = normal.element
        pPr = style_element.xpath('./w:pPr')[0] if style_element.xpath('./w:pPr') else OxmlElement('w:pPr')
        
        # Clear existing spacing/alignment
        for elem in pPr.xpath('./w:spacing | ./w:jc | ./w:ind'):
            pPr.remove(elem)
        
        # EXACT 12pt line spacing (240 twips)
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '0')
        spacing.set(qn('w:after'), '0')
        spacing.set(qn('w:line'), '240')
        spacing.set(qn('w:lineRule'), 'exact')
        pPr.append(spacing)
        
        # Full justification
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'both')
        pPr.append(jc)
        
        if not style_element.xpath('./w:pPr'):
            style_element.append(pPr)
        
        # Font settings
        normal.font.name = 'Times New Roman'
        normal.font.size = Pt(10)

    # Modify Heading 1 style - IEEE SECTION HEADINGS (BOLD, CENTERED, UPPERCASE)
    if 'Heading 1' in styles:
        heading1 = styles['Heading 1']
        style_element = heading1.element
        pPr = style_element.xpath('./w:pPr')[0] if style_element.xpath('./w:pPr') else OxmlElement('w:pPr')
        
        # Clear existing formatting
        for elem in pPr.xpath('./w:spacing | ./w:jc'):
            pPr.remove(elem)
        
        # Section heading spacing: 12pt before, 0pt after
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '240')  # 12pt
        spacing.set(qn('w:after'), '0')
        spacing.set(qn('w:line'), '240')
        spacing.set(qn('w:lineRule'), 'exact')
        pPr.append(spacing)
        
        # Center alignment
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'center')
        pPr.append(jc)
        
        if not style_element.xpath('./w:pPr'):
            style_element.append(pPr)
        
        heading1.font.name = 'Times New Roman'
        heading1.font.size = Pt(10)
        heading1.font.bold = True

    # Modify Heading 2 style for subsections - IEEE SUBSECTION HEADINGS (BOLD, LEFT)
    if 'Heading 2' in styles:
        heading2 = styles['Heading 2']
        style_element = heading2.element
        pPr = style_element.xpath('./w:pPr')[0] if style_element.xpath('./w:pPr') else OxmlElement('w:pPr')
        
        # Clear existing formatting
        for elem in pPr.xpath('./w:spacing | ./w:jc'):
            pPr.remove(elem)
        
        # Subsection spacing: 6pt before, 0pt after
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '120')  # 6pt
        spacing.set(qn('w:after'), '0')
        spacing.set(qn('w:line'), '240')
        spacing.set(qn('w:lineRule'), 'exact')
        pPr.append(spacing)
        
        # Left alignment
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'left')
        pPr.append(jc)
        
        if not style_element.xpath('./w:pPr'):
            style_element.append(pPr)
        
        heading2.font.name = 'Times New Roman'
        heading2.font.size = Pt(10)
        heading2.font.bold = True

def add_title(doc, title):
    """Add the paper title - EXACT MATCH TO PDF: 24pt bold centered Times New Roman."""
    para = doc.add_paragraph()
    run = para.add_run(sanitize_text(title))
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(24)  # 24pt exactly like PDF
    
    # Apply exact OpenXML formatting
    pPr = para._element.get_or_add_pPr()
    
    # Clear existing formatting
    for elem in pPr.xpath('./w:spacing | ./w:jc'):
        pPr.remove(elem)
    
    # Center alignment
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)
    
    # Title spacing: 0pt before, 12pt after
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), '0')
    spacing.set(qn('w:after'), '240')  # 12pt
    pPr.append(spacing)

def add_authors(doc, authors):
    """Add authors with proper IEEE formatting - 3 authors per row, multiple rows if needed."""
    if not authors:
        return
    
    if len(authors) == 0:
        return
    
    # IEEE format: maximum 3 authors per row, create additional rows for more authors
    authors_per_row = 3
    total_authors = len(authors)
    
    # Process authors in groups of 3
    for row_start in range(0, total_authors, authors_per_row):
        row_end = min(row_start + authors_per_row, total_authors)
        row_authors = authors[row_start:row_end]
        num_cols = len(row_authors)
        
        # Create table for this row of authors
        table = doc.add_table(rows=1, cols=num_cols)
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        table.allow_autofit = True
        
        # Set table width to full page width
        table.style = 'Table Grid'
        table.style.font.name = IEEE_CONFIG['font_name']
        table.style.font.size = IEEE_CONFIG['font_size_body']
        
        # Remove table borders for clean IEEE look
        for table_row in table.rows:
            for cell in table_row.cells:
                # Remove all borders
                tc = cell._element
                tcPr = tc.get_or_add_tcPr()
                tcBorders = OxmlElement('w:tcBorders')
                for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                    border = OxmlElement(f'w:{border_name}')
                    border.set(qn('w:val'), 'nil')
                    tcBorders.append(border)
                tcPr.append(tcBorders)
        
        # Process each author in this row
        for col_idx, author in enumerate(row_authors):
            if not author.get('name'):
                continue
                
            cell = table.cell(0, col_idx)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            
            # Set equal column widths - always use 3 column layout for consistency
            cell.width = Inches(6.5 / 3)  # Always divide by 3 for consistent column width
            
            # Add proper cell margins for IEEE spacing
            cell_element = cell._element
            cell_properties = cell_element.get_or_add_tcPr()
            margins = OxmlElement('w:tcMar')
            
            # Set cell margins for proper IEEE author block spacing
            for side in ['left', 'right', 'top', 'bottom']:
                margin = OxmlElement(f'w:{side}')
                margin.set(qn('w:w'), '72')  # 0.05 inch margins
                margin.set(qn('w:type'), 'dxa')
                margins.append(margin)
            cell_properties.append(margins)
            
            # Clear any existing content
            cell._element.clear_content()
            
            # Author name - bold, centered (IEEE standard)
            name_para = cell.add_paragraph()
            name_run = name_para.add_run(sanitize_text(author['name']))
            name_run.bold = True  # IEEE standard: author names are bold
            name_run.font.name = IEEE_CONFIG['font_name']
            name_run.font.size = IEEE_CONFIG['font_size_body']
            name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            name_para.paragraph_format.space_before = Pt(0)
            name_para.paragraph_format.space_after = Pt(3)
            
            # Handle individual fields - department, organization, city, etc.
            fields = [
                ('department', 'Department'),
                ('organization', 'Organization'), 
                ('university', 'University'),
                ('institution', 'Institution'),
                ('city', 'City'),
                ('state', 'State'),
                ('country', 'Country')
            ]
            
            # Add each field as a separate line if present
            for field_key, field_name in fields:
                if author.get(field_key):
                    field_para = cell.add_paragraph()
                    field_run = field_para.add_run(sanitize_text(author[field_key]))
                    field_run.italic = True  # IEEE standard: affiliations are italic
                    field_run.font.name = IEEE_CONFIG['font_name']
                    field_run.font.size = IEEE_CONFIG['font_size_body']
                    field_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    field_para.paragraph_format.space_before = Pt(0)
                    field_para.paragraph_format.space_after = Pt(2)
            
            # Process affiliation string if present (for backward compatibility)
            if author.get('affiliation'):
                affiliation_text = author['affiliation']
                if isinstance(affiliation_text, str):
                    affiliation_lines = affiliation_text.strip().split('\n')
                    for line in affiliation_lines:
                        line = line.strip()
                        if line and not line.lower().startswith('email'):  # Skip email lines here
                            affil_para = cell.add_paragraph()
                            affil_run = affil_para.add_run(sanitize_text(line))
                            affil_run.italic = True  # IEEE standard: affiliations are italic
                            affil_run.font.name = IEEE_CONFIG['font_name']
                            affil_run.font.size = IEEE_CONFIG['font_size_body']
                            affil_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            affil_para.paragraph_format.space_before = Pt(0)
                            affil_para.paragraph_format.space_after = Pt(2)
            
            # Handle email field
            email = author.get('email', '')
            if email:
                email_para = cell.add_paragraph()
                email_run = email_para.add_run(sanitize_text(email))
                email_run.font.name = IEEE_CONFIG['font_name']
                email_run.font.size = Pt(9)  # Slightly smaller for email
                email_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                email_para.paragraph_format.space_before = Pt(2)
                email_para.paragraph_format.space_after = Pt(0)
            
            # Add custom fields if any
            for custom_field in author.get('custom_fields', []):
                if custom_field.get('value'):
                    custom_para = cell.add_paragraph()
                    custom_run = custom_para.add_run(sanitize_text(custom_field['value']))
                    custom_run.italic = True
                    custom_run.font.name = IEEE_CONFIG['font_name']
                    custom_run.font.size = IEEE_CONFIG['font_size_body']
                    custom_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    custom_para.paragraph_format.space_before = Pt(0)
                    custom_para.paragraph_format.space_after = Pt(2)
        
        # Add spacing between author rows (but not after the last row)
        if row_end < total_authors:
            spacing_para = doc.add_paragraph()
            spacing_para.paragraph_format.space_after = Pt(8)  # Space between author rows
    
    # Add proper spacing after all authors
    spacing_para = doc.add_paragraph()
    spacing_para.paragraph_format.space_after = Pt(12)  # IEEE standard spacing

def add_abstract(doc, abstract):
    """Add the abstract section - EXACT VISUAL MATCH TO PDF: 9pt bold with Abstract— prefix."""
    if abstract:
        # Add abstract with bold title and content in same paragraph - EXACTLY like PDF
        para = doc.add_paragraph()
        
        # Bold "Abstract—" title (EXACT MATCH TO PDF)
        title_run = para.add_run("Abstract—")
        title_run.bold = True  # PDF uses BOLD for Abstract—
        title_run.italic = False
        title_run.font.name = 'Times New Roman'
        title_run.font.size = Pt(9)  # 9pt like PDF
        
        # Add abstract content immediately after on SAME LINE (BOLD like PDF)
        content_run = para.add_run(sanitize_text(abstract))
        content_run.bold = True  # PDF uses BOLD for abstract content
        content_run.italic = False
        content_run.font.name = 'Times New Roman'
        content_run.font.size = Pt(9)  # 9pt like PDF
        
        # Apply exact OpenXML formatting
        pPr = para._element.get_or_add_pPr()
        
        # Clear existing formatting
        for elem in pPr.xpath('./w:spacing | ./w:jc'):
            pPr.remove(elem)
        
        # Full justification
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'both')
        pPr.append(jc)
        
        # Abstract spacing: 0pt before, 6pt after
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '0')
        spacing.set(qn('w:after'), '120')  # 6pt
        pPr.append(spacing)

def add_keywords(doc, keywords):
    """Add the keywords section - EXACT IEEE LaTeX PDF formatting with OpenXML."""
    if keywords:
        # Add keywords with bold title and content in same paragraph
        para = doc.add_paragraph()
        
        # Bold "Keywords—" title (EXACT MATCH TO PDF)
        title_run = para.add_run("Keywords—")
        title_run.bold = True  # PDF uses BOLD for Keywords—
        title_run.italic = False
        title_run.font.name = 'Times New Roman'
        title_run.font.size = Pt(9)  # 9pt like PDF
        
        # Add keywords content immediately after on SAME LINE (BOLD like PDF)
        content_run = para.add_run(sanitize_text(keywords))
        content_run.bold = True  # PDF uses BOLD for keywords content
        content_run.italic = False
        content_run.font.name = 'Times New Roman'
        content_run.font.size = Pt(9)  # 9pt like PDF
        
        # Apply exact OpenXML formatting
        pPr = para._element.get_or_add_pPr()
        
        # Clear existing formatting
        for elem in pPr.xpath('./w:spacing | ./w:jc'):
            pPr.remove(elem)
        
        # Full justification
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'both')
        pPr.append(jc)
        
        # Keywords spacing: 0pt before, 12pt after
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '0')
        spacing.set(qn('w:after'), '240')  # 12pt
        pPr.append(spacing)

def apply_ieee_latex_formatting(para, spacing_before=0, spacing_after=0, line_spacing=240):
    """Apply EXACT IEEE LaTeX PDF formatting using low-level OpenXML editing."""
    pPr = para._element.get_or_add_pPr()
    
    # Clear existing formatting first
    for elem in pPr.xpath('./w:spacing | ./w:jc | ./w:adjustRightInd | ./w:snapToGrid'):
        pPr.remove(elem)
    
    # 1. FULL JUSTIFICATION = EQUAL LINE LENGTHS (distribute)
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'distribute')  # Equal line lengths like LaTeX
    pPr.append(jc)
    
    # 2. EXACT LINE SPACING (12pt = 240 twips)
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), str(spacing_before))
    spacing.set(qn('w:after'), str(spacing_after))
    spacing.set(qn('w:line'), str(line_spacing))
    spacing.set(qn('w:lineRule'), 'exact')
    pPr.append(spacing)
    
    # 3. ADVANCED JUSTIFICATION CONTROLS
    adjustRightInd = OxmlElement('w:adjustRightInd')
    adjustRightInd.set(qn('w:val'), '1')
    pPr.append(adjustRightInd)
    
    snapToGrid = OxmlElement('w:snapToGrid')
    snapToGrid.set(qn('w:val'), '0')
    pPr.append(snapToGrid)
    
    # 4. CHARACTER-LEVEL FORMATTING FOR TIGHT JUSTIFICATION
    for run in para.runs:
        rPr = run._element.get_or_add_rPr()
        
        # Clear existing character formatting
        for elem in rPr.xpath('./w:spacing | ./w:kern | ./w:w'):
            rPr.remove(elem)
        
        # Compress character spacing (-15 twips)
        spacing_elem = OxmlElement('w:spacing')
        spacing_elem.set(qn('w:val'), '-15')
        rPr.append(spacing_elem)
        
        # Tight kerning (8 twips)
        kern = OxmlElement('w:kern')
        kern.set(qn('w:val'), '8')
        rPr.append(kern)
        
        # Character width scaling (95%)
        w_elem = OxmlElement('w:w')
        w_elem.set(qn('w:val'), '95')
        rPr.append(w_elem)

def setup_two_column_layout(doc):
    """Setup TWO-COLUMN LAYOUT after abstract/keywords - EXACT IEEE LaTeX specifications."""
    # Add section break for two-column layout
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    new_section.start_type = WD_SECTION.CONTINUOUS
    
    # Configure two-column layout via OpenXML with EXACT IEEE specifications
    sectPr = new_section._sectPr
    
    # Set margins - EXACT IEEE LaTeX: 0.75" all sides (1080 twips)
    pgMar = sectPr.xpath('./w:pgMar')[0] if sectPr.xpath('./w:pgMar') else OxmlElement('w:pgMar')
    pgMar.set(qn('w:left'), '1080')
    pgMar.set(qn('w:right'), '1080')
    pgMar.set(qn('w:top'), '1080')
    pgMar.set(qn('w:bottom'), '1080')
    if not sectPr.xpath('./w:pgMar'):
        sectPr.append(pgMar)
    
    # Remove existing cols element if present
    existing_cols = sectPr.xpath('./w:cols')
    for col in existing_cols:
        sectPr.remove(col)
    
    # Add new cols element with EXACT IEEE LaTeX specifications
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'), '2')  # 2 columns
    cols.set(qn('w:space'), '360')  # 0.25" gap (360 twips)
    cols.set(qn('w:equalWidth'), '1')  # Equal width columns
    
    # Add column definitions - EXACT 3.3125" per column (4770 twips)
    for i in range(2):
        col = OxmlElement('w:col')
        col.set(qn('w:w'), '4770')  # 3.3125" width
        cols.append(col)
    
    sectPr.append(cols)

def add_ieee_body_paragraph(doc, text):
    """Add a body paragraph with EXACT IEEE LaTeX PDF formatting via OpenXML."""
    para = doc.add_paragraph()
    run = para.add_run(sanitize_text(text))
    
    # Font: Times New Roman 10pt
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    
    # FIXED: Apply full IEEE justification using the dedicated function
    apply_ieee_latex_formatting(para, spacing_before=0, spacing_after=0, line_spacing=240)
    
    return para

def add_justified_paragraph(doc, text, style_name='Normal', indent_left=None, indent_right=None, space_before=None, space_after=None):
    """Add a paragraph with professional justification settings for research paper quality."""
    # Use the new IEEE body paragraph function for exact formatting
    return add_ieee_body_paragraph(doc, text)

def add_section(doc, section_data, section_idx, is_first_section=False):
    """Add a section with content blocks, subsections, and figures - EXACT same as test.py."""
    if section_data.get('title'):
        # Create section heading with exact IEEE LaTeX formatting
        para = doc.add_paragraph()
        run = para.add_run(f"{section_idx}. {sanitize_text(section_data['title']).upper()}")
        
        # Font: Times New Roman 10pt bold
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.bold = True
        
        # Apply exact OpenXML formatting for section headings
        pPr = para._element.get_or_add_pPr()
        
        # Clear existing formatting
        for elem in pPr.xpath('./w:spacing | ./w:jc'):
            pPr.remove(elem)
        
        # Center alignment (IEEE standard for section headings)
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'center')
        pPr.append(jc)
        
        # Section heading spacing: 12pt before, 0pt after
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '240')  # 12pt before
        spacing.set(qn('w:after'), '0')     # 0pt after
        spacing.set(qn('w:line'), '240')    # 12pt line spacing
        spacing.set(qn('w:lineRule'), 'exact')
        pPr.append(spacing)

    # Process content blocks (text and images in order) - Support BOTH naming conventions
    content_blocks = section_data.get('contentBlocks', []) or section_data.get('content_blocks', [])
    
    for block_idx, block in enumerate(content_blocks):
        if block.get('type') == 'text' and block.get('content'):
            space_before = IEEE_CONFIG['line_spacing'] if is_first_section and block_idx == 0 else Pt(3)
            add_formatted_paragraph(
                doc, 
                block['content'],
                indent_left=IEEE_CONFIG['column_indent'],
                indent_right=IEEE_CONFIG['column_indent'],
                space_before=space_before,
                space_after=Pt(12)
            )
            
            # Check if this text block also has an image attached (React frontend pattern)
            if block.get('data') and block.get('caption'):
                # Handle image attached to text block
                import base64
                size = block.get('size', 'medium')
                # Map frontend size names to backend size names
                size_mapping = {
                    'very-small': 'Very Small',
                    'small': 'Small', 
                    'medium': 'Medium',
                    'large': 'Large'
                }
                mapped_size = size_mapping.get(size, 'Medium')
                width = IEEE_CONFIG['figure_sizes'].get(mapped_size, IEEE_CONFIG['figure_sizes']['Medium'])
                
                # Decode base64 image data
                try:
                    image_data = block['data']
                    
                    # Handle base64 data - remove prefix if present
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    # Decode base64 image data
                    try:
                        image_bytes = base64.b64decode(image_data)
                    except Exception as e:
                        print(f"ERROR: Failed to decode image data in text block: {str(e)}", file=sys.stderr)
                        continue
                    
                    # Create image stream
                    image_stream = BytesIO(image_bytes)
                    
                    para = doc.add_paragraph()
                    run = para.add_run()
                    picture = run.add_picture(image_stream, width=width)
                    if picture.height > IEEE_CONFIG['max_figure_height']:
                        scale_factor = IEEE_CONFIG['max_figure_height'] / picture.height
                        run.clear()
                        run.add_picture(image_stream, width=width * scale_factor, height=IEEE_CONFIG['max_figure_height'])
                    
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.paragraph_format.space_before = Pt(6)
                    para.paragraph_format.space_after = Pt(6)
                    
                    # Generate figure number based on section and image position
                    img_count = sum(1 for b in content_blocks[:block_idx+1] if b.get('type') == 'image' or (b.get('type') == 'text' and b.get('data')))
                    caption = doc.add_paragraph(f"Fig. {section_idx}.{img_count}: {sanitize_text(block['caption'])}")
                    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    caption.paragraph_format.space_before = Pt(0)
                    caption.paragraph_format.space_after = Pt(12)
                    if caption.runs:
                        caption.runs[0].font.name = IEEE_CONFIG['font_name']
                        caption.runs[0].font.size = IEEE_CONFIG['font_size_caption']
                except Exception as e:
                    print(f"Error processing image in text block: {e}", file=sys.stderr)
                    
        elif block.get('type') == 'image' and block.get('data') and block.get('caption'):
            # FIXED: Handle image blocks from React frontend with proper spacing
            import base64
            size = block.get('size', 'medium')
            # Map frontend size names to backend size names
            size_mapping = {
                'very-small': 'Very Small',
                'small': 'Small', 
                'medium': 'Medium',
                'large': 'Large'
            }
            mapped_size = size_mapping.get(size, 'Medium')
            width = IEEE_CONFIG['figure_sizes'].get(mapped_size, IEEE_CONFIG['figure_sizes']['Medium'])
            
            # Decode base64 image data
            try:
                image_data = block['data']
                
                # Handle base64 data - remove prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                # Decode base64 image data
                try:
                    image_bytes = base64.b64decode(image_data)
                except Exception as e:
                    print(f"ERROR: Failed to decode image data: {str(e)}", file=sys.stderr)
                    continue
                
                # Create image stream
                image_stream = BytesIO(image_bytes)
                
                # FIXED: Image spacing - wrap image in its own paragraph with proper spacing
                para = doc.add_paragraph()
                run = para.add_run()
                picture = run.add_picture(image_stream, width=width)
                if picture.height > IEEE_CONFIG['max_figure_height']:
                    scale_factor = IEEE_CONFIG['max_figure_height'] / picture.height
                    run.clear()
                    run.add_picture(image_stream, width=width * scale_factor, height=IEEE_CONFIG['max_figure_height'])
                
                # FIXED: Image spacing
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                para.paragraph_format.space_before = Pt(6)  # 6pt before image
                para.paragraph_format.space_after = Pt(6)   # 6pt after image
                para.paragraph_format.keep_with_next = True  # Keep with caption
                
                # FIXED: Caption - separate paragraph, centered, italic 9pt
                img_count = sum(1 for b in content_blocks[:block_idx+1] if b.get('type') == 'image')
                caption = doc.add_paragraph(f"Fig. {section_idx}.{img_count}: {sanitize_text(block['caption'])}")
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption.paragraph_format.space_before = Pt(0)   # 0pt before caption
                caption.paragraph_format.space_after = Pt(12)   # 12pt after caption
                if caption.runs:
                    caption.runs[0].font.name = 'Times New Roman'
                    caption.runs[0].font.size = Pt(9)  # 9pt caption
                    caption.runs[0].italic = True       # Italic caption
                
                # FIXED: Prevent overlap - add spacing after figure block
                spacing = doc.add_paragraph()
                spacing.paragraph_format.space_after = Pt(12)  # 12pt spacing to prevent overlap
            except Exception as e:
                print(f"Error processing image: {e}", file=sys.stderr)

    # Legacy support for old content field - EXACT same as test.py
    if not content_blocks and section_data.get('content'):
        space_before = IEEE_CONFIG['line_spacing'] if is_first_section else Pt(3)
        add_justified_paragraph(
            doc, 
            section_data['content'],
            indent_left=IEEE_CONFIG['column_indent'],
            indent_right=IEEE_CONFIG['column_indent'],
            space_before=space_before,
            space_after=Pt(12)
        )

    # Add subsections with multi-level support
    def add_subsection_recursive(subsections, section_idx, parent_numbering=""):
        """Recursively add subsections with proper hierarchical numbering."""
        # Group subsections by level and parent
        level_1_subsections = [s for s in subsections if s.get('level', 1) == 1 and not s.get('parentId')]
        
        for sub_idx, subsection in enumerate(level_1_subsections, 1):
            if subsection.get('title'):
                subsection_number = f"{section_idx}.{sub_idx}"
                para = doc.add_heading(f"{subsection_number} {sanitize_text(subsection['title'])}", level=2)
                para.paragraph_format.page_break_before = False
                para.paragraph_format.space_before = IEEE_CONFIG['line_spacing']
                para.paragraph_format.space_after = Pt(0)
                para.paragraph_format.keep_with_next = False
                para.paragraph_format.keep_together = False
                para.paragraph_format.widow_control = False

            if subsection.get('content'):
                add_justified_paragraph(
                    doc, 
                    sanitize_text(subsection['content']),
                    indent_left=IEEE_CONFIG['column_indent'],
                    indent_right=IEEE_CONFIG['column_indent'],
                    space_before=Pt(1),
                    space_after=Pt(12)
                )
            
            # Handle nested subsections (level 2 and beyond)
            add_nested_subsection(subsections, subsection['id'], f"{section_idx}.{sub_idx}", 2)
    
    def add_nested_subsection(all_subsections, parent_id, parent_number, level):
        """Add nested subsections recursively."""
        child_subsections = [s for s in all_subsections if s.get('parentId') == parent_id and s.get('level', 1) == level]
        
        for child_idx, child_sub in enumerate(child_subsections, 1):
            # Always define child_number, regardless of whether title exists
            child_number = f"{parent_number}.{child_idx}"
            
            if child_sub.get('title'):
                # Use different heading levels for deeper nesting, but cap at level 6
                heading_level = min(level + 1, 6)
                para = doc.add_heading(f"{child_number} {sanitize_text(child_sub['title'])}", level=heading_level)
                para.paragraph_format.page_break_before = False
                para.paragraph_format.space_before = Pt(6)
                para.paragraph_format.space_after = Pt(0)
                para.paragraph_format.keep_with_next = False
                para.paragraph_format.keep_together = False
                para.paragraph_format.widow_control = False

            if child_sub.get('content'):
                add_justified_paragraph(
                    doc, 
                    sanitize_text(child_sub['content']),
                    indent_left=IEEE_CONFIG['column_indent'] + Inches(0.1 * (level - 1)),  # Progressive indentation
                    indent_right=IEEE_CONFIG['column_indent'],
                    space_before=Pt(1),
                    space_after=Pt(12)
                )
            
            # Process content blocks if they exist
            if child_sub.get('contentBlocks'):
                for block in child_sub['contentBlocks']:
                    if block.get('type') == 'text' and block.get('content'):
                        add_formatted_paragraph(
                            doc, 
                            block['content'],
                            indent_left=IEEE_CONFIG['column_indent'] + Inches(0.1 * (level - 1)),
                            indent_right=IEEE_CONFIG['column_indent'],
                            space_before=Pt(1),
                            space_after=Pt(12)
                        )
            
            # Recursively handle even deeper nesting
            if level < 5:  # Limit depth to prevent excessive nesting
                add_nested_subsection(all_subsections, child_sub['id'], child_number, level + 1)
    
    # Call the recursive function to add all subsections
    add_subsection_recursive(section_data.get('subsections', []), section_idx)

class HTMLToWordParser(HTMLParser):
    """Parse HTML content and apply formatting to Word document."""
    
    def __init__(self, paragraph):
        super().__init__()
        self.paragraph = paragraph
        self.format_stack = []
        self.text_buffer = ""
    
    def handle_starttag(self, tag, attrs):
        # Flush any buffered text before starting new formatting
        self._flush_text()
        
        if tag.lower() in ['b', 'strong']:
            self.format_stack.append('bold')
        elif tag.lower() in ['i', 'em']:
            self.format_stack.append('italic')
        elif tag.lower() == 'u':
            self.format_stack.append('underline')
    
    def handle_endtag(self, tag):
        # Flush any buffered text before ending formatting
        self._flush_text()
        
        if tag.lower() in ['b', 'strong'] and 'bold' in self.format_stack:
            self.format_stack.remove('bold')
        elif tag.lower() in ['i', 'em'] and 'italic' in self.format_stack:
            self.format_stack.remove('italic')
        elif tag.lower() == 'u' and 'underline' in self.format_stack:
            self.format_stack.remove('underline')
    
    def handle_data(self, data):
        # Buffer the text data with sanitization
        self.text_buffer += sanitize_text(data)
    
    def _flush_text(self):
        """Create a run with accumulated text and current formatting."""
        if self.text_buffer:
            run = self.paragraph.add_run(self.text_buffer)
            run.font.name = IEEE_CONFIG['font_name']
            run.font.size = IEEE_CONFIG['font_size_body']
            
            # Apply current formatting
            if 'bold' in self.format_stack:
                run.bold = True
            if 'italic' in self.format_stack:
                run.italic = True
            if 'underline' in self.format_stack:
                run.underline = True
            
            self.text_buffer = ""
    
    def close(self):
        """Ensure any remaining text is flushed when parsing is complete."""
        self._flush_text()
        super().close()

def apply_equal_justification(para):
    """Apply comprehensive equal justification controls for perfect equal line lengths like research papers."""
    # Get paragraph element for XML manipulation
    para_element = para._element
    pPr = para_element.get_or_add_pPr()
    
    # Primary justification setting - distribute text evenly across line
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'distribute')  # Distribute justification for equal line lengths
    pPr.append(jc)
    
    # Proper line spacing for 10pt text (IEEE standard)
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:after'), '0')
    spacing.set(qn('w:before'), '0')
    spacing.set(qn('w:line'), '276')  # 13.8pt line spacing in twips (1.38 * 10pt * 20)
    spacing.set(qn('w:lineRule'), 'exact')
    pPr.append(spacing)
    
    # Text alignment baseline for consistent line positioning
    textAlignment = OxmlElement('w:textAlignment')
    textAlignment.set(qn('w:val'), 'baseline')
    pPr.append(textAlignment)
    
    # Force equal line lengths by enabling right margin adjustment
    adjust_right_ind = OxmlElement('w:adjustRightInd')
    adjust_right_ind.set(qn('w:val'), '1')  # Allow right margin adjustment for equal line lengths
    pPr.append(adjust_right_ind)
    
    # Enable text compression for better line fitting
    compress_punctuation = OxmlElement('w:compressPunctuation')
    compress_punctuation.set(qn('w:val'), '1')
    pPr.append(compress_punctuation)
    
    # Control automatic spacing for better justification
    auto_space_de = OxmlElement('w:autoSpaceDE')
    auto_space_de.set(qn('w:val'), '1')  # Enable auto spacing between Asian and Latin text
    pPr.append(auto_space_de)
    
    auto_space_dn = OxmlElement('w:autoSpaceDN')
    auto_space_dn.set(qn('w:val'), '1')  # Enable auto spacing between Asian text and numbers
    pPr.append(auto_space_dn)
    
    # Word wrap settings for better line breaks
    word_wrap = OxmlElement('w:wordWrap')
    word_wrap.set(qn('w:val'), '1')
    pPr.append(word_wrap)
    
    # Enable text distribution for equal line lengths
    text_direction = OxmlElement('w:textDirection')
    text_direction.set(qn('w:val'), 'lrTb')  # Left-to-right, top-to-bottom
    pPr.append(text_direction)
    
    # Force equal line distribution
    snap_to_grid = OxmlElement('w:snapToGrid')
    snap_to_grid.set(qn('w:val'), '0')  # Disable grid snapping for better justification
    pPr.append(snap_to_grid)
    
    # Character-level spacing controls for runs - allow flexibility for equal lines
    for run in para.runs:
        run_element = run._element
        rPr = run_element.get_or_add_rPr()
        
        # Allow character spacing adjustment for equal line lengths
        char_spacing = OxmlElement('w:spacing')
        char_spacing.set(qn('w:val'), '0')  # Start with no compression
        rPr.append(char_spacing)
        
        # Enable kerning for professional typography
        kern = OxmlElement('w:kern')
        kern.set(qn('w:val'), '20')  # 1pt kerning threshold
        rPr.append(kern)
        
        # Allow position adjustment for better line fitting
        position = OxmlElement('w:position')
        position.set(qn('w:val'), '0')
        rPr.append(position)
        
        # Enable text scaling for equal line lengths
        w_element = OxmlElement('w:w')
        w_element.set(qn('w:val'), '100')  # 100% width scaling (can be adjusted by Word)
        rPr.append(w_element)
    
    return para

def apply_perfect_research_justification(para):
    """Apply PERFECT research paper quality justification - 200% perfect like top academic journals."""
    
    # Get paragraph element for XML manipulation
    para_element = para._element
    pPr = para_element.get_or_add_pPr()
    
    # AGGRESSIVE justification setting - force perfect distribution
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'distribute')  # Distribute justification for absolutely equal line lengths
    pPr.append(jc)
    
    # PERFECT line spacing for 10pt text (IEEE standard) - EXACT control
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:after'), '0')
    spacing.set(qn('w:before'), '0')
    spacing.set(qn('w:line'), '276')  # 13.8pt line spacing in twips (1.38 * 10pt * 20)
    spacing.set(qn('w:lineRule'), 'exact')
    pPr.append(spacing)
    
    # BASELINE alignment for research paper consistency
    textAlignment = OxmlElement('w:textAlignment')
    textAlignment.set(qn('w:val'), 'baseline')
    pPr.append(textAlignment)
    
    # FORCE perfect line lengths by AGGRESSIVE right margin adjustment
    adjust_right_ind = OxmlElement('w:adjustRightInd')
    adjust_right_ind.set(qn('w:val'), '1')  # MAXIMUM right margin adjustment for perfect equal line lengths
    pPr.append(adjust_right_ind)
    
    # MAXIMUM text compression for perfect line fitting
    compress_punctuation = OxmlElement('w:compressPunctuation')
    compress_punctuation.set(qn('w:val'), '1')
    pPr.append(compress_punctuation)
    
    # PERFECT spacing controls for research paper quality
    auto_space_de = OxmlElement('w:autoSpaceDE')
    auto_space_de.set(qn('w:val'), '1')  # Perfect Asian-Latin spacing
    pPr.append(auto_space_de)
    
    auto_space_dn = OxmlElement('w:autoSpaceDN')
    auto_space_dn.set(qn('w:val'), '1')  # Perfect Asian-numeric spacing
    pPr.append(auto_space_dn)
    
    # PROFESSIONAL word wrapping for academic quality
    word_wrap = OxmlElement('w:wordWrap')
    word_wrap.set(qn('w:val'), '1')
    pPr.append(word_wrap)
    
    # PERFECT text direction for research papers
    text_direction = OxmlElement('w:textDirection')
    text_direction.set(qn('w:val'), 'lrTb')  # Left-to-right, top-to-bottom
    pPr.append(text_direction)
    
    # DISABLE grid snapping for MAXIMUM justification control
    snap_to_grid = OxmlElement('w:snapToGrid')
    snap_to_grid.set(qn('w:val'), '0')  # No grid interference with perfect justification
    pPr.append(snap_to_grid)
    
    # RESEARCH PAPER specific advanced controls
    # Force consistent line heights for academic quality
    line_rule = OxmlElement('w:lineRule')
    line_rule.set(qn('w:val'), 'exact')
    pPr.append(line_rule)
    
    # Prevent widow/orphan that breaks perfect justification
    widow_control = OxmlElement('w:widowControl')
    widow_control.set(qn('w:val'), '0')
    pPr.append(widow_control)
    
    # ACADEMIC JOURNAL quality spacing - no auto spacing
    space_before_auto = OxmlElement('w:spaceBeforeAuto')
    space_before_auto.set(qn('w:val'), '0')
    pPr.append(space_before_auto)
    
    space_after_auto = OxmlElement('w:spaceAfterAuto')
    space_after_auto.set(qn('w:val'), '0')
    pPr.append(space_after_auto)
    
    # AGGRESSIVE character-level controls for PERFECT distribution
    for run in para.runs:
        run_element = run._element
        rPr = run_element.get_or_add_rPr()
        
        # AGGRESSIVE character spacing for perfect equal line lengths
        char_spacing = OxmlElement('w:spacing')
        char_spacing.set(qn('w:val'), '-20')  # STRONG compression for perfect distribution
        rPr.append(char_spacing)
        
        # MAXIMUM kerning for professional typography
        kern = OxmlElement('w:kern')
        kern.set(qn('w:val'), '14')  # Aggressive kerning for tight, professional spacing
        rPr.append(kern)
        
        # PRECISE position control for perfect alignment
        position = OxmlElement('w:position')
        position.set(qn('w:val'), '0')
        rPr.append(position)
        
        # AGGRESSIVE text scaling for perfect line fitting
        w_element = OxmlElement('w:w')
        w_element.set(qn('w:val'), '90')  # 90% width scaling for tighter, more professional fit
        rPr.append(w_element)
        
        # RESEARCH PAPER quality font controls
        sz_cs = OxmlElement('w:szCs')
        sz_cs.set(qn('w:val'), str(int(IEEE_CONFIG['font_size_body'].pt * 2)))  # Ensure consistent size
        rPr.append(sz_cs)
        
        # DISABLE automatic expansion that breaks perfect justification
        no_proof = OxmlElement('w:noProof')
        no_proof.set(qn('w:val'), '1')
        rPr.append(no_proof)
    
    return para

def add_formatted_paragraph(doc, html_content, **kwargs):
    """FIXED: Add a paragraph with HTML formatting support and EXACT IEEE LaTeX formatting."""
    para = add_ieee_body_paragraph(doc, html_content or "")
    
    # FIXED: Ensure spacing parameters are applied if provided
    if 'space_before' in kwargs and kwargs['space_before'] is not None:
        para.paragraph_format.space_before = kwargs['space_before']
    if 'space_after' in kwargs and kwargs['space_after'] is not None:
        para.paragraph_format.space_after = kwargs['space_after']
    
    return para

def add_references(doc, references):
    """Add references section with proper alignment (hanging indent) and perfect justification."""
    if references:
        para = doc.add_heading("REFERENCES", level=1)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER  # Center references heading
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.keep_with_next = False
        
        for idx, ref in enumerate(references, 1):
            # Handle both string references and object references
            if isinstance(ref, str):
                ref_text = sanitize_text(ref)
            elif isinstance(ref, dict) and ref.get('text'):
                ref_text = sanitize_text(ref['text'])
            else:
                continue  # Skip invalid references
                
            # Create reference paragraph with hanging indent
            para = doc.add_paragraph(f"[{idx}] {ref_text}")
            
            # Apply IEEE reference formatting with hanging indent
            pPr = para._element.get_or_add_pPr()
            
            # Hanging indent: 0.25" (360 twips)
            ind = OxmlElement('w:ind')
            ind.set(qn('w:hanging'), '360')  # 0.25" hanging indent
            pPr.append(ind)
            
            # Reference spacing: 3pt before, 12pt after
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:before'), '60')   # 3pt before
            spacing.set(qn('w:after'), '240')   # 12pt after
            spacing.set(qn('w:line'), '180')    # 9pt line spacing for references
            spacing.set(qn('w:lineRule'), 'exact')
            pPr.append(spacing)
            
            # Set font: Times New Roman 9pt
            if para.runs:
                para.runs[0].font.name = 'Times New Roman'
                para.runs[0].font.size = Pt(9)  # 9pt for references
                
                # Apply perfect justification with equal line lengths
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                apply_equal_justification(para)

def enable_auto_hyphenation(doc):
    """Enable professional hyphenation to improve justification quality."""
    section = doc.sections[-1]
    sectPr = section._sectPr

    # Enable automatic hyphenation for better justification
    auto_hyphenation = OxmlElement('w:autoHyphenation')
    auto_hyphenation.set(qn('w:val'), '1')
    sectPr.append(auto_hyphenation)

    # Do NOT hyphenate capitalized words (proper nouns, acronyms)
    do_not_hyphenate_caps = OxmlElement('w:doNotHyphenateCaps')
    do_not_hyphenate_caps.set(qn('w:val'), '1')
    sectPr.append(do_not_hyphenate_caps)

    # Set optimal hyphenation zone for research papers (0.25 inch)
    hyphenation_zone = OxmlElement('w:hyphenationZone')
    hyphenation_zone.set(qn('w:val'), '360')  # 0.25 inch in twips
    sectPr.append(hyphenation_zone)

    # Limit consecutive hyphens to maintain readability
    consecutive_hyphen_limit = OxmlElement('w:consecutiveHyphenLimit')
    consecutive_hyphen_limit.set(qn('w:val'), '2')
    sectPr.append(consecutive_hyphen_limit)

def set_compatibility_options(doc):
    """Set compatibility options to optimize spacing and justification for research paper quality with equal line lengths."""
    compat = doc.settings.element.find(qn('w:compat'))
    if compat is None:
        doc.settings.element.append(OxmlElement('w:compat'))
        compat = doc.settings.element.find(qn('w:compat'))

    # Critical options for professional justification with equal line lengths
    
    # Use Word 2010+ justification algorithm for better spacing
    option1 = OxmlElement('w:useWord2010TableStyleRules')
    option1.set(qn('w:val'), '1')
    compat.append(option1)
    
    # Enable better line breaking for justified text
    option2 = OxmlElement('w:doNotBreakWrappedTables')
    option2.set(qn('w:val'), '1')
    compat.append(option2)
    
    # Use consistent font metrics for better spacing
    option3 = OxmlElement('w:useWord97LineBreakRules')
    option3.set(qn('w:val'), '0')  # Disable old line break rules
    compat.append(option3)
    
    # Enable advanced justification for equal line lengths
    option4 = OxmlElement('w:doNotExpandShiftReturn')
    option4.set(qn('w:val'), '1')  # Better line break handling
    compat.append(option4)
    
    # Force consistent character spacing
    option5 = OxmlElement('w:doNotUseEastAsianBreakRules')
    option5.set(qn('w:val'), '1')  # Use Western justification rules
    compat.append(option5)
    
    # Enable text compression for equal line fitting
    option6 = OxmlElement('w:allowSpaceOfSameStyleInTable')
    option6.set(qn('w:val'), '1')  # Better spacing in justified text
    compat.append(option6)
    
    # Prevent Word from expanding spaces for justification
    option2 = OxmlElement('w:doNotExpandShiftReturn')
    option2.set(qn('w:val'), '1')
    compat.append(option2)
    
    # Use consistent character spacing
    option3 = OxmlElement('w:useSingleBorderforContiguousCells')
    option3.set(qn('w:val'), '1')
    compat.append(option3)
    
    # Force exact spacing calculations
    option4 = OxmlElement('w:spacingInWholePoints')
    option4.set(qn('w:val'), '1')
    compat.append(option4)
    
    # Prevent auto spacing adjustments
    option5 = OxmlElement('w:doNotUseHTMLParagraphAutoSpacing')
    option5.set(qn('w:val'), '1')
    compat.append(option5)
    
    # Use legacy justification method (more precise)
    option6 = OxmlElement('w:useWord97LineBreakRules')
    option6.set(qn('w:val'), '1')
    compat.append(option6)
    
    # Disable automatic kerning adjustments
    option7 = OxmlElement('w:doNotAutoCompressPictures')
    option7.set(qn('w:val'), '1')
    compat.append(option7)
    
    # Force consistent text metrics
    option8 = OxmlElement('w:useNormalStyleForList')
    option8.set(qn('w:val'), '1')
    compat.append(option8)
    
    # Prevent text compression/expansion
    option9 = OxmlElement('w:doNotPromoteQF')
    option9.set(qn('w:val'), '1')
    compat.append(option9)
    
    # Use exact font metrics
    option10 = OxmlElement('w:useAltKinsokuLineBreakRules')
    option10.set(qn('w:val'), '0')
    compat.append(option10)

def generate_ieee_document(form_data):
    """Generate IEEE-formatted Word document with EXACT LaTeX PDF formatting via OpenXML."""
    doc = Document()
    
    # Apply EXACT IEEE LaTeX PDF specifications
    set_document_defaults(doc)
    
    # Configure first section for single-column title and authors (IEEE LaTeX standard)
    section = doc.sections[0]
    section.left_margin = Inches(0.75)   # EXACT IEEE LaTeX: 0.75" margins
    section.right_margin = Inches(0.75)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    
    # Add title and authors in single-column layout (EXACT IEEE LaTeX standard)
    add_title(doc, form_data.get('title', ''))
    add_authors(doc, form_data.get('authors', []))

    # Setup TWO-COLUMN LAYOUT for body content (EXACT IEEE LaTeX specifications)
    setup_two_column_layout(doc)
    
    # Add abstract and keywords in two-column layout with EXACT IEEE LaTeX formatting
    add_abstract(doc, form_data.get('abstract', ''))
    add_keywords(doc, form_data.get('keywords', ''))
    
    # Add sections with EXACT IEEE LaTeX formatting
    for idx, section_data in enumerate(form_data.get('sections', []), 1):
        add_section(doc, section_data, idx, is_first_section=(idx == 1))
    
    # Add references with EXACT IEEE LaTeX formatting
    add_references(doc, form_data.get('references', []))
    
    # Apply final IEEE LaTeX compatibility settings
    enable_auto_hyphenation(doc)
    set_compatibility_options(doc)
    
    # Generate final document
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def generate_ieee_html_preview(form_data):
    """Generate HTML preview that matches IEEE formatting exactly"""
    
    # Extract document data
    title = sanitize_text(form_data.get('title', 'Untitled Document'))
    authors = form_data.get('authors', [])
    abstract = sanitize_text(form_data.get('abstract', ''))
    keywords = sanitize_text(form_data.get('keywords', ''))
    sections = form_data.get('sections', [])
    references = form_data.get('references', [])
    
    # Format authors in table format matching DOCX IEEE style exactly
    authors_html = ''
    if authors:
        num_authors = len(authors)
        # Use inline-block for robust cross-browser support with proper spacing
        authors_html = f'<table style="width: 100%; border-collapse: collapse; margin: 0 auto; text-align: center; table-layout: fixed; display: table; box-sizing: border-box;"><tr style="display: table-row; width: 100%;">'
        
        for idx, author in enumerate(authors):
            # Author Name (bold)
            author_name = sanitize_text(author.get('name', ''))
            author_info = f"<strong>{author_name}</strong>"
            
            # Affiliation Fields in proper IEEE order: department, organization, city, state
            fields = ['department', 'organization', 'city', 'state']
            for field in fields:
                if author.get(field):
                    author_info += f"<br/><em>{sanitize_text(author[field])}</em>"
            
            # Email
            if author.get('email'):
                author_info += f"<br/><em>{sanitize_text(author['email'])}</em>"
            
            # Fallback to 'affiliation' if structured fields not available
            if not any(author.get(field) for field in fields) and author.get('affiliation'):
                author_info += f"<br/><em>{sanitize_text(author['affiliation'])}</em>"
            
            # Enhanced cell styling with box-sizing for proper width calculation
            col_width = 100 / num_authors
            authors_html += f'<td style="width: {col_width:.1f}%; vertical-align: top; padding: 8px; border: none; display: table-cell; box-sizing: border-box; word-wrap: break-word; overflow-wrap: break-word;">{author_info}</td>'
        
        authors_html += '</tr></table>'
    else:
        authors_html = '<div style="text-align: center; font-style: italic;">Anonymous</div>'
    
    # Create HTML with exact IEEE-like styling
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Times New Roman', serif;
                font-size: 10pt;
                line-height: 1.2;
                margin: 0.75in;
                background: white;
                color: black;
                text-align: justify;
            }}
            .ieee-title {{
                font-size: 24pt;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
                line-height: 1.3;
            }}
            .ieee-authors {{
                font-size: 10pt;
                text-align: center;
                margin: 15px 0;
            }}
            .ieee-section {{
                margin: 15px 0;
                text-align: justify;
            }}
            .ieee-abstract-title {{
                font-weight: bold;
                display: inline;
            }}
            .ieee-keywords-title {{
                font-weight: bold;
                display: inline;
            }}
            .ieee-heading {{
                font-weight: bold;
                margin: 15px 0 5px 0;
                text-transform: uppercase;
                font-size: 10pt;
            }}
            .ieee-reference {{
                margin: 3px 0;
                padding-left: 15px;
                text-indent: -15px;
                font-size: 9pt;
            }}
            .preview-note {{
                background: #e8f4fd;
                border: 1px solid #bee5eb;
                padding: 12px;
                margin: 20px 0;
                font-size: 9pt;
                color: #0c5460;
                text-align: center;
                border-radius: 4px;
            }}
            .content-block {{
                margin: 10px 0;
            }}
            .figure-caption {{
                font-size: 9pt;
                text-align: center;
                margin: 10px 0;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="preview-note">
            📄 IEEE Live Preview - Downloads provide full formatting with exact IEEE compliance
        </div>
        
        <div class="ieee-title">{title}</div>
        <div class="ieee-authors">{authors_html}</div>
    """
    
    # Add abstract
    if abstract:
        html += f"""
        <div class="ieee-section">
            <span class="ieee-abstract-title">Abstract—</span>{abstract}
        </div>
        """
    
    # Add keywords
    if keywords:
        html += f"""
        <div class="ieee-section">
            <span class="ieee-keywords-title">Index Terms—</span>{keywords}
        </div>
        """
    
    # Add sections with content blocks
    for i, section in enumerate(sections, 1):
        section_title = sanitize_text(section.get('title', ''))
        if section_title:
            html += f"""
            <div class="ieee-heading">{i}. {section_title}</div>
            """
            
            # Process content blocks within the section
            content_blocks = section.get('contentBlocks', [])
            for block in content_blocks:
                block_type = block.get('type', 'text')
                block_content = sanitize_text(block.get('content', ''))
                
                if block_type == 'text' and block_content:
                    html += f'<div class="content-block">{block_content}</div>'
                elif block_type == 'figure' and block_content:
                    html += f'<div class="content-block figure-caption">Fig. {i}. {block_content}</div>'
                elif block_type == 'equation' and block_content:
                    html += f'<div class="content-block" style="text-align: center; margin: 15px 0;">{block_content}</div>'
    
    # Add references
    if references:
        html += '<div class="ieee-heading">References</div>'
        for i, ref in enumerate(references, 1):
            ref_text = sanitize_text(ref.get('text', ''))
            if ref_text:
                html += f'<div class="ieee-reference">[{i}] {ref_text}</div>'
    
    html += """
        <div class="preview-note">
            ✨ Complete IEEE formatting with proper typography, spacing, and layout available via Download buttons
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """Main function for command line execution."""
    try:
        # Read JSON data from stdin
        input_data = sys.stdin.read()
        form_data = json.loads(input_data)
        
        # Generate IEEE document
        doc_data = generate_ieee_document(form_data)
        
        # Write binary data to stdout
        sys.stdout.buffer.write(doc_data)
        
    except Exception as e:
        import traceback
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()