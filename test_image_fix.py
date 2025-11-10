#!/usr/bin/env python3
"""
Test specifically for image inline issue fix
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document

def test_image_fix():
    """Test that images are no longer inline with text"""
    print("🖼️  TESTING IMAGE INLINE FIX")
    print("=" * 40)
    
    # Simple test with just text and image
    test_data = {
        "title": "Image Inline Fix Test",
        "abstract": "Testing image display fix.",
        "keywords": "image, inline, fix, word",
        "authors": [
            {
                "name": "Image Tester",
                "organization": "Test Lab",
                "email": "image@test.com"
            }
        ],
        "sections": [
            {
                "title": "Image Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This text should appear BEFORE the image. The image below should NOT be inline with this text.",
                        "order": 1
                    },
                    {
                        "type": "image",
                        "caption": "Test image that should be block-level",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "order": 2
                    },
                    {
                        "type": "text",
                        "content": "This text should appear AFTER the image with proper spacing. It should NOT be inline with the image.",
                        "order": 3
                    }
                ]
            }
        ],
        "references": []
    }
    
    print("📊 Test Data:")
    print(f"  • Sections: {len(test_data['sections'])}")
    print(f"  • Content blocks: {len(test_data['sections'][0]['contentBlocks'])}")
    
    # Find image block
    image_block = None
    for block in test_data['sections'][0]['contentBlocks']:
        if block['type'] == 'image':
            image_block = block
            break
    
    if image_block:
        print(f"  • Image caption: {image_block['caption']}")
        print(f"  • Image size: {image_block['size']}")
        print(f"  • Image data length: {len(image_block['data'])}")
    
    try:
        print("\n📄 Generating DOCX with image fix...")
        
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
            with open("test_image_fix_output.docx", "wb") as f:
                f.write(docx_buffer)
            print("📁 Saved as: test_image_fix_output.docx")
            
            # Analyze debug output for image processing
            print(f"\n📋 Debug Output Analysis:")
            if debug_output:
                debug_lines = debug_output.strip().split('\n')
                
                # Look for image-related messages
                image_messages = [line for line in debug_lines if 'image' in line.lower()]
                if image_messages:
                    print(f"  • Image processing messages:")
                    for msg in image_messages:
                        print(f"    - {msg.strip()}")
                else:
                    print(f"  ⚠️  No image processing messages found")
                
                # Look for section processing
                section_messages = [line for line in debug_lines if 'section' in line.lower()]
                if section_messages:
                    print(f"  • Section processing messages:")
                    for msg in section_messages:
                        print(f"    - {msg.strip()}")
                
                # Show all debug output if short
                if len(debug_lines) < 20:
                    print(f"  • All debug messages:")
                    for msg in debug_lines:
                        if msg.strip():
                            print(f"    - {msg.strip()}")
            else:
                print("  • No debug messages captured")
            
            print(f"\n🎯 MANUAL VERIFICATION:")
            print(f"Open test_image_fix_output.docx and check:")
            print(f"  1. Text before image appears normally")
            print(f"  2. Image is centered and fully visible (not cut off)")
            print(f"  3. Image is NOT inline with surrounding text")
            print(f"  4. Text after image appears with proper spacing")
            print(f"  5. Image caption appears below the image")
            
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
    success = test_image_fix()
    if success:
        print("\n🎉 IMAGE FIX TEST COMPLETED!")
    else:
        print("\n❌ IMAGE FIX TEST FAILED!")
    
    sys.exit(0 if success else 1)