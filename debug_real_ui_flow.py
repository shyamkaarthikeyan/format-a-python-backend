#!/usr/bin/env python3
"""
Debug script to test the EXACT real UI flow and check table content visibility
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_real_ui_flow():
    """Test with EXACT data structure from real UI"""
    
    # This is the EXACT structure that comes from the React frontend
    real_ui_data = {
        "title": "Real UI Flow Test - Table Content Visibility",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing table content visibility in Word documents.",
        "keywords": "tables, content, visibility, debugging",
        "sections": [
            {
                "id": "section_1",
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "id": "text_block_1",
                        "type": "text",
                        "content": "This text should appear before the table."
                    },
                    {
                        "id": "table_block_1",
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Sample Data Table",
                        "caption": "This is the table caption that shows",
                        "headers": ["Name", "Value", "Status"],
                        "tableData": [
                            ["Item 1", "100", "Active"],
                            ["Item 2", "200", "Inactive"],
                            ["Item 3", "300", "Pending"]
                        ]
                    },
                    {
                        "id": "text_block_2",
                        "type": "text",
                        "content": "This text should appear after the table."
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("🔍 Testing REAL UI flow - checking table content visibility...", file=sys.stderr)
    print(f"📊 Table data structure:", file=sys.stderr)
    table_block = real_ui_data['sections'][0]['contentBlocks'][1]
    print(f"   Type: {table_block['type']}", file=sys.stderr)
    print(f"   Table Type: {table_block['tableType']}", file=sys.stderr)
    print(f"   Table Name: {table_block['tableName']}", file=sys.stderr)
    print(f"   Caption: {table_block['caption']}", file=sys.stderr)
    print(f"   Headers: {table_block['headers']}", file=sys.stderr)
    print(f"   Data Rows: {len(table_block['tableData'])}", file=sys.stderr)
    for i, row in enumerate(table_block['tableData']):
        print(f"     Row {i+1}: {row}", file=sys.stderr)
    
    try:
        # Generate the document
        docx_bytes = generate_ieee_document(real_ui_data)
        
        # Save to file for inspection
        output_file = "debug_real_ui_flow_output.docx"
        with open(output_file, "wb") as f:
            f.write(docx_bytes)
        
        print(f"✅ Document generated: {output_file}", file=sys.stderr)
        print(f"📄 Document size: {len(docx_bytes)} bytes", file=sys.stderr)
        print("", file=sys.stderr)
        print("🔍 DEBUGGING CHECKLIST:", file=sys.stderr)
        print("1. Open the document in Microsoft Word", file=sys.stderr)
        print("2. Check if you see the table caption: 'This is the table caption that shows'", file=sys.stderr)
        print("3. Check if you see the table headers: Name, Value, Status", file=sys.stderr)
        print("4. Check if you see the table data rows:", file=sys.stderr)
        print("   - Item 1, 100, Active", file=sys.stderr)
        print("   - Item 2, 200, Inactive", file=sys.stderr)
        print("   - Item 3, 300, Pending", file=sys.stderr)
        print("", file=sys.stderr)
        print("❓ ISSUE: If you see the caption but NOT the table content, the problem is in table rendering.", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating document: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_real_ui_flow()
    sys.exit(0 if success else 1)