#!/usr/bin/env python
"""
مدیر امنیت ساده
Simple Security Manager
"""
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

def show_menu():
    """نمایش منوی اصلی"""
    print("\n🛡️ مدیر امنیت پروژه ساختمانی")
    print("=" * 50)
    print("1. بررسی سریع امنیت")
    print("2. بررسی تنظیمات")
    print("3. بررسی داده‌ها")
    print("4. پاک کردن داده‌های قدیمی")
    print("5. نمایش آمار امنیتی")
    print("6. خروج")
    print("=" * 50)

def quick_check():
    """بررسی سریع امنیت"""
    print("\n🔍 بررسی سریع امنیت...")
    
    # اجرای بررسی سریع
    os.system("python quick_security_check.py")
    
    input("\n⏸️ برای ادامه Enter بزنید...")

def settings_check():
    """بررسی تنظیمات"""
    print("\n⚙️ بررسی تنظیمات امنیتی...")
    
    # اجرای بررسی تنظیمات
    os.system("python manage.py security_check --check-type settings")
    
    input("\n⏸️ برای ادامه Enter بزنید...")

def data_check():
    """بررسی داده‌ها"""
    print("\n📊 بررسی داده‌ها...")
    
    # اجرای بررسی داده‌ها
    os.system("python manage.py security_check --check-type data --fix-issues")
    
    input("\n⏸️ برای ادامه Enter بزنید...")

def cleanup_data():
    """پاک کردن داده‌های قدیمی"""
    print("\n🧹 پاک کردن داده‌های قدیمی...")
    
    # اجرای پاک‌سازی
    os.system("python manage.py security_check --check-type cleanup")
    
    input("\n⏸️ برای ادامه Enter بزنید...")

def show_stats():
    """نمایش آمار امنیتی"""
    print("\n📈 آمار امنیتی...")
    
    try:
        from construction.security_monitoring import SecurityMonitor
        
        # دریافت آمار
        dashboard_data = SecurityMonitor.get_security_dashboard_data()
        
        print(f"📊 رویدادهای 24 ساعت گذشته: {dashboard_data['total_events_24h']}")
        print(f"🚨 رویدادهای بحرانی: {dashboard_data['critical_events']}")
        print(f"🔐 تلاش‌های ورود ناموفق: {dashboard_data['failed_logins']}")
        print(f"⚠️ IP های مشکوک: {dashboard_data['suspicious_ips']}")
        
        # نمایش آخرین رویدادها
        print("\n📋 آخرین رویدادها:")
        for event in dashboard_data['recent_events'][:5]:
            print(f"  • {event.event_type} - {event.timestamp.strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        print(f"❌ خطا در دریافت آمار: {e}")
    
    input("\n⏸️ برای ادامه Enter بزنید...")

def main():
    """تابع اصلی"""
    while True:
        show_menu()
        
        try:
            choice = input("\n🔢 انتخاب کنید (1-6): ").strip()
            
            if choice == '1':
                quick_check()
            elif choice == '2':
                settings_check()
            elif choice == '3':
                data_check()
            elif choice == '4':
                cleanup_data()
            elif choice == '5':
                show_stats()
            elif choice == '6':
                print("\n👋 خداحافظ!")
                break
            else:
                print("\n❌ انتخاب نامعتبر! لطفاً عدد 1 تا 6 وارد کنید.")
                
        except KeyboardInterrupt:
            print("\n\n👋 خداحافظ!")
            break
        except Exception as e:
            print(f"\n❌ خطا: {e}")
            input("⏸️ برای ادامه Enter بزنید...")

if __name__ == "__main__":
    main()
