#!/usr/bin/env python
"""
بررسی سریع امنیت - نسخه ساده
Quick Security Check - Simple Version
"""
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from django.conf import settings

def quick_security_check():
    """بررسی سریع و ساده امنیت"""
    
    print("🔒 بررسی سریع امنیت پروژه")
    print("=" * 40)
    
    issues = []
    warnings = []
    good = []
    
    # 1. بررسی DEBUG
    if settings.DEBUG:
        issues.append("❌ DEBUG = True (خطرناک در production)")
    else:
        good.append("✅ DEBUG = False")
    
    # 2. بررسی ALLOWED_HOSTS
    if not settings.ALLOWED_HOSTS:
        issues.append("❌ ALLOWED_HOSTS خالی است")
    else:
        good.append("✅ ALLOWED_HOSTS تنظیم شده")
    
    # 3. بررسی SECRET_KEY
    if len(settings.SECRET_KEY) < 50:
        warnings.append("⚠️ SECRET_KEY کوتاه است")
    else:
        good.append("✅ SECRET_KEY طول مناسب دارد")
    
    # 4. بررسی فایل‌های امنیتی
    security_files = [
        'construction/security_middleware.py',
        'construction/authentication.py',
        'construction/security_monitoring.py',
        'construction/data_protection.py',
        'construction_project/security_settings.py'
    ]
    
    missing_files = []
    for file_path in security_files:
        if os.path.exists(file_path):
            good.append(f"✅ {file_path}")
        else:
            missing_files.append(f"❌ {file_path}")
    
    # 5. بررسی middleware های امنیتی
    security_middleware = [
        'construction.security_middleware.SecurityHeadersMiddleware',
        'construction.security_middleware.AuditLogMiddleware',
        'construction.security_middleware.AdminSecurityMiddleware'
    ]
    
    for middleware in security_middleware:
        if middleware in settings.MIDDLEWARE:
            good.append(f"✅ {middleware}")
        else:
            warnings.append(f"⚠️ {middleware} موجود نیست")
    
    # نمایش نتایج
    print("\n🚨 مشکلات:")
    for issue in issues:
        print(f"  {issue}")
    
    print("\n⚠️ هشدارها:")
    for warning in warnings:
        print(f"  {warning}")
    
    print("\n✅ موارد خوب:")
    for item in good:
        print(f"  {item}")
    
    # خلاصه
    print("\n" + "=" * 40)
    print("📊 خلاصه:")
    print(f"🚨 مشکلات: {len(issues)}")
    print(f"⚠️ هشدارها: {len(warnings)}")
    print(f"✅ موارد خوب: {len(good)}")
    
    if len(issues) == 0:
        print("\n🎉 وضعیت امنیتی خوب است!")
    else:
        print(f"\n⚠️ {len(issues)} مشکل امنیتی نیاز به رفع دارد!")
    
    print("=" * 40)
    
    # پیشنهادات
    print("\n💡 پیشنهادات:")
    if len(issues) > 0:
        print("1. مشکلات امنیتی را رفع کنید")
    if len(warnings) > 0:
        print("2. هشدارها را بررسی کنید")
    print("3. هفته‌ای یک بار این بررسی را انجام دهید")
    print("4. رمز عبور قوی برای ادمین استفاده کنید")
    
    return len(issues), len(warnings), len(good)

if __name__ == "__main__":
    try:
        issues, warnings, good = quick_security_check()
        
        # خروجی با کد مناسب
        if issues > 0:
            sys.exit(1)  # خطا
        elif warnings > 0:
            sys.exit(2)  # هشدار
        else:
            sys.exit(0)  # موفق
            
    except Exception as e:
        print(f"❌ خطا در بررسی امنیت: {e}")
        sys.exit(1)
