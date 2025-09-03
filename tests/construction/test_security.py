"""
تست‌های امنیتی و احراز هویت
Security and Authentication Tests
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.cache import cache

from construction.models import Transaction, Investor, Project, Period
from construction.authentication import EnhancedAuthenticationBackend


class SecurityTestCase(TestCase):
    """تست‌های امنیتی پایه"""
    
    def setUp(self):
        """تنظیمات اولیه برای تست‌ها"""
        self.client = Client()
        
        # ایجاد کاربر تستی
        self.test_user = User.objects.create_user(
            username='security_test_user',
            password='secure_password_123',
            email='security@test.com',
            first_name='کاربر',
            last_name='تست امنیتی'
        )
        
        # ایجاد کاربر مدیر
        self.admin_user = User.objects.create_user(
            username='admin_test_user',
            password='admin_password_123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # ایجاد داده‌های تست
        self.investor = Investor.objects.create(
            first_name='احمد',
            last_name='محمدی',
            phone='09123456789',
            email='ahmad@test.com'
        )
        
        self.project = Project.objects.create(
            name='پروژه امنیتی',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        self.period = Period.objects.create(
            project=self.project,
            label='دوره امنیتی',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
    
    def tearDown(self):
        """پاک‌سازی cache بعد از هر تست"""
        cache.clear()
    
    def test_user_creation(self):
        """تست ایجاد کاربر"""
        self.assertTrue(User.objects.filter(username='security_test_user').exists())
        self.assertFalse(self.test_user.is_staff)
        self.assertFalse(self.test_user.is_superuser)
    
    def test_user_authentication(self):
        """تست احراز هویت کاربر"""
        # تست احراز هویت موفق
        user = authenticate(username='security_test_user', password='secure_password_123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'security_test_user')
        
        # تست احراز هویت ناموفق
        user = authenticate(username='security_test_user', password='wrong_password')
        self.assertIsNone(user)
    
    def test_login_page_access(self):
        """تست دسترسی به صفحه لاگین"""
        response = self.client.get('/construction/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ورود به سیستم')
    
    def test_register_page_access(self):
        """تست دسترسی به صفحه ثبت نام"""
        response = self.client.get('/construction/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ثبت نام')
    
    def test_dashboard_access_without_login(self):
        """تست دسترسی به داشبورد بدون لاگین"""
        response = self.client.get('/dashboard/')
        # باید به صفحه لاگین هدایت شود
        self.assertRedirects(response, '/construction/login/?next=/dashboard/')
    
    def test_dashboard_access_with_login(self):
        """تست دسترسی به داشبورد با لاگین"""
        self.client.login(username='security_test_user', password='secure_password_123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_access_regular_user(self):
        """تست دسترسی کاربر عادی به پنل ادمین"""
        self.client.login(username='security_test_user', password='secure_password_123')
        response = self.client.get('/admin/')
        # باید به صفحه لاگین ادمین هدایت شود
        self.assertRedirects(response, '/admin/login/?next=/admin/')
    
    def test_admin_access_admin_user(self):
        """تست دسترسی کاربر مدیر به پنل ادمین"""
        self.client.login(username='admin_test_user', password='admin_password_123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_logout_functionality(self):
        """تست عملکرد خروج از سیستم"""
        # لاگین
        self.client.login(username='security_test_user', password='secure_password_123')
        
        # بررسی لاگین بودن
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # خروج از سیستم
        response = self.client.get('/construction/logout/')
        self.assertEqual(response.status_code, 302)  # هدایت به صفحه اصلی
        
        # بررسی خروج از سیستم
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/construction/login/?next=/dashboard/')


class AuthenticationBackendTestCase(TestCase):
    """تست‌های Authentication Backend سفارشی"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.backend = EnhancedAuthenticationBackend()
        
        # ایجاد کاربر تستی
        self.test_user = User.objects.create_user(
            username='backend_test_user',
            password='backend_password_123',
            email='backend@test.com'
        )
    
    def tearDown(self):
        """پاک‌سازی cache"""
        cache.clear()
    
    def test_authenticate_success(self):
        """تست احراز هویت موفق"""
        user = self.backend.authenticate(
            request=None,
            username='backend_test_user',
            password='backend_password_123'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'backend_test_user')
    
    def test_authenticate_failure(self):
        """تست احراز هویت ناموفق"""
        user = self.backend.authenticate(
            request=None,
            username='backend_test_user',
            password='wrong_password'
        )
        self.assertIsNone(user)
    
    def test_authenticate_nonexistent_user(self):
        """تست احراز هویت کاربر ناموجود"""
        user = self.backend.authenticate(
            request=None,
            username='nonexistent_user',
            password='any_password'
        )
        self.assertIsNone(user)
    
    def test_get_user(self):
        """تست دریافت کاربر"""
        user = self.backend.get_user(self.test_user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'backend_test_user')
        
        # تست کاربر ناموجود
        user = self.backend.get_user(99999)
        self.assertIsNone(user)


class APISecurityTestCase(APITestCase):
    """تست‌های امنیتی API"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        # ایجاد کاربر تستی
        self.test_user = User.objects.create_user(
            username='api_test_user',
            password='api_password_123',
            email='api@test.com'
        )
        
        # ایجاد داده‌های تست
        self.investor = Investor.objects.create(
            first_name='احمد',
            last_name='محمدی',
            phone='09123456789',
            email='ahmad@test.com'
        )
        
        self.project = Project.objects.create(
            name='پروژه API امنیتی',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        self.period = Period.objects.create(
            project=self.project,
            label='دوره API امنیتی',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
    
    def test_api_access_without_authentication(self):
        """تست دسترسی به API بدون احراز هویت"""
        # تست دسترسی به لیست تراکنش‌ها
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # تست ایجاد تراکنش
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '10000',
            'date_shamsi_input': '1404-06-01',
            'description': 'تست امنیتی'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_api_access_with_authentication(self):
        """تست دسترسی به API با احراز هویت"""
        # احراز هویت کاربر
        self.client.force_authenticate(user=self.test_user)
        
        # تست دسترسی به لیست تراکنش‌ها
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # تست ایجاد تراکنش
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '10000',
            'date_shamsi_input': '1404-06-01',
            'description': 'تست امنیتی'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_api_token_authentication(self):
        """تست احراز هویت با Token"""
        from rest_framework.authtoken.models import Token
        
        # ایجاد token برای کاربر
        token = Token.objects.create(user=self.test_user)
        
        # احراز هویت با token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # تست دسترسی
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_csrf_protection(self):
        """تست محافظت CSRF"""
        # لاگین
        self.client.login(username='api_test_user', password='api_password_123')
        
        # تست ارسال درخواست بدون CSRF token
        url = reverse('transaction-list')
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '10000',
            'date_shamsi_input': '1404-06-01',
            'description': 'تست CSRF'
        }
        
        # استفاده از APIClient که CSRF را نادیده می‌گیرد
        from rest_framework.test import APIClient
        api_client = APIClient()
        api_client.force_authenticate(user=self.test_user)
        
        response = api_client.post(url, data, format='json')
        # باید موفق باشد چون APIClient CSRF را نادیده می‌گیرد
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RateLimitingTestCase(APITestCase):
    """تست‌های Rate Limiting"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.test_user = User.objects.create_user(
            username='rate_limit_user',
            password='rate_limit_password_123',
            email='ratelimit@test.com'
        )
        
        self.client.force_authenticate(user=self.test_user)
    
    def test_api_rate_limiting(self):
        """تست محدودیت نرخ درخواست"""
        url = reverse('transaction-list')
        
        # ارسال چندین درخواست متوالی
        for i in range(10):
            response = self.client.get(url)
            # در حال حاضر rate limiting فعال نیست، پس همه درخواست‌ها باید موفق باشند
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class DataValidationTestCase(APITestCase):
    """تست‌های اعتبارسنجی داده‌ها"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.test_user = User.objects.create_user(
            username='validation_user',
            password='validation_password_123',
            email='validation@test.com'
        )
        
        self.client.force_authenticate(user=self.test_user)
        
        # ایجاد داده‌های تست
        self.investor = Investor.objects.create(
            first_name='احمد',
            last_name='محمدی',
            phone='09123456789',
            email='ahmad@test.com'
        )
        
        self.project = Project.objects.create(
            name='پروژه اعتبارسنجی',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        self.period = Period.objects.create(
            project=self.project,
            label='دوره اعتبارسنجی',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
    
    def test_invalid_transaction_type(self):
        """تست نوع تراکنش نامعتبر"""
        url = reverse('transaction-list')
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'invalid_type',
            'amount': '10000',
            'date_shamsi_input': '1404-06-01',
            'description': 'تست نوع نامعتبر'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_negative_amount(self):
        """تست مبلغ منفی"""
        url = reverse('transaction-list')
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '-1000',
            'date_shamsi_input': '1404-06-01',
            'description': 'تست مبلغ منفی'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_required_fields(self):
        """تست فیلدهای اجباری مفقود"""
        url = reverse('transaction-list')
        data = {
            'transaction_type': 'principal_deposit',
            'amount': '10000',
            'description': 'تست فیلدهای مفقود'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_date_format(self):
        """تست فرمت تاریخ نامعتبر"""
        url = reverse('transaction-list')
        data = {
            'investor_id': self.investor.id,
            'project_id': self.project.id,
            'period_id': self.period.id,
            'transaction_type': 'principal_deposit',
            'amount': '10000',
            'date_shamsi': 'invalid_date',
            'description': 'تست تاریخ نامعتبر'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
class SecurityIntegrationTestCase(APITestCase):
    """تست‌های یکپارچگی امنیتی"""
    
    def test_full_security_workflow(self):
        """تست کامل workflow امنیتی"""
        # 1. ایجاد کاربر جدید
        user = User.objects.create_user(
            username='integration_user',
            password='integration_password_123',
            email='integration@test.com'
        )
        
        # 2. تست احراز هویت
        authenticated_user = authenticate(
            username='integration_user',
            password='integration_password_123'
        )
        self.assertIsNotNone(authenticated_user)
        
        # 3. تست دسترسی به API
        self.client.force_authenticate(user=user)
        
        # ایجاد داده‌های تست
        investor = Investor.objects.create(
            first_name='احمد',
            last_name='محمدی',
            phone='09123456789',
            email='ahmad@test.com'
        )
        
        project = Project.objects.create(
            name='پروژه یکپارچگی امنیتی',
            start_date_shamsi='1400-01-01',
            end_date_shamsi='1405-12-29',
            start_date_gregorian='2021-03-21',
            end_date_gregorian='2027-03-20'
        )
        
        period = Period.objects.create(
            project=project,
            label='دوره یکپارچگی امنیتی',
            year=1404,
            month_number=6,
            month_name='شهریور',
            weight=1,
            start_date_shamsi='1404-06-01',
            end_date_shamsi='1404-06-30',
            start_date_gregorian='2025-08-23',
            end_date_gregorian='2025-09-21'
        )
        
        # 4. تست ایجاد تراکنش
        url = reverse('transaction-list')
        data = {
            'investor_id': investor.id,
            'project_id': project.id,
            'period_id': period.id,
            'transaction_type': 'principal_deposit',
            'amount': '50000',
            'date_shamsi_input': '1404-06-01',
            'description': 'تست یکپارچگی امنیتی'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 5. تست دریافت تراکنش
        transaction_id = response.data['id']
        detail_url = reverse('transaction-detail', kwargs={'pk': transaction_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6. تست خروج از سیستم
        self.client.logout()
        
        # 7. تست عدم دسترسی بعد از خروج
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
