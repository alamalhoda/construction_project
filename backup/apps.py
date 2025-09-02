from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backup'
    verbose_name = 'مدیریت بک‌آپ'
    
    def ready(self):
        # Import signal handlers
        import backup.signals