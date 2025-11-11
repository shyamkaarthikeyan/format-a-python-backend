#!/usr/bin/env python3
"""
Test script to verify image visibility fixes in 2-column layout
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import generate_ieee_document
import base64

def create_test_document_with_images():
    """Create a test document with images to verify visibility fixes."""
    
    # Sample base64 image data (small PNG)
    sample_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    form_data = {
        "title": "Image Visibility Test Document",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "This document tests image visibility in 2-column IEEE format.",
        "keywords": "image visibility, 2-column layout, IEEE format",
        "sections": [
            {
                "title": "Introduction",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section contains text before an image."
                    },
                    {
                        "type": "image",
                        "data": sample_image_data,
                        "caption": "Test Image Small",
                        "size": "small"
                    },
                    {
                        "type": "text",
                        "content": "This section contains text after a small image."
                    },
                    {
                        "type": "image",
                        "data": sample_image_data,
                        "caption": "Test Image Medium",
                        "size": "medium"
                    },
                    {
                        "type": "text",
                        "content": "This section contains text after a medium image."
                    },
                    {
                        "type": "image",
                        "data": sample_image_data,
                        "caption": "Test Image Large",
                        "size": "large"
                    }
                ]
            },
            {
                "title": "Tables with Images",
                "contentBlocks": [
                    {
                        "type": "table",
                        "tableType": "image",
                        "caption": "Image Table Test",
                        "data": sample_image_data,
                        "size": "medium"
                    },
                    {
                        "type": "text",
                        "content": "Text after image table."
                    }
                ]
            }
        ]
    }
    
    try:
        print("🔧 Generating test document with image visibility fixes...")
        doc_bytes = generate_ieee_document(form_data)
        
        # Save test document
        output_path = "test_image_visibility_output.docx"
        with open(output_path, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Test document saved as: {output_path}")
        print("📋 Test includes:")
        print("   - Small, medium, and large images in content blocks")
        print("   - Image table")
        print("   - Text before and after images")
        print("   - 2-column layout compatibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating test document: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_test_document_with_images()
    sys.exit(0 if success else 1)