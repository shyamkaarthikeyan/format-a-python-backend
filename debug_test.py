#!/usr/bin/env python3
"""
Debug test for table and image processing
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def main():
    print("🚀 Starting debug test...")
    
    # Simple test data with table and image
    test_data = {
        "title": "Debug Test",
        "authors": [{"name": "Test Author"}],
        "sections": [
            {
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Table",
                        "caption": "A test table",
                        "headers": ["Col A", "Col B"],
                        "tableData": [["Data 1", "Data 2"]],
                        "order": 1
                    },
                    {
                        "type": "image",
                        "caption": "Test Image",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "order": 2
                    }
                ]
            }
        ]
    }
    
    try:
        print("📋 Building model...")
        model = build_document_model(test_data)
        print(f"✅ Model built with {len(model)} keys")
        
        # Check sections
        sections = model.get("sections", [])
        print(f"📊 Found {len(sections)} sections")
        
        for i, section in enumerate(sections):
            blocks = section.get("content_blocks", [])
            print(f"  Section {i+1}: {len(blocks)} content blocks")
            for j, block in enumerate(blocks):
                print(f"    Block {j+1}: {block.get('type', 'unknown')}")
        
        print("🌐 Rendering HTML...")
        html = render_to_html(model)
        print(f"✅ HTML rendered: {len(html)} characters")
        
        # Check for tables and images in HTML
        table_count = html.count('<table class="ieee-table">')
        image_count = html.count('<img src="data:image/')
        
        print(f"📊 HTML content:")
        print(f"  • Tables: {table_count}")
        print(f"  • Images: {image_count}")
        
        # Save HTML
        with open("debug_output.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📁 HTML saved to debug_output.html")
        
        print("✅ Debug test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()