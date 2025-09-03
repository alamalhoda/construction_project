"""
Middleware برای محافظت از صفحات کاربران
User Protection Middleware for Construction Project
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class UserAuthenticationMiddleware:
    """
    Middleware برای محافظت از صفحات کاربران
    """
    
    # صفحاتی که نیاز به احراز هویت دارند
    PROTECTED_PATHS = [
        '/construction/',
        '/api/dashboard/',
        '/protected/',
    ]
    
    # صفحاتی که نیاز به احراز هویت ندارند
    PUBLIC_PATHS = [
        '/',
        '/login/',
        '/register/',
        '/admin/',
        '/api/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # بررسی نیاز به احراز هویت
        if self.requires_authentication(request.path):
            if not request.user.is_authenticated:
                # ذخیره URL فعلی برای هدایت بعد از لاگین
                request.session['next'] = request.get_full_path()
                
                # لاگ کردن تلاش دسترسی غیرمجاز
                logger.warning(f"Unauthorized access attempt to {request.path} from IP: {self.get_client_ip(request)}")
                
                # هدایت به صفحه لاگین
                return redirect('user_login')
        
        response = self.get_response(request)
        return response
    
    def requires_authentication(self, path):
        """
        بررسی اینکه آیا مسیر نیاز به احراز هویت دارد یا نه
        """
        # بررسی مسیرهای عمومی
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return False
        
        # بررسی مسیرهای محافظت شده
        for protected_path in self.PROTECTED_PATHS:
            if path.startswith(protected_path):
                return True
        
        return False
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserSessionMiddleware:
    """
    Middleware برای مدیریت session کاربران
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # بررسی session timeout
        if request.user.is_authenticated:
            # به‌روزرسانی last activity
            request.session['last_activity'] = request.session.get('last_activity', 0)
            
            # بررسی timeout (2 ساعت)
            import time
            current_time = time.time()
            last_activity = request.session.get('last_activity', 0)
            
            if current_time - last_activity > 7200:  # 2 ساعت
                # Session منقضی شده
                from django.contrib.auth import logout
                logout(request)
                messages.warning(request, 'جلسه شما منقضی شده است. لطفاً دوباره وارد شوید.')
                return redirect('user_login')
            
            # به‌روزرسانی last activity
            request.session['last_activity'] = current_time
        
        response = self.get_response(request)
        return response
