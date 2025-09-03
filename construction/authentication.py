"""
سیستم احراز هویت پیشرفته
Advanced Authentication System for Construction Project
"""

import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets

logger = logging.getLogger('django.security')

class EnhancedAuthenticationBackend(ModelBackend):
    """
    سیستم احراز هویت پیشرفته با ویژگی‌های امنیتی
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        احراز هویت با بررسی‌های امنیتی اضافی
        """
        
        if username is None or password is None:
            return None
        
        try:
            # بررسی وجود کاربر
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # ثبت تلاش ورود ناموفق
            self.log_failed_attempt(request, username, "User not found")
            return None
        
        # بررسی فعال بودن کاربر
        if not user.is_active:
            self.log_failed_attempt(request, username, "User inactive")
            return None
        
        # بررسی قفل بودن حساب
        if self.is_account_locked(user):
            self.log_failed_attempt(request, username, "Account locked")
            return None
        
        # بررسی رمز عبور
        if user.check_password(password):
            # ورود موفق
            self.log_successful_login(request, user)
            self.reset_failed_attempts(user)
            return user
        else:
            # ورود ناموفق
            self.log_failed_attempt(request, username, "Invalid password")
            self.increment_failed_attempts(user)
            return None
    
    def log_successful_login(self, request, user):
        """ثبت ورود موفق"""
        ip_address = self.get_client_ip(request)
        logger.info(f"Successful login: {user.username} from {ip_address}")
        
        # به‌روزرسانی آخرین ورود
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
    
    def log_failed_attempt(self, request, username, reason):
        """ثبت تلاش ورود ناموفق"""
        ip_address = self.get_client_ip(request)
        logger.warning(f"Failed login attempt: {username} from {ip_address} - Reason: {reason}")
    
    def is_account_locked(self, user):
        """بررسی قفل بودن حساب"""
        # استفاده از cache به جای فیلدهای مدل
        from django.core.cache import cache
        
        cache_key = f"failed_attempts_{user.username}"
        failed_data = cache.get(cache_key, {'count': 0, 'last_attempt': None})
        
        max_attempts = 5  # حداکثر 5 تلاش
        failed_attempts = failed_data.get('count', 0)
        
        if failed_attempts >= max_attempts:
            # بررسی زمان قفل
            last_attempt = failed_data.get('last_attempt')
            if last_attempt:
                lock_duration = timedelta(minutes=30)  # 30 دقیقه قفل
                if timezone.now() - last_attempt < lock_duration:
                    return True
                else:
                    # باز کردن قفل
                    self.reset_failed_attempts(user)
        
        return False
    
    def increment_failed_attempts(self, user):
        """افزایش تعداد تلاش‌های ناموفق"""
        from django.core.cache import cache
        
        cache_key = f"failed_attempts_{user.username}"
        failed_data = cache.get(cache_key, {'count': 0, 'last_attempt': None})
        
        failed_data['count'] = failed_data.get('count', 0) + 1
        failed_data['last_attempt'] = timezone.now()
        
        # ذخیره در cache برای 1 ساعت
        cache.set(cache_key, failed_data, 3600)
    
    def reset_failed_attempts(self, user):
        """بازنشانی تعداد تلاش‌های ناموفق"""
        from django.core.cache import cache
        
        cache_key = f"failed_attempts_{user.username}"
        cache.delete(cache_key)
    
    def get_client_ip(self, request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class TwoFactorAuthentication:
    """
    سیستم احراز هویت دو مرحله‌ای
    """
    
    @staticmethod
    def generate_secret():
        """تولید کلید مخفی برای 2FA"""
        return secrets.token_hex(16)
    
    @staticmethod
    def generate_backup_codes(count=10):
        """تولید کدهای پشتیبان"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    @staticmethod
    def verify_totp_code(secret, code):
        """بررسی کد TOTP"""
        # پیاده‌سازی ساده - در production از کتابخانه‌های تخصصی استفاده کنید
        import time
        import hmac
        import hashlib
        import base64
        
        # تبدیل کلید مخفی
        key = base64.b32decode(secret)
        
        # محاسبه زمان فعلی
        current_time = int(time.time() // 30)
        
        # بررسی کد برای زمان فعلی و ±1
        for time_offset in [-1, 0, 1]:
            time_counter = current_time + time_offset
            
            # تولید کد
            hmac_hash = hmac.new(key, time_counter.to_bytes(8, 'big'), hashlib.sha1).digest()
            offset = hmac_hash[-1] & 0x0f
            code_generated = ((hmac_hash[offset] & 0x7f) << 24 |
                            (hmac_hash[offset + 1] & 0xff) << 16 |
                            (hmac_hash[offset + 2] & 0xff) << 8 |
                            (hmac_hash[offset + 3] & 0xff)) % 1000000
            
            if code_generated == int(code):
                return True
        
        return False

class PasswordSecurity:
    """
    کلاس امنیت رمز عبور
    """
    
    @staticmethod
    def validate_password_strength(password):
        """
        بررسی قدرت رمز عبور
        """
        errors = []
        
        # طول رمز عبور
        if len(password) < 12:
            errors.append("رمز عبور باید حداقل 12 کاراکتر باشد")
        
        # وجود حروف بزرگ
        if not any(c.isupper() for c in password):
            errors.append("رمز عبور باید شامل حروف بزرگ باشد")
        
        # وجود حروف کوچک
        if not any(c.islower() for c in password):
            errors.append("رمز عبور باید شامل حروف کوچک باشد")
        
        # وجود اعداد
        if not any(c.isdigit() for c in password):
            errors.append("رمز عبور باید شامل اعداد باشد")
        
        # وجود کاراکترهای خاص
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("رمز عبور باید شامل کاراکترهای خاص باشد")
        
        # بررسی رمزهای رایج
        common_passwords = [
            'password', '123456', 'qwerty', 'admin', 'letmein',
            'welcome', 'monkey', '1234567890', 'password123'
        ]
        
        if password.lower() in common_passwords:
            errors.append("رمز عبور انتخاب شده رایج است")
        
        return errors
    
    @staticmethod
    def generate_secure_password(length=16):
        """
        تولید رمز عبور امن
        """
        import string
        import secrets
        
        # کاراکترهای مجاز
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # تولید رمز عبور
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        # اطمینان از وجود انواع کاراکترها
        while True:
            errors = PasswordSecurity.validate_password_strength(password)
            if not errors:
                break
            password = ''.join(secrets.choice(characters) for _ in range(length))
        
        return password

class SessionSecurity:
    """
    کلاس امنیت جلسه
    """
    
    @staticmethod
    def create_secure_session(request, user):
        """
        ایجاد جلسه امن
        """
        # تنظیمات جلسه
        request.session.set_expiry(3600)  # 1 ساعت
        request.session['user_id'] = user.id
        request.session['login_time'] = timezone.now().isoformat()
        request.session['ip_address'] = SessionSecurity.get_client_ip(request)
        request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # تولید شناسه جلسه جدید
        request.session.cycle_key()
    
    @staticmethod
    def validate_session(request):
        """
        بررسی اعتبار جلسه
        """
        if not request.user.is_authenticated:
            return False
        
        # بررسی IP
        stored_ip = request.session.get('ip_address')
        current_ip = SessionSecurity.get_client_ip(request)
        
        if stored_ip != current_ip:
            logger.warning(f"Session IP mismatch for user {request.user.username}")
            return False
        
        # بررسی User Agent
        stored_ua = request.session.get('user_agent')
        current_ua = request.META.get('HTTP_USER_AGENT', '')
        
        if stored_ua != current_ua:
            logger.warning(f"Session User Agent mismatch for user {request.user.username}")
            return False
        
        return True
    
    @staticmethod
    def get_client_ip(request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
