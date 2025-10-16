from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import shutil
import os
from django.conf import settings
from construction.models import Transaction


class Command(BaseCommand):
    help = 'اصلاح تراکنش‌های برداشت که مبلغ مثبت دارند (تبدیل به منفی)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش تراکنش‌هایی که اصلاح خواهند شد بدون انجام تغییرات',
        )
        parser.add_argument(
            '--no-backup',
            action='store_true',
            help='ایجاد نکردن backup قبل از اصلاح (خطرناک)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== ابزار اصلاح مبالغ تراکنش‌های برداشت ===')
        )
        
        # یافتن تراکنش‌های برداشت با مبلغ مثبت
        problematic_transactions = Transaction.objects.filter(
            transaction_type='principal_withdrawal',
            amount__gt=0
        ).order_by('id')
        
        if not problematic_transactions.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ همه تراکنش‌های برداشت به درستی منفی هستند. هیچ تراکنشی نیاز به اصلاح ندارد.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  {problematic_transactions.count()} تراکنش برداشت با مبلغ مثبت یافت شد:')
        )
        self.stdout.write('')
        
        # نمایش لیست تراکنش‌های مشکل‌دار
        for trans in problematic_transactions:
            self.stdout.write(
                f'  ID: {trans.id} | مبلغ: {trans.amount:,.0f} تومان | '
                f'سرمایه‌گذار: {trans.investor.first_name} {trans.investor.last_name} | '
                f'تاریخ: {trans.date_shamsi} | توضیحات: {trans.description or "-"}'
            )
        
        self.stdout.write('')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS('🔍 حالت dry-run: هیچ تغییری انجام نشد. برای انجام اصلاحات از --dry-run استفاده نکنید.')
            )
            return
        
        # درخواست تایید از کاربر
        self.stdout.write(
            self.style.WARNING('⚠️  این عملیات مبالغ تراکنش‌های برداشت را منفی خواهد کرد.')
        )
        
        if not options['no_backup']:
            self.stdout.write(
                self.style.SUCCESS('📦 قبل از اصلاح، backup خودکار از دیتابیس ایجاد خواهد شد.')
            )
        
        confirm = input('\nآیا مطمئن هستید که می‌خواهید ادامه دهید؟ (yes/no): ')
        
        if confirm.lower() not in ['yes', 'y', 'بله']:
            self.stdout.write(self.style.ERROR('عملیات لغو شد.'))
            return
        
        try:
            # ایجاد backup
            if not options['no_backup']:
                self.create_backup()
            
            # انجام اصلاحات در یک transaction
            with transaction.atomic():
                fixed_count = 0
                for trans in problematic_transactions:
                    old_amount = trans.amount
                    trans.amount = -trans.amount
                    trans.save(update_fields=['amount'])
                    fixed_count += 1
                    
                    self.stdout.write(
                        f'✅ تراکنش ID {trans.id}: {old_amount:,.0f} تومان → {trans.amount:,.0f} تومان'
                    )
            
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(f'🎉 عملیات با موفقیت انجام شد!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'📊 {fixed_count} تراکنش اصلاح شد.')
            )
            
            # نمایش آمار نهایی
            self.show_final_stats()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در انجام عملیات: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR('عملیات لغو شد. دیتابیس تغییر نکرده است.')
            )

    def create_backup(self):
        """ایجاد backup از دیتابیس"""
        try:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_before_fix_withdrawals_{timestamp}.sqlite3'
            
            # مسیر دیتابیس اصلی
            db_path = settings.DATABASES['default']['NAME']
            
            # مسیر backup
            backup_dir = os.path.join(settings.BASE_DIR, 'database')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # کپی دیتابیس
            shutil.copy2(db_path, backup_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'📦 Backup ایجاد شد: {backup_filename}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'⚠️  خطا در ایجاد backup: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('ادامه عملیات بدون backup...')
            )

    def show_final_stats(self):
        """نمایش آمار نهایی"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📈 آمار نهایی:'))
        
        # شمارش تراکنش‌های برداشت
        all_withdrawals = Transaction.objects.filter(
            transaction_type='principal_withdrawal'
        )
        
        positive_withdrawals = all_withdrawals.filter(amount__gt=0).count()
        negative_withdrawals = all_withdrawals.filter(amount__lt=0).count()
        zero_withdrawals = all_withdrawals.filter(amount=0).count()
        
        self.stdout.write(f'  • تراکنش‌های برداشت مثبت: {positive_withdrawals}')
        self.stdout.write(f'  • تراکنش‌های برداشت منفی: {negative_withdrawals}')
        self.stdout.write(f'  • تراکنش‌های برداشت صفر: {zero_withdrawals}')
        
        if positive_withdrawals == 0:
            self.stdout.write(
                self.style.SUCCESS('  ✅ همه تراکنش‌های برداشت به درستی منفی هستند!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  هنوز {positive_withdrawals} تراکنش برداشت مثبت وجود دارد.')
            )
