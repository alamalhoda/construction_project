#!/usr/bin/env python
"""
اسکریپت تصحیح نوع تراکنش‌ها

قاعده تصحیح:
- مقادیر منفی: خروج از سرمایه ↔ سود (جابجایی)
- مقادیر مثبت: آورده ↔ سود (جابجایی)
"""

import os
import sys
import django
from pathlib import Path
from decimal import Decimal

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from construction.models import Transaction


def get_corrected_transaction_type(current_type, amount):
    """
    تعیین نوع تراکنش صحیح بر اساس قاعده
    """
    if amount < 0:  # مقادیر منفی
        if current_type == 'principal_withdrawal':
            return 'profit_accrual'
        elif current_type == 'profit_accrual':
            return 'principal_withdrawal'
    else:  # مقادیر مثبت
        if current_type == 'principal_deposit':
            return 'profit_accrual'
        elif current_type == 'profit_accrual':
            return 'principal_deposit'
    
    return current_type  # سایر موارد بدون تغییر


def analyze_corrections_needed():
    """
    تحلیل تعداد تراکنش‌هایی که نیاز به تصحیح دارند
    """
    print("🔍 تحلیل تراکنش‌های نیازمند تصحیح...")
    print("=" * 60)
    
    corrections_needed = 0
    corrections_by_type = {
        'negative_principal_withdrawal_to_profit': 0,
        'negative_profit_to_principal_withdrawal': 0,
        'positive_principal_deposit_to_profit': 0,
        'positive_profit_to_principal_deposit': 0,
    }
    
    all_transactions = Transaction.objects.all()
    
    for transaction in all_transactions:
        current_type = transaction.transaction_type
        amount = transaction.amount
        corrected_type = get_corrected_transaction_type(current_type, amount)
        
        if corrected_type != current_type:
            corrections_needed += 1
            
            # آمار تفصیلی
            if amount < 0:
                if current_type == 'principal_withdrawal':
                    corrections_by_type['negative_principal_withdrawal_to_profit'] += 1
                elif current_type == 'profit_accrual':
                    corrections_by_type['negative_profit_to_principal_withdrawal'] += 1
            else:
                if current_type == 'principal_deposit':
                    corrections_by_type['positive_principal_deposit_to_profit'] += 1
                elif current_type == 'profit_accrual':
                    corrections_by_type['positive_profit_to_principal_deposit'] += 1
    
    print(f"📊 کل تراکنش‌ها: {all_transactions.count()}")
    print(f"🔧 نیاز به تصحیح: {corrections_needed}")
    print(f"✅ صحیح: {all_transactions.count() - corrections_needed}")
    
    print("\n📋 تفصیل تصحیحات مورد نیاز:")
    print(f"  منفی: خروج از سرمایه → سود: {corrections_by_type['negative_principal_withdrawal_to_profit']}")
    print(f"  منفی: سود → خروج از سرمایه: {corrections_by_type['negative_profit_to_principal_withdrawal']}")
    print(f"  مثبت: آورده → سود: {corrections_by_type['positive_principal_deposit_to_profit']}")
    print(f"  مثبت: سود → آورده: {corrections_by_type['positive_profit_to_principal_deposit']}")
    
    return corrections_needed, corrections_by_type


def apply_corrections(dry_run=True):
    """
    اعمال تصحیحات
    """
    mode_text = "🧪 حالت تست (بدون تغییر)" if dry_run else "🚀 اعمال تغییرات"
    print(f"\n{mode_text}")
    print("=" * 60)
    
    corrected_count = 0
    
    all_transactions = Transaction.objects.all()
    
    for transaction in all_transactions:
        current_type = transaction.transaction_type
        amount = transaction.amount
        corrected_type = get_corrected_transaction_type(current_type, amount)
        
        if corrected_type != current_type:
            corrected_count += 1
            
            if dry_run:
                print(f"  ID {transaction.id}: {current_type} → {corrected_type} (مبلغ: {amount})")
            else:
                transaction.transaction_type = corrected_type
                transaction.save()
                print(f"  ✅ ID {transaction.id}: {current_type} → {corrected_type}")
    
    if not dry_run:
        print(f"\n🎉 {corrected_count} تراکنش با موفقیت تصحیح شد!")
    else:
        print(f"\n📊 {corrected_count} تراکنش آماده تصحیح است.")
    
    return corrected_count


def verify_corrections():
    """
    تایید صحت تصحیحات
    """
    print("\n🔍 تایید صحت تصحیحات...")
    print("=" * 60)
    
    remaining_errors = 0
    all_transactions = Transaction.objects.all()
    
    for transaction in all_transactions:
        current_type = transaction.transaction_type
        amount = transaction.amount
        corrected_type = get_corrected_transaction_type(current_type, amount)
        
        if corrected_type != current_type:
            remaining_errors += 1
            print(f"  ❌ ID {transaction.id}: هنوز نیاز به تصحیح دارد")
    
    if remaining_errors == 0:
        print("✅ همه تراکنش‌ها صحیح هستند!")
    else:
        print(f"❌ {remaining_errors} تراکنش هنوز نیاز به تصحیح دارد!")
    
    return remaining_errors == 0


def main():
    """
    تابع اصلی
    """
    print("🔧 اسکریپت تصحیح نوع تراکنش‌ها")
    print("=" * 60)
    
    # مرحله ۱: تحلیل
    corrections_needed, _ = analyze_corrections_needed()
    
    if corrections_needed == 0:
        print("\n✅ همه تراکنش‌ها از قبل صحیح هستند!")
        return
    
    # مرحله ۲: نمایش تغییرات (حالت تست)
    print(f"\n🧪 نمایش تغییرات (حالت تست):")
    apply_corrections(dry_run=True)
    
    # مرحله ۳: درخواست تأیید
    print("\n" + "=" * 60)
    print("⚠️  آیا می‌خواهید تصحیحات اعمال شود؟")
    print("برای تأیید 'yes' تایپ کنید، برای لغو Enter بزنید:")
    
    try:
        user_input = input().strip().lower()
        if user_input != 'yes':
            print("❌ عملیات لغو شد.")
            return
    except KeyboardInterrupt:
        print("\n❌ عملیات لغو شد.")
        return
    
    # مرحله ۴: اعمال تصحیحات
    apply_corrections(dry_run=False)
    
    # مرحله ۵: تایید نهایی
    verify_corrections()


if __name__ == '__main__':
    main()
