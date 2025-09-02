"""
تست‌های API برای Transaction
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, datetime
from jdatetime import datetime as jdatetime

from construction.models import Transaction, Investor, Project, Period
from construction.serializers import TransactionSerializer


class TransactionAPITestCase(APITestCase):
    """تست‌های API برای Transaction"""
    
    def setUp(self):
        """تنظیمات اولیه برای تست‌ها"""
        # ایجاد کاربر برای تست
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # ایجاد داده‌های تست
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
    
    def test_transaction_serializer_validation(self):
        """تست اعتبارسنجی serializer"""
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '10000',
            'date_shamsi': '1404-06-01',
            'description': 'تست تراکنش'
        }
        
        serializer = TransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
    
    def test_transaction_creation_with_persian_digits(self):
        """تست ایجاد تراکنش با اعداد فارسی"""
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '۱۰۰۰۰',  # اعداد فارسی
            'date_shamsi': '۱۴۰۴-۰۶-۰۱',  # اعداد فارسی
            'description': 'تست با اعداد فارسی'
        }
        
        serializer = TransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
        
        transaction = serializer.save()
        self.assertEqual(transaction.amount, 10000)
        self.assertEqual(transaction.date_shamsi, date(1404, 6, 1))
        self.assertIsNotNone(transaction.date_gregorian)
        self.assertGreater(transaction.day_remaining, 0)
        self.assertGreater(transaction.day_from_start, 0)
    
    def test_transaction_date_conversion(self):
        """تست تبدیل تاریخ شمسی به میلادی"""
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '50000',
            'date_shamsi': '1404-06-01',
            'description': 'تست تبدیل تاریخ'
        }
        
        serializer = TransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        transaction = serializer.save()
        
        # بررسی تبدیل تاریخ
        expected_gregorian = jdatetime.strptime('1404-06-01', '%Y-%m-%d').togregorian().date()
        self.assertEqual(transaction.date_gregorian, expected_gregorian)
    
    def test_transaction_day_calculations(self):
        """تست محاسبه روز مانده و روز از شروع"""
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '25000',
            'date_shamsi': '1404-06-01',
            'description': 'تست محاسبه روزها'
        }
        
        serializer = TransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        transaction = serializer.save()
        
        # بررسی محاسبه روزها
        self.assertIsNotNone(transaction.day_remaining)
        self.assertIsNotNone(transaction.day_from_start)
        self.assertGreater(transaction.day_remaining, 0)
        self.assertGreater(transaction.day_from_start, 0)
    
    def test_transaction_api_endpoint(self):
        """تست endpoint API"""
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '15000',
            'date_shamsi': '1404-06-01',
            'description': 'تست API endpoint'
        }
        
        url = reverse('transaction-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['amount'], '15000.00')
    
    def test_transaction_validation_errors(self):
        """تست خطاهای اعتبارسنجی"""
        # تست داده‌های نامعتبر
        invalid_data = {
            'investor_id': 999,  # investor وجود ندارد
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'invalid_type',  # نوع نامعتبر
            'amount': '-1000',  # مبلغ منفی
            'date_shamsi': 'invalid_date',  # تاریخ نامعتبر
        }
        
        serializer = TransactionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        # بررسی اینکه حداقل یکی از خطاها وجود دارد
        self.assertTrue(len(serializer.errors) > 0)
    
    def test_transaction_statistics_endpoint(self):
        """تست endpoint آمار تراکنش‌ها"""
        # ایجاد چند تراکنش تست
        Transaction.objects.create(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi=date(1404, 6, 1),
            date_gregorian=date(2025, 8, 23),
            amount=10000,
            transaction_type='principal_deposit',
            description='واریز اول'
        )
        
        Transaction.objects.create(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi=date(1404, 6, 2),
            date_gregorian=date(2025, 8, 24),
            amount=5000,
            transaction_type='profit_accrual',
            description='سود اول'
        )
        
        url = reverse('transaction-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_transactions', response.data)
        self.assertIn('total_deposits', response.data)
        self.assertIn('total_profits', response.data)
        self.assertEqual(response.data['total_transactions'], 2)
        self.assertEqual(response.data['total_deposits'], 10000.0)
        self.assertEqual(response.data['total_profits'], 5000.0)


class TransactionModelTestCase(TestCase):
    """تست‌های مدل Transaction"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.investor = Investor.objects.create(
            first_name='علی',
            last_name='احمدی',
            phone='09123456788',
            email='ali@test.com'
        )
        
        self.project = Project.objects.create(
            name='پروژه مدل تست',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        self.period = Period.objects.create(
            project=self.project,
            label='دوره مدل تست',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
    
    def test_transaction_model_save_method(self):
        """تست متد save مدل Transaction"""
        transaction = Transaction(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi='1404-06-01',
            amount=30000,
            transaction_type='principal_deposit',
            description='تست متد save'
        )
        
        # قبل از save، فیلدهای محاسبه شده None هستند
        self.assertIsNone(transaction.date_gregorian)
        self.assertEqual(transaction.day_remaining, 0)
        self.assertEqual(transaction.day_from_start, 0)
        
        transaction.save()
        
        # بعد از save، فیلدها محاسبه شده‌اند
        self.assertIsNotNone(transaction.date_gregorian)
        self.assertGreater(transaction.day_remaining, 0)
        self.assertGreater(transaction.day_from_start, 0)
    
    def test_transaction_str_method(self):
        """تست متد __str__ مدل Transaction"""
        transaction = Transaction.objects.create(
            investor=self.investor,
            project=self.project,
            period=self.period,
            date_shamsi=date(1404, 6, 1),
            date_gregorian=date(2025, 8, 23),
            amount=20000,
            transaction_type='principal_deposit',
            description='تست str'
        )
        
        str_repr = str(transaction)
        self.assertIn('علی احمدی', str_repr)
        self.assertIn('20000', str_repr)
        self.assertIn('آورده', str_repr)  # متن صحیح برای principal_deposit


@pytest.mark.django_db
class TransactionIntegrationTestCase(APITestCase):
    """تست‌های یکپارچگی Transaction"""
    
    def test_full_transaction_workflow(self):
        """تست کامل workflow تراکنش"""
        # 1. ایجاد داده‌های اولیه
        investor = Investor.objects.create(
            first_name='محمد',
            last_name='رضایی',
            phone='09123456787',
            email='mohammad@test.com'
        )
        
        project = Project.objects.create(
            name='پروژه یکپارچگی',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
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
        
        # 2. ایجاد تراکنش از طریق API
        data = {
            'investor_id': investor.id,
            'project_id': project.id,
            'period_id': period.id,
            'transaction_type': 'principal_deposit',
            'amount': '۱۰۰۰۰۰',  # اعداد فارسی
            'date_shamsi': '۱۴۰۴-۰۶-۰۱',  # اعداد فارسی
            'description': 'تست یکپارچگی کامل'
        }
        
        url = reverse('transaction-list')
        response = self.client.post(url, data, format='json')
        
        # 3. بررسی موفقیت ایجاد
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_id = response.data['id']
        
        # 4. بررسی داده‌های ذخیره شده
        transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(transaction.amount, 100000)
        self.assertEqual(transaction.date_shamsi, date(1404, 6, 1))
        self.assertIsNotNone(transaction.date_gregorian)
        self.assertGreater(transaction.day_remaining, 0)
        self.assertGreater(transaction.day_from_start, 0)
        
        # 5. تست دریافت تراکنش
        detail_url = reverse('transaction-detail', args=[transaction_id])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        
        # 6. تست آپدیت تراکنش
        update_data = {
            'investor_id': investor.id,
            'project_id': project.id,
            'period_id': period.id,
            'transaction_type': 'profit_accrual',
            'amount': '50000',
            'date_shamsi': '1404-06-02',
            'description': 'تست آپدیت'
        }
        
        update_response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 7. بررسی آپدیت
        updated_transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(updated_transaction.transaction_type, 'profit_accrual')
        self.assertEqual(updated_transaction.amount, 50000)
        
        # 8. تست حذف تراکنش
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 9. بررسی حذف
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=transaction_id)
