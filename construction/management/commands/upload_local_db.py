"""
Management Command برای آپلود دیتابیس محلی
Upload Local Database Management Command
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class Command(BaseCommand):
    help = 'آپلود دیتابیس محلی به GitHub و جایگزینی دیتابیس آنلاین'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-online',
            action='store_true',
            help='ایجاد backup از دیتابیس آنلاین قبل از جایگزینی',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='تأیید جایگزینی دیتابیس آنلاین',
        )
        parser.add_argument(
            '--commit-message',
            default='Update database from local',
            help='پیام commit برای آپلود',
        )
    
    def handle(self, *args, **options):
        backup_online = options['backup_online']
        confirm = options['confirm']
        commit_message = options['commit_message']
        
        self.stdout.write("🔄 آپلود دیتابیس محلی به GitHub")
        self.stdout.write("=" * 50)
        
        # بررسی وجود دیتابیس محلی
        local_db = Path('database/local.sqlite3')
        online_db = Path('database/online.sqlite3')
        
        if not local_db.exists():
            self.stdout.write(
                self.style.ERROR('❌ دیتابیس محلی یافت نشد!')
            )
            return
        
        self.stdout.write(f"📁 دیتابیس محلی: {local_db}")
        self.stdout.write(f"📁 دیتابیس آنلاین: {online_db}")
        
        # تأیید جایگزینی
        if not confirm:
            self.stdout.write(
                self.style.WARNING('⚠️  این عمل دیتابیس آنلاین را بازنویسی می‌کند!')
            )
            self.stdout.write('برای تأیید، --confirm را اضافه کنید')
            return
        
        try:
            # ایجاد backup از دیتابیس آنلاین
            if backup_online and online_db.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"database/online_backup_{timestamp}.sqlite3"
                shutil.copy2(online_db, backup_name)
                self.stdout.write(f"💾 Backup آنلاین: {backup_name}")
            
            # جایگزینی دیتابیس
            shutil.copy2(local_db, online_db)
            self.stdout.write("✅ دیتابیس محلی کپی شد به آنلاین")
            
            # اضافه کردن به Git
            subprocess.run(['git', 'add', 'database/online.sqlite3'], check=True)
            self.stdout.write("✅ دیتابیس آنلاین اضافه شد به Git")
            
            # Commit
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            self.stdout.write("✅ تغییرات commit شد")
            
            # Push به GitHub
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            self.stdout.write("✅ تغییرات push شد به GitHub")
            
            self.stdout.write(
                self.style.SUCCESS('✅ دیتابیس محلی با موفقیت آپلود شد')
            )
            self.stdout.write('💡 دیتابیس آنلاین در GitHub به‌روزرسانی شد')
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در Git: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در آپلود: {e}')
            )
