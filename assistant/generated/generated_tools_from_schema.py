"""
Tools تولید شده خودکار از OpenAPI Schema
این فایل به صورت خودکار از schema.json تولید شده است.

📊 آمار استخراج شده:
   - تعداد کل Endpoints: 107
   - تعداد کل پارامترها: 319
   - تعداد دسته‌بندی‌ها (Tags): 12

✅ اطلاعات شامل شده در هر Tool:
   - توضیحات کامل endpoint (description)
   - مسیر API (path)
   - متد HTTP (GET, POST, PUT, DELETE, PATCH)
   - تمام پارامترها (path, query, body) با نام فارسی
   - توضیحات کامل هر فیلد (description, type, format)
   - فیلدهای الزامی و اختیاری (required)
   - مقادیر enum (اگر وجود داشته باشد)
   - Validation rules (min/max, pattern, etc)
   - نیاز به احراز هویت (security)
   - کدهای وضعیت پاسخ (responses)
   - Operation ID
   - دسته‌بندی (tags)

⚠️  توجه: این Tools نیاز به پیاده‌سازی کامل دارند.
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
import re
from django.conf import settings


# ===== Tools for Expense (11 endpoint) =====

@tool
def expense_list(request=None) -> str:
    """
    دریافت لیست تمام هزینه‌های پروژه جاری

    دریافت لیست تمام هزینه‌های پروژه جاری
    
    این متد لیست هزینه‌های مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی با پیشوند "-" برای نزولی (پیش‌فرض: -created_at)
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Expense/?page=1&page_size=20&ordering=-amount
    
    نکات:
        - فقط هزینه‌های پروژه جاری برگردانده می‌شود
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Expense/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Expense/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_create(expense_type: str, amount: str, period: int, project: Optional[int] = None, description: Optional[str] = None, request=None) -> str:
    """
    ایجاد هزینه جدید برای پروژه جاری

    ایجاد هزینه جدید برای پروژه جاری
    
    این متد هزینه جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - period (الزامی): شناسه دوره متعلق به پروژه جاری
        - expense_type (الزامی): نوع هزینه (project_manager, facilities_manager, procurement, warehouse, construction_contractor, other)
        - amount (الزامی): مبلغ هزینه به تومان (به صورت string)
        - description (اختیاری): توضیحات تکمیلی
    
    Returns:
        Response با اطلاعات هزینه ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Expense/
        {
            "period": 1,
            "expense_type": "project_manager",
            "amount": "5000000",
            "description": "حقوق مدیر پروژه برای ماه دسامبر"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - expense_type (نوع هزینه): string
              نوع هزینه. مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: بله
            - amount (مبلغ): string
              مبلغ هزینه به تومان. باید مقدار مثبت باشد. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. حداکثر 500 کاراکتر. (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که هزینه برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: بله

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Expense/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if expense_type is None: raise ValueError('نوع هزینه الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if period is None: raise ValueError('دوره الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Expense/'
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if expense_type is not None:
            data['expense_type'] = expense_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if period is not None:
            data['period'] = period
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک هزینه خاص

    دریافت جزئیات یک هزینه خاص
    
    این متد اطلاعات کامل هزینه با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه
    
    Returns:
        Response با اطلاعات کامل هزینه شامل period_data و period_weight
    
    مثال:
        GET /api/v1/Expense/1/
    
    نکات:
        - فقط هزینه‌های پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Expense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Expense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_update(id: int, expense_type: str, amount: str, period: int, project: Optional[int] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی کامل هزینه

    به‌روزرسانی کامل هزینه
    
    این متد امکان تغییر همه فیلدهای یک هزینه را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه
    
    Request Body:
        - تمام فیلدهای قابل ویرایش (period, expense_type, amount, description)
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده هزینه (status 200)
    
    مثال:
        PUT /api/v1/Expense/1/
        {
            "period": 1,
            "expense_type": "project_manager",
            "amount": "6000000",
            "description": "حقوق مدیر پروژه - به‌روزرسانی شده"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند (به جز project که خودکار تنظیم می‌شود)
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - expense_type (نوع هزینه): string
              نوع هزینه. مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: بله
            - amount (مبلغ): string
              مبلغ هزینه به تومان. باید مقدار مثبت باشد. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. حداکثر 500 کاراکتر. (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که هزینه برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: بله

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Expense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if expense_type is None: raise ValueError('نوع هزینه الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if period is None: raise ValueError('دوره الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Expense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if expense_type is not None:
            data['expense_type'] = expense_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if period is not None:
            data['period'] = period
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_partial_update(id: int, project: Optional[int] = None, expense_type: Optional[str] = None, amount: Optional[str] = None, description: Optional[str] = None, period: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی هزینه

    به‌روزرسانی جزئی هزینه
    
    این متد امکان تغییر بخشی از فیلدهای هزینه را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی (period, expense_type, amount, description)
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده هزینه (status 200)
    
    مثال:
        PATCH /api/v1/Expense/1/
        {
            "amount": "7000000"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - expense_type (نوع هزینه): string
              نوع هزینه. مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ هزینه به تومان. باید مقدار مثبت باشد. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. حداکثر 500 کاراکتر. (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که هزینه برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Expense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Expense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if expense_type is not None:
            data['expense_type'] = expense_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if period is not None:
            data['period'] = period
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_destroy(id: int, request=None) -> str:
    """
    حذف هزینه

    حذف هزینه
    
    این متد هزینه را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Expense/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط هزینه‌های پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        - در صورت وجود وابستگی، ممکن است حذف ناموفق باشد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Expense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Expense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_dashboard_data_retrieve(request=None) -> str:
    """
    دریافت داده‌های لیست هزینه‌ها

    دریافت داده‌های لیست هزینه‌ها
    
    این endpoint داده‌های کامل داشبورد هزینه‌ها را بر اساس دوره‌ها و انواع هزینه
    برمی‌گرداند. شامل:
    - لیست تمام دوره‌ها با هزینه‌های هر نوع
    - مجموع تجمعی هزینه‌ها
    - مجموع هر ستون (هر نوع هزینه)
    - مجموع کل همه هزینه‌ها
    
    Returns:
        Response: شامل:
            - periods: لیست دوره‌ها با هزینه‌های هر نوع
            - expense_types: انواع هزینه‌ها
            - column_totals: مجموع هر نوع هزینه در تمام دوره‌ها
            - grand_total: مجموع کل همه هزینه‌ها
    
    نکات مهم:
    - فقط هزینه‌های پروژه جاری را برمی‌گرداند
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - داده‌ها بر اساس دوره مرتب می‌شوند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Expense/dashboard_data/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Expense/dashboard_data/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_get_expense_details_retrieve(request=None) -> str:
    """
    دریافت جزئیات هزینه برای ویرایش

    دریافت جزئیات هزینه برای ویرایش

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Expense/get_expense_details/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Expense/get_expense_details/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_total_expenses_retrieve(request=None) -> str:
    """
    دریافت مجموع کل هزینه‌های پروژه

    دریافت مجموع کل هزینه‌های پروژه

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Expense/total_expenses/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Expense/total_expenses/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_update_expense_create(expense_type: str, amount: str, period: int, project: Optional[int] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی یا ایجاد هزینه برای یک دوره و نوع خاص

    به‌روزرسانی یا ایجاد هزینه برای یک دوره و نوع خاص
    
    این endpoint امکان به‌روزرسانی یا ایجاد هزینه برای یک دوره و نوع خاص را فراهم می‌کند.
    اگر هزینه وجود داشته باشد، به‌روزرسانی می‌شود؛ در غیر این صورت ایجاد می‌شود.
    
    Parameters:
        period_id (int): شناسه دوره
        expense_type (str): نوع هزینه (project_manager, facilities_manager, ...)
        amount (float/str): مبلغ هزینه
        description (str, optional): توضیحات هزینه
    
    Returns:
        Response: شامل:
            - success: وضعیت موفقیت
            - message: پیام پاسخ
            - data: شامل expense_id, amount, description, created
    
    نکات مهم:
    - هزینه بر اساس پروژه جاری (active project) از session شناسایی می‌شود
    - اگر هزینه وجود داشته باشد، به‌روزرسانی می‌شود؛ در غیر این صورت ایجاد می‌شود
    - مبلغ باید به صورت string ارسال شود تا از مشکلات precision جلوگیری شود
    - نیاز به احراز هویت دارد (IsAuthenticated)

    پارامترهای درخواست:

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - expense_type (نوع هزینه): string
              نوع هزینه. مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: بله
            - amount (مبلغ): string
              مبلغ هزینه به تومان. باید مقدار مثبت باشد. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. حداکثر 500 کاراکتر. (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که هزینه برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: بله

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Expense/update_expense/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if expense_type is None: raise ValueError('نوع هزینه الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if period is None: raise ValueError('دوره الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Expense/update_expense/'
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if expense_type is not None:
            data['expense_type'] = expense_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if period is not None:
            data['period'] = period
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_with_periods_retrieve(request=None) -> str:
    """
    دریافت هزینه‌ها با اطلاعات دوره‌ها برای محاسبه دور...

    دریافت هزینه‌ها با اطلاعات دوره‌ها برای محاسبه دوره متوسط ساخت

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Expense/with_periods/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Expense/with_periods/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for InterestRate (7 endpoint) =====

@tool
def interestrate_list(request=None) -> str:
    """
    دریافت لیست تمام نرخ‌های سود پروژه جاری

    دریافت لیست تمام نرخ‌های سود پروژه جاری
    
    این متد لیست نرخ‌های سود مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/InterestRate/?page=1
    
    نکات:
        - فقط نرخ‌های سود پروژه جاری برگردانده می‌شود
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/InterestRate/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/InterestRate/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_create(rate: str, effective_date: str, project: Optional[int] = None, description: Optional[str] = None, is_active: Optional[bool] = None, request=None) -> str:
    """
    ایجاد نرخ سود جدید برای پروژه جاری

    ایجاد نرخ سود جدید برای پروژه جاری
    
    این متد نرخ سود جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - rate (الزامی): نرخ سود روزانه (به صورت string)
        - effective_date (الزامی): تاریخ اعمال شمسی (YYYY-MM-DD)
        - description (اختیاری): توضیحات
        - is_active (اختیاری): فعال/غیرفعال (پیش‌فرض: True)
    
    Returns:
        Response با اطلاعات نرخ سود ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/InterestRate/
        {
            "rate": "0.000481925679775",
            "effective_date": "1403-01-01",
            "description": "نرخ سود جدید از ابتدای سال 1403",
            "is_active": true
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - تاریخ میلادی به صورت خودکار محاسبه می‌شود
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - rate (rate): string
              نرخ سود روزانه (به صورت اعشاری، مثال: 0.000481925679775). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - effective_date (effective_date): string
              تاریخ اعمال نرخ سود به شمسی به فرمت YYYY-MM-DD (مثال: 1403-01-01). (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات درباره تغییر نرخ سود. (اختیاری)
              الزامی: خیر
            - is_active (is_active): boolean
              آیا این نرخ در حال حاضر فعال است؟ (پیش‌فرض: True)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/InterestRate/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if rate is None: raise ValueError('rate الزامی است')
        if rate is not None and not re.match(r'^-?\d{0,5}(?:\.\d{0,15})?$', str(rate)): raise ValueError('rate فرمت نامعتبر است')
        if effective_date is None: raise ValueError('effective_date الزامی است')
        if effective_date is not None and len(effective_date) < 1: raise ValueError('effective_date حداقل 1 کاراکتر باید باشد')
        # ساخت URL کامل
        url = '/api/v1/InterestRate/'
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if rate is not None:
            data['rate'] = rate
        if effective_date is not None:
            data['effective_date'] = effective_date
        if description is not None:
            data['description'] = description
        if is_active is not None:
            data['is_active'] = is_active
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک نرخ سود خاص

    دریافت جزئیات یک نرخ سود خاص
    
    این متد اطلاعات کامل نرخ سود با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای نرخ سود
    
    Returns:
        Response با اطلاعات کامل نرخ سود
    
    مثال:
        GET /api/v1/InterestRate/1/
    
    نکات:
        - فقط نرخ‌های سود پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/InterestRate/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/InterestRate/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_update(id: int, rate: str, effective_date: str, project: Optional[int] = None, description: Optional[str] = None, is_active: Optional[bool] = None, request=None) -> str:
    """
    به‌روزرسانی کامل نرخ سود

    به‌روزرسانی کامل نرخ سود
    
    این متد امکان تغییر همه فیلدهای یک نرخ سود را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای نرخ سود
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده نرخ سود (status 200)
    
    مثال:
        PUT /api/v1/InterestRate/1/
        {
            "rate": "0.000500000000000",
            "effective_date": "1403-07-01",
            "is_active": true
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - rate (rate): string
              نرخ سود روزانه (به صورت اعشاری، مثال: 0.000481925679775). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - effective_date (effective_date): string
              تاریخ اعمال نرخ سود به شمسی به فرمت YYYY-MM-DD (مثال: 1403-01-01). (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات درباره تغییر نرخ سود. (اختیاری)
              الزامی: خیر
            - is_active (is_active): boolean
              آیا این نرخ در حال حاضر فعال است؟ (پیش‌فرض: True)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/InterestRate/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if rate is None: raise ValueError('rate الزامی است')
        if rate is not None and not re.match(r'^-?\d{0,5}(?:\.\d{0,15})?$', str(rate)): raise ValueError('rate فرمت نامعتبر است')
        if effective_date is None: raise ValueError('effective_date الزامی است')
        if effective_date is not None and len(effective_date) < 1: raise ValueError('effective_date حداقل 1 کاراکتر باید باشد')
        # ساخت URL کامل
        url = '/api/v1/InterestRate/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if rate is not None:
            data['rate'] = rate
        if effective_date is not None:
            data['effective_date'] = effective_date
        if description is not None:
            data['description'] = description
        if is_active is not None:
            data['is_active'] = is_active
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_partial_update(id: int, project: Optional[int] = None, rate: Optional[str] = None, effective_date: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی نرخ سود

    به‌روزرسانی جزئی نرخ سود
    
    این متد امکان تغییر بخشی از فیلدهای نرخ سود را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای نرخ سود
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده نرخ سود (status 200)
    
    مثال:
        PATCH /api/v1/InterestRate/1/
        {
            "is_active": false
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - rate (rate): string
              نرخ سود روزانه (به صورت اعشاری، مثال: 0.000481925679775). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - effective_date (effective_date): string
              تاریخ اعمال نرخ سود به شمسی به فرمت YYYY-MM-DD (مثال: 1403-01-01). (الزامی)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات درباره تغییر نرخ سود. (اختیاری)
              الزامی: خیر
            - is_active (is_active): boolean
              آیا این نرخ در حال حاضر فعال است؟ (پیش‌فرض: True)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/InterestRate/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if rate is not None and not re.match(r'^-?\d{0,5}(?:\.\d{0,15})?$', str(rate)): raise ValueError('rate فرمت نامعتبر است')
        if effective_date is not None and len(effective_date) < 1: raise ValueError('effective_date حداقل 1 کاراکتر باید باشد')
        # ساخت URL کامل
        url = '/api/v1/InterestRate/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if rate is not None:
            data['rate'] = rate
        if effective_date is not None:
            data['effective_date'] = effective_date
        if description is not None:
            data['description'] = description
        if is_active is not None:
            data['is_active'] = is_active
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_destroy(id: int, request=None) -> str:
    """
    حذف نرخ سود

    حذف نرخ سود
    
    این متد نرخ سود را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای نرخ سود
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/InterestRate/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط نرخ‌های سود پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        - در صورت وجود وابستگی (تراکنش‌ها)، ممکن است حذف ناموفق باشد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/InterestRate/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/InterestRate/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_current_retrieve(request=None) -> str:
    """
    دریافت نرخ سود فعال فعلی برای پروژه فعال

    دریافت نرخ سود فعال فعلی برای پروژه فعال

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/InterestRate/current/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/InterestRate/current/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Investor (14 endpoint) =====

@tool
def investor_list(request=None) -> str:
    """
    دریافت لیست تمام سرمایه‌گذاران پروژه جاری

    دریافت لیست تمام سرمایه‌گذاران پروژه جاری
    
    این متد لیست سرمایه‌گذاران مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی با پیشوند "-" برای نزولی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Investor/?page=1&page_size=20
    
    نکات:
        - فقط سرمایه‌گذاران پروژه جاری برگردانده می‌شود
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Investor/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_create(first_name: str, last_name: str, phone: str, project: Optional[int] = None, email: Optional[str] = None, participation_type: Optional[str] = None, contract_date_shamsi: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ایجاد سرمایه‌گذار جدید برای پروژه جاری

    ایجاد سرمایه‌گذار جدید برای پروژه جاری
    
    این متد سرمایه‌گذار جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - first_name (الزامی): نام سرمایه‌گذار
        - last_name (الزامی): نام خانوادگی سرمایه‌گذار
        - phone (الزامی): شماره تماس
        - email (اختیاری): آدرس ایمیل
        - participation_type (اختیاری): نوع مشارکت (owner, investor)
        - contract_date_shamsi (اختیاری): تاریخ قرارداد شمسی
        - description (اختیاری): توضیحات
    
    Returns:
        Response با اطلاعات سرمایه‌گذار ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Investor/
        {
            "first_name": "علی",
            "last_name": "احمدی",
            "phone": "09123456789",
            "email": "ali@example.com",
            "participation_type": "owner",
            "description": "مالک واحد 101"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - first_name (first_name): string
              نام سرمایه‌گذار. (الزامی)
              الزامی: بله
            - last_name (last_name): string
              نام خانوادگی سرمایه‌گذار. (الزامی)
              الزامی: بله
            - phone (تلفن): string
              شماره تماس سرمایه‌گذار. (الزامی)
              الزامی: بله
            - email (ایمیل): string
              آدرس ایمیل سرمایه‌گذار. (اختیاری)
              الزامی: خیر
            - participation_type (participation_type): string
              نوع مشارکت. مقادیر معتبر: owner (مالک), investor (سرمایه‌گذار). (پیش‌فرض: owner)

* `owner` - مالک
* `investor` - سرمایه‌گذار
              الزامی: خیر
            - contract_date_shamsi (contract_date_shamsi): string
              تاریخ قرارداد به شمسی. (اختیاری)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره سرمایه‌گذار. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Investor/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if first_name is None: raise ValueError('first_name الزامی است')
        if first_name is not None and len(first_name) < 1: raise ValueError('first_name حداقل 1 کاراکتر باید باشد')
        if first_name is not None and len(first_name) > 100: raise ValueError('first_name حداکثر 100 کاراکتر می‌تواند باشد')
        if last_name is None: raise ValueError('last_name الزامی است')
        if last_name is not None and len(last_name) < 1: raise ValueError('last_name حداقل 1 کاراکتر باید باشد')
        if last_name is not None and len(last_name) > 100: raise ValueError('last_name حداکثر 100 کاراکتر می‌تواند باشد')
        if phone is None: raise ValueError('تلفن الزامی است')
        if phone is not None and len(phone) < 1: raise ValueError('تلفن حداقل 1 کاراکتر باید باشد')
        if phone is not None and len(phone) > 20: raise ValueError('تلفن حداکثر 20 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Investor/'
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name
        if phone is not None:
            data['phone'] = phone
        if email is not None:
            data['email'] = email
        if participation_type is not None:
            data['participation_type'] = participation_type
        if contract_date_shamsi is not None:
            data['contract_date_shamsi'] = contract_date_shamsi
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک سرمایه‌گذار خاص

    دریافت جزئیات یک سرمایه‌گذار خاص
    
    این متد اطلاعات کامل سرمایه‌گذار با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای سرمایه‌گذار
    
    Returns:
        Response با اطلاعات کامل سرمایه‌گذار شامل units
    
    مثال:
        GET /api/v1/Investor/1/
    
    نکات:
        - فقط سرمایه‌گذاران پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_update(id: int, first_name: str, last_name: str, phone: str, project: Optional[int] = None, email: Optional[str] = None, participation_type: Optional[str] = None, contract_date_shamsi: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی کامل سرمایه‌گذار

    به‌روزرسانی کامل سرمایه‌گذار
    
    این متد امکان تغییر همه فیلدهای یک سرمایه‌گذار را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای سرمایه‌گذار
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده سرمایه‌گذار (status 200)
    
    مثال:
        PUT /api/v1/Investor/1/
        {
            "first_name": "علی",
            "last_name": "احمدی",
            "phone": "09123456789",
            "participation_type": "owner"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - first_name (first_name): string
              نام سرمایه‌گذار. (الزامی)
              الزامی: بله
            - last_name (last_name): string
              نام خانوادگی سرمایه‌گذار. (الزامی)
              الزامی: بله
            - phone (تلفن): string
              شماره تماس سرمایه‌گذار. (الزامی)
              الزامی: بله
            - email (ایمیل): string
              آدرس ایمیل سرمایه‌گذار. (اختیاری)
              الزامی: خیر
            - participation_type (participation_type): string
              نوع مشارکت. مقادیر معتبر: owner (مالک), investor (سرمایه‌گذار). (پیش‌فرض: owner)

* `owner` - مالک
* `investor` - سرمایه‌گذار
              الزامی: خیر
            - contract_date_shamsi (contract_date_shamsi): string
              تاریخ قرارداد به شمسی. (اختیاری)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره سرمایه‌گذار. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Investor/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if first_name is None: raise ValueError('first_name الزامی است')
        if first_name is not None and len(first_name) < 1: raise ValueError('first_name حداقل 1 کاراکتر باید باشد')
        if first_name is not None and len(first_name) > 100: raise ValueError('first_name حداکثر 100 کاراکتر می‌تواند باشد')
        if last_name is None: raise ValueError('last_name الزامی است')
        if last_name is not None and len(last_name) < 1: raise ValueError('last_name حداقل 1 کاراکتر باید باشد')
        if last_name is not None and len(last_name) > 100: raise ValueError('last_name حداکثر 100 کاراکتر می‌تواند باشد')
        if phone is None: raise ValueError('تلفن الزامی است')
        if phone is not None and len(phone) < 1: raise ValueError('تلفن حداقل 1 کاراکتر باید باشد')
        if phone is not None and len(phone) > 20: raise ValueError('تلفن حداکثر 20 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name
        if phone is not None:
            data['phone'] = phone
        if email is not None:
            data['email'] = email
        if participation_type is not None:
            data['participation_type'] = participation_type
        if contract_date_shamsi is not None:
            data['contract_date_shamsi'] = contract_date_shamsi
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_partial_update(id: int, project: Optional[int] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, participation_type: Optional[str] = None, contract_date_shamsi: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی سرمایه‌گذار

    به‌روزرسانی جزئی سرمایه‌گذار
    
    این متد امکان تغییر بخشی از فیلدهای سرمایه‌گذار را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای سرمایه‌گذار
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده سرمایه‌گذار (status 200)
    
    مثال:
        PATCH /api/v1/Investor/1/
        {
            "phone": "09123456789"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - first_name (first_name): string
              نام سرمایه‌گذار. (الزامی)
              الزامی: خیر
            - last_name (last_name): string
              نام خانوادگی سرمایه‌گذار. (الزامی)
              الزامی: خیر
            - phone (تلفن): string
              شماره تماس سرمایه‌گذار. (الزامی)
              الزامی: خیر
            - email (ایمیل): string
              آدرس ایمیل سرمایه‌گذار. (اختیاری)
              الزامی: خیر
            - participation_type (participation_type): string
              نوع مشارکت. مقادیر معتبر: owner (مالک), investor (سرمایه‌گذار). (پیش‌فرض: owner)

* `owner` - مالک
* `investor` - سرمایه‌گذار
              الزامی: خیر
            - contract_date_shamsi (contract_date_shamsi): string
              تاریخ قرارداد به شمسی. (اختیاری)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره سرمایه‌گذار. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Investor/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if first_name is not None and len(first_name) < 1: raise ValueError('first_name حداقل 1 کاراکتر باید باشد')
        if first_name is not None and len(first_name) > 100: raise ValueError('first_name حداکثر 100 کاراکتر می‌تواند باشد')
        if last_name is not None and len(last_name) < 1: raise ValueError('last_name حداقل 1 کاراکتر باید باشد')
        if last_name is not None and len(last_name) > 100: raise ValueError('last_name حداکثر 100 کاراکتر می‌تواند باشد')
        if phone is not None and len(phone) < 1: raise ValueError('تلفن حداقل 1 کاراکتر باید باشد')
        if phone is not None and len(phone) > 20: raise ValueError('تلفن حداکثر 20 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name
        if phone is not None:
            data['phone'] = phone
        if email is not None:
            data['email'] = email
        if participation_type is not None:
            data['participation_type'] = participation_type
        if contract_date_shamsi is not None:
            data['contract_date_shamsi'] = contract_date_shamsi
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_destroy(id: int, request=None) -> str:
    """
    حذف سرمایه‌گذار

    حذف سرمایه‌گذار
    
    این متد سرمایه‌گذار را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای سرمایه‌گذار
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Investor/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط سرمایه‌گذاران پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        - در صورت وجود وابستگی، ممکن است حذف ناموفق باشد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Investor/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_detailed_statistics_retrieve(id: int, request=None) -> str:
    """
    دریافت آمار تفصیلی سرمایه‌گذار

    دریافت آمار تفصیلی سرمایه‌گذار
    
    این endpoint آمار کامل و تفصیلی برای یک سرمایه‌گذار خاص را محاسبه و برمی‌گرداند.
    شامل اطلاعات مالی، سرمایه، سود، نسبت‌ها و سایر متریک‌های مرتبط.
    
    Parameters:
        pk (int): شناسه سرمایه‌گذار
        project_id (int, optional): شناسه پروژه (از query parameter یا پروژه جاری)
    
    Returns:
        Response: شامل آمار تفصیلی سرمایه‌گذار
    
    مثال Response:
    {
        "total_investment": 50000000,
        "total_profit": 15000000,
        "grand_total": 115000000,
        "ownership_percentage": 25.5,
        "unit_cost": 5000000
    }
    
    نکات مهم:
    - اگر سرمایه‌گذار یافت نشود، خطای 404 برمی‌گرداند
    - محاسبات بر اساس پروژه جاری یا project_id ارسالی انجام می‌شود
    - تمام مبالغ به تومان هستند

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/{id}/detailed_statistics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/detailed_statistics/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_cumulative_capital_and_unit_cost_chart_retrieve(id: int, request=None) -> str:
    """
    دریافت داده‌های نمودار ترند سرمایه موجود و هزینه و...

    دریافت داده‌های نمودار ترند سرمایه موجود و هزینه واحد برای سرمایه‌گذار
    
    این endpoint داده‌های لازم برای نمودار ترند را محاسبه می‌کند:
    - سرمایه موجود تجمعی به میلیون تومان
    - هزینه واحد به میلیون تومان برای هر دوره

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/{id}/investor_cumulative_capital_and_unit_cost_chart/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/investor_cumulative_capital_and_unit_cost_chart/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_ownership_retrieve(id: int, request=None) -> str:
    """
    دریافت مالکیت سرمایه‌گذار به متر مربع

    دریافت مالکیت سرمایه‌گذار به متر مربع
    
    محاسبه: (آورده + سود) / قیمت هر متر مربع واحد انتخابی

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/{id}/ownership/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/ownership/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_ratios_retrieve(id: int, request=None) -> str:
    """
    دریافت نسبت‌های سرمایه‌گذار

    دریافت نسبت‌های سرمایه‌گذار

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/{id}/ratios/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Investor/{id}/ratios/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_all_investors_summary_retrieve(request=None) -> str:
    """
    دریافت خلاصه آمار تمام سرمایه‌گذاران

    دریافت خلاصه آمار تمام سرمایه‌گذاران
    
    این endpoint از سرویس محاسباتی InvestorCalculations استفاده می‌کند
    تا آمار کامل شامل نسبت‌های سرمایه، سود و شاخص نفع را ارائه دهد.

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/all_investors_summary/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Investor/all_investors_summary/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_participation_stats_retrieve(request=None) -> str:
    """
    دریافت آمار مشارکت کنندگان بر اساس نوع (مالک و سرم...

    دریافت آمار مشارکت کنندگان بر اساس نوع (مالک و سرمایه گذار)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/participation_stats/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Investor/participation_stats/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_summary_retrieve(request=None) -> str:
    """
    خلاصه مالی تمام سرمایه‌گذاران پروژه

    خلاصه مالی تمام سرمایه‌گذاران پروژه
    
    این endpoint خلاصه مالی تمام سرمایه‌گذاران پروژه جاری را محاسبه و برمی‌گرداند.
    
    خروجی شامل:
    - شناسه و نام هر سرمایه‌گذار
    - نوع مشارکت (مالک یا سرمایه‌گذار)
    - مجموع آورده‌ها
    - مجموع برداشت‌ها
    - سرمایه خالص
    - مجموع سود
    - مجموع کل (سرمایه + سود)
    
    سناریوهای استفاده:
    - نمایش لیست خلاصه تمام سرمایه‌گذاران
    - مقایسه عملکرد سرمایه‌گذاران
    - تهیه گزارش‌های مدیریتی
    - نمایش داشبورد سرمایه‌گذاران
    
    مثال استفاده:
    GET /api/v1/Investor/summary/
    
    مثال خروجی:
    [
        {
            "investor_id": 1,
            "name": "علی احمدی",
            "participation_type": "owner",
            "total_deposits": 100000000,
            "total_withdrawals": 0,
            "net_principal": 100000000,
            "total_profit": 15000000,
            "grand_total": 115000000
        },
        {
            "investor_id": 2,
            "name": "محمد رضایی",
            "participation_type": "investor",
            "total_deposits": 50000000,
            "total_withdrawals": 10000000,
            "net_principal": 40000000,
            "total_profit": 7500000,
            "grand_total": 47500000
        }
    ]
    
    نکات مهم:
    - نتایج بر اساس سرمایه خالص (net_principal) به صورت نزولی مرتب می‌شوند
    - فقط سرمایه‌گذاران پروژه جاری را شامل می‌شود
    - اگر پروژه جاری وجود نداشته باشد، تمام سرمایه‌گذاران را برمی‌گرداند
    - تمام مبالغ به تومان هستند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/summary/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Investor/summary/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_summary_ssot_retrieve(request=None) -> str:
    """
    خلاصه مالی تمام سرمایه‌گذاران با مرجع واحد (بدون S...

    خلاصه مالی تمام سرمایه‌گذاران با مرجع واحد (بدون SQL خام)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Investor/summary_ssot/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Investor/summary_ssot/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Period (8 endpoint) =====

@tool
def period_list(request=None) -> str:
    """
    دریافت لیست تمام دوره‌های پروژه جاری

    دریافت لیست تمام دوره‌های پروژه جاری
    
    این متد لیست دوره‌های مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت مرتب شده بر اساس سال و ماه (نزولی) هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Period/?page=1&page_size=12
    
    نکات:
        - فقط دوره‌های پروژه جاری برگردانده می‌شود
        - دوره‌ها به صورت نزولی (جدیدترین اول) مرتب می‌شوند
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Period/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Period/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_create(label: str, year: int, month_number: int, month_name: str, weight: int, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, project: Optional[int] = None, request=None) -> str:
    """
    ایجاد دوره جدید برای پروژه جاری

    ایجاد دوره جدید برای پروژه جاری
    
    این متد دوره جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - label (الزامی): عنوان دوره
        - year (الزامی): سال شمسی
        - month_number (الزامی): شماره ماه (1-12)
        - month_name (الزامی): نام ماه
        - weight (الزامی): وزن دوره
        - start_date_shamsi (الزامی): تاریخ شروع شمسی
        - end_date_shamsi (الزامی): تاریخ پایان شمسی
        - start_date_gregorian (الزامی): تاریخ شروع میلادی
        - end_date_gregorian (الزامی): تاریخ پایان میلادی
    
    Returns:
        Response با اطلاعات دوره ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Period/
        {
            "label": "مهر 1403",
            "year": 1403,
            "month_number": 7,
            "month_name": "مهر",
            "weight": 1,
            "start_date_shamsi": "1403-07-01",
            "end_date_shamsi": "1403-07-29",
            "start_date_gregorian": "2024-09-22",
            "end_date_gregorian": "2024-10-20"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - هر ترکیب (project, year, month_number) باید یکتا باشد
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - label (label): string
              عنوان دوره (مثال: "مهر 1403"). (الزامی)
              الزامی: بله
            - year (year): integer
              سال شمسی دوره (مثال: 1403). (الزامی)
              الزامی: بله
            - month_number (month_number): integer
              شماره ماه شمسی (1 تا 12). (الزامی)
              الزامی: بله
            - month_name (month_name): string
              نام ماه شمسی (مثال: "مهر"). (الزامی)
              الزامی: بله
            - weight (weight): integer
              وزن دوره برای محاسبات مالی. هرچه بیشتر باشد، تأثیر بیشتری در محاسبات دارد. (الزامی)
              الزامی: بله
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع دوره به شمسی. (الزامی)
              الزامی: بله
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان دوره به شمسی. (الزامی)
              الزامی: بله
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع دوره به میلادی. (الزامی)
              الزامی: بله
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان دوره به میلادی. (الزامی)
              الزامی: بله
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Period/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if label is None: raise ValueError('label الزامی است')
        if label is not None and len(label) < 1: raise ValueError('label حداقل 1 کاراکتر باید باشد')
        if label is not None and len(label) > 50: raise ValueError('label حداکثر 50 کاراکتر می‌تواند باشد')
        if year is None: raise ValueError('year الزامی است')
        if month_number is None: raise ValueError('month_number الزامی است')
        if month_name is None: raise ValueError('month_name الزامی است')
        if month_name is not None and len(month_name) < 1: raise ValueError('month_name حداقل 1 کاراکتر باید باشد')
        if month_name is not None and len(month_name) > 20: raise ValueError('month_name حداکثر 20 کاراکتر می‌تواند باشد')
        if weight is None: raise ValueError('weight الزامی است')
        if start_date_shamsi is None: raise ValueError('start_date_shamsi الزامی است')
        if end_date_shamsi is None: raise ValueError('end_date_shamsi الزامی است')
        if start_date_gregorian is None: raise ValueError('start_date_gregorian الزامی است')
        if end_date_gregorian is None: raise ValueError('end_date_gregorian الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Period/'
        
        # ساخت data برای request body
        data = {}
        if label is not None:
            data['label'] = label
        if year is not None:
            data['year'] = year
        if month_number is not None:
            data['month_number'] = month_number
        if month_name is not None:
            data['month_name'] = month_name
        if weight is not None:
            data['weight'] = weight
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if project is not None:
            data['project'] = project
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک دوره خاص

    دریافت جزئیات یک دوره خاص
    
    این متد اطلاعات کامل دوره با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای دوره
    
    Returns:
        Response با اطلاعات کامل دوره
    
    مثال:
        GET /api/v1/Period/1/
    
    نکات:
        - فقط دوره‌های پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این دوره را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Period/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Period/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_update(id: int, label: str, year: int, month_number: int, month_name: str, weight: int, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, project: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی کامل دوره

    به‌روزرسانی کامل دوره
    
    این متد امکان تغییر همه فیلدهای یک دوره را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای دوره
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده دوره (status 200)
    
    مثال:
        PUT /api/v1/Period/1/
        {
            "label": "مهر 1403",
            "year": 1403,
            "month_number": 7,
            "weight": 2
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این دوره را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - label (label): string
              عنوان دوره (مثال: "مهر 1403"). (الزامی)
              الزامی: بله
            - year (year): integer
              سال شمسی دوره (مثال: 1403). (الزامی)
              الزامی: بله
            - month_number (month_number): integer
              شماره ماه شمسی (1 تا 12). (الزامی)
              الزامی: بله
            - month_name (month_name): string
              نام ماه شمسی (مثال: "مهر"). (الزامی)
              الزامی: بله
            - weight (weight): integer
              وزن دوره برای محاسبات مالی. هرچه بیشتر باشد، تأثیر بیشتری در محاسبات دارد. (الزامی)
              الزامی: بله
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع دوره به شمسی. (الزامی)
              الزامی: بله
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان دوره به شمسی. (الزامی)
              الزامی: بله
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع دوره به میلادی. (الزامی)
              الزامی: بله
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان دوره به میلادی. (الزامی)
              الزامی: بله
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Period/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if label is None: raise ValueError('label الزامی است')
        if label is not None and len(label) < 1: raise ValueError('label حداقل 1 کاراکتر باید باشد')
        if label is not None and len(label) > 50: raise ValueError('label حداکثر 50 کاراکتر می‌تواند باشد')
        if year is None: raise ValueError('year الزامی است')
        if month_number is None: raise ValueError('month_number الزامی است')
        if month_name is None: raise ValueError('month_name الزامی است')
        if month_name is not None and len(month_name) < 1: raise ValueError('month_name حداقل 1 کاراکتر باید باشد')
        if month_name is not None and len(month_name) > 20: raise ValueError('month_name حداکثر 20 کاراکتر می‌تواند باشد')
        if weight is None: raise ValueError('weight الزامی است')
        if start_date_shamsi is None: raise ValueError('start_date_shamsi الزامی است')
        if end_date_shamsi is None: raise ValueError('end_date_shamsi الزامی است')
        if start_date_gregorian is None: raise ValueError('start_date_gregorian الزامی است')
        if end_date_gregorian is None: raise ValueError('end_date_gregorian الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Period/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if label is not None:
            data['label'] = label
        if year is not None:
            data['year'] = year
        if month_number is not None:
            data['month_number'] = month_number
        if month_name is not None:
            data['month_name'] = month_name
        if weight is not None:
            data['weight'] = weight
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if project is not None:
            data['project'] = project
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_partial_update(id: int, label: Optional[str] = None, year: Optional[int] = None, month_number: Optional[int] = None, month_name: Optional[str] = None, weight: Optional[int] = None, start_date_shamsi: Optional[str] = None, end_date_shamsi: Optional[str] = None, start_date_gregorian: Optional[str] = None, end_date_gregorian: Optional[str] = None, project: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی دوره

    به‌روزرسانی جزئی دوره
    
    این متد امکان تغییر بخشی از فیلدهای دوره را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای دوره
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده دوره (status 200)
    
    مثال:
        PATCH /api/v1/Period/1/
        {
            "weight": 2
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این دوره را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - label (label): string
              عنوان دوره (مثال: "مهر 1403"). (الزامی)
              الزامی: خیر
            - year (year): integer
              سال شمسی دوره (مثال: 1403). (الزامی)
              الزامی: خیر
            - month_number (month_number): integer
              شماره ماه شمسی (1 تا 12). (الزامی)
              الزامی: خیر
            - month_name (month_name): string
              نام ماه شمسی (مثال: "مهر"). (الزامی)
              الزامی: خیر
            - weight (weight): integer
              وزن دوره برای محاسبات مالی. هرچه بیشتر باشد، تأثیر بیشتری در محاسبات دارد. (الزامی)
              الزامی: خیر
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع دوره به شمسی. (الزامی)
              الزامی: خیر
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان دوره به شمسی. (الزامی)
              الزامی: خیر
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع دوره به میلادی. (الزامی)
              الزامی: خیر
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان دوره به میلادی. (الزامی)
              الزامی: خیر
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Period/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if label is not None and len(label) < 1: raise ValueError('label حداقل 1 کاراکتر باید باشد')
        if label is not None and len(label) > 50: raise ValueError('label حداکثر 50 کاراکتر می‌تواند باشد')
        if month_name is not None and len(month_name) < 1: raise ValueError('month_name حداقل 1 کاراکتر باید باشد')
        if month_name is not None and len(month_name) > 20: raise ValueError('month_name حداکثر 20 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Period/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if label is not None:
            data['label'] = label
        if year is not None:
            data['year'] = year
        if month_number is not None:
            data['month_number'] = month_number
        if month_name is not None:
            data['month_name'] = month_name
        if weight is not None:
            data['weight'] = weight
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if project is not None:
            data['project'] = project
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_destroy(id: int, request=None) -> str:
    """
    حذف دوره

    حذف دوره
    
    این متد دوره را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای دوره
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Period/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط دوره‌های پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        - در صورت وجود وابستگی (هزینه‌ها، تراکنش‌ها)، ممکن است حذف ناموفق باشد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این دوره را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Period/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Period/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_chart_data_retrieve(request=None) -> str:
    """
    دریافت داده‌های دوره‌ای برای نمودارها (سرمایه، هزی...

    دریافت داده‌های دوره‌ای برای نمودارها (سرمایه، هزینه، فروش، مانده صندوق)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Period/chart_data/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Period/chart_data/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_summary_retrieve(request=None) -> str:
    """
    دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقا...

    دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقادیر تجمعی
    
    این endpoint خلاصه کامل تمام دوره‌های پروژه را با تمام اطلاعات مالی
    شامل آورده‌ها، برداشت‌ها، سرمایه خالص، سود، هزینه‌ها و فروش‌ها برمی‌گرداند.
    
    Returns:
        Response: شامل:
            - data: لیست خلاصه هر دوره
            - totals: مجموع‌های کلی
            - current: خلاصه دوره جاری
    
    نکات مهم:
    - فقط دوره‌های پروژه جاری را شامل می‌شود
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - دوره‌ها به ترتیب زمانی مرتب می‌شوند
    - تمام مبالغ به تومان هستند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Period/period_summary/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Period/period_summary/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for PettyCashTransaction (12 endpoint) =====

@tool
def pettycashtransaction_list(request=None) -> str:
    """
    دریافت لیست تمام تراکنش‌های تنخواه پروژه جاری

    دریافت لیست تمام تراکنش‌های تنخواه پروژه جاری
    
    این متد لیست تراکنش‌های تنخواه مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/PettyCashTransaction/?page=1&page_size=20
    
    نکات:
        - فقط تراکنش‌های تنخواه پروژه جاری برگردانده می‌شود
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_create(expense_type: str, transaction_type: str, amount: str, description: Optional[str] = None, receipt_number: Optional[str] = None, date_shamsi_input: Optional[str] = None, request=None) -> str:
    """
    ایجاد تراکنش تنخواه جدید برای پروژه جاری

    ایجاد تراکنش تنخواه جدید برای پروژه جاری
    
    این متد تراکنش تنخواه جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - expense_type (الزامی): عامل اجرایی (project_manager, facilities_manager, procurement, warehouse, construction_contractor, other)
        - transaction_type (الزامی): نوع تراکنش (receipt, return)
        - amount (الزامی): مبلغ تراکنش (به صورت string)
        - date_shamsi_input (اختیاری): تاریخ شمسی (YYYY-MM-DD)
        - description (اختیاری): توضیحات
        - receipt_number (اختیاری): شماره فیش/رسید
    
    Returns:
        Response با اطلاعات تراکنش تنخواه ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/PettyCashTransaction/
        {
            "expense_type": "project_manager",
            "transaction_type": "receipt",
            "amount": "10000000",
            "date_shamsi_input": "1403-07-15",
            "description": "دریافت تنخواه برای خرید مواد اولیه",
            "receipt_number": "F-12345"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - تاریخ میلادی به صورت خودکار محاسبه می‌شود
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - expense_type (نوع هزینه): string
              عامل اجرایی (نوع هزینه). مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: بله
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: receipt (دریافت تنخواه از صندوق به عامل اجرایی), return (عودت تنخواه از عامل اجرایی به صندوق). (الزامی)

* `receipt` - دریافت تنخواه
* `return` - عودت تنخواه
              الزامی: بله
            - amount (مبلغ): string
              مبلغ تراکنش به تومان (همیشه مثبت ذخیره می‌شود). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش تنخواه. (اختیاری)
              الزامی: خیر
            - receipt_number (receipt_number): string
              شماره فیش یا رسید تراکنش. (اختیاری)
              الزامی: خیر
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/PettyCashTransaction/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if expense_type is None: raise ValueError('نوع هزینه الزامی است')
        if transaction_type is None: raise ValueError('transaction_type الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if receipt_number is not None and len(receipt_number) > 100: raise ValueError('receipt_number حداکثر 100 کاراکتر می‌تواند باشد')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/'
        
        # ساخت data برای request body
        data = {}
        if expense_type is not None:
            data['expense_type'] = expense_type
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if receipt_number is not None:
            data['receipt_number'] = receipt_number
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک تراکنش تنخواه خاص

    دریافت جزئیات یک تراکنش تنخواه خاص
    
    این متد اطلاعات کامل تراکنش تنخواه با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش تنخواه
    
    Returns:
        Response با اطلاعات کامل تراکنش تنخواه شامل signed_amount
    
    مثال:
        GET /api/v1/PettyCashTransaction/1/
    
    نکات:
        - فقط تراکنش‌های تنخواه پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_update(id: int, expense_type: str, transaction_type: str, amount: str, description: Optional[str] = None, receipt_number: Optional[str] = None, date_shamsi_input: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی کامل تراکنش تنخواه

    به‌روزرسانی کامل تراکنش تنخواه
    
    این متد امکان تغییر همه فیلدهای یک تراکنش تنخواه را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش تنخواه
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده تراکنش تنخواه (status 200)
    
    مثال:
        PUT /api/v1/PettyCashTransaction/1/
        {
            "expense_type": "project_manager",
            "transaction_type": "receipt",
            "amount": "12000000",
            "description": "به‌روزرسانی شده"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - expense_type (نوع هزینه): string
              عامل اجرایی (نوع هزینه). مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: بله
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: receipt (دریافت تنخواه از صندوق به عامل اجرایی), return (عودت تنخواه از عامل اجرایی به صندوق). (الزامی)

* `receipt` - دریافت تنخواه
* `return` - عودت تنخواه
              الزامی: بله
            - amount (مبلغ): string
              مبلغ تراکنش به تومان (همیشه مثبت ذخیره می‌شود). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش تنخواه. (اختیاری)
              الزامی: خیر
            - receipt_number (receipt_number): string
              شماره فیش یا رسید تراکنش. (اختیاری)
              الزامی: خیر
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/PettyCashTransaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if expense_type is None: raise ValueError('نوع هزینه الزامی است')
        if transaction_type is None: raise ValueError('transaction_type الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if receipt_number is not None and len(receipt_number) > 100: raise ValueError('receipt_number حداکثر 100 کاراکتر می‌تواند باشد')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if expense_type is not None:
            data['expense_type'] = expense_type
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if receipt_number is not None:
            data['receipt_number'] = receipt_number
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_partial_update(id: int, expense_type: Optional[str] = None, transaction_type: Optional[str] = None, amount: Optional[str] = None, description: Optional[str] = None, receipt_number: Optional[str] = None, date_shamsi_input: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی تراکنش تنخواه

    به‌روزرسانی جزئی تراکنش تنخواه
    
    این متد امکان تغییر بخشی از فیلدهای تراکنش تنخواه را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش تنخواه
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده تراکنش تنخواه (status 200)
    
    مثال:
        PATCH /api/v1/PettyCashTransaction/1/
        {
            "amount": "12000000"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - expense_type (نوع هزینه): string
              عامل اجرایی (نوع هزینه). مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
              الزامی: خیر
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: receipt (دریافت تنخواه از صندوق به عامل اجرایی), return (عودت تنخواه از عامل اجرایی به صندوق). (الزامی)

* `receipt` - دریافت تنخواه
* `return` - عودت تنخواه
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ تراکنش به تومان (همیشه مثبت ذخیره می‌شود). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش تنخواه. (اختیاری)
              الزامی: خیر
            - receipt_number (receipt_number): string
              شماره فیش یا رسید تراکنش. (اختیاری)
              الزامی: خیر
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/PettyCashTransaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if receipt_number is not None and len(receipt_number) > 100: raise ValueError('receipt_number حداکثر 100 کاراکتر می‌تواند باشد')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if expense_type is not None:
            data['expense_type'] = expense_type
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        if receipt_number is not None:
            data['receipt_number'] = receipt_number
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_destroy(id: int, request=None) -> str:
    """
    حذف تراکنش تنخواه

    حذف تراکنش تنخواه
    
    این متد تراکنش تنخواه را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش تنخواه
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/PettyCashTransaction/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط تراکنش‌های تنخواه پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/PettyCashTransaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_balance_detail_retrieve(request=None) -> str:
    """
    دریافت وضعیت مالی یک عامل اجرایی خاص

    دریافت وضعیت مالی یک عامل اجرایی خاص
    
    این endpoint وضعیت مالی کامل یک عامل اجرایی (expense_type) را
    شامل مانده، مجموع دریافت‌ها، هزینه‌ها و مرجوعی‌ها برمی‌گرداند.
    
    Parameters:
        expense_type (str): نوع عامل اجرایی (الزامی)
    
    Returns:
        Response: شامل:
            - expense_type: نوع عامل اجرایی
            - expense_type_label: برچسب نوع عامل
            - balance: مانده فعلی
            - total_receipts: مجموع دریافت‌ها
            - total_expenses: مجموع هزینه‌ها
            - total_returns: مجموع مرجوعی‌ها
    
    نکات مهم:
    - فقط تراکنش‌های پروژه جاری را شامل می‌شود
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - اگر expense_type ارسال نشود، خطای 400 برمی‌گرداند
    - مانده مثبت = بدهکار (پول در دست دارد)
    - مانده منفی = بستانکار (بدهکار است)
    - تمام مبالغ به تومان هستند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/balance_detail/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/balance_detail/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_balance_trend_retrieve(request=None) -> str:
    """
    ترند زمانی وضعیت مالی عامل اجرایی

    ترند زمانی وضعیت مالی عامل اجرایی

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/balance_trend/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/balance_trend/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_balances_retrieve(request=None) -> str:
    """
    دریافت وضعیت مالی همه عوامل اجرایی

    دریافت وضعیت مالی همه عوامل اجرایی

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/balances/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/balances/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_detailed_report_retrieve(request=None) -> str:
    """
    گزارش تفصیلی تراکنش‌های تنخواه با فیلتر و جستجو

    گزارش تفصیلی تراکنش‌های تنخواه با فیلتر و جستجو

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/detailed_report/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/detailed_report/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_period_balance_retrieve(request=None) -> str:
    """
    دریافت وضعیت مالی عامل اجرایی در یک دوره

    دریافت وضعیت مالی عامل اجرایی در یک دوره

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/period_balance/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/period_balance/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_statistics_retrieve(request=None) -> str:
    """
    آمار کلی تراکنش‌های تنخواه (Single Source of Truth...

    آمار کلی تراکنش‌های تنخواه (Single Source of Truth)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/PettyCashTransaction/statistics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/PettyCashTransaction/statistics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Project (16 endpoint) =====

@tool
def project_list(request=None) -> str:
    """
    دریافت لیست تمام پروژه‌ها

    دریافت لیست تمام پروژه‌ها
    
    این متد لیست تمام پروژه‌های موجود را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Project/?page=1&page_size=10
    
    نکات:
        - تمام پروژه‌ها برگردانده می‌شوند
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_create(name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, gradient_primary_color: Optional[str] = None, gradient_secondary_color: Optional[str] = None, request=None) -> str:
    """
    ایجاد پروژه جدید

    ایجاد پروژه جدید
    
    این متد پروژه جدید را ثبت می‌کند.
    
    Request Body:
        - name (الزامی): نام پروژه
        - start_date_shamsi (الزامی): تاریخ شروع شمسی
        - end_date_shamsi (الزامی): تاریخ پایان شمسی
        - start_date_gregorian (الزامی): تاریخ شروع میلادی
        - end_date_gregorian (الزامی): تاریخ پایان میلادی
        - total_infrastructure (اختیاری): زیر بنای کل
        - correction_factor (اختیاری): ضریب اصلاحی
        - construction_contractor_percentage (اختیاری): درصد پیمان ساخت
        - description (اختیاری): توضیحات
        - color (اختیاری): رنگ پروژه
        - icon (اختیاری): آیکون پروژه
    
    Returns:
        Response با اطلاعات پروژه ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Project/
        {
            "name": "پروژه ساختمانی نمونه",
            "start_date_shamsi": "1403-01-01",
            "end_date_shamsi": "1405-12-29",
            "start_date_gregorian": "2024-03-20",
            "end_date_gregorian": "2027-03-19",
            "total_infrastructure": "5000.00",
            "correction_factor": "1.0000000000"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - name (نام): string
              نام پروژه ساختمانی. (الزامی)
              الزامی: بله
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع پروژه به شمسی. (الزامی)
              الزامی: بله
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان پروژه به شمسی. (الزامی)
              الزامی: بله
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع پروژه به میلادی. (الزامی)
              الزامی: بله
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان پروژه به میلادی. (الزامی)
              الزامی: بله
            - total_infrastructure (total_infrastructure): string
              زیر بنای کل پروژه به متر مربع. (پیش‌فرض: 0.00)
              الزامی: خیر
            - correction_factor (correction_factor): string
              ضریب اصلاحی برای محاسبات پروژه. (پیش‌فرض: 1.0000000000)
              الزامی: خیر
            - construction_contractor_percentage (construction_contractor_percentage): string
              درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%). (پیش‌فرض: 0.100)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات اضافی درباره پروژه. (اختیاری)
              الزامی: خیر
            - color (color): string
              رنگ نمایش پروژه (فرمت HEX، مثال: #667eea). (پیش‌فرض: #667eea)
              الزامی: خیر
            - icon (icon): string
              نام کلاس آیکون Font Awesome (مثال: fa-building). (پیش‌فرض: fa-building)
              الزامی: خیر
            - gradient_primary_color (gradient_primary_color): string
              رنگ اول گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #667eea)
              الزامی: خیر
            - gradient_secondary_color (gradient_secondary_color): string
              رنگ دوم گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #764ba2)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Project/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if name is None: raise ValueError('نام الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if start_date_shamsi is None: raise ValueError('start_date_shamsi الزامی است')
        if end_date_shamsi is None: raise ValueError('end_date_shamsi الزامی است')
        if start_date_gregorian is None: raise ValueError('start_date_gregorian الزامی است')
        if end_date_gregorian is None: raise ValueError('end_date_gregorian الزامی است')
        if total_infrastructure is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_infrastructure)): raise ValueError('total_infrastructure فرمت نامعتبر است')
        if correction_factor is not None and not re.match(r'^-?\d{0,10}(?:\.\d{0,10})?$', str(correction_factor)): raise ValueError('correction_factor فرمت نامعتبر است')
        if construction_contractor_percentage is not None and not re.match(r'^-?\d{0,3}(?:\.\d{0,3})?$', str(construction_contractor_percentage)): raise ValueError('construction_contractor_percentage فرمت نامعتبر است')
        if color is not None and len(color) < 1: raise ValueError('color حداقل 1 کاراکتر باید باشد')
        if color is not None and len(color) > 7: raise ValueError('color حداکثر 7 کاراکتر می‌تواند باشد')
        if icon is not None and len(icon) < 1: raise ValueError('icon حداقل 1 کاراکتر باید باشد')
        if icon is not None and len(icon) > 50: raise ValueError('icon حداکثر 50 کاراکتر می‌تواند باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) < 1: raise ValueError('gradient_primary_color حداقل 1 کاراکتر باید باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) > 7: raise ValueError('gradient_primary_color حداکثر 7 کاراکتر می‌تواند باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) < 1: raise ValueError('gradient_secondary_color حداقل 1 کاراکتر باید باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) > 7: raise ValueError('gradient_secondary_color حداکثر 7 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Project/'
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if total_infrastructure is not None:
            data['total_infrastructure'] = total_infrastructure
        if correction_factor is not None:
            data['correction_factor'] = correction_factor
        if construction_contractor_percentage is not None:
            data['construction_contractor_percentage'] = construction_contractor_percentage
        if description is not None:
            data['description'] = description
        if color is not None:
            data['color'] = color
        if icon is not None:
            data['icon'] = icon
        if gradient_primary_color is not None:
            data['gradient_primary_color'] = gradient_primary_color
        if gradient_secondary_color is not None:
            data['gradient_secondary_color'] = gradient_secondary_color
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک پروژه خاص

    دریافت جزئیات یک پروژه خاص
    
    این متد اطلاعات کامل پروژه با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای پروژه
    
    Returns:
        Response با اطلاعات کامل پروژه
    
    مثال:
        GET /api/v1/Project/1/
    
    نکات:
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Project/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_update(id: int, name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, gradient_primary_color: Optional[str] = None, gradient_secondary_color: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی کامل پروژه

    به‌روزرسانی کامل پروژه
    
    این متد امکان تغییر همه فیلدهای یک پروژه را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای پروژه
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده پروژه (status 200)
    
    مثال:
        PUT /api/v1/Project/1/
        {
            "name": "پروژه به‌روزرسانی شده",
            "start_date_shamsi": "1403-01-01",
            "end_date_shamsi": "1405-12-29"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - name (نام): string
              نام پروژه ساختمانی. (الزامی)
              الزامی: بله
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع پروژه به شمسی. (الزامی)
              الزامی: بله
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان پروژه به شمسی. (الزامی)
              الزامی: بله
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع پروژه به میلادی. (الزامی)
              الزامی: بله
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان پروژه به میلادی. (الزامی)
              الزامی: بله
            - total_infrastructure (total_infrastructure): string
              زیر بنای کل پروژه به متر مربع. (پیش‌فرض: 0.00)
              الزامی: خیر
            - correction_factor (correction_factor): string
              ضریب اصلاحی برای محاسبات پروژه. (پیش‌فرض: 1.0000000000)
              الزامی: خیر
            - construction_contractor_percentage (construction_contractor_percentage): string
              درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%). (پیش‌فرض: 0.100)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات اضافی درباره پروژه. (اختیاری)
              الزامی: خیر
            - color (color): string
              رنگ نمایش پروژه (فرمت HEX، مثال: #667eea). (پیش‌فرض: #667eea)
              الزامی: خیر
            - icon (icon): string
              نام کلاس آیکون Font Awesome (مثال: fa-building). (پیش‌فرض: fa-building)
              الزامی: خیر
            - gradient_primary_color (gradient_primary_color): string
              رنگ اول گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #667eea)
              الزامی: خیر
            - gradient_secondary_color (gradient_secondary_color): string
              رنگ دوم گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #764ba2)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Project/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if name is None: raise ValueError('نام الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if start_date_shamsi is None: raise ValueError('start_date_shamsi الزامی است')
        if end_date_shamsi is None: raise ValueError('end_date_shamsi الزامی است')
        if start_date_gregorian is None: raise ValueError('start_date_gregorian الزامی است')
        if end_date_gregorian is None: raise ValueError('end_date_gregorian الزامی است')
        if total_infrastructure is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_infrastructure)): raise ValueError('total_infrastructure فرمت نامعتبر است')
        if correction_factor is not None and not re.match(r'^-?\d{0,10}(?:\.\d{0,10})?$', str(correction_factor)): raise ValueError('correction_factor فرمت نامعتبر است')
        if construction_contractor_percentage is not None and not re.match(r'^-?\d{0,3}(?:\.\d{0,3})?$', str(construction_contractor_percentage)): raise ValueError('construction_contractor_percentage فرمت نامعتبر است')
        if color is not None and len(color) < 1: raise ValueError('color حداقل 1 کاراکتر باید باشد')
        if color is not None and len(color) > 7: raise ValueError('color حداکثر 7 کاراکتر می‌تواند باشد')
        if icon is not None and len(icon) < 1: raise ValueError('icon حداقل 1 کاراکتر باید باشد')
        if icon is not None and len(icon) > 50: raise ValueError('icon حداکثر 50 کاراکتر می‌تواند باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) < 1: raise ValueError('gradient_primary_color حداقل 1 کاراکتر باید باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) > 7: raise ValueError('gradient_primary_color حداکثر 7 کاراکتر می‌تواند باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) < 1: raise ValueError('gradient_secondary_color حداقل 1 کاراکتر باید باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) > 7: raise ValueError('gradient_secondary_color حداکثر 7 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Project/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if total_infrastructure is not None:
            data['total_infrastructure'] = total_infrastructure
        if correction_factor is not None:
            data['correction_factor'] = correction_factor
        if construction_contractor_percentage is not None:
            data['construction_contractor_percentage'] = construction_contractor_percentage
        if description is not None:
            data['description'] = description
        if color is not None:
            data['color'] = color
        if icon is not None:
            data['icon'] = icon
        if gradient_primary_color is not None:
            data['gradient_primary_color'] = gradient_primary_color
        if gradient_secondary_color is not None:
            data['gradient_secondary_color'] = gradient_secondary_color
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_partial_update(id: int, name: Optional[str] = None, start_date_shamsi: Optional[str] = None, end_date_shamsi: Optional[str] = None, start_date_gregorian: Optional[str] = None, end_date_gregorian: Optional[str] = None, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, gradient_primary_color: Optional[str] = None, gradient_secondary_color: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی پروژه

    به‌روزرسانی جزئی پروژه
    
    این متد امکان تغییر بخشی از فیلدهای پروژه را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای پروژه
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده پروژه (status 200)
    
    مثال:
        PATCH /api/v1/Project/1/
        {
            "name": "نام جدید پروژه"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - name (نام): string
              نام پروژه ساختمانی. (الزامی)
              الزامی: خیر
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع پروژه به شمسی. (الزامی)
              الزامی: خیر
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان پروژه به شمسی. (الزامی)
              الزامی: خیر
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع پروژه به میلادی. (الزامی)
              الزامی: خیر
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان پروژه به میلادی. (الزامی)
              الزامی: خیر
            - total_infrastructure (total_infrastructure): string
              زیر بنای کل پروژه به متر مربع. (پیش‌فرض: 0.00)
              الزامی: خیر
            - correction_factor (correction_factor): string
              ضریب اصلاحی برای محاسبات پروژه. (پیش‌فرض: 1.0000000000)
              الزامی: خیر
            - construction_contractor_percentage (construction_contractor_percentage): string
              درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%). (پیش‌فرض: 0.100)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات اضافی درباره پروژه. (اختیاری)
              الزامی: خیر
            - color (color): string
              رنگ نمایش پروژه (فرمت HEX، مثال: #667eea). (پیش‌فرض: #667eea)
              الزامی: خیر
            - icon (icon): string
              نام کلاس آیکون Font Awesome (مثال: fa-building). (پیش‌فرض: fa-building)
              الزامی: خیر
            - gradient_primary_color (gradient_primary_color): string
              رنگ اول گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #667eea)
              الزامی: خیر
            - gradient_secondary_color (gradient_secondary_color): string
              رنگ دوم گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #764ba2)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Project/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if total_infrastructure is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_infrastructure)): raise ValueError('total_infrastructure فرمت نامعتبر است')
        if correction_factor is not None and not re.match(r'^-?\d{0,10}(?:\.\d{0,10})?$', str(correction_factor)): raise ValueError('correction_factor فرمت نامعتبر است')
        if construction_contractor_percentage is not None and not re.match(r'^-?\d{0,3}(?:\.\d{0,3})?$', str(construction_contractor_percentage)): raise ValueError('construction_contractor_percentage فرمت نامعتبر است')
        if color is not None and len(color) < 1: raise ValueError('color حداقل 1 کاراکتر باید باشد')
        if color is not None and len(color) > 7: raise ValueError('color حداکثر 7 کاراکتر می‌تواند باشد')
        if icon is not None and len(icon) < 1: raise ValueError('icon حداقل 1 کاراکتر باید باشد')
        if icon is not None and len(icon) > 50: raise ValueError('icon حداکثر 50 کاراکتر می‌تواند باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) < 1: raise ValueError('gradient_primary_color حداقل 1 کاراکتر باید باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) > 7: raise ValueError('gradient_primary_color حداکثر 7 کاراکتر می‌تواند باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) < 1: raise ValueError('gradient_secondary_color حداقل 1 کاراکتر باید باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) > 7: raise ValueError('gradient_secondary_color حداکثر 7 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Project/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if total_infrastructure is not None:
            data['total_infrastructure'] = total_infrastructure
        if correction_factor is not None:
            data['correction_factor'] = correction_factor
        if construction_contractor_percentage is not None:
            data['construction_contractor_percentage'] = construction_contractor_percentage
        if description is not None:
            data['description'] = description
        if color is not None:
            data['color'] = color
        if icon is not None:
            data['icon'] = icon
        if gradient_primary_color is not None:
            data['gradient_primary_color'] = gradient_primary_color
        if gradient_secondary_color is not None:
            data['gradient_secondary_color'] = gradient_secondary_color
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_destroy(id: int, request=None) -> str:
    """
    حذف پروژه

    حذف پروژه
    
    این متد پروژه را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای پروژه
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Project/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        - در صورت وجود وابستگی (هزینه‌ها، تراکنش‌ها، واحدها)، ممکن است حذف ناموفق باشد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Project/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Project/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_active_retrieve(request=None) -> str:
    """
    دریافت پروژه جاری (از session)

    دریافت پروژه جاری (از session)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/active/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/active/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_comprehensive_analysis_retrieve(request=None) -> str:
    """
    دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی

    دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/comprehensive_analysis/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/comprehensive_analysis/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_cost_metrics_retrieve(request=None) -> str:
    """
    دریافت متریک‌های هزینه

    دریافت متریک‌های هزینه

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/cost_metrics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/cost_metrics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_current_retrieve(request=None) -> str:
    """
    دریافت پروژه جاری کاربر از session

    دریافت پروژه جاری کاربر از session

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/current/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/current/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_profit_metrics_retrieve(request=None) -> str:
    """
    دریافت متریک‌های سود (کل، سالانه، ماهانه، روزانه)

    دریافت متریک‌های سود (کل، سالانه، ماهانه، روزانه)
    
    این endpoint متریک‌های مختلف سود شامل سود کل، سالانه، ماهانه و روزانه
    را برای پروژه محاسبه و برمی‌گرداند.
    
    Parameters:
        project_id (int, optional): شناسه پروژه (از query parameter یا پروژه جاری)
    
    Returns:
        Response: شامل متریک‌های سود
    
    نکات مهم:
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - محاسبات بر اساس تاریخ شروع و پایان پروژه انجام می‌شود
    - مبالغ به تومان هستند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/profit_metrics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/profit_metrics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_statistics_detailed_retrieve(request=None) -> str:
    """
    دریافت آمار تفصیلی پروژه

    دریافت آمار تفصیلی پروژه

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/project_statistics_detailed/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/project_statistics_detailed/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_timeline_retrieve(request=None) -> str:
    """
    محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ ام...

    محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ امروز

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/project_timeline/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/project_timeline/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_set_active_create(name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, gradient_primary_color: Optional[str] = None, gradient_secondary_color: Optional[str] = None, request=None) -> str:
    """
    تنظیم پروژه فعال

    تنظیم پروژه فعال

    پارامترهای درخواست:

        * بدنه (Request Body):
            - name (نام): string
              نام پروژه ساختمانی. (الزامی)
              الزامی: بله
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع پروژه به شمسی. (الزامی)
              الزامی: بله
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان پروژه به شمسی. (الزامی)
              الزامی: بله
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع پروژه به میلادی. (الزامی)
              الزامی: بله
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان پروژه به میلادی. (الزامی)
              الزامی: بله
            - total_infrastructure (total_infrastructure): string
              زیر بنای کل پروژه به متر مربع. (پیش‌فرض: 0.00)
              الزامی: خیر
            - correction_factor (correction_factor): string
              ضریب اصلاحی برای محاسبات پروژه. (پیش‌فرض: 1.0000000000)
              الزامی: خیر
            - construction_contractor_percentage (construction_contractor_percentage): string
              درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%). (پیش‌فرض: 0.100)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات اضافی درباره پروژه. (اختیاری)
              الزامی: خیر
            - color (color): string
              رنگ نمایش پروژه (فرمت HEX، مثال: #667eea). (پیش‌فرض: #667eea)
              الزامی: خیر
            - icon (icon): string
              نام کلاس آیکون Font Awesome (مثال: fa-building). (پیش‌فرض: fa-building)
              الزامی: خیر
            - gradient_primary_color (gradient_primary_color): string
              رنگ اول گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #667eea)
              الزامی: خیر
            - gradient_secondary_color (gradient_secondary_color): string
              رنگ دوم گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #764ba2)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Project/set_active/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if name is None: raise ValueError('نام الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if start_date_shamsi is None: raise ValueError('start_date_shamsi الزامی است')
        if end_date_shamsi is None: raise ValueError('end_date_shamsi الزامی است')
        if start_date_gregorian is None: raise ValueError('start_date_gregorian الزامی است')
        if end_date_gregorian is None: raise ValueError('end_date_gregorian الزامی است')
        if total_infrastructure is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_infrastructure)): raise ValueError('total_infrastructure فرمت نامعتبر است')
        if correction_factor is not None and not re.match(r'^-?\d{0,10}(?:\.\d{0,10})?$', str(correction_factor)): raise ValueError('correction_factor فرمت نامعتبر است')
        if construction_contractor_percentage is not None and not re.match(r'^-?\d{0,3}(?:\.\d{0,3})?$', str(construction_contractor_percentage)): raise ValueError('construction_contractor_percentage فرمت نامعتبر است')
        if color is not None and len(color) < 1: raise ValueError('color حداقل 1 کاراکتر باید باشد')
        if color is not None and len(color) > 7: raise ValueError('color حداکثر 7 کاراکتر می‌تواند باشد')
        if icon is not None and len(icon) < 1: raise ValueError('icon حداقل 1 کاراکتر باید باشد')
        if icon is not None and len(icon) > 50: raise ValueError('icon حداکثر 50 کاراکتر می‌تواند باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) < 1: raise ValueError('gradient_primary_color حداقل 1 کاراکتر باید باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) > 7: raise ValueError('gradient_primary_color حداکثر 7 کاراکتر می‌تواند باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) < 1: raise ValueError('gradient_secondary_color حداقل 1 کاراکتر باید باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) > 7: raise ValueError('gradient_secondary_color حداکثر 7 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Project/set_active/'
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if total_infrastructure is not None:
            data['total_infrastructure'] = total_infrastructure
        if correction_factor is not None:
            data['correction_factor'] = correction_factor
        if construction_contractor_percentage is not None:
            data['construction_contractor_percentage'] = construction_contractor_percentage
        if description is not None:
            data['description'] = description
        if color is not None:
            data['color'] = color
        if icon is not None:
            data['icon'] = icon
        if gradient_primary_color is not None:
            data['gradient_primary_color'] = gradient_primary_color
        if gradient_secondary_color is not None:
            data['gradient_secondary_color'] = gradient_secondary_color
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار کامل پروژه جاری شامل اطلاعات پروژه و آ...

    دریافت آمار کامل پروژه جاری شامل اطلاعات پروژه و آمار واحدها

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Project/statistics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Project/statistics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_switch_create(name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, gradient_primary_color: Optional[str] = None, gradient_secondary_color: Optional[str] = None, request=None) -> str:
    """
    تغییر پروژه جاری کاربر

    تغییر پروژه جاری کاربر

    پارامترهای درخواست:

        * بدنه (Request Body):
            - name (نام): string
              نام پروژه ساختمانی. (الزامی)
              الزامی: بله
            - start_date_shamsi (start_date_shamsi): string
              تاریخ شروع پروژه به شمسی. (الزامی)
              الزامی: بله
            - end_date_shamsi (end_date_shamsi): string
              تاریخ پایان پروژه به شمسی. (الزامی)
              الزامی: بله
            - start_date_gregorian (start_date_gregorian): string
              تاریخ شروع پروژه به میلادی. (الزامی)
              الزامی: بله
            - end_date_gregorian (end_date_gregorian): string
              تاریخ پایان پروژه به میلادی. (الزامی)
              الزامی: بله
            - total_infrastructure (total_infrastructure): string
              زیر بنای کل پروژه به متر مربع. (پیش‌فرض: 0.00)
              الزامی: خیر
            - correction_factor (correction_factor): string
              ضریب اصلاحی برای محاسبات پروژه. (پیش‌فرض: 1.0000000000)
              الزامی: خیر
            - construction_contractor_percentage (construction_contractor_percentage): string
              درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%). (پیش‌فرض: 0.100)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات اضافی درباره پروژه. (اختیاری)
              الزامی: خیر
            - color (color): string
              رنگ نمایش پروژه (فرمت HEX، مثال: #667eea). (پیش‌فرض: #667eea)
              الزامی: خیر
            - icon (icon): string
              نام کلاس آیکون Font Awesome (مثال: fa-building). (پیش‌فرض: fa-building)
              الزامی: خیر
            - gradient_primary_color (gradient_primary_color): string
              رنگ اول گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #667eea)
              الزامی: خیر
            - gradient_secondary_color (gradient_secondary_color): string
              رنگ دوم گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #764ba2)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Project/switch/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if name is None: raise ValueError('نام الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if start_date_shamsi is None: raise ValueError('start_date_shamsi الزامی است')
        if end_date_shamsi is None: raise ValueError('end_date_shamsi الزامی است')
        if start_date_gregorian is None: raise ValueError('start_date_gregorian الزامی است')
        if end_date_gregorian is None: raise ValueError('end_date_gregorian الزامی است')
        if total_infrastructure is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_infrastructure)): raise ValueError('total_infrastructure فرمت نامعتبر است')
        if correction_factor is not None and not re.match(r'^-?\d{0,10}(?:\.\d{0,10})?$', str(correction_factor)): raise ValueError('correction_factor فرمت نامعتبر است')
        if construction_contractor_percentage is not None and not re.match(r'^-?\d{0,3}(?:\.\d{0,3})?$', str(construction_contractor_percentage)): raise ValueError('construction_contractor_percentage فرمت نامعتبر است')
        if color is not None and len(color) < 1: raise ValueError('color حداقل 1 کاراکتر باید باشد')
        if color is not None and len(color) > 7: raise ValueError('color حداکثر 7 کاراکتر می‌تواند باشد')
        if icon is not None and len(icon) < 1: raise ValueError('icon حداقل 1 کاراکتر باید باشد')
        if icon is not None and len(icon) > 50: raise ValueError('icon حداکثر 50 کاراکتر می‌تواند باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) < 1: raise ValueError('gradient_primary_color حداقل 1 کاراکتر باید باشد')
        if gradient_primary_color is not None and len(gradient_primary_color) > 7: raise ValueError('gradient_primary_color حداکثر 7 کاراکتر می‌تواند باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) < 1: raise ValueError('gradient_secondary_color حداقل 1 کاراکتر باید باشد')
        if gradient_secondary_color is not None and len(gradient_secondary_color) > 7: raise ValueError('gradient_secondary_color حداکثر 7 کاراکتر می‌تواند باشد')
        # ساخت URL کامل
        url = '/api/v1/Project/switch/'
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if start_date_shamsi is not None:
            data['start_date_shamsi'] = start_date_shamsi
        if end_date_shamsi is not None:
            data['end_date_shamsi'] = end_date_shamsi
        if start_date_gregorian is not None:
            data['start_date_gregorian'] = start_date_gregorian
        if end_date_gregorian is not None:
            data['end_date_gregorian'] = end_date_gregorian
        if total_infrastructure is not None:
            data['total_infrastructure'] = total_infrastructure
        if correction_factor is not None:
            data['correction_factor'] = correction_factor
        if construction_contractor_percentage is not None:
            data['construction_contractor_percentage'] = construction_contractor_percentage
        if description is not None:
            data['description'] = description
        if color is not None:
            data['color'] = color
        if icon is not None:
            data['icon'] = icon
        if gradient_primary_color is not None:
            data['gradient_primary_color'] = gradient_primary_color
        if gradient_secondary_color is not None:
            data['gradient_secondary_color'] = gradient_secondary_color
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Sale (7 endpoint) =====

@tool
def sale_list(request=None) -> str:
    """
    دریافت لیست تمام فروش/مرجوعی‌های پروژه جاری

    دریافت لیست تمام فروش/مرجوعی‌های پروژه جاری
    
    این متد لیست فروش/مرجوعی‌های مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Sale/?page=1&page_size=20
    
    نکات:
        - فقط فروش/مرجوعی‌های پروژه جاری برگردانده می‌شود
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Sale/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Sale/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_create(period: int, amount: str, project: Optional[int] = None, description: Optional[str] = None, request=None) -> str:
    """
    ایجاد فروش/مرجوعی جدید برای پروژه جاری

    ایجاد فروش/مرجوعی جدید برای پروژه جاری
    
    این متد فروش/مرجوعی جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - period (الزامی): شناسه دوره
        - amount (الزامی): مبلغ فروش/مرجوعی (به صورت string)
        - description (اختیاری): توضیحات
    
    Returns:
        Response با اطلاعات فروش/مرجوعی ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Sale/
        {
            "period": 1,
            "amount": "100000000",
            "description": "فروش واحد 101"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که فروش/مرجوعی برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: بله
            - amount (مبلغ): string
              مبلغ فروش/مرجوعی به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره فروش/مرجوعی. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Sale/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if period is None: raise ValueError('دوره الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Sale/'
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if period is not None:
            data['period'] = period
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک فروش/مرجوعی خاص

    دریافت جزئیات یک فروش/مرجوعی خاص
    
    این متد اطلاعات کامل فروش/مرجوعی با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای فروش/مرجوعی
    
    Returns:
        Response با اطلاعات کامل فروش/مرجوعی شامل project_data و period_data
    
    مثال:
        GET /api/v1/Sale/1/
    
    نکات:
        - فقط فروش/مرجوعی‌های پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Sale/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Sale/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_update(id: int, period: int, amount: str, project: Optional[int] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی کامل فروش/مرجوعی

    به‌روزرسانی کامل فروش/مرجوعی
    
    این متد امکان تغییر همه فیلدهای یک فروش/مرجوعی را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای فروش/مرجوعی
    
    Request Body:
        - تمام فیلدهای قابل ویرایش (period, amount, description)
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده فروش/مرجوعی (status 200)
    
    مثال:
        PUT /api/v1/Sale/1/
        {
            "period": 1,
            "amount": "120000000",
            "description": "فروش واحد 101 - به‌روزرسانی شده"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که فروش/مرجوعی برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: بله
            - amount (مبلغ): string
              مبلغ فروش/مرجوعی به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره فروش/مرجوعی. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Sale/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if period is None: raise ValueError('دوره الزامی است')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Sale/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if period is not None:
            data['period'] = period
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_partial_update(id: int, project: Optional[int] = None, period: Optional[int] = None, amount: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی فروش/مرجوعی

    به‌روزرسانی جزئی فروش/مرجوعی
    
    این متد امکان تغییر بخشی از فیلدهای فروش/مرجوعی را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای فروش/مرجوعی
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده فروش/مرجوعی (status 200)
    
    مثال:
        PATCH /api/v1/Sale/1/
        {
            "amount": "120000000"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره‌ای که فروش/مرجوعی برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ فروش/مرجوعی به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره فروش/مرجوعی. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Sale/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Sale/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if period is not None:
            data['period'] = period
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_destroy(id: int, request=None) -> str:
    """
    حذف فروش/مرجوعی

    حذف فروش/مرجوعی
    
    این متد فروش/مرجوعی را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای فروش/مرجوعی
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Sale/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط فروش/مرجوعی‌های پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Sale/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Sale/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_total_sales_retrieve(request=None) -> str:
    """
    دریافت مجموع فروش‌ها

    دریافت مجموع فروش‌ها

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Sale/total_sales/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Sale/total_sales/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Transaction (11 endpoint) =====

@tool
def transaction_list(investor: Optional[int] = None, period: Optional[int] = None, project: Optional[int] = None, transaction_type: Optional[str] = None, request=None) -> str:
    """
    دریافت لیست تمام تراکنش‌های پروژه جاری

    دریافت لیست تمام تراکنش‌های پروژه جاری
    
    این متد لیست تراکنش‌های مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل فیلتر و مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
        - investor: فیلتر بر اساس شناسه سرمایه‌گذار
        - period: فیلتر بر اساس شناسه دوره
        - transaction_type: فیلتر بر اساس نوع تراکنش
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Transaction/?investor=1&transaction_type=principal_deposit
    
    نکات:
        - فقط تراکنش‌های پروژه جاری برگردانده می‌شود
        - امکان فیلتر بر اساس سرمایه‌گذار، دوره و نوع تراکنش
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * کوئری (Query String):
            - investor (سرمایه‌گذار): integer
              الزامی: خیر
            - period (دوره): integer
              الزامی: خیر
            - project (پروژه): integer
              الزامی: خیر
            - transaction_type (transaction_type): string
              * `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
              الزامی: خیر
              مقادیر معتبر: loan_deposit, principal_deposit, principal_withdrawal, profit_accrual

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Transaction/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if transaction_type is not None and transaction_type not in ['loan_deposit', 'principal_deposit', 'principal_withdrawal', 'profit_accrual']: raise ValueError('transaction_type باید یکی از این باشد: loan_deposit', 'principal_deposit', 'principal_withdrawal', 'profit_accrual')
        # ساخت URL کامل
        url = '/api/v1/Transaction/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}
        if investor is not None:
            kwargs['investor'] = investor
        if period is not None:
            kwargs['period'] = period
        if project is not None:
            kwargs['project'] = project
        if transaction_type is not None:
            kwargs['transaction_type'] = transaction_type
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_create(amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    ایجاد تراکنش جدید برای پروژه جاری

    ایجاد تراکنش جدید برای پروژه جاری
    
    این متد تراکنش جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - investor/investor_id (الزامی): شناسه سرمایه‌گذار
        - period/period_id (الزامی): شناسه دوره
        - date_shamsi_input یا date_shamsi_raw (الزامی): تاریخ شمسی
        - amount (الزامی): مبلغ تراکنش (به صورت string)
        - transaction_type (الزامی): نوع تراکنش
        - description (اختیاری): توضیحات
    
    Returns:
        Response با اطلاعات تراکنش ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Transaction/
        {
            "investor": 1,
            "period": 1,
            "date_shamsi_input": "1403-07-15",
            "amount": "50000000",
            "transaction_type": "principal_deposit",
            "description": "آورده اولیه"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - روز مانده و روز از شروع به صورت خودکار محاسبه می‌شوند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - date_shamsi_raw (date_shamsi_raw): string
              تاریخ شمسی خام برای دریافت مستقیم از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ تراکنش به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: principal_deposit (آورده), loan_deposit (آورده وام), principal_withdrawal (خروج از سرمایه), profit_accrual (سود). (الزامی)

* `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش. (اختیاری)
              الزامی: خیر
            - investor (سرمایه‌گذار): integer
              شناسه سرمایه‌گذار (جایگزین investor_id). (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره (جایگزین period_id). (اختیاری)
              الزامی: خیر
            - investor_id (investor_id): integer
              شناسه سرمایه‌گذار. می‌تواند از investor یا investor_id استفاده شود. (اختیاری)
              الزامی: خیر
            - period_id (period_id): integer
              شناسه دوره. می‌تواند از period یا period_id استفاده شود. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Transaction/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if date_shamsi_raw is not None and len(date_shamsi_raw) < 1: raise ValueError('date_shamsi_raw حداقل 1 کاراکتر باید باشد')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if transaction_type is None: raise ValueError('transaction_type الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/'
        
        # ساخت data برای request body
        data = {}
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if date_shamsi_raw is not None:
            data['date_shamsi_raw'] = date_shamsi_raw
        if amount is not None:
            data['amount'] = amount
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if description is not None:
            data['description'] = description
        if investor is not None:
            data['investor'] = investor
        if period is not None:
            data['period'] = period
        if investor_id is not None:
            data['investor_id'] = investor_id
        if period_id is not None:
            data['period_id'] = period_id
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک تراکنش خاص

    دریافت جزئیات یک تراکنش خاص
    
    این متد اطلاعات کامل تراکنش با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش
    
    Returns:
        Response با اطلاعات کامل تراکنش شامل investor_data, period_data, project_data
    
    مثال:
        GET /api/v1/Transaction/1/
    
    نکات:
        - فقط تراکنش‌های پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Transaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_update(id: int, amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی کامل تراکنش

    به‌روزرسانی کامل تراکنش
    
    این متد امکان تغییر همه فیلدهای یک تراکنش را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده تراکنش (status 200)
    
    مثال:
        PUT /api/v1/Transaction/1/
        {
            "investor": 1,
            "period": 1,
            "date_shamsi_input": "1403-07-15",
            "amount": "60000000",
            "transaction_type": "principal_deposit"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - date_shamsi_raw (date_shamsi_raw): string
              تاریخ شمسی خام برای دریافت مستقیم از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ تراکنش به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: principal_deposit (آورده), loan_deposit (آورده وام), principal_withdrawal (خروج از سرمایه), profit_accrual (سود). (الزامی)

* `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش. (اختیاری)
              الزامی: خیر
            - investor (سرمایه‌گذار): integer
              شناسه سرمایه‌گذار (جایگزین investor_id). (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره (جایگزین period_id). (اختیاری)
              الزامی: خیر
            - investor_id (investor_id): integer
              شناسه سرمایه‌گذار. می‌تواند از investor یا investor_id استفاده شود. (اختیاری)
              الزامی: خیر
            - period_id (period_id): integer
              شناسه دوره. می‌تواند از period یا period_id استفاده شود. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Transaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if date_shamsi_raw is not None and len(date_shamsi_raw) < 1: raise ValueError('date_shamsi_raw حداقل 1 کاراکتر باید باشد')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if transaction_type is None: raise ValueError('transaction_type الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if date_shamsi_raw is not None:
            data['date_shamsi_raw'] = date_shamsi_raw
        if amount is not None:
            data['amount'] = amount
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if description is not None:
            data['description'] = description
        if investor is not None:
            data['investor'] = investor
        if period is not None:
            data['period'] = period
        if investor_id is not None:
            data['investor_id'] = investor_id
        if period_id is not None:
            data['period_id'] = period_id
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_partial_update(id: int, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, amount: Optional[str] = None, transaction_type: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی تراکنش

    به‌روزرسانی جزئی تراکنش
    
    این متد امکان تغییر بخشی از فیلدهای تراکنش را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده تراکنش (status 200)
    
    مثال:
        PATCH /api/v1/Transaction/1/
        {
            "amount": "60000000"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - date_shamsi_raw (date_shamsi_raw): string
              تاریخ شمسی خام برای دریافت مستقیم از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ تراکنش به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: principal_deposit (آورده), loan_deposit (آورده وام), principal_withdrawal (خروج از سرمایه), profit_accrual (سود). (الزامی)

* `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش. (اختیاری)
              الزامی: خیر
            - investor (سرمایه‌گذار): integer
              شناسه سرمایه‌گذار (جایگزین investor_id). (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره (جایگزین period_id). (اختیاری)
              الزامی: خیر
            - investor_id (investor_id): integer
              شناسه سرمایه‌گذار. می‌تواند از investor یا investor_id استفاده شود. (اختیاری)
              الزامی: خیر
            - period_id (period_id): integer
              شناسه دوره. می‌تواند از period یا period_id استفاده شود. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Transaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if date_shamsi_raw is not None and len(date_shamsi_raw) < 1: raise ValueError('date_shamsi_raw حداقل 1 کاراکتر باید باشد')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if date_shamsi_raw is not None:
            data['date_shamsi_raw'] = date_shamsi_raw
        if amount is not None:
            data['amount'] = amount
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if description is not None:
            data['description'] = description
        if investor is not None:
            data['investor'] = investor
        if period is not None:
            data['period'] = period
        if investor_id is not None:
            data['investor_id'] = investor_id
        if period_id is not None:
            data['period_id'] = period_id
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_destroy(id: int, request=None) -> str:
    """
    حذف تراکنش

    حذف تراکنش
    
    این متد تراکنش را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای تراکنش
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Transaction/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط تراکنش‌های پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Transaction/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_combined_retrieve(request=None) -> str:
    """
    دریافت تراکنش‌های اصلی به همراه تراکنش‌های سود مرت...

    دریافت تراکنش‌های اصلی به همراه تراکنش‌های سود مرتبط در یک رکورد
    فقط تراکنش‌های اصلی (غیر سود) را برمی‌گرداند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Transaction/combined/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Transaction/combined/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_detailed_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار تفصیلی تراکنش‌ها با فیلترهای پیشرفته

    دریافت آمار تفصیلی تراکنش‌ها با فیلترهای پیشرفته

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Transaction/detailed_statistics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Transaction/detailed_statistics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_recalculate_construction_contractor_create(amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    محاسبه مجدد همه هزینه‌های پیمان ساختمان

    محاسبه مجدد همه هزینه‌های پیمان ساختمان

    پارامترهای درخواست:

        * بدنه (Request Body):
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - date_shamsi_raw (date_shamsi_raw): string
              تاریخ شمسی خام برای دریافت مستقیم از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ تراکنش به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: principal_deposit (آورده), loan_deposit (آورده وام), principal_withdrawal (خروج از سرمایه), profit_accrual (سود). (الزامی)

* `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش. (اختیاری)
              الزامی: خیر
            - investor (سرمایه‌گذار): integer
              شناسه سرمایه‌گذار (جایگزین investor_id). (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره (جایگزین period_id). (اختیاری)
              الزامی: خیر
            - investor_id (investor_id): integer
              شناسه سرمایه‌گذار. می‌تواند از investor یا investor_id استفاده شود. (اختیاری)
              الزامی: خیر
            - period_id (period_id): integer
              شناسه دوره. می‌تواند از period یا period_id استفاده شود. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Transaction/recalculate_construction_contractor/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if date_shamsi_raw is not None and len(date_shamsi_raw) < 1: raise ValueError('date_shamsi_raw حداقل 1 کاراکتر باید باشد')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if transaction_type is None: raise ValueError('transaction_type الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/recalculate_construction_contractor/'
        
        # ساخت data برای request body
        data = {}
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if date_shamsi_raw is not None:
            data['date_shamsi_raw'] = date_shamsi_raw
        if amount is not None:
            data['amount'] = amount
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if description is not None:
            data['description'] = description
        if investor is not None:
            data['investor'] = investor
        if period is not None:
            data['period'] = period
        if investor_id is not None:
            data['investor_id'] = investor_id
        if period_id is not None:
            data['period_id'] = period_id
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_recalculate_profits_create(amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    محاسبه مجدد سودها با نرخ سود فعال فعلی برای پروژه ...

    محاسبه مجدد سودها با نرخ سود فعال فعلی برای پروژه فعال

    پارامترهای درخواست:

        * بدنه (Request Body):
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - date_shamsi_raw (date_shamsi_raw): string
              تاریخ شمسی خام برای دریافت مستقیم از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ تراکنش به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - transaction_type (transaction_type): string
              نوع تراکنش. مقادیر معتبر: principal_deposit (آورده), loan_deposit (آورده وام), principal_withdrawal (خروج از سرمایه), profit_accrual (سود). (الزامی)

* `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره تراکنش. (اختیاری)
              الزامی: خیر
            - investor (سرمایه‌گذار): integer
              شناسه سرمایه‌گذار (جایگزین investor_id). (اختیاری)
              الزامی: خیر
            - period (دوره): integer
              شناسه دوره (جایگزین period_id). (اختیاری)
              الزامی: خیر
            - investor_id (investor_id): integer
              شناسه سرمایه‌گذار. می‌تواند از investor یا investor_id استفاده شود. (اختیاری)
              الزامی: خیر
            - period_id (period_id): integer
              شناسه دوره. می‌تواند از period یا period_id استفاده شود. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Transaction/recalculate_profits/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if date_shamsi_raw is not None and len(date_shamsi_raw) < 1: raise ValueError('date_shamsi_raw حداقل 1 کاراکتر باید باشد')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        if transaction_type is None: raise ValueError('transaction_type الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Transaction/recalculate_profits/'
        
        # ساخت data برای request body
        data = {}
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if date_shamsi_raw is not None:
            data['date_shamsi_raw'] = date_shamsi_raw
        if amount is not None:
            data['amount'] = amount
        if transaction_type is not None:
            data['transaction_type'] = transaction_type
        if description is not None:
            data['description'] = description
        if investor is not None:
            data['investor'] = investor
        if period is not None:
            data['period'] = period
        if investor_id is not None:
            data['investor_id'] = investor_id
        if period_id is not None:
            data['period_id'] = period_id
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار کلی تراکنش‌های پروژه

    دریافت آمار کلی تراکنش‌های پروژه
    
    این endpoint آمار جامع و کلی تمام تراکنش‌های پروژه جاری را برمی‌گرداند.
    
    خروجی شامل:
    - تعداد کل تراکنش‌ها
    - مجموع آورده‌ها (deposits)
    - مجموع برداشت‌ها (withdrawals)
    - مجموع سود (profits)
    - سرمایه خالص (net principal)
    - مجموع کل (grand total)
    - تعداد سرمایه‌گذاران منحصر به فرد
    
    سناریوهای استفاده:
    - نمایش خلاصه مالی پروژه
    - نمایش داشبورد تراکنش‌ها
    - تحلیل جریان نقدی پروژه
    - محاسبه شاخص‌های مالی کلیدی
    - تهیه گزارش‌های مدیریتی
    
    مثال استفاده:
    GET /api/v1/Transaction/statistics/
    
    مثال خروجی:
    {
        "total_transactions": 150,
        "total_deposits": 500000000,
        "total_withdrawals": -20000000,
        "total_profits": 75000000,
        "net_principal": 480000000,
        "grand_total": 555000000,
        "unique_investors": 5
    }
    
    نکات مهم:
    - فقط تراکنش‌های پروژه جاری را شامل می‌شود
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - مجموع برداشت‌ها به صورت منفی محاسبه می‌شود
    - تمام مبالغ به تومان هستند

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Transaction/statistics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Transaction/statistics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Unit (7 endpoint) =====

@tool
def unit_list(request=None) -> str:
    """
    دریافت لیست تمام واحدهای پروژه جاری

    دریافت لیست تمام واحدهای پروژه جاری
    
    این متد لیست واحدهای مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/Unit/?page=1&page_size=20
    
    نکات:
        - فقط واحدهای پروژه جاری برگردانده می‌شود
        - نیاز به احراز هویت دارد

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Unit/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Unit/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_create(name: str, area: str, price_per_meter: str, total_price: str, project: Optional[int] = None, request=None) -> str:
    """
    ایجاد واحد جدید برای پروژه جاری

    ایجاد واحد جدید برای پروژه جاری
    
    این متد واحد جدید را برای پروژه فعال ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - name (الزامی): نام واحد
        - area (الزامی): متراژ واحد (به صورت string)
        - price_per_meter (الزامی): قیمت هر متر (به صورت string)
        - total_price (الزامی): قیمت نهایی (به صورت string)
    
    Returns:
        Response با اطلاعات واحد ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/Unit/
        {
            "name": "واحد 101",
            "area": "120.5",
            "price_per_meter": "5000000",
            "total_price": "602500000"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - قیمت نهایی باید برابر area × price_per_meter باشد
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - name (نام): string
              نام واحد (مثال: "واحد 101" یا "آپارتمان 2A"). (الزامی)
              الزامی: بله
            - area (area): string
              متراژ واحد به متر مربع. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - price_per_meter (price_per_meter): string
              قیمت هر متر مربع به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - total_price (total_price): string
              قیمت نهایی واحد به تومان (محاسبه شده: area × price_per_meter). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/Unit/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if name is None: raise ValueError('نام الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if area is None: raise ValueError('area الزامی است')
        if area is not None and not re.match(r'^-?\d{0,8}(?:\.\d{0,4})?$', str(area)): raise ValueError('area فرمت نامعتبر است')
        if price_per_meter is None: raise ValueError('price_per_meter الزامی است')
        if price_per_meter is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(price_per_meter)): raise ValueError('price_per_meter فرمت نامعتبر است')
        if total_price is None: raise ValueError('total_price الزامی است')
        if total_price is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_price)): raise ValueError('total_price فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Unit/'
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if area is not None:
            data['area'] = area
        if price_per_meter is not None:
            data['price_per_meter'] = price_per_meter
        if total_price is not None:
            data['total_price'] = total_price
        if project is not None:
            data['project'] = project
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک واحد خاص

    دریافت جزئیات یک واحد خاص
    
    این متد اطلاعات کامل واحد با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای واحد
    
    Returns:
        Response با اطلاعات کامل واحد
    
    مثال:
        GET /api/v1/Unit/1/
    
    نکات:
        - فقط واحدهای پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Unit/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Unit/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_update(id: int, name: str, area: str, price_per_meter: str, total_price: str, project: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی کامل واحد

    به‌روزرسانی کامل واحد
    
    این متد امکان تغییر همه فیلدهای یک واحد را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای واحد
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده واحد (status 200)
    
    مثال:
        PUT /api/v1/Unit/1/
        {
            "name": "واحد 101",
            "area": "125.0",
            "price_per_meter": "5500000",
            "total_price": "687500000"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - name (نام): string
              نام واحد (مثال: "واحد 101" یا "آپارتمان 2A"). (الزامی)
              الزامی: بله
            - area (area): string
              متراژ واحد به متر مربع. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - price_per_meter (price_per_meter): string
              قیمت هر متر مربع به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - total_price (total_price): string
              قیمت نهایی واحد به تومان (محاسبه شده: area × price_per_meter). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/Unit/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if name is None: raise ValueError('نام الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if area is None: raise ValueError('area الزامی است')
        if area is not None and not re.match(r'^-?\d{0,8}(?:\.\d{0,4})?$', str(area)): raise ValueError('area فرمت نامعتبر است')
        if price_per_meter is None: raise ValueError('price_per_meter الزامی است')
        if price_per_meter is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(price_per_meter)): raise ValueError('price_per_meter فرمت نامعتبر است')
        if total_price is None: raise ValueError('total_price الزامی است')
        if total_price is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_price)): raise ValueError('total_price فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Unit/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if area is not None:
            data['area'] = area
        if price_per_meter is not None:
            data['price_per_meter'] = price_per_meter
        if total_price is not None:
            data['total_price'] = total_price
        if project is not None:
            data['project'] = project
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_partial_update(id: int, name: Optional[str] = None, area: Optional[str] = None, price_per_meter: Optional[str] = None, total_price: Optional[str] = None, project: Optional[int] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی واحد

    به‌روزرسانی جزئی واحد
    
    این متد امکان تغییر بخشی از فیلدهای واحد را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای واحد
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده واحد (status 200)
    
    مثال:
        PATCH /api/v1/Unit/1/
        {
            "price_per_meter": "5500000"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - name (نام): string
              نام واحد (مثال: "واحد 101" یا "آپارتمان 2A"). (الزامی)
              الزامی: خیر
            - area (area): string
              متراژ واحد به متر مربع. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - price_per_meter (price_per_meter): string
              قیمت هر متر مربع به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - total_price (total_price): string
              قیمت نهایی واحد به تومان (محاسبه شده: area × price_per_meter). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - project (پروژه): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/Unit/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if name is not None and len(name) < 1: raise ValueError('نام حداقل 1 کاراکتر باید باشد')
        if name is not None and len(name) > 200: raise ValueError('نام حداکثر 200 کاراکتر می‌تواند باشد')
        if area is not None and not re.match(r'^-?\d{0,8}(?:\.\d{0,4})?$', str(area)): raise ValueError('area فرمت نامعتبر است')
        if price_per_meter is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(price_per_meter)): raise ValueError('price_per_meter فرمت نامعتبر است')
        if total_price is not None and not re.match(r'^-?\d{0,13}(?:\.\d{0,2})?$', str(total_price)): raise ValueError('total_price فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/Unit/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if name is not None:
            data['name'] = name
        if area is not None:
            data['area'] = area
        if price_per_meter is not None:
            data['price_per_meter'] = price_per_meter
        if total_price is not None:
            data['total_price'] = total_price
        if project is not None:
            data['project'] = project
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_destroy(id: int, request=None) -> str:
    """
    حذف واحد

    حذف واحد
    
    این متد واحد را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای واحد
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/Unit/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط واحدهای پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        - در صورت وجود وابستگی (سرمایه‌گذاران)، ممکن است حذف ناموفق باشد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/Unit/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/Unit/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار کلی واحدها

    دریافت آمار کلی واحدها

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/Unit/statistics/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/Unit/statistics/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for UnitSpecificExpense (6 endpoint) =====

@tool
def unitspecificexpense_list(project: Optional[int] = None, unit: Optional[int] = None, request=None) -> str:
    """
    دریافت لیست تمام هزینه‌های اختصاصی واحدهای پروژه ج...

    دریافت لیست تمام هزینه‌های اختصاصی واحدهای پروژه جاری
    
    این متد لیست هزینه‌های اختصاصی مرتبط با پروژه فعال را برمی‌گرداند.
    نتایج به صورت صفحه‌بندی شده و قابل فیلتر و مرتب‌سازی هستند.
    
    Query Parameters:
        - page: شماره صفحه (پیش‌فرض: 1)
        - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
        - ordering: فیلد مرتب‌سازی
        - unit: فیلتر بر اساس شناسه واحد
        - project: فیلتر بر اساس شناسه پروژه
    
    Returns:
        Response با ساختار paginated شامل results, count, next, previous
    
    مثال:
        GET /api/v1/UnitSpecificExpense/?unit=1&page=1
    
    نکات:
        - فقط هزینه‌های اختصاصی پروژه جاری برگردانده می‌شود
        - امکان فیلتر بر اساس واحد
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * کوئری (Query String):
            - project (پروژه): integer
              الزامی: خیر
            - unit (unit): integer
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/UnitSpecificExpense/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/UnitSpecificExpense/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}
        if project is not None:
            kwargs['project'] = project
        if unit is not None:
            kwargs['unit'] = unit
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_create(title: str, amount: str, project: Optional[int] = None, project_id: Optional[int] = None, unit: Optional[int] = None, unit_id: Optional[int] = None, date_shamsi_input: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ایجاد هزینه اختصاصی جدید برای واحد

    ایجاد هزینه اختصاصی جدید برای واحد
    
    این متد هزینه اختصاصی جدید را برای یک واحد ثبت می‌کند.
    پروژه به صورت خودکار از session کاربر تعیین می‌شود.
    
    Request Body:
        - unit/unit_id (الزامی): شناسه واحد
        - title (الزامی): عنوان هزینه
        - date_shamsi_input (الزامی): تاریخ شمسی (YYYY-MM-DD)
        - amount (الزامی): مبلغ هزینه (به صورت string)
        - description (اختیاری): توضیحات
    
    Returns:
        Response با اطلاعات هزینه اختصاصی ایجاد شده (status 201)
    
    مثال:
        POST /api/v1/UnitSpecificExpense/
        {
            "unit": 1,
            "title": "نصب کولر گازی",
            "date_shamsi_input": "1403-07-15",
            "amount": "5000000",
            "description": "نصب کولر گازی در واحد 101"
        }
    
    نکات:
        - جزئیات فیلدها در serializer descriptions موجود است
        - پروژه به صورت خودکار از session تنظیم می‌شود
        - تاریخ میلادی به صورت خودکار محاسبه می‌شود
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه (جایگزین project_id). اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)
              الزامی: خیر
            - project_id (project_id): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)
              الزامی: خیر
            - unit (unit): integer
              شناسه واحد (جایگزین unit_id). (اختیاری)
              الزامی: خیر
            - unit_id (unit_id): integer
              شناسه واحد. می‌تواند از unit یا unit_id استفاده شود. (اختیاری)
              الزامی: خیر
            - title (title): string
              عنوان هزینه اختصاصی واحد (مثال: "نصب کولر گازی"). (الزامی)
              الزامی: بله
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ هزینه به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/UnitSpecificExpense/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if title is None: raise ValueError('title الزامی است')
        if title is not None and len(title) < 1: raise ValueError('title حداقل 1 کاراکتر باید باشد')
        if title is not None and len(title) > 200: raise ValueError('title حداکثر 200 کاراکتر می‌تواند باشد')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/UnitSpecificExpense/'
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if project_id is not None:
            data['project_id'] = project_id
        if unit is not None:
            data['unit'] = unit
        if unit_id is not None:
            data['unit_id'] = unit_id
        if title is not None:
            data['title'] = title
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_retrieve(id: int, request=None) -> str:
    """
    دریافت جزئیات یک هزینه اختصاصی خاص

    دریافت جزئیات یک هزینه اختصاصی خاص
    
    این متد اطلاعات کامل هزینه اختصاصی با شناسه مشخص شده را برمی‌گرداند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه اختصاصی
    
    Returns:
        Response با اطلاعات کامل هزینه اختصاصی شامل unit_data و project_data
    
    مثال:
        GET /api/v1/UnitSpecificExpense/1/
    
    نکات:
        - فقط هزینه‌های اختصاصی پروژه جاری قابل دسترسی هستند
        - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/UnitSpecificExpense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/UnitSpecificExpense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_update(id: int, title: str, amount: str, project: Optional[int] = None, project_id: Optional[int] = None, unit: Optional[int] = None, unit_id: Optional[int] = None, date_shamsi_input: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی کامل هزینه اختصاصی

    به‌روزرسانی کامل هزینه اختصاصی
    
    این متد امکان تغییر همه فیلدهای یک هزینه اختصاصی را فراهم می‌کند.
    تمام فیلدهای قابل ویرایش باید ارسال شوند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه اختصاصی
    
    Request Body:
        - تمام فیلدهای قابل ویرایش
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده هزینه اختصاصی (status 200)
    
    مثال:
        PUT /api/v1/UnitSpecificExpense/1/
        {
            "unit": 1,
            "title": "نصب کولر گازی - به‌روزرسانی شده",
            "date_shamsi_input": "1403-07-15",
            "amount": "6000000"
        }
    
    نکات:
        - همه فیلدها باید ارسال شوند
        - برای به‌روزرسانی جزئی از PATCH استفاده کنید
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه (جایگزین project_id). اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)
              الزامی: خیر
            - project_id (project_id): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)
              الزامی: خیر
            - unit (unit): integer
              شناسه واحد (جایگزین unit_id). (اختیاری)
              الزامی: خیر
            - unit_id (unit_id): integer
              شناسه واحد. می‌تواند از unit یا unit_id استفاده شود. (اختیاری)
              الزامی: خیر
            - title (title): string
              عنوان هزینه اختصاصی واحد (مثال: "نصب کولر گازی"). (الزامی)
              الزامی: بله
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ هزینه به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: بله
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PUT
        - مسیر: /api/v1/UnitSpecificExpense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if title is None: raise ValueError('title الزامی است')
        if title is not None and len(title) < 1: raise ValueError('title حداقل 1 کاراکتر باید باشد')
        if title is not None and len(title) > 200: raise ValueError('title حداکثر 200 کاراکتر می‌تواند باشد')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if amount is None: raise ValueError('مبلغ الزامی است')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/UnitSpecificExpense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if project_id is not None:
            data['project_id'] = project_id
        if unit is not None:
            data['unit'] = unit
        if unit_id is not None:
            data['unit_id'] = unit_id
        if title is not None:
            data['title'] = title
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PUT',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_partial_update(id: int, project: Optional[int] = None, project_id: Optional[int] = None, unit: Optional[int] = None, unit_id: Optional[int] = None, title: Optional[str] = None, date_shamsi_input: Optional[str] = None, amount: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی جزئی هزینه اختصاصی

    به‌روزرسانی جزئی هزینه اختصاصی
    
    این متد امکان تغییر بخشی از فیلدهای هزینه اختصاصی را فراهم می‌کند.
    فقط فیلدهای ارسال شده تغییر می‌کنند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه اختصاصی
    
    Request Body:
        - فیلدهای انتخابی برای به‌روزرسانی
    
    Returns:
        Response با اطلاعات به‌روزرسانی شده هزینه اختصاصی (status 200)
    
    مثال:
        PATCH /api/v1/UnitSpecificExpense/1/
        {
            "amount": "6000000"
        }
    
    نکات:
        - فقط فیلدهای ارسال شده تغییر می‌کنند
        - فیلدهای ارسال نشده حفظ می‌شوند
        - انعطاف بیشتری نسبت به PUT دارد
        - جزئیات فیلدها در serializer descriptions موجود است
        - نیاز به احراز هویت دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

        * بدنه (Request Body):
            - project (پروژه): integer
              شناسه پروژه (جایگزین project_id). اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)
              الزامی: خیر
            - project_id (project_id): integer
              شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)
              الزامی: خیر
            - unit (unit): integer
              شناسه واحد (جایگزین unit_id). (اختیاری)
              الزامی: خیر
            - unit_id (unit_id): integer
              شناسه واحد. می‌تواند از unit یا unit_id استفاده شود. (اختیاری)
              الزامی: خیر
            - title (title): string
              عنوان هزینه اختصاصی واحد (مثال: "نصب کولر گازی"). (الزامی)
              الزامی: خیر
            - date_shamsi_input (date_shamsi_input): string
              تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)
              الزامی: خیر
            - amount (مبلغ): string
              مبلغ هزینه به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)
              الزامی: خیر
            - description (توضیحات): string
              توضیحات تکمیلی درباره هزینه. (اختیاری)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: PATCH
        - مسیر: /api/v1/UnitSpecificExpense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        if title is not None and len(title) < 1: raise ValueError('title حداقل 1 کاراکتر باید باشد')
        if title is not None and len(title) > 200: raise ValueError('title حداکثر 200 کاراکتر می‌تواند باشد')
        if date_shamsi_input is not None and len(date_shamsi_input) < 1: raise ValueError('date_shamsi_input حداقل 1 کاراکتر باید باشد')
        if amount is not None and not re.match(r'^-?\d{0,18}(?:\.\d{0,2})?$', str(amount)): raise ValueError('مبلغ فرمت نامعتبر است')
        # ساخت URL کامل
        url = '/api/v1/UnitSpecificExpense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if project_id is not None:
            data['project_id'] = project_id
        if unit is not None:
            data['unit'] = unit
        if unit_id is not None:
            data['unit_id'] = unit_id
        if title is not None:
            data['title'] = title
        if date_shamsi_input is not None:
            data['date_shamsi_input'] = date_shamsi_input
        if amount is not None:
            data['amount'] = amount
        if description is not None:
            data['description'] = description
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='PATCH',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_destroy(id: int, request=None) -> str:
    """
    حذف هزینه اختصاصی

    حذف هزینه اختصاصی
    
    این متد هزینه اختصاصی را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.
    
    URL Parameters:
        - pk: شناسه یکتای هزینه اختصاصی
    
    Returns:
        Response خالی با status 204 No Content در صورت موفقیت
    
    مثال:
        DELETE /api/v1/UnitSpecificExpense/1/
    
    نکات:
        - حذف برگشت‌ناپذیر است
        - فقط هزینه‌های اختصاصی پروژه جاری قابل حذف هستند
        - نیاز به احراز هویت و دسترسی APISecurityPermission دارد

    پارامترهای درخواست:

        * مسیر (URL Path):
            - id (شناسه): integer
              یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
              الزامی: بله
              مثال: 1

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: DELETE
        - مسیر: /api/v1/UnitSpecificExpense/{id}/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        import re
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        # Validation
        if id is None: raise ValueError('شناسه الزامی است')
        # ساخت URL کامل
        url = '/api/v1/UnitSpecificExpense/{id}/'
        if id is not None:
            url = url.replace('{id}', str(id))
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='DELETE',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Authentication (7 endpoint) =====

@tool
def auth_change_password_create(request=None) -> str:
    """
    تغییر رمز عبور کاربر

    تغییر رمز عبور کاربر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/auth/change-password/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/auth/change-password/'
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_csrf_retrieve(request=None) -> str:
    """
    دریافت CSRF Token برای استفاده در درخواست‌های بعدی

    دریافت CSRF Token برای استفاده در درخواست‌های بعدی

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/auth/csrf/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/auth/csrf/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_login_create(request=None) -> str:
    """
    ورود کاربر به سیستم و دریافت token

    ورود کاربر به سیستم و دریافت token

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/auth/login/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/auth/login/'
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_logout_create(request=None) -> str:
    """
    خروج کاربر از سیستم و حذف token

    خروج کاربر از سیستم و حذف token

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/auth/logout/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/auth/logout/'
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_register_create(request=None) -> str:
    """
    ثبت‌نام کاربر جدید (فقط برای ادمین‌ها)

    ثبت‌نام کاربر جدید (فقط برای ادمین‌ها)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: POST
        - مسیر: /api/v1/auth/register/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/auth/register/'
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='POST',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_user_retrieve(request=None) -> str:
    """
    دریافت اطلاعات کاربر احراز هویت شده

    دریافت اطلاعات کاربر احراز هویت شده

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/auth/user/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/auth/user/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def status_retrieve(request=None) -> str:
    """
    بررسی وضعیت API و اطلاعات کاربر

    بررسی وضعیت API و اطلاعات کاربر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/status/
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/status/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Analysis (1 endpoint) =====

@tool
def comprehensive_analysis_retrieve(project_id: Optional[int] = None, request=None) -> str:
    """
    دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی

    دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی

    پارامترهای درخواست:

        * کوئری (Query String):
            - project_id (project_id): integer
              شناسه پروژه (اختیاری - اگر مشخص نشود از پروژه جاری استفاده می‌شود)
              الزامی: خیر

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    نکات مهم:
        - روش HTTP: GET
        - مسیر: /api/v1/comprehensive/comprehensive_analysis/
        - نیاز به احراز هویت: SessionAuthentication, tokenAuth
    """
    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )        # ساخت URL کامل
        url = '/api/v1/comprehensive/comprehensive_analysis/'
        
        # ساخت kwargs برای query parameters
        kwargs = {}
        if project_id is not None:
            kwargs['project_id'] = project_id
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='GET',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

