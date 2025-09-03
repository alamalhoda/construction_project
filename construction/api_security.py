"""
سیستم امنیتی API
API Security System for Construction Project
"""

from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger('django.security')

class APISecurityPermission(permissions.BasePermission):
    """
    مجوز امنیتی سفارشی برای API
    """
    
    def has_permission(self, request, view):
        """
        بررسی مجوز دسترسی به API
        """
        
        # در محیط development، اجازه دسترسی بدون احراز هویت برای همه درخواست‌ها
        if settings.DEBUG:
            logger.info(f"Development mode: Allowing {request.method} request to {request.path} without authentication")
            return True
        
        # در محیط production، بررسی احراز هویت برای همه درخواست‌ها
        if not request.user.is_authenticated:
            logger.warning(f"Production mode: Unauthenticated {request.method} request to {request.path} from {self.get_client_ip(request)}")
            return False
        
        # بررسی فعال بودن کاربر
        if not request.user.is_active:
            logger.warning(f"Inactive user API access attempt: {request.user.username}")
            return False
        
        # بررسی دسترسی به API
        if not self.has_api_access(request.user):
            logger.warning(f"User {request.user.username} attempted API access without permission")
            return False
        
        # ثبت دسترسی موفق
        logger.info(f"Successful API access: {request.user.username} from {self.get_client_ip(request)}")
        return True
    
    def has_api_access(self, user):
        """
        بررسی دسترسی کاربر به API
        """
        # کاربران staff و superuser دسترسی کامل دارند
        if user.is_staff or user.is_superuser:
            return True
        
        # بررسی دسترسی‌های سفارشی
        # می‌توانید اینجا منطق سفارشی اضافه کنید
        return True
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ReadOnlyPermission(permissions.BasePermission):
    """
    مجوز فقط خواندنی برای API
    """
    
    def has_permission(self, request, view):
        """
        بررسی مجوز فقط خواندنی
        """
        
        # فقط کاربران احراز هویت شده
        if not request.user.is_authenticated:
            return False
        
        # فقط درخواست‌های GET مجاز
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # برای سایر درخواست‌ها، کاربر باید staff باشد
        return request.user.is_staff

class AdminOnlyPermission(permissions.BasePermission):
    """
    مجوز فقط برای ادمین‌ها
    """
    
    def has_permission(self, request, view):
        """
        بررسی مجوز ادمین
        """
        
        # فقط کاربران احراز هویت شده
        if not request.user.is_authenticated:
            return False
        
        # فقط staff و superuser
        return request.user.is_staff or request.user.is_superuser

class APIThrottlePermission(permissions.BasePermission):
    """
    مجوز محدودیت نرخ درخواست برای API
    """
    
    def has_permission(self, request, view):
        """
        بررسی محدودیت نرخ درخواست
        """
        
        # بررسی محدودیت نرخ درخواست
        if self.is_rate_limited(request):
            logger.warning(f"Rate limit exceeded for user {request.user.username if request.user.is_authenticated else 'anonymous'}")
            return False
        
        return True
    
    def is_rate_limited(self, request):
        """
        بررسی محدودیت نرخ درخواست
        """
        # پیاده‌سازی ساده - در production بهتر است از cache استفاده شود
        # فعلاً False برمی‌گردانیم (بدون محدودیت)
        return False

class SecureAPIAuthentication(SessionAuthentication):
    """
    احراز هویت امن برای API
    """
    
    def authenticate(self, request):
        """
        احراز هویت امن
        """
        
        # احراز هویت معمولی
        user_auth_tuple = super().authenticate(request)
        
        if user_auth_tuple is None:
            return None
        
        user, auth = user_auth_tuple
        
        # بررسی‌های امنیتی اضافی
        if not self.is_secure_request(request, user):
            return None
        
        return user_auth_tuple
    
    def is_secure_request(self, request, user):
        """
        بررسی امنیت درخواست
        """
        
        # بررسی IP
        client_ip = self.get_client_ip(request)
        if self.is_blocked_ip(client_ip):
            logger.warning(f"Blocked IP attempted API access: {client_ip}")
            return False
        
        # بررسی User Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if self.is_suspicious_user_agent(user_agent):
            logger.warning(f"Suspicious user agent detected: {user_agent}")
            return False
        
        # بررسی جلسه
        if not self.is_valid_session(request, user):
            logger.warning(f"Invalid session for user: {user.username}")
            return False
        
        return True
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_blocked_ip(self, ip):
        """
        بررسی IP مسدود شده
        """
        # لیست IP های مسدود شده
        blocked_ips = [
            # می‌توانید IP های مسدود شده را اینجا اضافه کنید
        ]
        return ip in blocked_ips
    
    def is_suspicious_user_agent(self, user_agent):
        """
        بررسی User Agent مشکوک
        """
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper',
            'curl', 'wget', 'python-requests',
            'sqlmap', 'nikto', 'nmap'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def is_valid_session(self, request, user):
        """
        بررسی اعتبار جلسه
        """
        # بررسی زمان جلسه
        if hasattr(request, 'session'):
            session_key = request.session.session_key
            if session_key:
                # بررسی زمان آخرین فعالیت
                last_activity = request.session.get('last_activity')
                if last_activity:
                    last_activity_time = timezone.datetime.fromisoformat(last_activity)
                    if timezone.now() - last_activity_time > timedelta(hours=2):
                        return False
        
        return True

class APIViewSetMixin:
    """
    Mixin برای ViewSet های امن
    """
    
    authentication_classes = [SecureAPIAuthentication, TokenAuthentication]
    permission_classes = [APISecurityPermission]
    
    def get_permissions(self):
        """
        تنظیم مجوزها بر اساس action
        """
        if self.action == 'list' or self.action == 'retrieve':
            # فقط خواندنی
            permission_classes = [ReadOnlyPermission]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # فقط ادمین‌ها
            permission_classes = [AdminOnlyPermission]
        else:
            # مجوز پیش‌فرض
            permission_classes = [APISecurityPermission]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        ایجاد رکورد با ثبت اطلاعات کاربر
        """
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """
        به‌روزرسانی رکورد با ثبت اطلاعات کاربر
        """
        serializer.save(updated_by=self.request.user)
    
    def get_queryset(self):
        """
        فیلتر کردن queryset بر اساس کاربر
        """
        queryset = super().get_queryset()
        
        # اگر کاربر ادمین نیست، فقط رکوردهای خودش را ببیند
        if not self.request.user.is_staff:
            # اینجا می‌توانید منطق فیلتر کردن را اضافه کنید
            pass
        
        return queryset
