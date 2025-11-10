#!/usr/bin/env python3
"""
Test both table and image rendering to ensure they display properly in Word documents
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_table_and_image_rendering():
    """Test that both tables and images display properly in Word documents"""
    print("🧪 TESTING TABLE AND IMAGE RENDERING")
    print("=" * 50)
    
    # Test data with both tables and images
    test_data = {
        "title": "Table and Image Rendering Test",
        "abstract": "Testing both table and image rendering in Word documents to ensure proper display.",
        "keywords": "tables, images, word, docx, rendering, display",
        "authors": [
            {
                "name": "Test Author",
                "organization": "Test University",
                "email": "test@example.com"
            }
        ],
        "sections": [
            {
                "title": "Test Section with Table and Image",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section contains both a table and an image to test proper rendering.",
                        "order": 1
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Data Table",
                        "caption": "Sample data for testing table rendering",
                        "headers": ["Item", "Value", "Status", "Notes"],
                        "tableData": [
                            ["Item A", "100", "Active", "Working properly"],
                            ["Item B", "200", "Inactive", "Needs attention"],
                            ["Item C", "300", "Pending", "Under review"],
                            ["Item D", "400", "Complete", "Finished successfully"]
                        ],
                        "order": 2
                    },
                    {
                        "type": "text",
                        "content": "The table above should be fully visible with all columns and rows. Below is an image that should display completely without being cut off.",
                        "order": 3
                    },
                    {
                        "type": "image",
                        "caption": "Test image for display verification",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "order": 4
                    },
                    {
                        "type": "text",
                        "content": "The image above should be centered and fully visible. This text should appear below the image with proper spacing.",
                        "order": 5
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("📊 Test Data Analysis:")
    print(f"  • Title: {test_data['title']}")
    print(f"  • Sections: {len(test_data['sections'])}")
    print(f"  • Content blocks: {len(test_data['sections'][0]['contentBlocks'])}")
    
    # Analyze content blocks
    content_blocks = test_data['sections'][0]['contentBlocks']
    table_count = sum(1 for block in content_blocks if block['type'] == 'table')
    image_count = sum(1 for block in content_blocks if block['type'] == 'image')
    text_count = sum(1 for block in content_blocks if block['type'] == 'text')
    
    print(f"  • Text blocks: {text_count}")
    print(f"  • Table blocks: {table_count}")
    print(f"  • Image blocks: {image_count}")
    
    # Find and analyze the table
    table_block = next((block for block in content_blocks if block['type'] == 'table'), None)
    if table_block:
        print(f"  • Table headers: {len(table_block['headers'])} columns")
        print(f"  • Table rows: {len(table_block['tableData'])} data rows")
        print(f"  • Headers: {table_block['headers']}")
    
    # Find and analyze the image
    image_block = next((block for block in content_blocks if block['type'] == 'image'), None)
    if image_block:
        print(f"  • Image caption: {image_block['caption']}")
        print(f"  • Image size: {image_block['size']}")
        print(f"  • Image data length: {len(image_block['data'])} characters")
    
    try:
        print("\n📄 Generating DOCX document...")
        
        # Capture debug output
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
            with open("test_table_and_image_fix_output.docx", "wb") as f:
                f.write(docx_buffer)
            print("📁 Saved as: test_table_and_image_fix_output.docx")
            
            # Analyze debug output
            print(f"\n📋 Debug Output Analysis:")
            if debug_output:
                debug_lines = debug_output.strip().split('\n')
                print(f"  • Debug messages: {len(debug_lines)}")
                
                # Look for table-related messages
                table_messages = [line for line in debug_lines if 'table' in line.lower() or 'column' in line.lower() or 'header' in line.lower() or 'data cell' in line.lower()]
                if table_messages:
                    print(f"  • Table messages: {len(table_messages)}")
                    for msg in table_messages[:5]:  # Show first 5
                        print(f"    - {msg.strip()}")
                    if len(table_messages) > 5:
                        print(f"    ... and {len(table_messages) - 5} more")
                
                # Look for image-related messages
                image_messages = [line for line in debug_lines if 'image' in line.lower() or 'picture' in line.lower() or 'width' in line.lower() or 'height' in line.lower()]
                if image_messages:
                    print(f"  • Image messages: {len(image_messages)}")
                    for msg in image_messages:
                        print(f"    - {msg.strip()}")
                
                # Look for error messages
                error_messages = [line for line in debug_lines if 'error' in line.lower() or 'warning' in line.lower() or 'failed' in line.lower()]
                if error_messages:
                    print(f"  ⚠️  Error/Warning messages: {len(error_messages)}")
                    for msg in error_messages:
                        print(f"    - {msg.strip()}")
                else:
                    print("  ✅ No error or warning messages")
            else:
                print("  • No debug messages captured")
            
            # File size validation
            if file_size > 35000:  # Should be substantial with table and image content
                print("✅ File size indicates substantial content was generated")
            else:
                print("⚠️  File size seems small - content might be missing")
                
            print("\n🎯 MANUAL VERIFICATION CHECKLIST:")
            print("Open test_table_and_image_fix_output.docx in Microsoft Word and verify:")
            print("\n📊 TABLE VERIFICATION:")
            print("   ✓ Table caption: 'TABLE 1.1: SAMPLE DATA FOR TESTING TABLE RENDERING'")
            print("   ✓ Table has 4 columns: Item, Value, Status, Notes")
            print("   ✓ Table has 4 data rows with test data")
            print("   ✓ Headers are bold and centered")
            print("   ✓ Data cells are left-aligned and readable")
            print("   ✓ Table borders are visible")
            print("   ✓ Table is properly spaced from surrounding text")
            
            print("\n🖼️  IMAGE VERIFICATION:")
            print("   ✓ Image caption: 'FIG. 1.1: TEST IMAGE FOR DISPLAY VERIFICATION'")
            print("   ✓ Image is centered on the page")
            print("   ✓ Image is fully visible (not cut off or inline with text)")
            print("   ✓ Image has proper spacing above and below")
            print("   ✓ Text flows properly around the image")
            print("   ✓ Caption appears below the image")
            
            print("\n📝 TEXT VERIFICATION:")
            print("   ✓ All text paragraphs are visible and properly formatted")
            print("   ✓ Text before table/image appears correctly")
            print("   ✓ Text after table/image appears correctly")
            print("   ✓ Proper spacing between all elements")
            
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
    success = test_table_and_image_rendering()
    if success:
        print("\n🎉 TABLE AND IMAGE RENDERING TEST COMPLETED!")
        print("Please manually verify both table and image display correctly in the Word document.")
    else:
        print("\n❌ TABLE AND IMAGE RENDERING TEST FAILED!")
    
    sys.exit(0 if success else 1)