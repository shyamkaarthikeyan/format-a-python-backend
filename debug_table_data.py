#!/usr/bin/env python3
"""
Debug script to analyze table and image data flow
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_document_data(data):
    """Analyze document data to find tables and images"""
    print("🔍 ANALYZING DOCUMENT DATA FOR TABLES AND IMAGES")
    print("=" * 60)
    
    # Check top-level structure
    print("📋 Top-level keys:")
    for key in data.keys():
        print(f"  • {key}: {type(data[key])}")
    
    # Check for standalone tables
    tables = data.get("tables", [])
    print(f"\n📊 Standalone Tables: {len(tables)} found")
    for i, table in enumerate(tables):
        print(f"  Table {i+1}:")
        print(f"    - Type: {table.get('type', 'unknown')}")
        print(f"    - TableType: {table.get('tableType', 'unknown')}")
        print(f"    - Name: {table.get('tableName', 'unnamed')}")
        print(f"    - Caption: {table.get('caption', 'no caption')}")
        if table.get('headers'):
            print(f"    - Headers: {table['headers']}")
        if table.get('tableData'):
            print(f"    - Data rows: {len(table['tableData'])}")
        if table.get('data'):
            print(f"    - Image data: {len(table['data'])} characters")
    
    # Check for standalone figures
    figures = data.get("figures", [])
    print(f"\n🖼️ Standalone Figures: {len(figures)} found")
    for i, figure in enumerate(figures):
        print(f"  Figure {i+1}:")
        print(f"    - Caption: {figure.get('caption', 'no caption')}")
        print(f"    - Size: {figure.get('size', 'unknown')}")
        if figure.get('data'):
            print(f"    - Image data: {len(figure['data'])} characters")
    
    # Check sections for content blocks
    sections = data.get("sections", [])
    print(f"\n📑 Sections: {len(sections)} found")
    
    total_table_blocks = 0
    total_image_blocks = 0
    
    for i, section in enumerate(sections):
        content_blocks = section.get("contentBlocks", [])
        section_tables = [b for b in content_blocks if b.get("type") == "table"]
        section_images = [b for b in content_blocks if b.get("type") == "image"]
        
        print(f"  Section {i+1}: '{section.get('title', 'Untitled')}'")
        print(f"    - Content blocks: {len(content_blocks)}")
        print(f"    - Table blocks: {len(section_tables)}")
        print(f"    - Image blocks: {len(section_images)}")
        
        # Analyze table blocks
        for j, table_block in enumerate(section_tables):
            print(f"      Table Block {j+1}:")
            print(f"        - TableType: {table_block.get('tableType', 'unknown')}")
            print(f"        - TableName: {table_block.get('tableName', 'unnamed')}")
            if table_block.get('headers'):
                print(f"        - Headers: {table_block['headers']}")
            if table_block.get('tableData'):
                print(f"        - Data rows: {len(table_block['tableData'])}")
            if table_block.get('data'):
                print(f"        - Image data: {len(table_block['data'])} characters")
        
        # Analyze image blocks
        for j, image_block in enumerate(section_images):
            print(f"      Image Block {j+1}:")
            print(f"        - Caption: {image_block.get('caption', 'no caption')}")
            print(f"        - Size: {image_block.get('size', 'unknown')}")
            if image_block.get('data'):
                print(f"        - Image data: {len(image_block['data'])} characters")
        
        total_table_blocks += len(section_tables)
        total_image_blocks += len(section_images)
    
    print(f"\n📊 SUMMARY:")
    print(f"  • Standalone tables: {len(tables)}")
    print(f"  • Standalone figures: {len(figures)}")
    print(f"  • Table content blocks: {total_table_blocks}")
    print(f"  • Image content blocks: {total_image_blocks}")
    print(f"  • Total tables: {len(tables) + total_table_blocks}")
    print(f"  • Total images: {len(figures) + total_image_blocks}")

def create_test_data_with_tables():
    """Create test data with tables and images"""
    return {
        "title": "Test Document with Tables and Images",
        "authors": [{"name": "Test Author", "email": "test@example.com"}],
        "abstract": "Test abstract",
        "keywords": "test, tables, images",
        "sections": [
            {
                "id": "section1",
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "id": "text1",
                        "type": "text",
                        "content": "This is a test paragraph.",
                        "order": 1
                    },
                    {
                        "id": "table1",
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Interactive Table",
                        "caption": "This is a test interactive table",
                        "headers": ["Header 1", "Header 2", "Header 3"],
                        "tableData": [
                            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
                        ],
                        "size": "medium",
                        "order": 2
                    },
                    {
                        "id": "table2",
                        "type": "table",
                        "tableType": "image",
                        "tableName": "Test Image Table",
                        "caption": "This is a test image table",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "large",
                        "order": 3
                    },
                    {
                        "id": "image1",
                        "type": "image",
                        "caption": "Test Figure",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "order": 4
                    }
                ],
                "order": 1
            }
        ],
        "references": [],
        "figures": [
            {
                "id": "fig1",
                "caption": "Standalone Figure",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "size": "small",
                "originalName": "test.png",
                "mimeType": "image/png"
            }
        ],
        "tables": [
            {
                "id": "standalone_table1",
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Standalone Interactive Table",
                "caption": "This is a standalone interactive table",
                "headers": ["Col A", "Col B"],
                "tableData": [
                    ["Data A1", "Data B1"],
                    ["Data A2", "Data B2"]
                ],
                "size": "medium"
            }
        ]
    }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test with sample data
        print("🧪 Testing with sample data...")
        test_data = create_test_data_with_tables()
        analyze_document_data(test_data)
    else:
        # Read from stdin (like the real API)
        print("📥 Reading document data from stdin...")
        try:
            input_data = sys.stdin.read()
            if not input_data.strip():
                print("❌ No data received from stdin")
                sys.exit(1)
            
            document_data = json.loads(input_data)
            analyze_document_data(document_data)
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)