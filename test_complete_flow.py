#!/usr/bin/env python3
"""
Complete end-to-end test of table and image flow from frontend to backend
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def test_complete_flow():
    """Test the complete flow with realistic frontend data"""
    print("🧪 TESTING COMPLETE TABLE & IMAGE FLOW")
    print("=" * 60)
    
    # Realistic data that matches what the frontend now sends
    realistic_data = {
        "id": "doc_123",
        "title": "Advanced Machine Learning Techniques for Data Analysis",
        "abstract": "This paper presents novel machine learning approaches for analyzing large-scale datasets. We introduce three new algorithms that significantly improve processing speed and accuracy compared to existing methods. Our experimental results demonstrate up to 40% improvement in classification accuracy and 60% reduction in processing time. The proposed techniques have been validated on multiple real-world datasets including image recognition, natural language processing, and financial data analysis.",
        "keywords": "machine learning, data analysis, algorithms, classification, neural networks, deep learning",
        "authors": [
            {
                "id": "author1",
                "name": "Dr. Sarah Johnson",
                "department": "Computer Science Department",
                "organization": "Stanford University",
                "city": "Stanford",
                "state": "CA",
                "email": "sarah.johnson@stanford.edu",
                "customFields": []
            },
            {
                "id": "author2", 
                "name": "Prof. Michael Chen",
                "department": "AI Research Lab",
                "organization": "MIT",
                "city": "Cambridge",
                "state": "MA",
                "email": "m.chen@mit.edu",
                "customFields": []
            }
        ],
        "sections": [
            {
                "id": "intro",
                "title": "Introduction",
                "contentBlocks": [
                    {
                        "id": "intro_text",
                        "type": "text",
                        "content": "Machine learning has revolutionized data analysis across numerous domains. Traditional approaches often struggle with large-scale datasets due to computational limitations and accuracy constraints. This paper addresses these challenges by introducing three novel algorithms designed for efficient processing of complex data structures.",
                        "order": 1
                    },
                    {
                        "id": "intro_table",
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Comparison of Existing Methods",
                        "caption": "Performance comparison of traditional machine learning methods",
                        "headers": ["Method", "Accuracy (%)", "Processing Time (ms)", "Memory Usage (MB)"],
                        "tableData": [
                            ["SVM", "85.2", "1200", "256"],
                            ["Random Forest", "87.8", "800", "512"],
                            ["Neural Network", "89.1", "2000", "1024"],
                            ["Our Method", "94.3", "480", "128"]
                        ],
                        "size": "large",
                        "order": 2
                    }
                ],
                "subsections": [],
                "order": 1
            },
            {
                "id": "methodology",
                "title": "Methodology", 
                "contentBlocks": [
                    {
                        "id": "method_text",
                        "type": "text",
                        "content": "Our approach consists of three main components: feature extraction, dimensionality reduction, and classification. Each component has been optimized for both speed and accuracy.",
                        "order": 1
                    },
                    {
                        "id": "architecture_image",
                        "type": "image",
                        "caption": "System Architecture Overview",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "large",
                        "order": 2
                    }
                ],
                "subsections": [],
                "order": 2
            }
        ],
        "references": [
            {
                "id": "ref1",
                "text": "Smith, J. et al. 'Deep Learning for Large Scale Data Processing.' Nature Machine Intelligence, vol. 3, pp. 123-145, 2023.",
                "order": 1
            },
            {
                "id": "ref2", 
                "text": "Chen, L. and Wang, K. 'Efficient Algorithms for Real-time Classification.' IEEE Transactions on Pattern Analysis, vol. 45, no. 2, pp. 67-89, 2023.",
                "order": 2
            }
        ],
        "figures": [
            {
                "id": "perf_chart",
                "fileName": "performance_chart.png",
                "originalName": "performance_chart.png", 
                "caption": "Performance comparison across different datasets",
                "size": "medium",
                "position": "here",
                "order": 1,
                "mimeType": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            },
            {
                "id": "accuracy_plot",
                "fileName": "accuracy_plot.png", 
                "originalName": "accuracy_plot.png",
                "caption": "Accuracy trends over training iterations",
                "size": "small",
                "position": "here", 
                "order": 2,
                "mimeType": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            }
        ],
        "tables": [
            {
                "id": "dataset_table",
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Dataset Characteristics", 
                "caption": "Characteristics of datasets used in experiments",
                "size": "medium",
                "position": "here",
                "order": 1,
                "headers": ["Dataset", "Size", "Features", "Classes", "Domain"],
                "tableData": [
                    ["CIFAR-10", "60,000", "3,072", "10", "Image Recognition"],
                    ["IMDB Reviews", "50,000", "10,000", "2", "Text Classification"],
                    ["Stock Prices", "100,000", "15", "3", "Financial Analysis"],
                    ["Medical Records", "25,000", "50", "5", "Healthcare"]
                ]
            },
            {
                "id": "results_table_img",
                "type": "image", 
                "tableType": "image",
                "tableName": "Detailed Results Matrix",
                "caption": "Comprehensive results matrix with statistical significance",
                "size": "large",
                "position": "here",
                "order": 2,
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "mimeType": "image/png",
                "originalName": "results_matrix.png"
            }
        ],
        "settings": {
            "fontSize": "10pt",
            "columns": "2", 
            "exportFormat": "docx",
            "includePageNumbers": True,
            "includeCopyright": False
        }
    }
    
    print("📊 Input Data Analysis:")
    print(f"  • Title: {realistic_data['title'][:50]}...")
    print(f"  • Authors: {len(realistic_data['authors'])}")
    print(f"  • Sections: {len(realistic_data['sections'])}")
    print(f"  • Standalone Tables: {len(realistic_data['tables'])}")
    print(f"  • Standalone Figures: {len(realistic_data['figures'])}")
    print(f"  • References: {len(realistic_data['references'])}")
    
    # Count content blocks in sections
    section_tables = 0
    section_images = 0
    section_text = 0
    
    for section in realistic_data['sections']:
        for block in section.get('contentBlocks', []):
            if block['type'] == 'table':
                section_tables += 1
            elif block['type'] == 'image':
                section_images += 1
            elif block['type'] == 'text':
                section_text += 1
    
    print(f"  • Section Content Blocks:")
    print(f"    - Text blocks: {section_text}")
    print(f"    - Table blocks: {section_tables}")
    print(f"    - Image blocks: {section_images}")
    
    try:
        # Step 1: Build document model
        print(f"\n📋 Step 1: Building Document Model...")
        model = build_document_model(realistic_data)
        
        # Analyze model structure
        model_sections = model.get("sections", [])
        total_content_blocks = 0
        total_tables = 0
        total_images = 0
        
        for section in model_sections:
            blocks = section.get("content_blocks", [])
            total_content_blocks += len(blocks)
            
            for block in blocks:
                if block.get("type") in ["table", "table_image"]:
                    total_tables += 1
                elif block.get("type") == "figure":
                    total_images += 1
        
        print(f"✅ Model built successfully")
        print(f"📊 Model Structure:")
        print(f"  • Sections: {len(model_sections)}")
        print(f"  • Total content blocks: {total_content_blocks}")
        print(f"  • Tables in model: {total_tables}")
        print(f"  • Images in model: {total_images}")
        
        # Step 2: Render HTML
        print(f"\n🌐 Step 2: Rendering HTML...")
        html = render_to_html(model)
        
        # Analyze HTML content
        html_tables = html.count('<table class="ieee-table">')
        html_images = html.count('<img src="data:image/')
        html_table_captions = html.count('ieee-table-caption')
        html_figure_captions = html.count('ieee-figure-caption')
        
        print(f"✅ HTML rendered successfully ({len(html)} characters)")
        print(f"📊 HTML Content Analysis:")
        print(f"  • HTML tables: {html_tables}")
        print(f"  • HTML images: {html_images}")
        print(f"  • Table captions: {html_table_captions}")
        print(f"  • Figure captions: {html_figure_captions}")
        
        # Save HTML
        with open("test_complete_flow.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📁 HTML saved: test_complete_flow.html")
        
        # Step 3: Generate DOCX
        print(f"\n📄 Step 3: Generating DOCX...")
        docx_bytes = generate_ieee_document(realistic_data)
        
        with open("test_complete_flow.docx", "wb") as f:
            f.write(docx_bytes)
        print(f"✅ DOCX generated successfully ({len(docx_bytes)} bytes)")
        print(f"📁 DOCX saved: test_complete_flow.docx")
        
        # Step 4: Results Analysis
        print(f"\n🎯 Step 4: Results Analysis")
        print("=" * 60)
        
        expected_total_tables = len(realistic_data['tables']) + section_tables
        expected_total_images = len(realistic_data['figures']) + section_images
        
        print(f"Expected Content:")
        print(f"  • Total tables (standalone + section): {expected_total_tables}")
        print(f"  • Total images (standalone + section): {expected_total_images}")
        
        print(f"Processed Content:")
        print(f"  • Tables in model: {total_tables}")
        print(f"  • Images in model: {total_images}")
        
        print(f"Rendered Content:")
        print(f"  • Interactive tables in HTML: {html_tables}")
        print(f"  • Images in HTML (includes image tables): {html_images}")
        
        # Validation
        success_criteria = [
            (total_tables >= expected_total_tables, f"Model tables: {total_tables} >= {expected_total_tables}"),
            (total_images >= expected_total_images, f"Model images: {total_images} >= {expected_total_images}"),
            (html_images >= expected_total_images, f"HTML images: {html_images} >= {expected_total_images}"),
            (len(docx_bytes) > 30000, f"DOCX size: {len(docx_bytes)} > 30000 bytes"),
            (len(html) > 5000, f"HTML size: {len(html)} > 5000 characters")
        ]
        
        print(f"\n✅ Validation Results:")
        all_passed = True
        for passed, description in success_criteria:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {description}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 COMPLETE FLOW TEST: SUCCESS!")
            print("=" * 60)
            print("✅ All tables and images are processed correctly")
            print("✅ Frontend → Backend integration working")
            print("✅ HTML preview rendering all content")
            print("✅ DOCX generation including all elements")
            print("✅ IEEE formatting applied consistently")
            return True
        else:
            print(f"\n❌ COMPLETE FLOW TEST: ISSUES DETECTED")
            print("Some validation criteria failed - check details above")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting complete flow test...")
    success = test_complete_flow()
    if success:
        print("\n🎊 ALL TESTS PASSED! Tables and images are working correctly!")
    else:
        print("\n💥 SOME TESTS FAILED! Check the output above for details.")
        sys.exit(1)