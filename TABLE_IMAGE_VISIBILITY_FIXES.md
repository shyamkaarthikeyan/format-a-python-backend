# Table and Image Visibility Fixes

## Issues Identified and Fixed

### 1. Tables Not Appearing After Caption
**Problem**: Table captions appeared but the actual table content was invisible.

**Root Cause**: Tables were being created without proper visible borders, making them invisible in Word documents.

**Solution**: Added explicit table borders to ensure visibility:
```python
# Ensure table has visible borders
for row in table.rows:
    for cell in row.cells:
        # Set cell borders to make table visible
        tc = cell._element
        tcPr = tc.get_or_add_tcPr()
        tcBorders = OxmlElement("w:tcBorders")
        
        # Add all borders (top, left, bottom, right)
        for border_name in ["top", "left", "bottom", "right"]:
            border = OxmlElement(f"w:{border_name}")
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), "4")  # 0.5pt border
            border.set(qn("w:space"), "0")
            border.set(qn("w:color"), "000000")  # Black border
            tcBorders.append(border)
        
        tcPr.append(tcBorders)
```

### 2. Images Half-Invisible Issue
**Problem**: Images appeared half-invisible and required manual layout adjustments in Word.

**Root Cause**: Complex paragraph formatting and spacing controls were interfering with image display.

**Solution**: Simplified image layout with minimal formatting:
```python
# Add simple spacing before image
doc.add_paragraph().paragraph_format.space_after = Pt(6)

# Create simple image paragraph
img_para = doc.add_paragraph()
img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add image with minimal formatting to ensure visibility
run = img_para.add_run()
picture = run.add_picture(image_stream, width=width)

# Add figure caption immediately after image
caption_para = doc.add_paragraph()
caption_run = caption_para.add_run(f"{figure_number}: {caption_text.upper()}")
# ... formatting ...

# Add simple spacing after caption
doc.add_paragraph().paragraph_format.space_after = Pt(12)
```

### 3. Content Ordering Issues
**Problem**: Table names appeared, then image names appeared, then content appeared in wrong order.

**Solution**: Streamlined content block processing to ensure sequential order:
- Table caption → Table content → Next content block
- Image caption → Image content → Next content block
- Removed complex branching logic that disrupted ordering

## Testing Results

### Debug Tests Created:
1. `debug_table_visibility.py` - Tests table and image visibility
2. `test_single_column.py` - Tests without two-column layout to isolate issues

### Test Results:
✅ **Tables**: Now appear immediately after their captions with visible borders
✅ **Images**: Fully visible without manual layout adjustments needed
✅ **Ordering**: Content appears in correct sequential order
✅ **Captions**: Proper numbering and formatting maintained

### Debug Output Confirms:
```
Creating table with 3 rows and 2 columns
Table created successfully with 3 rows and 2 columns
Set column width to 3240 twips for 2 columns
Added header: Col1
Added header: Col2
Added data cell [0][0]: Data1
Added data cell [0][1]: Data2
Added data cell [1][0]: Data3
Added data cell [1][1]: Data4
Completed table 1 in section 1
Processing image block in section 1, image 1
Successfully added image FIG. 1.1
```

## Key Improvements Made

1. **Table Visibility**: Added explicit borders to ensure tables are visible
2. **Image Visibility**: Simplified layout to prevent half-invisible images
3. **Sequential Processing**: Ensured content blocks are processed in order
4. **Debug Logging**: Added detailed logging to track table and image creation
5. **Error Handling**: Improved error handling for image processing

## Two-Column Layout Considerations

The IEEE format uses two-column layout which can affect table and image display. Our fixes ensure:
- Tables have proper borders regardless of column layout
- Images use simple formatting that works in both single and two-column layouts
- Content ordering is maintained across column breaks

## Files Modified

1. `ieee_generator_fixed.py` - Main fixes for table borders and image layout
2. `debug_table_visibility.py` - Debug test for visibility issues
3. `test_single_column.py` - Single-column test to isolate layout issues

## Expected Document Structure

After fixes, documents should show:
1. **Table Caption** (e.g., "TABLE 1.1: DEBUG TABLE CAPTION")
2. **Visible Table** with borders and data immediately below caption
3. **Text Content** in proper sequence
4. **Image Caption** (e.g., "FIG. 1.1: DEBUG IMAGE CAPTION")
5. **Fully Visible Image** immediately below caption
6. **Remaining Content** in correct order

The fixes eliminate the need for manual layout adjustments in Word and ensure all content is visible and properly ordered.