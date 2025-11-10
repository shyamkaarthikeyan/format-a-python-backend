#!/usr/bin/env python3
"""
Test frontend integration with standalone tables and figures
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def test_frontend_integration():
    """Test with data structure that matches frontend"""
    print("🧪 TESTING FRONTEND INTEGRATION")
    print("=" * 50)
    
    # Data structure that matches what frontend now sends
    frontend_data = {
        "title": "Frontend Integration Test",
        "authors": [
            {"name": "Test Author", "department": "Computer Science", "email": "test@example.com"}
        ],
        "abstract": "This tests the integration between frontend table/figure forms and backend processing.",
        "keywords": "frontend, backend, tables, figures, integration",
        "sections": [
            {
                "id": "section1",
                "title": "Content Section",
                "contentBlocks": [
                    {
                        "id": "text1",
                        "type": "text",
                        "content": "This section contains content blocks from sections.",
                        "order": 1
                    }
                ],
                "order": 1
            }
        ],
        "references": [],
        "figures": [
            {
                "id": "fig1",
                "fileName": "standalone_figure.png",
                "originalName": "standalone_figure.png",
                "caption": "Standalone Figure from Figure Form",
                "size": "medium",
                "position": "here",
                "order": 1,
                "mimeType": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            }
        ],
        "tables": [
            {
                "id": "table1",
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Standalone Table",
                "caption": "Table from Table Form",
                "size": "medium",
                "position": "here",
                "order": 1,
                "headers": ["Parameter", "Value", "Unit"],
                "tableData": [
                    ["Temperature", "25", "°C"],
                    ["Pressure", "1013", "hPa"],
                    ["Humidity", "60", "%"]
                ]
            },
            {
                "id": "table2", 
                "type": "image",
                "tableType": "image",
                "tableName": "Image Table",
                "caption": "Table as Image",
                "size": "large",
                "position": "here",
                "order": 2,
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "mimeType": "image/png",
                "originalName": "table_image.png"
            }
        ]
    }
    
    try:
        print("📋 Building document model...")
        model = build_document_model(frontend_data)
        
        # Analyze the model
        sections = model.get("sections", [])
        print(f"📊 Model Analysis:")
        print(f"  • Sections: {len(sections)}")
        
        total_tables = 0
        total_images = 0
        
        for i, section in enumerate(sections):
            blocks = section.get("content_blocks", [])
            section_tables = [b for b in blocks if b.get("type") in ["table", "table_image"]]
            section_images = [b for b in blocks if b.get("type") == "figure"]
            
            print(f"  • Section {i+1}: '{section.get('title', 'Untitled')}'")
            print(f"    - Content blocks: {len(blocks)}")
            print(f"    - Tables: {len(section_tables)}")
            print(f"    - Images: {len(section_images)}")
            
            for j, table in enumerate(section_tables):
                print(f"      Table {j+1}: {table.get('type')} - Number: {table.get('number', 'no number')}")
                if table.get("caption", {}).get("text"):
                    print(f"        Caption: {table['caption']['text']}")
            
            for j, image in enumerate(section_images):
                print(f"      Image {j+1}: {image.get('type')} - Number: {image.get('number', 'no number')}")
                if image.get("caption", {}).get("text"):
                    print(f"        Caption: {image['caption']['text']}")
            
            total_tables += len(section_tables)
            total_images += len(section_images)
        
        print(f"\n📊 Total Content:")
        print(f"  • Tables processed: {total_tables}")
        print(f"  • Images processed: {total_images}")
        
        # Render HTML
        print("\n🌐 Rendering HTML...")
        html = render_to_html(model)
        
        # Check HTML content
        html_tables = html.count('<table class="ieee-table">')
        html_images = html.count('<img src="data:image/')
        
        print(f"📊 HTML Content:")
        print(f"  • HTML tables: {html_tables}")
        print(f"  • HTML images: {html_images}")
        
        # Save HTML
        with open("test_frontend_integration.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📁 HTML saved: test_frontend_integration.html")
        
        # Generate DOCX
        print("\n📄 Generating DOCX...")
        docx_bytes = generate_ieee_document(frontend_data)
        
        with open("test_frontend_integration.docx", "wb") as f:
            f.write(docx_bytes)
        print(f"📁 DOCX saved: test_frontend_integration.docx ({len(docx_bytes)} bytes)")
        
        # Results
        print(f"\n🎉 INTEGRATION TEST RESULTS:")
        print("=" * 50)
        
        expected_tables = len(frontend_data.get("tables", [])) 
        expected_figures = len(frontend_data.get("figures", []))
        
        print(f"Expected from frontend:")
        print(f"  • Standalone tables: {expected_tables}")
        print(f"  • Standalone figures: {expected_figures}")
        
        print(f"Processed by backend:")
        print(f"  • Tables in model: {total_tables}")
        print(f"  • Images in model: {total_images}")
        
        print(f"Rendered in HTML:")
        print(f"  • HTML tables: {html_tables}")
        print(f"  • HTML images: {html_images}")
        
        # Check if everything matches
        # Note: Image tables appear as HTML images, not HTML tables
        expected_interactive_tables = len([t for t in frontend_data.get("tables", []) if t.get("type") == "interactive"])
        expected_total_images = expected_figures + len([t for t in frontend_data.get("tables", []) if t.get("type") == "image"])
        
        success = (
            total_tables >= expected_tables and 
            total_images >= expected_figures and
            html_tables >= expected_interactive_tables and
            html_images >= expected_total_images
        )
        
        if success:
            print("✅ SUCCESS: Frontend integration working correctly!")
            print("   - Standalone tables and figures are processed")
            print("   - HTML rendering includes all content")
            print("   - DOCX generation completed")
        else:
            print("❌ ISSUE: Some content not processed correctly")
            print(f"   Expected: {expected_tables} tables, {expected_figures} figures")
            print(f"   Got: {total_tables} tables, {total_images} images in model")
            print(f"   HTML: {html_tables} tables, {html_images} images")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting frontend integration test...")
    success = test_frontend_integration()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)