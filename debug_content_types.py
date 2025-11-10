#!/usr/bin/env python3
"""
Debug script to test content type processing
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def test_content_types():
    """Test all content types: text, table, image, equation, subsection"""
    print("🧪 TESTING ALL CONTENT TYPES")
    print("=" * 50)
    
    # Create test data with all content types
    test_data = {
        "title": "Content Types Test Document",
        "authors": [
            {"name": "Test Author", "department": "Computer Science", "email": "test@university.edu"}
        ],
        "abstract": "This document tests all content types in IEEE format.",
        "keywords": "content types, tables, images, equations, IEEE format",
        "sections": [
            {
                "id": "section1",
                "title": "All Content Types Test",
                "contentBlocks": [
                    {
                        "id": "text1",
                        "type": "text",
                        "content": "This is a text block to test text rendering.",
                        "order": 1
                    },
                    {
                        "id": "table1",
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Table",
                        "caption": "This is a test table",
                        "headers": ["Column A", "Column B", "Column C"],
                        "tableData": [
                            ["Data 1A", "Data 1B", "Data 1C"],
                            ["Data 2A", "Data 2B", "Data 2C"],
                            ["Data 3A", "Data 3B", "Data 3C"]
                        ],
                        "size": "medium",
                        "order": 2
                    },
                    {
                        "id": "image1",
                        "type": "image",
                        "caption": "Test Image",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "order": 3
                    },
                    {
                        "id": "equation1",
                        "type": "equation",
                        "content": "E = mc²",
                        "equationNumber": "1",
                        "order": 4
                    },
                    {
                        "id": "subsection1",
                        "type": "subsection",
                        "title": "Test Subsection",
                        "content": "This is a subsection content.",
                        "order": 5
                    }
                ],
                "order": 1
            }
        ],
        "references": [
            {"id": "ref1", "text": "Test Reference. IEEE Transactions, 2023.", "order": 1}
        ]
    }
    
    try:
        print("📋 Building document model...")
        model = build_document_model(test_data)
        
        print("📊 Analyzing model structure:")
        sections = model.get("sections", [])
        
        for i, section in enumerate(sections):
            content_blocks = section.get("content_blocks", [])
            print(f"  Section {i+1}: '{section.get('title', 'Untitled')}'")
            print(f"    - Content blocks: {len(content_blocks)}")
            
            for j, block in enumerate(content_blocks):
                block_type = block.get("type", "unknown")
                print(f"      Block {j+1}: {block_type}")
                
                if block_type == "table":
                    print(f"        - Table type: {block.get('table_type', 'not set')}")
                    print(f"        - Headers: {block.get('headers', 'not set')}")
                    print(f"        - Caption: {block.get('caption', {}).get('text', 'not set')}")
                elif block_type == "figure":
                    print(f"        - Caption: {block.get('caption', {}).get('text', 'not set')}")
                elif block_type == "equation":
                    print(f"        - Content: {block.get('content', 'not set')}")
                elif block_type == "text":
                    content = block.get("content", "")
                    print(f"        - Content: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        print("\n🌐 Rendering to HTML...")
        html = render_to_html(model)
        
        # Count different elements in HTML
        table_count = html.count('<table')
        image_count = html.count('<img')
        equation_count = html.count('ieee-equation')
        
        print(f"📊 HTML Analysis:")
        print(f"  • HTML tables: {table_count}")
        print(f"  • HTML images: {image_count}")
        print(f"  • HTML equations: {equation_count}")
        print(f"  • HTML length: {len(html)} characters")
        
        # Save HTML for inspection
        html_file = "debug_content_types_output.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"📁 HTML saved: {html_file}")
        
        print("\n📄 Generating DOCX...")
        docx_bytes = generate_ieee_document(test_data)
        
        docx_file = "debug_content_types_output.docx"
        with open(docx_file, 'wb') as f:
            f.write(docx_bytes)
        print(f"📁 DOCX saved: {docx_file} ({len(docx_bytes)} bytes)")
        
        print(f"\n🎉 TEST COMPLETE!")
        print("=" * 50)
        print("Generated files:")
        print(f"  • {html_file}")
        print(f"  • {docx_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting content types test...")
    success = test_content_types()
    if success:
        print("✅ Test completed successfully")
    else:
        print("❌ Test failed")
        sys.exit(1)