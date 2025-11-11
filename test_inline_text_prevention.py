#!/usr/bin/env python3
"""
Test to verify images don't become inline with text causing half-visibility
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document
import base64

def test_inline_text_prevention():
    """Test that images don't become inline with text."""
    
    # Sample image data
    sample_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    form_data = {
        "title": "Inline Text Prevention Test",
        "authors": [{"name": "Test Author", "affiliation": "Test University"}],
        "abstract": "Testing that images don't become inline with text causing half-visibility issues.",
        "keywords": "inline text, image visibility, 2-column layout",
        "sections": [
            {
                "title": "Critical Test Section",
                "contentBlocks": [
                    {"type": "text", "content": "This is a long paragraph of text that should flow properly in the 2-column layout. The text should not interfere with images and images should not become inline with this text causing half-visibility issues. This paragraph is intentionally long to test text flow around images."},
                    {"type": "image", "data": sample_image, "caption": "Test Image After Long Text", "size": "large"},
                    {"type": "text", "content": "Another paragraph immediately after the image. This text should be completely separated from the image above and should not cause the image to become half-visible or inline."},
                    {"type": "image", "data": sample_image, "caption": "Second Test Image", "size": "medium"},
                    {"type": "text", "content": "Final paragraph to test complete separation. Images should be fully visible and properly spaced."},
                    {"type": "image", "data": sample_image, "caption": "Final Test Image", "size": "small"}
                ]
            }
        ]
    }
    
    try:
        print("🔧 Testing inline text prevention...")
        doc_bytes = generate_ieee_document(form_data)
        
        with open("test_inline_prevention_output.docx", "wb") as f:
            f.write(doc_bytes)
        
        print("✅ Test completed: test_inline_prevention_output.docx")
        print("📋 Verify in Word that:")
        print("   - Images are NOT inline with text")
        print("   - Images are fully visible (not half-hidden)")
        print("   - Proper spacing between text and images")
        print("   - Figure numbers display correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_inline_text_prevention()