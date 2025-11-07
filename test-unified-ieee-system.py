#!/usr/bin/env python3
"""
Test the new unified ieee_generator_fixed.py system for both DOCX and HTML preview
"""

import sys
import os
import json

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from ieee_generator_fixed import generate_ieee_document, generate_ieee_html_preview
    print("✅ Successfully imported ieee_generator_fixed.py functions")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_ieee_system():
    """Test both DOCX and HTML generation using ieee_generator_fixed.py"""
    
    # Test data
    test_data = {
        "title": "Advanced Machine Learning Techniques for Real-Time Data Processing",
        "authors": [
            {
                "name": "Dr. John Smith",
                "email": "john.smith@university.edu",
                "affiliation": "Department of Computer Science, Tech University"
            },
            {
                "name": "Prof. Jane Doe", 
                "email": "jane.doe@research.org",
                "affiliation": "AI Research Institute"
            },
            {
                "name": "Dr. Mike Johnson",
                "email": "mike.johnson@corp.com", 
                "affiliation": "Corporate Research Lab"
            }
        ],
        "abstract": "This paper presents novel machine learning techniques for processing large-scale real-time data streams. We introduce a hybrid approach combining deep neural networks with traditional statistical methods to achieve superior performance in dynamic environments.",
        "keywords": "machine learning, real-time processing, data streams, neural networks",
        "sections": [
            {
                "title": "Introduction",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "Real-time data processing has become increasingly important in modern applications. This section introduces the fundamental concepts and challenges in this domain."
                    }
                ]
            },
            {
                "title": "Methodology", 
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "Our approach combines deep learning techniques with traditional statistical methods to achieve optimal performance in real-time scenarios."
                    }
                ]
            }
        ],
        "references": [
            {
                "text": "Smith, J., Doe, J., and Johnson, M. (2023). 'Advanced ML Techniques,' IEEE Transactions on Neural Networks, vol. 34, no. 2, pp. 123-145."
            }
        ]
    }
    
    print("\n🧪 Testing IEEE Generator Fixed System")
    print("=" * 50)
    
    # Test 1: HTML Preview Generation
    print("\n1️⃣ Testing HTML Preview Generation...")
    try:
        html_content = generate_ieee_html_preview(test_data)
        print(f"✅ HTML Preview Generated: {len(html_content)} characters")
        
        # Save to file for inspection
        with open('test_preview_output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("💾 HTML preview saved to: test_preview_output.html")
        
        # Check if HTML contains expected IEEE elements
        html_lower = html_content.lower()
        ieee_elements = [
            'ieee-title',
            'ieee-authors', 
            'abstract',
            'index terms',
            'introduction',
            'methodology',
            'references'
        ]
        
        found_elements = [elem for elem in ieee_elements if elem in html_lower]
        print(f"🔍 IEEE Elements Found: {len(found_elements)}/{len(ieee_elements)}")
        print(f"   Elements: {', '.join(found_elements)}")
        
        if len(found_elements) >= 5:
            print("✅ HTML Preview: PASS - Contains proper IEEE formatting")
            html_test_result = True
        else:
            print("⚠️  HTML Preview: PARTIAL - Some IEEE elements missing")
            html_test_result = False
            
    except Exception as e:
        print(f"❌ HTML Preview Generation Failed: {e}")
        html_test_result = False
    
    # Test 2: DOCX Document Generation
    print("\n2️⃣ Testing DOCX Document Generation...")
    try:
        docx_data = generate_ieee_document(test_data)
        print(f"✅ DOCX Document Generated: {len(docx_data)} bytes")
        
        # Save to file for inspection
        with open('test_document_output.docx', 'wb') as f:
            f.write(docx_data)
        print("💾 DOCX document saved to: test_document_output.docx")
        
        if len(docx_data) > 10000:  # Reasonable size check
            print("✅ DOCX Generation: PASS - Document has reasonable size")
            docx_test_result = True
        else:
            print("⚠️  DOCX Generation: PARTIAL - Document may be incomplete")
            docx_test_result = False
            
    except Exception as e:
        print(f"❌ DOCX Document Generation Failed: {e}")
        docx_test_result = False
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"HTML Preview Generation: {'✅ PASS' if html_test_result else '❌ FAIL'}")
    print(f"DOCX Document Generation: {'✅ PASS' if docx_test_result else '❌ FAIL'}")
    
    if html_test_result and docx_test_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("ieee_generator_fixed.py is working correctly for both preview and document generation")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Please check the error messages above")
        return False

if __name__ == "__main__":
    success = test_ieee_system()
    sys.exit(0 if success else 1)
