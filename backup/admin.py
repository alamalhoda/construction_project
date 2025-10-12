from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import BackupRecord, BackupSettings


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'backup_type', 'status_badge', 'created_at', 
        'total_records', 'file_size_display', 'duration_display'
    ]
    list_filter = ['backup_type', 'status', 'created_at']
    search_fields = ['name', 'success_message', 'error_message']
    readonly_fields = [
        'created_at', 'completed_at', 'duration_display', 
        'file_size_display', 'is_successful'
    ]
    fieldsets = (
        ('اطلاعات کلی', {
            'fields': ('name', 'backup_type', 'status', 'created_at', 'completed_at')
        }),
        ('آمار داده‌ها', {
            'fields': (
                'projects_count', 'investors_count', 'periods_count', 
                'transactions_count', 'units_count', 'interest_rates_count',
                'expenses_count', 'sales_count', 'user_profiles_count', 'total_records'
            )
        }),
        ('اطلاعات فایل', {
            'fields': ('file_path', 'file_size_display', 'duration_display')
        }),
        ('پیام‌ها', {
            'fields': ('success_message', 'error_message'),
            'classes': ('collapse',)
        }),
        ('تنظیمات', {
            'fields': ('include_media', 'compression_enabled'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'
    
    def file_size_display(self, obj):
        if obj.file_size_kb:
            if obj.file_size_kb > 1024:
                return f"{obj.file_size_kb / 1024:.1f} MB"
            else:
                return f"{obj.file_size_kb:.1f} KB"
        return "-"
    file_size_display.short_description = 'حجم فایل'
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "-"
    duration_display.short_description = 'مدت زمان'
    
    def is_successful(self, obj):
        if obj.is_successful:
            return format_html('<span style="color: green;">✅ موفق</span>')
        else:
            return format_html('<span style="color: red;">❌ ناموفق</span>')
    is_successful.short_description = 'نتیجه'


@admin.register(BackupSettings)
class BackupSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('تنظیمات بک‌آپ خودکار', {
            'fields': (
                'auto_backup_enabled', 'auto_backup_interval', 'auto_backup_time'
            )
        }),
        ('تنظیمات نگهداری', {
            'fields': (
                'max_backups', 'auto_cleanup_enabled', 'cleanup_after_days'
            )
        }),
        ('تنظیمات فایل', {
            'fields': (
                'compression_enabled', 'include_media_files'
            )
        }),
        ('تنظیمات اعلان', {
            'fields': (
                'email_notifications', 'notification_email'
            )
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # فقط یک رکورد تنظیمات مجاز است
        return not BackupSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # حذف تنظیمات مجاز نیست
        return False