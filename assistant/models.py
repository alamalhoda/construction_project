"""
مدل‌های مربوط به AI Assistant
"""

from django.db import models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from construction.models import Project


class ChatLog(models.Model):
    """
    مدل ذخیره‌سازی چت‌های کاربران با دستیار هوشمند
    
    این مدل تمام اطلاعات مربوط به هر مکالمه را ذخیره می‌کند:
    - سوال و پاسخ کاربر
    - مدل LLM استفاده شده
    - ابزارهای استفاده شده
    - اطلاعات توکن‌ها
    - مدت زمان اجرا
    """
    
    # روابط
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_logs',
        verbose_name="کاربر",
        help_text="کاربری که این چت را انجام داده است"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_logs',
        verbose_name="پروژه",
        help_text="پروژه مرتبط با این چت (در صورت وجود)"
    )
    
    # اطلاعات LLM
    llm_provider = models.CharField(
        max_length=50,
        verbose_name="ارائه‌دهنده LLM",
        help_text="نوع ارائه‌دهنده LLM (مثل OpenAI, Anthropic, ...)"
    )
    llm_model = models.CharField(
        max_length=200,
        verbose_name="مدل LLM",
        help_text="نام مدل LLM استفاده شده (مثل GPT-4, Claude-3, ...)"
    )
    
    # محتوای چت
    user_message = models.TextField(
        verbose_name="پیام کاربر",
        help_text="سوال یا پیام ارسالی توسط کاربر"
    )
    assistant_response = models.TextField(
        verbose_name="پاسخ دستیار",
        help_text="پاسخ تولید شده توسط دستیار هوشمند"
    )
    
    # ابزارهای استفاده شده
    tools_used = models.JSONField(
        default=list,
        blank=True,
        verbose_name="ابزارهای استفاده شده",
        help_text="لیست ابزارهایی که در این چت استفاده شده‌اند (به صورت JSON)"
    )
    tools_count = models.IntegerField(
        default=0,
        verbose_name="تعداد ابزارها",
        help_text="تعداد کل ابزارهای استفاده شده"
    )
    
    # اطلاعات توکن‌ها
    input_tokens = models.IntegerField(
        default=0,
        verbose_name="توکن‌های ورودی",
        help_text="تعداد توکن‌های ورودی مصرف شده"
    )
    output_tokens = models.IntegerField(
        default=0,
        verbose_name="توکن‌های خروجی",
        help_text="تعداد توکن‌های خروجی تولید شده"
    )
    total_tokens = models.IntegerField(
        default=0,
        verbose_name="مجموع توکن‌ها",
        help_text="مجموع توکن‌های مصرف شده"
    )
    cached_tokens = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="توکن‌های کش شده",
        help_text="تعداد توکن‌های کش شده (در صورت پشتیبانی)"
    )
    reasoning_tokens = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="توکن‌های استدلال",
        help_text="تعداد توکن‌های استدلال (در صورت پشتیبانی)"
    )
    
    # اطلاعات زمان
    duration_seconds = models.FloatField(
        verbose_name="مدت زمان اجرا (ثانیه)",
        help_text="مدت زمان لازم برای تولید پاسخ (به ثانیه)"
    )
    
    # اطلاعات اضافی
    success = models.BooleanField(
        default=True,
        verbose_name="موفقیت",
        help_text="آیا چت با موفقیت انجام شده است؟"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="پیام خطا",
        help_text="پیام خطا در صورت بروز مشکل"
    )
    
    # متادیتا
    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
        help_text="زمان ایجاد این رکورد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی",
        help_text="زمان آخرین به‌روزرسانی"
    )
    
    class Meta:
        verbose_name = "لاگ چت"
        verbose_name_plural = "لاگ‌های چت"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['llm_provider', '-created_at']),
        ]
    
    def __str__(self):
        return f"چت {self.user.username} - {self.created_at.strftime('%Y/%m/%d %H:%M')}"
    
    @property
    def duration_formatted(self):
        """فرمت کردن مدت زمان به صورت خوانا"""
        if self.duration_seconds < 1:
            return f"{int(self.duration_seconds * 1000)}ms"
        elif self.duration_seconds < 60:
            return f"{self.duration_seconds:.2f}s"
        else:
            minutes = int(self.duration_seconds // 60)
            seconds = self.duration_seconds % 60
            return f"{minutes}m {seconds:.2f}s"
    
    @property
    def tools_list(self):
        """لیست ابزارهای استفاده شده به صورت خوانا"""
        if not self.tools_used:
            return []
        return [tool.get('name', tool) if isinstance(tool, dict) else tool for tool in self.tools_used]

