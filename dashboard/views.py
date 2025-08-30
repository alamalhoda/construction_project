from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
import os

# Create your views here.

def dashboard_home(request):
    """نمایش صفحه اصلی داشبورد"""
    return render(request, 'dashboard/home.html')

def charts_investor(request):
    """نمایش صفحه نمودارهای سرمایه‌گذار"""
    # خواندن فایل HTML از پوشه view
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'charts_investor.html')
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
