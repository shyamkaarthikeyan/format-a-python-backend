#!/usr/bin/env python3
"""
Debug script to test table creation in the IEEE generator specifically.
This will help identify if the issue is in the IEEE generator or elsewhere.
"""

import sys
from ieee_generator_fixed import generate_ieee_document

def create_table_only_test():
    """Create test data with only a table to isolate the issue."""
    
    test_data = {
        "title": "Table Only Test",
        "authors": [
            {
                "id": "author_1",
                "name": "Table Test Author",
                "email": "table@test.com",
                "customFields": []
            }
        ],
        "abstract": "This document contains only a table to test table visibility.",
        "keywords": "table, test, debug",
        "sections": [
            {
                "id": "section_1",
                "title": "Table Test Section",
                "order": 1,
                "contentBlocks": [
                    {
                        "id": "block_1",
                        "type": "text",
                        "content": "This text comes before the table.",
                        "order": 0
                    },
                    {
                        "id": "block_2",
                        "type": "table",
                        "tableName": "Debug Table Name",
                        "caption": "Debug Table Caption",
                        "order": 1,
                        "tableType": "interactive",
                        "rows": 2,
                        "columns": 2,
                        "headers": ["Col A", "Col B"],
                        "tableData": [
                            ["Data A1", "Data B1"]
                        ]
                    },
                    {
                        "id": "block_3",
                        "type": "text",
                        "content": "This text comes after the table.",
                        "order": 2
                    }
                ],
                "subsections": []
            }
        ],
        "references": [],
        "figures": [],
        "tables": [],
        "settings": {
            "fontSize": "9.5pt",
            "columns": "double",
            "exportFormat": "docx",
            "includePageNumbers": True,
            "includeCopyright": True
        }
    }
    
    return test_data

def main():
    """Run the table-only test."""
    print("=== TABLE ONLY TEST ===")
    
    test_data = create_table_only_test()
    
    print("Test data structure:")
    table_block = test_data["sections"][0]["contentBlocks"][1]
    print(f"- Table Type: {table_block.get('tableType')}")
    print(f"- Headers: {table_block.get('headers')}")
    print(f"- Data: {table_block.get('tableData')}")
    print(f"- Rows x Cols: {table_block.get('rows')} x {table_block.get('columns')}")
    
    print("\nGenerating document with IEEE generator...")
    try:
        # Generate the document
        doc_bytes = generate_ieee_document(test_data)
        
        # Save to file
        output_file = "debug_table_data_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Document generated: {output_file}")
        print(f"📊 Document size: {len(doc_bytes)} bytes")
        
        print("\n=== EXPECTED IN DOCUMENT ===")
        print("1. Title: 'Table Only Test'")
        print("2. Author: Table Test Author")
        print("3. Abstract and keywords")
        print("4. Section 1: 'Table Test Section'")
        print("   a. Text: 'This text comes before the table.'")
        print("   b. TABLE 1.1: DEBUG TABLE CAPTION")
        print("   c. Actual table with:")
        print("      - Headers: Col A, Col B")
        print("      - Data row: Data A1, Data B1")
        print("   d. Text: 'This text comes after the table.'")
        
        print("\n=== CRITICAL CHECK ===")
        print("🔍 Open the document in Word and verify:")
        print("   ❓ Does TABLE 1.1 caption appear?")
        print("   ❓ Does the actual table appear immediately after the caption?")
        print("   ❓ Are the table borders visible?")
        print("   ❓ Is the table content (Col A, Col B, Data A1, Data B1) visible?")
        
        print("\n=== DEBUGGING INFO ===")
        print("If the table doesn't appear, the issue is in:")
        print("- add_ieee_table() function")
        print("- Table border generation")
        print("- Document structure in IEEE generator")
        print("- Two-column layout interference")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())