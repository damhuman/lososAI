from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.telegram_auth import TelegramAuth
from app.core.security import verify_token, get_admin_by_id
from app.db.session import get_async_session
from app.db.models.user import User
from app.db.models.admin import AdminUser


# Initialize Telegram auth
telegram_auth = TelegramAuth(settings.TELEGRAM_BOT_TOKEN)


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Get current user from Telegram Web App init data
    Expects header: Authorization: tma <init_data>
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        auth_type, init_data = authorization.split(" ", 1)
        if auth_type.lower() != "tma":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization type. Expected 'tma'"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Validate init data
    validated_data = telegram_auth.validate_init_data(init_data)
    user_data = validated_data["user"]
    
    # Get or create user
    user_id = user_data["id"]
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            id=user_id,
            first_name=user_data["first_name"],
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            language_code=user_data.get("language_code", "uk")
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Update user info if changed
        updated = False
        if user.first_name != user_data["first_name"]:
            user.first_name = user_data["first_name"]
            updated = True
        if user.last_name != user_data.get("last_name"):
            user.last_name = user_data.get("last_name")
            updated = True
        if user.username != user_data.get("username"):
            user.username = user_data.get("username")
            updated = True
        if user.language_code != user_data.get("language_code", "uk"):
            user.language_code = user_data.get("language_code", "uk")
            updated = True
            
        if updated:
            await session.commit()
            await session.refresh(user)
    
    # Check if user is blocked
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked"
        )
    
    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    session: AsyncSession = Depends(get_async_session)
) -> Optional[User]:
    """Get current user, but don't require authentication"""
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, session)
    except HTTPException:
        return None


# JWT Bearer scheme for admin authentication
bearer_scheme = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session)
) -> AdminUser:
    """Get current admin user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    
    # Verify the access token
    admin_id = verify_token(credentials.credentials, token_type="access")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get admin user from database
    admin = await get_admin_by_id(session, int(admin_id))
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive"
        )
    
    return admin