from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
import logging
import json

# Create your views here.

# ایجاد logger برای dashboard views
logger = logging.getLogger('dashboard.views')

@login_required
def dashboard_home(request):
    """هدایت به داشبورد کاربری"""
    logger.info("User %s accessed dashboard_home, redirecting to user-dashboard", request.user.username)
    return redirect('/user-dashboard/')

@login_required
def project_dashboard(request):
    """نمایش صفحه داشبورد پروژه"""
    logger.info("User %s accessing project_dashboard", request.user.username)
    # خواندن فایل HTML از پوشه view
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'project_dashboard.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served project_dashboard for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in project_dashboard for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)


@login_required
def investor_profile(request):
    """نمایش صفحه پروفایل سرمایه‌گذاران"""
    logger.info("User %s accessing investor_profile", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'investor_profile.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served investor_profile for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in investor_profile for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def investor_pdf(request):
    """نمایش صفحه گزارش PDF سرمایه‌گذار"""
    logger.info("User %s accessing investor_pdf", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'investor_pdf.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served investor_pdf for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in investor_pdf for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def transaction_manager(request):
    """نمایش صفحه مدیریت تراکنش‌های مالی"""
    logger.info("User %s accessing transaction_manager", request.user.username)
    from django.middleware.csrf import get_token
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # فقط اگر token معتبر موجود بود، آن را به JavaScript اضافه کن
        # در غیر این صورت، JavaScript از cookie یا API endpoint استفاده خواهد کرد
        if csrf_token:
            logger.debug("CSRF token generated for user %s", request.user.username)
            csrf_script = f"""
        <script>
        // CSRF Token از سرور
        window.csrfToken = {json.dumps(csrf_token)};
        console.log('CSRF Token from server:', window.csrfToken);
        console.log('CSRF Token length:', window.csrfToken.length);
        </script>
        """
            # قرار دادن script قبل از closing body tag
            content = content.replace('</body>', csrf_script + '</body>')
        else:
            logger.warning("CSRF token not available for user %s", request.user.username)
        
        logger.info("Successfully served transaction_manager for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in transaction_manager for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def serve_csv_file(request, filename):
    """سرو کردن فایل‌های CSV از پوشه view"""
    logger.info("User %s requesting CSV file: %s", request.user.username, filename)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            response = HttpResponse(file.read(), content_type='text/csv')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            logger.info("Successfully served CSV file %s for user %s", filename, request.user.username)
            return response
    except FileNotFoundError:
        logger.error("CSV file not found: %s for user %s", file_path, request.user.username)
        raise Http404('‏‍فایل یافت نشد')
    except Exception as e:
        logger.exception("Unexpected error serving CSV file %s for user %s: %s", filename, request.user.username, e)
        raise Http404('خطای سرور')

@login_required
def test_home_page(request):
    """نمایش صفحه تست Home Dashboard"""
    logger.info("User %s accessing test_home_page", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_home_page.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served test_home_page for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل تست Home یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in test_home_page for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def test_transaction_manager(request):
    """نمایش صفحه تست مدیریت تراکنش‌ها"""
    logger.info("User %s accessing test_transaction_manager", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served test_transaction_manager for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل تست مدیریت تراکنش‌ها یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in test_transaction_manager for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def test_transaction_api(request):
    """نمایش صفحه تست API های مدیریت تراکنش‌ها"""
    logger.info("User %s accessing test_transaction_api", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_transaction_manager_api.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served test_transaction_api for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل تست API مدیریت تراکنش‌ها یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in test_transaction_api for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def test_filters(request):
    """نمایش صفحه تست فیلترهای مدیریت تراکنش‌ها"""
    logger.info("User %s accessing test_filters", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'test_filters.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served test_filters for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل تست فیلترها یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in test_filters for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def expense_dashboard(request):
    """نمایش صفحه لیست هزینه ها"""
    logger.info("User %s accessing expense_dashboard", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'expense_dashboard.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served expense_dashboard for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل لیست هزینه ها یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in expense_dashboard for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def interest_rate_manager(request):
    """نمایش صفحه مدیریت نرخ سود"""
    logger.info("User %s accessing interest_rate_manager", request.user.username)
    from django.middleware.csrf import get_token
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'interestrate_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # فقط اگر token معتبر موجود بود، آن را به JavaScript اضافه کن
        # در غیر این صورت، JavaScript از cookie یا API endpoint استفاده خواهد کرد
        if csrf_token:
            logger.debug("CSRF token generated for user %s", request.user.username)
            csrf_script = f"""
        <script>
        // CSRF Token از سرور
        window.csrfToken = {json.dumps(csrf_token)};
        console.log('CSRF Token from server:', window.csrfToken);
        console.log('CSRF Token length:', window.csrfToken.length);
        </script>
        """
            # قرار دادن script قبل از closing body tag
            content = content.replace('</body>', csrf_script + '</body>')
        else:
            logger.warning("CSRF token not available for user %s", request.user.username)
        
        logger.info("Successfully served interest_rate_manager for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل مدیریت نرخ سود یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in interest_rate_manager for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def period_summary(request):
    """نمایش صفحه خلاصه دوره‌ای پروژه"""
    logger.info("User %s accessing period_summary", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'period_summary.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served period_summary for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل خلاصه دوره‌ای یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in period_summary for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def investors_summary_print(request):
    """نمایش صفحه چاپ خلاصه سرمایه‌گذاران"""
    logger.info("User %s accessing investors_summary_print", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'investors_summary_print.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served investors_summary_print for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل خلاصه سرمایه‌گذاران یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in investors_summary_print for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def period_summary_print(request):
    """نمایش صفحه چاپ خلاصه دوره‌ای پروژه"""
    logger.info("User %s accessing period_summary_print", request.user.username)
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'period_summary_print.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully served period_summary_print for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل خلاصه دوره‌ای یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in period_summary_print for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def user_dashboard(request):
    """نمایش داشبورد کاربری از فایل جدید"""
    logger.info("User %s accessing user_dashboard", request.user.username)
    
    # بررسی دسترسی کاربر
    if not request.user.is_authenticated:
        logger.warning("Unauthenticated user attempted to access user_dashboard")
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
    
    logger.debug("User %s is_technical_admin: %s", request.user.username, context['is_technical_admin'])
    
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
        
        logger.info("Successfully served user_dashboard for user %s (admin: %s)", request.user.username, context['is_technical_admin'])
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('‏‍فایل داشبورد کاربری یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in user_dashboard for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)

@login_required
def detailed_calculations(request):
    """نمایش صفحه محاسبات دقیق"""
    logger.info("User %s accessing detailed_calculations", request.user.username)
    from construction.calculations import (
        ProjectCalculations, 
        ProfitCalculations, 
        InvestorCalculations, 
        TransactionCalculations,
        ComprehensiveCalculations
    )
    
    try:
        # دریافت تحلیل جامع پروژه
        logger.debug("Fetching comprehensive analysis for user %s", request.user.username)
        comprehensive_analysis = ComprehensiveCalculations.get_comprehensive_project_analysis()
        
        # دریافت آمار تمام سرمایه‌گذاران
        logger.debug("Fetching investors summary for user %s", request.user.username)
        investors_summary = InvestorCalculations.get_all_investors_summary()
        
        # آماده‌سازی context
        context = {
            'comprehensive_analysis': comprehensive_analysis,
            'investors_summary': investors_summary,
            'user': request.user,
            'user_full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        }
        
        # خواندن فایل HTML از پوشه view
        file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'detailed_calculations.html')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # جایگزینی template variables
            content = content.replace('{{ user_full_name }}', context['user_full_name'])
            
            logger.info("Successfully served detailed_calculations for user %s", request.user.username)
            return HttpResponse(content)
        except FileNotFoundError:
            logger.error("File not found: %s for user %s", file_path, request.user.username)
            return HttpResponse('فایل محاسبات دقیق یافت نشد', status=404)
            
    except Exception as e:
        logger.exception("Error in detailed_calculations for user %s: %s", request.user.username, e)
        return HttpResponse(f'خطا در محاسبات: {str(e)}', status=500)


@login_required
def petty_cash_dashboard(request):
    """صفحه مدیریت تراکنش‌های تنخواه"""
    logger.info("User %s accessing petty_cash_dashboard", request.user.username)
    from django.middleware.csrf import get_token
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_dashboard.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # فقط اگر token معتبر موجود بود، آن را به JavaScript اضافه کن
        # در غیر این صورت، JavaScript از cookie یا API endpoint استفاده خواهد کرد
        if csrf_token:
            logger.debug("CSRF token generated for user %s", request.user.username)
            csrf_script = f"""
        <script>
        // CSRF Token از سرور
        window.csrfToken = {json.dumps(csrf_token)};
        console.log('CSRF Token from server:', window.csrfToken);
        console.log('CSRF Token length:', window.csrfToken.length);
        </script>
        """
            # قرار دادن script قبل از closing body tag
            content = content.replace('</body>', csrf_script + '</body>')
        else:
            logger.warning("CSRF token not available for user %s", request.user.username)
        
        logger.info("Successfully served petty_cash_dashboard for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل مدیریت تنخواه یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in petty_cash_dashboard for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)


@login_required
def petty_cash_balance_report(request):
    """صفحه گزارش وضعیت مالی"""
    logger.info("User %s accessing petty_cash_balance_report", request.user.username)
    from django.middleware.csrf import get_token
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_balance_report.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # فقط اگر token معتبر موجود بود، آن را به JavaScript اضافه کن
        # در غیر این صورت، JavaScript از cookie یا API endpoint استفاده خواهد کرد
        if csrf_token:
            logger.debug("CSRF token generated for user %s", request.user.username)
            csrf_script = f"""
        <script>
        window.csrfToken = {json.dumps(csrf_token)};
        </script>
        """
            content = content.replace('</body>', csrf_script + '</body>')
        else:
            logger.warning("CSRF token not available for user %s", request.user.username)
        
        logger.info("Successfully served petty_cash_balance_report for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل گزارش وضعیت مالی یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in petty_cash_balance_report for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)


@login_required
def petty_cash_period_report(request):
    """صفحه گزارش دوره‌ای"""
    logger.info("User %s accessing petty_cash_period_report", request.user.username)
    from django.middleware.csrf import get_token
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_period_report.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # فقط اگر token معتبر موجود بود، آن را به JavaScript اضافه کن
        # در غیر این صورت، JavaScript از cookie یا API endpoint استفاده خواهد کرد
        if csrf_token:
            logger.debug("CSRF token generated for user %s", request.user.username)
            csrf_script = f"""
        <script>
        window.csrfToken = {json.dumps(csrf_token)};
        </script>
        """
            content = content.replace('</body>', csrf_script + '</body>')
        else:
            logger.warning("CSRF token not available for user %s", request.user.username)
        
        logger.info("Successfully served petty_cash_period_report for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل گزارش دوره‌ای یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in petty_cash_period_report for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)


@login_required
def petty_cash_detail_report(request):
    """صفحه گزارش تفصیلی"""
    logger.info("User %s accessing petty_cash_detail_report", request.user.username)
    from django.middleware.csrf import get_token
    
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_detail_report.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # دریافت CSRF token از Django
        csrf_token = get_token(request)
        
        # فقط اگر token معتبر موجود بود، آن را به JavaScript اضافه کن
        # در غیر این صورت، JavaScript از cookie یا API endpoint استفاده خواهد کرد
        if csrf_token:
            logger.debug("CSRF token generated for user %s", request.user.username)
            csrf_script = f"""
        <script>
        window.csrfToken = {json.dumps(csrf_token)};
        </script>
        """
            content = content.replace('</body>', csrf_script + '</body>')
        else:
            logger.warning("CSRF token not available for user %s", request.user.username)
        
        logger.info("Successfully served petty_cash_detail_report for user %s", request.user.username)
        return HttpResponse(content)
    except FileNotFoundError:
        logger.error("File not found: %s for user %s", file_path, request.user.username)
        return HttpResponse('فایل گزارش تفصیلی یافت نشد', status=404)
    except Exception as e:
        logger.exception("Unexpected error in petty_cash_detail_report for user %s: %s", request.user.username, e)
        return HttpResponse('خطای سرور', status=500)


