#!/usr/bin/env python3
"""
اسکریپت اجرای دستورات Django با فعال‌سازی خودکار محیط مجازی
استفاده: python3 run_django.py [دستورات Django]
مثال: python3 run_django.py migrate construction
"""

import os
import sys
import subprocess
from pathlib import Path

def check_and_activate_venv():
    """بررسی و فعال‌سازی محیط مجازی"""
    
    # بررسی وجود پوشه env
    env_path = Path("env")
    if not env_path.exists():
        print("❌ پوشه محیط مجازی (env) یافت نشد!")
        print("لطفاً ابتدا محیط مجازی را ایجاد کنید:")
        print("python3 -m venv env")
        sys.exit(1)
    
    # بررسی فعال بودن محیط مجازی
    if not os.environ.get('VIRTUAL_ENV'):
        print("🔄 فعال‌سازی محیط مجازی...")
        
        # مسیر Python در محیط مجازی
        venv_python = env_path / "bin" / "python3"
        if not venv_python.exists():
            venv_python = env_path / "bin" / "python"
        
        if not venv_python.exists():
            print("❌ Python در محیط مجازی یافت نشد!")
            sys.exit(1)
        
        # اجرای دستور با Python محیط مجازی
        return str(venv_python)
    else:
        print("✅ محیط مجازی قبلاً فعال است")
        return sys.executable

def main():
    if len(sys.argv) < 2:
        print("استفاده: python3 run_django.py [دستورات Django]")
        print("مثال: python3 run_django.py migrate construction")
        sys.exit(1)
    
    # بررسی و فعال‌سازی محیط مجازی
    python_path = check_and_activate_venv()
    
    # ساخت دستور Django
    django_args = ["manage.py"] + sys.argv[1:]
    
    print(f"🚀 اجرای دستور: {python_path} {' '.join(django_args)}")
    
    # اجرای دستور
    try:
        result = subprocess.run([python_path] + django_args, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در اجرای دستور: {e}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ فایل manage.py یافت نشد!")
        print("لطفاً از پوشه اصلی پروژه Django اجرا کنید.")
        sys.exit(1)

if __name__ == "__main__":
    main()
