"""
Management Command برای تبدیل تمام فیلدهای رقمی از ریال به تومان
Convert Rial to Toman Management Command
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from construction.models import (
    Unit, Transaction, Expense, Sale, InterestRate
)

class Command(BaseCommand):
    help = 'تبدیل تمام فیلدهای رقمی از ریال به تومان (تقسیم بر ۱۰)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش تغییرات بدون اعمال آن‌ها',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='ایجاد بکاپ قبل از تبدیل',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        create_backup = options['backup']
        
        self.stdout.write("💰 شروع تبدیل ریال به تومان")
        self.stdout.write("=" * 50)
        
        if dry_run:
            self.stdout.write("🔍 حالت آزمایشی: هیچ تغییری اعمال نخواهد شد")
        
        if create_backup:
            self.stdout.write("💾 ایجاد بکاپ قبل از تبدیل...")
            self.create_backup()
        
        # تبدیل فیلدهای رقمی
        conversion_stats = {}
        
        try:
            with transaction.atomic():
                # تبدیل واحدها
                conversion_stats['units'] = self.convert_units(dry_run)
                
                # تبدیل تراکنش‌ها
                conversion_stats['transactions'] = self.convert_transactions(dry_run)
                
                # تبدیل هزینه‌ها
                conversion_stats['expenses'] = self.convert_expenses(dry_run)
                
                # تبدیل فروش‌ها
                conversion_stats['sales'] = self.convert_sales(dry_run)
                
                # تبدیل نرخ سود (این فیلد نیازی به تبدیل ندارد چون درصد است)
                conversion_stats['interest_rates'] = self.convert_interest_rates(dry_run)
                
                if dry_run:
                    # در حالت dry-run، transaction را rollback می‌کنیم
                    transaction.set_rollback(True)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ خطا در تبدیل: {str(e)}")
            )
            raise
        
        # نمایش آمار
        self.display_conversion_stats(conversion_stats)
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS("✅ تبدیل ریال به تومان با موفقیت انجام شد")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ حالت آزمایشی - هیچ تغییری اعمال نشد")
            )
    
    def create_backup(self):
        """ایجاد بکاپ از دیتابیس"""
        try:
            from backup.management.commands.create_backup import Command as BackupCommand
            backup_cmd = BackupCommand()
            backup_cmd.handle()
            self.stdout.write("✅ بکاپ با موفقیت ایجاد شد")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ خطا در ایجاد بکاپ: {str(e)}")
            )
    
    def convert_units(self, dry_run=False):
        """تبدیل فیلدهای رقمی واحدها"""
        self.stdout.write("\n🏠 تبدیل واحدها...")
        
        units = Unit.objects.all()
        count = 0
        
        for unit in units:
            old_price_per_meter = unit.price_per_meter
            old_total_price = unit.total_price
            
            # تبدیل قیمت‌ها
            unit.price_per_meter = unit.price_per_meter / Decimal('10')
            unit.total_price = unit.total_price / Decimal('10')
            
            if not dry_run:
                unit.save()
            
            count += 1
            
            self.stdout.write(
                f"  🏠 {unit.name}: "
                f"قیمت/متر {old_price_per_meter} → {unit.price_per_meter}, "
                f"قیمت کل {old_total_price} → {unit.total_price}"
            )
        
        return count
    
    def convert_transactions(self, dry_run=False):
        """تبدیل فیلدهای رقمی تراکنش‌ها"""
        self.stdout.write("\n💳 تبدیل تراکنش‌ها...")
        
        transactions = Transaction.objects.all()
        count = 0
        
        for transaction in transactions:
            old_amount = transaction.amount
            
            # تبدیل مبلغ
            transaction.amount = transaction.amount / Decimal('10')
            
            if not dry_run:
                transaction.save()
            
            count += 1
            
            if count <= 5:  # نمایش فقط 5 تراکنش اول برای جلوگیری از خروجی زیاد
                self.stdout.write(
                    f"  💳 {transaction.investor} - {transaction.get_transaction_type_display()}: "
                    f"{old_amount} → {transaction.amount}"
                )
            elif count == 6:
                self.stdout.write(f"  ... و {len(transactions) - 5} تراکنش دیگر")
        
        return count
    
    def convert_expenses(self, dry_run=False):
        """تبدیل فیلدهای رقمی هزینه‌ها"""
        self.stdout.write("\n💸 تبدیل هزینه‌ها...")
        
        expenses = Expense.objects.all()
        count = 0
        
        for expense in expenses:
            old_amount = expense.amount
            
            # تبدیل مبلغ
            expense.amount = expense.amount / Decimal('10')
            
            if not dry_run:
                expense.save()
            
            count += 1
            
            if count <= 5:  # نمایش فقط 5 هزینه اول
                self.stdout.write(
                    f"  💸 {expense.get_expense_type_display()} - {expense.period}: "
                    f"{old_amount} → {expense.amount}"
                )
            elif count == 6:
                self.stdout.write(f"  ... و {len(expenses) - 5} هزینه دیگر")
        
        return count
    
    def convert_sales(self, dry_run=False):
        """تبدیل فیلدهای رقمی فروش‌ها"""
        self.stdout.write("\n🛒 تبدیل فروش‌ها...")
        
        sales = Sale.objects.all()
        count = 0
        
        for sale in sales:
            old_amount = sale.amount
            
            # تبدیل مبلغ
            sale.amount = sale.amount / Decimal('10')
            
            if not dry_run:
                sale.save()
            
            count += 1
            
            if count <= 5:  # نمایش فقط 5 فروش اول
                self.stdout.write(
                    f"  🛒 {sale.project} - {sale.period}: "
                    f"{old_amount} → {sale.amount}"
                )
            elif count == 6:
                self.stdout.write(f"  ... و {len(sales) - 5} فروش دیگر")
        
        return count
    
    def convert_interest_rates(self, dry_run=False):
        """تبدیل نرخ‌های سود (نیازی به تبدیل ندارد چون درصد است)"""
        self.stdout.write("\n📈 بررسی نرخ‌های سود...")
        
        rates = InterestRate.objects.all()
        count = len(rates)
        
        self.stdout.write(
            f"  📈 {count} نرخ سود یافت شد (نیازی به تبدیل ندارند - درصد هستند)"
        )
        
        return 0  # هیچ تغییری اعمال نشد
    
    def display_conversion_stats(self, stats):
        """نمایش آمار تبدیل"""
        self.stdout.write("\n📊 آمار تبدیل:")
        self.stdout.write("=" * 30)
        
        total_records = 0
        for model_name, count in stats.items():
            if count > 0:
                self.stdout.write(f"  📋 {model_name}: {count} رکورد")
                total_records += count
        
        self.stdout.write(f"\n🎯 مجموع: {total_records} رکورد تبدیل شد")
        
        # نمایش نمونه‌ای از مقادیر جدید
        self.stdout.write("\n💡 نمونه مقادیر تبدیل شده:")
        self.stdout.write("  🔸 ریال 1,000,000 → تومان 100,000")
        self.stdout.write("  🔸 ریال 50,000 → تومان 5,000")
        self.stdout.write("  🔸 ریال 2,500 → تومان 250")
