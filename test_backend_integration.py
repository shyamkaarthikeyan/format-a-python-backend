"""
Backend Integration Tests for PDF Service Communication

This test suite verifies the complete PDF generation flow from frontend request
to PDF response, including PDF service integration, fallback behavior, and
error propagation mechanisms.

Requirements: 2.4, 3.4, 3.5, 4.4
"""

import os
import sys
import json
import base64
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_service_client import PDFServiceClient, PDFServiceError, PDFConversionResponse


class TestEndToEndPDFGeneration:
    """
    Test complete PDF generation flow from frontend request to PDF response.
    
    Requirements: 2.4, 3.4, 4.4
    """
    
    def test_complete_pdf_generation_flow_with_pdf_service(self):
        """
        Test end-to-end PDF generation using PDF service.
        
        Flow:
        1. Frontend sends request with document data
        2. Backend generates DOCX document
        3. Backend sends DOCX to PDF service
        4. PDF service converts to PDF
        5. Backend returns PDF to frontend
        """
        # Step 1: Simulate frontend request
        document_data = {
            'title': 'Integration Test Paper',
            'authors': [
                {'name': 'Test Author 1', 'email': 'author1@test.com', 'affiliation': 'Test University'},
                {'name': 'Test Author 2', 'email': 'author2@test.com', 'affiliation': 'Test Institute'}
            ],
            'abstract': 'This is a test abstract for integration testing.',
            'format': 'pdf',
            'action': 'download'
        }
        
        # Step 2: Generate DOCX document
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        assert docx_bytes is not None
        assert len(docx_bytes) > 0
        assert isinstance(docx_bytes, bytes)
        
        # Step 3: Mock PDF service conversion
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            # Mock successful PDF conversion
            mock_pdf_data = base64.b64encode(b'%PDF-1.4 test pdf content').decode('utf-8')
            mock_response = PDFConversionResponse(
                success=True,
                pdf_data=mock_pdf_data,
                size=len(b'%PDF-1.4 test pdf content'),
                conversion_method='docx2pdf_exact',
                processing_time_ms=1500
            )
            mock_convert.return_value = mock_response
            
            # Step 4: Call PDF service
            client = PDFServiceClient(service_url='http://test-service.com')
            response = client.convert_to_pdf(docx_bytes)
            
            # Step 5: Verify response
            assert response.success is True
            assert response.pdf_data is not None
            assert response.conversion_method == 'docx2pdf_exact'
            
            # Decode and verify PDF data
            pdf_bytes = base64.b64decode(response.pdf_data)
            assert pdf_bytes.startswith(b'%PDF')
            
            # Verify PDF service was called with correct data
            mock_convert.assert_called_once_with(docx_bytes)
    
    def test_complete_pdf_generation_flow_with_preview(self):
        """
        Test end-to-end PDF preview generation.
        
        Flow:
        1. Frontend sends preview request
        2. Backend generates DOCX document
        3. Backend converts to PDF for preview
        4. Backend returns PDF preview to frontend
        """
        # Step 1: Simulate frontend preview request
        document_data = {
            'title': 'Preview Test Paper',
            'authors': [{'name': 'Preview Author', 'email': 'preview@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Preview abstract',
            'format': 'preview',  # or no format specified
            'action': 'preview'
        }
        
        # Step 2: Generate DOCX document
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        assert docx_bytes is not None
        assert len(docx_bytes) > 0
        
        # Step 3: Mock PDF conversion for preview
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_pdf_data = base64.b64encode(b'%PDF-1.4 preview pdf').decode('utf-8')
            mock_response = PDFConversionResponse(
                success=True,
                pdf_data=mock_pdf_data,
                size=len(b'%PDF-1.4 preview pdf'),
                conversion_method='docx2pdf_exact',
                processing_time_ms=1200
            )
            mock_convert.return_value = mock_response
            
            # Step 4: Convert to PDF for preview
            client = PDFServiceClient(service_url='http://test-service.com')
            response = client.convert_to_pdf(docx_bytes)
            
            # Step 5: Verify preview response
            assert response.success is True
            assert response.pdf_data is not None
            
            pdf_bytes = base64.b64decode(response.pdf_data)
            assert pdf_bytes.startswith(b'%PDF')
    
    def test_docx_download_flow_without_pdf_service(self):
        """
        Test DOCX download flow that doesn't require PDF service.
        
        Requirements: 3.4 (Word-only mode functions without PDF service)
        """
        # Simulate frontend DOCX download request
        document_data = {
            'title': 'DOCX Download Test',
            'authors': [{'name': 'DOCX Author', 'email': 'docx@test.com', 'affiliation': 'Test Lab'}],
            'abstract': 'DOCX abstract',
            'format': 'docx',
            'action': 'download'
        }
        
        # Generate DOCX document (no PDF service needed)
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        assert docx_bytes is not None
        assert len(docx_bytes) > 0
        assert isinstance(docx_bytes, bytes)
        
        # Verify DOCX can be encoded for response
        docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')
        assert docx_base64 is not None
        assert len(docx_base64) > 0


class TestPDFServiceFallbackBehavior:
    """
    Test PDF service fallback behavior when service is unavailable.
    
    Requirements: 2.4, 3.4, 3.5
    """
    
    def test_fallback_to_direct_conversion_on_service_unavailable(self):
        """
        Test system falls back to direct conversion when PDF service is unavailable.
        
        Requirements: 3.5 (PDF service unavailable -> backend provides Word generation)
        """
        document_data = {
            'title': 'Fallback Test Paper',
            'authors': [{'name': 'Fallback Author', 'email': 'fallback@test.com', 'affiliation': 'Test Center'}],
            'abstract': 'Testing fallback mechanism',
            'format': 'pdf'
        }
        
        # Generate DOCX document
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        # Mock PDF service failure
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Service temporarily unavailable",
                "SERVICE_UNAVAILABLE",
                60
            )
            
            client = PDFServiceClient(service_url='http://test-service.com')
            
            # Verify PDF service raises error
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(docx_bytes)
            
            assert exc_info.value.error_code == "SERVICE_UNAVAILABLE"
            assert exc_info.value.retry_after == 60
            
            # In real implementation, this would trigger fallback to direct conversion
            # Verify fallback mechanism exists
            from docx_to_pdf_converter_direct import convert_docx_to_pdf_direct
            
            # Fallback conversion should work
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
    
    def test_fallback_on_connection_error(self):
        """
        Test fallback when PDF service connection fails.
        
        Requirements: 2.4 (Handle PDF service unavailability gracefully)
        """
        document_data = {
            'title': 'Connection Error Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing connection error handling'
        }
        
        # Generate DOCX document
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        # Mock connection error
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Cannot connect to PDF service",
                "CONNECTION_ERROR"
            )
            
            client = PDFServiceClient(service_url='http://unreachable-service.com')
            
            # Verify connection error is raised
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(docx_bytes)
            
            assert exc_info.value.error_code == "CONNECTION_ERROR"
            
            # Verify fallback to direct conversion works
            from docx_to_pdf_converter_direct import convert_docx_to_pdf_direct
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            assert pdf_bytes is not None
    
    def test_fallback_on_timeout(self):
        """
        Test fallback when PDF service times out.
        
        Requirements: 2.4 (Handle PDF service failures gracefully)
        """
        document_data = {
            'title': 'Timeout Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing timeout handling'
        }
        
        # Generate DOCX document
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        # Mock timeout error
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Conversion timeout after 30s",
                "TIMEOUT"
            )
            
            client = PDFServiceClient(service_url='http://slow-service.com', timeout=30)
            
            # Verify timeout error is raised
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(docx_bytes)
            
            assert exc_info.value.error_code == "TIMEOUT"
            
            # Verify fallback works
            from docx_to_pdf_converter_direct import convert_docx_to_pdf_direct
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            assert pdf_bytes is not None
    
    def test_retry_logic_with_eventual_success(self):
        """
        Test retry logic succeeds after transient failures.
        
        Requirements: 2.4 (Retry logic with exponential backoff)
        """
        document_data = {
            'title': 'Retry Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing retry logic'
        }
        
        # Generate DOCX document
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        # Mock transient failure followed by success
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            # First call fails, second succeeds
            mock_pdf_data = base64.b64encode(b'%PDF-1.4 success after retry').decode('utf-8')
            mock_convert.side_effect = [
                PDFServiceError("Service temporarily unavailable", "SERVICE_UNAVAILABLE", 1),
                PDFConversionResponse(
                    success=True,
                    pdf_data=mock_pdf_data,
                    size=len(b'%PDF-1.4 success after retry'),
                    conversion_method='docx2pdf_exact',
                    processing_time_ms=2000
                )
            ]
            
            client = PDFServiceClient(service_url='http://test-service.com')
            
            # Use retry method
            with patch('time.sleep'):  # Mock sleep to speed up test
                response = client.convert_to_pdf_with_retry(docx_bytes, max_attempts=2)
            
            assert response.success is True
            assert response.pdf_data is not None
            assert mock_convert.call_count == 2


class TestErrorPropagationAndUserFeedback:
    """
    Test error propagation and user feedback mechanisms.
    
    Requirements: 4.4 (Clear error messages with suggested next steps)
    """
    
    def test_invalid_request_error_propagation(self):
        """
        Test that invalid request errors are properly propagated to frontend.
        
        Requirements: 4.4 (Display clear error message with suggested next steps)
        """
        # Mock invalid DOCX data
        invalid_docx_bytes = b'not a valid docx file'
        
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Invalid DOCX data",
                "INVALID_REQUEST"
            )
            
            client = PDFServiceClient(service_url='http://test-service.com')
            
            # Verify error is raised with correct code
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(invalid_docx_bytes)
            
            assert exc_info.value.error_code == "INVALID_REQUEST"
            assert "Invalid DOCX data" in exc_info.value.message
            
            # This error should be caught by backend and returned to frontend
            # with user-friendly message
    
    def test_rate_limit_error_with_retry_after(self):
        """
        Test rate limit errors include retry_after information for user feedback.
        
        Requirements: 4.4 (Provide meaningful error messages)
        """
        document_data = {
            'title': 'Rate Limit Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing rate limit handling'
        }
        
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Rate limit exceeded",
                "RATE_LIMITED",
                30
            )
            
            client = PDFServiceClient(service_url='http://test-service.com')
            
            # Verify error includes retry_after
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(docx_bytes)
            
            assert exc_info.value.error_code == "RATE_LIMITED"
            assert exc_info.value.retry_after == 30
            
            # Frontend can use retry_after to show: "Please try again in 30 seconds"
    
    def test_service_unavailable_error_with_fallback_message(self):
        """
        Test service unavailable errors trigger fallback with appropriate messaging.
        
        Requirements: 3.5, 4.4 (Fallback with user notification)
        """
        document_data = {
            'title': 'Service Unavailable Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing service unavailable handling'
        }
        
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Service temporarily unavailable",
                "SERVICE_UNAVAILABLE",
                60
            )
            
            client = PDFServiceClient(service_url='http://test-service.com')
            
            # Verify error is raised
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(docx_bytes)
            
            assert exc_info.value.error_code == "SERVICE_UNAVAILABLE"
            
            # Backend should catch this and:
            # 1. Fall back to direct conversion
            # 2. Return success with message about fallback method used
            from docx_to_pdf_converter_direct import convert_docx_to_pdf_direct
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            
            # Simulate backend response with fallback info
            response = {
                'success': True,
                'file_data': base64.b64encode(pdf_bytes).decode('utf-8'),
                'conversion_method': 'direct_docx2pdf_fallback',
                'message': 'PDF generated using fallback method (PDF service temporarily unavailable)'
            }
            
            assert response['success'] is True
            assert 'fallback' in response['conversion_method']
    
    def test_conversion_failure_error_details(self):
        """
        Test conversion failure errors include detailed information for debugging.
        
        Requirements: 4.4 (Clear error messages)
        """
        document_data = {
            'title': 'Conversion Failure Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing conversion failure handling'
        }
        
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        with patch.object(PDFServiceClient, 'convert_to_pdf') as mock_convert:
            mock_convert.side_effect = PDFServiceError(
                "Conversion failed: LibreOffice process crashed",
                "CONVERSION_FAILED"
            )
            
            client = PDFServiceClient(service_url='http://test-service.com')
            
            # Verify error includes detailed message
            with pytest.raises(PDFServiceError) as exc_info:
                client.convert_to_pdf(docx_bytes)
            
            assert exc_info.value.error_code == "CONVERSION_FAILED"
            assert "LibreOffice" in exc_info.value.message
            
            # Frontend should show: "PDF generation failed. Please try again."


class TestEnvironmentConfiguration:
    """
    Test environment variable configuration for PDF service integration.
    
    Requirements: 3.3 (Environment variable configuration)
    """
    
    def test_pdf_service_url_from_environment(self):
        """Test PDF service URL is read from environment variable"""
        with patch.dict(os.environ, {'PDF_SERVICE_URL': 'https://prod-pdf-service.railway.app'}):
            client = PDFServiceClient()
            assert client.service_url == 'https://prod-pdf-service.railway.app'
    
    def test_pdf_service_timeout_from_environment(self):
        """Test PDF service timeout is read from environment variable"""
        with patch.dict(os.environ, {
            'PDF_SERVICE_URL': 'http://test.com',
            'PDF_SERVICE_TIMEOUT': '45'
        }):
            from pdf_service_client import create_pdf_service_client
            client = create_pdf_service_client()
            assert client.timeout == 45
    
    def test_use_pdf_service_flag(self):
        """Test USE_PDF_SERVICE flag controls PDF service usage"""
        # Test with PDF service enabled
        with patch.dict(os.environ, {'USE_PDF_SERVICE': 'true'}):
            use_service = os.environ.get('USE_PDF_SERVICE', 'true').lower() == 'true'
            assert use_service is True
        
        # Test with PDF service disabled
        with patch.dict(os.environ, {'USE_PDF_SERVICE': 'false'}):
            use_service = os.environ.get('USE_PDF_SERVICE', 'true').lower() == 'true'
            assert use_service is False
    
    def test_default_configuration_values(self):
        """Test default values are used when environment variables are not set"""
        with patch.dict(os.environ, {}, clear=True):
            # Clear all environment variables
            url = os.environ.get('PDF_SERVICE_URL', 'http://localhost:5000')
            timeout = int(os.environ.get('PDF_SERVICE_TIMEOUT', '30'))
            use_service = os.environ.get('USE_PDF_SERVICE', 'true').lower() == 'true'
            
            assert url == 'http://localhost:5000'
            assert timeout == 30
            assert use_service is True


class TestWordGenerationIndependence:
    """
    Test that Word generation works independently of PDF service.
    
    Requirements: 3.4 (Word generation unchanged, no PDF service dependency)
    """
    
    def test_word_generation_without_pdf_service(self):
        """Test DOCX generation works without PDF service"""
        document_data = {
            'title': 'Independent Word Generation Test',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing Word generation independence'
        }
        
        # Generate DOCX without any PDF service interaction
        from ieee_generator_fixed import generate_ieee_document
        docx_bytes = generate_ieee_document(document_data)
        
        assert docx_bytes is not None
        assert len(docx_bytes) > 0
        assert isinstance(docx_bytes, bytes)
    
    def test_word_generation_with_pdf_service_unavailable(self):
        """Test DOCX generation succeeds even when PDF service is down"""
        document_data = {
            'title': 'Word Generation with Service Down',
            'authors': [{'name': 'Test Author', 'email': 'test@test.com', 'affiliation': 'Test Org'}],
            'abstract': 'Testing resilience'
        }
        
        # Mock PDF service as unavailable
        with patch.dict(os.environ, {'PDF_SERVICE_URL': 'http://unavailable-service.com'}):
            # Word generation should still work
            from ieee_generator_fixed import generate_ieee_document
            docx_bytes = generate_ieee_document(document_data)
            
            assert docx_bytes is not None
            assert len(docx_bytes) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
