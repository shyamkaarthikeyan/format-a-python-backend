"""
Tests for PDF Service Client

This test file verifies the core functionality of the PDF service client,
including health checks, conversion requests, and retry logic.
"""

import os
import base64
import pytest
from unittest.mock import Mock, patch, MagicMock
from pdf_service_client import (
    PDFServiceClient,
    PDFServiceError,
    PDFConversionRequest,
    PDFConversionResponse,
    create_pdf_service_client
)


class TestPDFConversionRequest:
    """Test PDFConversionRequest model"""
    
    def test_valid_request(self):
        """Test creating a valid conversion request"""
        docx_data = base64.b64encode(b"test docx content").decode('utf-8')
        request = PDFConversionRequest(docx_data=docx_data)
        request.validate()
        assert request.docx_data == docx_data
        assert request.quality == "high"
        assert request.timeout == 30
    
    def test_invalid_base64(self):
        """Test validation fails with invalid base64"""
        request = PDFConversionRequest(docx_data="not-valid-base64!!!")
        with pytest.raises(ValueError, match="Invalid base64"):
            request.validate()
    
    def test_empty_docx_data(self):
        """Test validation fails with empty data"""
        request = PDFConversionRequest(docx_data="")
        with pytest.raises(ValueError, match="DOCX data is required"):
            request.validate()


class TestPDFServiceClient:
    """Test PDFServiceClient functionality"""
    
    def test_client_initialization(self):
        """Test client initializes with correct configuration"""
        client = PDFServiceClient(
            service_url="https://test-service.com",
            timeout=60,
            max_retries=5
        )
        assert client.service_url == "https://test-service.com"
        assert client.timeout == 60
        assert client.max_retries == 5
    
    def test_client_initialization_from_env(self):
        """Test client uses environment variables"""
        with patch.dict(os.environ, {'PDF_SERVICE_URL': 'https://env-service.com'}):
            client = PDFServiceClient()
            assert client.service_url == "https://env-service.com"
    
    def test_trailing_slash_removed(self):
        """Test trailing slash is removed from service URL"""
        client = PDFServiceClient(service_url="https://test-service.com/")
        assert client.service_url == "https://test-service.com"
    
    @patch('pdf_service_client.requests.Session')
    def test_health_check_success(self, mock_session_class):
        """Test successful health check"""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "service": "pdf-converter",
            "libreoffice_available": True
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client and perform health check
        client = PDFServiceClient()
        client.session = mock_session
        
        result = client.health_check()
        
        assert result["status"] == "healthy"
        assert result["libreoffice_available"] is True
        mock_session.get.assert_called_once()
    
    @patch('pdf_service_client.requests.Session')
    def test_health_check_failure(self, mock_session_class):
        """Test health check handles service failure"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 503
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient()
        client.session = mock_session
        
        with pytest.raises(PDFServiceError) as exc_info:
            client.health_check()
        
        assert exc_info.value.error_code == "HEALTH_CHECK_FAILED"
    
    @patch('pdf_service_client.requests.Session')
    def test_is_service_available(self, mock_session_class):
        """Test service availability check"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient()
        client.session = mock_session
        
        assert client.is_service_available() is True
    
    @patch('pdf_service_client.requests.Session')
    def test_convert_to_pdf_success(self, mock_session_class):
        """Test successful PDF conversion"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "pdf_data": base64.b64encode(b"PDF content").decode('utf-8'),
            "size": 1024,
            "conversion_method": "docx2pdf_exact",
            "processing_time_ms": 2500
        }
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient()
        client.session = mock_session
        
        docx_bytes = b"test docx content"
        result = client.convert_to_pdf(docx_bytes)
        
        assert result.success is True
        assert result.pdf_data is not None
        assert result.size == 1024
        assert result.conversion_method == "docx2pdf_exact"
        mock_session.post.assert_called_once()
    
    @patch('pdf_service_client.requests.Session')
    def test_convert_to_pdf_rate_limited(self, mock_session_class):
        """Test handling of rate limit errors"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '30'}
        mock_response.text = "Rate limit exceeded"
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient()
        client.session = mock_session
        
        with pytest.raises(PDFServiceError) as exc_info:
            client.convert_to_pdf(b"test content")
        
        assert exc_info.value.error_code == "RATE_LIMITED"
        assert exc_info.value.retry_after == 30
    
    @patch('pdf_service_client.requests.Session')
    def test_convert_to_pdf_service_unavailable(self, mock_session_class):
        """Test handling of service unavailable errors"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.headers = {'Retry-After': '60'}
        mock_response.text = "Service unavailable"
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient()
        client.session = mock_session
        
        with pytest.raises(PDFServiceError) as exc_info:
            client.convert_to_pdf(b"test content")
        
        assert exc_info.value.error_code == "SERVICE_UNAVAILABLE"
        assert exc_info.value.retry_after == 60
    
    @patch('pdf_service_client.requests.Session')
    def test_convert_to_pdf_invalid_request(self, mock_session_class):
        """Test handling of invalid request errors"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid DOCX data"
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient()
        client.session = mock_session
        
        with pytest.raises(PDFServiceError) as exc_info:
            client.convert_to_pdf(b"test content")
        
        assert exc_info.value.error_code == "INVALID_REQUEST"
    
    @patch('pdf_service_client.time.sleep')
    @patch('pdf_service_client.requests.Session')
    def test_convert_with_retry_success_after_failure(self, mock_session_class, mock_sleep):
        """Test retry logic succeeds after initial failure"""
        mock_session = Mock()
        
        # First call fails with 503, second call succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        mock_response_fail.headers = {'Retry-After': '1'}
        mock_response_fail.text = "Service unavailable"
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "success": True,
            "pdf_data": base64.b64encode(b"PDF content").decode('utf-8'),
            "size": 1024
        }
        
        mock_session.post.side_effect = [mock_response_fail, mock_response_success]
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient(max_retries=2)
        client.session = mock_session
        
        result = client.convert_to_pdf_with_retry(b"test content")
        
        assert result.success is True
        assert mock_session.post.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('pdf_service_client.time.sleep')
    @patch('pdf_service_client.requests.Session')
    def test_convert_with_retry_all_attempts_fail(self, mock_session_class, mock_sleep):
        """Test retry logic fails after all attempts"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.headers = {'Retry-After': '1'}
        mock_response.text = "Service unavailable"
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PDFServiceClient(max_retries=2)
        client.session = mock_session
        
        with pytest.raises(PDFServiceError):
            client.convert_to_pdf_with_retry(b"test content", max_attempts=2)
        
        assert mock_session.post.call_count == 2


def test_create_pdf_service_client():
    """Test convenience function for creating client"""
    with patch.dict(os.environ, {
        'PDF_SERVICE_URL': 'https://test.com',
        'PDF_SERVICE_TIMEOUT': '45'
    }):
        client = create_pdf_service_client()
        assert client.service_url == "https://test.com"
        assert client.timeout == 45


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
