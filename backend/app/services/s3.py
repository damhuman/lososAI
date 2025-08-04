import os
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from PIL import Image
import io
from fastapi import HTTPException, UploadFile

from app.core.config import settings


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.public_url = settings.S3_PUBLIC_URL
    
    async def upload_image(
        self, 
        file: UploadFile, 
        folder: str = "products",
        max_size_mb: int = 5,
        max_width: int = 1200,
        max_height: int = 1200
    ) -> str:
        """
        Upload and optimize image to S3
        
        Args:
            file: FastAPI UploadFile
            folder: S3 folder name
            max_size_mb: Maximum file size in MB
            max_width: Maximum image width in pixels
            max_height: Maximum image height in pixels
            
        Returns:
            Public URL of uploaded image
        """
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Read file content
            content = await file.read()
            
            # Validate file size
            if len(content) > max_size_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File size too large. Maximum {max_size_mb}MB allowed"
                )
            
            # Process image with Pillow
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Generate unique filename
            file_extension = 'jpg'  # Always convert to JPG for consistency
            filename = f"{folder}/{uuid.uuid4().hex}.{file_extension}"
            
            # Convert to bytes
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=85, optimize=True)
            optimized_content = output_buffer.getvalue()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=optimized_content,
                ContentType='image/jpeg',
                ACL='public-read'
            )
            
            # Return public URL
            return f"{self.public_url}/{filename}"
            
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
    
    async def delete_image(self, image_url: str) -> bool:
        """
        Delete image from S3 by URL
        
        Args:
            image_url: Full public URL of the image
            
        Returns:
            True if deleted successfully
        """
        try:
            # Extract key from URL
            if not image_url.startswith(self.public_url):
                return False
            
            key = image_url.replace(f"{self.public_url}/", "")
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            return True
            
        except ClientError:
            return False
    
    def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for private file access
        
        Args:
            key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")


# Global instance
s3_service = S3Service()