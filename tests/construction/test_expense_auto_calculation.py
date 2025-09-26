from django.test import TestCase
from django_jalali.db import models as jmodels
from decimal import Decimal
from construction.models import Project, Period, Expense
import jdatetime


class ExpenseAutoCalculationTestCase(TestCase):
    """تست محاسبه خودکار هزینه پیمان ساختمان"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        # ایجاد پروژه تست
        self.project = Project.objects.create(
            name="پروژه تست",
            start_date_shamsi=jdatetime.date(1403, 1, 1),
            end_date_shamsi=jdatetime.date(1403, 12, 29),
            start_date_gregorian=jdatetime.date(1403, 1, 1).togregorian(),
            end_date_gregorian=jdatetime.date(1403, 12, 29).togregorian(),
            is_active=True
        )
        
        # ایجاد دوره تست
        self.period = Period.objects.create(
            project=self.project,
            label="فروردین 1403",
            year=1403,
            month_number=1,
            month_name="فروردین",
            weight=1,
            start_date_shamsi=jdatetime.date(1403, 1, 1),
            end_date_shamsi=jdatetime.date(1403, 1, 31),
            start_date_gregorian=jdatetime.date(1403, 1, 1).togregorian(),
            end_date_gregorian=jdatetime.date(1403, 1, 31).togregorian()
        )
    
    def test_construction_contractor_calculation(self):
        """تست محاسبه هزینه پیمان ساختمان"""
        # ایجاد هزینه‌های مختلف برای دوره
        Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='project_manager',
            amount=Decimal('1000000'),
            description='حقوق مدیر پروژه'
        )
        
        Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='facilities_manager',
            amount=Decimal('800000'),
            description='حقوق سرپرست کارگاه'
        )
        
        Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='procurement',
            amount=Decimal('600000'),
            description='حقوق کارپرداز'
        )
        
        # مجموع سایر هزینه‌ها: 1,000,000 + 800,000 + 600,000 = 2,400,000
        # 10% مجموع: 240,000
        
        # محاسبه هزینه پیمان ساختمان
        temp_expense = Expense(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        )
        calculated_amount = temp_expense.calculate_construction_contractor_amount()
        
        self.assertEqual(calculated_amount, Decimal('240000.00'))
    
    def test_automatic_construction_contractor_creation(self):
        """تست ایجاد خودکار هزینه پیمان ساختمان"""
        # ایجاد هزینه‌های مختلف
        Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='project_manager',
            amount=Decimal('1000000'),
            description='حقوق مدیر پروژه'
        )
        
        Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='warehouse',
            amount=Decimal('500000'),
            description='حقوق انباردار'
        )
        
        # محاسبه و ایجاد خودکار هزینه پیمان ساختمان
        Expense.update_construction_contractor_for_period(self.period, self.project)
        
        # بررسی وجود هزینه پیمان ساختمان
        construction_contractor_expense = Expense.objects.filter(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        ).first()
        
        self.assertIsNotNone(construction_contractor_expense)
        self.assertEqual(construction_contractor_expense.amount, Decimal('150000.00'))  # 10% of 1,500,000
        self.assertIn('محاسبه خودکار', construction_contractor_expense.description)
    
    def test_construction_contractor_update_on_expense_change(self):
        """تست به‌روزرسانی خودکار هنگام تغییر هزینه‌ها"""
        # ایجاد هزینه اولیه
        expense = Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='project_manager',
            amount=Decimal('1000000'),
            description='حقوق مدیر پروژه'
        )
        
        # محاسبه اولیه
        Expense.update_construction_contractor_for_period(self.period, self.project)
        
        # بررسی مبلغ اولیه (10% of 1,000,000 = 100,000)
        initial_contractor = Expense.objects.get(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        )
        self.assertEqual(initial_contractor.amount, Decimal('100000.00'))
        
        # تغییر مبلغ هزینه
        expense.amount = Decimal('2000000')
        expense.save()  # این باید signal را فعال کند
        
        # بررسی به‌روزرسانی خودکار (10% of 2,000,000 = 200,000)
        updated_contractor = Expense.objects.get(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        )
        self.assertEqual(updated_contractor.amount, Decimal('200000.00'))
    
    def test_construction_contractor_removal_on_expense_deletion(self):
        """تست حذف خودکار هنگام حذف هزینه‌ها"""
        # ایجاد هزینه‌ها
        expense1 = Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='project_manager',
            amount=Decimal('1000000'),
            description='حقوق مدیر پروژه'
        )
        
        Expense.objects.create(
            project=self.project,
            period=self.period,
            expense_type='facilities_manager',
            amount=Decimal('500000'),
            description='حقوق سرپرست کارگاه'
        )
        
        # محاسبه اولیه
        Expense.update_construction_contractor_for_period(self.period, self.project)
        
        # بررسی وجود هزینه پیمان ساختمان (10% of 1,500,000 = 150,000)
        contractor_before = Expense.objects.get(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        )
        self.assertEqual(contractor_before.amount, Decimal('150000.00'))
        
        # حذف یکی از هزینه‌ها
        expense1.delete()  # این باید signal را فعال کند
        
        # بررسی به‌روزرسانی خودکار (10% of 500,000 = 50,000)
        contractor_after = Expense.objects.get(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        )
        self.assertEqual(contractor_after.amount, Decimal('50000.00'))
    
    def test_no_construction_contractor_when_no_other_expenses(self):
        """تست عدم ایجاد هزینه پیمان ساختمان وقتی هیچ هزینه دیگری وجود ندارد"""
        # محاسبه بدون وجود هزینه‌های دیگر
        Expense.update_construction_contractor_for_period(self.period, self.project)
        
        # بررسی عدم وجود هزینه پیمان ساختمان
        contractor_exists = Expense.objects.filter(
            project=self.project,
            period=self.period,
            expense_type='construction_contractor'
        ).exists()
        
        self.assertFalse(contractor_exists)
