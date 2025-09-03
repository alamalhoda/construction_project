def test_admin_page_loading():
    """بررسی لود شدن صفحه ادمین"""
    
    print("\n🌐 بررسی لود شدن صفحه ادمین:")
    print("=" * 50)
    
    try:
        import urllib.request
        import urllib.error
        
        # درخواست به صفحه ادمین
        response = urllib.request.urlopen("http://127.0.0.1:8000/admin/", timeout=10)
        
        if response.getcode() == 200:
            print("✅ صفحه ادمین در دسترس است")
            return True
        else:
            print(f"⚠️ وضعیت غیرمنتظره: {response.getcode()}")
            return False
            
    except urllib.error.HTTPError as e:
        if e.code == 302:
            print("✅ صفحه ادمین در دسترس است (redirect به login)")
            return True
        else:
            print(f"⚠️ وضعیت HTTP: {e.code}")
            return False
    except Exception as e:
        print(f"❌ خطا در اتصال به سرور: {e}")
        return False

def test_jalali_settings():
    """بررسی تنظیمات JALALI_SETTINGS"""
    
    print("\n⚙️ بررسی تنظیمات JALALI_SETTINGS:")
    print("=" * 50)
    
    from django.conf import settings
    
    if hasattr(settings, 'JALALI_SETTINGS'):
        jalali_settings = settings.JALALI_SETTINGS
        
        if 'ADMIN_JS_STATIC_FILES' in jalali_settings:
            js_files = jalali_settings['ADMIN_JS_STATIC_FILES']
            print(f"📁 تعداد فایل‌های JavaScript: {len(js_files)}")
            
            # بررسی وجود calendar.all.js
            if 'admin/jquery.ui.datepicker.jalali/scripts/calendar.all.js' in js_files:
                print("✅ calendar.all.js در لیست فایل‌ها موجود است")
                return True
            else:
                print("❌ calendar.all.js در لیست فایل‌ها موجود نیست")
                return False
        else:
            print("❌ ADMIN_JS_STATIC_FILES یافت نشد")
            return False
    else:
        print("❌ JALALI_SETTINGS یافت نشد")
        return False

def test_django_jalali_app():
    """بررسی نصب django-jalali"""
    
    print("\n📦 بررسی نصب django-jalali:")
    print("=" * 50)
    
    from django.conf import settings
    
    if 'django_jalali' in settings.INSTALLED_APPS:
        print("✅ django_jalali در INSTALLED_APPS موجود است")
        
        # بررسی ورژن
        try:
            import django_jalali
            print(f"📋 ورژن django-jalali: {django_jalali.__version__}")
            return True
        except ImportError:
            print("❌ django_jalali قابل import نیست")
            return False
    else:
        print("❌ django_jalali در INSTALLED_APPS موجود نیست")
        return False

if __name__ == "__main__":
    print("🚀 شروع تست رفع مشکل تقویم شمسی")
    print("=" * 60)
    
    # اجرای تست‌ها
    tests = [
        ("فایل‌های JavaScript", test_jalali_js_files),
        ("تنظیمات JALALI", test_jalali_settings),
        ("نصب django-jalali", test_django_jalali_app),
        ("لود صفحه ادمین", test_admin_page_loading),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ خطا در تست {test_name}: {e}")
            results.append((test_name, False))
    
    # خلاصه نتایج
    print("\n" + "=" * 60)
    print("📊 خلاصه نتایج:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 همه تست‌ها موفق بودند!")
        print("📅 تقویم شمسی باید در Django Admin کار کند")
        print("🌐 برای تست: http://127.0.0.1:8000/admin/")
        print("👤 نام کاربری: admin")
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند.")
        print("🔧 لطفاً مشکلات را بررسی کنید.")
    
    print("=" * 60)
