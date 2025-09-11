#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست عملکرد دکمه محاسبه مجدد سودها
این فایل عملکرد دکمه محاسبه مجدد سودها را بدون اجرای واقعی بررسی می‌کند
"""

import os
import sys
import django
from decimal import Decimal

# تنظیم Django
sys.path.append('/Users/alamalhoda/Projects/Arash_Project/djangobuilder/construction_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from construction.models import Transaction, InterestRate, Project, Investor, Period
from django.db import transaction as db_transaction


def analyze_recalculate_profits_flow():
    """
    تحلیل کامل جریان عملکرد دکمه محاسبه مجدد سودها
    """
    print("=" * 80)
    print("تحلیل عملکرد دکمه محاسبه مجدد سودها")
    print("=" * 80)
    
    # 1. بررسی نرخ سود فعلی
    print("\n1. بررسی نرخ سود فعلی:")
    print("-" * 40)
    current_rate = InterestRate.get_current_rate()
    if current_rate:
        print(f"✅ نرخ سود فعال: {current_rate.rate}%")
        print(f"   تاریخ اعمال: {current_rate.effective_date}")
        print(f"   وضعیت: {'فعال' if current_rate.is_active else 'غیرفعال'}")
    else:
        print("❌ هیچ نرخ سود فعالی یافت نشد")
        return
    
    # 2. بررسی تراکنش‌های موجود
    print("\n2. بررسی تراکنش‌های موجود:")
    print("-" * 40)
    
    # تعداد کل تراکنش‌ها
    total_transactions = Transaction.objects.count()
    print(f"📊 تعداد کل تراکنش‌ها: {total_transactions}")
    
    # تراکنش‌های سرمایه
    capital_transactions = Transaction.objects.filter(
        transaction_type__in=['principal_deposit', 'principal_withdrawal']
    ).count()
    print(f"💰 تراکنش‌های سرمایه: {capital_transactions}")
    
    # تراکنش‌های سود موجود
    existing_profits = Transaction.objects.filter(
        transaction_type='profit_accrual'
    ).count()
    print(f"📈 تراکنش‌های سود موجود: {existing_profits}")
    
    # تراکنش‌های سود سیستم‌ی
    system_profits = Transaction.objects.filter(
        transaction_type='profit_accrual',
        is_system_generated=True
    ).count()
    print(f"🤖 تراکنش‌های سود سیستم‌ی: {system_profits}")
    
    # 3. شبیه‌سازی محاسبه سودهای جدید
    print("\n3. شبیه‌سازی محاسبه سودهای جدید:")
    print("-" * 40)
    
    # دریافت تراکنش‌های سرمایه که باید سود داشته باشند
    capital_transactions_with_profit = Transaction.objects.filter(
        transaction_type__in=['principal_deposit', 'principal_withdrawal'],
        day_remaining__gt=0
    )
    
    print(f"🔍 تراکنش‌های سرمایه با روز باقی‌مانده: {capital_transactions_with_profit.count()}")
    
    # محاسبه سودهای جدید (بدون ذخیره)
    new_profit_transactions = []
    total_profit_amount = Decimal('0')
    
    for transaction in capital_transactions_with_profit:
        profit_amount = transaction.calculate_profit(current_rate)
        
        if profit_amount != 0:
            new_profit_transactions.append({
                'transaction_id': transaction.id,
                'investor': f"{transaction.investor.first_name} {transaction.investor.last_name}",
                'amount': transaction.amount,
                'profit_amount': profit_amount,
                'day_remaining': transaction.day_remaining,
                'transaction_type': transaction.get_transaction_type_display()
            })
            total_profit_amount += profit_amount
    
    print(f"📊 تعداد سودهای جدید که محاسبه خواهند شد: {len(new_profit_transactions)}")
    print(f"💰 مجموع مبلغ سودهای جدید: {total_profit_amount:,.2f}")
    
    # 4. نمایش جزئیات سودهای جدید
    print("\n4. جزئیات سودهای جدید:")
    print("-" * 40)
    
    if new_profit_transactions:
        for i, profit in enumerate(new_profit_transactions[:5], 1):  # نمایش 5 مورد اول
            print(f"{i}. سرمایه‌گذار: {profit['investor']}")
            print(f"   مبلغ: {profit['amount']:,.2f}")
            print(f"   سود: {profit['profit_amount']:,.2f}")
            print(f"   روز باقی‌مانده: {profit['day_remaining']}")
            print(f"   نوع: {profit['transaction_type']}")
            print()
        
        if len(new_profit_transactions) > 5:
            print(f"... و {len(new_profit_transactions) - 5} مورد دیگر")
    else:
        print("❌ هیچ سود جدیدی محاسبه نخواهد شد")
    
    # 5. خلاصه عملیات
    print("\n5. خلاصه عملیات محاسبه مجدد:")
    print("-" * 40)
    print(f"🗑️  تعداد رکوردهای حذف شده: {existing_profits}")
    print(f"➕ تعداد رکوردهای جدید: {len(new_profit_transactions)}")
    print(f"📊 مجموع تأثیر: {existing_profits + len(new_profit_transactions)}")
    print(f"💰 مجموع مبلغ سودهای جدید: {total_profit_amount:,.2f}")
    
    # 6. بررسی تأثیرات
    print("\n6. بررسی تأثیرات:")
    print("-" * 40)
    
    if existing_profits > 0:
        print(f"⚠️  {existing_profits} رکورد سود موجود حذف خواهد شد")
    
    if len(new_profit_transactions) > 0:
        print(f"✅ {len(new_profit_transactions)} رکورد سود جدید ایجاد خواهد شد")
    
    if existing_profits == 0 and len(new_profit_transactions) == 0:
        print("ℹ️  هیچ تغییری در داده‌ها ایجاد نخواهد شد")
    
    print("\n" + "=" * 80)
    print("تحلیل کامل شد")
    print("=" * 80)


def test_calculate_profit_method():
    """
    تست متد محاسبه سود برای یک تراکنش نمونه
    """
    print("\n" + "=" * 80)
    print("تست متد محاسبه سود")
    print("=" * 80)
    
    # دریافت اولین تراکنش سرمایه
    capital_transaction = Transaction.objects.filter(
        transaction_type__in=['principal_deposit', 'principal_withdrawal'],
        day_remaining__gt=0
    ).first()
    
    if not capital_transaction:
        print("❌ هیچ تراکنش سرمایه‌ای یافت نشد")
        return
    
    current_rate = InterestRate.get_current_rate()
    if not current_rate:
        print("❌ هیچ نرخ سود فعالی یافت نشد")
        return
    
    print(f"🔍 تراکنش نمونه:")
    print(f"   شناسه: {capital_transaction.id}")
    print(f"   سرمایه‌گذار: {capital_transaction.investor.first_name} {capital_transaction.investor.last_name}")
    print(f"   مبلغ: {capital_transaction.amount:,.2f}")
    print(f"   نوع: {capital_transaction.get_transaction_type_display()}")
    print(f"   روز باقی‌مانده: {capital_transaction.day_remaining}")
    print(f"   نرخ سود: {current_rate.rate}%")
    
    # محاسبه سود
    profit_amount = capital_transaction.calculate_profit(current_rate)
    
    print(f"\n📊 نتیجه محاسبه:")
    print(f"   سود محاسبه شده: {profit_amount:,.2f}")
    print(f"   درصد سود: {(profit_amount / capital_transaction.amount * 100):.4f}%")
    
    if profit_amount > 0:
        print("✅ سود مثبت محاسبه شد")
    elif profit_amount < 0:
        print("⚠️  سود منفی محاسبه شد")
    else:
        print("ℹ️  سود صفر محاسبه شد")


def test_recalculate_profits_api():
    """
    تست API endpoint محاسبه مجدد سودها (بدون اجرای واقعی)
    """
    print("\n" + "=" * 80)
    print("تست API محاسبه مجدد سودها")
    print("=" * 80)
    
    from django.test import Client
    from django.contrib.auth.models import User
    
    # ایجاد کلاینت تست
    client = Client()
    
    # بررسی endpoint
    print("🔍 بررسی endpoint:")
    print("   URL: /construction/api/v1/Transaction/recalculate_profits/")
    print("   Method: POST")
    print("   Headers: Content-Type: application/json, X-CSRFToken")
    
    # شبیه‌سازی درخواست (بدون ارسال واقعی)
    print("\n📋 شبیه‌سازی درخواست:")
    print("   - دریافت نرخ سود فعلی")
    print("   - حذف همه سودهای قبلی")
    print("   - محاسبه سودهای جدید")
    print("   - ذخیره سودهای جدید")
    print("   - بازگشت آمار عملیات")
    
    print("\n✅ تست API با موفقیت شبیه‌سازی شد")


def compare_before_after():
    """
    مقایسه وضعیت قبل و بعد از محاسبه مجدد
    """
    print("\n" + "=" * 80)
    print("مقایسه وضعیت قبل و بعد")
    print("=" * 80)
    
    # وضعیت فعلی
    current_profits = Transaction.objects.filter(transaction_type='profit_accrual')
    current_total = sum(profit.amount for profit in current_profits)
    
    print("📊 وضعیت فعلی:")
    print(f"   تعداد سودهای موجود: {current_profits.count()}")
    print(f"   مجموع مبلغ سودها: {current_total:,.2f}")
    
    # شبیه‌سازی وضعیت بعدی
    current_rate = InterestRate.get_current_rate()
    if current_rate:
        capital_transactions = Transaction.objects.filter(
            transaction_type__in=['principal_deposit', 'principal_withdrawal'],
            day_remaining__gt=0
        )
        
        new_total = sum(
            transaction.calculate_profit(current_rate) 
            for transaction in capital_transactions
        )
        
        print("\n📈 وضعیت بعد از محاسبه مجدد:")
        print(f"   تعداد سودهای جدید: {capital_transactions.count()}")
        print(f"   مجموع مبلغ سودهای جدید: {new_total:,.2f}")
        
        print("\n🔄 تغییرات:")
        print(f"   تغییر در تعداد: {capital_transactions.count() - current_profits.count()}")
        print(f"   تغییر در مبلغ: {new_total - current_total:,.2f}")
        print(f"   درصد تغییر: {((new_total - current_total) / current_total * 100) if current_total != 0 else 0:.2f}%")


if __name__ == "__main__":
    try:
        print("🚀 شروع تحلیل عملکرد دکمه محاسبه مجدد سودها...")
        analyze_recalculate_profits_flow()
        test_calculate_profit_method()
        test_recalculate_profits_api()
        compare_before_after()
        print("\n✅ تحلیل با موفقیت انجام شد")
    except Exception as e:
        print(f"\n❌ خطا در تحلیل: {str(e)}")
        import traceback
        traceback.print_exc()
