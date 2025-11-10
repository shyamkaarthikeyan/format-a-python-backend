print("🚀 Starting simple test...")

try:
    from ieee_generator_fixed import build_document_model, render_to_html
    print("✅ Imports successful")
    
    # Simple test data
    test_data = {
        "title": "Test",
        "authors": [],
        "sections": [{
            "title": "Test Section",
            "contentBlocks": [{
                "type": "table",
                "tableType": "interactive",
                "headers": ["A", "B"],
                "tableData": [["1", "2"]]
            }]
        }]
    }
    
    print("📋 Building model...")
    model = build_document_model(test_data)
    print(f"✅ Model built: {len(model)} keys")
    
    print("🌐 Rendering HTML...")
    html = render_to_html(model)
    print(f"✅ HTML rendered: {len(html)} characters")
    
    # Check for table content
    if '<table class="ieee-table">' in html:
        print("✅ Table found in HTML!")
        # Count table elements
        table_count = html.count('<table class="ieee-table">')
        header_count = html.count('<th class="ieee-table-header">')
        cell_count = html.count('<td class="ieee-table-cell">')
        print(f"   Tables: {table_count}, Headers: {header_count}, Cells: {cell_count}")
    else:
        print("❌ No table found in HTML")
    
    # Save HTML for inspection
    with open("simple_test_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("📁 HTML saved to simple_test_output.html")
    
    print("🎉 Test completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()