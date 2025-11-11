# Table and Image Ordering & Visibility Fixes

## Issues Fixed

### 1. Table Name and Caption Duplication
**Problem**: Table names appeared, then image names appeared, causing confusion and duplication.

**Solution**: 
- Simplified caption handling in `add_section()` function
- Use single caption source: prefer `caption` over `tableName`
- Add caption immediately before table content
- Removed complex caption duplication logic

### 2. Image Half-Invisible Issue
**Problem**: Images appeared half-invisible due to complex section breaks and OpenXML spacing controls.

**Solution**:
- Simplified image layout in both `add_section()` and `add_ieee_table()` functions
- Removed complex section breaks that caused layout issues
- Used simple paragraph spacing instead of aggressive OpenXML controls
- Removed `keepNext`, `keepLines`, and other complex positioning controls

### 3. Wrong Content Ordering
**Problem**: Tables and images appeared in wrong order due to complex processing logic.

**Solution**:
- Streamlined content block processing in `add_section()` function
- Process content blocks sequentially without complex branching
- Ensure captions appear immediately before their content
- Maintain proper numbering for tables and figures

## Code Changes Made

### 1. Fixed Table Block Processing
```python
# Before: Complex caption duplication logic
# After: Simple, direct caption handling
elif block.get("type") == "table":
    table_count += 1
    caption_text = block.get("caption", "").strip()
    table_name = block.get("tableName", "").strip()
    final_caption = caption_text or table_name or f"Data Table {table_count}"
    
    # Add caption BEFORE table
    caption_para = doc.add_paragraph()
    caption_run = caption_para.add_run(f"TABLE {section_idx}.{table_count}: {sanitize_text(final_caption).upper()}")
    # ... formatting ...
    
    # Add table content immediately after
    add_ieee_table(doc, block, section_idx, table_count)
```

### 2. Simplified Image Handling
```python
# Before: Complex section breaks and OpenXML controls
# After: Simple, reliable image layout
try:
    import base64
    # Decode image data
    image_data = block["data"]
    if "," in image_data:
        image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image_stream = BytesIO(image_bytes)

    # Simple spacing and layout
    spacing_para = doc.add_paragraph()
    spacing_para.paragraph_format.space_before = Pt(12)
    spacing_para.paragraph_format.space_after = Pt(6)

    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # ... add image and caption ...
```

### 3. Fixed Image Table Type
```python
# Before: Complex OpenXML spacing and positioning controls
# After: Simple, reliable image layout matching regular images
elif table_type == "image":
    # Simple spacing before image
    spacing_para = doc.add_paragraph()
    spacing_para.paragraph_format.space_before = Pt(12)
    spacing_para.paragraph_format.space_after = Pt(6)

    # Create image paragraph with center alignment
    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # ... simple image handling ...
```

## Test Results

Created `test_ordering_visibility_fix.py` to verify fixes:

✅ **Tables**: Appear immediately after their captions
✅ **Images**: Fully visible (not half-hidden)  
✅ **Ordering**: Content appears in correct sequential order
✅ **Captions**: No duplicate captions
✅ **Numbering**: Proper table and figure numbering

## Expected Document Structure

1. **Title and Authors**
2. **Abstract and Keywords**
3. **Section 1: Introduction**
   - Text paragraph
   - TABLE 1.1: Sample Data Table (with table content)
   - Text paragraph  
   - FIG. 1.1: Test Image Caption (with image)
   - Text paragraph
4. **Section 2: Results**
   - Text paragraph
   - TABLE 2.1: Results Table One (with table content)
   - TABLE 2.2: Results Table Two (with table content)
   - FIG. 2.1: Results Chart (with image)
   - FIG. 2.2: Comparison Graph (with image)
5. **References**

## Key Improvements

1. **Reliability**: Removed complex OpenXML controls that caused layout issues
2. **Simplicity**: Streamlined code paths for easier maintenance
3. **Consistency**: Uniform handling of tables and images
4. **Visibility**: All content elements are now fully visible in Word
5. **Order**: Sequential processing ensures correct content order

The fixes ensure that tables and images appear in the correct order with proper visibility, eliminating the half-invisible image issue and wrong ordering problems.