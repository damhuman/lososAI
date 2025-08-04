from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import logging
from typing import Optional
from datetime import datetime

from app.core.config import settings

router = APIRouter()

logger = logging.getLogger(__name__)

class ErrorReport(BaseModel):
    error_type: str
    message: str
    user_id: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None

@router.post("/report")
async def report_error(error_report: ErrorReport):
    """
    Report an error from the frontend and notify admin
    """
    try:
        # Log the error
        logger.error(f"Frontend error reported: {error_report.error_type} - {error_report.message}")
        
        # Send notification to admin chat via Telegram Bot API
        await send_admin_notification(error_report)
        
        return {"status": "success", "message": "Error reported successfully"}
        
    except Exception as e:
        logger.error(f"Failed to report error: {str(e)}")
        # Don't fail the request even if notification fails
        return {"status": "partial", "message": "Error logged but notification failed"}

async def send_admin_notification(error_report: ErrorReport):
    """
    Send error notification to admin chat via Telegram Bot API
    """
    if not settings.ADMIN_CHAT_ID:
        logger.warning("ADMIN_CHAT_ID not configured, skipping notification")
        return
    
    # Format error message for admin
    timestamp = error_report.timestamp or datetime.now()
    message = f"""
🚨 *Webapp Error Report*

*Type:* {error_report.error_type}
*Message:* {error_report.message}
*Time:* {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
*User ID:* {error_report.user_id or 'Unknown'}
*URL:* {error_report.url or 'Unknown'}
*User Agent:* {error_report.user_agent or 'Unknown'}

Please check the system logs for more details.
    """.strip()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": settings.ADMIN_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send admin notification: {response.text}")
            else:
                logger.info("Admin notification sent successfully")
                
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Simple health check endpoint for frontend to test API connectivity
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "seafood-store-api"
    }