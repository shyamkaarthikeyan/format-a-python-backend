#!/usr/bin/env python3
"""
Test script to verify table and image ordering and visibility fixes.
"""

import base64
import json
import sys
from ieee_generator_fixed import generate_ieee_document

def create_test_data():
    """Create test data with tables and images to test ordering and visibility."""
    
    # Create a simple base64 image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    test_data = {
        "title": "Test Document: Table and Image Ordering",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "This document tests the ordering and visibility of tables and images in IEEE format.",
        "keywords": "testing, tables, images, ordering, visibility",
        "sections": [
            {
                "title": "Introduction",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section contains text followed by a table and then an image to test proper ordering."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "caption": "Sample Data Table",
                        "tableName": "Test Table 1",
                        "headers": ["Column A", "Column B", "Column C"],
                        "tableData": [
                            ["Row 1 A", "Row 1 B", "Row 1 C"],
                            ["Row 2 A", "Row 2 B", "Row 2 C"],
                            ["Row 3 A", "Row 3 B", "Row 3 C"]
                        ]
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the table and before the image."
                    },
                    {
                        "type": "image",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "caption": "Test Image Caption",
                        "size": "medium"
                    },
                    {
                        "type": "text",
                        "content": "This text should appear after the image."
                    }
                ]
            },
            {
                "title": "Results",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section tests multiple tables and images in sequence."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "caption": "Results Table One",
                        "headers": ["Parameter", "Value", "Unit"],
                        "tableData": [
                            ["Temperature", "25.5", "°C"],
                            ["Pressure", "101.3", "kPa"],
                            ["Humidity", "65", "%"]
                        ]
                    },
                    {
                        "type": "table",
                        "tableType": "interactive", 
                        "caption": "Results Table Two",
                        "headers": ["Test", "Result", "Status"],
                        "tableData": [
                            ["Test A", "Pass", "OK"],
                            ["Test B", "Pass", "OK"],
                            ["Test C", "Fail", "Error"]
                        ]
                    },
                    {
                        "type": "image",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "caption": "Results Chart",
                        "size": "large"
                    },
                    {
                        "type": "image",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "caption": "Comparison Graph", 
                        "size": "small"
                    }
                ]
            }
        ],
        "references": [
            "Test Reference 1: Sample citation for testing purposes.",
            "Test Reference 2: Another sample citation to verify reference formatting."
        ]
    }
    
    return test_data

def main():
    """Run the test and generate the document."""
    print("Creating test data...")
    test_data = create_test_data()
    
    print("Generating IEEE document...")
    try:
        # Generate the document
        doc_bytes = generate_ieee_document(test_data)
        
        # Save to file
        output_file = "test_ordering_visibility_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Document generated successfully: {output_file}")
        print("\nExpected order in document:")
        print("1. Title and authors")
        print("2. Abstract and keywords")
        print("3. Section 1: Introduction")
        print("   - Text paragraph")
        print("   - TABLE 1.1: Sample Data Table (with table content)")
        print("   - Text paragraph")
        print("   - FIG. 1.1: Test Image Caption (with image)")
        print("   - Text paragraph")
        print("4. Section 2: Results")
        print("   - Text paragraph")
        print("   - TABLE 2.1: Results Table One (with table content)")
        print("   - TABLE 2.2: Results Table Two (with table content)")
        print("   - FIG. 2.1: Results Chart (with image)")
        print("   - FIG. 2.2: Comparison Graph (with image)")
        print("5. References")
        print("\n📋 Please check the generated document to verify:")
        print("   ✓ Tables appear immediately after their captions")
        print("   ✓ Images are fully visible (not half-hidden)")
        print("   ✓ Content appears in the correct order")
        print("   ✓ No duplicate captions")
        
    except Exception as e:
        print(f"❌ Error generating document: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())