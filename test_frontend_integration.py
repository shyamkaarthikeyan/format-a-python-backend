#!/usr/bin/env python3
"""
Test script to verify frontend integration with all content types
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ieee_generator_fixed import build_document_model, render_to_html, generate_ieee_document

def test_frontend_integration():
    """Test all content types as they would come from the frontend"""
    print("🧪 TESTING FRONTEND INTEGRATION - ALL CONTENT TYPES")
    print("=" * 60)
    
    # Create test data that matches frontend structure
    test_data = {
        "title": "Frontend Integration Test Document",
        "authors": [
            {"name": "Frontend User", "department": "Computer Science", "email": "user@university.edu"}
        ],
        "abstract": "This document tests all content types from the frontend interface.",
        "keywords": "frontend, integration, tables, images, equations, subsections",
        "sections": [
            {
                "id": "section1",
                "title": "Interactive Content Types",
                "contentBlocks": [
                    {
                        "id": "text1",
                        "type": "text",
                        "content": "This section demonstrates all interactive content types available in the frontend.",
                        "order": 1
                    },
                    {
                        "id": "table1",
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Performance Data",
                        "caption": "System performance comparison across different algorithms",
                        "headers": ["Algorithm", "Speed (ms)", "Accuracy (%)", "Memory (MB)"],
                        "tableData": [
                            ["Algorithm A", "150", "95.2", "128"],
                            ["Algorithm B", "200", "97.8", "256"],
                            ["Algorithm C", "120", "93.1", "64"],
                            ["Algorithm D", "180", "96.5", "192"]
                        ],
                        "size": "large",
                        "rows": 4,
                        "columns": 4,
                        "order": 2
                    },
                    {
                        "id": "image1",
                        "type": "image",
                        "caption": "System Architecture Diagram",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "large",
                        "originalName": "architecture.png",
                        "mimeType": "image/png",
                        "order": 3
                    },
                    {
                        "id": "equation1",
                        "type": "equation",
                        "content": "E = mc²",
                        "equationNumber": "1",
                        "order": 4
                    },
                    {
                        "id": "subsection1",
                        "type": "subsection",
                        "title": "Implementation Details",
                        "content": "This subsection provides detailed implementation information for the proposed system.",
                        "order": 5
                    },
                    {
                        "id": "equation2",
                        "type": "equation",
                        "content": "F = ma",
                        "equationNumber": "2",
                        "order": 6
                    }
                ],
                "order": 1
            },
            {
                "id": "section2",
                "title": "Advanced Content Types",
                "contentBlocks": [
                    {
                        "id": "text2",
                        "type": "text",
                        "content": "This section demonstrates more advanced content combinations.",
                        "order": 1
                    },
                    {
                        "id": "table2",
                        "type": "table",
                        "tableType": "image",
                        "tableName": "Image Table",
                        "caption": "Visual representation of data",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "size": "medium",
                        "originalName": "table_image.png",
                        "mimeType": "image/png",
                        "order": 2
                    },
                    {
                        "id": "subsection2",
                        "type": "subsection",
                        "title": "Results Analysis",
                        "content": "The results show significant improvements in performance metrics.",
                        "order": 3
                    },
                    {
                        "id": "equation3",
                        "type": "equation",
                        "content": "∫₀^∞ e^(-x²) dx = √π/2",
                        "equationNumber": "3",
                        "order": 4
                    }
                ],
                "order": 2
            }
        ],
        "references": [
            {"id": "ref1", "text": "Smith, J. et al. 'Advanced Document Generation.' IEEE Transactions, 2023.", "order": 1},
            {"id": "ref2", "text": "Johnson, A. 'Frontend Integration Patterns.' ACM Computing Surveys, 2023.", "order": 2}
        ],
        # Test standalone tables and figures (as they come from frontend forms)
        "tables": [
            {
                "id": "standalone_table1",
                "type": "interactive",
                "tableType": "interactive",
                "tableName": "Standalone Performance Table",
                "caption": "This table was created using the table form interface",
                "headers": ["Metric", "Value", "Unit", "Status"],
                "tableData": [
                    ["CPU Usage", "45", "%", "Normal"],
                    ["Memory Usage", "2.1", "GB", "Normal"],
                    ["Disk I/O", "120", "MB/s", "High"],
                    ["Network", "50", "Mbps", "Normal"]
                ],
                "size": "medium",
                "rows": 4,
                "columns": 4,
                "order": 1
            }
        ],
        "figures": [
            {
                "id": "standalone_fig1",
                "caption": "Standalone Performance Graph",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "size": "large",
                "originalName": "performance_graph.png",
                "mimeType": "image/png",
                "order": 1
            }
        ]
    }
    
    try:
        print("📋 Building document model...")
        model = build_document_model(test_data)
        
        print("📊 Analyzing model structure:")
        sections = model.get("sections", [])
        
        total_content_blocks = 0
        total_tables = 0
        total_images = 0
        total_equations = 0
        total_subsections = 0
        
        for i, section in enumerate(sections):
            content_blocks = section.get("content_blocks", [])
            total_content_blocks += len(content_blocks)
            
            print(f"  Section {i+1}: '{section.get('title', 'Untitled')}'")
            print(f"    - Content blocks: {len(content_blocks)}")
            
            for j, block in enumerate(content_blocks):
                block_type = block.get("type", "unknown")
                print(f"      Block {j+1}: {block_type}")
                
                if block_type in ["table", "table_image"]:
                    total_tables += 1
                    print(f"        - Table type: {block.get('table_type', 'not set')}")
                    if block.get('headers'):
                        print(f"        - Headers: {len(block['headers'])} columns")
                    if block.get('caption', {}).get('text'):
                        caption_text = block['caption']['text'][:50]
                        print(f"        - Caption: {caption_text}{'...' if len(caption_text) > 50 else ''}")
                elif block_type == "figure":
                    total_images += 1
                    if block.get('caption', {}).get('text'):
                        caption_text = block['caption']['text'][:50]
                        print(f"        - Caption: {caption_text}{'...' if len(caption_text) > 50 else ''}")
                elif block_type == "equation":
                    total_equations += 1
                    content = block.get("content", "")[:30]
                    print(f"        - Content: {content}{'...' if len(content) > 30 else ''}")
                    if block.get("number"):
                        print(f"        - Number: {block['number']}")
                elif block_type == "paragraph":
                    content = block.get("text", "")[:50]
                    print(f"        - Text: {content}{'...' if len(content) > 50 else ''}")
        
        print(f"\n📊 Model Summary:")
        print(f"  • Total content blocks: {total_content_blocks}")
        print(f"  • Tables: {total_tables}")
        print(f"  • Images: {total_images}")
        print(f"  • Equations: {total_equations}")
        print(f"  • Subsections: {total_subsections}")
        
        print("\n🌐 Rendering to HTML...")
        html = render_to_html(model)
        
        # Count different elements in HTML
        html_table_count = html.count('<table')
        html_image_count = html.count('<img')
        html_equation_count = html.count('ieee-equation')
        
        print(f"📊 HTML Analysis:")
        print(f"  • HTML tables: {html_table_count}")
        print(f"  • HTML images: {html_image_count}")
        print(f"  • HTML equations: {html_equation_count}")
        print(f"  • HTML length: {len(html)} characters")
        
        # Save HTML for inspection
        html_file = "test_frontend_integration.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"📁 HTML saved: {html_file}")
        
        print("\n📄 Generating DOCX...")
        docx_bytes = generate_ieee_document(test_data)
        
        docx_file = "test_frontend_integration.docx"
        with open(docx_file, 'wb') as f:
            f.write(docx_bytes)
        print(f"📁 DOCX saved: {docx_file} ({len(docx_bytes)} bytes)")
        
        print(f"\n🎉 FRONTEND INTEGRATION TEST COMPLETE!")
        print("=" * 60)
        print("Generated files:")
        print(f"  • {html_file} - HTML preview")
        print(f"  • {docx_file} - Word document")
        
        print(f"\n📊 Results Summary:")
        print(f"  • Content blocks processed: {total_content_blocks}")
        print(f"  • Tables in model: {total_tables}")
        print(f"  • Images in model: {total_images}")
        print(f"  • Equations in model: {total_equations}")
        print(f"  • HTML tables rendered: {html_table_count}")
        print(f"  • HTML images rendered: {html_image_count}")
        print(f"  • HTML equations rendered: {html_equation_count}")
        
        # Check for consistency
        success = True
        if total_tables != html_table_count:
            print(f"⚠️  WARNING: Table count mismatch - Model: {total_tables}, HTML: {html_table_count}")
            success = False
        if total_images != html_image_count:
            print(f"⚠️  WARNING: Image count mismatch - Model: {total_images}, HTML: {html_image_count}")
            success = False
        if total_equations != html_equation_count:
            print(f"⚠️  WARNING: Equation count mismatch - Model: {total_equations}, HTML: {html_equation_count}")
            success = False
        
        if success:
            print("✅ SUCCESS: All content types processed correctly!")
        else:
            print("❌ ISSUES: Some content types have mismatches")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting frontend integration test...")
    success = test_frontend_integration()
    if success:
        print("✅ Test completed successfully")
    else:
        print("❌ Test failed")
        sys.exit(1)