from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied


def role_required(required_role):
    """
    Decorator برای بررسی نقش کاربر
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'برای دسترسی به این صفحه باید وارد شوید.')
                return redirect('user_login')
            
            # بررسی وجود پروفایل کاربر
            if not hasattr(request.user, 'userprofile'):
                messages.error(request, 'پروفایل کاربری شما یافت نشد. لطفاً با مدیر سیستم تماس بگیرید.')
                return redirect('user_login')
            
            user_profile = request.user.userprofile
            
            # بررسی نقش مورد نیاز
            if required_role == 'technical_admin' and not user_profile.is_technical_admin:
                messages.error(request, 'شما دسترسی لازم برای این صفحه را ندارید.')
                return redirect('user_dashboard')
            
            elif required_role == 'end_user' and not user_profile.is_end_user:
                messages.error(request, 'شما دسترسی لازم برای این صفحه را ندارید.')
                return redirect('user_dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def technical_admin_required(view_func):
    """
    Decorator برای دسترسی مدیر فنی - ساده شده
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'برای دسترسی به این صفحه باید وارد شوید.')
            return redirect('user_login')
        
        # بررسی دسترسی مدیر فنی - ساده شده
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'شما دسترسی لازم برای این صفحه را ندارید. فقط مدیر فنی می‌تواند به این بخش دسترسی داشته باشد.')
            return redirect('user_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def end_user_required(view_func):
    """
    Decorator برای دسترسی کاربر نهایی - ساده شده
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'برای دسترسی به این صفحه باید وارد شوید.')
            return redirect('user_login')
        
        # بررسی دسترسی کاربر نهایی - ساده شده
        if request.user.is_staff or request.user.is_superuser:
            # مدیر فنی هم می‌تواند به صفحات کاربر نهایی دسترسی داشته باشد
            pass
        
        return view_func(request, *args, **kwargs)
    return wrapper


def dashboard_access_required(view_func):
    """
    Decorator برای دسترسی به داشبورد - ساده شده
    همه کاربران می‌توانند به داشبورد دسترسی داشته باشند
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'برای دسترسی به داشبورد باید وارد شوید.')
            return redirect('user_login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def api_permission_required(permission_type='read'):
    """
    Decorator برای کنترل دسترسی API
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden('Authentication required')
            
            # بررسی وجود پروفایل کاربر
            if not hasattr(request.user, 'userprofile'):
                return HttpResponseForbidden('User profile not found')
            
            user_profile = request.user.userprofile
            
            # بررسی دسترسی بر اساس نوع درخواست
            if permission_type == 'write' and not user_profile.is_technical_admin:
                return HttpResponseForbidden('Write access denied. Technical admin required.')
            
            elif permission_type == 'admin' and not user_profile.is_technical_admin:
                return HttpResponseForbidden('Admin access denied. Technical admin required.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
