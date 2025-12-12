"""
Helper برای تولید JWT Token برای دستیار هوشمند
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from typing import Optional


def generate_jwt_token(user_id: int, project_id: Optional[int] = None, expires_in_hours: int = 1) -> str:
    """
    تولید JWT Token برای دستیار هوشمند
    
    Args:
        user_id: شناسه کاربر
        project_id: شناسه پروژه (اختیاری)
        expires_in_hours: مدت اعتبار token به ساعت (پیش‌فرض: 1 ساعت)
    
    Returns:
        JWT token به صورت string
    """
    payload = {
        'user_id': user_id,
        'project_id': project_id,
        'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    
    return token
