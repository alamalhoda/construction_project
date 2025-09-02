"""
تست‌های Model ها
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, datetime
from jdatetime import datetime as jdatetime

from construction.models import Transaction, Investor, Project, Period


class TransactionModelTestCase(TestCase):
    """تست‌های مدل Transaction"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.investor = Investor.objects.create(
            first_name='احمد',
            last_name='محمدی',
            phone='09123456789',
            email='ahmad@test.com'
        )
        
        self.project = Project.objects.create(
            name='پروژه تست',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        self.period = Period.objects.create(
            project=self.project,
            label='دوره تست',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
    
    def test_transaction_creation(self):
        """تست ایجاد تراکنش"""
        transaction = Transaction.objects.create(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi=date(1404, 6, 1),
            date_gregorian=date(2025, 8, 23),
            amount=10000,
            transaction_type='principal_deposit',
            description='تست ایجاد'
        )
        
        self.assertEqual(transaction.investor, self.investor)
        self.assertEqual(transaction.project, self.project)
        self.assertEqual(transaction.period, self.period)
        self.assertEqual(transaction.amount, 10000)
        self.assertEqual(transaction.transaction_type, 'principal_deposit')
        self.assertEqual(transaction.description, 'تست ایجاد')
        self.assertIsNotNone(transaction.created_at)
    
    def test_transaction_save_method_date_conversion(self):
        """تست تبدیل تاریخ در متد save"""
        transaction = Transaction(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi='1404-06-01',
            amount=20000,
            transaction_type='principal_deposit',
            description='تست تبدیل تاریخ'
        )
        
        # قبل از save
        self.assertIsNone(transaction.date_gregorian)
        
        transaction.save()
        
        # بعد از save
        self.assertIsNotNone(transaction.date_gregorian)
        expected_gregorian = jdatetime.strptime('1404-06-01', '%Y-%m-%d').togregorian().date()
        self.assertEqual(transaction.date_gregorian, expected_gregorian)
    
    def test_transaction_save_method_day_calculations(self):
        """تست محاسبه روزها در متد save"""
        transaction = Transaction(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi='1404-06-01',
            amount=30000,
            transaction_type='principal_deposit',
            description='تست محاسبه روزها'
        )
        
        # قبل از save
        self.assertEqual(transaction.day_remaining, 0)
        self.assertEqual(transaction.day_from_start, 0)
        
        transaction.save()
        
        # بعد از save
        self.assertGreater(transaction.day_remaining, 0)
        self.assertGreater(transaction.day_from_start, 0)
        
        # بررسی محاسبه دقیق
        expected_gregorian = jdatetime.strptime('1404-06-01', '%Y-%m-%d').togregorian().date()
        # تبدیل تاریخ‌های پروژه به date اگر string هستند
        end_date = self.project.end_date_gregorian
        if isinstance(end_date, str):
            from datetime import datetime
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        start_date = self.project.start_date_gregorian
        if isinstance(start_date, str):
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        expected_day_remaining = (end_date - expected_gregorian).days
        expected_day_from_start = (expected_gregorian - start_date).days
        
        self.assertEqual(transaction.day_remaining, expected_day_remaining)
        self.assertEqual(transaction.day_from_start, expected_day_from_start)
    
    def test_transaction_str_method(self):
        """تست متد __str__"""
        transaction = Transaction.objects.create(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi=date(1404, 6, 1),
            date_gregorian=date(2025, 8, 23),
            amount=40000,
            transaction_type='principal_deposit',
            description='تست str'
        )
        
        str_repr = str(transaction)
        self.assertIn('احمد محمدی', str_repr)
        self.assertIn('40000', str_repr)
        self.assertIn('آورده', str_repr)  # متن صحیح برای principal_deposit
        self.assertIn('دوره تست', str_repr)
        self.assertIn('1404-06-01', str_repr)
        self.assertIn('2025-08-23', str_repr)
    
    def test_transaction_choices(self):
        """تست انتخاب‌های transaction_type"""
        # تست انتخاب‌های معتبر
        valid_types = ['principal_deposit', 'principal_withdrawal', 'profit_accrual']
        
        for transaction_type in valid_types:
            transaction = Transaction.objects.create(
                investor=self.investor,
                project=self.project,
                period=self.period,
                date_shamsi=date(1404, 6, 1),
                date_gregorian=date(2025, 8, 23),
                amount=5000,
                transaction_type=transaction_type,
                description=f'تست {transaction_type}'
            )
            self.assertEqual(transaction.transaction_type, transaction_type)
    
    def test_transaction_default_values(self):
        """تست مقادیر پیش‌فرض"""
        transaction = Transaction(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi='1404-06-01',
            amount=6000,
            transaction_type='principal_deposit'
            # description خالی است
        )
        
        self.assertEqual(transaction.day_remaining, 0)
        self.assertEqual(transaction.day_from_start, 0)
        self.assertEqual(transaction.description, '')
    
    def test_transaction_foreign_key_relationships(self):
        """تست روابط foreign key"""
        transaction = Transaction.objects.create(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi=date(1404, 6, 1),
            date_gregorian=date(2025, 8, 23),
            amount=7000,
            transaction_type='principal_deposit',
            description='تست روابط'
        )
        
        # تست دسترسی به related objects
        self.assertEqual(transaction.investor.first_name, 'احمد')
        self.assertEqual(transaction.project.name, 'پروژه تست')
        self.assertEqual(transaction.period.label, 'دوره تست')
        
        # تست cascade delete
        investor_id = self.investor.id
        self.investor.delete()
        
        # بررسی اینکه تراکنش حذف شده باشد
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=transaction.id)


class InvestorModelTestCase(TestCase):
    """تست‌های مدل Investor"""
    
    def test_investor_creation(self):
        """تست ایجاد investor"""
        investor = Investor.objects.create(
            first_name='علی',
            last_name='احمدی',
            phone='09123456788',
            email='ali@test.com'
        )
        
        self.assertEqual(investor.first_name, 'علی')
        self.assertEqual(investor.last_name, 'احمدی')
        self.assertEqual(investor.phone, '09123456788')
        self.assertEqual(investor.email, 'ali@test.com')
        self.assertIsNotNone(investor.created_at)
    
    def test_investor_str_method(self):
        """تست متد __str__"""
        investor = Investor.objects.create(
            first_name='محمد',
            last_name='رضایی',
            phone='09123456787',
            email='mohammad@test.com'
        )
        
        str_repr = str(investor)
        self.assertIn('محمد', str_repr)
        self.assertIn('رضایی', str_repr)
    
    def test_investor_email_validation(self):
        """تست اعتبارسنجی email"""
        # تست email معتبر
        investor = Investor.objects.create(
            first_name='تست',
            last_name='ایمیل',
            phone='09123456786',
            email='test@example.com'
        )
        self.assertEqual(investor.email, 'test@example.com')
    
    def test_investor_phone_validation(self):
        """تست اعتبارسنجی phone"""
        investor = Investor.objects.create(
            first_name='تست',
            last_name='تلفن',
            phone='09123456785',
            email='phone@test.com'
        )
        self.assertEqual(investor.phone, '09123456785')


class ProjectModelTestCase(TestCase):
    """تست‌های مدل Project"""
    
    def test_project_creation(self):
        """تست ایجاد project"""
        project = Project.objects.create(
            name='پروژه جدید',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        self.assertEqual(project.name, 'پروژه جدید')
        self.assertEqual(project.start_date_shamsi, '1400-01-01')
        self.assertEqual(project.end_date_shamsi, '1405-12-29')
        self.assertEqual(project.start_date_gregorian, '2021-03-21')
        self.assertEqual(project.end_date_gregorian, '2027-03-20')
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)
    
    def test_project_str_method(self):
        """تست متد __str__"""
        project = Project.objects.create(
            name='پروژه تست str',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        str_repr = str(project)
        self.assertIn('پروژه تست str', str_repr)
    
    def test_project_date_relationships(self):
        """تست روابط تاریخ‌ها"""
        project = Project.objects.create(
            name='پروژه تاریخ',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        # بررسی اینکه تاریخ شروع قبل از تاریخ پایان باشد
        self.assertLess(project.start_date_gregorian, project.end_date_gregorian)
        self.assertLess(project.start_date_shamsi, project.end_date_shamsi)


class PeriodModelTestCase(TestCase):
    """تست‌های مدل Period"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.project = Project.objects.create(
            name='پروژه تست Period',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
    
    def test_period_creation(self):
        """تست ایجاد period"""
        period = Period.objects.create(
            project=self.project,
            label='دوره جدید',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
        
        self.assertEqual(period.label, 'دوره جدید')
        self.assertEqual(period.year, 1404)
        self.assertEqual(period.month_number, 6)
        self.assertEqual(period.month_name, 'شهریور')
        self.assertEqual(period.weight, 1)
        self.assertEqual(period.start_date_shamsi, '1404-06-01')
        self.assertEqual(period.end_date_shamsi, '1404-06-30')
        self.assertEqual(period.start_date_gregorian, '2025-08-23')
        self.assertEqual(period.end_date_gregorian, '2025-09-21')
    
    def test_period_str_method(self):
        """تست متد __str__"""
        period = Period.objects.create(
            project=self.project,
            label='دوره تست str',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
        
        str_repr = str(period)
        self.assertIn('دوره تست str', str_repr)
    
    def test_period_month_validation(self):
        """تست اعتبارسنجی ماه"""
        # تست ماه معتبر
        period = Period.objects.create(
            project=self.project,
            label='دوره ماه معتبر',
            year=1404,
            month_number=12,  # ماه معتبر
            month_name='اسفند',
            weight=1,
            start_date_shamsi='1404-12-01',
            end_date_shamsi='1404-12-29',
            start_date_gregorian='2026-02-20',
            end_date_gregorian='2026-03-20'
        )
        
        self.assertEqual(period.month_number, 12)
        self.assertEqual(period.month_name, 'اسفند')


@pytest.mark.django_db
class ModelIntegrationTestCase(TestCase):
    """تست‌های یکپارچگی مدل‌ها"""
    
    def test_full_transaction_workflow(self):
        """تست کامل workflow با مدل‌ها"""
        # 1. ایجاد investor
        investor = Investor.objects.create(
            first_name='تست',
            last_name='یکپارچگی',
            phone='09123456784',
            email='integration@test.com'
        )
        
        # 2. ایجاد project
        project = Project.objects.create(
            name='پروژه یکپارچگی',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        # 3. ایجاد period
        period = Period.objects.create(
            project=project,
            label='دوره یکپارچگی',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
        
        # 4. ایجاد transaction
        transaction = Transaction.objects.create(
            investor=investor,
            project=project,
            period=period,
            date_shamsi='1404-06-01',
            amount=100000,
            transaction_type='principal_deposit',
            description='تست یکپارچگی کامل'
        )
        
        # 5. بررسی روابط
        self.assertEqual(transaction.investor, investor)
        self.assertEqual(transaction.project, project)
        self.assertEqual(transaction.period, period)
        
        # 6. بررسی محاسبات خودکار
        self.assertIsNotNone(transaction.date_gregorian)
        self.assertGreater(transaction.day_remaining, 0)
        self.assertGreater(transaction.day_from_start, 0)
        
        # 7. تست cascade delete
        project_id = project.id
        project.delete()
        
        # بررسی اینکه transaction حذف شده باشد
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=transaction.id)
        
        # بررسی اینکه investor باقی مانده باشد
        self.assertTrue(Investor.objects.filter(id=investor.id).exists())
        # period باید حذف شده باشد چون project حذف شده
        self.assertFalse(Period.objects.filter(id=period.id).exists())
