"""
Security utilities - Password hashing, JWT tokens, encryption.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import SecretStr

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# JWT Token handling
def create_access_token(
    subject: UUID,
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: UUID) -> str:
    """Create a JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[UUID]:
    """Verify a token and return the subject UUID."""
    payload = decode_token(token)
    if not payload:
        return None
    if payload.get("type") != token_type:
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        return UUID(sub)
    except ValueError:
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """Get token expiry datetime."""
    payload = decode_token(token)
    if not payload:
        return None
    exp = payload.get("exp")
    if not exp:
        return None
    return datetime.utcfromtimestamp(exp)


# API Key generation
def generate_api_key() -> str:
    """Generate a secure API key."""
    import secrets
    return f"kt_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return get_password_hash(api_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return verify_password(plain_key, hashed_key)


# Encryption utilities (for sensitive data at rest)
from cryptography.fernet import Fernet
import base64


def get_encryption_key() -> bytes:
    """Get or generate encryption key from settings."""
    # In production, this should come from a secure key management system
    key = settings.SECRET_KEY[:32].encode()
    # Fernet requires 32 url-safe base64-encoded bytes
    return base64.urlsafe_b64encode(key.ljust(32, b'0')[:32])


_cipher_suite = None


def get_cipher_suite() -> Fernet:
    """Get the Fernet cipher suite."""
    global _cipher_suite
    if _cipher_suite is None:
        _cipher_suite = Fernet(get_encryption_key())
    return _cipher_suite


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    cipher = get_cipher_suite()
    encrypted = cipher.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    cipher = get_cipher_suite()
    decoded = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = cipher.decrypt(decoded)
    return decrypted.decode()


# Rate limiting key generation
def get_rate_limit_key(identifier: str, endpoint: str) -> str:
    """Generate a rate limit key."""
    return f"ratelimit:{endpoint}:{identifier}"


# CSRF token generation
def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    import secrets
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify a CSRF token."""
    import hmac
    return hmac.compare_digest(token, expected)