#!/usr/bin/env python3
"""
Test script to verify 2-column image layout fixes
Addresses: figure names, text wrapping, column compatibility
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document
import base64

def create_2column_image_test():
    """Test images in 2-column layout with proper figure numbering."""
    
    # Sample base64 image data (small test image)
    sample_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    form_data = {
        "title": "2-Column Image Layout Test",
        "authors": [{"name": "Test Author", "affiliation": "Test University"}],
        "abstract": "Testing image visibility and figure numbering in 2-column IEEE format.",
        "keywords": "2-column layout, image visibility, figure numbering",
        "sections": [
            {
                "title": "Image Tests",
                "contentBlocks": [
                    {"type": "text", "content": "Text before first image. This text should flow around the image properly in the 2-column layout."},
                    {"type": "image", "data": sample_image, "caption": "First Test Image", "size": "small"},
                    {"type": "text", "content": "Text between images. This should demonstrate proper text flow."},
                    {"type": "image", "data": sample_image, "caption": "Second Test Image", "size": "medium"},
                    {"type": "text", "content": "More text to test column flow and image positioning."},
                    {"type": "image", "data": sample_image, "caption": "Third Test Image", "size": "large"}
                ]
            }
        ]
    }
    
    try:
        print("🔧 Testing 2-column image layout fixes...")
        doc_bytes = generate_ieee_document(form_data)
        
        with open("test_2column_image_output.docx", "wb") as f:
            f.write(doc_bytes)
        
        print("✅ Test completed: test_2column_image_output.docx")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    create_2column_image_test()