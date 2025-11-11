#!/usr/bin/env python3
"""
Debug script to identify why tables don't appear and images are half-invisible.
"""

import base64
import json
import sys
from ieee_generator_fixed import generate_ieee_document

def create_debug_data():
    """Create minimal test data to debug table and image issues."""
    
    # Create a simple base64 image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    test_data = {
        "title": "Debug Test: Table and Image Visibility",
        "authors": [
            {
                "name": "Debug Author",
                "affiliation": "Debug University",
                "email": "debug@example.com"
            }
        ],
        "abstract": "Debug test for table and image visibility issues.",
        "keywords": "debug, tables, images, visibility",
        "sections": [
            {
                "title": "Debug Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This text should appear first."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "caption": "Debug Table Caption",
                        "headers": ["Col1", "Col2"],
                        "tableData": [
                            ["Data1", "Data2"],
                            ["Data3", "Data4"]
                        ]
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the table."
                    },
                    {
                        "type": "image",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "caption": "Debug Image Caption",
                        "size": "medium"
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the image."
                    }
                ]
            }
        ],
        "references": []
    }
    
    return test_data

def main():
    """Run the debug test."""
    print("=== DEBUG: Table and Image Visibility Test ===")
    test_data = create_debug_data()
    
    print("\nTest data structure:")
    print(f"- Sections: {len(test_data['sections'])}")
    print(f"- Content blocks: {len(test_data['sections'][0]['contentBlocks'])}")
    
    for i, block in enumerate(test_data['sections'][0]['contentBlocks']):
        print(f"  Block {i}: {block['type']}")
        if block['type'] == 'table':
            print(f"    - Headers: {block.get('headers', [])}")
            print(f"    - Data rows: {len(block.get('tableData', []))}")
            print(f"    - Table type: {block.get('tableType', 'unknown')}")
        elif block['type'] == 'image':
            print(f"    - Has data: {bool(block.get('data'))}")
            print(f"    - Size: {block.get('size', 'unknown')}")
    
    print("\n=== Generating document ===")
    try:
        doc_bytes = generate_ieee_document(test_data)
        
        output_file = "debug_table_visibility_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Document generated: {output_file}")
        print("\n=== Expected in document ===")
        print("1. Text: 'This text should appear first.'")
        print("2. TABLE 1.1: DEBUG TABLE CAPTION")
        print("3. Actual table with headers [Col1, Col2] and 2 data rows")
        print("4. Text: 'This text should appear after the table.'")
        print("5. FIG. 1.1: DEBUG IMAGE CAPTION")
        print("6. Actual image (fully visible)")
        print("7. Text: 'This text should appear after the image.'")
        
        print("\n=== Check for issues ===")
        print("❓ Does the table appear after TABLE 1.1 caption?")
        print("❓ Is the image fully visible after FIG. 1.1 caption?")
        print("❓ Are all text blocks in the right order?")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())