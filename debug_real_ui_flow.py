#!/usr/bin/env python3
"""
Debug script to simulate EXACT UI data flow and identify table visibility issues.
This replicates the exact data structure sent from the frontend.
"""

import base64
import json
import sys
from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def create_real_ui_table_data():
    """Create test data that exactly matches what the UI sends."""
    
    # This is the EXACT structure the frontend sends after our fixes
    test_data = {
        "id": "doc_123",
        "title": "Real UI Flow Test: Table Visibility Debug",
        "abstract": "Testing the exact data structure sent from the UI to identify table visibility issues.",
        "keywords": "debug, ui, tables, visibility",
        "authors": [
            {
                "id": "author_1",
                "name": "UI Test Author",
                "department": "Computer Science",
                "organization": "Test University",
                "city": "Test City",
                "state": "Test State",
                "email": "test@example.com",
                "customFields": []
            }
        ],
        "sections": [
            {
                "id": "section_1",
                "title": "Test Section with Tables",
                "order": 0,
                "contentBlocks": [
                    {
                        "id": "block_1",
                        "type": "text",
                        "content": "This is text before the table.",
                        "order": 0
                    },
                    {
                        "id": "block_2",
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "UI Created Table",
                        "caption": "Table Created Through UI Form",
                        "size": "medium",
                        "position": "here",
                        "order": 1,
                        # Interactive table data from UI
                        "rows": 3,
                        "columns": 3,
                        "headers": ["UI Col 1", "UI Col 2", "UI Col 3"],
                        "tableData": [
                            ["UI Data 1A", "UI Data 1B", "UI Data 1C"],
                            ["UI Data 2A", "UI Data 2B", "UI Data 2C"],
                            ["UI Data 3A", "UI Data 3B", "UI Data 3C"]
                        ]
                    },
                    {
                        "id": "block_3",
                        "type": "text",
                        "content": "This is text after the table.",
                        "order": 2
                    }
                ],
                "subsections": []
            }
        ],
        # Standalone tables from TableForm component
        "tables": [
            {
                "id": "table_standalone_1",
                "type": "interactive",
                "tableType": "interactive",  # Both type and tableType set (our fix)
                "tableName": "Standalone UI Table",
                "caption": "Table from TableForm Component",
                "size": "medium",
                "position": "here",
                "order": 0,
                "rows": 2,
                "columns": 2,
                "headers": ["Standalone Col 1", "Standalone Col 2"],
                "tableData": [
                    ["Standalone Data 1A", "Standalone Data 1B"],
                    ["Standalone Data 2A", "Standalone Data 2B"]
                ]
            }
        ],
        "figures": [],
        "references": [],
        "settings": {
            "fontSize": "10pt",
            "columns": "2",
            "exportFormat": "docx",
            "includePageNumbers": True,
            "includeCopyright": False
        }
    }
    
    return test_data

def debug_data_processing_step_by_step(test_data):
    """Debug each step of data processing to find where tables get lost."""
    
    print("=== STEP-BY-STEP DATA PROCESSING DEBUG ===")
    
    # Step 1: Analyze input data
    print("\n📊 STEP 1: INPUT DATA ANALYSIS")
    standalone_tables = test_data.get("tables", [])
    content_block_tables = []
    
    for section in test_data.get("sections", []):
        for block in section.get("contentBlocks", []):
            if block.get("type") == "table":
                content_block_tables.append(block)
    
    print(f"  • Standalone tables: {len(standalone_tables)}")
    print(f"  • Content block tables: {len(content_block_tables)}")
    
    for i, table in enumerate(standalone_tables):
        print(f"    Standalone table {i+1}:")
        print(f"      - ID: {table.get('id')}")
        print(f"      - Type: {table.get('type')}")
        print(f"      - TableType: {table.get('tableType')}")
        print(f"      - Name: {table.get('tableName')}")
        print(f"      - Headers: {table.get('headers')}")
        print(f"      - Data rows: {len(table.get('tableData', []))}")
    
    for i, table in enumerate(content_block_tables):
        print(f"    Content block table {i+1}:")
        print(f"      - ID: {table.get('id')}")
        print(f"      - Type: {table.get('type')}")
        print(f"      - TableType: {table.get('tableType')}")
        print(f"      - Name: {table.get('tableName')}")
        print(f"      - Headers: {table.get('headers')}")
        print(f"      - Data rows: {len(table.get('tableData', []))}")
    
    # Step 2: Test document model building
    print("\n🏗️  STEP 2: DOCUMENT MODEL BUILDING")
    try:
        model = build_document_model(test_data)
        print(f"  ✅ Document model built successfully")
        
        # Analyze model structure
        sections = model.get("sections", [])
        print(f"  • Model sections: {len(sections)}")
        
        for i, section in enumerate(sections):
            content_blocks = section.get("content_blocks", [])
            table_blocks = [b for b in content_blocks if b.get("type") == "table"]
            print(f"    Section {i+1}: {len(content_blocks)} blocks, {len(table_blocks)} tables")
            
            for j, table_block in enumerate(table_blocks):
                print(f"      Table {j+1}:")
                print(f"        - Type: {table_block.get('type')}")
                print(f"        - Has headers: {bool(table_block.get('headers'))}")
                print(f"        - Has data: {bool(table_block.get('tableData'))}")
                print(f"        - Caption: {table_block.get('caption', {}).get('text', 'No caption')}")
        
    except Exception as e:
        print(f"  ❌ Document model building failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test HTML rendering
    print("\n🌐 STEP 3: HTML RENDERING")
    try:
        html = render_to_html(model)
        print(f"  ✅ HTML rendered: {len(html)} characters")
        
        # Count HTML elements
        html_tables = html.count('<table class="ieee-table">')
        html_captions = html.count('ieee-table-caption')
        html_headers = html.count('<th class="ieee-table-header">')
        html_cells = html.count('<td class="ieee-table-cell">')
        
        print(f"  • HTML tables: {html_tables}")
        print(f"  • HTML captions: {html_captions}")
        print(f"  • HTML headers: {html_headers}")
        print(f"  • HTML cells: {html_cells}")
        
        # Save HTML for inspection
        with open("debug_real_ui_flow.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  💾 HTML saved as: debug_real_ui_flow.html")
        
    except Exception as e:
        print(f"  ❌ HTML rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test Word document generation
    print("\n📄 STEP 4: WORD DOCUMENT GENERATION")
    try:
        print("  🔄 Starting Word document generation...")
        doc_bytes = generate_ieee_document(test_data)
        
        if not doc_bytes or len(doc_bytes) == 0:
            print("  ❌ Word document is empty")
            return False
        
        print(f"  ✅ Word document generated: {len(doc_bytes)} bytes")
        
        # Save Word document
        with open("debug_real_ui_flow_output.docx", "wb") as f:
            f.write(doc_bytes)
        print(f"  💾 Word document saved as: debug_real_ui_flow_output.docx")
        
    except Exception as e:
        print(f"  ❌ Word document generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run the real UI flow debug test."""
    print("=== REAL UI FLOW DEBUG TEST ===")
    print("Simulating exact data structure from frontend after fixes")
    
    test_data = create_real_ui_table_data()
    
    success = debug_data_processing_step_by_step(test_data)
    
    print("\n=== DEBUG RESULTS ===")
    if success:
        print("✅ All processing steps completed successfully")
        print("\n🔍 MANUAL VERIFICATION REQUIRED:")
        print("1. Open debug_real_ui_flow.html in browser")
        print("   - Check if tables are visible with borders")
        print("   - Verify table data matches input")
        print("2. Open debug_real_ui_flow_output.docx in Word")
        print("   - Check if tables appear after captions")
        print("   - Verify table data matches HTML preview")
        print("3. Compare HTML vs Word document")
        print("   - Tables should be identical in both")
        
        print("\n❓ DEBUGGING QUESTIONS:")
        print("• Are tables visible in HTML preview?")
        print("• Are tables visible in Word document?")
        print("• Do table captions appear in both?")
        print("• Is table data identical in both?")
        print("• Are there any console errors during generation?")
        
    else:
        print("❌ Processing failed - check error messages above")
        print("\n🔧 TROUBLESHOOTING:")
        print("• Check if all required dependencies are installed")
        print("• Verify Python backend is working correctly")
        print("• Check for data structure issues in input")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())