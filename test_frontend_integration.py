#!/usr/bin/env python3
"""
Test script that simulates the exact data structure sent from the frontend UI.
This will help identify where the table and image visibility issues occur.
"""

import base64
import json
import sys
from ieee_generator_fixed import generate_ieee_document

def create_frontend_simulation_data():
    """Create test data that exactly matches what the frontend UI sends."""
    
    # Create a simple base64 image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    # This exactly matches the data structure from StreamlinedSectionForm -> ContentBlock -> TableBlockEditor
    test_data = {
        "title": "Frontend Integration Test",
        "authors": [
            {
                "id": "author_1",
                "name": "Frontend Test Author",
                "department": "Computer Science",
                "organization": "Frontend University",
                "city": "Test City",
                "state": "Test State",
                "email": "frontend@test.com",
                "customFields": []
            }
        ],
        "abstract": "This document tests the exact frontend-to-backend integration for table and image visibility.",
        "keywords": "frontend, backend, integration, tables, images",
        "sections": [
            {
                "id": "section_1",
                "title": "Frontend Integration Test Section",
                "order": 1,
                "contentBlocks": [
                    {
                        "id": "block_1",
                        "type": "text",
                        "content": "This text block comes before the interactive table.",
                        "order": 0
                    },
                    {
                        "id": "block_2",
                        "type": "table",
                        "tableName": "Interactive Table from Frontend",
                        "caption": "Frontend Interactive Table Caption",
                        "order": 1,
                        # These fields come from TableBlockEditor
                        "tableType": "interactive",
                        "rows": 3,
                        "columns": 3,
                        "headers": ["Frontend Header 1", "Frontend Header 2", "Frontend Header 3"],
                        "tableData": [
                            ["Frontend Data 1,1", "Frontend Data 1,2", "Frontend Data 1,3"],
                            ["Frontend Data 2,1", "Frontend Data 2,2", "Frontend Data 2,3"]
                        ]
                    },
                    {
                        "id": "block_3",
                        "type": "text",
                        "content": "This text block comes between the table and image.",
                        "order": 2
                    },
                    {
                        "id": "block_4",
                        "type": "image",
                        "caption": "Frontend Image Block Caption",
                        "imageId": "img_1234567890",
                        "data": test_image_b64,
                        "fileName": "frontend_test_image.png",
                        "size": "medium",
                        "order": 3
                    },
                    {
                        "id": "block_5",
                        "type": "text",
                        "content": "This text block comes after the image.",
                        "order": 4
                    },
                    {
                        "id": "block_6",
                        "type": "table",
                        "tableName": "Image Table from Frontend",
                        "caption": "Frontend Image Table Caption",
                        "order": 5,
                        # This is an image table (uploaded table image)
                        "tableType": "image",
                        "imageId": "table_1234567890",
                        "data": test_image_b64,
                        "fileName": "frontend_table_image.png"
                    }
                ],
                "subsections": []
            }
        ],
        "references": [
            {
                "id": "ref_1",
                "text": "Frontend Integration Test Reference.",
                "order": 1
            }
        ],
        "figures": [],
        "tables": [],  # Tables are in contentBlocks, not here
        "settings": {
            "fontSize": "9.5pt",
            "columns": "double",
            "exportFormat": "docx",
            "includePageNumbers": True,
            "includeCopyright": True
        }
    }
    
    return test_data

def debug_frontend_data(data):
    """Debug the frontend data structure."""
    print("=== FRONTEND DATA STRUCTURE DEBUG ===", file=sys.stderr)
    
    sections = data.get("sections", [])
    print(f"Sections: {len(sections)}", file=sys.stderr)
    
    for i, section in enumerate(sections):
        print(f"Section {i+1}: {section.get('title', 'No title')}", file=sys.stderr)
        
        content_blocks = section.get("contentBlocks", [])
        print(f"  Content blocks: {len(content_blocks)}", file=sys.stderr)
        
        for j, block in enumerate(content_blocks):
            block_type = block.get("type", "unknown")
            print(f"    Block {j+1} ({block.get('order', 'no order')}): {block_type}", file=sys.stderr)
            
            if block_type == "table":
                print(f"      Table Name: '{block.get('tableName', 'None')}'", file=sys.stderr)
                print(f"      Caption: '{block.get('caption', 'None')}'", file=sys.stderr)
                print(f"      Table Type: '{block.get('tableType', 'None')}'", file=sys.stderr)
                
                if block.get('tableType') == 'interactive':
                    print(f"      Headers: {block.get('headers', [])}", file=sys.stderr)
                    print(f"      Data rows: {len(block.get('tableData', []))}", file=sys.stderr)
                    print(f"      Dimensions: {block.get('rows', 0)} x {block.get('columns', 0)}", file=sys.stderr)
                    
                    # Show actual table data
                    table_data = block.get('tableData', [])
                    for row_idx, row in enumerate(table_data):
                        print(f"        Row {row_idx}: {row}", file=sys.stderr)
                        
                elif block.get('tableType') == 'image':
                    print(f"      Image ID: {block.get('imageId', 'None')}", file=sys.stderr)
                    print(f"      File Name: {block.get('fileName', 'None')}", file=sys.stderr)
                    print(f"      Has Data: {bool(block.get('data'))}", file=sys.stderr)
                    
            elif block_type == "image":
                print(f"      Caption: '{block.get('caption', 'None')}'", file=sys.stderr)
                print(f"      Image ID: {block.get('imageId', 'None')}", file=sys.stderr)
                print(f"      Size: {block.get('size', 'None')}", file=sys.stderr)
                print(f"      File Name: {block.get('fileName', 'None')}", file=sys.stderr)
                print(f"      Has Data: {bool(block.get('data'))}", file=sys.stderr)
                
            elif block_type == "text":
                content_preview = block.get('content', '')[:50] + "..." if len(block.get('content', '')) > 50 else block.get('content', '')
                print(f"      Content: '{content_preview}'", file=sys.stderr)

def main():
    """Run the frontend integration test."""
    print("=== FRONTEND INTEGRATION TEST ===")
    
    # Create test data that matches frontend structure
    test_data = create_frontend_simulation_data()
    
    # Debug the input data structure
    debug_frontend_data(test_data)
    
    print("\n=== GENERATING DOCUMENT ===")
    try:
        # Generate the document
        doc_bytes = generate_ieee_document(test_data)
        
        # Save to file
        output_file = "test_frontend_integration_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Document generated successfully: {output_file}")
        print(f"📊 Document size: {len(doc_bytes)} bytes")
        
        print("\n=== EXPECTED DOCUMENT STRUCTURE ===")
        print("1. Title: 'Frontend Integration Test'")
        print("2. Authors: Frontend Test Author with full details")
        print("3. Abstract and keywords")
        print("4. Section 1: 'Frontend Integration Test Section'")
        print("   a. Text: 'This text block comes before the interactive table.'")
        print("   b. TABLE 1.1: INTERACTIVE TABLE FROM FRONTEND")
        print("      - Should show visible interactive table with borders")
        print("      - Headers: Frontend Header 1, Frontend Header 2, Frontend Header 3")
        print("      - 2 data rows with Frontend Data X,Y values")
        print("   c. Text: 'This text block comes between the table and image.'")
        print("   d. FIG. 1.1: FRONTEND IMAGE BLOCK CAPTION")
        print("      - Should show fully visible image (not half-hidden)")
        print("   e. Text: 'This text block comes after the image.'")
        print("   f. TABLE 1.2: IMAGE TABLE FROM FRONTEND")
        print("      - Should show table image (uploaded table)")
        print("5. References")
        
        print("\n=== CRITICAL CHECKS ===")
        print("🔍 Open the document and verify:")
        print("   1. Interactive table (TABLE 1.1) appears with visible borders and data")
        print("   2. Image (FIG. 1.1) is fully visible, not half-hidden")
        print("   3. Image table (TABLE 1.2) appears as an image")
        print("   4. All content appears in the correct sequential order")
        print("   5. No duplicate captions or missing content")
        
        print("\n=== TROUBLESHOOTING GUIDE ===")
        print("❌ If interactive table doesn't appear:")
        print("   - Check table border generation in add_ieee_table()")
        print("   - Verify tableType='interactive' is processed correctly")
        print("   - Check headers and tableData are being used")
        print("❌ If image is half-hidden:")
        print("   - Check image paragraph formatting in add_section()")
        print("   - Verify two-column layout isn't interfering")
        print("❌ If image table doesn't appear:")
        print("   - Check tableType='image' processing in add_ieee_table()")
        print("   - Verify image data is being decoded correctly")
        
    except Exception as e:
        print(f"❌ Error generating document: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())