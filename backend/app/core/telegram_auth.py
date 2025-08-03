import hashlib
import hmac
import json
import time
from typing import Dict, Optional
from urllib.parse import parse_qs

from fastapi import HTTPException, status


class TelegramAuth:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        
    def validate_init_data(self, init_data: str) -> Dict:
        """
        Validates Telegram Web App init data
        Returns user data if valid, raises HTTPException if not
        """
        try:
            parsed_data = parse_qs(init_data)
            
            # Extract hash and prepare data for validation
            hash_value = parsed_data.get("hash", [""])[0]
            if not hash_value:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing hash in init data"
                )
            
            # Remove hash from data and sort
            data_check_arr = []
            for key, values in parsed_data.items():
                if key != "hash":
                    data_check_arr.append(f"{key}={values[0]}")
            
            data_check_arr.sort()
            data_check_string = "\n".join(data_check_arr)
            
            # Validate hash
            secret_key = hmac.new(
                b"WebAppData",
                self.bot_token.encode(),
                hashlib.sha256
            ).digest()
            
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if calculated_hash != hash_value:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid init data"
                )
            
            # Check auth_date (prevent replay attacks)
            auth_date = int(parsed_data.get("auth_date", ["0"])[0])
            if auth_date == 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing auth_date"
                )
            
            # Check if data is not older than 1 hour
            if time.time() - auth_date > 3600:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Init data is too old"
                )
            
            # Parse user data
            user_data = json.loads(parsed_data.get("user", ["{}"])[0])
            
            return {
                "user": user_data,
                "auth_date": auth_date,
                "query_id": parsed_data.get("query_id", [""])[0],
                "start_param": parsed_data.get("start_param", [""])[0]
            }
            
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to validate init data: {str(e)}"
            )
    
    def extract_user_id(self, init_data: str) -> Optional[int]:
        """Extract user ID from init data without full validation"""
        try:
            parsed_data = parse_qs(init_data)
            user_data = json.loads(parsed_data.get("user", ["{}"])[0])
            return user_data.get("id")
        except:
            return None