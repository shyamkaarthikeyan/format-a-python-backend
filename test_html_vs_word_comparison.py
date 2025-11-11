#!/usr/bin/env python3
"""
Test script to compare HTML preview vs Word document output for tables.
This will help identify why tables show in UI preview but not in Word document.
"""

import base64
import json
import sys
from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def create_simple_table_test():
    """Create simple test data with one interactive table."""
    
    test_data = {
        "title": "HTML vs Word Table Comparison Test",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing table visibility in HTML preview vs Word document.",
        "keywords": "tables, html, word, comparison",
        "sections": [
            {
                "title": "Table Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This text should appear before the table."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Comparison Test Table",
                        "caption": "Simple Table for HTML vs Word Comparison",
                        "headers": ["Column A", "Column B", "Column C"],
                        "tableData": [
                            ["Data 1A", "Data 1B", "Data 1C"],
                            ["Data 2A", "Data 2B", "Data 2C"],
                            ["Data 3A", "Data 3B", "Data 3C"]
                        ],
                        "rows": 3,
                        "columns": 3
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the table."
                    }
                ]
            }
        ],
        "references": []
    }
    
    return test_data

def analyze_html_table_rendering(html):
    """Analyze how tables are rendered in HTML."""
    print("=== HTML TABLE ANALYSIS ===")
    
    # Count table elements
    table_containers = html.count('<div class="ieee-table-container">')
    tables = html.count('<table class="ieee-table">')
    table_headers = html.count('<th class="ieee-table-header">')
    table_cells = html.count('<td class="ieee-table-cell">')
    table_captions = html.count('ieee-table-caption')
    
    print(f"📊 HTML Table Elements:")
    print(f"  • Table containers: {table_containers}")
    print(f"  • Tables: {tables}")
    print(f"  • Table headers: {table_headers}")
    print(f"  • Table cells: {table_cells}")
    print(f"  • Table captions: {table_captions}")
    
    # Extract table HTML for inspection
    if '<table class="ieee-table">' in html:
        start_idx = html.find('<div class="ieee-table-container">')
        end_idx = html.find('</div>', start_idx) + 6
        table_html = html[start_idx:end_idx]
        
        print(f"\n📋 Sample Table HTML:")
        print("=" * 50)
        print(table_html[:500] + "..." if len(table_html) > 500 else table_html)
        print("=" * 50)
        
        return True
    else:
        print("❌ No table found in HTML!")
        return False

def analyze_word_table_generation(test_data):
    """Analyze how tables are processed for Word document."""
    print("\n=== WORD TABLE ANALYSIS ===")
    
    # Check the data structure that goes to Word generation
    for section_idx, section in enumerate(test_data['sections']):
        print(f"\nSection {section_idx + 1}: {section['title']}")
        
        for block_idx, block in enumerate(section['contentBlocks']):
            if block['type'] == 'table':
                print(f"  📋 Table Block {block_idx + 1}:")
                print(f"    • Type: {block['type']}")
                print(f"    • Table Type: {block.get('tableType', 'unknown')}")
                print(f"    • Table Name: {block.get('tableName', 'No name')}")
                print(f"    • Caption: {block.get('caption', 'No caption')}")
                print(f"    • Headers: {block.get('headers', [])}")
                print(f"    • Rows: {block.get('rows', 0)}")
                print(f"    • Columns: {block.get('columns', 0)}")
                print(f"    • Data rows: {len(block.get('tableData', []))}")
                
                # Check if data structure is complete
                headers = block.get('headers', [])
                table_data = block.get('tableData', [])
                
                if headers and table_data:
                    print(f"    ✅ Complete table data structure")
                    print(f"    • Sample header: {headers[0] if headers else 'None'}")
                    print(f"    • Sample data: {table_data[0] if table_data else 'None'}")
                else:
                    print(f"    ❌ Incomplete table data structure")
                    print(f"    • Headers missing: {not headers}")
                    print(f"    • Data missing: {not table_data}")

def main():
    """Run the HTML vs Word comparison test."""
    print("=== HTML vs WORD TABLE COMPARISON TEST ===")
    print("Comparing table rendering in HTML preview vs Word document")
    
    test_data = create_simple_table_test()
    
    print("\n=== STEP 1: GENERATE HTML PREVIEW ===")
    try:
        # Generate HTML preview (same as UI preview)
        model = build_document_model(test_data)
        html = render_to_html(model)
        
        print(f"✅ HTML generated: {len(html)} characters")
        
        # Save HTML for inspection
        with open("test_html_preview.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("💾 HTML saved as: test_html_preview.html")
        
        # Analyze HTML table rendering
        html_has_tables = analyze_html_table_rendering(html)
        
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        return 1
    
    print("\n=== STEP 2: ANALYZE WORD DATA STRUCTURE ===")
    analyze_word_table_generation(test_data)
    
    print("\n=== STEP 3: GENERATE WORD DOCUMENT ===")
    try:
        # Generate Word document (same backend function)
        doc_bytes = generate_ieee_document(test_data)
        
        if not doc_bytes or len(doc_bytes) == 0:
            print("❌ Error: Generated Word document is empty")
            return 1
        
        output_file = "test_html_vs_word_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Word document generated: {output_file}")
        print(f"   File size: {len(doc_bytes)} bytes")
        
    except Exception as e:
        print(f"❌ Word generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n=== COMPARISON RESULTS ===")
    if html_has_tables:
        print("✅ HTML Preview: Tables rendered correctly with borders")
        print("📋 Expected in HTML: <table class=\"ieee-table\"> with headers and data")
    else:
        print("❌ HTML Preview: No tables found")
    
    print("📄 Word Document: Check the generated .docx file")
    print("🔍 Manual Verification Required:")
    print("   1. Open test_html_preview.html in browser")
    print("   2. Open test_html_vs_word_output.docx in Word")
    print("   3. Compare table visibility and formatting")
    
    print("\n=== DEBUGGING QUESTIONS ===")
    print("❓ Does the HTML preview show the table correctly?")
    print("❓ Does the Word document show the table correctly?")
    print("❓ Are the table borders visible in both?")
    print("❓ Is the table data identical in both?")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())