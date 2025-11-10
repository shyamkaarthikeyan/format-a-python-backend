"""
Critical Fixes Patch for IEEE Generator
Fixes: 1) PDF justification, 2) DOCX image positioning, 3) Table name duplication
"""

import re

def apply_critical_fixes():
    """Apply critical fixes to the IEEE generator."""
    
    # Fix 1: Improve PDF justification CSS
    pdf_justification_css = """
    /* ENHANCED PDF JUSTIFICATION - Force perfect text alignment */
    body, p, .ieee-paragraph, .ieee-abstract, .ieee-keywords, .ieee-section {
        text-align: justify !important;
        text-justify: inter-word !important;
        text-align-last: justify !important;
        hyphens: auto !important;
        -webkit-hyphens: auto !important;
        -moz-hyphens: auto !important;
        -ms-hyphens: auto !important;
        word-spacing: 0.1em !important;
        letter-spacing: 0.02em !important;
        line-height: 1.2 !important;
    }
    
    /* WeasyPrint specific justification */
    body, p, .ieee-paragraph {
        -weasy-text-align-last: justify !important;
        -weasy-hyphens: auto !important;
    }
    
    /* Prevent text from being left-aligned */
    * {
        text-align: justify !important;
    }
    
    .ieee-title, .ieee-authors, .ieee-section-title, .ieee-table-caption, .ieee-figure-caption {
        text-align: center !important;
    }
    """
    
    # Fix 2: DOCX image positioning improvements
    docx_image_fix = """
    # Add proper spacing before and after images to prevent text overlap
    def add_image_with_spacing(doc, image_data, width, caption=None):
        # Add spacing before image
        spacing_before = doc.add_paragraph()
        spacing_before.paragraph_format.space_before = Pt(12)
        spacing_before.paragraph_format.space_after = Pt(0)
        
        # Add image paragraph
        image_para = doc.add_paragraph()
        image_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        image_para.paragraph_format.space_before = Pt(6)
        image_para.paragraph_format.space_after = Pt(6)
        
        # Add image
        run = image_para.add_run()
        picture = run.add_picture(image_stream, width=width)
        
        # Add caption if provided
        if caption:
            caption_para = doc.add_paragraph(caption)
            caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            caption_para.paragraph_format.space_before = Pt(3)
            caption_para.paragraph_format.space_after = Pt(12)
        
        # Add spacing after image
        spacing_after = doc.add_paragraph()
        spacing_after.paragraph_format.space_before = Pt(0)
        spacing_after.paragraph_format.space_after = Pt(12)
    """
    
    # Fix 3: Table name deduplication logic
    table_name_fix = """
    def get_clean_table_caption(table_data):
        caption = table_data.get('caption', '').strip()
        table_name = table_data.get('tableName', '').strip()
        
        # If both exist, check for duplication
        if caption and table_name:
            # Remove common duplications
            if table_name.lower() in caption.lower():
                return caption
            elif caption.lower() in table_name.lower():
                return table_name
            elif caption.lower() == table_name.lower():
                return caption
            else:
                # They're different, prefer caption
                return caption
        
        # Use whichever exists
        return caption or table_name or 'Data Table'
    """
    
    return {
        'pdf_css': pdf_justification_css,
        'docx_image': docx_image_fix,
        'table_name': table_name_fix
    }

if __name__ == "__main__":
    fixes = apply_critical_fixes()
    print("Critical fixes generated:")
    print("1. PDF Justification CSS")
    print("2. DOCX Image Positioning")
    print("3. Table Name Deduplication")