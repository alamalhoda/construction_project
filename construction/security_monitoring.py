"""
سیستم نظارت امنیتی
Security Monitoring System for Construction Project
"""

import logging
import json
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

logger = logging.getLogger('django.security')

class SecurityEvent(models.Model):
    """
    مدل برای ثبت رویدادهای امنیتی
    """
    
    EVENT_TYPES = [
        ('login_success', 'ورود موفق'),
        ('login_failed', 'ورود ناموفق'),
        ('logout', 'خروج'),
        ('admin_access', 'دسترسی به ادمین'),
        ('suspicious_activity', 'فعالیت مشکوک'),
        ('rate_limit_exceeded', 'تجاوز از حد مجاز'),
        ('file_upload', 'آپلود فایل'),
        ('data_export', 'خروجی داده'),
        ('password_change', 'تغییر رمز عبور'),
        ('account_locked', 'قفل شدن حساب'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('critical', 'بحرانی'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="نوع رویداد")
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name="سطح اهمیت")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کاربر")
    ip_address = models.GenericIPAddressField(verbose_name="آدرس IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    description = models.TextField(verbose_name="توضیحات")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="اطلاعات اضافی")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان")
    resolved = models.BooleanField(default=False, verbose_name="حل شده")
    
    class Meta:
        verbose_name = "رویداد امنیتی"
        verbose_name_plural = "رویدادهای امنیتی"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.ip_address} - {self.timestamp}"

class SecurityMonitor:
    """
    کلاس نظارت امنیتی
    """
    
    @staticmethod
    def log_event(event_type, severity, user=None, request=None, description="", metadata=None):
        """
        ثبت رویداد امنیتی
        """
        try:
            # استخراج اطلاعات از request
            ip_address = "unknown"
            user_agent = ""
            
            if request:
                ip_address = SecurityMonitor.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # ایجاد رویداد
            event = SecurityEvent.objects.create(
                event_type=event_type,
                severity=severity,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                description=description,
                metadata=metadata or {}
            )
            
            # ثبت در لاگ
            logger.info(f"Security event logged: {event_type} - {severity} - {ip_address}")
            
            # بررسی رویدادهای بحرانی
            if severity == 'critical':
                SecurityMonitor.send_alert(event)
            
            return event
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            return None
    
    @staticmethod
    def get_client_ip(request):
        """دریافت IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def send_alert(event):
        """
        ارسال هشدار برای رویدادهای بحرانی
        """
        try:
            subject = f"🚨 هشدار امنیتی - {event.get_event_type_display()}"
            
            message = f"""
رویداد امنیتی بحرانی شناسایی شد:

نوع رویداد: {event.get_event_type_display()}
سطح اهمیت: {event.get_severity_display()}
کاربر: {event.user.username if event.user else 'نامشخص'}
IP: {event.ip_address}
زمان: {event.timestamp}
توضیحات: {event.description}

لطفاً فوراً بررسی کنید.
            """
            
            # ارسال ایمیل (در production)
            if hasattr(settings, 'SECURITY_ALERT_EMAIL'):
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.SECURITY_ALERT_EMAIL],
                    fail_silently=False,
                )
            
            logger.critical(f"Security alert sent for event: {event.id}")
            
        except Exception as e:
            logger.error(f"Error sending security alert: {e}")
    
    @staticmethod
    def analyze_suspicious_activity():
        """
        تحلیل فعالیت‌های مشکوک
        """
        # بررسی تلاش‌های ورود ناموفق
        recent_failed_logins = SecurityEvent.objects.filter(
            event_type='login_failed',
            timestamp__gte=timezone.now() - timedelta(hours=1)
        )
        
        # گروه‌بندی بر اساس IP
        ip_attempts = {}
        for event in recent_failed_logins:
            ip = event.ip_address
            if ip not in ip_attempts:
                ip_attempts[ip] = 0
            ip_attempts[ip] += 1
        
        # شناسایی IP های مشکوک
        suspicious_ips = [ip for ip, count in ip_attempts.items() if count >= 10]
        
        for ip in suspicious_ips:
            SecurityMonitor.log_event(
                event_type='suspicious_activity',
                severity='high',
                description=f"IP {ip} با {ip_attempts[ip]} تلاش ورود ناموفق در 1 ساعت گذشته",
                metadata={'ip': ip, 'attempts': ip_attempts[ip]}
            )
    
    @staticmethod
    def get_security_dashboard_data():
        """
        دریافت داده‌های داشبورد امنیتی
        """
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # آمار رویدادها
        events_24h = SecurityEvent.objects.filter(timestamp__gte=last_24h)
        events_7d = SecurityEvent.objects.filter(timestamp__gte=last_7d)
        
        # رویدادهای بحرانی
        critical_events = events_24h.filter(severity='critical')
        
        # تلاش‌های ورود ناموفق
        failed_logins = events_24h.filter(event_type='login_failed')
        
        # IP های مشکوک
        suspicious_ips = events_24h.filter(
            event_type='suspicious_activity'
        ).values_list('metadata__ip', flat=True)
        
        return {
            'total_events_24h': events_24h.count(),
            'total_events_7d': events_7d.count(),
            'critical_events': critical_events.count(),
            'failed_logins': failed_logins.count(),
            'suspicious_ips': len(set(suspicious_ips)),
            'recent_events': events_24h[:10],
        }

class SecurityReport:
    """
    کلاس تولید گزارش‌های امنیتی
    """
    
    @staticmethod
    def generate_daily_report():
        """
        تولید گزارش روزانه امنیتی
        """
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.now()
        
        events = SecurityEvent.objects.filter(
            timestamp__gte=yesterday,
            timestamp__lt=today
        )
        
        # آمار کلی
        total_events = events.count()
        critical_events = events.filter(severity='critical').count()
        failed_logins = events.filter(event_type='login_failed').count()
        
        # رویدادهای برتر
        top_events = events.values('event_type').annotate(
            count=models.Count('event_type')
        ).order_by('-count')[:5]
        
        # IP های فعال
        top_ips = events.values('ip_address').annotate(
            count=models.Count('ip_address')
        ).order_by('-count')[:5]
        
        report = {
            'date': yesterday.date(),
            'total_events': total_events,
            'critical_events': critical_events,
            'failed_logins': failed_logins,
            'top_events': list(top_events),
            'top_ips': list(top_ips),
        }
        
        return report
    
    @staticmethod
    def generate_weekly_report():
        """
        تولید گزارش هفتگی امنیتی
        """
        week_ago = timezone.now() - timedelta(days=7)
        
        events = SecurityEvent.objects.filter(timestamp__gte=week_ago)
        
        # آمار کلی
        total_events = events.count()
        events_by_type = events.values('event_type').annotate(
            count=models.Count('event_type')
        )
        events_by_severity = events.values('severity').annotate(
            count=models.Count('severity')
        )
        
        # روند روزانه
        daily_trend = []
        for i in range(7):
            day_start = week_ago + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            day_events = events.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end
            ).count()
            daily_trend.append({
                'date': day_start.date(),
                'count': day_events
            })
        
        report = {
            'period': f"{week_ago.date()} - {timezone.now().date()}",
            'total_events': total_events,
            'events_by_type': list(events_by_type),
            'events_by_severity': list(events_by_severity),
            'daily_trend': daily_trend,
        }
        
        return report

# مدیریت دستی رویدادهای امنیتی
class SecurityEventManager:
    """
    مدیریت دستی رویدادهای امنیتی
    """
    
    @staticmethod
    def mark_resolved(event_id):
        """علامت‌گذاری رویداد به عنوان حل شده"""
        try:
            event = SecurityEvent.objects.get(id=event_id)
            event.resolved = True
            event.save()
            return True
        except SecurityEvent.DoesNotExist:
            return False
    
    @staticmethod
    def get_unresolved_events():
        """دریافت رویدادهای حل نشده"""
        return SecurityEvent.objects.filter(resolved=False).order_by('-timestamp')
    
    @staticmethod
    def cleanup_old_events(days=30):
        """پاک کردن رویدادهای قدیمی"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = SecurityEvent.objects.filter(
            timestamp__lt=cutoff_date,
            severity__in=['low', 'medium']
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old security events")
        return deleted_count
