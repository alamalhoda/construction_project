#!/usr/bin/env python
"""
اسکریپت تست جداسازی پروژه‌ها
این اسکریپت بررسی می‌کند که:
1. داده‌های دو پروژه کاملاً جدا هستند
2. API فقط داده‌های پروژه جاری را برمی‌گرداند
3. تغییر پروژه، داده‌های نمایش داده شده را تغییر می‌دهد
"""

import os
import sys
import django

# تنظیم Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from django.contrib.auth.models import User
from construction.models import Project, Investor, Expense, Transaction, Unit, Period, Sale
from construction.project_manager import ProjectManager
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from datetime import date
from django_jalali.db.models import jDateField
import jdatetime


def create_test_data():
    """ایجاد داده‌های تست"""
    print("\n" + "="*80)
    print("📋 ایجاد داده‌های تست...")
    print("="*80)
    
    # ایجاد یا دریافت کاربر تست
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ کاربر تست ایجاد شد: {user.username}")
    else:
        print(f"ℹ️  کاربر تست موجود است: {user.username}")
    
    # ایجاد دو پروژه تست
    # تاریخ‌های شمسی و میلادی
    start_shamsi1 = jdatetime.date(1400, 1, 1)
    end_shamsi1 = jdatetime.date(1405, 12, 29)
    start_gregorian1 = jdatetime.JalaliToGregorian(1400, 1, 1).getGregorianList()
    end_gregorian1 = jdatetime.JalaliToGregorian(1405, 12, 29).getGregorianList()
    
    start_shamsi2 = jdatetime.date(1401, 1, 1)
    end_shamsi2 = jdatetime.date(1406, 12, 29)
    start_gregorian2 = jdatetime.JalaliToGregorian(1401, 1, 1).getGregorianList()
    end_gregorian2 = jdatetime.JalaliToGregorian(1406, 12, 29).getGregorianList()
    
    project1, created1 = Project.objects.get_or_create(
        name='پروژه تست 1',
        defaults={
            'start_date_shamsi': start_shamsi1,
            'end_date_shamsi': end_shamsi1,
            'start_date_gregorian': date(start_gregorian1[0], start_gregorian1[1], start_gregorian1[2]),
            'end_date_gregorian': date(end_gregorian1[0], end_gregorian1[1], end_gregorian1[2]),
            'is_active': False,
            'color': '#ff0000',
            'icon': 'fa-building'
        }
    )
    
    project2, created2 = Project.objects.get_or_create(
        name='پروژه تست 2',
        defaults={
            'start_date_shamsi': start_shamsi2,
            'end_date_shamsi': end_shamsi2,
            'start_date_gregorian': date(start_gregorian2[0], start_gregorian2[1], start_gregorian2[2]),
            'end_date_gregorian': date(end_gregorian2[0], end_gregorian2[1], end_gregorian2[2]),
            'is_active': False,
            'color': '#00ff00',
            'icon': 'fa-home'
        }
    )
    
    if created1:
        print(f"✅ پروژه 1 ایجاد شد: {project1.name} (ID: {project1.id})")
    else:
        print(f"ℹ️  پروژه 1 موجود است: {project1.name} (ID: {project1.id})")
    
    if created2:
        print(f"✅ پروژه 2 ایجاد شد: {project2.name} (ID: {project2.id})")
    else:
        print(f"ℹ️  پروژه 2 موجود است: {project2.name} (ID: {project2.id})")
    
    # حذف داده‌های قبلی تست (اگر وجود دارند)
    Investor.objects.filter(project__in=[project1, project2]).delete()
    Expense.objects.filter(project__in=[project1, project2]).delete()
    Transaction.objects.filter(project__in=[project1, project2]).delete()
    Unit.objects.filter(project__in=[project1, project2]).delete()
    Sale.objects.filter(project__in=[project1, project2]).delete()
    Period.objects.filter(project__in=[project1, project2]).delete()
    
    # ایجاد سرمایه‌گذار برای پروژه 1
    investor1 = Investor.objects.create(
        project=project1,
        first_name='احمد',
        last_name='محمدی',
        participation_type='owner'
    )
    print(f"✅ سرمایه‌گذار 1 ایجاد شد: {investor1.first_name} {investor1.last_name} (پروژه: {project1.name})")
    
    # حذف سرمایه‌گذاران قبلی پروژه 2 (اگر وجود دارند)
    Investor.objects.filter(project=project2).delete()
    
    # ایجاد 10 سرمایه‌گذار برای پروژه 2
    print("\n📊 ایجاد سرمایه‌گذاران برای پروژه 2...")
    
    investors_project2 = []
    
    # 3 مالک
    owner_names = [
        ('علی', 'رضایی'),
        ('محمد', 'احمدی'),
        ('حسن', 'کریمی'),
    ]
    
    for first_name, last_name in owner_names:
        investor = Investor.objects.create(
            project=project2,
            first_name=first_name,
            last_name=last_name,
            participation_type='owner'
        )
        investors_project2.append(investor)
        print(f"✅ مالک ایجاد شد: {investor.first_name} {investor.last_name} (پروژه: {project2.name})")
    
    # 7 سرمایه‌گذار
    investor_names = [
        ('رضا', 'موسوی'),
        ('سعید', 'نوری'),
        ('امیر', 'صادقی'),
        ('کامران', 'جعفری'),
        ('مجید', 'زاهدی'),
        ('ایمان', 'حسینی'),
        ('بهرام', 'رحمانی'),
    ]
    
    for first_name, last_name in investor_names:
        investor = Investor.objects.create(
        project=project2,
            first_name=first_name,
            last_name=last_name,
        participation_type='investor'
    )
        investors_project2.append(investor)
        print(f"✅ سرمایه‌گذار ایجاد شد: {investor.first_name} {investor.last_name} (پروژه: {project2.name})")
    
    # استفاده از اولین سرمایه‌گذار (مالک اول) برای داده‌های تست قبلی
    investor2 = investors_project2[0]
    print(f"\n✅ مجموع {len(investors_project2)} سرمایه‌گذار برای پروژه 2 ایجاد شد (3 مالک، 7 سرمایه‌گذار)")
    
    # ایجاد دوره برای پروژه 1 (برای Expense)
    period1, p_created1 = Period.objects.get_or_create(
        project=project1,
        year=1402,
        month_number=1,
        defaults={
            'label': 'فروردین 1402',
            'month_name': 'فروردین',
            'weight': 1.0,
            'start_date_shamsi': jdatetime.date(1402, 1, 1),
            'end_date_shamsi': jdatetime.date(1402, 1, 31),
            'start_date_gregorian': date(
                jdatetime.JalaliToGregorian(1402, 1, 1).getGregorianList()[0],
                jdatetime.JalaliToGregorian(1402, 1, 1).getGregorianList()[1],
                jdatetime.JalaliToGregorian(1402, 1, 1).getGregorianList()[2]
            ),
            'end_date_gregorian': date(
                jdatetime.JalaliToGregorian(1402, 1, 31).getGregorianList()[0],
                jdatetime.JalaliToGregorian(1402, 1, 31).getGregorianList()[1],
                jdatetime.JalaliToGregorian(1402, 1, 31).getGregorianList()[2]
            ),
        }
    )
    if p_created1:
        print(f"✅ دوره برای پروژه 1 ایجاد شد: {period1.label}")
    
    # ایجاد دوره برای پروژه 2 (برای Expense)
    period2, p_created2 = Period.objects.get_or_create(
        project=project2,
        year=1402,
        month_number=1,
        defaults={
            'label': 'فروردین 1402',
            'month_name': 'فروردین',
            'weight': 1.0,
            'start_date_shamsi': jdatetime.date(1402, 1, 1),
            'end_date_shamsi': jdatetime.date(1402, 1, 31),
            'start_date_gregorian': date(
                jdatetime.JalaliToGregorian(1402, 1, 1).getGregorianList()[0],
                jdatetime.JalaliToGregorian(1402, 1, 1).getGregorianList()[1],
                jdatetime.JalaliToGregorian(1402, 1, 1).getGregorianList()[2]
            ),
            'end_date_gregorian': date(
                jdatetime.JalaliToGregorian(1402, 1, 31).getGregorianList()[0],
                jdatetime.JalaliToGregorian(1402, 1, 31).getGregorianList()[1],
                jdatetime.JalaliToGregorian(1402, 1, 31).getGregorianList()[2]
            ),
        }
    )
    if p_created2:
        print(f"✅ دوره برای پروژه 2 ایجاد شد: {period2.label}")
    
    # حذف دوره‌های قبلی پروژه 2 (اگر وجود دارند)
    Period.objects.filter(project=project2).delete()
    
    # ایجاد دوره‌های سال 1405 و 1406 برای پروژه 2
    print("\n📊 ایجاد دوره‌های سال‌های 1405 و 1406 برای پروژه 2...")
    
    month_names = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    
    # تعداد روزهای هر ماه (برای سال عادی)
    month_days = {
        1: 31,   # فروردین
        2: 31,   # اردیبهشت
        3: 31,   # خرداد
        4: 31,   # تیر
        5: 31,   # مرداد
        6: 31,   # شهریور
        7: 30,   # مهر
        8: 30,   # آبان
        9: 30,   # آذر
        10: 30,  # دی
        11: 30,  # بهمن
        12: 29,  # اسفند (سال عادی)
    }
    
    periods_project2 = []
    
    # ایجاد دوره‌های سال 1405
    for month_num in range(1, 13):
        year = 1405
        month_name = month_names[month_num - 1]
        label = f'{month_name} {year}'
        
        # محاسبه تعداد روزهای ماه (برای اسفند باید بررسی کنیم که سال کبیسه است یا نه)
        if month_num == 12:
            # بررسی سال کبیسه
            try:
                # تلاش برای ایجاد روز 30 اسفند برای بررسی کبیسه بودن
                test_date = jdatetime.date(year, 12, 30)
                days_in_month = 30
            except ValueError:
                days_in_month = 29
        else:
            days_in_month = month_days[month_num]
        
        start_date_shamsi = jdatetime.date(year, month_num, 1)
        end_date_shamsi = jdatetime.date(year, month_num, days_in_month)
        
        # تبدیل به میلادی
        start_gregorian = start_date_shamsi.togregorian()
        end_gregorian = end_date_shamsi.togregorian()
        
        period, created = Period.objects.get_or_create(
            project=project2,
            year=year,
            month_number=month_num,
            defaults={
                'label': label,
                'month_name': month_name,
                'weight': 1.0,
                'start_date_shamsi': start_date_shamsi,
                'end_date_shamsi': end_date_shamsi,
                'start_date_gregorian': start_gregorian,
                'end_date_gregorian': end_gregorian,
            }
        )
        periods_project2.append(period)
        if created:
            print(f"✅ دوره ایجاد شد: {period.label}")
    
    # ایجاد دوره‌های سال 1406
    for month_num in range(1, 13):
        year = 1406
        month_name = month_names[month_num - 1]
        label = f'{month_name} {year}'
        
        # محاسبه تعداد روزهای ماه (برای اسفند باید بررسی کنیم که سال کبیسه است یا نه)
        if month_num == 12:
            # بررسی سال کبیسه
            try:
                # تلاش برای ایجاد روز 30 اسفند برای بررسی کبیسه بودن
                test_date = jdatetime.date(year, 12, 30)
                days_in_month = 30
            except ValueError:
                days_in_month = 29
        else:
            days_in_month = month_days[month_num]
        
        start_date_shamsi = jdatetime.date(year, month_num, 1)
        end_date_shamsi = jdatetime.date(year, month_num, days_in_month)
        
        # تبدیل به میلادی
        start_gregorian = start_date_shamsi.togregorian()
        end_gregorian = end_date_shamsi.togregorian()
        
        period, created = Period.objects.get_or_create(
            project=project2,
            year=year,
            month_number=month_num,
            defaults={
                'label': label,
                'month_name': month_name,
                'weight': 1.0,
                'start_date_shamsi': start_date_shamsi,
                'end_date_shamsi': end_date_shamsi,
                'start_date_gregorian': start_gregorian,
                'end_date_gregorian': end_gregorian,
            }
        )
        periods_project2.append(period)
        if created:
            print(f"✅ دوره ایجاد شد: {period.label}")
    
    # استفاده از اولین دوره برای expense2 (فروردین 1405)
    if periods_project2:
        period2 = periods_project2[0]
    else:
        # اگر دوره‌ای ایجاد نشد، یک دوره پیش‌فرض ایجاد می‌کنیم
        period2, _ = Period.objects.get_or_create(
            project=project2,
            year=1405,
            month_number=1,
            defaults={
                'label': 'فروردین 1405',
                'month_name': 'فروردین',
                'weight': 1.0,
                'start_date_shamsi': jdatetime.date(1405, 1, 1),
                'end_date_shamsi': jdatetime.date(1405, 1, 31),
                'start_date_gregorian': jdatetime.date(1405, 1, 1).togregorian(),
                'end_date_gregorian': jdatetime.date(1405, 1, 31).togregorian(),
            }
        )
    
    print(f"\n✅ مجموع {len(periods_project2)} دوره برای پروژه 2 ایجاد شد")
    
    # ایجاد هزینه برای پروژه 1
    expense1, e_created1 = Expense.objects.get_or_create(
        project=project1,
        period=period1,
        expense_type='other',
        defaults={
            'amount': 1000000,
            'description': 'هزینه تست پروژه 1'
        }
    )
    if e_created1:
        print(f"✅ هزینه 1 ایجاد شد: {expense1.amount:,} تومان (پروژه: {project1.name})")
    
    # حذف هزینه‌های قبلی پروژه 2 (اگر وجود دارند)
    Expense.objects.filter(project=project2).delete()
    
    # ایجاد هزینه‌های متنوع برای پروژه 2 از فروردین 1405 تا تیر 1406
    print("\n📊 ایجاد هزینه‌های متنوع برای پروژه 2 (از فروردین 1405 تا تیر 1406)...")
    
    expense_types = [
        ('project_manager', 'مدیر پروژه'),
        ('facilities_manager', 'سرپرست کارگاه'),
        ('procurement', 'کارپرداز'),
        ('warehouse', 'انباردار'),
        ('construction_contractor', 'پیمان ساختمان'),
        ('other', 'سایر'),
    ]
    
    # محاسبه دوره‌های لازم (فروردین 1405 تا تیر 1406)
    # periods_project2 شامل تمام دوره‌های 1405 و 1406 است
    # ما نیاز به دوره‌های 1 تا 12 سال 1405 و دوره‌های 1 تا 4 سال 1406 داریم
    
    target_periods = []
    for period in periods_project2:
        # فروردین 1405 (year=1405, month=1) تا تیر 1406 (year=1406, month=4)
        if (period.year == 1405) or (period.year == 1406 and period.month_number <= 4):
            target_periods.append(period)
    
    # مبالغ مختلف برای انواع هزینه‌ها
    base_amounts = {
        'project_manager': 5000000,
        'facilities_manager': 4000000,
        'procurement': 3000000,
        'warehouse': 2000000,
        'construction_contractor': 10000000,
        'other': 1500000,
    }
    
    expenses_project2_list = []
    
    # ایجاد هزینه برای هر دوره
    for period in target_periods:
        # ایجاد هزینه‌های مختلف برای هر دوره
        for expense_type_code, expense_type_name in expense_types:
            # تغییر مبلغ بر اساس دوره (برای تنوع)
            month_factor = period.month_number / 12.0
            amount = int(base_amounts[expense_type_code] * (1 + month_factor * 0.2))
            
            expense = Expense.objects.create(
                project=project2,
                period=period,
                expense_type=expense_type_code,
                amount=amount,
                description=f'{expense_type_name} - {period.label} - پروژه 2'
            )
            expenses_project2_list.append(expense)
            print(f"✅ هزینه ایجاد شد: {expense.get_expense_type_display()} - {period.label} - {expense.amount:,} تومان")
    
    # استفاده از اولین هزینه برای expense2 (برای سازگاری با کد قبلی)
    expense2 = expenses_project2_list[0] if expenses_project2_list else None
    
    print(f"\n✅ مجموع {len(expenses_project2_list)} هزینه برای پروژه 2 ایجاد شد")
    
    # حذف تراکنش‌های قبلی تست (اگر وجود دارند)
    Transaction.objects.filter(project__in=[project1, project2]).delete()
    
    # ایجاد تراکنش‌های تست برای سرمایه‌گذار 1 (پروژه 1)
    print("\n📊 ایجاد تراکنش‌های تست برای سرمایه‌گذار 1 (پروژه 1)...")
    
    # آورده 1 - پروژه 1
    tr1_date_shamsi1 = jdatetime.date(1402, 2, 15)
    tr1_gregorian1 = jdatetime.JalaliToGregorian(1402, 2, 15).getGregorianList()
    transaction1_1 = Transaction.objects.create(
        project=project1,
        investor=investor1,
        period=period1,
        date_shamsi=tr1_date_shamsi1,
        date_gregorian=date(tr1_gregorian1[0], tr1_gregorian1[1], tr1_gregorian1[2]),
        amount=50000000,
        transaction_type='principal_deposit',
        description='آورده اول سرمایه‌گذار 1 - پروژه 1'
    )
    print(f"✅ تراکنش 1-1 (آورده) ایجاد شد: {transaction1_1.amount:,} تومان")
    
    # آورده 2 - پروژه 1
    tr1_date_shamsi2 = jdatetime.date(1402, 3, 10)
    tr1_gregorian2 = jdatetime.JalaliToGregorian(1402, 3, 10).getGregorianList()
    transaction1_2 = Transaction.objects.create(
        project=project1,
        investor=investor1,
        period=period1,
        date_shamsi=tr1_date_shamsi2,
        date_gregorian=date(tr1_gregorian2[0], tr1_gregorian2[1], tr1_gregorian2[2]),
        amount=30000000,
        transaction_type='principal_deposit',
        description='آورده دوم سرمایه‌گذار 1 - پروژه 1'
    )
    print(f"✅ تراکنش 1-2 (آورده) ایجاد شد: {transaction1_2.amount:,} تومان")
    
    # برداشت 1 - پروژه 1
    tr1_date_shamsi3 = jdatetime.date(1402, 4, 5)
    tr1_gregorian3 = jdatetime.JalaliToGregorian(1402, 4, 5).getGregorianList()
    transaction1_3 = Transaction.objects.create(
        project=project1,
        investor=investor1,
        period=period1,
        date_shamsi=tr1_date_shamsi3,
        date_gregorian=date(tr1_gregorian3[0], tr1_gregorian3[1], tr1_gregorian3[2]),
        amount=10000000,
        transaction_type='principal_withdrawal',
        description='برداشت اول سرمایه‌گذار 1 - پروژه 1'
    )
    print(f"✅ تراکنش 1-3 (برداشت) ایجاد شد: {transaction1_3.amount:,} تومان")
    
    # برداشت 2 - پروژه 1
    tr1_date_shamsi4 = jdatetime.date(1402, 5, 20)
    tr1_gregorian4 = jdatetime.JalaliToGregorian(1402, 5, 20).getGregorianList()
    transaction1_4 = Transaction.objects.create(
        project=project1,
        investor=investor1,
        period=period1,
        date_shamsi=tr1_date_shamsi4,
        date_gregorian=date(tr1_gregorian4[0], tr1_gregorian4[1], tr1_gregorian4[2]),
        amount=5000000,
        transaction_type='principal_withdrawal',
        description='برداشت دوم سرمایه‌گذار 1 - پروژه 1'
    )
    print(f"✅ تراکنش 1-4 (برداشت) ایجاد شد: {transaction1_4.amount:,} تومان")
    
    # حذف تراکنش‌های قبلی پروژه 2 (اگر وجود دارند)
    Transaction.objects.filter(project=project2).delete()
    
    # ایجاد تراکنش‌های تست برای همه سرمایه‌گذاران پروژه 2 (از فروردین 1405 تا تیر 1406)
    print("\n📊 ایجاد تراکنش‌های تست برای سرمایه‌گذاران پروژه 2 (از فروردین 1405 تا تیر 1406)...")
    
    # دریافت دوره‌های لازم (فروردین 1405 تا تیر 1406)
    target_periods_for_transactions = []
    for period in periods_project2:
        if (period.year == 1405) or (period.year == 1406 and period.month_number <= 4):
            target_periods_for_transactions.append(period)
    
    transactions_project2 = []
    
    # برای هر سرمایه‌گذار، تراکنش‌هایی در دوره‌های مختلف ایجاد می‌کنیم
    for idx, investor in enumerate(investors_project2):
        investor_type = "مالک" if investor.participation_type == 'owner' else "سرمایه‌گذار"
        print(f"\n📊 ایجاد تراکنش‌ها برای {investor_type} {investor.first_name} {investor.last_name}...")
        
        # مبالغ پایه بر اساس نوع سرمایه‌گذار
        if investor.participation_type == 'owner':
            base_deposit = 100000000  # 100 میلیون برای مالکان
            base_loan = 50000000      # 50 میلیون برای آورده وام
            base_withdrawal = 20000000  # 20 میلیون برای برداشت
        else:
            base_deposit = 50000000   # 50 میلیون برای سرمایه‌گذاران
            base_loan = 25000000      # 25 میلیون برای آورده وام
            base_withdrawal = 10000000  # 10 میلیون برای برداشت
        
        # تعداد تراکنش‌ها برای هر سرمایه‌گذار
        # برای هر 4 دوره، یک مجموعه تراکنش ایجاد می‌کنیم
        transaction_count = 0
        
        for period_idx, period in enumerate(target_periods_for_transactions):
            # ایجاد تراکنش در هر دوره (با احتمال‌های مختلف)
            period_day = 5 + (period_idx % 20)  # روز بین 5 تا 24 ماه
            
            # آورده (در حدود 60% از دوره‌ها)
            if (period_idx + idx) % 3 == 0:
                tr_date_shamsi = jdatetime.date(period.year, period.month_number, period_day)
                tr_gregorian = tr_date_shamsi.togregorian()
                
                amount = int(base_deposit * (1 + (idx % 3) * 0.1))  # تنوع در مبالغ
                
                transaction = Transaction.objects.create(
                    project=project2,
                    investor=investor,
                    period=period,
                    date_shamsi=tr_date_shamsi,
                    date_gregorian=tr_gregorian,
                    amount=amount,
                    transaction_type='principal_deposit',
                    description=f'آورده - {investor.first_name} {investor.last_name} - {period.label}'
                )
                transactions_project2.append(transaction)
                transaction_count += 1
                print(f"  ✅ تراکنش (آورده) ایجاد شد: {amount:,} تومان - {period.label}")
            
            # آورده وام (در حدود 30% از دوره‌ها)
            if (period_idx + idx) % 5 == 1:
                tr_date_shamsi = jdatetime.date(period.year, period.month_number, min(period_day + 5, 28))
                tr_gregorian = tr_date_shamsi.togregorian()
                
                amount = int(base_loan * (1 + (idx % 2) * 0.15))
                
                transaction = Transaction.objects.create(
                    project=project2,
                    investor=investor,
                    period=period,
                    date_shamsi=tr_date_shamsi,
                    date_gregorian=tr_gregorian,
                    amount=amount,
                    transaction_type='loan_deposit',
                    description=f'آورده وام - {investor.first_name} {investor.last_name} - {period.label}'
                )
                transactions_project2.append(transaction)
                transaction_count += 1
                print(f"  ✅ تراکنش (آورده وام) ایجاد شد: {amount:,} تومان - {period.label}")
            
            # برداشت (در حدود 20% از دوره‌ها)
            if (period_idx + idx) % 7 == 2:
                tr_date_shamsi = jdatetime.date(period.year, period.month_number, min(period_day + 10, 28))
                tr_gregorian = tr_date_shamsi.togregorian()
                
                amount = int(base_withdrawal * (1 + (idx % 2) * 0.1))
                
                transaction = Transaction.objects.create(
                    project=project2,
                    investor=investor,
                    period=period,
                    date_shamsi=tr_date_shamsi,
                    date_gregorian=tr_gregorian,
                    amount=amount,
                    transaction_type='principal_withdrawal',
                    description=f'برداشت - {investor.first_name} {investor.last_name} - {period.label}'
                )
                transactions_project2.append(transaction)
                transaction_count += 1
                print(f"  ✅ تراکنش (برداشت) ایجاد شد: {amount:,} تومان - {period.label}")
        
        print(f"✅ مجموع {transaction_count} تراکنش برای {investor_type} {investor.first_name} {investor.last_name} ایجاد شد")
    
    transactions_project1 = [transaction1_1, transaction1_2, transaction1_3, transaction1_4]
    
    print(f"\n✅ مجموع {len(transactions_project2)} تراکنش برای همه سرمایه‌گذاران پروژه 2 ایجاد شد")
    
    # حذف واحدها و فروش/مرجوعی‌های قبلی تست (اگر وجود دارند)
    Unit.objects.filter(project__in=[project1, project2]).delete()
    Sale.objects.filter(project__in=[project1, project2]).delete()
    
    # ایجاد واحدهای تست برای پروژه 1
    print("\n📊 ایجاد واحدهای تست برای پروژه 1...")
    
    unit1_1 = Unit.objects.create(
        project=project1,
        name='واحد 101',
        area=150.50,
        price_per_meter=50000000,
        total_price=7525000000
    )
    print(f"✅ واحد 1-1 ایجاد شد: {unit1_1.name} - {unit1_1.area} متر - {unit1_1.total_price:,} تومان")
    
    unit1_2 = Unit.objects.create(
        project=project1,
        name='واحد 102',
        area=120.75,
        price_per_meter=48000000,
        total_price=5796000000
    )
    print(f"✅ واحد 1-2 ایجاد شد: {unit1_2.name} - {unit1_2.area} متر - {unit1_2.total_price:,} تومان")
    
    unit1_3 = Unit.objects.create(
        project=project1,
        name='واحد 103',
        area=180.25,
        price_per_meter=52000000,
        total_price=9373000000
    )
    print(f"✅ واحد 1-3 ایجاد شد: {unit1_3.name} - {unit1_3.area} متر - {unit1_3.total_price:,} تومان")
    
    # اختصاص واحدها به سرمایه‌گذار 1
    investor1.units.add(unit1_1, unit1_2)
    print(f"✅ واحدهای {unit1_1.name} و {unit1_2.name} به سرمایه‌گذار 1 اختصاص داده شد")
    
    # ایجاد واحدهای تست برای پروژه 2
    print("\n📊 ایجاد واحدهای تست برای پروژه 2...")
    
    unit2_1 = Unit.objects.create(
        project=project2,
        name='واحد 201',
        area=200.00,
        price_per_meter=60000000,
        total_price=12000000000
    )
    print(f"✅ واحد 2-1 ایجاد شد: {unit2_1.name} - {unit2_1.area} متر - {unit2_1.total_price:,} تومان")
    
    unit2_2 = Unit.objects.create(
        project=project2,
        name='واحد 202',
        area=165.50,
        price_per_meter=58000000,
        total_price=9599000000
    )
    print(f"✅ واحد 2-2 ایجاد شد: {unit2_2.name} - {unit2_2.area} متر - {unit2_2.total_price:,} تومان")
    
    unit2_3 = Unit.objects.create(
        project=project2,
        name='واحد 203',
        area=140.25,
        price_per_meter=55000000,
        total_price=7713750000
    )
    print(f"✅ واحد 2-3 ایجاد شد: {unit2_3.name} - {unit2_3.area} متر - {unit2_3.total_price:,} تومان")
    
    unit2_4 = Unit.objects.create(
        project=project2,
        name='واحد 204',
        area=220.75,
        price_per_meter=62000000,
        total_price=13686500000
    )
    print(f"✅ واحد 2-4 ایجاد شد: {unit2_4.name} - {unit2_4.area} متر - {unit2_4.total_price:,} تومان")
    
    # اختصاص واحدها به مالکان پروژه 2
    # مالک اول (علی رضایی) - واحد 201
    investors_project2[0].units.add(unit2_1)
    print(f"✅ واحد {unit2_1.name} به مالک {investors_project2[0].first_name} {investors_project2[0].last_name} اختصاص داده شد")
    
    # مالک دوم (محمد احمدی) - واحد 202
    investors_project2[1].units.add(unit2_2)
    print(f"✅ واحد {unit2_2.name} به مالک {investors_project2[1].first_name} {investors_project2[1].last_name} اختصاص داده شد")
    
    # مالک سوم (حسن کریمی) - واحد 203 و 204
    investors_project2[2].units.add(unit2_3, unit2_4)
    print(f"✅ واحدهای {unit2_3.name} و {unit2_4.name} به مالک {investors_project2[2].first_name} {investors_project2[2].last_name} اختصاص داده شد")
    
    units_project1 = [unit1_1, unit1_2, unit1_3]
    units_project2 = [unit2_1, unit2_2, unit2_3, unit2_4]
    
    # ایجاد فروش/مرجوعی‌های تست برای پروژه 1
    print("\n📊 ایجاد فروش/مرجوعی‌های تست برای پروژه 1...")
    
    sale1_1 = Sale.objects.create(
        project=project1,
        period=period1,
        amount=500000000,
        description='فروش واحد 101 - پروژه 1'
    )
    print(f"✅ فروش 1-1 ایجاد شد: {sale1_1.amount:,} تومان - {sale1_1.description}")
    
    sale1_2 = Sale.objects.create(
        project=project1,
        period=period1,
        amount=300000000,
        description='فروش واحد 102 - پروژه 1'
    )
    print(f"✅ فروش 1-2 ایجاد شد: {sale1_2.amount:,} تومان - {sale1_2.description}")
    
    sale1_3 = Sale.objects.create(
        project=project1,
        period=period1,
        amount=-50000000,
        description='مرجوعی واحد 103 - پروژه 1'
    )
    print(f"✅ مرجوعی 1-3 ایجاد شد: {sale1_3.amount:,} تومان - {sale1_3.description}")
    
    # ایجاد فروش/مرجوعی‌های تست برای پروژه 2
    print("\n📊 ایجاد فروش/مرجوعی‌های تست برای پروژه 2...")
    
    sale2_1 = Sale.objects.create(
        project=project2,
        period=period2,
        amount=800000000,
        description='فروش واحد 201 - پروژه 2'
    )
    print(f"✅ فروش 2-1 ایجاد شد: {sale2_1.amount:,} تومان - {sale2_1.description}")
    
    sale2_2 = Sale.objects.create(
        project=project2,
        period=period2,
        amount=600000000,
        description='فروش واحد 202 - پروژه 2'
    )
    print(f"✅ فروش 2-2 ایجاد شد: {sale2_2.amount:,} تومان - {sale2_2.description}")
    
    sale2_3 = Sale.objects.create(
        project=project2,
        period=period2,
        amount=450000000,
        description='فروش واحد 203 - پروژه 2'
    )
    print(f"✅ فروش 2-3 ایجاد شد: {sale2_3.amount:,} تومان - {sale2_3.description}")
    
    sale2_4 = Sale.objects.create(
        project=project2,
        period=period2,
        amount=-80000000,
        description='مرجوعی واحد 204 - پروژه 2'
    )
    print(f"✅ مرجوعی 2-4 ایجاد شد: {sale2_4.amount:,} تومان - {sale2_4.description}")
    
    sales_project1 = [sale1_1, sale1_2, sale1_3]
    sales_project2 = [sale2_1, sale2_2, sale2_3, sale2_4]
    
    return user, project1, project2, investor1, investor2, expense1, expense2, period1, period2, transactions_project1, transactions_project2, units_project1, units_project2, sales_project1, sales_project2, investors_project2


def create_request(user, project_id=None):
    """ایجاد request برای تست"""
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    
    # اضافه کردن session
    middleware = SessionMiddleware(lambda x: x)
    middleware.process_request(request)
    request.session.save()
    
    if project_id:
        request.session['current_project_id'] = project_id
    
    return request


def test_project_isolation():
    """تست جداسازی پروژه‌ها"""
    print("\n" + "="*80)
    print("🧪 شروع تست‌های جداسازی پروژه‌ها")
    print("="*80)
    
    # ایجاد داده‌های تست
    user, project1, project2, investor1, investor2, expense1, expense2, period1, period2, transactions_project1, transactions_project2, units_project1, units_project2, sales_project1, sales_project2, investors_project2 = create_test_data()
    
    # تست 1: بررسی جداسازی داده‌ها در دیتابیس
    print("\n" + "-"*80)
    print("📊 تست 1: بررسی جداسازی داده‌ها در دیتابیس")
    print("-"*80)
    
    investors_project1 = Investor.objects.filter(project=project1)
    investors_project2 = Investor.objects.filter(project=project2)
    
    expenses_project1 = Expense.objects.filter(project=project1)
    expenses_project2 = Expense.objects.filter(project=project2)
    
    print(f"\n✅ سرمایه‌گذاران پروژه 1: {investors_project1.count()} نفر")
    for inv in investors_project1:
        print(f"   - {inv.first_name} {inv.last_name} (ID: {inv.id})")
    
    print(f"\n✅ سرمایه‌گذاران پروژه 2: {investors_project2.count()} نفر")
    for inv in investors_project2:
        print(f"   - {inv.first_name} {inv.last_name} (ID: {inv.id})")
    
    print(f"\n✅ هزینه‌های پروژه 1: {expenses_project1.count()} مورد")
    for exp in expenses_project1:
        print(f"   - {exp.amount:,} تومان - {exp.description} (ID: {exp.id})")
    
    print(f"\n✅ هزینه‌های پروژه 2: {expenses_project2.count()} مورد")
    for exp in expenses_project2:
        print(f"   - {exp.amount:,} تومان - {exp.description} (ID: {exp.id})")
    
    # بررسی عدم تداخل
    assert investors_project1.count() == 1, "❌ پروژه 1 باید دقیقاً 1 سرمایه‌گذار داشته باشد"
    assert investors_project2.count() == 10, "❌ پروژه 2 باید دقیقاً 10 سرمایه‌گذار داشته باشد"
    
    # بررسی نوع سرمایه‌گذاران پروژه 2
    owners_count = investors_project2.filter(participation_type='owner').count()
    investors_count = investors_project2.filter(participation_type='investor').count()
    assert owners_count == 3, f"❌ پروژه 2 باید 3 مالک داشته باشد (دریافت شده: {owners_count})"
    assert investors_count == 7, f"❌ پروژه 2 باید 7 سرمایه‌گذار داشته باشد (دریافت شده: {investors_count})"
    
    # بررسی اختصاص واحدها به مالکان
    owners = list(investors_project2.filter(participation_type='owner'))
    total_units_assigned = sum(owner.units.count() for owner in owners)
    assert total_units_assigned == 4, f"❌ باید 4 واحد به مالکان اختصاص داده شود (دریافت شده: {total_units_assigned})"
    
    assert investors_project1.first().id != investors_project2.first().id, "❌ سرمایه‌گذاران باید متفاوت باشند"
    
    # توجه: ممکن است هزینه‌های اضافی از construction_contractor_percentage ایجاد شده باشند
    # بررسی اینکه هزینه‌های پروژه 2 با انواع مختلف ایجاد شده‌اند
    # باید حداقل 16 دوره × 6 نوع = 96 هزینه داشته باشیم (فروردین 1405 تا تیر 1406)
    assert expenses_project2.count() >= 96, f"❌ پروژه 2 باید حداقل 96 هزینه داشته باشد (دریافت شده: {expenses_project2.count()})"
    
    # بررسی انواع هزینه‌ها
    expense_types_count = expenses_project2.values('expense_type').distinct().count()
    assert expense_types_count == 6, f"❌ پروژه 2 باید 6 نوع هزینه مختلف داشته باشد (دریافت شده: {expense_types_count})"
    
    # بررسی هزینه‌های اصلی
    expense1_ids = [exp.id for exp in expenses_project1]
    expense2_ids = [exp.id for exp in expenses_project2]
    
    assert expense1.id in expense1_ids, "❌ هزینه 1 باید در لیست هزینه‌های پروژه 1 باشد"
    if expense2:
        assert expense2.id in expense2_ids, "❌ هزینه 2 باید در لیست هزینه‌های پروژه 2 باشد"
        assert expense2.id not in expense1_ids, "❌ هزینه 2 نباید در لیست هزینه‌های پروژه 1 باشد"
    assert expense1.id not in expense2_ids, "❌ هزینه 1 نباید در لیست هزینه‌های پروژه 2 باشد"
    assert expenses_project1.filter(id=expense1.id).exists(), "❌ هزینه 1 باید متعلق به پروژه 1 باشد"
    if expense2:
        assert expenses_project2.filter(id=expense2.id).exists(), "❌ هزینه 2 باید متعلق به پروژه 2 باشد"
    
    # بررسی تراکنش‌ها
    transactions_project1_db = Transaction.objects.filter(project=project1)
    transactions_project2_db = Transaction.objects.filter(project=project2)
    
    print(f"\n✅ تراکنش‌های پروژه 1: {transactions_project1_db.count()} مورد")
    for tr in transactions_project1_db:
        print(f"   - {tr.amount:,} تومان - {tr.get_transaction_type_display()} - {tr.description} (ID: {tr.id})")
    
    print(f"\n✅ تراکنش‌های پروژه 2: {transactions_project2_db.count()} مورد")
    for tr in transactions_project2_db:
        print(f"   - {tr.amount:,} تومان - {tr.get_transaction_type_display()} - {tr.description} (ID: {tr.id})")
    
    # بررسی عدم تداخل تراکنش‌ها
    transaction1_ids = [tr.id for tr in transactions_project1_db]
    transaction2_ids = [tr.id for tr in transactions_project2_db]
    
    assert len(transactions_project1_db) >= len(transactions_project1), f"❌ پروژه 1 باید حداقل {len(transactions_project1)} تراکنش داشته باشد"
    assert len(transactions_project2_db) >= len(transactions_project2), f"❌ پروژه 2 باید حداقل {len(transactions_project2)} تراکنش داشته باشد"
    
    # بررسی اینکه تراکنش‌های پروژه 1 در لیست تراکنش‌های پروژه 1 هستند
    for tr in transactions_project1:
        assert tr.id in transaction1_ids, f"❌ تراکنش {tr.id} باید در لیست تراکنش‌های پروژه 1 باشد"
        assert tr.id not in transaction2_ids, f"❌ تراکنش {tr.id} نباید در لیست تراکنش‌های پروژه 2 باشد"
    
    # بررسی اینکه تراکنش‌های پروژه 2 در لیست تراکنش‌های پروژه 2 هستند
    for tr in transactions_project2:
        assert tr.id in transaction2_ids, f"❌ تراکنش {tr.id} باید در لیست تراکنش‌های پروژه 2 باشد"
        assert tr.id not in transaction1_ids, f"❌ تراکنش {tr.id} نباید در لیست تراکنش‌های پروژه 1 باشد"
    
    # بررسی اینکه همه تراکنش‌ها متعلق به سرمایه‌گذار و پروژه درست هستند
    for tr in transactions_project1_db:
        assert tr.project.id == project1.id, f"❌ تراکنش {tr.id} باید متعلق به پروژه 1 باشد"
        assert tr.investor.id == investor1.id, f"❌ تراکنش {tr.id} باید متعلق به سرمایه‌گذار 1 باشد"
    
    # بررسی اینکه تراکنش‌های پروژه 2 متعلق به سرمایه‌گذاران پروژه 2 هستند
    investors_project2_ids = [inv.id for inv in investors_project2]
    for tr in transactions_project2_db:
        assert tr.project.id == project2.id, f"❌ تراکنش {tr.id} باید متعلق به پروژه 2 باشد"
        assert tr.investor.id in investors_project2_ids, f"❌ تراکنش {tr.id} باید متعلق به یکی از سرمایه‌گذاران پروژه 2 باشد"
    
    # بررسی انواع تراکنش‌ها
    transaction_types = transactions_project2_db.values('transaction_type').distinct()
    transaction_types_list = [t['transaction_type'] for t in transaction_types]
    assert 'principal_deposit' in transaction_types_list, "❌ باید تراکنش‌های آورده وجود داشته باشد"
    assert 'loan_deposit' in transaction_types_list, "❌ باید تراکنش‌های آورده وام وجود داشته باشد"
    assert 'principal_withdrawal' in transaction_types_list, "❌ باید تراکنش‌های برداشت وجود داشته باشد"
    
    # بررسی اینکه تراکنش‌ها در دوره‌های درست ایجاد شده‌اند (فروردین 1405 تا تیر 1406)
    for tr in transactions_project2_db:
        assert (tr.period.year == 1405) or (tr.period.year == 1406 and tr.period.month_number <= 4), \
            f"❌ تراکنش {tr.id} باید در دوره‌های فروردین 1405 تا تیر 1406 باشد"
    
    # بررسی واحدها
    units_project1_db = Unit.objects.filter(project=project1)
    units_project2_db = Unit.objects.filter(project=project2)
    
    print(f"\n✅ واحدهای پروژه 1: {units_project1_db.count()} مورد")
    for unit in units_project1_db:
        print(f"   - {unit.name} - {unit.area} متر - {unit.total_price:,} تومان (ID: {unit.id})")
    
    print(f"\n✅ واحدهای پروژه 2: {units_project2_db.count()} مورد")
    for unit in units_project2_db:
        print(f"   - {unit.name} - {unit.area} متر - {unit.total_price:,} تومان (ID: {unit.id})")
    
    # بررسی عدم تداخل واحدها
    unit1_ids = [unit.id for unit in units_project1_db]
    unit2_ids = [unit.id for unit in units_project2_db]
    
    assert len(units_project1_db) >= len(units_project1), f"❌ پروژه 1 باید حداقل {len(units_project1)} واحد داشته باشد"
    assert len(units_project2_db) >= len(units_project2), f"❌ پروژه 2 باید حداقل {len(units_project2)} واحد داشته باشد"
    
    # بررسی اینکه واحدهای پروژه 1 در لیست واحدهای پروژه 1 هستند
    for unit in units_project1:
        assert unit.id in unit1_ids, f"❌ واحد {unit.id} باید در لیست واحدهای پروژه 1 باشد"
        assert unit.id not in unit2_ids, f"❌ واحد {unit.id} نباید در لیست واحدهای پروژه 2 باشد"
    
    # بررسی اینکه واحدهای پروژه 2 در لیست واحدهای پروژه 2 هستند
    for unit in units_project2:
        assert unit.id in unit2_ids, f"❌ واحد {unit.id} باید در لیست واحدهای پروژه 2 باشد"
        assert unit.id not in unit1_ids, f"❌ واحد {unit.id} نباید در لیست واحدهای پروژه 1 باشد"
    
    # بررسی اینکه همه واحدها متعلق به پروژه درست هستند
    for unit in units_project1_db:
        assert unit.project.id == project1.id, f"❌ واحد {unit.id} باید متعلق به پروژه 1 باشد"
    
    for unit in units_project2_db:
        assert unit.project.id == project2.id, f"❌ واحد {unit.id} باید متعلق به پروژه 2 باشد"
    
    # بررسی فروش/مرجوعی‌ها
    sales_project1_db = Sale.objects.filter(project=project1)
    sales_project2_db = Sale.objects.filter(project=project2)
    
    print(f"\n✅ فروش/مرجوعی‌های پروژه 1: {sales_project1_db.count()} مورد")
    for sale in sales_project1_db:
        print(f"   - {sale.amount:,} تومان - {sale.description} (ID: {sale.id})")
    
    print(f"\n✅ فروش/مرجوعی‌های پروژه 2: {sales_project2_db.count()} مورد")
    for sale in sales_project2_db:
        print(f"   - {sale.amount:,} تومان - {sale.description} (ID: {sale.id})")
    
    # بررسی عدم تداخل فروش/مرجوعی‌ها
    sale1_ids = [sale.id for sale in sales_project1_db]
    sale2_ids = [sale.id for sale in sales_project2_db]
    
    assert len(sales_project1_db) >= len(sales_project1), f"❌ پروژه 1 باید حداقل {len(sales_project1)} فروش/مرجوعی داشته باشد"
    assert len(sales_project2_db) >= len(sales_project2), f"❌ پروژه 2 باید حداقل {len(sales_project2)} فروش/مرجوعی داشته باشد"
    
    # بررسی اینکه فروش/مرجوعی‌های پروژه 1 در لیست فروش/مرجوعی‌های پروژه 1 هستند
    for sale in sales_project1:
        assert sale.id in sale1_ids, f"❌ فروش/مرجوعی {sale.id} باید در لیست فروش/مرجوعی‌های پروژه 1 باشد"
        assert sale.id not in sale2_ids, f"❌ فروش/مرجوعی {sale.id} نباید در لیست فروش/مرجوعی‌های پروژه 2 باشد"
    
    # بررسی اینکه فروش/مرجوعی‌های پروژه 2 در لیست فروش/مرجوعی‌های پروژه 2 هستند
    for sale in sales_project2:
        assert sale.id in sale2_ids, f"❌ فروش/مرجوعی {sale.id} باید در لیست فروش/مرجوعی‌های پروژه 2 باشد"
        assert sale.id not in sale1_ids, f"❌ فروش/مرجوعی {sale.id} نباید در لیست فروش/مرجوعی‌های پروژه 1 باشد"
    
    # بررسی اینکه همه فروش/مرجوعی‌ها متعلق به پروژه درست هستند
    for sale in sales_project1_db:
        assert sale.project.id == project1.id, f"❌ فروش/مرجوعی {sale.id} باید متعلق به پروژه 1 باشد"
    
    for sale in sales_project2_db:
        assert sale.project.id == project2.id, f"❌ فروش/مرجوعی {sale.id} باید متعلق به پروژه 2 باشد"
    
    print("\n✅ تست 1: PASSED - داده‌ها در دیتابیس به درستی جدا هستند")
    
    # تست 2: بررسی ProjectManager.get_current_project
    print("\n" + "-"*80)
    print("📊 تست 2: بررسی ProjectManager.get_current_project")
    print("-"*80)
    
    # تست با پروژه 1
    request1 = create_request(user, project1.id)
    current_project1 = ProjectManager.get_current_project(request1)
    assert current_project1 is not None, "❌ پروژه جاری نباید None باشد"
    assert current_project1.id == project1.id, f"❌ پروژه جاری باید پروژه 1 باشد (دریافت شده: {current_project1.id})"
    print(f"✅ پروژه جاری (با session): {current_project1.name} (ID: {current_project1.id})")
    
    # تست با پروژه 2
    request2 = create_request(user, project2.id)
    current_project2 = ProjectManager.get_current_project(request2)
    assert current_project2 is not None, "❌ پروژه جاری نباید None باشد"
    assert current_project2.id == project2.id, f"❌ پروژه جاری باید پروژه 2 باشد (دریافت شده: {current_project2.id})"
    print(f"✅ پروژه جاری (با session): {current_project2.name} (ID: {current_project2.id})")
    
    print("\n✅ تست 2: PASSED - ProjectManager.get_current_project به درستی کار می‌کند")
    
    # تست 3: بررسی فیلتر ViewSetها
    print("\n" + "-"*80)
    print("📊 تست 3: بررسی فیلتر ViewSetها")
    print("-"*80)
    
    from construction.api import InvestorViewSet, ExpenseViewSet, TransactionViewSet, UnitViewSet, SaleViewSet
    
    # تست InvestorViewSet با پروژه 1
    request1 = create_request(user, project1.id)
    investor_viewset1 = InvestorViewSet()
    investor_viewset1.request = request1
    queryset1 = investor_viewset1.get_queryset()
    investors_from_api1 = list(queryset1.filter(project=project1))
    
    print(f"\n✅ سرمایه‌گذاران از API (پروژه 1): {len(investors_from_api1)} نفر")
    for inv in investors_from_api1:
        print(f"   - {inv.first_name} {inv.last_name} (پروژه: {inv.project.name})")
        assert inv.project.id == project1.id, f"❌ سرمایه‌گذار باید متعلق به پروژه 1 باشد"
    
    # تست InvestorViewSet با پروژه 2
    request2 = create_request(user, project2.id)
    investor_viewset2 = InvestorViewSet()
    investor_viewset2.request = request2
    queryset2 = investor_viewset2.get_queryset()
    investors_from_api2 = list(queryset2.filter(project=project2))
    
    print(f"\n✅ سرمایه‌گذاران از API (پروژه 2): {len(investors_from_api2)} نفر")
    for inv in investors_from_api2:
        print(f"   - {inv.first_name} {inv.last_name} (پروژه: {inv.project.name})")
        assert inv.project.id == project2.id, f"❌ سرمایه‌گذار باید متعلق به پروژه 2 باشد"
    
    # بررسی عدم تداخل
    assert len(investors_from_api1) == 1, "❌ API باید فقط 1 سرمایه‌گذار برای پروژه 1 برگرداند"
    assert len(investors_from_api2) == 10, "❌ API باید 10 سرمایه‌گذار برای پروژه 2 برگرداند"
    
    # بررسی نوع سرمایه‌گذاران پروژه 2 در API
    owners_from_api2 = [inv for inv in investors_from_api2 if inv.participation_type == 'owner']
    investors_from_api2_only = [inv for inv in investors_from_api2 if inv.participation_type == 'investor']
    assert len(owners_from_api2) == 3, f"❌ API باید 3 مالک برای پروژه 2 برگرداند (دریافت شده: {len(owners_from_api2)})"
    assert len(investors_from_api2_only) == 7, f"❌ API باید 7 سرمایه‌گذار برای پروژه 2 برگرداند (دریافت شده: {len(investors_from_api2_only)})"
    
    assert investors_from_api1[0].id != investors_from_api2[0].id, "❌ سرمایه‌گذاران باید متفاوت باشند"
    
    # تست ExpenseViewSet
    expense_viewset1 = ExpenseViewSet()
    expense_viewset1.request = request1
    expenses_queryset1 = expense_viewset1.get_queryset()
    expenses_from_api1 = list(expenses_queryset1)
    
    expense_viewset2 = ExpenseViewSet()
    expense_viewset2.request = request2
    expenses_queryset2 = expense_viewset2.get_queryset()
    expenses_from_api2 = list(expenses_queryset2)
    
    print(f"\n✅ هزینه‌ها از API (پروژه 1): {len(expenses_from_api1)} مورد")
    for exp in expenses_from_api1:
        print(f"   - {exp.amount:,} تومان - {exp.description} (پروژه: {exp.project.name})")
        assert exp.project.id == project1.id, f"❌ هزینه باید متعلق به پروژه 1 باشد"
    
    print(f"\n✅ هزینه‌ها از API (پروژه 2): {len(expenses_from_api2)} مورد")
    for exp in expenses_from_api2:
        print(f"   - {exp.amount:,} تومان - {exp.description} (پروژه: {exp.project.name})")
        assert exp.project.id == project2.id, f"❌ هزینه باید متعلق به پروژه 2 باشد"
    
    # توجه: ممکن است هزینه‌های اضافی از construction_contractor_percentage ایجاد شده باشند
    # بنابراین فقط بررسی می‌کنیم که هزینه‌های اصلی متفاوت هستند
    expense1_ids_from_api = [exp.id for exp in expenses_from_api1]
    expense2_ids_from_api = [exp.id for exp in expenses_from_api2]
    
    assert expense1.id in expense1_ids_from_api, "❌ هزینه 1 باید در لیست هزینه‌های API پروژه 1 باشد"
    assert expense2.id in expense2_ids_from_api, "❌ هزینه 2 باید در لیست هزینه‌های API پروژه 2 باشد"
    assert expense1.id not in expense2_ids_from_api, "❌ هزینه 1 نباید در لیست هزینه‌های API پروژه 2 باشد"
    assert expense2.id not in expense1_ids_from_api, "❌ هزینه 2 نباید در لیست هزینه‌های API پروژه 1 باشد"
    
    # بررسی اینکه همه هزینه‌های API متعلق به پروژه درست هستند
    for exp in expenses_from_api1:
        assert exp.project.id == project1.id, f"❌ همه هزینه‌های API پروژه 1 باید متعلق به پروژه 1 باشند"
    for exp in expenses_from_api2:
        assert exp.project.id == project2.id, f"❌ همه هزینه‌های API پروژه 2 باید متعلق به پروژه 2 باشند"
    
    # تست TransactionViewSet
    transaction_viewset1 = TransactionViewSet()
    transaction_viewset1.request = request1
    transactions_queryset1 = transaction_viewset1.get_queryset()
    transactions_from_api1 = list(transactions_queryset1)
    
    transaction_viewset2 = TransactionViewSet()
    transaction_viewset2.request = request2
    transactions_queryset2 = transaction_viewset2.get_queryset()
    transactions_from_api2 = list(transactions_queryset2)
    
    print(f"\n✅ تراکنش‌ها از API (پروژه 1): {len(transactions_from_api1)} مورد")
    for tr in transactions_from_api1:
        print(f"   - {tr.amount:,} تومان - {tr.get_transaction_type_display()} - {tr.description} (پروژه: {tr.project.name})")
        assert tr.project.id == project1.id, f"❌ تراکنش باید متعلق به پروژه 1 باشد"
    
    print(f"\n✅ تراکنش‌ها از API (پروژه 2): {len(transactions_from_api2)} مورد")
    for tr in transactions_from_api2:
        print(f"   - {tr.amount:,} تومان - {tr.get_transaction_type_display()} - {tr.description} (پروژه: {tr.project.name})")
        assert tr.project.id == project2.id, f"❌ تراکنش باید متعلق به پروژه 2 باشد"
    
    # بررسی عدم تداخل تراکنش‌ها
    transaction1_ids_from_api = [tr.id for tr in transactions_from_api1]
    transaction2_ids_from_api = [tr.id for tr in transactions_from_api2]
    
    assert len(transactions_from_api1) >= len(transactions_project1), f"❌ API باید حداقل {len(transactions_project1)} تراکنش برای پروژه 1 برگرداند"
    assert len(transactions_from_api2) >= len(transactions_project2), f"❌ API باید حداقل {len(transactions_project2)} تراکنش برای پروژه 2 برگرداند"
    
    # بررسی اینکه تراکنش‌های پروژه 1 در لیست تراکنش‌های API پروژه 1 هستند
    for tr in transactions_project1:
        assert tr.id in transaction1_ids_from_api, f"❌ تراکنش {tr.id} باید در لیست تراکنش‌های API پروژه 1 باشد"
        assert tr.id not in transaction2_ids_from_api, f"❌ تراکنش {tr.id} نباید در لیست تراکنش‌های API پروژه 2 باشد"
    
    # بررسی اینکه تراکنش‌های پروژه 2 در لیست تراکنش‌های API پروژه 2 هستند
    for tr in transactions_project2:
        assert tr.id in transaction2_ids_from_api, f"❌ تراکنش {tr.id} باید در لیست تراکنش‌های API پروژه 2 باشد"
        assert tr.id not in transaction1_ids_from_api, f"❌ تراکنش {tr.id} نباید در لیست تراکنش‌های API پروژه 1 باشد"
    
    # بررسی اینکه همه تراکنش‌های API متعلق به پروژه درست هستند
    for tr in transactions_from_api1:
        assert tr.project.id == project1.id, f"❌ همه تراکنش‌های API پروژه 1 باید متعلق به پروژه 1 باشند"
    for tr in transactions_from_api2:
        assert tr.project.id == project2.id, f"❌ همه تراکنش‌های API پروژه 2 باید متعلق به پروژه 2 باشند"
    
    # تست UnitViewSet
    unit_viewset1 = UnitViewSet()
    unit_viewset1.request = request1
    units_queryset1 = unit_viewset1.get_queryset()
    units_from_api1 = list(units_queryset1)
    
    unit_viewset2 = UnitViewSet()
    unit_viewset2.request = request2
    units_queryset2 = unit_viewset2.get_queryset()
    units_from_api2 = list(units_queryset2)
    
    print(f"\n✅ واحدها از API (پروژه 1): {len(units_from_api1)} مورد")
    for unit in units_from_api1:
        print(f"   - {unit.name} - {unit.area} متر - {unit.total_price:,} تومان (پروژه: {unit.project.name})")
        assert unit.project.id == project1.id, f"❌ واحد باید متعلق به پروژه 1 باشد"
    
    print(f"\n✅ واحدها از API (پروژه 2): {len(units_from_api2)} مورد")
    for unit in units_from_api2:
        print(f"   - {unit.name} - {unit.area} متر - {unit.total_price:,} تومان (پروژه: {unit.project.name})")
        assert unit.project.id == project2.id, f"❌ واحد باید متعلق به پروژه 2 باشد"
    
    # بررسی عدم تداخل واحدها
    unit1_ids_from_api = [unit.id for unit in units_from_api1]
    unit2_ids_from_api = [unit.id for unit in units_from_api2]
    
    assert len(units_from_api1) >= len(units_project1), f"❌ API باید حداقل {len(units_project1)} واحد برای پروژه 1 برگرداند"
    assert len(units_from_api2) >= len(units_project2), f"❌ API باید حداقل {len(units_project2)} واحد برای پروژه 2 برگرداند"
    
    # بررسی اینکه واحدهای پروژه 1 در لیست واحدهای API پروژه 1 هستند
    for unit in units_project1:
        assert unit.id in unit1_ids_from_api, f"❌ واحد {unit.id} باید در لیست واحدهای API پروژه 1 باشد"
        assert unit.id not in unit2_ids_from_api, f"❌ واحد {unit.id} نباید در لیست واحدهای API پروژه 2 باشد"
    
    # بررسی اینکه واحدهای پروژه 2 در لیست واحدهای API پروژه 2 هستند
    for unit in units_project2:
        assert unit.id in unit2_ids_from_api, f"❌ واحد {unit.id} باید در لیست واحدهای API پروژه 2 باشد"
        assert unit.id not in unit1_ids_from_api, f"❌ واحد {unit.id} نباید در لیست واحدهای API پروژه 1 باشد"
    
    # بررسی اینکه همه واحدهای API متعلق به پروژه درست هستند
    for unit in units_from_api1:
        assert unit.project.id == project1.id, f"❌ همه واحدهای API پروژه 1 باید متعلق به پروژه 1 باشند"
    for unit in units_from_api2:
        assert unit.project.id == project2.id, f"❌ همه واحدهای API پروژه 2 باید متعلق به پروژه 2 باشند"
    
    # تست SaleViewSet
    sale_viewset1 = SaleViewSet()
    sale_viewset1.request = request1
    sales_queryset1 = sale_viewset1.get_queryset()
    sales_from_api1 = list(sales_queryset1)
    
    sale_viewset2 = SaleViewSet()
    sale_viewset2.request = request2
    sales_queryset2 = sale_viewset2.get_queryset()
    sales_from_api2 = list(sales_queryset2)
    
    print(f"\n✅ فروش/مرجوعی‌ها از API (پروژه 1): {len(sales_from_api1)} مورد")
    for sale in sales_from_api1:
        print(f"   - {sale.amount:,} تومان - {sale.description} (پروژه: {sale.project.name})")
        assert sale.project.id == project1.id, f"❌ فروش/مرجوعی باید متعلق به پروژه 1 باشد"
    
    print(f"\n✅ فروش/مرجوعی‌ها از API (پروژه 2): {len(sales_from_api2)} مورد")
    for sale in sales_from_api2:
        print(f"   - {sale.amount:,} تومان - {sale.description} (پروژه: {sale.project.name})")
        assert sale.project.id == project2.id, f"❌ فروش/مرجوعی باید متعلق به پروژه 2 باشد"
    
    # بررسی عدم تداخل فروش/مرجوعی‌ها
    sale1_ids_from_api = [sale.id for sale in sales_from_api1]
    sale2_ids_from_api = [sale.id for sale in sales_from_api2]
    
    assert len(sales_from_api1) >= len(sales_project1), f"❌ API باید حداقل {len(sales_project1)} فروش/مرجوعی برای پروژه 1 برگرداند"
    assert len(sales_from_api2) >= len(sales_project2), f"❌ API باید حداقل {len(sales_project2)} فروش/مرجوعی برای پروژه 2 برگرداند"
    
    # بررسی اینکه فروش/مرجوعی‌های پروژه 1 در لیست فروش/مرجوعی‌های API پروژه 1 هستند
    for sale in sales_project1:
        assert sale.id in sale1_ids_from_api, f"❌ فروش/مرجوعی {sale.id} باید در لیست فروش/مرجوعی‌های API پروژه 1 باشد"
        assert sale.id not in sale2_ids_from_api, f"❌ فروش/مرجوعی {sale.id} نباید در لیست فروش/مرجوعی‌های API پروژه 2 باشد"
    
    # بررسی اینکه فروش/مرجوعی‌های پروژه 2 در لیست فروش/مرجوعی‌های API پروژه 2 هستند
    for sale in sales_project2:
        assert sale.id in sale2_ids_from_api, f"❌ فروش/مرجوعی {sale.id} باید در لیست فروش/مرجوعی‌های API پروژه 2 باشد"
        assert sale.id not in sale1_ids_from_api, f"❌ فروش/مرجوعی {sale.id} نباید در لیست فروش/مرجوعی‌های API پروژه 1 باشد"
    
    # بررسی اینکه همه فروش/مرجوعی‌های API متعلق به پروژه درست هستند
    for sale in sales_from_api1:
        assert sale.project.id == project1.id, f"❌ همه فروش/مرجوعی‌های API پروژه 1 باید متعلق به پروژه 1 باشند"
    for sale in sales_from_api2:
        assert sale.project.id == project2.id, f"❌ همه فروش/مرجوعی‌های API پروژه 2 باید متعلق به پروژه 2 باشند"
    
    print("\n✅ تست 3: PASSED - ViewSetها به درستی فیلتر می‌کنند")
    
    # تست 4: بررسی تغییر پروژه
    print("\n" + "-"*80)
    print("📊 تست 4: بررسی تغییر پروژه")
    print("-"*80)
    
    request = create_request(user)
    
    # تنظیم پروژه 1
    ProjectManager.set_current_project(request, project1.id)
    current = ProjectManager.get_current_project(request)
    assert current.id == project1.id, "❌ پروژه باید به پروژه 1 تغییر کرده باشد"
    print(f"✅ پروژه به {current.name} تغییر کرد")
    
    # بررسی داده‌های پروژه 1
    investor_viewset = InvestorViewSet()
    investor_viewset.request = request
    investors = list(investor_viewset.get_queryset())
    assert len(investors) == 1 and investors[0].id == investor1.id, "❌ باید فقط سرمایه‌گذار پروژه 1 نمایش داده شود"
    print(f"   - {len(investors)} سرمایه‌گذار: {investors[0].first_name} {investors[0].last_name}")
    
    # بررسی تراکنش‌های پروژه 1
    transaction_viewset = TransactionViewSet()
    transaction_viewset.request = request
    transactions = list(transaction_viewset.get_queryset())
    assert len(transactions) >= len(transactions_project1), f"❌ باید حداقل {len(transactions_project1)} تراکنش برای پروژه 1 نمایش داده شود"
    for tr in transactions:
        assert tr.project.id == project1.id, f"❌ همه تراکنش‌ها باید متعلق به پروژه 1 باشند"
        assert tr.investor.id == investor1.id, f"❌ همه تراکنش‌ها باید متعلق به سرمایه‌گذار 1 باشند"
    print(f"   - {len(transactions)} تراکنش برای سرمایه‌گذار {investors[0].first_name} {investors[0].last_name}")
    
    # تنظیم پروژه 2
    ProjectManager.set_current_project(request, project2.id)
    current = ProjectManager.get_current_project(request)
    assert current.id == project2.id, "❌ پروژه باید به پروژه 2 تغییر کرده باشد"
    print(f"✅ پروژه به {current.name} تغییر کرد")
    
    # بررسی داده‌های پروژه 2
    investor_viewset = InvestorViewSet()
    investor_viewset.request = request
    investors = list(investor_viewset.get_queryset())
    assert len(investors) == 10, f"❌ باید 10 سرمایه‌گذار برای پروژه 2 نمایش داده شود (دریافت شده: {len(investors)})"
    
    # بررسی نوع سرمایه‌گذاران
    owners = [inv for inv in investors if inv.participation_type == 'owner']
    investors_only = [inv for inv in investors if inv.participation_type == 'investor']
    assert len(owners) == 3, f"❌ باید 3 مالک نمایش داده شود (دریافت شده: {len(owners)})"
    assert len(investors_only) == 7, f"❌ باید 7 سرمایه‌گذار نمایش داده شود (دریافت شده: {len(investors_only)})"
    
    print(f"   - {len(investors)} سرمایه‌گذار: {len(owners)} مالک، {len(investors_only)} سرمایه‌گذار")
    
    # بررسی تراکنش‌های پروژه 2
    transaction_viewset = TransactionViewSet()
    transaction_viewset.request = request
    transactions = list(transaction_viewset.get_queryset())
    assert len(transactions) >= len(transactions_project2), f"❌ باید حداقل {len(transactions_project2)} تراکنش برای پروژه 2 نمایش داده شود"
    
    # بررسی اینکه همه تراکنش‌ها متعلق به پروژه 2 و سرمایه‌گذاران پروژه 2 هستند
    investors_project2_ids = [inv.id for inv in investors_project2]
    for tr in transactions:
        assert tr.project.id == project2.id, f"❌ همه تراکنش‌ها باید متعلق به پروژه 2 باشند"
        assert tr.investor.id in investors_project2_ids, f"❌ همه تراکنش‌ها باید متعلق به یکی از سرمایه‌گذاران پروژه 2 باشند"
    
    # بررسی انواع تراکنش‌ها
    transaction_types_in_api = set(tr.transaction_type for tr in transactions)
    assert 'principal_deposit' in transaction_types_in_api, "❌ باید تراکنش‌های آورده در API وجود داشته باشد"
    assert 'loan_deposit' in transaction_types_in_api, "❌ باید تراکنش‌های آورده وام در API وجود داشته باشد"
    assert 'principal_withdrawal' in transaction_types_in_api, "❌ باید تراکنش‌های برداشت در API وجود داشته باشد"
    
    print(f"   - {len(transactions)} تراکنش برای {len(investors)} سرمایه‌گذار")
    
    print("\n✅ تست 4: PASSED - تغییر پروژه به درستی کار می‌کند")
    
    # خلاصه نتایج
    print("\n" + "="*80)
    print("✅ خلاصه نتایج تست‌ها")
    print("="*80)
    print("✅ همه تست‌ها PASSED شدند!")
    print("\n📌 نتیجه:")
    print("   1. ✅ داده‌ها در دیتابیس به درستی جدا هستند")
    print("   2. ✅ ProjectManager.get_current_project به درستی کار می‌کند")
    print("   3. ✅ ViewSetها به درستی فیلتر می‌کنند")
    print("   4. ✅ تغییر پروژه به درستی کار می‌کند")
    print("\n🎉 ساختار چند پروژه‌ای به درستی فعال شده است!")
    print("="*80 + "\n")


if __name__ == '__main__':
    try:
        test_project_isolation()
    except AssertionError as e:
        print(f"\n❌ خطا در تست: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

