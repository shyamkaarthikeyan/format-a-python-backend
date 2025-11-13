"""
PDF Service Client for Backend Integration

This module provides an HTTP client to communicate with the standalone PDF service
deployed on Railway/Render. It includes retry logic with exponential backoff for
transient failures and health check functionality to monitor service availability.

Requirements: 2.2, 2.4, 6.5
"""

import os
import base64
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PDFConversionRequest:
    """Request model for PDF conversion"""
    docx_data: str  # base64 encoded DOCX bytes
    options: Dict[str, Any] = None
    timeout: int = 30
    quality: str = "high"
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}
    
    def validate(self):
        """Validate the conversion request"""
        if not self.docx_data:
            raise ValueError("DOCX data is required")
        
        try:
            base64.b64decode(self.docx_data)
        except Exception as e:
            raise ValueError(f"Invalid base64 DOCX data: {str(e)}")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "docx_data": self.docx_data,
            "options": self.options
        }


@dataclass
class PDFConversionResponse:
    """Response model for PDF conversion"""
    success: bool
    pdf_data: Optional[str] = None  # base64 encoded PDF bytes
    size: Optional[int] = None
    conversion_method: str = "docx2pdf_exact"
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class PDFServiceError(Exception):
    """Base exception for PDF service errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, retry_after: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        self.retry_after = retry_after
        super().__init__(message)


class PDFServiceClient:
    """
    HTTP client for communicating with the PDF service.
    
    Features:
    - Retry logic with exponential backoff for transient failures
    - Health check functionality to monitor service availability
    - Comprehensive error handling and logging
    """
    
    def __init__(
        self,
        service_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        """
        Initialize the PDF service client.
        
        Args:
            service_url: URL of the PDF service (defaults to PDF_SERVICE_URL env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for exponential retry delay
        """
        self.service_url = service_url or os.environ.get('PDF_SERVICE_URL', 'http://localhost:5000')
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Remove trailing slash from service URL
        self.service_url = self.service_url.rstrip('/')
        
        # Create session with retry logic
        self.session = self._create_session_with_retries()
        
        logger.info(f"PDF Service Client initialized with URL: {self.service_url}")
    
    def _create_session_with_retries(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Retry strategy:
        - Retry on connection errors, timeouts, and 5xx server errors
        - Use exponential backoff between retries
        - Don't retry on 4xx client errors (except 429 rate limit)
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the PDF service.
        
        Returns:
            Dictionary with health status information
            
        Raises:
            PDFServiceError: If health check fails
        """
        try:
            logger.info("Performing health check on PDF service")
            
            response = self.session.get(
                f"{self.service_url}/health",
                timeout=10  # Shorter timeout for health checks
            )
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"PDF service is healthy: {health_data}")
                return health_data
            else:
                error_msg = f"Health check failed with status {response.status_code}"
                logger.error(error_msg)
                raise PDFServiceError(error_msg, "HEALTH_CHECK_FAILED")
                
        except PDFServiceError:
            # Re-raise PDF service errors without wrapping
            raise
        except requests.Timeout:
            error_msg = "Health check timeout"
            logger.error(error_msg)
            raise PDFServiceError(error_msg, "TIMEOUT")
        except requests.ConnectionError as e:
            error_msg = f"Cannot connect to PDF service: {str(e)}"
            logger.error(error_msg)
            raise PDFServiceError(error_msg, "CONNECTION_ERROR")
        except Exception as e:
            error_msg = f"Health check failed: {str(e)}"
            logger.error(error_msg)
            raise PDFServiceError(error_msg, "UNKNOWN_ERROR")
    
    def is_service_available(self) -> bool:
        """
        Check if the PDF service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            self.health_check()
            return True
        except PDFServiceError:
            return False
    
    def convert_to_pdf(self, docx_bytes: bytes) -> PDFConversionResponse:
        """
        Convert DOCX bytes to PDF using the PDF service.
        
        Args:
            docx_bytes: DOCX file content as bytes
            
        Returns:
            PDFConversionResponse with conversion results
            
        Raises:
            PDFServiceError: If conversion fails
        """
        start_time = time.time()
        
        try:
            # Encode DOCX data to base64
            docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')
            
            # Create and validate request
            request = PDFConversionRequest(docx_data=docx_base64)
            request.validate()
            
            logger.info(f"Sending PDF conversion request (DOCX size: {len(docx_bytes)} bytes)")
            
            # Send conversion request to correct endpoint
            response = self.session.post(
                f"{self.service_url}/convert-pdf",
                json=request.to_dict(),
                timeout=self.timeout
            )
            
            # Handle different response status codes
            if response.status_code == 200:
                result = response.json()
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                logger.info(f"PDF conversion successful (took {elapsed_ms}ms)")
                
                return PDFConversionResponse(
                    success=result.get('success', True),
                    pdf_data=result.get('pdf_data'),
                    size=result.get('size'),
                    conversion_method=result.get('conversion_method', 'docx2pdf_exact'),
                    processing_time_ms=result.get('processing_time_ms', elapsed_ms),
                    error=result.get('error')
                )
            
            elif response.status_code == 400:
                error_msg = f"Invalid request: {response.text}"
                logger.error(error_msg)
                raise PDFServiceError(error_msg, "INVALID_REQUEST")
            
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 30))
                error_msg = "Rate limit exceeded"
                logger.warning(f"{error_msg}, retry after {retry_after}s")
                raise PDFServiceError(error_msg, "RATE_LIMITED", retry_after)
            
            elif response.status_code == 503:
                retry_after = int(response.headers.get('Retry-After', 60))
                error_msg = "Service temporarily unavailable"
                logger.warning(f"{error_msg}, retry after {retry_after}s")
                raise PDFServiceError(error_msg, "SERVICE_UNAVAILABLE", retry_after)
            
            else:
                error_msg = f"Conversion failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise PDFServiceError(error_msg, "CONVERSION_FAILED")
                
        except requests.Timeout:
            error_msg = f"Conversion timeout after {self.timeout}s"
            logger.error(error_msg)
            raise PDFServiceError(error_msg, "TIMEOUT")
        
        except requests.ConnectionError as e:
            error_msg = f"Cannot connect to PDF service: {str(e)}"
            logger.error(error_msg)
            raise PDFServiceError(error_msg, "CONNECTION_ERROR")
        
        except PDFServiceError:
            # Re-raise PDF service errors
            raise
        
        except Exception as e:
            error_msg = f"Unexpected error during conversion: {str(e)}"
            logger.error(error_msg)
            raise PDFServiceError(error_msg, "UNKNOWN_ERROR")
    
    def convert_to_pdf_with_retry(
        self,
        docx_bytes: bytes,
        max_attempts: Optional[int] = None
    ) -> PDFConversionResponse:
        """
        Convert DOCX to PDF with manual retry logic for specific error cases.
        
        This method adds an additional retry layer on top of the session's
        automatic retries for handling specific scenarios like rate limiting.
        
        Args:
            docx_bytes: DOCX file content as bytes
            max_attempts: Maximum number of attempts (defaults to max_retries)
            
        Returns:
            PDFConversionResponse with conversion results
            
        Raises:
            PDFServiceError: If all retry attempts fail
        """
        max_attempts = max_attempts or self.max_retries
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"PDF conversion attempt {attempt}/{max_attempts}")
                return self.convert_to_pdf(docx_bytes)
            
            except PDFServiceError as e:
                last_error = e
                
                # Don't retry on client errors (except rate limiting)
                if e.error_code in ["INVALID_REQUEST"]:
                    logger.error(f"Non-retryable error: {e.message}")
                    raise
                
                # Check if we should retry
                if attempt < max_attempts:
                    # Calculate delay with exponential backoff
                    if e.retry_after:
                        delay = e.retry_after
                    else:
                        delay = self.backoff_factor * (2 ** (attempt - 1))
                    
                    logger.warning(f"Attempt {attempt} failed: {e.message}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_attempts} attempts failed")
                    raise
        
        # This should never be reached, but just in case
        if last_error:
            raise last_error
        raise PDFServiceError("Conversion failed after all retry attempts", "MAX_RETRIES_EXCEEDED")


# Convenience function for quick usage
def create_pdf_service_client() -> PDFServiceClient:
    """
    Create a PDF service client with default configuration from environment variables.
    
    Environment variables:
    - PDF_SERVICE_URL: URL of the PDF service
    - PDF_SERVICE_TIMEOUT: Request timeout in seconds (default: 30)
    
    Returns:
        Configured PDFServiceClient instance
    """
    timeout = int(os.environ.get('PDF_SERVICE_TIMEOUT', '30'))
    return PDFServiceClient(timeout=timeout)
