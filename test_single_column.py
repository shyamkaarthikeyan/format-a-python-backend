#!/usr/bin/env python3
"""
Test script with single-column layout to check if two-column layout is causing visibility issues.
"""

import base64
import json
import sys
from ieee_generator_fixed import generate_ieee_document

# Monkey patch to disable two-column layout temporarily
def disabled_two_column_layout(doc):
    """Disabled two-column layout for testing."""
    print("Two-column layout disabled for testing", file=sys.stderr)
    pass

# Replace the function
import ieee_generator_fixed
ieee_generator_fixed.setup_two_column_layout = disabled_two_column_layout

def create_test_data():
    """Create test data to check visibility without two-column layout."""
    
    # Create a simple base64 image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    test_data = {
        "title": "Single Column Test: Table and Image Visibility",
        "authors": [
            {
                "name": "Test Author",
                "affiliation": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "Testing table and image visibility in single-column layout.",
        "keywords": "testing, single-column, tables, images",
        "sections": [
            {
                "title": "Test Section",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This is text before the table."
                    },
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "caption": "Test Table in Single Column",
                        "headers": ["Header A", "Header B", "Header C"],
                        "tableData": [
                            ["Row 1 A", "Row 1 B", "Row 1 C"],
                            ["Row 2 A", "Row 2 B", "Row 2 C"],
                            ["Row 3 A", "Row 3 B", "Row 3 C"]
                        ]
                    },
                    {
                        "type": "text",
                        "content": "This is text between table and image."
                    },
                    {
                        "type": "image",
                        "data": f"data:image/png;base64,{test_image_b64}",
                        "caption": "Test Image in Single Column",
                        "size": "medium"
                    },
                    {
                        "type": "text",
                        "content": "This is text after the image."
                    }
                ]
            }
        ],
        "references": []
    }
    
    return test_data

def main():
    """Run the single-column test."""
    print("=== SINGLE COLUMN TEST ===")
    test_data = create_test_data()
    
    print("Generating document with single-column layout...")
    try:
        doc_bytes = generate_ieee_document(test_data)
        
        output_file = "test_single_column_output.docx"
        with open(output_file, "wb") as f:
            f.write(doc_bytes)
        
        print(f"✅ Single-column document generated: {output_file}")
        print("\n=== Check this document ===")
        print("1. Is the table visible after TABLE 1.1 caption?")
        print("2. Is the image fully visible after FIG. 1.1 caption?")
        print("3. Are all elements in the correct order?")
        print("\nIf tables and images are visible in single-column but not in two-column,")
        print("then the two-column layout is causing the visibility issues.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())