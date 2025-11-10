#!/usr/bin/env python3
"""
Comprehensive fix for table and image issues:
1. Tables in document sections not appearing in Word
2. Images appearing inline with text
3. UI showing "No tables added yet" when tables exist in sections
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_comprehensive_fixes():
    """Test all fixes for table and image issues"""
    print("🔧 COMPREHENSIVE TABLE AND IMAGE FIXES TEST")
    print("=" * 60)
    
    # Test data that includes tables in document sections (not standalone)
    test_data = {
        "title": "Comprehensive Table and Image Fix Test",
        "abstract": "Testing fixes for table and image rendering issues in document sections.",
        "keywords": "tables, images, sections, word, docx, fixes",
        "authors": [
            {
                "name": "Fix Tester",
                "organization": "Test University",
                "email": "fix@test.com"
            }
        ],
        "sections": [
            {
                "title": "Section with Table and Image",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section demonstrates tables and images within document sections.",
                        "order": 1
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Section Table Test",
                        "caption": "Table within document section",
                        "headers": ["Feature", "Status", "Notes"],
                        "tableData": [
                            ["Table in Section", "Working", "Should appear in Word"],
                            ["Image Display", "Fixed", "No longer inline"],
                            ["UI Recognition", "Fixed", "Tables counted properly"]
                        ],
                        "order": 2
                    },
                    {
                        "type": "text",
                        "content": "The table above should be fully visible. Below is an image that should display as a block element.",
                        "order": 3
                    },
                    {
                        "type": "image",
                        "caption": "Block-level image test",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "order": 4
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the image with proper spacing, not inline with it.",
                        "order": 5
                    }
                ]
            },
            {
                "title": "Second Section with More Content",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section has additional content to test multiple sections.",
                        "order": 1
                    },
                    {
                        "type": "table",
                        "tableType": "interactive", 
                        "tableName": "Second Section Table",
                        "caption": "Another table in a different section",
                        "headers": ["Item", "Value", "Result"],
                        "tableData": [
                            ["Test A", "Pass", "Success"],
                            ["Test B", "Pass", "Success"],
                            ["Test C", "Pass", "Success"]
                        ],
                        "order": 2
                    }
                ]
            }
        ],
        # Also include standalone tables to test both scenarios
        "tables": [
            {
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Standalone Table",
                "caption": "This is a standalone table",
                "headers": ["Standalone", "Table", "Test"],
                "tableData": [
                    ["Row 1", "Data 1", "Value 1"],
                    ["Row 2", "Data 2", "Value 2"]
                ]
            }
        ],
        "references": []
    }
    
    print("📊 Test Data Analysis:")
    print(f"  • Title: {test_data['title']}")
    print(f"  • Sections: {len(test_data['sections'])}")
    print(f"  • Standalone tables: {len(test_data.get('tables', []))}")
    
    # Count tables and images in sections
    section_tables = 0
    section_images = 0
    total_content_blocks = 0
    
    for section in test_data['sections']:
        content_blocks = section.get('contentBlocks', [])
        total_content_blocks += len(content_blocks)
        for block in content_blocks:
            if block['type'] == 'table':
                section_tables += 1
            elif block['type'] == 'image':
                section_images += 1
    
    print(f"  • Total content blocks: {total_content_blocks}")
    print(f"  • Tables in sections: {section_tables}")
    print(f"  • Images in sections: {section_images}")
    print(f"  • Expected total tables: {section_tables + len(test_data.get('tables', []))}")
    
    try:
        print("\n📄 Generating DOCX with comprehensive fixes...")
        
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
            with open("comprehensive_fixes_test_output.docx", "wb") as f:
                f.write(docx_buffer)
            print("📁 Saved as: comprehensive_fixes_test_output.docx")
            
            # Analyze debug output
            print(f"\n📋 Debug Output Analysis:")
            if debug_output:
                debug_lines = debug_output.strip().split('\n')
                
                # Count table processing messages
                table_creation_msgs = [line for line in debug_lines if 'Creating table with' in line]
                table_header_msgs = [line for line in debug_lines if 'Added header:' in line]
                table_data_msgs = [line for line in debug_lines if 'Added data cell' in line]
                
                print(f"  • Tables created: {len(table_creation_msgs)}")
                print(f"  • Headers added: {len(table_header_msgs)}")
                print(f"  • Data cells added: {len(table_data_msgs)}")
                
                # Count image processing messages
                image_msgs = [line for line in debug_lines if 'Added image as block element' in line or 'Added image with width' in line]
                print(f"  • Images processed: {len(image_msgs)}")
                
                # Show table creation messages
                if table_creation_msgs:
                    print(f"\n  📊 Table Creation Details:")
                    for msg in table_creation_msgs:
                        print(f"    - {msg.strip()}")
                
                # Show image processing messages
                if image_msgs:
                    print(f"\n  🖼️  Image Processing Details:")
                    for msg in image_msgs:
                        print(f"    - {msg.strip()}")
                
                # Check for errors
                error_msgs = [line for line in debug_lines if 'Error' in line or 'Warning' in line]
                if error_msgs:
                    print(f"\n  ⚠️  Issues Found:")
                    for msg in error_msgs:
                        print(f"    - {msg.strip()}")
                else:
                    print(f"\n  ✅ No errors or warnings found")
            
            print(f"\n🎯 VERIFICATION CHECKLIST:")
            print(f"Open comprehensive_fixes_test_output.docx and verify:")
            print(f"\n📊 TABLES:")
            print(f"   ✓ Section 1 table: 'TABLE 1.1: TABLE WITHIN DOCUMENT SECTION'")
            print(f"   ✓ Section 2 table: 'TABLE 2.1: ANOTHER TABLE IN A DIFFERENT SECTION'") 
            print(f"   ✓ Standalone table: Should appear at beginning")
            print(f"   ✓ All tables have headers and data rows visible")
            print(f"   ✓ Tables are properly formatted with borders")
            print(f"\n🖼️  IMAGES:")
            print(f"   ✓ Image appears as block element (not inline)")
            print(f"   ✓ Image is centered with proper spacing")
            print(f"   ✓ Text before and after image is properly separated")
            print(f"   ✓ Image caption appears below image")
            print(f"\n📝 LAYOUT:")
            print(f"   ✓ All content appears in correct order")
            print(f"   ✓ Proper spacing between all elements")
            print(f"   ✓ No overlapping or inline display issues")
            
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
    success = test_comprehensive_fixes()
    if success:
        print("\n🎉 COMPREHENSIVE FIXES TEST COMPLETED!")
        print("Please verify the Word document to confirm all fixes are working.")
    else:
        print("\n❌ COMPREHENSIVE FIXES TEST FAILED!")
    
    sys.exit(0 if success else 1)