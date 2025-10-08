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
def investor_pdf(request):
    """نمایش صفحه گزارش PDF سرمایه‌گذار"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'investor_pdf.html')
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

@login_required
def user_dashboard(request):
    """نمایش داشبورد کاربری از فایل جدید"""
    
    # بررسی دسترسی کاربر
    if not request.user.is_authenticated:
        return redirect('user_login')
    
    user = request.user
    
    # آماده‌سازی context برای template
    context = {
        'user': user,
        'user_full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'last_login': user.last_login,
        'date_joined': user.date_joined,
        'is_technical_admin': user.is_staff or user.is_superuser,
        'is_end_user': not (user.is_staff or user.is_superuser),
    }
    
    # خواندن فایل HTML از پوشه view
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'user_dashboard.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # جایگزینی template variables با مقادیر واقعی
        content = content.replace('{{ user_full_name }}', context['user_full_name'])
        
        # جایگزینی template tags برای دسترسی مدیر فنی
        if context['is_technical_admin']:
            # نمایش کامل برای مدیر فنی
            content = content.replace('{% if is_technical_admin %}', '')
            content = content.replace('{% else %}', '<!-- کاربران عادی -->')
            content = content.replace('{% endif %}', '')
        else:
            # حذف بخش admin و نمایش فقط بخش user
            admin_start = content.find('{% if is_technical_admin %}')
            else_pos = content.find('{% else %}')
            endif_pos = content.find('{% endif %}')
            
            if admin_start != -1 and else_pos != -1 and endif_pos != -1:
                # نگه داشتن فقط بخش else (کاربر عادی)
                user_content = content[else_pos + len('{% else %}'):endif_pos]
                content = content[:admin_start] + user_content + content[endif_pos + len('{% endif %}'):]
            else:
                # اگر template tags پیدا نشد، همه محتوا را نمایش بده
                content = content.replace('{% if is_technical_admin %}', '')
                content = content.replace('{% else %}', '')
                content = content.replace('{% endif %}', '')
        
        # پاک کردن template tags باقی‌مانده
        content = content.replace('{% if is_technical_admin %}', '')
        content = content.replace('{% endif %}', '')
        
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('‏‍فایل داشبورد کاربری یافت نشد', status=404)


