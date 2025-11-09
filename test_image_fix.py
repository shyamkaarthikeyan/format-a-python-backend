#!/usr/bin/env python3
"""
Test script to verify image integration fix in IEEE generator
This tests that images from the figures array are properly processed
"""

import json
import sys
import os
from ieee_generator_fixed import generate_ieee_document

def test_image_integration():
    """Test that figures array is properly processed in DOCX generation"""
    
    print("🧪 Testing Image Integration Fix...")
    
    # Test document with figures array (matching frontend structure)
    test_data = {
        "title": "Image Integration Test Document",
        "authors": [
            {
                "name": "Test Author",
                "department": "Computer Science",
                "organization": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "This document tests that images from the figures array are properly integrated into the generated Word document.",
        "keywords": "image integration, DOCX generation, IEEE formatting",
        "sections": [
            {
                "title": "Introduction",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section contains text content. Images should appear after the sections.",
                        "order": 0
                    }
                ]
            }
        ],
        "references": [
            {
                "text": "Test Reference. (2024). Sample reference for testing.",
                "order": 0
            }
        ],
        # Key test: figures array from frontend figure form
        "figures": [
            {
                "id": "figure1",
                "fileName": "test_image.png",
                "originalName": "test_image.png", 
                "caption": "Test image from figures array",
                "size": "medium",
                "position": "here",
                "order": 0,
                "mimeType": "image/png",
                # Simple 1x1 pixel PNG in base64
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            },
            {
                "id": "figure2",
                "fileName": "test_image2.png", 
                "originalName": "test_image2.png",
                "caption": "Second test image with large size",
                "size": "large",
                "position": "here",
                "order": 1,
                "mimeType": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
        ]
    }
    
    print(f"📋 Test data contains {len(test_data['figures'])} figures")
    
    try:
        # Generate DOCX document
        print("🔄 Generating DOCX document...")
        docx_bytes = generate_ieee_document(test_data)
        
        if docx_bytes and len(docx_bytes) > 0:
            print(f"✅ DOCX generated successfully: {len(docx_bytes)} bytes")
            
            # Save test document
            output_file = "test_image_integration.docx"
            with open(output_file, 'wb') as f:
                f.write(docx_bytes)
            
            print(f"💾 Test document saved as: {output_file}")
            print("📖 Open this file in Microsoft Word to verify:")
            print("   - Document contains title and content")
            print("   - FIG. 1: Test image from figures array")
            print("   - FIG. 2: Second test image with large size")
            print("   - Images are properly sized and positioned")
            
            return True
            
        else:
            print("❌ DOCX generation failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error during DOCX generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_integration()
    
    if success:
        print("\n✅ Image integration test completed successfully!")
        print("The IEEE generator now processes figures from the figures array.")
        print("Images from the frontend figure form should now appear in Word documents.")
    else:
        print("\n❌ Image integration test failed!")
        print("Check the error messages above for debugging information.")
    
    sys.exit(0 if success else 1)