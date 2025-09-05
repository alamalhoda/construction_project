"""
Management Command برای دانلود دیتابیس آنلاین
Download Online Database Management Command
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class Command(BaseCommand):
    help = 'دانلود دیتابیس آنلاین از GitHub و جایگزینی با دیتابیس محلی'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-local',
            action='store_true',
            help='ایجاد backup از دیتابیس محلی قبل از جایگزینی',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='تأیید جایگزینی دیتابیس محلی',
        )
        parser.add_argument(
            '--branch',
            default='master',
            help='شاخه Git برای دانلود (پیش‌فرض: master)',
        )
    
    def handle(self, *args, **options):
        backup_local = options['backup_local']
        confirm = options['confirm']
        branch = options['branch']
        
        self.stdout.write("🔄 دانلود دیتابیس آنلاین از GitHub")
        self.stdout.write("=" * 50)
        
        # بررسی وجود دیتابیس محلی
        local_db = Path('database/local.sqlite3')
        online_db = Path('database/online.sqlite3')
        
        # تأیید جایگزینی
        if not confirm:
            self.stdout.write(
                self.style.WARNING('⚠️  این عمل دیتابیس محلی را بازنویسی می‌کند!')
            )
            self.stdout.write('برای تأیید، --confirm را اضافه کنید')
            return
        
        try:
            # ایجاد backup از دیتابیس محلی
            if backup_local and local_db.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"database/local_backup_{timestamp}.sqlite3"
                shutil.copy2(local_db, backup_name)
                self.stdout.write(f"💾 Backup محلی: {backup_name}")
            
            # دانلود از GitHub
            self.stdout.write(f"📥 دانلود از شاخه {branch}...")
            
            # بررسی وضعیت Git
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                self.stdout.write(
                    self.style.WARNING('⚠️  تغییرات uncommitted وجود دارد!')
                )
                self.stdout.write('لطفاً ابتدا تغییرات را commit کنید')
                return
            
            # Stash تغییرات محلی
            subprocess.run(['git', 'stash'], check=True)
            self.stdout.write("💾 تغییرات محلی stash شد")
            
            # Pull از GitHub
            subprocess.run(['git', 'pull', 'origin', branch], check=True)
            self.stdout.write("✅ Pull از GitHub انجام شد")
            
            # بررسی وجود دیتابیس آنلاین
            if not online_db.exists():
                self.stdout.write(
                    self.style.ERROR('❌ دیتابیس آنلاین در GitHub یافت نشد!')
                )
                return
            
            # جایگزینی دیتابیس
            shutil.copy2(online_db, local_db)
            
            # Restore تغییرات محلی
            subprocess.run(['git', 'stash', 'pop'], check=True)
            self.stdout.write("🔄 تغییرات محلی restore شد")
            
            self.stdout.write(
                self.style.SUCCESS('✅ دیتابیس آنلاین با موفقیت دانلود شد')
            )
            self.stdout.write('💡 حالا می‌توانید روی دیتابیس محلی کار کنید')
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در Git: {e}')
            )
            # Restore تغییرات در صورت خطا
            try:
                subprocess.run(['git', 'stash', 'pop'], check=True)
            except:
                pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در دانلود: {e}')
            )
