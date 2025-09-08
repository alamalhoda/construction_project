#!/usr/bin/env python
"""
Test script for Chabokan.net setup
This script tests all the configuration files and settings
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings_chabokan')
        django.setup()
        print("✅ Django settings imported successfully")
        
        # Test health check
        from health_check import health_check, simple_health_check
        print("✅ Health check module imported successfully")
        
        # Test security module
        from security_chabokan import check_security_settings
        print("✅ Security module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_django_settings():
    """Test Django settings configuration"""
    print("\n🔍 Testing Django settings...")
    
    try:
        from django.conf import settings
        
        # Test basic settings
        assert hasattr(settings, 'SECRET_KEY'), "SECRET_KEY not found"
        assert hasattr(settings, 'DATABASES'), "DATABASES not found"
        assert hasattr(settings, 'STATIC_ROOT'), "STATIC_ROOT not found"
        
        print("✅ Basic Django settings are configured")
        
        # Test database configuration
        db_config = settings.DATABASES['default']
        assert db_config['ENGINE'] == 'django.db.backends.postgresql', "Database engine should be PostgreSQL"
        print("✅ Database configuration is correct")
        
        # Test static files configuration
        assert settings.STATIC_ROOT, "STATIC_ROOT should be set"
        assert settings.STATIC_URL, "STATIC_URL should be set"
        print("✅ Static files configuration is correct")
        
        return True
    except Exception as e:
        print(f"❌ Django settings test failed: {e}")
        return False

def test_requirements():
    """Test if requirements file exists and is valid"""
    print("\n🔍 Testing requirements file...")
    
    try:
        requirements_file = Path("requirements-chabokan.txt")
        assert requirements_file.exists(), "requirements-chabokan.txt not found"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
            
        # Check for essential packages
        essential_packages = [
            'Django==4.2.23',
            'gunicorn',
            'whitenoise',
            'psycopg2-binary',
            'python-dotenv'
        ]
        
        for package in essential_packages:
            assert package in content, f"Package {package} not found in requirements"
        
        print("✅ Requirements file is valid")
        return True
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def test_environment_file():
    """Test if environment file template exists"""
    print("\n🔍 Testing environment file template...")
    
    try:
        env_file = Path(".env.chabokan")
        assert env_file.exists(), ".env.chabokan not found"
        
        with open(env_file, 'r') as f:
            content = f.read()
            
        # Check for essential environment variables
        essential_vars = [
            'SECRET_KEY',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_HOST',
            'ALLOWED_HOST'
        ]
        
        for var in essential_vars:
            assert var in content, f"Environment variable {var} not found in template"
        
        print("✅ Environment file template is valid")
        return True
    except Exception as e:
        print(f"❌ Environment file test failed: {e}")
        return False

def test_scripts():
    """Test if all scripts exist and are executable"""
    print("\n🔍 Testing scripts...")
    
    scripts = [
        "deploy_chabokan.sh",
        "start_chabokan.sh",
        "scripts/setup_chabokan_db.py",
        "staticfiles_management.py",
        "security_chabokan.py",
        "health_check.py"
    ]
    
    for script in scripts:
        script_path = Path(script)
        assert script_path.exists(), f"Script {script} not found"
        
        if script.endswith('.sh'):
            assert os.access(script_path, os.X_OK), f"Script {script} is not executable"
        
        print(f"✅ {script} is valid")
    
    return True

def test_wsgi_configuration():
    """Test WSGI configuration"""
    print("\n🔍 Testing WSGI configuration...")
    
    try:
        # Test if wsgi_chabokan.py exists
        wsgi_file = Path("wsgi_chabokan.py")
        assert wsgi_file.exists(), "wsgi_chabokan.py not found"
        
        # Test if it can be imported
        import wsgi_chabokan
        assert hasattr(wsgi_chabokan, 'application'), "WSGI application not found"
        
        print("✅ WSGI configuration is valid")
        return True
    except Exception as e:
        print(f"❌ WSGI configuration test failed: {e}")
        return False

def test_gunicorn_configuration():
    """Test Gunicorn configuration"""
    print("\n🔍 Testing Gunicorn configuration...")
    
    try:
        gunicorn_file = Path("gunicorn.conf.py")
        assert gunicorn_file.exists(), "gunicorn.conf.py not found"
        
        # Test if it can be imported
        import gunicorn.conf
        print("✅ Gunicorn configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Gunicorn configuration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Chabokan.net setup...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_django_settings,
        test_requirements,
        test_environment_file,
        test_scripts,
        test_wsgi_configuration,
        test_gunicorn_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Chabokan.net setup is ready!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
