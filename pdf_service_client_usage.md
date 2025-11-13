# PDF Service Client Usage Guide

This guide demonstrates how to use the PDF Service Client to communicate with the standalone PDF conversion service.

## Installation

The client requires the following dependencies (already in requirements.txt):
- `requests>=2.31.0`

## Configuration

Set the following environment variables:

```bash
# Required: URL of the PDF service
PDF_SERVICE_URL=https://pdf-service-production.up.railway.app

# Optional: Request timeout in seconds (default: 30)
PDF_SERVICE_TIMEOUT=30
```

## Basic Usage

### 1. Create a Client Instance

```python
from pdf_service_client import PDFServiceClient, create_pdf_service_client

# Option 1: Use convenience function (reads from environment variables)
client = create_pdf_service_client()

# Option 2: Create with custom configuration
client = PDFServiceClient(
    service_url="https://pdf-service.example.com",
    timeout=60,
    max_retries=3,
    backoff_factor=0.5
)
```

### 2. Check Service Health

```python
try:
    health_status = client.health_check()
    print(f"Service status: {health_status['status']}")
    print(f"LibreOffice available: {health_status['libreoffice_available']}")
except PDFServiceError as e:
    print(f"Health check failed: {e.message}")
```

### 3. Convert DOCX to PDF

```python
from pdf_service_client import PDFServiceClient, PDFServiceError

client = create_pdf_service_client()

# Read DOCX file
with open('document.docx', 'rb') as f:
    docx_bytes = f.read()

try:
    # Convert to PDF
    response = client.convert_to_pdf(docx_bytes)
    
    if response.success:
        # Decode PDF data
        import base64
        pdf_bytes = base64.b64decode(response.pdf_data)
        
        # Save PDF file
        with open('output.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"Conversion successful!")
        print(f"PDF size: {response.size} bytes")
        print(f"Processing time: {response.processing_time_ms}ms")
    else:
        print(f"Conversion failed: {response.error}")
        
except PDFServiceError as e:
    print(f"Error: {e.message} (code: {e.error_code})")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
```

### 4. Convert with Automatic Retry

For better reliability, use the retry method:

```python
try:
    response = client.convert_to_pdf_with_retry(docx_bytes, max_attempts=3)
    
    if response.success:
        pdf_bytes = base64.b64decode(response.pdf_data)
        # Process PDF...
        
except PDFServiceError as e:
    print(f"All retry attempts failed: {e.message}")
```

## Integration Example

Here's a complete example of integrating the client into a Flask endpoint:

```python
from flask import Flask, request, jsonify
from pdf_service_client import create_pdf_service_client, PDFServiceError
import base64

app = Flask(__name__)
pdf_client = create_pdf_service_client()

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        # Get DOCX data from request
        data = request.get_json()
        docx_base64 = data.get('docx_data')
        
        if not docx_base64:
            return jsonify({'error': 'DOCX data required'}), 400
        
        # Decode DOCX
        docx_bytes = base64.b64decode(docx_base64)
        
        # Convert to PDF with retry
        response = pdf_client.convert_to_pdf_with_retry(docx_bytes)
        
        if response.success:
            return jsonify({
                'success': True,
                'pdf_data': response.pdf_data,
                'size': response.size,
                'processing_time_ms': response.processing_time_ms
            })
        else:
            return jsonify({
                'success': False,
                'error': response.error
            }), 500
            
    except PDFServiceError as e:
        if e.error_code == "SERVICE_UNAVAILABLE":
            # Implement fallback logic here
            return jsonify({
                'error': 'PDF service temporarily unavailable',
                'retry_after': e.retry_after
            }), 503
        else:
            return jsonify({
                'error': e.message,
                'error_code': e.error_code
            }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Error Handling

The client raises `PDFServiceError` exceptions with specific error codes:

| Error Code | Description | Retry Recommended |
|------------|-------------|-------------------|
| `INVALID_REQUEST` | Invalid DOCX data or request format | No |
| `RATE_LIMITED` | Too many requests | Yes (after retry_after) |
| `SERVICE_UNAVAILABLE` | Service temporarily down | Yes (after retry_after) |
| `TIMEOUT` | Request timeout | Yes |
| `CONNECTION_ERROR` | Cannot connect to service | Yes |
| `CONVERSION_FAILED` | PDF conversion failed | No |
| `HEALTH_CHECK_FAILED` | Health check failed | Yes |
| `UNKNOWN_ERROR` | Unexpected error | Maybe |

## Best Practices

1. **Use retry logic**: Always use `convert_to_pdf_with_retry()` for production code
2. **Check service health**: Periodically check service availability with `is_service_available()`
3. **Implement fallback**: Have a fallback conversion method when the service is unavailable
4. **Handle errors gracefully**: Catch `PDFServiceError` and provide user-friendly messages
5. **Configure timeouts**: Adjust timeout based on expected document size and complexity
6. **Monitor performance**: Log conversion times and error rates for monitoring

## Testing

Run the test suite:

```bash
pytest format-a-python-backend/test_pdf_service_client.py -v
```

## Requirements Satisfied

This implementation satisfies the following requirements:
- **2.2**: Backend communicates with PDF service via REST API calls
- **2.4**: Handles PDF service unavailability gracefully
- **6.5**: Provides metrics for request volume, conversion times, and error rates
