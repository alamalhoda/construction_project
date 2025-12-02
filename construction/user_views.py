"""
View های مربوط به کاربران نهایی
User Views for Construction Project
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django import forms
import logging
from .decorators import technical_admin_required, end_user_required, dashboard_access_required

logger = logging.getLogger(__name__)

class UserRegistrationForm(UserCreationForm):
    """فرم ثبت نام کاربران"""
    email = forms.EmailField(required=True, label='ایمیل')
    first_name = forms.CharField(max_length=30, required=True, label='نام')
    last_name = forms.CharField(max_length=30, required=True, label='نام خانوادگی')
    
    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'نام کاربری',
            'password1': 'رمز عبور',
            'password2': 'تکرار رمز عبور',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اضافه کردن کلاس‌های CSS
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'لطفاً {field.label} را وارد کنید'

@csrf_protect
@never_cache
def user_login_view(request):
    """صفحه لاگین کاربران نهایی"""
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # تنظیم session بر اساس remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # session فقط تا بسته شدن مرورگر
                    else:
                        request.session.set_expiry(1209600)  # 2 هفته
                    
                    # ثبت لاگ ورود موفق
                    logger.info(f"User {username} logged in successfully from IP: {request.META.get('REMOTE_ADDR')}")
                    
                    # هدایت به صفحه بعد از لاگین
                    next_url = request.GET.get('next', 'user_dashboard')
                    # اگر next_url با / شروع می‌شود، آن را مستقیماً استفاده کن
                    if next_url.startswith('/'):
                        return redirect(next_url)
                    else:
                        return redirect(next_url)
                else:
                    messages.error(request, 'حساب کاربری شما غیرفعال است.')
                    logger.warning(f"Login attempt for inactive user: {username}")
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
                logger.warning(f"Failed login attempt for username: {username} from IP: {request.META.get('REMOTE_ADDR')}")
        else:
            messages.error(request, 'لطفاً تمام فیلدها را پر کنید.')
    
    return render(request, 'construction/user_login.html')

@csrf_protect
def user_register_view(request):
    """صفحه ثبت نام کاربران"""
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # استفاده از commit=False برای تنظیم is_active
            user.email = form.cleaned_data.get('email')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.is_active = False  # کاربر جدید به صورت پیش‌فرض غیرفعال است
            user.save()
            
            # لاگ کردن ثبت نام موفق
            logger.info(f"New user registered (inactive): {user.username} ({user.email})")
            
            messages.success(request, 'ثبت نام با موفقیت انجام شد. حساب کاربری شما در انتظار تایید مدیر است. پس از تایید می‌توانید وارد شوید.')
            return redirect('user_login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'construction/user_register.html', {'form': form})

@login_required
def user_logout_view(request):
    """خروج از سیستم"""
    username = request.user.username
    logout(request)
    logger.info(f"User {username} logged out")
    messages.success(request, 'با موفقیت از سیستم خارج شدید.')
    return redirect('user_login')

# user_dashboard_view منتقل شده به dashboard/views.py
# @dashboard_access_required
# def user_dashboard_view(request):
#     """داشبورد کاربران - منتقل شده به dashboard app"""
#     # این view به dashboard/views.py منتقل شده است
#     from dashboard.views import user_dashboard
#     return user_dashboard(request)

@login_required
def user_profile_view(request):
    """پروفایل کاربر"""
    if request.method == 'POST':
        # به‌روزرسانی اطلاعات کاربر
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'اطلاعات پروفایل با موفقیت به‌روزرسانی شد.')
        return redirect('user_profile')
    
    return render(request, 'construction/user_profile.html', {'user': request.user})

@login_required
def change_password_view(request):
    """تغییر رمز عبور"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        if not user.check_password(old_password):
            messages.error(request, 'رمز عبور فعلی اشتباه است.')
        elif new_password != confirm_password:
            messages.error(request, 'رمز عبور جدید و تکرار آن مطابقت ندارند.')
        elif len(new_password) < 8:
            messages.error(request, 'رمز عبور باید حداقل 8 کاراکتر باشد.')
        else:
            user.set_password(new_password)
            user.save()
            
            # لاگ کردن تغییر رمز عبور
            logger.info(f"User {user.username} changed password")
            
            messages.success(request, 'رمز عبور با موفقیت تغییر کرد.')
            return redirect('user_profile')
    
    return render(request, 'construction/change_password.html')

# View های محافظت شده برای صفحات اصلی - ساده شده
@method_decorator(technical_admin_required, name='dispatch')
class ProtectedIndexView(TemplateView):
    """صفحه اصلی محافظت شده - فقط مدیر فنی"""
    template_name = 'construction/protected_index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context



# API endpoints برای JavaScript
@login_required
def user_info_api(request):
    """API برای دریافت اطلاعات کاربر"""
    user = request.user
    return JsonResponse({
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_authenticated': user.is_authenticated,
        'last_login': user.last_login.isoformat() if user.last_login else None,
    })

@login_required
def user_logout_api(request):
    """API برای خروج از سیستم"""
    username = request.user.username
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'با موفقیت از سیستم خارج شدید.'
    })
