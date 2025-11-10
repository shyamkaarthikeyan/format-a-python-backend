#!/usr/bin/env python3
"""
Test specifically for table rendering in Word documents
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_table_rendering():
    """Test that tables actually appear in the Word document"""
    print("🧪 TESTING TABLE RENDERING IN WORD DOCUMENT")
    print("=" * 50)
    
    # Simple test data with just a table
    test_data = {
        "title": "Table Rendering Test",
        "abstract": "Testing table rendering in Word documents.",
        "keywords": "tables, word, docx, rendering",
        "authors": [
            {
                "name": "Test Author",
                "organization": "Test University",
                "email": "test@example.com"
            }
        ],
        "sections": [
            {
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section contains a test table below:",
                        "order": 1
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Data Table",
                        "caption": "Sample data for testing table rendering",
                        "headers": ["Name", "Value", "Status"],
                        "tableData": [
                            ["Item 1", "100", "Active"],
                            ["Item 2", "200", "Inactive"],
                            ["Item 3", "300", "Pending"]
                        ],
                        "order": 2
                    },
                    {
                        "type": "text", 
                        "content": "The table above should be visible in the Word document.",
                        "order": 3
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("📊 Test Data:")
    print(f"  • Title: {test_data['title']}")
    print(f"  • Sections: {len(test_data['sections'])}")
    print(f"  • Content blocks: {len(test_data['sections'][0]['contentBlocks'])}")
    
    # Find the table block
    table_block = None
    for block in test_data['sections'][0]['contentBlocks']:
        if block['type'] == 'table':
            table_block = block
            break
    
    if table_block:
        print(f"  • Table headers: {table_block['headers']}")
        print(f"  • Table rows: {len(table_block['tableData'])}")
        print(f"  • Table name: {table_block['tableName']}")
    
    try:
        print("\n📄 Generating DOCX document...")
        docx_buffer = generate_ieee_document(test_data)
        
        if docx_buffer:
            file_size = len(docx_buffer)
            print(f"✅ DOCX generated successfully!")
            print(f"📁 File size: {file_size} bytes")
            
            # Save the test file
            with open("test_table_fix_output.docx", "wb") as f:
                f.write(docx_buffer)
            print("📁 Saved as: test_table_fix_output.docx")
            
            # Basic validation
            if file_size > 20000:  # Should be substantial with table content
                print("✅ File size indicates content was generated")
            else:
                print("⚠️  File size seems small - table might not be included")
                
            print("\n🎯 MANUAL VERIFICATION NEEDED:")
            print("   1. Open test_table_fix_output.docx in Microsoft Word")
            print("   2. Check if the table is visible with:")
            print("      - Table caption: 'TABLE 1.1: SAMPLE DATA FOR TESTING TABLE RENDERING'")
            print("      - 3 columns: Name, Value, Status")
            print("      - 3 data rows with test data")
            print("      - Proper IEEE formatting (9pt Times New Roman)")
            
            return True
            
        else:
            print("❌ Failed to generate DOCX document")
            return False
            
    except Exception as e:
        print(f"❌ Error generating document: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_table_rendering()
    if success:
        print("\n🎉 TABLE RENDERING TEST COMPLETED!")
        print("Please manually verify the table appears correctly in the Word document.")
    else:
        print("\n❌ TABLE RENDERING TEST FAILED!")
    
    sys.exit(0 if success else 1)