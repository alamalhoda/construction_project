from django.apps import AppConfig


class ConstructionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'construction'
    verbose_name = 'سیستم مدیریت پروژه ساختمانی'
    
    def ready(self):
        import construction.signals
