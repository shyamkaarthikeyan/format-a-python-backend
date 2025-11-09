#!/usr/bin/env python3
"""
Test script to verify unified HTML generation system
This checks if both DOCX and PDF generation use the same HTML template
"""

import json
import sys
import os
from ieee_generator_fixed import (
    generate_ieee_master_html, 
    pandoc_html_to_docx, 
    weasyprint_pdf_from_html,
    generate_ieee_document
)

def test_unified_html_generation():
    """Test that both DOCX and PDF use the same unified HTML system"""
    
    print("🧪 Testing Unified HTML Generation System...")
    
    # Test document data
    test_data = {
        "title": "Unified HTML Generation Test",
        "authors": [
            {
                "name": "Test Author",
                "department": "Computer Science", 
                "organization": "Test University",
                "email": "test@example.com"
            }
        ],
        "abstract": "This document tests the unified HTML generation system to ensure both DOCX and PDF outputs are generated from the same HTML template, resulting in identical formatting and layout. The unified system uses a master HTML template with precise CSS styling that matches IEEE LaTeX specifications, then converts this HTML to both DOCX (via pypandoc) and PDF (via WeasyPrint) formats. This approach ensures perfect visual consistency between the two output formats, eliminating discrepancies in line breaks, justification, spacing, and overall document appearance that would occur if different generation methods were used.",
        "keywords": "unified HTML generation, DOCX-PDF consistency, IEEE formatting, pypandoc, WeasyPrint",
        "sections": [
            {
                "title": "Unified HTML System Overview",
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "The unified HTML generation system creates a single master HTML template with precise CSS styling that matches IEEE LaTeX specifications. This template is then converted to both DOCX and PDF formats using specialized converters, ensuring identical visual output.",
                        "order": 0
                    }
                ]
            },
            {
                "title": "Implementation Details", 
                "contentBlocks": [
                    {
                        "type": "text",
                        "content": "The system uses pypandoc for HTML-to-DOCX conversion and WeasyPrint for HTML-to-PDF conversion. Both converters process the same master HTML template, which includes precise CSS rules for typography, spacing, margins, and layout that match IEEE LaTeX output exactly.",
                        "order": 0
                    }
                ]
            }
        ],
        "references": [
            {
                "text": "IEEE Standards Association. (2021). IEEE Editorial Style Manual. IEEE Press.",
                "order": 0
            }
        ],
        "figures": [
            {
                "id": "figure1",
                "fileName": "test_image.png",
                "originalName": "test_image.png",
                "caption": "Test figure for unified HTML generation",
                "size": "medium",
                "position": "here", 
                "order": 0,
                "mimeType": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
        ]
    }
    
    print(f"📋 Test data: {test_data['title']}")
    print(f"   Authors: {len(test_data['authors'])}")
    print(f"   Sections: {len(test_data['sections'])}")
    print(f"   Figures: {len(test_data['figures'])}")
    
    # Test 1: Generate master HTML template
    print("\n🔄 Step 1: Testing master HTML generation...")
    try:
        master_html = generate_ieee_master_html(test_data)
        if master_html and len(master_html) > 1000:  # Should be substantial
            print(f"✅ Master HTML generated: {len(master_html)} characters")
            
            # Save HTML for inspection
            with open("test_unified_generation.html", "w", encoding="utf-8") as f:
                f.write(master_html)
            print("💾 HTML saved as: test_unified_generation.html")
        else:
            print("❌ Master HTML generation failed or too short")
            return False
    except Exception as e:
        print(f"❌ Master HTML generation error: {e}")
        return False
    
    # Test 2: Test pypandoc HTML-to-DOCX conversion
    print("\n🔄 Step 2: Testing pypandoc HTML-to-DOCX conversion...")
    try:
        docx_bytes = pandoc_html_to_docx(master_html)
        if docx_bytes and len(docx_bytes) > 0:
            print(f"✅ Pypandoc DOCX conversion succeeded: {len(docx_bytes)} bytes")
            
            # Save DOCX for inspection
            with open("test_unified_generation.docx", "wb") as f:
                f.write(docx_bytes)
            print("💾 DOCX saved as: test_unified_generation.docx")
            
            unified_docx_available = True
        else:
            print("⚠️ Pypandoc DOCX conversion failed - will use fallback")
            unified_docx_available = False
    except Exception as e:
        print(f"⚠️ Pypandoc error: {e}")
        unified_docx_available = False
    
    # Test 3: Test WeasyPrint HTML-to-PDF conversion
    print("\n🔄 Step 3: Testing WeasyPrint HTML-to-PDF conversion...")
    try:
        pdf_bytes = weasyprint_pdf_from_html(master_html)
        if pdf_bytes and len(pdf_bytes) > 0:
            print(f"✅ WeasyPrint PDF conversion succeeded: {len(pdf_bytes)} bytes")
            
            # Save PDF for inspection
            with open("test_unified_generation.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("💾 PDF saved as: test_unified_generation.pdf")
            
            unified_pdf_available = True
        else:
            print("❌ WeasyPrint PDF conversion failed")
            unified_pdf_available = False
    except Exception as e:
        print(f"❌ WeasyPrint error: {e}")
        unified_pdf_available = False
    
    # Test 4: Test fallback DOCX generation (old system)
    print("\n🔄 Step 4: Testing fallback DOCX generation...")
    try:
        fallback_docx_bytes = generate_ieee_document(test_data)
        if fallback_docx_bytes and len(fallback_docx_bytes) > 0:
            print(f"✅ Fallback DOCX generation succeeded: {len(fallback_docx_bytes)} bytes")
            
            # Save fallback DOCX for comparison
            with open("test_fallback_generation.docx", "wb") as f:
                f.write(fallback_docx_bytes)
            print("💾 Fallback DOCX saved as: test_fallback_generation.docx")
            
            fallback_docx_available = True
        else:
            print("❌ Fallback DOCX generation failed")
            fallback_docx_available = False
    except Exception as e:
        print(f"❌ Fallback DOCX error: {e}")
        fallback_docx_available = False
    
    # Analysis and recommendations
    print("\n📊 Analysis Results:")
    print(f"   Master HTML generation: {'✅ Working' if master_html else '❌ Failed'}")
    print(f"   Pypandoc DOCX (unified): {'✅ Working' if unified_docx_available else '❌ Failed'}")
    print(f"   WeasyPrint PDF (unified): {'✅ Working' if unified_pdf_available else '❌ Failed'}")
    print(f"   Fallback DOCX (old): {'✅ Working' if fallback_docx_available else '❌ Failed'}")
    
    print("\n🎯 Consistency Analysis:")
    if unified_docx_available and unified_pdf_available:
        print("✅ PERFECT: Both DOCX and PDF use unified HTML system")
        print("   → Output should be identical between formats")
        print("   → This is the ideal state for Vercel deployment")
    elif not unified_docx_available and unified_pdf_available:
        print("⚠️ INCONSISTENT: PDF uses unified HTML, DOCX uses fallback")
        print("   → This explains why Word and PDF outputs differ")
        print("   → DOCX falls back to old OpenXML system")
        print("   → PDF uses new unified HTML system")
        print("   → Need to fix pypandoc availability on Vercel")
    elif unified_docx_available and not unified_pdf_available:
        print("⚠️ INCONSISTENT: DOCX uses unified HTML, PDF fails")
        print("   → Need to fix WeasyPrint availability")
    else:
        print("❌ CRITICAL: Both unified systems failed")
        print("   → Both formats will use different fallback methods")
        print("   → Need to fix both pypandoc and WeasyPrint")
    
    print("\n🚀 Recommendations for Vercel:")
    if not unified_docx_available:
        print("1. 🔧 Install pypandoc in Vercel environment")
        print("   - Add pypandoc to requirements.txt")
        print("   - Ensure pandoc binary is available")
        print("   - Test pypandoc import and conversion")
    
    if not unified_pdf_available:
        print("2. 🔧 Install WeasyPrint in Vercel environment")
        print("   - Add weasyprint to requirements.txt")
        print("   - Ensure system dependencies are available")
        print("   - Test WeasyPrint import and conversion")
    
    if unified_docx_available and unified_pdf_available:
        print("✅ System is properly configured for consistent output!")
    
    print("\n📖 Testing Instructions:")
    print("1. Check generated files:")
    print("   - test_unified_generation.html (master template)")
    if unified_docx_available:
        print("   - test_unified_generation.docx (unified system)")
    if fallback_docx_available:
        print("   - test_fallback_generation.docx (old system)")
    if unified_pdf_available:
        print("   - test_unified_generation.pdf (unified system)")
    
    print("2. Compare documents visually:")
    print("   - Open all generated files")
    print("   - Check line breaks, spacing, and formatting")
    print("   - Verify identical appearance between unified outputs")
    
    return unified_docx_available and unified_pdf_available

if __name__ == "__main__":
    success = test_unified_html_generation()
    
    if success:
        print("\n✅ Unified HTML generation system is working correctly!")
        print("Both DOCX and PDF should have identical formatting.")
    else:
        print("\n⚠️ Unified HTML generation system has issues!")
        print("This explains why DOCX and PDF outputs differ.")
    
    sys.exit(0 if success else 1)