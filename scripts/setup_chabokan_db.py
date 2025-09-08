#!/usr/bin/env python
"""
Database setup script for Chabokan.net deployment
This script helps set up the PostgreSQL database for production
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings_chabokan')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.conf import settings

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    try:
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_superuser():
    """Create superuser if it doesn't exist"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        try:
            print("🔄 Creating superuser...")
            User.objects.create_superuser(
                username='admin',
                email='admin@chabokan.net',
                password='admin123'  # Change this in production!
            )
            print("✅ Superuser created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change the password after first login!")
        except Exception as e:
            print(f"❌ Superuser creation failed: {e}")
            return False
    else:
        print("ℹ️  Superuser already exists")
    
    return True

def collect_static():
    """Collect static files"""
    try:
        print("🔄 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Chabokan.net database setup...")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        return False
    
    # Run migrations
    if not run_migrations():
        print("❌ Cannot proceed without successful migrations")
        return False
    
    # Create superuser
    if not create_superuser():
        print("❌ Cannot proceed without superuser")
        return False
    
    # Collect static files
    if not collect_static():
        print("⚠️  Static files collection failed, but continuing...")
    
    print("=" * 50)
    print("✅ Database setup completed successfully!")
    print("🎉 Your Django application is ready for Chabokan.net!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
