from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    # صفحات اصلی
    path('', views.backup_dashboard, name='dashboard'),
    path('list/', views.backup_list, name='list'),
    path('settings/', views.backup_settings_view, name='settings'),
    path('detail/<int:pk>/', views.backup_detail, name='detail'),
    
    # API endpoints
    path('api/create/', views.create_backup_api, name='create_api'),
    path('api/delete/', views.delete_backup_api, name='delete_api'),
    path('api/stats/', views.get_backup_stats_api, name='stats_api'),
    path('api/cleanup/', views.cleanup_backups_api, name='cleanup_api'),
    path('api/cron/', views.manage_cron_api, name='cron_api'),
    
    # دانلود
    path('download/<int:pk>/', views.download_backup, name='download'),
]
