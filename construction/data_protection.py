"""
سیستم محافظت از داده‌ها
Data Protection System for Construction Project
"""

import hashlib
import secrets
import logging
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import os
import mimetypes

logger = logging.getLogger('django.security')

class SecureFileStorage(FileSystemStorage):
    """
    سیستم ذخیره‌سازی امن فایل‌ها
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = os.path.join(settings.MEDIA_ROOT, 'secure_files')
        super().__init__(location, base_url)
    
    def _save(self, name, content):
        """
        ذخیره امن فایل با نام رمزگذاری شده
        """
        # تولید نام امن
        secure_name = self.generate_secure_filename(name)
        
        # بررسی نوع فایل
        if not self.is_allowed_file_type(content):
            raise ValueError("نوع فایل مجاز نیست")
        
        # بررسی اندازه فایل
        if content.size > self.get_max_file_size():
            raise ValueError("اندازه فایل بیش از حد مجاز است")
        
        # ذخیره فایل
        return super()._save(secure_name, content)
    
    def generate_secure_filename(self, original_name):
        """
        تولید نام امن برای فایل
        """
        # استخراج پسوند
        name, ext = os.path.splitext(original_name)
        
        # تولید نام تصادفی
        random_name = secrets.token_hex(16)
        
        # ترکیب نام و پسوند
        secure_name = f"{random_name}{ext}"
        
        return secure_name
    
    def is_allowed_file_type(self, content):
        """
        بررسی نوع فایل مجاز
        """
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf', 'text/plain',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        
        # تشخیص نوع فایل
        content_type = mimetypes.guess_type(content.name)[0]
        
        return content_type in allowed_types
    
    def get_max_file_size(self):
        """
        حداکثر اندازه فایل مجاز (5MB)
        """
        return 5 * 1024 * 1024  # 5MB

class DataEncryption:
    """
    کلاس رمزگذاری داده‌ها
    """
    
    @staticmethod
    def encrypt_sensitive_data(data, key=None):
        """
        رمزگذاری داده‌های حساس
        """
        if key is None:
            key = settings.SECRET_KEY
        
        # استفاده از hash برای رمزگذاری ساده
        # در production از کتابخانه‌های تخصصی استفاده کنید
        encrypted = hashlib.sha256((data + key).encode()).hexdigest()
        return encrypted
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        هش کردن رمز عبور
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # ترکیب رمز عبور و نمک
        combined = password + salt
        
        # تولید هش
        password_hash = hashlib.pbkdf2_hmac('sha256', combined.encode(), salt.encode(), 100000)
        
        return password_hash.hex(), salt

class DataBackup:
    """
    کلاس پشتیبان‌گیری امن داده‌ها
    """
    
    @staticmethod
    def create_encrypted_backup():
        """
        ایجاد پشتیبان رمزگذاری شده
        """
        try:
            from django.core.management import call_command
            import tempfile
            import zipfile
            import os
            
            # ایجاد فایل موقت
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
                # خروجی داده‌ها
                call_command('dumpdata', stdout=tmp_file)
                tmp_file.flush()
                
                # رمزگذاری فایل
                encrypted_file = DataBackup.encrypt_file(tmp_file.name)
                
                # حذف فایل موقت
                os.unlink(tmp_file.name)
                
                return encrypted_file
                
        except Exception as e:
            logger.error(f"Error creating encrypted backup: {e}")
            return None
    
    @staticmethod
    def encrypt_file(file_path):
        """
        رمزگذاری فایل
        """
        # پیاده‌سازی ساده - در production از کتابخانه‌های تخصصی استفاده کنید
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # رمزگذاری ساده
        encrypted_content = hashlib.sha256(content).hexdigest()
        
        # ذخیره فایل رمزگذاری شده
        encrypted_file_path = file_path + '.encrypted'
        with open(encrypted_file_path, 'w') as f:
            f.write(encrypted_content)
        
        return encrypted_file_path

class DataAnonymization:
    """
    کلاس ناشناس‌سازی داده‌ها
    """
    
    @staticmethod
    def anonymize_user_data(user):
        """
        ناشناس‌سازی داده‌های کاربر
        """
        # تغییر نام کاربری
        user.username = f"user_{secrets.token_hex(8)}"
        
        # تغییر ایمیل
        user.email = f"user_{secrets.token_hex(8)}@anonymized.com"
        
        # تغییر نام و نام خانوادگی
        user.first_name = "Anonymous"
        user.last_name = "User"
        
        user.save()
        
        logger.info(f"User data anonymized for user ID: {user.id}")
    
    @staticmethod
    def anonymize_sensitive_fields(model_instance, fields_to_anonymize):
        """
        ناشناس‌سازی فیلدهای حساس
        """
        for field_name in fields_to_anonymize:
            if hasattr(model_instance, field_name):
                original_value = getattr(model_instance, field_name)
                
                # تولید مقدار ناشناس
                anonymized_value = DataAnonymization.generate_anonymized_value(original_value)
                
                # تنظیم مقدار جدید
                setattr(model_instance, field_name, anonymized_value)
        
        model_instance.save()
    
    @staticmethod
    def generate_anonymized_value(original_value):
        """
        تولید مقدار ناشناس
        """
        if isinstance(original_value, str):
            # برای رشته‌ها
            return f"***{secrets.token_hex(4)}***"
        elif isinstance(original_value, (int, float)):
            # برای اعداد
            return 0
        else:
            # برای سایر انواع
            return None

class DataRetention:
    """
    کلاس مدیریت نگهداری داده‌ها
    """
    
    @staticmethod
    def cleanup_old_data():
        """
        پاک کردن داده‌های قدیمی
        """
        # پاک کردن session های قدیمی
        from django.contrib.sessions.models import Session
        old_sessions = Session.objects.filter(
            expire_date__lt=timezone.now()
        )
        deleted_sessions = old_sessions.count()
        old_sessions.delete()
        
        # پاک کردن لاگ های قدیمی
        from django.contrib.admin.models import LogEntry
        old_logs = LogEntry.objects.filter(
            action_time__lt=timezone.now() - timedelta(days=90)
        )
        deleted_logs = old_logs.count()
        old_logs.delete()
        
        logger.info(f"Cleaned up {deleted_sessions} old sessions and {deleted_logs} old logs")
        
        return {
            'deleted_sessions': deleted_sessions,
            'deleted_logs': deleted_logs
        }
    
    @staticmethod
    def archive_old_data():
        """
        آرشیو داده‌های قدیمی
        """
        # آرشیو تراکنش‌های قدیمی
        from construction.models import Transaction
        
        old_transactions = Transaction.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=365)
        )
        
        # ایجاد فایل آرشیو
        archive_data = []
        for transaction in old_transactions:
            archive_data.append({
                'id': transaction.id,
                'amount': str(transaction.amount),
                'date': transaction.date_shamsi.isoformat(),
                'type': transaction.transaction_type,
                'archived_at': timezone.now().isoformat()
            })
        
        # ذخیره آرشیو
        archive_file = f"archive_transactions_{timezone.now().strftime('%Y%m%d')}.json"
        archive_path = os.path.join(settings.MEDIA_ROOT, 'archives', archive_file)
        
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        import json
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
        # حذف داده‌های اصلی
        deleted_count = old_transactions.count()
        old_transactions.delete()
        
        logger.info(f"Archived {deleted_count} old transactions to {archive_file}")
        
        return {
            'archived_count': deleted_count,
            'archive_file': archive_file
        }

class DataIntegrity:
    """
    کلاس بررسی یکپارچگی داده‌ها
    """
    
    @staticmethod
    def verify_data_integrity():
        """
        بررسی یکپارچگی داده‌ها
        """
        integrity_issues = []
        
        # بررسی تراکنش‌ها
        from construction.models import Transaction, Project, Investor, Period
        
        # تراکنش‌های بدون پروژه
        orphaned_transactions = Transaction.objects.filter(project__isnull=True)
        if orphaned_transactions.exists():
            integrity_issues.append({
                'type': 'orphaned_transactions',
                'count': orphaned_transactions.count(),
                'description': 'تراکنش‌های بدون پروژه'
            })
        
        # تراکنش‌های بدون سرمایه‌گذار
        transactions_without_investor = Transaction.objects.filter(investor__isnull=True)
        if transactions_without_investor.exists():
            integrity_issues.append({
                'type': 'transactions_without_investor',
                'count': transactions_without_investor.count(),
                'description': 'تراکنش‌های بدون سرمایه‌گذار'
            })
        
        # تراکنش‌های بدون دوره
        transactions_without_period = Transaction.objects.filter(period__isnull=True)
        if transactions_without_period.exists():
            integrity_issues.append({
                'type': 'transactions_without_period',
                'count': transactions_without_period.count(),
                'description': 'تراکنش‌های بدون دوره'
            })
        
        # بررسی مقادیر منفی
        negative_amounts = Transaction.objects.filter(amount__lt=0)
        if negative_amounts.exists():
            integrity_issues.append({
                'type': 'negative_amounts',
                'count': negative_amounts.count(),
                'description': 'تراکنش‌های با مبلغ منفی'
            })
        
        return integrity_issues
    
    @staticmethod
    def fix_integrity_issues(issues):
        """
        رفع مشکلات یکپارچگی
        """
        fixed_count = 0
        
        for issue in issues:
            if issue['type'] == 'orphaned_transactions':
                # حذف تراکنش‌های بدون پروژه
                from construction.models import Transaction
                deleted = Transaction.objects.filter(project__isnull=True).delete()[0]
                fixed_count += deleted
            
            elif issue['type'] == 'negative_amounts':
                # تصحیح مقادیر منفی
                from construction.models import Transaction
                updated = Transaction.objects.filter(amount__lt=0).update(amount=0)
                fixed_count += updated
        
        logger.info(f"Fixed {fixed_count} integrity issues")
        return fixed_count
