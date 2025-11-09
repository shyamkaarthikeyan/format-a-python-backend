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

# IEEE formatting configuration - EXACT MATCH TO PDF FORMATTING
IEEE_CONFIG = {
    'font_name': 'Times New Roman',
    'font_size_title': Pt(24),        # PDF: 24pt bold centered title
    'font_size_author': Pt(10),       # PDF: 10pt author names
    'font_size_body': Pt(10),         # PDF: 10pt body text in 2-column
    'font_size_abstract': Pt(9),      # PDF: 9pt abstract and keywords
    'font_size_email': Pt(9),         # PDF: 9pt email addresses
    'margin_left': Inches(0.75),      # PDF: 54pt = 0.75 inch margins
    'margin_right': Inches(0.75),
    'margin_top': Inches(0.75),
    'margin_bottom': Inches(0.75),
    'column_count_body': 2,           # PDF: 2-column layout for body
    'column_spacing': Inches(0.25),   # PDF: 18pt = 0.25 inch gap between columns
    'column_width': Inches(3.375),    # PDF: calculated column width
    'line_spacing_single': Pt(12),    # PDF: single line spacing
    'line_spacing_body': Pt(13),      # PDF: body text line spacing
    'spacing_after_title': Pt(12),    # PDF: spacing after title
    'spacing_after_authors': Pt(10),  # PDF: spacing after authors
    'spacing_after_abstract': Pt(6),  # PDF: spacing after abstract
    'spacing_after_keywords': Pt(12), # PDF: spacing after keywords
}

def set_document_defaults(doc):
    """Set document-wide defaults to minimize unwanted spacing - EXACT same as test.py."""
    styles = doc.styles

    # Modify Normal style - EXACT same as test.py
    if 'Normal' in styles:
        normal = styles['Normal']
        normal.paragraph_format.space_before = Pt(0)
        normal.paragraph_format.space_after = Pt(12)
        normal.paragraph_format.line_spacing = IEEE_CONFIG['line_spacing_body']
        normal.paragraph_format.line_spacing_rule = 0  # Exact spacing
        normal.paragraph_format.widow_control = False
        normal.font.name = IEEE_CONFIG['font_name']
        normal.font.size = IEEE_CONFIG['font_size_body']
        # Add better spacing control
        normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal.paragraph_format.first_line_indent = Pt(0)

    # Modify Heading 1 style - IEEE SECTION HEADINGS (BOLD, CENTERED)
    if 'Heading 1' in styles:
        heading1 = styles['Heading 1']
        heading1.base_style = styles['Normal']
        heading1.paragraph_format.space_before = Pt(12)
        heading1.paragraph_format.space_after = Pt(6)
        heading1.paragraph_format.line_spacing = Pt(10)
        heading1.paragraph_format.line_spacing_rule = 0
        heading1.paragraph_format.keep_with_next = False
        heading1.paragraph_format.page_break_before = False
        heading1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading1.font.name = IEEE_CONFIG['font_name']
        heading1.font.size = IEEE_CONFIG['font_size_body']
        heading1.font.bold = True  # IEEE standard: Section headings are BOLD

    # Modify Heading 2 style for subsections - IEEE SUBSECTION HEADINGS (BOLD, LEFT)
    if 'Heading 2' in styles:
        heading2 = styles['Heading 2']
        heading2.base_style = styles['Normal']
        heading2.paragraph_format.space_before = Pt(6)
        heading2.paragraph_format.space_after = Pt(3)
        heading2.paragraph_format.line_spacing = Pt(10)
        heading2.paragraph_format.line_spacing_rule = 0
        heading2.paragraph_format.keep_with_next = False
        heading2.paragraph_format.page_break_before = False
        heading2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        heading2.font.name = IEEE_CONFIG['font_name']
        heading2.font.size = IEEE_CONFIG['font_size_body']
        heading2.font.bold = True  # IEEE standard: Subsection headings are BOLD

def add_title(doc, title):
    """Add the paper title - EXACT MATCH TO PDF: 24pt bold centered Times New Roman."""
    para = doc.add_paragraph()
    run = para.add_run(sanitize_text(title))
    run.bold = True
    run.font.name = IEEE_CONFIG['font_name']
    run.font.size = IEEE_CONFIG['font_size_title']  # 24pt exactly like PDF
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(0)
    para.paragraph_format.space_after = IEEE_CONFIG['spacing_after_title']  # 12pt like PDF

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
    """Add the abstract section - EXACT MATCH TO PDF: 9pt bold with Abstract— prefix."""
    if abstract:
        # Add abstract with bold title and content in same paragraph
        para = doc.add_paragraph()
        
        # Bold "Abstract—" title (EXACT MATCH TO PDF)
        title_run = para.add_run("Abstract—")
        title_run.bold = True  # PDF uses BOLD for Abstract—
        title_run.italic = False
        title_run.font.name = IEEE_CONFIG['font_name']
        title_run.font.size = IEEE_CONFIG['font_size_abstract']  # 9pt like PDF
        
        # Add abstract content immediately after on SAME LINE (BOLD like PDF)
        content_run = para.add_run(sanitize_text(abstract))
        content_run.bold = True  # PDF uses BOLD for abstract content
        content_run.italic = False
        content_run.font.name = IEEE_CONFIG['font_name']
        content_run.font.size = IEEE_CONFIG['font_size_abstract']  # 9pt like PDF
        
        # Apply PERFECT IEEE justification formatting for research paper quality
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after = IEEE_CONFIG['spacing_after_abstract']  # Standard IEEE spacing after abstract
        para.paragraph_format.line_spacing = IEEE_CONFIG['line_spacing_body']
        para.paragraph_format.line_spacing_rule = 0  # Exact spacing
        para.paragraph_format.widow_control = False
        para.paragraph_format.keep_with_next = False
        
        # Apply PERFECT justification with aggressive research paper quality settings
        apply_perfect_research_justification(para)

def add_keywords(doc, keywords):
    """Add the keywords section - EXACT MATCH TO PDF: 9pt bold with Keywords— prefix."""
    if keywords:
        # Add keywords with bold title and content in same paragraph
        para = doc.add_paragraph()
        
        # Bold "Keywords—" title (EXACT MATCH TO PDF)
        title_run = para.add_run("Keywords—")
        title_run.bold = True  # PDF uses BOLD for Keywords—
        title_run.italic = False
        title_run.font.name = IEEE_CONFIG['font_name']
        title_run.font.size = IEEE_CONFIG['font_size_abstract']  # 9pt like PDF
        
        # Add keywords content immediately after on SAME LINE (BOLD like PDF)
        content_run = para.add_run(sanitize_text(keywords))
        content_run.bold = True  # PDF uses BOLD for keywords content
        content_run.italic = False
        content_run.font.name = IEEE_CONFIG['font_name']
        content_run.font.size = IEEE_CONFIG['font_size_abstract']  # 9pt like PDF
        
        # Apply proper IEEE justification formatting
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after = Pt(12)  # Standard IEEE spacing after keywords
        para.paragraph_format.line_spacing = IEEE_CONFIG['line_spacing_body']
        para.paragraph_format.line_spacing_rule = 0  # Exact spacing
        para.paragraph_format.widow_control = False
        para.paragraph_format.keep_with_next = False
        
        # Apply comprehensive equal justification
        apply_equal_justification(para)

def add_justified_paragraph(doc, text, style_name='Normal', indent_left=None, indent_right=None, space_before=None, space_after=None):
    """Add a paragraph with professional justification settings for research paper quality."""
    para = doc.add_paragraph(sanitize_text(text))
    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Set paragraph formatting with proper line spacing for 10pt text
    para.paragraph_format.line_spacing = Pt(13.8)  # 1.38 * 10pt for proper line spacing
    para.paragraph_format.line_spacing_rule = 0  # Exact spacing
    para.paragraph_format.widow_control = True  # Enable widow control for better page breaks
    para.paragraph_format.keep_with_next = False
    para.paragraph_format.keep_together = False
    
    # Set spacing
    if space_before is not None:
        para.paragraph_format.space_before = space_before
    if space_after is not None:
        para.paragraph_format.space_after = space_after
    
    # Set indentation
    if indent_left is not None:
        para.paragraph_format.left_indent = indent_left
    if indent_right is not None:
        para.paragraph_format.right_indent = indent_right
    
    # Font formatting - no aggressive character spacing
    if para.runs:
        run = para.runs[0]
        run.font.name = IEEE_CONFIG['font_name']
        run.font.size = IEEE_CONFIG['font_size_body']
    
    # Apply professional justification
    apply_equal_justification(para)
    
    return para

def add_section(doc, section_data, section_idx, is_first_section=False):
    """Add a section with content blocks, subsections, and figures - EXACT same as test.py."""
    if section_data.get('title'):
        para = doc.add_heading(f"{section_idx}. {sanitize_text(section_data['title']).upper()}", level=1)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER  # Center section titles
        para.paragraph_format.page_break_before = False
        para.paragraph_format.space_before = IEEE_CONFIG['line_spacing']  # Exactly one line before heading
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.keep_with_next = False
        para.paragraph_format.keep_together = False
        para.paragraph_format.widow_control = False

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
            # Handle image blocks from React frontend
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
                img_count = sum(1 for b in content_blocks[:block_idx+1] if b.get('type') == 'image')
                caption = doc.add_paragraph(f"Fig. {section_idx}.{img_count}: {sanitize_text(block['caption'])}")
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption.paragraph_format.space_before = Pt(0)
                caption.paragraph_format.space_after = Pt(12)
                if caption.runs:
                    caption.runs[0].font.name = IEEE_CONFIG['font_name']
                    caption.runs[0].font.size = IEEE_CONFIG['font_size_caption']
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

def add_formatted_paragraph(doc, html_content, style_name='Normal', indent_left=None, indent_right=None, space_before=None, space_after=None):
    """Add a paragraph with HTML formatting support and perfect equal line length justification."""
    para = doc.add_paragraph(style=style_name)
    
    # Set spacing and indentation first
    if indent_left is not None:
        para.paragraph_format.left_indent = indent_left
    if indent_right is not None:
        para.paragraph_format.right_indent = indent_right
    if space_before is not None:
        para.paragraph_format.space_before = space_before
    if space_after is not None:
        para.paragraph_format.space_after = space_after
    
    # Parse HTML and apply formatting
    if html_content and '<' in html_content and '>' in html_content:
        # Content contains HTML tags - use parser
        parser = HTMLToWordParser(para)
        parser.feed(html_content)
        parser.close()  # Important: flush any remaining text
    else:
        # Plain text content from frontend forms
        run = para.add_run(html_content or "")
        run.font.name = IEEE_CONFIG['font_name']
        run.font.size = IEEE_CONFIG['font_size_body']
    
    # Set proper line spacing for 10pt text
    para.paragraph_format.line_spacing = Pt(13.8)  # 1.38 * 10pt for proper spacing
    para.paragraph_format.line_spacing_rule = 0  # Exact spacing
    para.paragraph_format.widow_control = True  # Enable widow control
    para.paragraph_format.keep_with_next = False
    para.paragraph_format.keep_together = False
    
    # Apply comprehensive equal line length justification - this is the key fix
    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY  # Set basic justification first
    apply_equal_justification(para)  # Then apply advanced equal line length controls
    
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
            if ref.get('text'):
                # Sanitize the reference text to prevent Unicode encoding errors
                ref_text = sanitize_text(ref['text'])
                para = doc.add_paragraph(f"[{idx}] {ref_text}")
                
                # Set formatting first
                para.paragraph_format.left_indent = IEEE_CONFIG['column_indent'] + Inches(0.25)
                para.paragraph_format.right_indent = IEEE_CONFIG['column_indent']
                para.paragraph_format.first_line_indent = Inches(-0.25)
                para.paragraph_format.line_spacing = Pt(13.8)  # Proper line spacing
                para.paragraph_format.line_spacing_rule = 0
                para.paragraph_format.space_before = Pt(3)
                para.paragraph_format.space_after = Pt(12)
                para.paragraph_format.widow_control = True  # Enable widow control
                para.paragraph_format.keep_with_next = False
                para.paragraph_format.keep_together = True
                
                # Set font
                if para.runs:
                    para.runs[0].font.name = IEEE_CONFIG['font_name']
                    para.runs[0].font.size = IEEE_CONFIG['font_size_body']
                
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
    """Generate an IEEE-formatted Word document with proper layout."""
    doc = Document()
    
    set_document_defaults(doc)
    
    # Configure first section for single-column title and authors
    section = doc.sections[0]
    section.left_margin = IEEE_CONFIG['margin_left']
    section.right_margin = IEEE_CONFIG['margin_right']
    section.top_margin = IEEE_CONFIG['margin_top']
    section.bottom_margin = IEEE_CONFIG['margin_bottom']
    
    # Add title and authors in single-column layout (IEEE standard)
    add_title(doc, form_data.get('title', ''))
    add_authors(doc, form_data.get('authors', []))

    # Add section break for two-column layout (for body content)
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    new_section.start_type = WD_SECTION.CONTINUOUS
    new_section.left_margin = IEEE_CONFIG['margin_left']
    new_section.right_margin = IEEE_CONFIG['margin_right']
    new_section.top_margin = IEEE_CONFIG['margin_top']
    new_section.bottom_margin = IEEE_CONFIG['margin_bottom']
    
    # Configure two-column layout for body content
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')
    if cols:
        cols = cols[0]
    else:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    
    cols.set(qn('w:num'), str(IEEE_CONFIG['column_count_body']))
    cols.set(qn('w:sep'), '0')
    cols.set(qn('w:space'), str(int(Inches(0.25).pt * 20)))  # Convert to twips (0.25 inch gap)
    cols.set(qn('w:equalWidth'), '1')
    
    # Add column definitions with proper width
    for i in range(IEEE_CONFIG['column_count_body']):
        col = OxmlElement('w:col')
        col.set(qn('w:w'), str(int(Inches(3.375).pt * 20)))  # Convert to twips (3.375 inch width)
        cols.append(col)
    
    # Prevent column balancing for stable layout
    no_balance = OxmlElement('w:noBalance')
    no_balance.set(qn('w:val'), '1')
    sectPr.append(no_balance)
    
    # Now add abstract and keywords in the properly configured 2-column layout
    add_abstract(doc, form_data.get('abstract', ''))
    add_keywords(doc, form_data.get('keywords', ''))
    
    for idx, section_data in enumerate(form_data.get('sections', []), 1):
        add_section(doc, section_data, idx, is_first_section=(idx == 1))
    
    add_references(doc, form_data.get('references', []))
    
    enable_auto_hyphenation(doc)
    set_compatibility_options(doc)
    
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