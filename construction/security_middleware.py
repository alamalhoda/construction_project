"""
Middleware های امنیتی سفارشی
Custom Security Middleware for Construction Project
"""

import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('django.security')

class AdminSecurityMiddleware(MiddlewareMixin):
    """
    Middleware امنیتی برای Django Admin
    """
    
    def process_request(self, request):
        # بررسی دسترسی به admin
        if request.path.startswith('/admin/'):
            # بررسی IP (در production)
            if hasattr(settings, 'ADMIN_ALLOWED_IPS'):
                client_ip = self.get_client_ip(request)
                if client_ip not in settings.ADMIN_ALLOWED_IPS:
                    logger.warning(f"Admin access attempt from unauthorized IP: {client_ip}")
                    return HttpResponseForbidden("Access denied")
            
            # بررسی User Agent مشکوک
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            if self.is_suspicious_user_agent(user_agent):
                logger.warning(f"Suspicious user agent detected: {user_agent}")
                return HttpResponseForbidden("Access denied")
            
            # بررسی Rate Limiting برای admin
            if self.is_rate_limited(request):
                logger.warning(f"Rate limit exceeded for admin access from IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("Too many requests")
        
        return None
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_suspicious_user_agent(self, user_agent):
        """بررسی User Agent مشکوک"""
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper',
            'curl', 'wget', 'python-requests',
            'sqlmap', 'nikto', 'nmap'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def is_rate_limited(self, request):
        """بررسی Rate Limiting"""
        # پیاده‌سازی ساده Rate Limiting
        # در production بهتر است از Redis استفاده شود
        client_ip = self.get_client_ip(request)
        
        # اینجا می‌توانید از cache یا database برای ذخیره درخواست‌ها استفاده کنید
        # فعلاً فقط True برمی‌گردانیم (بدون محدودیت)
        return False

class LoginAttemptMiddleware(MiddlewareMixin):
    """
    Middleware برای ردیابی تلاش‌های ورود
    """
    
    def process_request(self, request):
        if request.path == '/admin/login/' and request.method == 'POST':
            username = request.POST.get('username', '')
            
            # ثبت تلاش ورود
            logger.info(f"Login attempt for username: {username} from IP: {self.get_client_ip(request)}")
            
            # بررسی تعداد تلاش‌های ناموفق
            if self.has_too_many_failed_attempts(username):
                logger.warning(f"Too many failed login attempts for username: {username}")
                return HttpResponseForbidden("Too many failed login attempts")
        
        return None
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def has_too_many_failed_attempts(self, username):
        """بررسی تعداد تلاش‌های ناموفق"""
        # پیاده‌سازی ساده - در production بهتر است از cache استفاده شود
        # فعلاً False برمی‌گردانیم (بدون محدودیت)
        return False

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware برای اضافه کردن هدرهای امنیتی
    """
    
    def process_response(self, request, response):
        from django.conf import settings
        
        # Content Security Policy - نرم‌تر برای development
        if settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://stackpath.bootstrapcdn.com https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com https://unpkg.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
                "connect-src 'self'; "
                "frame-ancestors 'self';"
            )
        else:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        
        # X-Content-Type-Options
        if not settings.DEBUG:
            response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection
        if not settings.DEBUG:
            response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy - نرم‌تر برای development
        if settings.DEBUG:
            response['Referrer-Policy'] = 'no-referrer-when-downgrade'
        else:
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=(), "
            "vibrate=(), "
            "fullscreen=(self), "
            "sync-xhr=()"
        )
        
        return response

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware برای ثبت فعالیت‌های امنیتی
    """
    
    def process_request(self, request):
        # ثبت درخواست‌های مهم
        if request.path.startswith('/admin/'):
            logger.info(f"Admin access: {request.method} {request.path} from {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        # ثبت پاسخ‌های مهم
        if request.path.startswith('/admin/') and response.status_code >= 400:
            logger.warning(f"Admin error response: {response.status_code} for {request.path}")
        
        return response
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
