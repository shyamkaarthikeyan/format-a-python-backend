#!/usr/bin/env python3
"""
Debug script to identify why tables show only captions but not data in Word documents
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def debug_table_issue():
    """Debug table rendering issue - caption appears but table data doesn't"""
    print("🔍 DEBUGGING TABLE RENDERING ISSUE")
    print("=" * 50)
    
    # Test data that mimics frontend form input
    test_data = {
        "title": "Table Debug Test",
        "abstract": "Testing why table captions appear but table data doesn't.",
        "keywords": "tables, debugging, word, docx",
        "authors": [
            {
                "name": "Debug User",
                "organization": "Test Lab",
                "email": "debug@test.com"
            }
        ],
        "sections": [
            {
                "title": "Test Section with Table",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This text should appear before the table.",
                        "order": 1
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Debug Test Table",
                        "caption": "This is a test table for debugging",
                        "headers": ["Column A", "Column B", "Column C"],
                        "tableData": [
                            ["Row 1 A", "Row 1 B", "Row 1 C"],
                            ["Row 2 A", "Row 2 B", "Row 2 C"],
                            ["Row 3 A", "Row 3 B", "Row 3 C"]
                        ],
                        "order": 2
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the table.",
                        "order": 3
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("📊 Debug Data Analysis:")
    table_block = test_data['sections'][0]['contentBlocks'][1]
    print(f"  • Table type: {table_block['type']}")
    print(f"  • Table tableType: {table_block['tableType']}")
    print(f"  • Table name: {table_block['tableName']}")
    print(f"  • Table caption: {table_block['caption']}")
    print(f"  • Headers: {table_block['headers']}")
    print(f"  • Rows: {len(table_block['tableData'])}")
    print(f"  • First row: {table_block['tableData'][0]}")
    
    # Test the table data extraction logic
    print("\n🔧 Testing Table Data Extraction:")
    headers = table_block.get("headers", [])
    rows_data = table_block.get("tableData", []) or table_block.get("rows", [])
    
    print(f"  • Extracted headers: {headers}")
    print(f"  • Extracted rows_data: {rows_data}")
    print(f"  • Headers valid: {bool(headers)}")
    print(f"  • Rows valid: {bool(rows_data)}")
    
    if not headers or not rows_data:
        print("❌ ISSUE FOUND: Headers or rows_data is empty!")
        print(f"  • Headers empty: {not headers}")
        print(f"  • Rows empty: {not rows_data}")
        return False
    
    try:
        print("\n📄 Generating DOCX with debug info...")
        
        # Redirect stderr to capture debug output
        import io
        from contextlib import redirect_stderr
        
        stderr_capture = io.StringIO()
        
        with redirect_stderr(stderr_capture):
            docx_buffer = generate_ieee_document(test_data)
        
        debug_output = stderr_capture.getvalue()
        
        if docx_buffer:
            file_size = len(docx_buffer)
            print(f"✅ DOCX generated successfully!")
            print(f"📁 File size: {file_size} bytes")
            
            # Save the test file
            with open("debug_table_issue_output.docx", "wb") as f:
                f.write(docx_buffer)
            print("📁 Saved as: debug_table_issue_output.docx")
            
            # Analyze debug output
            print(f"\n📋 Debug Output Analysis:")
            if debug_output:
                print("Debug messages captured:")
                for line in debug_output.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            else:
                print("  No debug messages captured")
            
            # Check for table-related warnings
            if "Warning: Interactive table missing headers or data" in debug_output:
                print("❌ CRITICAL: Table data extraction failed!")
                return False
            elif "table" in debug_output.lower():
                print("✅ Table processing messages found in debug output")
            
            print("\n🎯 MANUAL VERIFICATION STEPS:")
            print("1. Open debug_table_issue_output.docx in Microsoft Word")
            print("2. Look for:")
            print("   - Table caption: 'TABLE 1.1: THIS IS A TEST TABLE FOR DEBUGGING'")
            print("   - Actual table with 3 columns and 3 data rows")
            print("   - Headers: Column A, Column B, Column C")
            print("   - Data rows with 'Row X Y' format")
            print("3. If only caption appears without table data, the issue is confirmed")
            
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
    success = debug_table_issue()
    if success:
        print("\n🎉 DEBUG TEST COMPLETED!")
        print("Check the generated Word document to verify if tables render correctly.")
    else:
        print("\n❌ DEBUG TEST FAILED!")
    
    sys.exit(0 if success else 1)