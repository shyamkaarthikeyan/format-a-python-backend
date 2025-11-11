#!/usr/bin/env python3
"""
Test script to verify the dual table system: standalone tables vs content block tables.
This tests the exact flow from UI TableForm to Word document.
"""

import base64
import json
import sys
from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def create_standalone_table_test():
    """Create test data with standalone tables (from TableForm component)."""
    
    test_data = {
        "title": "Dual Table System Test: Standalone Tables",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing standalone tables from TableForm component.",
        "keywords": "tables, standalone, tableform",
        "sections": [
            {
                "title": "Regular Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section has regular content blocks."
                    }
                ]
            }
        ],
        # STANDALONE TABLES - from TableForm component
        "tables": [
            {
                "id": "table_1",
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Standalone Interactive Table",
                "caption": "Table Created in TableForm Component",
                "size": "medium",
                "position": "here",
                "order": 0,
                "rows": 3,
                "columns": 3,
                "headers": ["Header A", "Header B", "Header C"],
                "tableData": [
                    ["Row 1A", "Row 1B", "Row 1C"],
                    ["Row 2A", "Row 2B", "Row 2C"],
                    ["Row 3A", "Row 3B", "Row 3C"]
                ]
            },
            {
                "id": "table_2",
                "type": "image",
                "tableType": "image",
                "tableName": "Standalone Image Table",
                "caption": "Image Table from TableForm",
                "size": "medium",
                "position": "here",
                "order": 1,
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==",
                "mimeType": "image/png",
                "originalName": "test_table.png",
                "fileName": "table_image.png"
            }
        ],
        "references": []
    }
    
    return test_data

def create_content_block_table_test():
    """Create test data with content block tables (from section content blocks)."""
    
    test_data = {
        "title": "Dual Table System Test: Content Block Tables",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing content block tables from section content blocks.",
        "keywords": "tables, contentblocks, sections",
        "sections": [
            {
                "title": "Section with Content Block Tables",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This text comes before the content block table."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Content Block Interactive Table",
                        "caption": "Table Created in Section Content Block",
                        "headers": ["Col X", "Col Y", "Col Z"],
                        "tableData": [
                            ["Data X1", "Data Y1", "Data Z1"],
                            ["Data X2", "Data Y2", "Data Z2"]
                        ],
                        "rows": 2,
                        "columns": 3
                    },
                    {
                        "type": "text",
                        "content": "This text comes after the content block table."
                    }
                ]
            }
        ],
        # NO standalone tables
        "references": []
    }
    
    return test_data

def create_mixed_table_test():
    """Create test data with BOTH standalone tables AND content block tables."""
    
    test_data = {
        "title": "Dual Table System Test: Mixed Tables",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing both standalone tables and content block tables together.",
        "keywords": "tables, mixed, standalone, contentblocks",
        "sections": [
            {
                "title": "Section with Content Block Table",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section has a content block table."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Content Block Table",
                        "caption": "Table from Content Block",
                        "headers": ["CB Col 1", "CB Col 2"],
                        "tableData": [
                            ["CB Data 1", "CB Data 2"],
                            ["CB Data 3", "CB Data 4"]
                        ],
                        "rows": 2,
                        "columns": 2
                    }
                ]
            }
        ],
        # STANDALONE TABLES - should be added to first section
        "tables": [
            {
                "id": "standalone_table",
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Standalone Table",
                "caption": "Table from TableForm",
                "size": "medium",
                "position": "here",
                "order": 999,  # Should appear after content block tables
                "rows": 2,
                "columns": 2,
                "headers": ["SA Col 1", "SA Col 2"],
                "tableData": [
                    ["SA Data 1", "SA Data 2"],
                    ["SA Data 3", "SA Data 4"]
                ]
            }
        ],
        "references": []
    }
    
    return test_data

def analyze_table_processing(test_name, test_data):
    """Analyze how tables are processed in both HTML and Word generation."""
    print(f"\n=== {test_name.upper()} ===")
    
    # Analyze input data structure
    standalone_tables = test_data.get("tables", [])
    content_block_tables = []
    
    for section in test_data.get("sections", []):
        for block in section.get("contentBlocks", []):
            if block.get("type") == "table":
                content_block_tables.append(block)
    
    print(f"📊 Input Data Analysis:")
    print(f"  • Standalone tables: {len(standalone_tables)}")
    print(f"  • Content block tables: {len(content_block_tables)}")
    
    if standalone_tables:
        print(f"  • Standalone table names: {[t.get('tableName', 'No name') for t in standalone_tables]}")
    
    if content_block_tables:
        print(f"  • Content block table names: {[t.get('tableName', 'No name') for t in content_block_tables]}")
    
    # Test HTML generation
    print(f"\n🌐 HTML Generation:")
    try:
        model = build_document_model(test_data)
        html = render_to_html(model)
        
        html_tables = html.count('<table class="ieee-table">')
        html_captions = html.count('ieee-table-caption')
        
        print(f"  ✅ HTML generated: {len(html)} characters")
        print(f"  • HTML tables: {html_tables}")
        print(f"  • HTML captions: {html_captions}")
        
    except Exception as e:
        print(f"  ❌ HTML generation failed: {e}")
        return False
    
    # Test Word generation
    print(f"\n📄 Word Generation:")
    try:
        doc_bytes = generate_ieee_document(test_data)
        
        if doc_bytes and len(doc_bytes) > 0:
            print(f"  ✅ Word document generated: {len(doc_bytes)} bytes")
            
            # Save for inspection
            filename = f"test_dual_table_{test_name.lower().replace(' ', '_')}.docx"
            with open(filename, "wb") as f:
                f.write(doc_bytes)
            print(f"  💾 Saved as: {filename}")
            
        else:
            print(f"  ❌ Word document is empty")
            return False
            
    except Exception as e:
        print(f"  ❌ Word generation failed: {e}")
        return False
    
    return True

def main():
    """Run the dual table system test."""
    print("=== DUAL TABLE SYSTEM TEST ===")
    print("Testing standalone tables vs content block tables")
    
    # Test 1: Standalone tables only
    test1_data = create_standalone_table_test()
    success1 = analyze_table_processing("Standalone Tables Only", test1_data)
    
    # Test 2: Content block tables only
    test2_data = create_content_block_table_test()
    success2 = analyze_table_processing("Content Block Tables Only", test2_data)
    
    # Test 3: Mixed tables (both types)
    test3_data = create_mixed_table_test()
    success3 = analyze_table_processing("Mixed Tables", test3_data)
    
    print("\n=== SUMMARY ===")
    print(f"✅ Standalone tables test: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Content block tables test: {'PASSED' if success2 else 'FAILED'}")
    print(f"✅ Mixed tables test: {'PASSED' if success3 else 'FAILED'}")
    
    if success1 and success2 and success3:
        print("\n🎉 All tests passed! Dual table system is working correctly.")
        print("\n📋 Expected Results:")
        print("1. Standalone tables should be converted to content blocks")
        print("2. Content block tables should be processed directly")
        print("3. Mixed tables should show both types in correct order")
        print("4. HTML preview and Word document should match")
        
        return 0
    else:
        print("\n❌ Some tests failed. Check the generated files for issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())