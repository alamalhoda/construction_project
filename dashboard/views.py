from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os

# Create your views here.

@login_required
def dashboard_home(request):
    """هدایت به داشبورد کاربری"""
    return redirect('/user-dashboard/')

@login_required
def project_dashboard(request):
    """نمایش صفحه داشبورد پروژه"""
    # خواندن فایل HTML از پوشه view
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'project_dashboard.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

@login_required
def csv_viewer(request):
    """نمایش صفحه نمایشگر CSV"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'csv_viewer.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

@login_required
def csv_tabulator_viewer(request):
    """نمایش صفحه نمایشگر CSV با Tabulator"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'csv_tabulator_viewer.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

@login_required
def investor_profile(request):
    """نمایش صفحه پروفایل سرمایه‌گذاران"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'investor_profile.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

@login_required
def transaction_manager(request):
    """نمایش صفحه مدیریت تراکنش‌های مالی"""
    from django.middleware.csrf import get_token
    from django.utils.crypto import get_random_string
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # اگر token خالی است، یک token جدید تولید کن
        if not csrf_token:
            csrf_token = get_random_string(64)
        
        # اضافه کردن CSRF token به JavaScript
        csrf_script = f"""
        <script>
        // CSRF Token از سرور
        window.csrfToken = '{csrf_token}';
        console.log('CSRF Token from server:', window.csrfToken);
        console.log('CSRF Token length:', window.csrfToken.length);
        </script>
        """
        
        # قرار دادن script قبل از closing body tag
        content = content.replace('</body>', csrf_script + '</body>')
        
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

@login_required
def serve_csv_file(request, filename):
    """سرو کردن فایل‌های CSV از پوشه view"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            response = HttpResponse(file.read(), content_type='text/csv')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    except FileNotFoundError:
        raise Http404('‏‍فایل یافت نشد')

@login_required
def test_home_page(request):
    """نمایش صفحه تست Home Dashboard"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_home_page.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست Home یافت نشد', status=404)

@login_required
def test_transaction_manager(request):
    """نمایش صفحه تست مدیریت تراکنش‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست مدیریت تراکنش‌ها یافت نشد', status=404)

@login_required
def test_transaction_api(request):
    """نمایش صفحه تست API های مدیریت تراکنش‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_transaction_manager_api.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست API مدیریت تراکنش‌ها یافت نشد', status=404)

@login_required
def test_filters(request):
    """نمایش صفحه تست فیلترهای مدیریت تراکنش‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_filters.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست فیلترها یافت نشد', status=404)

@login_required
def expense_dashboard(request):
    """نمایش صفحه داشبورد هزینه‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'expense_dashboard.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل داشبورد هزینه‌ها یافت نشد', status=404)

@login_required
def interest_rate_manager(request):
    """نمایش صفحه مدیریت نرخ سود"""
    from django.middleware.csrf import get_token
    from django.utils.crypto import get_random_string
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'interestrate_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # اگر token خالی است، یک token جدید تولید کن
        if not csrf_token:
            csrf_token = get_random_string(64)
        
        # اضافه کردن CSRF token به JavaScript
        csrf_script = f"""
        <script>
        // CSRF Token از سرور
        window.csrfToken = '{csrf_token}';
        console.log('CSRF Token from server:', window.csrfToken);
        console.log('CSRF Token length:', window.csrfToken.length);
        </script>
        """
        
        # قرار دادن script قبل از closing body tag
        content = content.replace('</body>', csrf_script + '</body>')
        
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل مدیریت نرخ سود یافت نشد', status=404)


