from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from pydantic import BaseModel

from app.db.session import get_async_session
from app.db.models.user import User

router = APIRouter()


class BotUserData(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = "uk"
    is_bot: Optional[bool] = False


class BotInteractionRequest(BaseModel):
    user: BotUserData
    interaction_type: str  # "start", "message", "web_app", "callback"
    message_text: Optional[str] = None
    
    
@router.post("/interactions")
async def record_bot_interaction(
    interaction: BotInteractionRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Record bot interaction and create/update user data"""
    
    # Skip bot users
    if interaction.user.is_bot:
        return {"status": "skipped", "reason": "bot_user"}
    
    user_id = interaction.user.id
    current_time = datetime.utcnow()
    
    # Get existing user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            id=user_id,
            first_name=interaction.user.first_name,
            last_name=interaction.user.last_name,
            username=interaction.user.username,
            language_code=interaction.user.language_code or "uk",
            bot_interactions_count=1,
            first_bot_interaction=current_time,
            last_bot_interaction=current_time
        )
        session.add(user)
        print(f"📝 Created new user: {user.first_name} ({user.id})")
    else:
        # Update existing user
        updated = False
        
        # Update basic info if changed
        if user.first_name != interaction.user.first_name:
            user.first_name = interaction.user.first_name
            updated = True
        if user.last_name != interaction.user.last_name:
            user.last_name = interaction.user.last_name
            updated = True
        if user.username != interaction.user.username:
            user.username = interaction.user.username
            updated = True
        if user.language_code != (interaction.user.language_code or "uk"):
            user.language_code = interaction.user.language_code or "uk"
            updated = True
            
        # Update interaction tracking
        user.bot_interactions_count = (user.bot_interactions_count or 0) + 1
        user.last_bot_interaction = current_time
        
        # Set first interaction if not set
        if not user.first_bot_interaction:
            user.first_bot_interaction = current_time
            
        if updated:
            print(f"📝 Updated user info: {user.first_name} ({user.id})")
        
        print(f"📊 User interaction #{user.bot_interactions_count}: {user.first_name} ({user.id})")
    
    await session.commit()
    await session.refresh(user)
    
    return {
        "status": "recorded",
        "user_id": user.id,
        "interaction_count": user.bot_interactions_count,
        "interaction_type": interaction.interaction_type
    }


@router.get("/users/{user_id}")
async def get_bot_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get user information for bot"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code,
        "is_gold_client": user.is_gold_client,
        "is_blocked": user.is_blocked,
        "bot_interactions_count": user.bot_interactions_count,
        "first_bot_interaction": user.first_bot_interaction,
        "last_bot_interaction": user.last_bot_interaction,
        "created_at": user.created_at
    }


@router.get("/stats")
async def get_bot_stats(session: AsyncSession = Depends(get_async_session)):
    """Get bot usage statistics"""
    
    # Total users
    total_users = await session.execute(select(func.count(User.id)))
    total_users_count = total_users.scalar()
    
    # Users with bot interactions
    bot_users = await session.execute(
        select(func.count(User.id)).where(User.bot_interactions_count > 0)
    )
    bot_users_count = bot_users.scalar()
    
    # Total bot interactions
    total_interactions = await session.execute(
        select(func.sum(User.bot_interactions_count))
    )
    total_interactions_count = total_interactions.scalar() or 0
    
    # Active users (interacted in last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    active_users = await session.execute(
        select(func.count(User.id)).where(User.last_bot_interaction >= week_ago)
    )
    active_users_count = active_users.scalar()
    
    return {
        "total_users": total_users_count,
        "bot_users": bot_users_count,
        "total_bot_interactions": total_interactions_count,
        "active_users_last_7_days": active_users_count,
        "average_interactions_per_user": (
            total_interactions_count / bot_users_count 
            if bot_users_count > 0 else 0
        )
    }