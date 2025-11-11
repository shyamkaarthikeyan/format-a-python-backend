#!/usr/bin/env python3
"""
Test script to verify table and image visibility fixes.
"""

import base64
import json
import sys
from ieee_generator_fixed import generate_ieee_document

def create_test_data():
    """Create test data with tables and images to verify visibility fixes."""
    
    # Create a simple base64 image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    test_data = {
        "title": "Visibility Fixes Test: Tables and Images",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing table and image visibility fixes in IEEE document generation.",
        "keywords": "tables, images, visibility, fixes",
        "sections": [
            {
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This text should appear before the table."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "caption": "Test Table with Visible Borders",
                        "headers": ["Header 1", "Header 2", "Header 3"],
                        "tableData": [
                            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
                            ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"]
                        ]
                    },
                    {
                        "type": "text",
                        "content": "This text should appear between the table and image."
                    },
                    {
                        "type": "image",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "caption": "Test Image with Full Visibility",
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
    """Run the visibility fixes test."""
    print("=== VISIBILITY FIXES TEST ===")
    print("Testing table and image visibility fixes...")
    
    test_data = create_test_data()
    
    print("\nTest structure:")
    print(f"- Title: {test_data['title']}")
    print(f"- Sections: {len(test_data['sections'])}")
    print(f"- Content blocks: {len(test_data['sections'][0]['contentBlocks'])}")
    
    for i, block in enumerate(test_data['sections'][0]['contentBlocks']):
        print(f"  Block {i+1}: {block['type']}")
        if block['type'] == 'table':
            print(f"    - Caption: {block.get('caption', 'No caption')}")
            print(f"    - Headers: {len(block.get('headers', []))} columns")
            print(f"    - Data rows: {len(block.get('tableData', []))}")
        elif block['type'] == 'image':
            print(f"    - Caption: {block.get('caption', 'No caption')}")
            print(f"    - Size: {block.get('size', 'unknown')}")
    
    print("\n=== Generating document ===")
    try:
        doc_bytes = generate_ieee_document(test_data)
        
        if not doc_bytes or len(doc_bytes) == 0:
            print("❌ Error: Generated document is empty")
            return 1
        
        output_file = "test_visibility_fixes_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Document generated: {output_file}")
        print(f"   File size: {len(doc_bytes)} bytes")
        
        print("\n=== Expected Results ===")
        print("✅ Table should appear immediately after 'TABLE 1.1: TEST TABLE WITH VISIBLE BORDERS'")
        print("✅ Table should have visible black borders around all cells")
        print("✅ Image should be fully visible after 'FIG. 1.1: TEST IMAGE WITH FULL VISIBILITY'")
        print("✅ Content should appear in correct order: text → table → text → image → text")
        print("✅ No manual layout adjustments should be needed in Word")
        
        print("\n=== Fixes Applied ===")
        print("1. Table Visibility: Placeholder tables created when data is missing")
        print("2. Table Borders: Explicit black borders added to all table cells")
        print("3. Image Visibility: Simplified layout without complex section breaks")
        print("4. Content Ordering: Streamlined processing logic")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())