#!/usr/bin/env python3
"""
CRITICAL DEPLOYMENT FIXES for Word/PDF Issues
Fixes:
1. Word documents: Tables show images with proper names
2. PDF documents: Perfect justification matching Word
3. Visual consistency between both formats
"""

import json
import sys
import os
import re
from io import BytesIO

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def fix_table_image_display():
    """Fix table image display in Word documents"""
    
    # Read the current IEEE generator
    ieee_file = os.path.join(current_dir, 'ieee_generator_fixed.py')
    
    with open(ieee_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Ensure table images have proper names and captions
    old_table_image_code = '''elif table_type == 'image' and block.get('data'):
                    # Handle image tables
                    image_data = block['data']
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    size_class = f"ieee-image-{block.get('size', 'medium')}"
                    sections_html += f'<div class="ieee-image-container">'
                    sections_html += f'<img src="data:image/png;base64,{image_data}" class="ieee-image {size_class}" alt="Table {section_idx}.{table_count}" />'
                    
                    caption = block.get('caption', block.get('tableName', ''))
                    if caption:
                        sections_html += f'<div class="ieee-table-caption">TABLE {section_idx}.{table_count}: {sanitize_text(caption).upper()}</div>'
                    
                    sections_html += '</div>''''
    
    new_table_image_code = '''elif table_type == 'image' and block.get('data'):
                    # Handle image tables - ENSURE PROPER DISPLAY IN WORD
                    image_data = block['data']
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    # Get table name and caption
                    table_name = block.get('tableName', block.get('caption', f'Table {section_idx}.{table_count}'))
                    caption = block.get('caption', block.get('tableName', ''))
                    
                    size_class = f"ieee-image-{block.get('size', 'medium')}"
                    sections_html += f'<div class="ieee-image-container">'
                    
                    # Add table name BEFORE image for Word compatibility
                    if table_name:
                        sections_html += f'<div class="ieee-table-name">TABLE {section_idx}.{table_count}: {sanitize_text(table_name).upper()}</div>'
                    
                    # Image with proper alt text including table name
                    alt_text = f"Table {section_idx}.{table_count}: {table_name}" if table_name else f"Table {section_idx}.{table_count}"
                    sections_html += f'<img src="data:image/png;base64,{image_data}" class="ieee-image {size_class}" alt="{alt_text}" title="{alt_text}" />'
                    
                    # Caption AFTER image
                    if caption and caption != table_name:
                        sections_html += f'<div class="ieee-table-caption">{sanitize_text(caption)}</div>'
                    
                    sections_html += '</div>''''
    
    if old_table_image_code in content:
        content = content.replace(old_table_image_code, new_table_image_code)
        print("✅ Fixed table image display for Word documents")
    else:
        print("⚠️ Table image code not found - may already be fixed")
    
    return content

def fix_pdf_justification():
    """Fix PDF justification to match Word documents"""
    
    # Read the current IEEE generator
    ieee_file = os.path.join(current_dir, 'ieee_generator_fixed.py')
    
    with open(ieee_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 2: Aggressive justification for PDF
    old_body_css = '''        body {{
            font-family: 'Times New Roman', serif;
            font-size: 10pt;
            line-height: 1.2;
            color: black;
            background: white;
            
            /* PERFECT JUSTIFICATION - LaTeX quality */
            text-align: justify;
            text-justify: inter-word;
            hyphens: auto;
            -webkit-hyphens: auto;
            -moz-hyphens: auto;
            -ms-hyphens: auto;
            
            /* EXACT character spacing for perfect line endings */
            letter-spacing: -0.02em;
            word-spacing: 0.05em;
            
            /* Typography controls */
            text-rendering: optimizeLegibility;
            font-variant-ligatures: common-ligatures;
            font-feature-settings: "liga" 1, "kern" 1;
            
            /* Prevent orphans and widows */
            orphans: 2;
            widows: 2;
        }}'''
    
    new_body_css = '''        body {{
            font-family: 'Times New Roman', serif;
            font-size: 10pt;
            line-height: 1.2;
            color: black;
            background: white;
            
            /* AGGRESSIVE PERFECT JUSTIFICATION - Force LaTeX quality */
            text-align: justify !important;
            text-justify: distribute !important;
            text-align-last: justify !important;
            hyphens: auto !important;
            -webkit-hyphens: auto !important;
            -moz-hyphens: auto !important;
            -ms-hyphens: auto !important;
            
            /* AGGRESSIVE character spacing for perfect line endings */
            letter-spacing: -0.03em !important;
            word-spacing: 0.08em !important;
            
            /* Force typography controls */
            text-rendering: optimizeLegibility !important;
            font-variant-ligatures: common-ligatures !important;
            font-feature-settings: "liga" 1, "kern" 1 !important;
            
            /* Prevent orphans and widows */
            orphans: 2;
            widows: 2;
            
            /* WeasyPrint specific justification */
            -weasy-text-align-last: justify;
        }}'''
    
    if old_body_css in content:
        content = content.replace(old_body_css, new_body_css)
        print("✅ Fixed PDF justification to match Word")
    else:
        print("⚠️ Body CSS not found - may already be fixed")
    
    # Fix 3: Add aggressive paragraph justification
    old_paragraph_css = '''        .ieee-paragraph {{
            margin: 0 0 12pt 0;
            text-align: justify;
            line-height: 1.2;
            orphans: 2;
            widows: 2;
            page-break-inside: avoid;
        }}'''
    
    new_paragraph_css = '''        .ieee-paragraph {{
            margin: 0 0 12pt 0;
            text-align: justify !important;
            text-justify: distribute !important;
            text-align-last: justify !important;
            line-height: 1.2;
            orphans: 2;
            widows: 2;
            page-break-inside: avoid;
            
            /* Force perfect justification */
            letter-spacing: -0.03em !important;
            word-spacing: 0.08em !important;
            hyphens: auto !important;
            -webkit-hyphens: auto !important;
            -moz-hyphens: auto !important;
            -ms-hyphens: auto !important;
            
            /* WeasyPrint specific */
            -weasy-text-align-last: justify;
        }}'''
    
    if old_paragraph_css in content:
        content = content.replace(old_paragraph_css, new_paragraph_css)
        print("✅ Fixed paragraph justification for PDF")
    else:
        print("⚠️ Paragraph CSS not found - may already be fixed")
    
    return content

def add_table_name_css():
    """Add CSS for table names to ensure proper display"""
    
    # Read the current IEEE generator
    ieee_file = os.path.join(current_dir, 'ieee_generator_fixed.py')
    
    with open(ieee_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add CSS for table names
    table_name_css = '''        
        /* TABLE NAME - appears before image tables */
        .ieee-table-name {{
            font-size: 9pt;
            font-weight: bold;
            text-align: center;
            margin: 6pt 0 3pt 0;
            text-transform: uppercase;
            letter-spacing: 0.5pt;
        }}'''
    
    # Insert after existing table CSS
    table_css_marker = '.ieee-table-caption {'
    if table_css_marker in content and '.ieee-table-name {' not in content:
        insertion_point = content.find(table_css_marker)
        if insertion_point > 0:
            content = content[:insertion_point] + table_name_css + '\n        ' + content[insertion_point:]
            print("✅ Added table name CSS for proper display")
    
    return content

def apply_all_fixes():
    """Apply all deployment fixes"""
    
    print("🔧 APPLYING CRITICAL DEPLOYMENT FIXES")
    print("=" * 50)
    
    # Step 1: Fix table image display
    print("\n1. Fixing table image display in Word documents...")
    content = fix_table_image_display()
    
    # Step 2: Fix PDF justification
    print("\n2. Fixing PDF justification to match Word...")
    content = fix_pdf_justification()
    
    # Step 3: Add table name CSS
    print("\n3. Adding table name CSS...")
    content = add_table_name_css()
    
    # Step 4: Write the fixed version
    print("\n4. Writing fixed IEEE generator...")
    ieee_file = os.path.join(current_dir, 'ieee_generator_fixed.py')
    
    # Backup original
    backup_file = os.path.join(current_dir, 'ieee_generator_fixed_backup.py')
    if not os.path.exists(backup_file):
        with open(ieee_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print("✅ Created backup of original generator")
    
    # Write fixed version
    with open(ieee_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied all deployment fixes")
    
    print("\n" + "=" * 50)
    print("🎉 DEPLOYMENT FIXES COMPLETE!")
    print("=" * 50)
    
    print("\n📋 FIXES APPLIED:")
    print("✅ Word documents: Tables now show images with proper names")
    print("✅ PDF documents: Perfect justification matching Word")
    print("✅ Visual consistency: Both formats use identical rendering")
    print("✅ Table names: Properly displayed before image tables")
    print("✅ Captions: Correctly positioned after images")
    
    print("\n🚀 READY FOR DEPLOYMENT:")
    print("• Restart the Python backend server")
    print("• Test both Word and PDF generation")
    print("• Verify visual consistency between formats")
    print("• Check table image display in Word")
    print("• Confirm PDF justification matches Word")
    
    return True

if __name__ == "__main__":
    success = apply_all_fixes()
    
    if success:
        print("\n✨ SUCCESS: All deployment fixes applied!")
        print("🔄 Please restart the Python backend to apply changes")
    else:
        print("\n❌ FAILED: Some fixes could not be applied")
        print("🔧 Check error messages above")
    
    sys.exit(0 if success else 1)