from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.api.deps import get_async_session, get_current_admin
from app.core.security import (
    authenticate_admin, create_access_token, create_refresh_token, 
    verify_token, get_admin_by_id
)
from app.db.models.admin import AdminUser
from app.schemas.admin import (
    AdminLogin, TokenResponse, TokenRefresh, AdminUserResponse, LoginResponse
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def admin_login(
    login_data: AdminLogin,
    session: AsyncSession = Depends(get_async_session)
):
    """Admin login endpoint - authenticate and return JWT tokens"""
    # Authenticate admin
    admin = await authenticate_admin(session, login_data.username, login_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Update last login timestamp
    await session.execute(
        update(AdminUser)
        .where(AdminUser.id == admin.id)
        .values(last_login=datetime.utcnow())
    )
    await session.commit()
    await session.refresh(admin)  # Refresh to get updated last_login
    
    # Create tokens
    access_token = create_access_token(subject=admin.id)
    refresh_token = create_refresh_token(subject=admin.id)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes in seconds
        admin=AdminUserResponse.model_validate(admin)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(get_async_session)
):
    """Refresh access token using refresh token"""
    # Verify refresh token
    admin_id = verify_token(token_data.refresh_token, token_type="refresh")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Check if admin still exists and is active
    admin = await get_admin_by_id(session, int(admin_id))
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(subject=admin.id)
    refresh_token = create_refresh_token(subject=admin.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes in seconds
    )


@router.post("/logout")
async def admin_logout():
    """Admin logout endpoint - client should discard tokens"""
    # In a production app, you might want to maintain a token blacklist
    # For now, we rely on the client to discard the tokens
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin_info(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get current admin user information"""
    return AdminUserResponse.model_validate(current_admin)