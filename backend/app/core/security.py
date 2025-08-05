from datetime import datetime, timedelta
from typing import Any, Union, Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models.admin import AdminUser

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify JWT token and return subject if valid"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        token_type_payload: str = payload.get("type")
        
        if subject is None or token_type_payload != token_type:
            return None
        return subject
    except jwt.PyJWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


async def authenticate_admin(session: AsyncSession, username: str, password: str) -> Optional[AdminUser]:
    """Authenticate admin user with username/password"""
    query = select(AdminUser).where(
        AdminUser.username == username,
        AdminUser.is_active == True
    )
    result = await session.execute(query)
    admin = result.scalar_one_or_none()
    
    if not admin:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


async def get_admin_by_id(session: AsyncSession, admin_id: int) -> Optional[AdminUser]:
    """Get admin user by ID"""
    query = select(AdminUser).where(
        AdminUser.id == admin_id,
        AdminUser.is_active == True
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()