from django.db import models
from django.utils import timezone
from django_jalali.db import models as jmodels


class BackupRecord(models.Model):
    """
    مدل ثبت اطلاعات بک‌آپ‌ها
    برای نگهداری تاریخچه و آمار بک‌آپ‌ها
    """
    name = models.CharField(max_length=100, verbose_name="نام بک‌آپ")
    backup_type = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'دستی'),
            ('automatic', 'خودکار'),
            ('scheduled', 'زمان‌بندی شده'),
        ],
        default='manual',
        verbose_name="نوع بک‌آپ"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'در انتظار'),
            ('running', 'در حال اجرا'),
            ('completed', 'تکمیل شده'),
            ('failed', 'ناموفق'),
        ],
        default='pending',
        verbose_name="وضعیت"
    )
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    completed_at = jmodels.jDateTimeField(null=True, blank=True, verbose_name="تاریخ تکمیل")
    
    # آمار داده‌ها
    projects_count = models.IntegerField(default=0, verbose_name="تعداد پروژه‌ها")
    investors_count = models.IntegerField(default=0, verbose_name="تعداد سرمایه‌گذاران")
    periods_count = models.IntegerField(default=0, verbose_name="تعداد دوره‌ها")
    transactions_count = models.IntegerField(default=0, verbose_name="تعداد تراکنش‌ها")
    units_count = models.IntegerField(default=0, verbose_name="تعداد واحدها")
    total_records = models.IntegerField(default=0, verbose_name="کل رکوردها")
    
    # اطلاعات فایل
    file_size_kb = models.FloatField(default=0, verbose_name="حجم فایل (KB)")
    file_path = models.CharField(max_length=500, verbose_name="مسیر فایل")
    
    # پیام‌ها و خطاها
    success_message = models.TextField(blank=True, verbose_name="پیام موفقیت")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    
    # تنظیمات
    include_media = models.BooleanField(default=False, verbose_name="شامل فایل‌های رسانه")
    compression_enabled = models.BooleanField(default=True, verbose_name="فشرده‌سازی فعال")
    
    class Meta:
        verbose_name = "رکورد بک‌آپ"
        verbose_name_plural = "رکوردهای بک‌آپ"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def duration(self):
        """محاسبه مدت زمان بک‌آپ"""
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def is_successful(self):
        """بررسی موفقیت بک‌آپ"""
        return self.status == 'completed' and not self.error_message
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('backup:detail', kwargs={'pk': self.pk})


class BackupSettings(models.Model):
    """
    مدل تنظیمات بک‌آپ
    برای نگهداری تنظیمات کلی سیستم بک‌آپ
    """
    # تنظیمات خودکار
    auto_backup_enabled = models.BooleanField(default=False, verbose_name="بک‌آپ خودکار فعال")
    auto_backup_interval = models.IntegerField(
        default=24,
        verbose_name="فاصله بک‌آپ خودکار (ساعت)"
    )
    auto_backup_time = models.TimeField(
        default='02:00',
        verbose_name="زمان بک‌آپ خودکار"
    )
    
    # تنظیمات نگهداری
    max_backups = models.IntegerField(
        default=10,
        verbose_name="حداکثر تعداد بک‌آپ‌ها"
    )
    auto_cleanup_enabled = models.BooleanField(
        default=True,
        verbose_name="پاک‌سازی خودکار فعال"
    )
    cleanup_after_days = models.IntegerField(
        default=30,
        verbose_name="پاک‌سازی بعد از (روز)"
    )
    
    # تنظیمات فایل
    compression_enabled = models.BooleanField(
        default=True,
        verbose_name="فشرده‌سازی فعال"
    )
    include_media_files = models.BooleanField(
        default=False,
        verbose_name="شامل فایل‌های رسانه"
    )
    
    # تنظیمات اعلان
    email_notifications = models.BooleanField(
        default=False,
        verbose_name="اعلان‌های ایمیل"
    )
    notification_email = models.EmailField(
        blank=True,
        verbose_name="ایمیل اعلان‌ها"
    )
    
    # متادیتا
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    
    class Meta:
        verbose_name = "تنظیمات بک‌آپ"
        verbose_name_plural = "تنظیمات بک‌آپ"
    
    def __str__(self):
        return "تنظیمات بک‌آپ"
    
    def save(self, *args, **kwargs):
        # اطمینان از وجود تنها یک رکورد تنظیمات
        if not self.pk and BackupSettings.objects.exists():
            # اگر رکوردی وجود دارد، آن را به‌روزرسانی کن
            existing = BackupSettings.objects.first()
            existing.auto_backup_enabled = self.auto_backup_enabled
            existing.auto_backup_interval = self.auto_backup_interval
            existing.auto_backup_time = self.auto_backup_time
            existing.max_backups = self.max_backups
            existing.auto_cleanup_enabled = self.auto_cleanup_enabled
            existing.cleanup_after_days = self.cleanup_after_days
            existing.compression_enabled = self.compression_enabled
            existing.include_media_files = self.include_media_files
            existing.email_notifications = self.email_notifications
            existing.notification_email = self.notification_email
            existing.save()
            return existing
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """دریافت تنظیمات فعلی"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings