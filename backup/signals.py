from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BackupRecord, BackupSettings
from .utils import cleanup_old_backups


@receiver(post_save, sender=BackupRecord)
def auto_cleanup_after_backup(sender, instance, created, **kwargs):
    """
    پاک‌سازی خودکار بک‌آپ‌های قدیمی بعد از ایجاد بک‌آپ جدید
    """
    if created and instance.status == 'completed':
        settings_obj = BackupSettings.get_settings()
        
        if settings_obj.auto_cleanup_enabled:
            try:
                cleanup_old_backups(
                    max_backups=settings_obj.max_backups,
                    cleanup_after_days=settings_obj.cleanup_after_days
                )
            except Exception as e:
                print(f"خطا در پاک‌سازی خودکار: {e}")


@receiver(post_save, sender=BackupSettings)
def send_notification_on_settings_change(sender, instance, created, **kwargs):
    """
    ارسال اعلان در صورت تغییر تنظیمات مهم
    """
    if not created:  # فقط در صورت به‌روزرسانی
        # می‌توانید اینجا کد ارسال ایمیل یا اعلان را اضافه کنید
        pass
