#!/usr/bin/env python3
"""
Test script to simulate the exact UI flow for table creation
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_ui_table_flow():
    """Test the exact table flow from the UI"""
    
    # Simulate data that would come from the React frontend
    # This matches the structure from table-form.tsx and table-block-editor.tsx
    ui_data = {
        "title": "UI Table Flow Test",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing table visibility from UI flow.",
        "keywords": "tables, UI, testing",
        "sections": [
            {
                "id": "section_1",
                "title": "Test Section with Tables",
                "contentBlocks": [
                    {
                        "id": "block_1",
                        "type": "text",
                        "content": "This is text before the table."
                    },
                    {
                        "id": "block_2", 
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Sample Data Table",
                        "caption": "Test table from UI",
                        "headers": ["Name", "Age", "City"],
                        "tableData": [
                            ["John Doe", "25", "New York"],
                            ["Jane Smith", "30", "Los Angeles"],
                            ["Bob Johnson", "35", "Chicago"]
                        ],
                        "order": 1
                    },
                    {
                        "id": "block_3",
                        "type": "text", 
                        "content": "This is text after the table."
                    },
                    {
                        "id": "block_4",
                        "type": "table",
                        "tableType": "interactive", 
                        "tableName": "Performance Metrics",
                        "caption": "Performance comparison table",
                        "headers": ["Method", "Accuracy", "Speed"],
                        "tableData": [
                            ["Method A", "95%", "Fast"],
                            ["Method B", "92%", "Medium"],
                            ["Method C", "98%", "Slow"]
                        ],
                        "order": 2
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("🔍 Testing UI table flow with multiple tables...", file=sys.stderr)
    print(f"📊 Number of content blocks: {len(ui_data['sections'][0]['contentBlocks'])}", file=sys.stderr)
    
    # Count tables
    table_blocks = [block for block in ui_data['sections'][0]['contentBlocks'] if block.get('type') == 'table']
    print(f"📊 Number of table blocks: {len(table_blocks)}", file=sys.stderr)
    
    for i, table_block in enumerate(table_blocks, 1):
        print(f"📊 Table {i}: {table_block.get('tableName', 'Unnamed')}", file=sys.stderr)
        print(f"   Headers: {table_block.get('headers', [])}", file=sys.stderr)
        print(f"   Rows: {len(table_block.get('tableData', []))}", file=sys.stderr)
    
    try:
        # Generate the document
        docx_bytes = generate_ieee_document(ui_data)
        
        # Save to file for inspection
        output_file = "test_ui_table_flow_output.docx"
        with open(output_file, "wb") as f:
            f.write(docx_bytes)
        
        print(f"✅ Document generated successfully: {output_file}", file=sys.stderr)
        print(f"📄 Document size: {len(docx_bytes)} bytes", file=sys.stderr)
        print("🔍 Please open the document in Word to check if tables are visible", file=sys.stderr)
        print("📋 Expected: 2 tables with captions should be visible in the document", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating document: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_ui_table_flow()
    sys.exit(0 if success else 1)