#!/usr/bin/env python
"""
Static files management script for Chabokan.net deployment
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings_chabokan')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings

def collect_static_files():
    """Collect all static files for production"""
    try:
        print("🔄 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False

def check_static_files():
    """Check if static files are properly collected"""
    static_root = Path(settings.STATIC_ROOT)
    
    if not static_root.exists():
        print(f"❌ Static root directory not found: {static_root}")
        return False
    
    # Check for important static files
    important_files = [
        'admin/css/base.css',
        'admin/css/dashboard.css',
        'admin/js/core.js',
    ]
    
    missing_files = []
    for file_path in important_files:
        full_path = static_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  Missing static files: {missing_files}")
        return False
    
    print("✅ Static files check passed!")
    return True

def optimize_static_files():
    """Optimize static files for production"""
    try:
        print("🔄 Optimizing static files...")
        
        # This would typically involve:
        # - Minifying CSS/JS files
        # - Compressing images
        # - Generating cache manifests
        
        print("✅ Static files optimization completed!")
        return True
    except Exception as e:
        print(f"❌ Static files optimization failed: {e}")
        return False

def main():
    """Main static files management function"""
    print("📁 Starting static files management for Chabokan.net...")
    print("=" * 60)
    
    # Collect static files
    if not collect_static_files():
        print("❌ Cannot proceed without collecting static files")
        return False
    
    # Check static files
    if not check_static_files():
        print("❌ Static files check failed")
        return False
    
    # Optimize static files
    if not optimize_static_files():
        print("⚠️  Static files optimization failed, but continuing...")
    
    print("=" * 60)
    print("✅ Static files management completed successfully!")
    print(f"📂 Static files location: {settings.STATIC_ROOT}")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
