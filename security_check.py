#!/usr/bin/env python
"""
Security configuration and checks for Chabokan.net deployment
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# Setup Django
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line

def check_security_settings():
    """Check if security settings are properly configured"""
    print("🔒 Checking security settings...")
    
    security_checks = []
    
    # Check DEBUG mode
    if settings.DEBUG:
        security_checks.append("⚠️  DEBUG is enabled (development mode)")
    else:
        security_checks.append("✅ DEBUG is disabled (production mode)")
    
    # Check SECRET_KEY
    if settings.SECRET_KEY == '^l)7d*%h&db4uft@dk%h-w&nup#pu%)a!d)c7jwgoixo5_hm0$':
        security_checks.append("❌ SECRET_KEY is using default value")
    else:
        security_checks.append("✅ SECRET_KEY is customized")
    
    # Check ALLOWED_HOSTS
    if '*' in settings.ALLOWED_HOSTS:
        security_checks.append("❌ ALLOWED_HOSTS contains wildcard (*)")
    else:
        security_checks.append("✅ ALLOWED_HOSTS is properly configured")
    
    # Check HTTPS settings
    if hasattr(settings, 'SECURE_SSL_REDIRECT') and settings.SECURE_SSL_REDIRECT:
        security_checks.append("✅ SSL redirect is enabled")
    else:
        security_checks.append("⚠️  SSL redirect is not configured")
    
    # Check HSTS settings
    if hasattr(settings, 'SECURE_HSTS_SECONDS') and settings.SECURE_HSTS_SECONDS > 0:
        security_checks.append("✅ HSTS is configured")
    else:
        security_checks.append("⚠️  HSTS is not configured")
    
    # Check CSRF settings
    if settings.CSRF_COOKIE_SECURE:
        security_checks.append("✅ CSRF cookie is secure")
    else:
        if settings.DEBUG:
            security_checks.append("⚠️  CSRF cookie is not secure (development mode)")
        else:
            security_checks.append("❌ CSRF cookie is not secure")
    
    # Check session settings
    if settings.SESSION_COOKIE_SECURE:
        security_checks.append("✅ Session cookie is secure")
    else:
        if settings.DEBUG:
            security_checks.append("⚠️  Session cookie is not secure (development mode)")
        else:
            security_checks.append("❌ Session cookie is not secure")
    
    # Print results
    for check in security_checks:
        print(f"  {check}")
    
    # Count issues
    issues = [check for check in security_checks if check.startswith("❌")]
    warnings = [check for check in security_checks if check.startswith("⚠️")]
    
    print(f"\n📊 Security Summary:")
    print(f"  Issues: {len(issues)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Passed: {len(security_checks) - len(issues) - len(warnings)}")
    
    return len(issues) == 0

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        'SECRET_KEY',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'ALLOWED_HOST',
    ]
    
    optional_vars = [
        'EMAIL_HOST',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'TRUSTED_ORIGIN',
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_required.append(var)
        else:
            print(f"  ✅ {var} is set")
    
    for var in optional_vars:
        if not os.environ.get(var):
            missing_optional.append(var)
        else:
            print(f"  ✅ {var} is set")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables:")
        for var in missing_required:
            print(f"  - {var}")
    
    if missing_optional:
        print(f"\n⚠️  Missing optional environment variables:")
        for var in missing_optional:
            print(f"  - {var}")
    
    return len(missing_required) == 0

def generate_security_report():
    """Generate a comprehensive security report"""
    print("🛡️  Generating security report...")
    
    report = []
    report.append("# Security Report for Chabokan.net Deployment")
    report.append("=" * 50)
    report.append("")
    
    # Django version
    import django
    report.append(f"## Django Version: {django.get_version()}")
    report.append("")
    
    # Security settings
    report.append("## Security Settings")
    report.append(f"- DEBUG: {settings.DEBUG}")
    report.append(f"- ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    report.append(f"- SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', 'Not set')}")
    report.append(f"- SECURE_HSTS_SECONDS: {getattr(settings, 'SECURE_HSTS_SECONDS', 'Not set')}")
    report.append(f"- CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
    report.append(f"- SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    report.append("")
    
    # Environment variables
    report.append("## Environment Variables")
    for var in ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_HOST', 'ALLOWED_HOST']:
        value = os.environ.get(var, 'Not set')
        if var == 'SECRET_KEY' and value != 'Not set':
            value = f"{value[:10]}..." if len(value) > 10 else value
        report.append(f"- {var}: {value}")
    report.append("")
    
    # Recommendations
    report.append("## Security Recommendations")
    report.append("1. Change the default SECRET_KEY")
    report.append("2. Configure proper ALLOWED_HOSTS")
    report.append("3. Enable SSL/HTTPS")
    report.append("4. Set up proper logging")
    report.append("5. Regular security updates")
    report.append("6. Monitor access logs")
    report.append("")
    
    # Save report
    report_file = Path("security_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Security report saved to: {report_file}")
    return True

def main():
    """Main security check function"""
    print("🛡️  Starting security checks for Chabokan.net...")
    print("=" * 60)
    
    # Check security settings
    security_ok = check_security_settings()
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Generate security report
    generate_security_report()
    
    print("=" * 60)
    if security_ok and env_ok:
        print("✅ Security checks passed!")
        print("🎉 Your application is ready for secure deployment!")
    else:
        print("❌ Security checks failed!")
        print("⚠️  Please fix the issues before deployment")
    
    return security_ok and env_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
