"""
construction_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from health_check import health_check, simple_health_check
from construction import user_views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('construction/', include('construction.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('backup/', include('backup.urls')),
    
    # Authentication URLs - moved to root level
    path('login/', user_views.user_login_view, name='user_login'),
    path('register/', user_views.user_register_view, name='user_register'),
    path('logout/', user_views.user_logout_view, name='user_logout'),
    path('user-dashboard/', user_views.user_dashboard_view, name='user_dashboard'),
    path('profile/', user_views.user_profile_view, name='user_profile'),
    path('change-password/', user_views.change_password_view, name='change_password'),

    path('admin/', admin.site.urls),
    # API URLs
    path('', include('construction.urls')),
    
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/simple/', simple_health_check, name='simple_health_check'),
]

# اضافه کردن static files برای همه حالات (development و production)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
