#!/usr/bin/env python
"""
Health check endpoint for Chabokan.net deployment
This script provides a simple health check for monitoring
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

from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import json

def health_check(request):
    """
    Health check endpoint that returns the status of various components
    """
    health_status = {
        'status': 'healthy',
        'timestamp': django.utils.timezone.now().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check static files
    try:
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            health_status['checks']['static_files'] = {
                'status': 'healthy',
                'message': 'Static files directory exists'
            }
        else:
            health_status['checks']['static_files'] = {
                'status': 'unhealthy',
                'message': 'Static files directory not found'
            }
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['static_files'] = {
            'status': 'unhealthy',
            'message': f'Static files check failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check environment variables
    required_env_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_HOST']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        health_status['checks']['environment'] = {
            'status': 'unhealthy',
            'message': f'Missing environment variables: {missing_vars}'
        }
        health_status['status'] = 'unhealthy'
    else:
        health_status['checks']['environment'] = {
            'status': 'healthy',
            'message': 'All required environment variables are set'
        }
    
    # Check Django settings
    try:
        debug_mode = settings.DEBUG
        if debug_mode:
            health_status['checks']['django_settings'] = {
                'status': 'warning',
                'message': 'DEBUG mode is enabled (not recommended for production)'
            }
        else:
            health_status['checks']['django_settings'] = {
                'status': 'healthy',
                'message': 'Django settings are properly configured'
            }
    except Exception as e:
        health_status['checks']['django_settings'] = {
            'status': 'unhealthy',
            'message': f'Django settings check failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Return appropriate HTTP status code
    if health_status['status'] == 'healthy':
        return JsonResponse(health_status, status=200)
    elif health_status['status'] == 'warning':
        return JsonResponse(health_status, status=200)
    else:
        return JsonResponse(health_status, status=503)

def simple_health_check(request):
    """
    Simple health check that just returns OK
    """
    return JsonResponse({'status': 'OK'}, status=200)

if __name__ == '__main__':
    # This can be run as a standalone script for testing
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/health/')
    
    response = health_check(request)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.content.decode()}")
