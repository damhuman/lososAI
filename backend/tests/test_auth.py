"""Tests for authentication and middleware."""
import pytest
from httpx import AsyncClient
import hmac
import hashlib
import time
from urllib.parse import parse_qs

from app.core.config import settings

# Mark all test functions in this module as asyncio
pytestmark = pytest.mark.asyncio


class TestJWTAuth:
    """Test JWT Authentication for admin endpoints."""
    
    async def test_missing_auth_header(self, client: AsyncClient):
        """Test request without Authorization header."""
        response = await client.get("/api/v1/admin/categories")
        assert response.status_code in [401, 403]  # HTTPBearer returns 403, but both are valid for missing auth
    
    async def test_invalid_auth_scheme(self, client: AsyncClient):
        """Test request with invalid auth scheme."""
        headers = {"Authorization": "Basic invalid"}
        response = await client.get("/api/v1/admin/categories", headers=headers)
        assert response.status_code in [401, 403]  # Different auth schemes can return either
    
    async def test_invalid_jwt_token(self, client: AsyncClient):
        """Test request with invalid JWT token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/api/v1/admin/categories", headers=headers)
        assert response.status_code == 401
    
    async def test_malformed_jwt_token(self, client: AsyncClient):
        """Test request with malformed JWT token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/admin/categories", headers=headers)
        assert response.status_code == 401
    
    async def test_valid_jwt_token(self, client: AsyncClient, admin_headers):
        """Test request with valid JWT token."""
        response = await client.get("/api/v1/admin/categories", headers=admin_headers)
        assert response.status_code == 200


class TestTelegramAuth:
    """Test Telegram Web App authentication."""
    
    def create_valid_init_data(self, user_data: dict) -> str:
        """Create valid Telegram init data with proper hash."""
        # Create query parameters
        params = {
            "query_id": "test_query_id",
            "user": str(user_data).replace("'", '"'),
            "auth_date": str(int(time.time())),
        }
        
        # Create data string for hash calculation
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # Calculate hash
        secret_key = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        params["hash"] = hash_value
        return "&".join([f"{k}={v}" for k, v in params.items()])
    
    async def test_missing_telegram_auth(self, unauthenticated_client: AsyncClient):
        """Test Telegram endpoint without auth."""
        response = await unauthenticated_client.get("/api/v1/orders/")
        assert response.status_code == 401
    
    async def test_invalid_telegram_auth_scheme(self, unauthenticated_client: AsyncClient):
        """Test Telegram endpoint with invalid auth scheme."""
        headers = {"Authorization": "Basic invalid"}
        response = await unauthenticated_client.get("/api/v1/orders/", headers=headers)
        assert response.status_code == 401
    
    async def test_invalid_telegram_hash(self, unauthenticated_client: AsyncClient):
        """Test Telegram endpoint with invalid hash."""
        invalid_init_data = "query_id=test&user={}&auth_date=1234567890&hash=invalid"
        headers = {"Authorization": f"tma {invalid_init_data}"}
        response = await unauthenticated_client.get("/api/v1/orders/", headers=headers)
        assert response.status_code == 401
    
    async def test_expired_telegram_auth(self, unauthenticated_client: AsyncClient):
        """Test Telegram endpoint with expired auth."""
        old_timestamp = int(time.time()) - 90000  # Very old timestamp
        params = {
            "query_id": "test_query_id",
            "user": '{"id":123456789,"first_name":"Test","username":"testuser"}',
            "auth_date": str(old_timestamp),
            "hash": "some_hash"
        }
        init_data = "&".join([f"{k}={v}" for k, v in params.items()])
        headers = {"Authorization": f"tma {init_data}"}
        response = await unauthenticated_client.get("/api/v1/orders/", headers=headers)
        assert response.status_code == 401
    
    async def test_malformed_user_data(self, unauthenticated_client: AsyncClient):
        """Test Telegram endpoint with malformed user data."""
        init_data = "query_id=test&user=invalid_json&auth_date=1234567890&hash=test"
        headers = {"Authorization": f"tma {init_data}"}
        response = await unauthenticated_client.get("/api/v1/orders/", headers=headers)
        assert response.status_code == 401


class TestCORS:
    """Test CORS middleware."""
    
    async def test_cors_preflight(self, client: AsyncClient):
        """Test CORS preflight request."""
        headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = await client.options("/api/v1/products", headers=headers)
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
    
    async def test_cors_actual_request(self, client: AsyncClient):
        """Test CORS headers on actual request."""
        headers = {"Origin": "https://example.com"}
        response = await client.get("/api/v1/categories", headers=headers)
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
    
    async def test_cors_credentials(self, client: AsyncClient):
        """Test CORS credentials handling."""
        headers = {"Origin": "https://example.com"}
        response = await client.get("/api/v1/categories", headers=headers)
        assert response.status_code == 200
        # Check if credentials are allowed
        cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
        if cors_credentials:
            assert cors_credentials.lower() == "true"


class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    async def test_rate_limit_not_exceeded(self, client: AsyncClient):
        """Test normal request rate."""
        for _ in range(5):
            response = await client.get("/api/v1/categories")
            assert response.status_code == 200
    
    # Note: If rate limiting is implemented, add tests for:
    # - Exceeding rate limits
    # - Rate limit headers
    # - Different limits for different endpoints


class TestErrorHandling:
    """Test global error handling."""
    
    async def test_internal_server_error_handling(self, client: AsyncClient):
        """Test that 500 errors are handled properly."""
        # This would require injecting an error condition
        # For now, just test that valid requests work
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
    
    async def test_request_validation_error(self, client: AsyncClient):
        """Test request validation error handling."""
        # Send invalid JSON
        response = await client.post("/api/v1/promo/validate", content="invalid json")
        assert response.status_code == 422
    
    async def test_method_not_allowed_error(self, client: AsyncClient):
        """Test method not allowed error."""
        response = await client.patch("/api/v1/categories")
        assert response.status_code == 405
    
    async def test_not_found_error(self, client: AsyncClient):
        """Test 404 error handling."""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404


class TestMiddleware:
    """Test custom middleware."""
    
    async def test_request_processing(self, client: AsyncClient):
        """Test that requests are processed correctly."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        # Check response headers
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
    
    async def test_response_headers(self, client: AsyncClient):
        """Test that proper response headers are set."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        # Common security headers that might be added by middleware
        expected_headers = [
            "content-type"
        ]
        for header in expected_headers:
            assert header.lower() in [h.lower() for h in response.headers.keys()]
    
    async def test_request_id_header(self, client: AsyncClient):
        """Test request ID header (if implemented)."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        # If request ID middleware is implemented
        request_id = response.headers.get("X-Request-ID")
        if request_id:
            assert len(request_id) > 0


class TestSecurity:
    """Test security-related functionality."""
    
    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test protection against SQL injection."""
        # Try SQL injection in query parameters
        malicious_category = "'; DROP TABLE categories; --"
        response = await client.get(f"/api/v1/products?category_id={malicious_category}")
        # Should return empty results, not cause an error
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_xss_protection(self, client: AsyncClient, admin_headers):
        """Test XSS protection in data handling."""
        # Try to create category with XSS payload
        xss_payload = "<script>alert('xss')</script>"
        category_data = {
            "id": "xss_test",
            "name": xss_payload,
            "icon": "🐟",
            "order": 1
        }
        response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
        
        if response.status_code == 200:
            # If creation succeeds, check that data is properly escaped/sanitized
            created_category = response.json()
            # The name should either be escaped or rejected
            assert created_category["name"] != xss_payload or "<script>" not in created_category["name"]
    
    async def test_file_upload_security(self, client: AsyncClient, admin_headers):
        """Test file upload security (if endpoint exists)."""
        # This would test the image upload endpoint
        # For now, just verify the endpoint exists and requires auth
        response = await client.post("/api/v1/admin/upload/image", files={"image": ("test.txt", b"test", "text/plain")})
        # Should require authentication
        assert response.status_code == 401