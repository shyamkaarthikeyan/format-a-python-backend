#!/usr/bin/env python3
"""
Complete flow debug script to trace table and image data from frontend to backend.
This will help identify exactly where the visibility issues occur.
"""

import base64
import json
import sys
from ieee_generator_fixed import generate_ieee_document

def create_comprehensive_test_data():
    """Create test data that matches the exact frontend schema structure."""
    
    # Create a simple base64 image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    # This matches the exact structure sent from the frontend
    test_data = {
        "title": "Complete Flow Debug Test",
        "authors": [
            {
                "id": "author_1",
                "name": "Debug Author",
                "department": "Computer Science",
                "organization": "Debug University",
                "city": "Debug City",
                "state": "Debug State",
                "email": "debug@example.com",
                "customFields": []
            }
        ],
        "abstract": "This document tests the complete data flow from frontend to backend for table and image visibility issues.",
        "keywords": "debug, frontend, backend, tables, images, visibility",
        "sections": [
            {
                "id": "section_1",
                "title": "Test Section with Content Blocks",
                "order": 1,
                "contentBlocks": [
                    {
                        "id": "text_1",
                        "type": "text",
                        "content": "This is the first text block before the table.",
                        "order": 1
                    },
                    {
                        "id": "table_1",
                        "type": "table",
                        "tableName": "Frontend Table Name",
                        "caption": "Frontend Table Caption",
                        "tableType": "interactive",
                        "size": "medium",
                        "position": "here",
                        "order": 2,
                        "rows": 3,
                        "columns": 3,
                        "headers": ["Frontend Col 1", "Frontend Col 2", "Frontend Col 3"],
                        "tableData": [
                            ["Frontend R1C1", "Frontend R1C2", "Frontend R1C3"],
                            ["Frontend R2C1", "Frontend R2C2", "Frontend R2C3"]
                        ]
                    },
                    {
                        "id": "text_2", 
                        "type": "text",
                        "content": "This is text between the table and image.",
                        "order": 3
                    },
                    {
                        "id": "image_1",
                        "type": "image",
                        "caption": "Frontend Image Caption",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "size": "medium",
                        "position": "here",
                        "order": 4
                    },
                    {
                        "id": "text_3",
                        "type": "text", 
                        "content": "This is the final text block after the image.",
                        "order": 5
                    }
                ],
                "subsections": []
            }
        ],
        "references": [
            {
                "id": "ref_1",
                "text": "Debug Reference 1: Testing reference formatting.",
                "order": 1
            }
        ],
        "figures": [],
        "tables": [],  # Tables are now in contentBlocks, not separate
        "settings": {
            "fontSize": "9.5pt",
            "columns": "double",
            "exportFormat": "docx",
            "includePageNumbers": True,
            "includeCopyright": True
        }
    }
    
    return test_data

def debug_data_structure(data, prefix=""):
    """Debug the data structure to see what's being processed."""
    print(f"{prefix}=== DATA STRUCTURE DEBUG ===", file=sys.stderr)
    
    # Check sections
    sections = data.get("sections", [])
    print(f"{prefix}Sections found: {len(sections)}", file=sys.stderr)
    
    for i, section in enumerate(sections):
        print(f"{prefix}Section {i+1}: {section.get('title', 'No title')}", file=sys.stderr)
        
        # Check content blocks
        content_blocks = section.get("contentBlocks", [])
        print(f"{prefix}  Content blocks: {len(content_blocks)}", file=sys.stderr)
        
        for j, block in enumerate(content_blocks):
            block_type = block.get("type", "unknown")
            print(f"{prefix}    Block {j+1}: {block_type}", file=sys.stderr)
            
            if block_type == "table":
                print(f"{prefix}      Table Name: {block.get('tableName', 'None')}", file=sys.stderr)
                print(f"{prefix}      Table Caption: {block.get('caption', 'None')}", file=sys.stderr)
                print(f"{prefix}      Table Type: {block.get('tableType', 'None')}", file=sys.stderr)
                print(f"{prefix}      Headers: {block.get('headers', [])}", file=sys.stderr)
                print(f"{prefix}      Data rows: {len(block.get('tableData', []))}", file=sys.stderr)
                print(f"{prefix}      Rows x Cols: {block.get('rows', 0)} x {block.get('columns', 0)}", file=sys.stderr)
                
            elif block_type == "image":
                print(f"{prefix}      Image Caption: {block.get('caption', 'None')}", file=sys.stderr)
                print(f"{prefix}      Image Size: {block.get('size', 'None')}", file=sys.stderr)
                print(f"{prefix}      Has Data: {bool(block.get('data'))}", file=sys.stderr)
                if block.get('data'):
                    data_preview = block['data'][:50] + "..." if len(block['data']) > 50 else block['data']
                    print(f"{prefix}      Data Preview: {data_preview}", file=sys.stderr)
                    
            elif block_type == "text":
                content_preview = block.get('content', '')[:50] + "..." if len(block.get('content', '')) > 50 else block.get('content', '')
                print(f"{prefix}      Text Preview: {content_preview}", file=sys.stderr)

def main():
    """Run the complete flow debug test."""
    print("=== COMPLETE FLOW DEBUG TEST ===")
    
    # Create test data that matches frontend structure
    test_data = create_comprehensive_test_data()
    
    # Debug the input data structure
    debug_data_structure(test_data, "INPUT: ")
    
    print("\n=== GENERATING DOCUMENT ===")
    try:
        # Generate the document
        doc_bytes = generate_ieee_document(test_data)
        
        # Save to file
        output_file = "debug_complete_flow_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Document generated successfully: {output_file}")
        print(f"📊 Document size: {len(doc_bytes)} bytes")
        
        print("\n=== EXPECTED DOCUMENT STRUCTURE ===")
        print("1. Title: 'Complete Flow Debug Test'")
        print("2. Authors: Debug Author with full affiliation")
        print("3. Abstract and keywords")
        print("4. Section 1: 'Test Section with Content Blocks'")
        print("   a. Text: 'This is the first text block before the table.'")
        print("   b. TABLE 1.1: FRONTEND TABLE CAPTION")
        print("      - Should show visible table with borders")
        print("      - Headers: Frontend Col 1, Frontend Col 2, Frontend Col 3")
        print("      - 2 data rows with Frontend R1C1, etc.")
        print("   c. Text: 'This is text between the table and image.'")
        print("   d. FIG. 1.1: FRONTEND IMAGE CAPTION")
        print("      - Should show fully visible image (not half-hidden)")
        print("   e. Text: 'This is the final text block after the image.'")
        print("5. References: Debug Reference 1")
        
        print("\n=== DEBUGGING CHECKLIST ===")
        print("❓ Open the generated document and check:")
        print("   1. Does TABLE 1.1 caption appear?")
        print("   2. Does the actual table appear immediately after the caption?")
        print("   3. Is the table visible with borders and data?")
        print("   4. Does FIG. 1.1 caption appear?")
        print("   5. Does the actual image appear immediately after the caption?")
        print("   6. Is the image fully visible (not half-hidden)?")
        print("   7. Are all text blocks in the correct order?")
        
        print("\n=== TROUBLESHOOTING ===")
        print("If tables don't appear: Check table border generation")
        print("If images are half-hidden: Check image paragraph formatting")
        print("If order is wrong: Check content block processing sequence")
        
    except Exception as e:
        print(f"❌ Error generating document: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())