from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.conf import settings
import os

# Create your views here.

def dashboard_home(request):
    """هدایت به داشبورد API"""
    return redirect('/api/dashboard/')

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

def csv_viewer(request):
    """نمایش صفحه نمایشگر CSV"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'csv_viewer.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

def csv_tabulator_viewer(request):
    """نمایش صفحه نمایشگر CSV با Tabulator"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'csv_tabulator_viewer.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

def investor_profile(request):
    """نمایش صفحه پروفایل سرمایه‌گذاران"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'investor_profile.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

def transaction_manager(request):
    """نمایش صفحه مدیریت تراکنش‌های مالی"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل یافت نشد', status=404)

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

def test_home_page(request):
    """نمایش صفحه تست Home Dashboard"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_home_page.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست Home یافت نشد', status=404)

def test_transaction_manager(request):
    """نمایش صفحه تست مدیریت تراکنش‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست مدیریت تراکنش‌ها یافت نشد', status=404)

def test_transaction_api(request):
    """نمایش صفحه تست API های مدیریت تراکنش‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_transaction_manager_api.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست API مدیریت تراکنش‌ها یافت نشد', status=404)

def test_filters(request):
    """نمایش صفحه تست فیلترهای مدیریت تراکنش‌ها"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_filters.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل تست فیلترها یافت نشد', status=404)


