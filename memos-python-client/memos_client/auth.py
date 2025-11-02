"""
Authentication manager for the Memos client.
"""

import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import base64

import httpx
from .config import ClientConfig
from .exceptions import AuthenticationError, NetworkError, MemosException


class AuthManager:
    """Manages authentication for the Memos client."""
    
    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self._session_data: Optional[Dict[str, Any]] = None
        self._session_expires_at: Optional[datetime] = None
        self._access_token: Optional[str] = config.access_token
        
    async def authenticate(self) -> Dict[str, str]:
        """
        Authenticate and return headers for API requests.
        
        Returns:
            Dictionary of authentication headers
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # If we have an access token, use it directly
        if self._access_token:
            return {"Authorization": f"Bearer {self._access_token}"}
        
        # If we have username/password, create a session
        if self.config.username and self.config.password:
            await self._create_session()
            if self._access_token:
                return {"Authorization": f"Bearer {self._access_token}"}
        
        raise AuthenticationError("No valid authentication method available")
    
    async def _create_session(self) -> None:
        """Create a new session using username/password."""
        if not (self.config.username and self.config.password):
            raise AuthenticationError("Username and password required for session creation")
        
        session_data = {
            "password_credentials": {
                "username": self.config.username,
                "password": self.config.password
            }
        }
        
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                response = await client.post(
                    f"{self.config.api_base_url}/auth/sessions",
                    json=session_data,
                    headers=self.config.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._session_data = data
                    
                    # Extract access token from session response if available
                    # In real implementation, you might need to generate a JWT or get it from response
                    if "access_token" in data:
                        self._access_token = data["access_token"]
                    
                    # Set session expiration (typically 2 weeks from last access)
                    self._session_expires_at = datetime.now() + timedelta(weeks=2)
                    
                else:
                    error_msg = "Authentication failed"
                    try:
                        error_data = response.json()
                        if "message" in error_data:
                            error_msg = error_data["message"]
                    except:
                        pass
                    
                    raise AuthenticationError(
                        error_msg,
                        status_code=response.status_code,
                        response_data=response.json() if response.content else {}
                    )
                    
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to connect to authentication endpoint: {e}", e)
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Unexpected error during authentication: {e}")
    
    async def get_current_session(self) -> Optional[Dict[str, Any]]:
        """
        Get current session information.
        
        Returns:
            Session data if authenticated, None otherwise
        """
        if not self._access_token:
            return None
        
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                headers = await self.authenticate()
                response = await client.get(
                    f"{self.config.api_base_url}/auth/sessions/current",
                    headers={**self.config.headers, **headers}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception:
            return None
    
    async def refresh_session(self) -> None:
        """Refresh the current session if needed."""
        if self._session_expires_at and datetime.now() >= self._session_expires_at:
            # Session expired, need to re-authenticate
            if self.config.username and self.config.password:
                await self._create_session()
            else:
                raise AuthenticationError("Session expired and no credentials available for refresh")
    
    async def logout(self) -> None:
        """Logout and invalidate the current session."""
        if not self._access_token:
            return
        
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                headers = await self.authenticate()
                await client.delete(
                    f"{self.config.api_base_url}/auth/sessions/current",
                    headers={**self.config.headers, **headers}
                )
        except Exception:
            # Ignore errors during logout
            pass
        finally:
            self._access_token = None
            self._session_data = None
            self._session_expires_at = None
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return bool(self._access_token)
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user information from session data."""
        if self._session_data and "user" in self._session_data:
            return self._session_data["user"]
        return None
    
    def _decode_jwt_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode JWT payload (for informational purposes only).
        
        Note: This doesn't verify the signature, only decodes the payload.
        """
        try:
            # JWT has 3 parts separated by dots
            parts = token.split(".")
            if len(parts) != 3:
                return None
            
            # Decode the payload (second part)
            payload = parts[1]
            # Add padding if needed
            padding = len(payload) % 4
            if padding:
                payload += "=" * (4 - padding)
            
            decoded_bytes = base64.urlsafe_b64decode(payload)
            return json.loads(decoded_bytes.decode("utf-8"))
        except Exception:
            return None
