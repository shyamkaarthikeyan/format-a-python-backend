# PDF Service Integration Guide

## Overview

The backend document generator has been enhanced to route PDF conversion requests through a standalone PDF service with automatic fallback to direct conversion when the service is unavailable.

## Architecture

```
Frontend Request (format: "pdf")
         ↓
Backend Document Generator
         ↓
1. Generate DOCX (ieee_generator_fixed.py)
         ↓
2. Convert to PDF:
   ├─→ Try PDF Service (if configured)
   │   ├─→ Success: Return PDF from service
   │   └─→ Failure: Fall back to direct conversion
   └─→ Direct Conversion (docx_to_pdf_converter_direct.py)
         ↓
Return PDF to Frontend
```

## Configuration

### Environment Variables

Add these environment variables to your deployment configuration:

```bash
# PDF Service URL (required for PDF service integration)
PDF_SERVICE_URL=https://your-pdf-service.railway.app

# PDF Service timeout in seconds (optional, default: 30)
PDF_SERVICE_TIMEOUT=30

# Enable/disable PDF service (optional, default: true)
# Set to 'false' to always use direct conversion
USE_PDF_SERVICE=true
```

### Vercel Configuration

Add environment variables in Vercel dashboard:
1. Go to Project Settings → Environment Variables
2. Add `PDF_SERVICE_URL` with your PDF service URL
3. Add `PDF_SERVICE_TIMEOUT` (optional)
4. Add `USE_PDF_SERVICE` (optional)

### Local Development

Create a `.env` file in `format-a-python-backend/`:

```bash
PDF_SERVICE_URL=http://localhost:5000
PDF_SERVICE_TIMEOUT=30
USE_PDF_SERVICE=true
```

## Features

### 1. PDF Service Routing

When a PDF request is received:
- Backend generates DOCX document first (existing functionality)
- Attempts to convert DOCX to PDF using PDF service
- Returns high-quality PDF from service

### 2. Automatic Fallback

If PDF service fails or is unavailable:
- System automatically falls back to direct conversion
- No user-facing errors
- Seamless degradation of service

### 3. Backward Compatibility

- Word document generation unchanged
- Existing direct conversion still available
- No breaking changes to API

## Request Flow

### PDF Download Request

```json
POST /api/document-generator
{
  "title": "Research Paper",
  "authors": ["Author Name"],
  "abstract": "Paper abstract",
  "format": "pdf",
  "action": "download"
}
```

**Response:**
```json
{
  "success": true,
  "file_data": "base64_encoded_pdf",
  "file_type": "application/pdf",
  "file_size": 123456,
  "conversion_method": "pdf_service_docx2pdf_exact",
  "message": "PDF generated successfully"
}
```

### PDF Preview Request

```json
POST /api/document-generator
{
  "title": "Research Paper",
  "authors": ["Author Name"],
  "abstract": "Paper abstract",
  "format": "preview"
}
```

**Response:**
```json
{
  "success": true,
  "file_data": "base64_encoded_pdf",
  "file_type": "application/pdf",
  "file_size": 123456,
  "conversion_method": "pdf_service_docx2pdf_exact",
  "message": "PDF preview generated successfully"
}
```

## Conversion Methods

The `conversion_method` field in responses indicates which method was used:

- `pdf_service_docx2pdf_exact` - PDF service with LibreOffice conversion
- `direct_docx2pdf_fallback` - Direct conversion fallback
- `docx_to_pdf_conversion` - Legacy direct conversion

## Error Handling

### PDF Service Errors

The system handles various PDF service errors gracefully:

| Error Code | Description | Fallback Behavior |
|------------|-------------|-------------------|
| `CONNECTION_ERROR` | Cannot connect to service | Use direct conversion |
| `TIMEOUT` | Request timeout | Use direct conversion |
| `SERVICE_UNAVAILABLE` | Service temporarily down | Use direct conversion |
| `RATE_LIMITED` | Too many requests | Use direct conversion |
| `CONVERSION_FAILED` | Conversion error | Use direct conversion |

### Logging

All PDF service interactions are logged:

```
✅ PDF service client initialized: https://pdf-service.railway.app
📄 Step 2: Converting DOCX to PDF using PDF service...
✅ PDF generated via PDF service (size: 123456 bytes, method: docx2pdf_exact)
```

Or with fallback:

```
⚠️ PDF service failed (CONNECTION_ERROR): Cannot connect to PDF service
🔄 Falling back to direct conversion...
✅ PDF generated via direct conversion fallback (size: 123456 bytes)
```

## Testing

### Run Integration Tests

```bash
python format-a-python-backend/test_pdf_service_integration.py
```

### Test PDF Service Client

```bash
python format-a-python-backend/test_pdf_service_client.py
```

### Manual Testing

1. **Test with PDF service:**
   ```bash
   export PDF_SERVICE_URL=https://your-pdf-service.railway.app
   export USE_PDF_SERVICE=true
   # Make PDF request
   ```

2. **Test fallback:**
   ```bash
   export PDF_SERVICE_URL=http://invalid-url:9999
   export USE_PDF_SERVICE=true
   # Make PDF request - should fall back to direct conversion
   ```

3. **Test direct conversion only:**
   ```bash
   export USE_PDF_SERVICE=false
   # Make PDF request - should use direct conversion
   ```

## Monitoring

### Health Checks

The PDF service client includes health check functionality:

```python
from pdf_service_client import create_pdf_service_client

client = create_pdf_service_client()

# Check if service is available
if client.is_service_available():
    print("PDF service is healthy")
else:
    print("PDF service is unavailable, using fallback")
```

### Metrics

Monitor these metrics in your logs:
- PDF service success rate
- Fallback usage frequency
- Conversion times
- Error rates by type

## Troubleshooting

### PDF Service Not Being Used

1. Check environment variables are set:
   ```bash
   echo $PDF_SERVICE_URL
   echo $USE_PDF_SERVICE
   ```

2. Check logs for initialization:
   ```
   ✅ PDF service client initialized: https://...
   ```

3. Verify PDF service is accessible:
   ```bash
   curl https://your-pdf-service.railway.app/health
   ```

### Always Falling Back to Direct Conversion

1. Check PDF service health:
   ```bash
   curl https://your-pdf-service.railway.app/health
   ```

2. Check timeout settings (increase if needed):
   ```bash
   export PDF_SERVICE_TIMEOUT=60
   ```

3. Review error logs for specific error codes

### Direct Conversion Not Working

1. Verify LibreOffice is installed locally
2. Check `docx_to_pdf_converter_direct.py` is available
3. Review conversion logs for errors

## Requirements Satisfied

This implementation satisfies the following requirements:

- **3.1**: Backend generates Word document first, maintaining existing functionality
- **3.2**: PDF requests route through PDF service (generate DOCX → send to service)
- **3.3**: PDF service response passed directly to frontend
- **3.4**: Word-only mode works without PDF service dependency
- **3.5**: Fallback to direct conversion when PDF service unavailable

## Next Steps

1. Deploy PDF service to Railway/Render
2. Configure `PDF_SERVICE_URL` in Vercel environment variables
3. Monitor PDF service usage and fallback rates
4. Adjust timeout settings based on performance metrics
