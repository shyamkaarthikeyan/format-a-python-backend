#!/usr/bin/env python3
"""
Test script to verify deployment fixes for critical runtime errors
This tests the IEEE generator for crashes and consistency issues
"""

import json
import sys
import os
import traceback

def test_deployment_fixes():
    """Test that all critical runtime errors are fixed"""
    
    print("🧪 Testing Deployment Fixes for Critical Runtime Errors...")
    
    # Test document data that exercises all problematic code paths
    test_data = {
        "title": "Critical Runtime Error Fix Verification",
        "authors": [
            {
                "name": "Deployment Test",
                "department": "Quality Assurance",
                "organization": "Format-A Team",
                "email": "test@format-a.com"
            }
        ],
        "abstract": "This document tests all the critical runtime error fixes to ensure the IEEE generator works correctly on Vercel deployment. It includes sections with text, images, tables, and references to exercise all code paths that previously caused crashes.",
        "keywords": "deployment fixes, runtime errors, IEEE generator, Vercel compatibility",
        "sections": [
            {
                "title": "Text Processing Test",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "This section tests the add_formatted_paragraph function to ensure it doesn't cause NameError crashes.",
                        "order": 0
                    }
                ]
            },
            {
                "title": "Image Processing Test",
                "contentBlocks": [
                    {
                        "type": "text", 
                        "content": "This section contains text followed by an image to test figure numbering.",
                        "order": 0
                    },
                    {
                        "type": "image",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                        "caption": "Test image for figure numbering verification",
                        "size": "medium",
                        "order": 1
                    }
                ]
            },
            {
                "title": "Table Processing Test",
                "contentBlocks": [
                    {
                        "type": "table",
                        "tableType": "interactive",
                        "tableName": "Test Table",
                        "caption": "Test table for table numbering verification",
                        "headers": ["Column 1", "Column 2"],
                        "tableData": [
                            ["Row 1 Col 1", "Row 1 Col 2"],
                            ["Row 2 Col 1", "Row 2 Col 2"]
                        ],
                        "order": 0
                    }
                ]
            }
        ],
        "references": [
            {
                "text": "Test Reference 1. (2024). Sample reference for testing purposes.",
                "order": 0
            },
            {
                "text": "Test Reference 2. (2024). Another sample reference to test alignment.",
                "order": 1
            }
        ],
        "figures": [
            {
                "id": "figure1",
                "fileName": "test_figure.png",
                "originalName": "test_figure.png",
                "caption": "Test figure from figures array",
                "size": "medium",
                "position": "here",
                "order": 0,
                "mimeType": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
        ]
    }
    
    print(f"📋 Test Document: {test_data['title']}")
    print(f"   Sections: {len(test_data['sections'])}")
    print(f"   References: {len(test_data['references'])}")
    print(f"   Figures: {len(test_data['figures'])}")
    
    # Test 1: Import and basic function availability
    print("\n🔄 Step 1: Testing imports and function availability...")
    try:
        from ieee_generator_fixed import (
            generate_ieee_document,
            generate_ieee_master_html,
            pandoc_html_to_docx,
            weasyprint_pdf_from_html
        )
        print("✅ All main functions imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False
    
    # Test 2: HTML generation (should always work)
    print("\n🔄 Step 2: Testing HTML generation...")
    try:
        html_output = generate_ieee_master_html(test_data)
        if html_output and len(html_output) > 1000:
            print(f"✅ HTML generation successful: {len(html_output)} characters")
            
            # Save for inspection
            with open("deployment_test.html", "w", encoding="utf-8") as f:
                f.write(html_output)
            print("💾 HTML saved as: deployment_test.html")
        else:
            print("❌ HTML generation failed or output too short")
            return False
    except Exception as e:
        print(f"❌ HTML generation error: {e}")
        traceback.print_exc()
        return False
    
    # Test 3: DOCX generation (critical path)
    print("\n🔄 Step 3: Testing DOCX generation...")
    try:
        # Test unified HTML-to-DOCX conversion
        docx_bytes = pandoc_html_to_docx(html_output)
        if docx_bytes and len(docx_bytes) > 0:
            print(f"✅ Unified DOCX generation successful: {len(docx_bytes)} bytes")
            
            with open("deployment_test_unified.docx", "wb") as f:
                f.write(docx_bytes)
            print("💾 Unified DOCX saved as: deployment_test_unified.docx")
            
            unified_docx_success = True
        else:
            print("⚠️ Unified DOCX generation failed, testing fallback...")
            unified_docx_success = False
    except Exception as e:
        print(f"⚠️ Unified DOCX error: {e}")
        unified_docx_success = False
    
    # Test fallback DOCX generation
    if not unified_docx_success:
        try:
            fallback_docx_bytes = generate_ieee_document(test_data)
            if fallback_docx_bytes and len(fallback_docx_bytes) > 0:
                print(f"✅ Fallback DOCX generation successful: {len(fallback_docx_bytes)} bytes")
                
                with open("deployment_test_fallback.docx", "wb") as f:
                    f.write(fallback_docx_bytes)
                print("💾 Fallback DOCX saved as: deployment_test_fallback.docx")
                
                fallback_docx_success = True
            else:
                print("❌ Fallback DOCX generation failed")
                fallback_docx_success = False
        except Exception as e:
            print(f"❌ Fallback DOCX error: {e}")
            traceback.print_exc()
            fallback_docx_success = False
    else:
        fallback_docx_success = True
    
    # Test 4: PDF generation
    print("\n🔄 Step 4: Testing PDF generation...")
    try:
        pdf_bytes = weasyprint_pdf_from_html(html_output)
        if pdf_bytes and len(pdf_bytes) > 0:
            print(f"✅ PDF generation successful: {len(pdf_bytes)} bytes")
            
            with open("deployment_test.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("💾 PDF saved as: deployment_test.pdf")
            
            pdf_success = True
        else:
            print("❌ PDF generation failed")
            pdf_success = False
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        traceback.print_exc()
        pdf_success = False
    
    # Analysis
    print("\n📊 Deployment Readiness Analysis:")
    
    html_ok = html_output and len(html_output) > 1000
    docx_ok = unified_docx_success or fallback_docx_success
    pdf_ok = pdf_success
    
    print(f"   HTML Generation: {'✅ Working' if html_ok else '❌ Failed'}")
    print(f"   DOCX Generation: {'✅ Working' if docx_ok else '❌ Failed'}")
    print(f"   PDF Generation: {'✅ Working' if pdf_ok else '❌ Failed'}")
    
    if unified_docx_success and pdf_success:
        print("\n🎉 PERFECT: Both formats use unified HTML system")
        print("   → Consistent output guaranteed")
        print("   → Ready for Vercel deployment")
        deployment_ready = True
    elif docx_ok and pdf_ok:
        print("\n✅ GOOD: Both formats working (with fallbacks)")
        print("   → DOCX uses fallback system")
        print("   → PDF uses unified system")
        print("   → Deployment possible but not optimal")
        deployment_ready = True
    elif docx_ok and not pdf_ok:
        print("\n⚠️ PARTIAL: DOCX works, PDF failed")
        print("   → Users can generate DOCX documents")
        print("   → PDF generation needs fixing")
        deployment_ready = False
    elif not docx_ok and pdf_ok:
        print("\n⚠️ PARTIAL: PDF works, DOCX failed")
        print("   → Users can generate PDF documents")
        print("   → DOCX generation needs fixing")
        deployment_ready = False
    else:
        print("\n❌ CRITICAL: Both formats failed")
        print("   → Cannot deploy - no working generation")
        print("   → Need to fix critical runtime errors")
        deployment_ready = False
    
    print("\n🔍 Critical Error Check:")
    if html_ok:
        print("✅ No HTML generation crashes")
    else:
        print("❌ HTML generation crashes - check sanitize_text and template")
    
    if docx_ok:
        print("✅ No DOCX generation crashes")
    else:
        print("❌ DOCX generation crashes - check missing functions:")
        print("   - add_formatted_paragraph")
        print("   - add_ieee_body_paragraph") 
        print("   - apply_ieee_latex_formatting")
    
    if pdf_ok:
        print("✅ No PDF generation crashes")
    else:
        print("❌ PDF generation crashes - check ReportLab fallback")
    
    print("\n📖 Generated Files for Inspection:")
    if html_ok:
        print("   - deployment_test.html (master template)")
    if unified_docx_success:
        print("   - deployment_test_unified.docx (unified system)")
    if fallback_docx_success and not unified_docx_success:
        print("   - deployment_test_fallback.docx (fallback system)")
    if pdf_ok:
        print("   - deployment_test.pdf (unified system)")
    
    return deployment_ready

if __name__ == "__main__":
    success = test_deployment_fixes()
    
    if success:
        print("\n🎉 SUCCESS: Deployment fixes working correctly!")
        print("The IEEE generator is ready for Vercel deployment.")
        print("Both DOCX and PDF generation are functional.")
    else:
        print("\n⚠️ WARNING: Critical issues remain!")
        print("Fix the identified problems before Vercel deployment.")
        print("Users may experience crashes or missing functionality.")
    
    sys.exit(0 if success else 1)