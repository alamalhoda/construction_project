"""
WSGI config for construction_project - Chabokan.net deployment.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set Django settings module for Chabokan deployment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings_chabokan')

application = get_wsgi_application()
