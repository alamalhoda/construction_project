#!/usr/bin/env python3
"""
اسکریپت تست برای بررسی عملکرد تبدیل ریال به تومان
Test script to check Rial to Toman conversion functionality
"""

import os
import sys
import django
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from construction.models import Unit, Transaction, Expense, Sale

def test_conversion():
    """تست عملکرد تبدیل"""
    print("🧪 تست عملکرد تبدیل ریال به تومان")
    print("=" * 50)
    
    # شمارش رکوردها
    units_count = Unit.objects.count()
    transactions_count = Transaction.objects.count()
    expenses_count = Expense.objects.count()
    sales_count = Sale.objects.count()
    
    print(f"📊 آمار فعلی دیتابیس:")
    print(f"  🏠 واحدها: {units_count}")
    print(f"  💳 تراکنش‌ها: {transactions_count}")
    print(f"  💸 هزینه‌ها: {expenses_count}")
    print(f"  🛒 فروش‌ها: {sales_count}")
    
    total_records = units_count + transactions_count + expenses_count + sales_count
    print(f"\n🎯 مجموع رکوردهای قابل تبدیل: {total_records}")
    
    # نمایش نمونه مقادیر
    if units_count > 0:
        print(f"\n💡 نمونه مقادیر فعلی:")
        unit = Unit.objects.first()
        print(f"  🏠 {unit.name}:")
        print(f"    قیمت/متر: {unit.price_per_meter:,} ریال → {unit.price_per_meter / 10:,.0f} تومان")
        print(f"    قیمت کل: {unit.total_price:,} ریال → {unit.total_price / 10:,.0f} تومان")
    
    if transactions_count > 0:
        transaction = Transaction.objects.first()
        print(f"  💳 {transaction.investor} - {transaction.get_transaction_type_display()}:")
        print(f"    مبلغ: {transaction.amount:,} ریال → {transaction.amount / 10:,.0f} تومان")
    
    print(f"\n✅ آماده برای تبدیل {total_records} رکورد")

if __name__ == "__main__":
    test_conversion()
