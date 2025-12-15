"""
Admin configuration برای Assistant models
"""

from django.contrib import admin
from django.utils.html import format_html
from assistant.models import ChatLog


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    """
    Admin interface برای ChatLog
    """
    
    list_display = [
        'id',
        'user',
        'project',
        'llm_model',
        'created_at',
        'duration_formatted_display',
        'total_tokens',
        'tools_count',
        'success_status',
    ]
    
    list_filter = [
        'llm_provider',
        'success',
        'created_at',
        'project',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user_message',
        'assistant_response',
        'llm_model',
        'llm_provider',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'duration_formatted',
        'tools_list_display',
        'token_usage_display',
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'project', 'created_at', 'updated_at')
        }),
        ('محتوای چت', {
            'fields': ('user_message', 'assistant_response')
        }),
        ('اطلاعات LLM', {
            'fields': ('llm_provider', 'llm_model')
        }),
        ('ابزارها', {
            'fields': ('tools_used', 'tools_count', 'tools_list_display')
        }),
        ('اطلاعات توکن‌ها', {
            'fields': (
                'input_tokens',
                'output_tokens',
                'total_tokens',
                'cached_tokens',
                'reasoning_tokens',
                'token_usage_display',
            )
        }),
        ('اطلاعات زمان', {
            'fields': ('duration_seconds', 'duration_formatted')
        }),
        ('وضعیت', {
            'fields': ('success', 'error_message')
        }),
    )
    
    def duration_formatted_display(self, obj):
        """نمایش مدت زمان به صورت فرمت شده"""
        return obj.duration_formatted
    duration_formatted_display.short_description = 'مدت زمان'
    duration_formatted_display.admin_order_field = 'duration_seconds'
    
    def success_status(self, obj):
        """نمایش وضعیت موفقیت با رنگ"""
        if obj.success:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ موفق</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ ناموفق</span>'
            )
    success_status.short_description = 'وضعیت'
    success_status.admin_order_field = 'success'
    
    def tools_list_display(self, obj):
        """نمایش لیست ابزارها به صورت خوانا"""
        tools = obj.tools_list
        if not tools:
            return "هیچ ابزاری استفاده نشده"
        return format_html('<br>'.join([f"• {tool}" for tool in tools]))
    tools_list_display.short_description = 'لیست ابزارها'
    
    def token_usage_display(self, obj):
        """نمایش اطلاعات توکن‌ها به صورت خوانا"""
        parts = [
            f"ورودی: {obj.input_tokens:,}",
            f"خروجی: {obj.output_tokens:,}",
            f"مجموع: {obj.total_tokens:,}",
        ]
        if obj.cached_tokens:
            parts.append(f"کش: {obj.cached_tokens:,}")
        if obj.reasoning_tokens:
            parts.append(f"استدلال: {obj.reasoning_tokens:,}")
        return format_html('<br>'.join(parts))
    token_usage_display.short_description = 'جزئیات توکن‌ها'
    
    def get_queryset(self, request):
        """بهینه‌سازی query با select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'project')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

