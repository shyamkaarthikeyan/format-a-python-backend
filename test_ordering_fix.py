#!/usr/bin/env python3
"""
Test script to verify table and image ordering fixes
"""

import json
import sys
from ieee_generator_fixed import generate_ieee_document

def test_ordering_fix():
    """Test that tables and images appear in correct order"""
    
    # Create test data with mixed tables and figures
    test_data = {
        "title": "Test Document for Ordering Fix",
        "abstract": "This document tests the ordering of tables and figures.",
        "keywords": "test, ordering, tables, figures",
        "authors": [
            {
                "name": "Test Author",
                "email": "test@example.com",
                "affiliation": "Test University"
            }
        ],
        "sections": [
            {
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This is the first paragraph.",
                        "order": 0
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Table 1",
                        "caption": "First test table",
                        "headers": ["Column A", "Column B"],
                        "tableData": [["Row 1 A", "Row 1 B"], ["Row 2 A", "Row 2 B"]],
                        "order": 1
                    },
                    {
                        "type": "text", 
                        "content": "This is the second paragraph after the table.",
                        "order": 2
                    },
                    {
                        "type": "image",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                        "caption": "Test Figure 1",
                        "size": "medium",
                        "order": 3
                    },
                    {
                        "type": "text",
                        "content": "This is the third paragraph after the figure.",
                        "order": 4
                    }
                ]
            }
        ],
        "tables": [
            {
                "id": "standalone_table_1",
                "type": "interactive", 
                "tableName": "Standalone Table",
                "caption": "This is a standalone table",
                "headers": ["Header 1", "Header 2", "Header 3"],
                "tableData": [
                    ["Data 1", "Data 2", "Data 3"],
                    ["Data 4", "Data 5", "Data 6"]
                ],
                "order": 10  # Should appear after section content
            }
        ],
        "figures": [
            {
                "id": "standalone_figure_1",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "caption": "Standalone Figure",
                "size": "medium",
                "order": 5  # Should appear before standalone table
            }
        ],
        "references": []
    }
    
    print("Testing ordering fix with mixed content...")
    print("Expected order:")
    print("1. First paragraph (order: 0)")
    print("2. Test Table 1 (order: 1)")
    print("3. Second paragraph (order: 2)")
    print("4. Test Figure 1 (order: 3)")
    print("5. Third paragraph (order: 4)")
    print("6. Standalone Figure (order: 5)")
    print("7. Standalone Table (order: 10)")
    print()
    
    try:
        # Generate document
        result = generate_ieee_document(test_data)
        
        if result:
            # Save test output (result is bytes directly)
            with open('test_ordering_fix_output.docx', 'wb') as f:
                f.write(result)
            
            print("✅ Document generated successfully!")
            print("📄 Output saved as: test_ordering_fix_output.docx")
            print("🔍 Please open the document to verify:")
            print("   - Tables and figures appear in correct order")
            print("   - Images are fully visible (not half-cut)")
            print("   - Table names appear above tables")
            print("   - Figure captions appear below figures")
            return True
            
        else:
            print("❌ Document generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ordering_fix()
    sys.exit(0 if success else 1)