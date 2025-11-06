#!/usr/bin/env python3
"""
Test the import of ieee_generator_fixed
"""

import sys
import os

# Add the current directory to Python path (same as in document-generator.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from ieee_generator_fixed import generate_ieee_document
    print("✅ Successfully imported generate_ieee_document")
    
    # Test with minimal data
    test_data = {
        "title": "Test Document",
        "authors": [{"name": "Test Author"}],
        "abstract": "Test abstract",
        "sections": [{"title": "Introduction", "content": "Test content"}]
    }
    
    try:
        result = generate_ieee_document(test_data)
        print("✅ Successfully generated document")
        print(f"Document type: {type(result)}")
        if hasattr(result, 'seek'):
            result.seek(0, 2)  # Seek to end
            size = result.tell()
            print(f"Document size: {size} bytes")
        else:
            print(f"Document length: {len(result) if hasattr(result, '__len__') else 'unknown'}")
    except Exception as e:
        print(f"❌ Document generation failed: {e}")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Current directory:", current_dir)
    print("Files in current directory:")
    for f in os.listdir(current_dir):
        print(f"  {f}")