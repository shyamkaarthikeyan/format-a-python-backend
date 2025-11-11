#!/usr/bin/env python3
"""
Debug script to test table visibility in Word documents
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_table_visibility():
    """Test table visibility with different table configurations"""
    
    # Test data with interactive table
    test_data = {
        "title": "Table Visibility Test Document",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "This document tests table visibility in Word documents.",
        "keywords": "tables, visibility, testing",
        "sections": [
            {
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section contains a test table to verify visibility."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Table",
                        "caption": "Sample Data Table",
                        "headers": ["Column 1", "Column 2", "Column 3"],
                        "tableData": [
                            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
                            ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"]
                        ]
                    },
                    {
                        "type": "text",
                        "content": "Text after the table to verify proper spacing."
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("🔍 Testing table visibility in Word document...", file=sys.stderr)
    print(f"📊 Table data: {test_data['sections'][0]['contentBlocks'][1]}", file=sys.stderr)
    
    try:
        # Generate the document
        docx_bytes = generate_ieee_document(test_data)
        
        # Save to file for inspection
        output_file = "debug_table_visibility_test.docx"
        with open(output_file, "wb") as f:
            f.write(docx_bytes)
        
        print(f"✅ Document generated successfully: {output_file}", file=sys.stderr)
        print(f"📄 Document size: {len(docx_bytes)} bytes", file=sys.stderr)
        print("🔍 Please open the document in Word to check if the table is visible", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating document: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_table_visibility()
    sys.exit(0 if success else 1)