#!/usr/bin/env python
"""
اسکریپت ساده تصحیح نوع تراکنش‌ها

قاعده تصحیح:
- مقادیر منفی: خروج از سرمایه ↔ سود (جابجایی)
- مقادیر مثبت: آورده ↔ سود (جابجایی)
"""

import os
import sys
import django
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from construction.models import Transaction


def main():
    """
    تابع اصلی - تصحیح مستقیم
    """
    print("🔧 شروع تصحیح نوع تراکنش‌ها...")
    print("=" * 60)
    
    # شمارنده‌ها
    total_fixed = 0
    errors = 0
    
    # دریافت همه تراکنش‌ها
    all_transactions = Transaction.objects.all()
    print(f"📊 تعداد کل تراکنش‌ها: {all_transactions.count()}")
    
    # پردازش هر تراکنش
    for transaction in all_transactions:
        try:
            original_type = transaction.transaction_type
            amount = transaction.amount
            new_type = None
            
            # تعیین نوع جدید بر اساس قاعده
            if amount < 0:  # مقادیر منفی
                if original_type == 'principal_withdrawal':
                    new_type = 'profit_accrual'
                elif original_type == 'profit_accrual':
                    new_type = 'principal_withdrawal'
            else:  # مقادیر مثبت
                if original_type == 'principal_deposit':
                    new_type = 'profit_accrual'
                elif original_type == 'profit_accrual':
                    new_type = 'principal_deposit'
            
            # اعمال تغییر در صورت نیاز
            if new_type and new_type != original_type:
                transaction.transaction_type = new_type
                transaction.save()
                total_fixed += 1
                print(f"✅ ID {transaction.id}: {original_type} → {new_type} (مبلغ: {amount})")
                
        except Exception as e:
            errors += 1
            print(f"❌ خطا در ID {transaction.id}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎉 تصحیح کامل شد!")
    print(f"📈 تراکنش‌های تصحیح شده: {total_fixed}")
    print(f"❌ خطاها: {errors}")
    
    # گزارش نهایی
    print("\n🔍 وضعیت نهایی:")
    print("-" * 40)
    
    for tx_type in ['principal_deposit', 'profit_accrual', 'principal_withdrawal']:
        count = Transaction.objects.filter(transaction_type=tx_type).count()
        positive_count = Transaction.objects.filter(transaction_type=tx_type, amount__gt=0).count()
        negative_count = Transaction.objects.filter(transaction_type=tx_type, amount__lt=0).count()
        print(f"{tx_type}: {count} (مثبت: {positive_count}, منفی: {negative_count})")


if __name__ == '__main__':
    main()
