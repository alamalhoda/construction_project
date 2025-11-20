"""
Tools تولید شده خودکار از OpenAPI Schema
این فایل به صورت خودکار از schema.json تولید شده است.

📊 آمار استخراج شده:
   - تعداد کل Endpoints: 105
   - تعداد کل پارامترها: 311
   - تعداد دسته‌بندی‌ها (Tags): 13

✅ اطلاعات شامل شده در هر Tool:
   - توضیحات کامل endpoint (description)
   - مسیر API (path)
   - متد HTTP (GET, POST, PUT, DELETE, PATCH)
   - تمام پارامترها (path, query, body)
   - توضیحات کامل هر فیلد (description, type, format)
   - فیلدهای الزامی و اختیاری (required)
   - مقادیر enum (اگر وجود داشته باشد)
   - نیاز به احراز هویت (security)
   - کدهای وضعیت پاسخ (responses)
   - Operation ID
   - دسته‌بندی (tags)

⚠️  توجه: این Tools نیاز به پیاده‌سازی کامل دارند.
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
from django.conf import settings


# ===== Tools for Expense (11 endpoint) =====

@tool
def expense_list(request=None) -> str:
    """
    ViewSet برای مدیریت هزینه‌های پروژه

    این ViewSet امکان مدیریت کامل هزینه‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌ها
    - دریافت آمار و گزارش‌های مالی
    - محاسبه مجموع هزینه‌ها بر اساس نوع و دوره
    - مدیریت هزینه‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت هزینه‌های مواد اولیه (material)
    - ثبت هزینه‌های نیروی کار (labor)
    - ثبت هزینه‌های اداری و عمومی (administrative)
    - دریافت گزارش‌های مالی برای تحلیل پروژه
    - محاسبه هزینه‌های تجمعی برای هر دوره
    
    مثال‌های کاربرد:
    - برای ثبت خرید سیمان و آجر: expense_type='material', amount='5000000'
    - برای ثبت حقوق کارگران: expense_type='labor', amount='3000000'
    - برای دریافت لیست تمام هزینه‌ها: GET /api/v1/Expense/
    - برای دریافت آمار هزینه‌ها: GET /api/v1/Expense/dashboard_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها می‌توانند به یک دوره خاص مرتبط باشند
    - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other

    این Tool از API endpoint GET /api/v1/Expense/ استفاده می‌کند.
    Operation ID: Expense_list
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Expense/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_list') or get_viewset_class_from_path('/api/v1/Expense/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_create(project: int, expense_type: str, amount: str, period: int, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet برای مدیریت هزینه‌های پروژه

    این ViewSet امکان مدیریت کامل هزینه‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌ها
    - دریافت آمار و گزارش‌های مالی
    - محاسبه مجموع هزینه‌ها بر اساس نوع و دوره
    - مدیریت هزینه‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت هزینه‌های مواد اولیه (material)
    - ثبت هزینه‌های نیروی کار (labor)
    - ثبت هزینه‌های اداری و عمومی (administrative)
    - دریافت گزارش‌های مالی برای تحلیل پروژه
    - محاسبه هزینه‌های تجمعی برای هر دوره
    
    مثال‌های کاربرد:
    - برای ثبت خرید سیمان و آجر: expense_type='material', amount='5000000'
    - برای ثبت حقوق کارگران: expense_type='labor', amount='3000000'
    - برای دریافت لیست تمام هزینه‌ها: GET /api/v1/Expense/
    - برای دریافت آمار هزینه‌ها: GET /api/v1/Expense/dashboard_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها می‌توانند به یک دوره خاص مرتبط باشند
    - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other

    این Tool از API endpoint POST /api/v1/Expense/ استفاده می‌کند.
    Operation ID: Expense_create
    دسته‌بندی: Expense

    Args:
        project (int): پروژه
        expense_type (str): نوع هزینه
        amount (str): مبلغ
        description (str): توضیحات
        period (int): دوره
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Expense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Expense/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_create') or get_viewset_class_from_path('/api/v1/Expense/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_retrieve(id: int, request=None) -> str:
    """
    دریافت اطلاعات کامل یک هزینه خاص بر اساس شناسه (ID) آن.

    ⚠️ **هشدار مهم:** این ابزار نیاز به پارامتر id دارد که باید یک عدد صحیح (int) باشد.
    هیچ‌وقت این ابزار را بدون id فراخوانی نکنید - این کار باعث خطا می‌شود.

    این Tool از API endpoint GET /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_retrieve
    دسته‌بندی: Expense

    Args:
        id (int): شناسه عددی هزینه (مثلاً 1، 2، 3 و غیره).
                 ⚠️ این پارامتر الزامی است و نمی‌تواند None یا خالی باشد.
                 اگر کاربر سوالی درباره "هزینه شماره X" یا "هزینه X" پرسید،
                 ابتدا عدد X را از سوال استخراج کنید، سپس آن را به عنوان id پاس دهید.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: اطلاعات کامل هزینه شامل: مبلغ، نوع، دوره، توضیحات و سایر جزئیات

    مثال‌های استفاده صحیح:
        - سوال: "هزینه شماره 1" → expense_retrieve(id=1) ✅
        - سوال: "هزینه 5" → expense_retrieve(id=5) ✅
        - سوال: "اطلاعات هزینه 10" → expense_retrieve(id=10) ✅

    مثال‌های استفاده نادرست (هرگز این کار را نکنید):
        - expense_retrieve() ❌ (بدون id - خطا می‌دهد)
        - expense_retrieve(id=None) ❌ (id نمی‌تواند None باشد)
        - expense_retrieve(id="1") ❌ (id باید int باشد، نه string)

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
        - id باید یک عدد صحیح مثبت باشد (int)
        - اگر هزینه‌ای با این id وجود نداشته باشد، خطا برمی‌گرداند
        - اگر id را از سوال کاربر پیدا نکردید، ابتدا از expense_list استفاده کنید
        - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_retrieve') or get_viewset_class_from_path('/api/v1/Expense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_update(id: int, project: int, expense_type: str, amount: str, period: int, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet برای مدیریت هزینه‌های پروژه

    این ViewSet امکان مدیریت کامل هزینه‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌ها
    - دریافت آمار و گزارش‌های مالی
    - محاسبه مجموع هزینه‌ها بر اساس نوع و دوره
    - مدیریت هزینه‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت هزینه‌های مواد اولیه (material)
    - ثبت هزینه‌های نیروی کار (labor)
    - ثبت هزینه‌های اداری و عمومی (administrative)
    - دریافت گزارش‌های مالی برای تحلیل پروژه
    - محاسبه هزینه‌های تجمعی برای هر دوره
    
    مثال‌های کاربرد:
    - برای ثبت خرید سیمان و آجر: expense_type='material', amount='5000000'
    - برای ثبت حقوق کارگران: expense_type='labor', amount='3000000'
    - برای دریافت لیست تمام هزینه‌ها: GET /api/v1/Expense/
    - برای دریافت آمار هزینه‌ها: GET /api/v1/Expense/dashboard_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها می‌توانند به یک دوره خاص مرتبط باشند
    - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other

    این Tool از API endpoint PUT /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_update
    دسته‌بندی: Expense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        project (int): پروژه
        expense_type (str): نوع هزینه
        amount (str): مبلغ
        description (str): توضیحات
        period (int): دوره
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Expense/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_update') or get_viewset_class_from_path('/api/v1/Expense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_partial_update(id: int, project: Optional[int] = None, expense_type: Optional[str] = None, amount: Optional[str] = None, description: Optional[str] = None, period: Optional[int] = None, request=None) -> str:
    """
    ViewSet برای مدیریت هزینه‌های پروژه

    این ViewSet امکان مدیریت کامل هزینه‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌ها
    - دریافت آمار و گزارش‌های مالی
    - محاسبه مجموع هزینه‌ها بر اساس نوع و دوره
    - مدیریت هزینه‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت هزینه‌های مواد اولیه (material)
    - ثبت هزینه‌های نیروی کار (labor)
    - ثبت هزینه‌های اداری و عمومی (administrative)
    - دریافت گزارش‌های مالی برای تحلیل پروژه
    - محاسبه هزینه‌های تجمعی برای هر دوره
    
    مثال‌های کاربرد:
    - برای ثبت خرید سیمان و آجر: expense_type='material', amount='5000000'
    - برای ثبت حقوق کارگران: expense_type='labor', amount='3000000'
    - برای دریافت لیست تمام هزینه‌ها: GET /api/v1/Expense/
    - برای دریافت آمار هزینه‌ها: GET /api/v1/Expense/dashboard_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها می‌توانند به یک دوره خاص مرتبط باشند
    - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other

    این Tool از API endpoint PATCH /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_partial_update
    دسته‌بندی: Expense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        project (int): پروژه
        expense_type (str): نوع هزینه
        amount (str): مبلغ
        description (str): توضیحات
        period (int): دوره
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Expense/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_partial_update') or get_viewset_class_from_path('/api/v1/Expense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_destroy(id: int, request=None) -> str:
    """
    ViewSet برای مدیریت هزینه‌های پروژه

    این ViewSet امکان مدیریت کامل هزینه‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌ها
    - دریافت آمار و گزارش‌های مالی
    - محاسبه مجموع هزینه‌ها بر اساس نوع و دوره
    - مدیریت هزینه‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت هزینه‌های مواد اولیه (material)
    - ثبت هزینه‌های نیروی کار (labor)
    - ثبت هزینه‌های اداری و عمومی (administrative)
    - دریافت گزارش‌های مالی برای تحلیل پروژه
    - محاسبه هزینه‌های تجمعی برای هر دوره
    
    مثال‌های کاربرد:
    - برای ثبت خرید سیمان و آجر: expense_type='material', amount='5000000'
    - برای ثبت حقوق کارگران: expense_type='labor', amount='3000000'
    - برای دریافت لیست تمام هزینه‌ها: GET /api/v1/Expense/
    - برای دریافت آمار هزینه‌ها: GET /api/v1/Expense/dashboard_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها می‌توانند به یک دوره خاص مرتبط باشند
    - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other

    این Tool از API endpoint DELETE /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_destroy
    دسته‌بندی: Expense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Expense/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_destroy') or get_viewset_class_from_path('/api/v1/Expense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_dashboard_data_retrieve(request=None) -> str:
    """
    دریافت داده‌های لیست هزینه‌ها برای نمایش در داشبورد

    این endpoint داده‌های لازم برای نمایش در داشبورد هزینه‌ها را برمی‌گرداند.
    
    خروجی شامل:
    - لیست تمام هزینه‌ها با اطلاعات دوره
    - آمار کلی هزینه‌ها (تعداد، مجموع)
    - اطلاعات پروژه جاری
    - داده‌های ماتریسی برای نمایش جدولی
    
    سناریوهای استفاده:
    - نمایش داشبورد هزینه‌ها در رابط کاربری
    - فیلتر کردن هزینه‌ها بر اساس دوره
    - محاسبه مجموع هزینه‌ها برای گزارش‌گیری
    - نمایش ترند هزینه‌ها در طول زمان
    
    مثال استفاده:
    GET /api/v1/Expense/dashboard_data/
    
    مثال خروجی:
    {
        "success": true,
        "data": {
            "periods": [
                {
                    "period_id": 1,
                    "period_label": "مرداد 1402",
                    "expenses": {
                        "material": {"amount": 5000000, "label": "مواد اولیه"},
                        "labor": {"amount": 3000000, "label": "نیروی کار"}
                    },
                    "period_total": 8000000,
                    "cumulative_total": 8000000
                }
            ],
            "grand_total": 15000000,
            "project_name": "پروژه نمونه"
        }
    }
    
    نکات مهم:
    - فقط هزینه‌های پروژه جاری را برمی‌گرداند
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - داده‌ها بر اساس دوره مرتب می‌شوند

    این Tool از API endpoint GET /api/v1/Expense/dashboard_data/ استفاده می‌کند.
    Operation ID: Expense_dashboard_data_retrieve
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    مثال استفاده:
        GET /api/v1/Expense/dashboard_data/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_dashboard_data_retrieve') or get_viewset_class_from_path('/api/v1/Expense/dashboard_data/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_dashboard_data_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='dashboard_data_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Expense/get_expense_details/ استفاده می‌کند.
    Operation ID: Expense_get_expense_details_retrieve
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    مثال استفاده:
        GET /api/v1/Expense/get_expense_details/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_get_expense_details_retrieve') or get_viewset_class_from_path('/api/v1/Expense/get_expense_details/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_get_expense_details_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='get_expense_details_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Expense/total_expenses/ استفاده می‌کند.
    Operation ID: Expense_total_expenses_retrieve
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    مثال استفاده:
        GET /api/v1/Expense/total_expenses/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_total_expenses_retrieve') or get_viewset_class_from_path('/api/v1/Expense/total_expenses/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_total_expenses_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='total_expenses_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_update_expense_create(project: int, expense_type: str, amount: str, period: int, description: Optional[str] = None, request=None) -> str:
    """
    به‌روزرسانی یا ایجاد هزینه برای یک دوره و نوع خاص.

    این endpoint هزینه را برای یک دوره و نوع خاص به‌روزرسانی می‌کند.
    اگر هزینه وجود نداشته باشد، آن را ایجاد می‌کند. هزینه بر اساس پروژه جاری،
    دوره و نوع هزینه شناسایی می‌شود. مبلغ به صورت Decimal ذخیره می‌شود.
    
    قابلیت‌ها/خروجی شامل:
    - ثبت یا به‌روزرسانی هزینه با جزئیات کامل
    - بازگشت جزئیات هزینه با ID و وضعیت ایجاد/به‌روزرسانی
    
    سناریوهای استفاده:
    - ثبت هزینه‌های ماهانه پروژه ساختمانی توسط مدیر پروژه
    - به‌روزرسانی مبلغ هزینه‌های قبلی در صورت تغییر
    - ثبت هزینه‌های دوره‌ای به صورت دسته‌ای از سیستم حسابداری خارجی
    - ویرایش هزینه‌های ثبت شده در داشبورد مدیریت
    
    مثال استفاده:
        POST /api/v1/Expense/update_expense/
    
    مثال ورودی/خروجی:
        Input:
        {
            "period_id": 3,
            "expense_type": "project_manager",
            "amount": "5000000",
            "description": "حقوق مدیر پروژه"
        }
    
        Output:
        {
            "success": true,
            "message": "هزینه با موفقیت به‌روزرسانی شد",
            "data": {
                "expense_id": 15,
                "amount": 5000000.0,
                "description": "حقوق مدیر پروژه",
                "created": false
            }
        }
    
    نکات مهم:
    - هزینه بر اساس پروژه جاری (active project) از session شناسایی می‌شود
    - اگر هزینه وجود داشته باشد، به‌روزرسانی می‌شود؛ در غیر این صورت ایجاد می‌شود
    - مبلغ باید به صورت string ارسال شود تا از مشکلات precision جلوگیری شود
    - نیاز به احراز هویت دارد (IsAuthenticated)

    این Tool از API endpoint POST /api/v1/Expense/update_expense/ استفاده می‌کند.
    Operation ID: Expense_update_expense_create
    دسته‌بندی: Expense

    Args:
        project (int): پروژه
        expense_type (str): نوع هزینه
        amount (str): مبلغ
        description (str): توضیحات
        period (int): دوره
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Expense/update_expense/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_update_expense_create') or get_viewset_class_from_path('/api/v1/Expense/update_expense/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_update_expense_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update_expense_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def expense_with_periods_retrieve(request=None) -> str:
    """
    دریافت هزینه‌ها با اطلاعات دوره‌ها برای محاسبه دوره متوسط ساخت

    این Tool از API endpoint GET /api/v1/Expense/with_periods/ استفاده می‌کند.
    Operation ID: Expense_with_periods_retrieve
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Expense

    مثال استفاده:
        GET /api/v1/Expense/with_periods/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Expense_with_periods_retrieve') or get_viewset_class_from_path('/api/v1/Expense/with_periods/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Expense_with_periods_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='with_periods_retrieve',
            request=request,
            method='GET',
            pk=pk,
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
    ViewSet for the InterestRate class

    این Tool از API endpoint GET /api/v1/InterestRate/ استفاده می‌کند.
    Operation ID: InterestRate_list
    دسته‌بندی: InterestRate

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/InterestRate/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_list') or get_viewset_class_from_path('/api/v1/InterestRate/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_create(rate: str, effective_date: str, project: Optional[int] = None, effective_date_gregorian: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None, request=None) -> str:
    """
    ViewSet for the InterestRate class

    این Tool از API endpoint POST /api/v1/InterestRate/ استفاده می‌کند.
    Operation ID: InterestRate_create
    دسته‌بندی: InterestRate

    Args:
        project (int): پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)
        rate (str): مثال: 0.000481925679775
        effective_date (str): تاریخ شمسی به فرمت YYYY-MM-DD
        effective_date_gregorian (str): تاریخ اعمال (میلادی) (فرمت: YYYY-MM-DD)
        description (str): دلیل تغییر نرخ سود
        is_active (bool): آیا این نرخ در حال حاضر فعال است؟
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: InterestRate

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/InterestRate/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_create') or get_viewset_class_from_path('/api/v1/InterestRate/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_create یافت نشد"
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if rate is not None:
            data['rate'] = rate
        if effective_date is not None:
            data['effective_date'] = effective_date
        if effective_date_gregorian is not None:
            data['effective_date_gregorian'] = effective_date_gregorian
        if description is not None:
            data['description'] = description
        if is_active is not None:
            data['is_active'] = is_active
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_retrieve(id: int, request=None) -> str:
    """
    ViewSet for the InterestRate class

    این Tool از API endpoint GET /api/v1/InterestRate/{id}/ استفاده می‌کند.
    Operation ID: InterestRate_retrieve
    دسته‌بندی: InterestRate

    Args:
        id (int): یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: InterestRate

    مثال استفاده:
        GET /api/v1/InterestRate/1/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_retrieve') or get_viewset_class_from_path('/api/v1/InterestRate/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_update(id: int, rate: str, effective_date: str, project: Optional[int] = None, effective_date_gregorian: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None, request=None) -> str:
    """
    ViewSet for the InterestRate class

    این Tool از API endpoint PUT /api/v1/InterestRate/{id}/ استفاده می‌کند.
    Operation ID: InterestRate_update
    دسته‌بندی: InterestRate

    Args:
        id (int): یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        project (int): پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)
        rate (str): مثال: 0.000481925679775
        effective_date (str): تاریخ شمسی به فرمت YYYY-MM-DD
        effective_date_gregorian (str): تاریخ اعمال (میلادی) (فرمت: YYYY-MM-DD)
        description (str): دلیل تغییر نرخ سود
        is_active (bool): آیا این نرخ در حال حاضر فعال است؟
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: InterestRate

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/InterestRate/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_update') or get_viewset_class_from_path('/api/v1/InterestRate/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_update یافت نشد"
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if rate is not None:
            data['rate'] = rate
        if effective_date is not None:
            data['effective_date'] = effective_date
        if effective_date_gregorian is not None:
            data['effective_date_gregorian'] = effective_date_gregorian
        if description is not None:
            data['description'] = description
        if is_active is not None:
            data['is_active'] = is_active
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_partial_update(id: int, project: Optional[int] = None, rate: Optional[str] = None, effective_date: Optional[str] = None, effective_date_gregorian: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None, request=None) -> str:
    """
    ViewSet for the InterestRate class

    این Tool از API endpoint PATCH /api/v1/InterestRate/{id}/ استفاده می‌کند.
    Operation ID: InterestRate_partial_update
    دسته‌بندی: InterestRate

    Args:
        id (int): یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        project (int): پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)
        rate (str): مثال: 0.000481925679775
        effective_date (str): تاریخ شمسی به فرمت YYYY-MM-DD
        effective_date_gregorian (str): تاریخ اعمال (میلادی) (فرمت: YYYY-MM-DD)
        description (str): دلیل تغییر نرخ سود
        is_active (bool): آیا این نرخ در حال حاضر فعال است؟
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: InterestRate

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/InterestRate/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_partial_update') or get_viewset_class_from_path('/api/v1/InterestRate/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_partial_update یافت نشد"
        
        # ساخت data برای request body
        data = {}
        if project is not None:
            data['project'] = project
        if rate is not None:
            data['rate'] = rate
        if effective_date is not None:
            data['effective_date'] = effective_date
        if effective_date_gregorian is not None:
            data['effective_date_gregorian'] = effective_date_gregorian
        if description is not None:
            data['description'] = description
        if is_active is not None:
            data['is_active'] = is_active
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_destroy(id: int, request=None) -> str:
    """
    ViewSet for the InterestRate class

    این Tool از API endpoint DELETE /api/v1/InterestRate/{id}/ استفاده می‌کند.
    Operation ID: InterestRate_destroy
    دسته‌بندی: InterestRate

    Args:
        id (int): یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/InterestRate/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_destroy') or get_viewset_class_from_path('/api/v1/InterestRate/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def interestrate_current_retrieve(request=None) -> str:
    """
    دریافت نرخ سود فعال فعلی برای پروژه فعال

    این Tool از API endpoint GET /api/v1/InterestRate/current/ استفاده می‌کند.
    Operation ID: InterestRate_current_retrieve
    دسته‌بندی: InterestRate

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: InterestRate

    مثال استفاده:
        GET /api/v1/InterestRate/current/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('InterestRate_current_retrieve') or get_viewset_class_from_path('/api/v1/InterestRate/current/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای InterestRate_current_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='current_retrieve',
            request=request,
            method='GET',
            pk=pk,
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
    ViewSet for the Investor class

    این Tool از API endpoint GET /api/v1/Investor/ استفاده می‌کند.
    Operation ID: Investor_list
    دسته‌بندی: Investor

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Investor/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_list') or get_viewset_class_from_path('/api/v1/Investor/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_create(project: int, first_name: str, last_name: str, phone: str, email: Optional[str] = None, participation_type: Optional[str] = None, contract_date_shamsi: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Investor class

    این Tool از API endpoint POST /api/v1/Investor/ استفاده می‌کند.
    Operation ID: Investor_create
    دسته‌بندی: Investor

    Args:
        project (int): پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد
        first_name (str): نام
        last_name (str): نام خانوادگی
        phone (str): شماره تماس
        email (str): ایمیل (ایمیل)
        participation_type (str): نوع مشارکت
        contract_date_shamsi (str): تاریخ قرارداد (شمسی) (فرمت: YYYY-MM-DD)
        description (str): توضیحات اضافی درباره این سرمایه‌گذار
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Investor

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Investor/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_create') or get_viewset_class_from_path('/api/v1/Investor/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_retrieve(id: int, request=None) -> str:
    """
    دریافت اطلاعات کامل یک سرمایه‌گذار خاص بر اساس شناسه (ID) آن.

    ⚠️ **هشدار مهم:** این ابزار نیاز به پارامتر id دارد که باید یک عدد صحیح (int) باشد.
    هیچ‌وقت این ابزار را بدون id فراخوانی نکنید - این کار باعث خطا می‌شود.

    این Tool از API endpoint GET /api/v1/Investor/{id}/ استفاده می‌کند.
    Operation ID: Investor_retrieve
    دسته‌بندی: Investor

    Args:
        id (int): شناسه عددی سرمایه‌گذار (مثلاً 1، 2، 3 و غیره).
                 ⚠️ این پارامتر الزامی است و نمی‌تواند None یا خالی باشد.
                 اگر کاربر سوالی درباره "سرمایه‌گذار شماره X" یا "سرمایه‌گذار X" پرسید،
                 ابتدا عدد X را از سوال استخراج کنید، سپس آن را به عنوان id پاس دهید.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: اطلاعات کامل سرمایه‌گذار شامل: نام، واحدها، تراکنش‌ها و سایر جزئیات

    مثال‌های استفاده صحیح:
        - سوال: "سرمایه‌گذار شماره 1" → investor_retrieve(id=1) ✅
        - سوال: "سرمایه‌گذار 5" → investor_retrieve(id=5) ✅
        - سوال: "اطلاعات سرمایه‌گذار 10" → investor_retrieve(id=10) ✅

    مثال‌های استفاده نادرست (هرگز این کار را نکنید):
        - investor_retrieve() ❌ (بدون id - خطا می‌دهد)
        - investor_retrieve(id=None) ❌ (id نمی‌تواند None باشد)
        - investor_retrieve(id="1") ❌ (id باید int باشد، نه string)

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
        - id باید یک عدد صحیح مثبت باشد (int)
        - اگر سرمایه‌گذاری با این id وجود نداشته باشد، خطا برمی‌گرداند
        - اگر id را از سوال کاربر پیدا نکردید، ابتدا از investor_list استفاده کنید
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_retrieve') or get_viewset_class_from_path('/api/v1/Investor/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_update(id: int, project: int, first_name: str, last_name: str, phone: str, email: Optional[str] = None, participation_type: Optional[str] = None, contract_date_shamsi: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Investor class

    این Tool از API endpoint PUT /api/v1/Investor/{id}/ استفاده می‌کند.
    Operation ID: Investor_update
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        project (int): پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد
        first_name (str): نام
        last_name (str): نام خانوادگی
        phone (str): شماره تماس
        email (str): ایمیل (ایمیل)
        participation_type (str): نوع مشارکت
        contract_date_shamsi (str): تاریخ قرارداد (شمسی) (فرمت: YYYY-MM-DD)
        description (str): توضیحات اضافی درباره این سرمایه‌گذار
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Investor/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_update') or get_viewset_class_from_path('/api/v1/Investor/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_partial_update(id: int, project: Optional[int] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, participation_type: Optional[str] = None, contract_date_shamsi: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Investor class

    این Tool از API endpoint PATCH /api/v1/Investor/{id}/ استفاده می‌کند.
    Operation ID: Investor_partial_update
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        project (int): پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد
        first_name (str): نام
        last_name (str): نام خانوادگی
        phone (str): شماره تماس
        email (str): ایمیل (ایمیل)
        participation_type (str): نوع مشارکت
        contract_date_shamsi (str): تاریخ قرارداد (شمسی) (فرمت: YYYY-MM-DD)
        description (str): توضیحات اضافی درباره این سرمایه‌گذار
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Investor/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_partial_update') or get_viewset_class_from_path('/api/v1/Investor/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_destroy(id: int, request=None) -> str:
    """
    ViewSet for the Investor class

    این Tool از API endpoint DELETE /api/v1/Investor/{id}/ استفاده می‌کند.
    Operation ID: Investor_destroy
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Investor/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_destroy') or get_viewset_class_from_path('/api/v1/Investor/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_detailed_statistics_retrieve(id: int, request=None) -> str:
    """
    دریافت آمار تفصیلی سرمایه‌گذار

    این endpoint آمار کامل و تفصیلی یک سرمایه‌گذار خاص را محاسبه و برمی‌گرداند.
    
    پارامترها:
    - pk (int): شناسه یکتای سرمایه‌گذار
    - project_id (query param, اختیاری): شناسه پروژه (در صورت عدم ارسال از پروژه جاری استفاده می‌شود)
    
    خروجی شامل:
    - مجموع آورده‌ها (deposits)
    - مجموع برداشت‌ها (withdrawals)
    - مجموع سود (profits)
    - سرمایه خالص (net principal)
    - مجموع کل (grand total)
    - درصد مالکیت
    - نسبت‌های مالی
    
    سناریوهای استفاده:
    - نمایش پروفایل کامل سرمایه‌گذار
    - محاسبه سهم هر سرمایه‌گذار در پروژه
    - تهیه گزارش‌های مالی تفصیلی
    - تحلیل عملکرد سرمایه‌گذاری
    
    مثال استفاده:
    GET /api/v1/Investor/5/detailed_statistics/
    GET /api/v1/Investor/5/detailed_statistics/?project_id=1
    
    مثال خروجی:
    {
        "investor_id": 5,
        "name": "علی احمدی",
        "total_deposits": 100000000,
        "total_withdrawals": 0,
        "net_principal": 100000000,
        "total_profit": 15000000,
        "grand_total": 115000000,
        "ownership_percentage": 25.5,
        "unit_cost": 5000000
    }
    
    نکات مهم:
    - اگر سرمایه‌گذار یافت نشود، خطای 404 برمی‌گرداند
    - محاسبات بر اساس پروژه جاری یا project_id ارسالی انجام می‌شود
    - تمام مبالغ به تومان هستند

    این Tool از API endpoint GET /api/v1/Investor/{id}/detailed_statistics/ استفاده می‌کند.
    Operation ID: Investor_detailed_statistics_retrieve
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/1/detailed_statistics/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_detailed_statistics_retrieve') or get_viewset_class_from_path('/api/v1/Investor/{id}/detailed_statistics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_detailed_statistics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='detailed_statistics_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_cumulative_capital_and_unit_cost_chart_retrieve(id: int, request=None) -> str:
    """
    دریافت داده‌های نمودار ترند سرمایه موجود و هزینه واحد برای سرمایه‌گذار

    این endpoint داده‌های لازم برای نمودار ترند را محاسبه می‌کند:
    - سرمایه موجود تجمعی به میلیون تومان
    - هزینه واحد به میلیون تومان برای هر دوره

    این Tool از API endpoint GET /api/v1/Investor/{id}/investor_cumulative_capital_and_unit_cost_chart/ استفاده می‌کند.
    Operation ID: Investor_investor_cumulative_capital_and_unit_cost_chart_retrieve
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/1/investor_cumulative_capital_and_unit_cost_chart/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_investor_cumulative_capital_and_unit_cost_chart_retrieve') or get_viewset_class_from_path('/api/v1/Investor/{id}/investor_cumulative_capital_and_unit_cost_chart/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_investor_cumulative_capital_and_unit_cost_chart_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='investor_cumulative_capital_and_unit_cost_chart_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    محاسبه: (آورده + سود) / قیمت هر متر مربع واحد انتخابی

    این Tool از API endpoint GET /api/v1/Investor/{id}/ownership/ استفاده می‌کند.
    Operation ID: Investor_ownership_retrieve
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/1/ownership/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_ownership_retrieve') or get_viewset_class_from_path('/api/v1/Investor/{id}/ownership/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_ownership_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='ownership_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Investor/{id}/ratios/ استفاده می‌کند.
    Operation ID: Investor_ratios_retrieve
    دسته‌بندی: Investor

    Args:
        id (int): یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/1/ratios/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_ratios_retrieve') or get_viewset_class_from_path('/api/v1/Investor/{id}/ratios/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_ratios_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='ratios_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این endpoint از سرویس محاسباتی InvestorCalculations استفاده می‌کند
    تا آمار کامل شامل نسبت‌های سرمایه، سود و شاخص نفع را ارائه دهد.

    این Tool از API endpoint GET /api/v1/Investor/all_investors_summary/ استفاده می‌کند.
    Operation ID: Investor_all_investors_summary_retrieve
    دسته‌بندی: Investor

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/all_investors_summary/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_all_investors_summary_retrieve') or get_viewset_class_from_path('/api/v1/Investor/all_investors_summary/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_all_investors_summary_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='all_investors_summary_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_participation_stats_retrieve(request=None) -> str:
    """
    دریافت آمار مشارکت کنندگان بر اساس نوع (مالک و سرمایه گذار)

    این Tool از API endpoint GET /api/v1/Investor/participation_stats/ استفاده می‌کند.
    Operation ID: Investor_participation_stats_retrieve
    دسته‌بندی: Investor

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/participation_stats/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_participation_stats_retrieve') or get_viewset_class_from_path('/api/v1/Investor/participation_stats/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_participation_stats_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='participation_stats_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Investor/summary/ استفاده می‌کند.
    Operation ID: Investor_summary_retrieve
    دسته‌بندی: Investor

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/summary/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_summary_retrieve') or get_viewset_class_from_path('/api/v1/Investor/summary/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_summary_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='summary_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def investor_summary_ssot_retrieve(request=None) -> str:
    """
    خلاصه مالی تمام سرمایه‌گذاران با مرجع واحد (بدون SQL خام)

    این Tool از API endpoint GET /api/v1/Investor/summary_ssot/ استفاده می‌کند.
    Operation ID: Investor_summary_ssot_retrieve
    دسته‌بندی: Investor

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Investor

    مثال استفاده:
        GET /api/v1/Investor/summary_ssot/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Investor_summary_ssot_retrieve') or get_viewset_class_from_path('/api/v1/Investor/summary_ssot/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Investor_summary_ssot_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='summary_ssot_retrieve',
            request=request,
            method='GET',
            pk=pk,
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
    ViewSet for the Period class

    این Tool از API endpoint GET /api/v1/Period/ استفاده می‌کند.
    Operation ID: Period_list
    دسته‌بندی: Period

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Period/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_list') or get_viewset_class_from_path('/api/v1/Period/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_create(label: str, year: int, month_number: int, month_name: str, weight: int, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, project: int, request=None) -> str:
    """
    ViewSet for the Period class

    این Tool از API endpoint POST /api/v1/Period/ استفاده می‌کند.
    Operation ID: Period_create
    دسته‌بندی: Period

    Args:
        label (str): عنوان دوره
        year (int): سال شمسی
        month_number (int): شماره ماه
        month_name (str): نام ماه
        weight (int): وزن دوره
        start_date_shamsi (str): تاریخ شروع شمسی (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان شمسی (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع میلادی (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان میلادی (فرمت: YYYY-MM-DD)
        project (int): پروژه
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Period

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Period/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_create') or get_viewset_class_from_path('/api/v1/Period/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_retrieve(id: int, request=None) -> str:
    """
    دریافت اطلاعات کامل یک دوره خاص بر اساس شناسه (ID) آن.

    ⚠️ **هشدار مهم:** این ابزار نیاز به پارامتر id دارد که باید یک عدد صحیح (int) باشد.
    هیچ‌وقت این ابزار را بدون id فراخوانی نکنید - این کار باعث خطا می‌شود.

    این Tool از API endpoint GET /api/v1/Period/{id}/ استفاده می‌کند.
    Operation ID: Period_retrieve
    دسته‌بندی: Period

    Args:
        id (int): شناسه عددی دوره (مثلاً 1، 2، 3 و غیره).
                 ⚠️ این پارامتر الزامی است و نمی‌تواند None یا خالی باشد.
                 اگر کاربر سوالی درباره "دوره شماره X" یا "دوره X" پرسید،
                 ابتدا عدد X را از سوال استخراج کنید، سپس آن را به عنوان id پاس دهید.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: اطلاعات کامل دوره شامل: نام، تاریخ شروع و پایان، هزینه‌ها و سایر جزئیات

    مثال‌های استفاده صحیح:
        - سوال: "دوره شماره 1" → period_retrieve(id=1) ✅
        - سوال: "دوره 5" → period_retrieve(id=5) ✅
        - سوال: "اطلاعات دوره 10" → period_retrieve(id=10) ✅

    مثال‌های استفاده نادرست (هرگز این کار را نکنید):
        - period_retrieve() ❌ (بدون id - خطا می‌دهد)
        - period_retrieve(id=None) ❌ (id نمی‌تواند None باشد)
        - period_retrieve(id="1") ❌ (id باید int باشد، نه string)

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
        - id باید یک عدد صحیح مثبت باشد (int)
        - اگر دوره‌ای با این id وجود نداشته باشد، خطا برمی‌گرداند
        - اگر id را از سوال کاربر پیدا نکردید، ابتدا از period_list استفاده کنید
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_retrieve') or get_viewset_class_from_path('/api/v1/Period/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_update(id: int, label: str, year: int, month_number: int, month_name: str, weight: int, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, project: int, request=None) -> str:
    """
    ViewSet for the Period class

    این Tool از API endpoint PUT /api/v1/Period/{id}/ استفاده می‌کند.
    Operation ID: Period_update
    دسته‌بندی: Period

    Args:
        id (int): یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        label (str): عنوان دوره
        year (int): سال شمسی
        month_number (int): شماره ماه
        month_name (str): نام ماه
        weight (int): وزن دوره
        start_date_shamsi (str): تاریخ شروع شمسی (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان شمسی (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع میلادی (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان میلادی (فرمت: YYYY-MM-DD)
        project (int): پروژه
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Period

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Period/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_update') or get_viewset_class_from_path('/api/v1/Period/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_partial_update(id: int, label: Optional[str] = None, year: Optional[int] = None, month_number: Optional[int] = None, month_name: Optional[str] = None, weight: Optional[int] = None, start_date_shamsi: Optional[str] = None, end_date_shamsi: Optional[str] = None, start_date_gregorian: Optional[str] = None, end_date_gregorian: Optional[str] = None, project: Optional[int] = None, request=None) -> str:
    """
    ViewSet for the Period class

    این Tool از API endpoint PATCH /api/v1/Period/{id}/ استفاده می‌کند.
    Operation ID: Period_partial_update
    دسته‌بندی: Period

    Args:
        id (int): یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        label (str): عنوان دوره
        year (int): سال شمسی
        month_number (int): شماره ماه
        month_name (str): نام ماه
        weight (int): وزن دوره
        start_date_shamsi (str): تاریخ شروع شمسی (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان شمسی (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع میلادی (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان میلادی (فرمت: YYYY-MM-DD)
        project (int): پروژه
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Period

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Period/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_partial_update') or get_viewset_class_from_path('/api/v1/Period/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_destroy(id: int, request=None) -> str:
    """
    ViewSet for the Period class

    این Tool از API endpoint DELETE /api/v1/Period/{id}/ استفاده می‌کند.
    Operation ID: Period_destroy
    دسته‌بندی: Period

    Args:
        id (int): یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Period/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_destroy') or get_viewset_class_from_path('/api/v1/Period/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_chart_data_retrieve(request=None) -> str:
    """
    دریافت داده‌های دوره‌ای برای نمودارها (سرمایه، هزینه، فروش، مانده صندوق)

    این Tool از API endpoint GET /api/v1/Period/chart_data/ استفاده می‌کند.
    Operation ID: Period_chart_data_retrieve
    دسته‌بندی: Period

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Period

    مثال استفاده:
        GET /api/v1/Period/chart_data/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_chart_data_retrieve') or get_viewset_class_from_path('/api/v1/Period/chart_data/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_chart_data_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='chart_data_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def period_summary_retrieve(request=None) -> str:
    """
    دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقادیر تجمعی

    این endpoint خلاصه کامل مالی برای تمام دوره‌های پروژه را برمی‌گرداند.
    
    خروجی شامل:
    - اطلاعات هر دوره (شناسه، برچسب، تاریخ)
    - آورده‌های دوره و تجمعی
    - برداشت‌های دوره و تجمعی
    - سرمایه خالص دوره و تجمعی
    - سود دوره و تجمعی
    - هزینه‌های دوره و تجمعی
    - فروش/مرجوعی دوره و تجمعی
    - مانده صندوق برای هر دوره
    
    سناریوهای استفاده:
    - نمایش گزارش دوره‌ای کامل پروژه
    - تحلیل روند مالی در طول زمان
    - نمایش ترند سرمایه، هزینه و سود
    - محاسبه مانده صندوق برای هر دوره
    - تهیه گزارش‌های تفصیلی دوره‌ای
    
    مثال استفاده:
    GET /api/v1/Period/period_summary/
    
    مثال خروجی:
    {
        "success": true,
        "data": [
            {
                "period_id": 1,
                "period_label": "مرداد 1402",
                "deposits": 100000000,
                "cumulative_deposits": 100000000,
                "withdrawals": 0,
                "cumulative_withdrawals": 0,
                "net_capital": 100000000,
                "cumulative_net_capital": 100000000,
                "profits": 5000000,
                "cumulative_profits": 5000000,
                "expenses": 30000000,
                "cumulative_expenses": 30000000,
                "sales": 0,
                "cumulative_sales": 0,
                "fund_balance": 75000000
            }
        ],
        "current": {...}
    }
    
    نکات مهم:
    - فقط دوره‌های پروژه جاری را شامل می‌شود
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - دوره‌ها به ترتیب زمانی مرتب می‌شوند
    - تمام مبالغ به تومان هستند

    این Tool از API endpoint GET /api/v1/Period/period_summary/ استفاده می‌کند.
    Operation ID: Period_period_summary_retrieve
    دسته‌بندی: Period

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Period

    مثال استفاده:
        GET /api/v1/Period/period_summary/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Period_period_summary_retrieve') or get_viewset_class_from_path('/api/v1/Period/period_summary/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Period_period_summary_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='period_summary_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for PettyCashTransaction (11 endpoint) =====

@tool
def pettycashtransaction_list(request=None) -> str:
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_list
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_list') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_create(expense_type: str, transaction_type: str, amount: str, description: Optional[str] = None, receipt_number: Optional[str] = None, date_shamsi_input: Optional[str] = None, request=None) -> str:
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه

    این Tool از API endpoint POST /api/v1/PettyCashTransaction/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_create
    دسته‌بندی: PettyCashTransaction

    Args:
        expense_type (str): نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
        transaction_type (str): نوع تراکنش
        amount (str): همیشه مثبت ذخیره می‌شود
        description (str): توضیحات
        receipt_number (str): شماره فیش/رسید
        date_shamsi_input (str): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: PettyCashTransaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/PettyCashTransaction/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_create') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_retrieve(id: int, request=None) -> str:
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/{id}/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/1/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_retrieve') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_update(id: int, expense_type: str, transaction_type: str, amount: str, description: Optional[str] = None, receipt_number: Optional[str] = None, date_shamsi_input: Optional[str] = None, request=None) -> str:
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه

    این Tool از API endpoint PUT /api/v1/PettyCashTransaction/{id}/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_update
    دسته‌بندی: PettyCashTransaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        expense_type (str): نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
        transaction_type (str): نوع تراکنش
        amount (str): همیشه مثبت ذخیره می‌شود
        description (str): توضیحات
        receipt_number (str): شماره فیش/رسید
        date_shamsi_input (str): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/PettyCashTransaction/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_update') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_partial_update(id: int, expense_type: Optional[str] = None, transaction_type: Optional[str] = None, amount: Optional[str] = None, description: Optional[str] = None, receipt_number: Optional[str] = None, date_shamsi_input: Optional[str] = None, request=None) -> str:
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه

    این Tool از API endpoint PATCH /api/v1/PettyCashTransaction/{id}/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_partial_update
    دسته‌بندی: PettyCashTransaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        expense_type (str): نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
        transaction_type (str): نوع تراکنش
        amount (str): همیشه مثبت ذخیره می‌شود
        description (str): توضیحات
        receipt_number (str): شماره فیش/رسید
        date_shamsi_input (str): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/PettyCashTransaction/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_partial_update') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_destroy(id: int, request=None) -> str:
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه

    این Tool از API endpoint DELETE /api/v1/PettyCashTransaction/{id}/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_destroy
    دسته‌بندی: PettyCashTransaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/PettyCashTransaction/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_destroy') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def pettycashtransaction_balance_detail_retrieve(request=None) -> str:
    """
    دریافت وضعیت مالی یک عامل اجرایی خاص

    این endpoint وضعیت مالی تفصیلی یک عامل اجرایی (مدیر پروژه، سرپرست کارگاه، کارپرداز، انباردار، پیمانکار) را برمی‌گرداند.
    
    پارامترها:
    - expense_type (query param, الزامی): نوع عامل اجرایی (project_manager, facilities_manager, procurement, warehouse, construction_contractor)
    
    خروجی شامل:
    - نوع عامل اجرایی و برچسب فارسی آن
    - مانده فعلی (balance)
    - مجموع دریافت‌ها (total_receipts)
    - مجموع هزینه‌ها (total_expenses)
    - مجموع برگشت‌ها (total_returns)
    - وضعیت بستانکاری/بدهکاری
    
    سناریوهای استفاده:
    - نمایش وضعیت مالی هر عامل اجرایی
    - بررسی مانده تنخواه هر شخص
    - محاسبه بدهی یا طلب هر عامل
    - تهیه گزارش‌های تفصیلی تنخواه
    - مدیریت جریان نقدی عوامل اجرایی
    
    مثال استفاده:
    GET /api/v1/PettyCashTransaction/balance_detail/?expense_type=project_manager
    
    مثال خروجی:
    {
        "success": true,
        "data": {
            "expense_type": "project_manager",
            "expense_type_label": "مدیر پروژه",
            "balance": 5000000,
            "total_receipts": 20000000,
            "total_expenses": 15000000,
            "total_returns": 0,
            "is_creditor": false,
            "is_debtor": true
        }
    }
    
    نکات مهم:
    - فقط تراکنش‌های پروژه جاری را شامل می‌شود
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - اگر expense_type ارسال نشود، خطای 400 برمی‌گرداند
    - مانده مثبت = بدهکار (پول در دست دارد)
    - مانده منفی = بستانکار (بدهکار است)
    - تمام مبالغ به تومان هستند

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/balance_detail/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_balance_detail_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/balance_detail/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_balance_detail_retrieve') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/balance_detail/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_balance_detail_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='balance_detail_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/balance_trend/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_balance_trend_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/balance_trend/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_balance_trend_retrieve') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/balance_trend/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_balance_trend_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='balance_trend_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/balances/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_balances_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/balances/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_balances_retrieve') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/balances/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_balances_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='balances_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/detailed_report/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_detailed_report_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/detailed_report/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_detailed_report_retrieve') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/detailed_report/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_detailed_report_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='detailed_report_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/period_balance/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_period_balance_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: PettyCashTransaction

    مثال استفاده:
        GET /api/v1/PettyCashTransaction/period_balance/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('PettyCashTransaction_period_balance_retrieve') or get_viewset_class_from_path('/api/v1/PettyCashTransaction/period_balance/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای PettyCashTransaction_period_balance_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='period_balance_retrieve',
            request=request,
            method='GET',
            pk=pk,
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
    ViewSet for the Project class

    این Tool از API endpoint GET /api/v1/Project/ استفاده می‌کند.
    Operation ID: Project_list
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Project/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_list') or get_viewset_class_from_path('/api/v1/Project/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_create(name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Project class

    این Tool از API endpoint POST /api/v1/Project/ استفاده می‌کند.
    Operation ID: Project_create
    دسته‌بندی: Project

    Args:
        name (str): نام پروژه
        start_date_shamsi (str): تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure (str): زیر بنای کل پروژه به متر مربع
        correction_factor (str): ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage (str): درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description (str): توضیحات اضافی درباره پروژه
        color (str): رنگ نمایش پروژه (فرمت HEX)
        icon (str): نام کلاس آیکون Font Awesome (مثال: fa-building)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Project

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Project/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_create') or get_viewset_class_from_path('/api/v1/Project/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_retrieve(id: int, request=None) -> str:
    """
    ViewSet for the Project class

    این Tool از API endpoint GET /api/v1/Project/{id}/ استفاده می‌کند.
    Operation ID: Project_retrieve
    دسته‌بندی: Project

    Args:
        id (int): یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/1/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_retrieve') or get_viewset_class_from_path('/api/v1/Project/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_update(id: int, name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Project class

    این Tool از API endpoint PUT /api/v1/Project/{id}/ استفاده می‌کند.
    Operation ID: Project_update
    دسته‌بندی: Project

    Args:
        id (int): یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        name (str): نام پروژه
        start_date_shamsi (str): تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure (str): زیر بنای کل پروژه به متر مربع
        correction_factor (str): ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage (str): درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description (str): توضیحات اضافی درباره پروژه
        color (str): رنگ نمایش پروژه (فرمت HEX)
        icon (str): نام کلاس آیکون Font Awesome (مثال: fa-building)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Project/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_update') or get_viewset_class_from_path('/api/v1/Project/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_partial_update(id: int, name: Optional[str] = None, start_date_shamsi: Optional[str] = None, end_date_shamsi: Optional[str] = None, start_date_gregorian: Optional[str] = None, end_date_gregorian: Optional[str] = None, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Project class

    این Tool از API endpoint PATCH /api/v1/Project/{id}/ استفاده می‌کند.
    Operation ID: Project_partial_update
    دسته‌بندی: Project

    Args:
        id (int): یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        name (str): نام پروژه
        start_date_shamsi (str): تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure (str): زیر بنای کل پروژه به متر مربع
        correction_factor (str): ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage (str): درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description (str): توضیحات اضافی درباره پروژه
        color (str): رنگ نمایش پروژه (فرمت HEX)
        icon (str): نام کلاس آیکون Font Awesome (مثال: fa-building)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Project/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_partial_update') or get_viewset_class_from_path('/api/v1/Project/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_destroy(id: int, request=None) -> str:
    """
    ViewSet for the Project class

    این Tool از API endpoint DELETE /api/v1/Project/{id}/ استفاده می‌کند.
    Operation ID: Project_destroy
    دسته‌بندی: Project

    Args:
        id (int): یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Project/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_destroy') or get_viewset_class_from_path('/api/v1/Project/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_active_retrieve(request=None) -> str:
    """
    دریافت پروژه جاری (از session)

    این Tool از API endpoint GET /api/v1/Project/active/ استفاده می‌کند.
    Operation ID: Project_active_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/active/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_active_retrieve') or get_viewset_class_from_path('/api/v1/Project/active/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_active_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='active_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این endpoint یک تحلیل کامل و جامع از وضعیت مالی پروژه را ارائه می‌دهد.
    
    پارامترها:
    - project_id (query param, اختیاری): شناسه پروژه (در صورت عدم ارسال از پروژه جاری استفاده می‌شود)
    
    خروجی شامل:
    - اطلاعات کلی پروژه
    - آمار سرمایه‌گذاران
    - آمار تراکنش‌ها (آورده، برداشت، سود)
    - آمار هزینه‌ها
    - آمار فروش‌ها
    - محاسبات مالی (سرمایه خالص، مجموع کل، مانده صندوق)
    - متریک‌های عملکردی
    
    سناریوهای استفاده:
    - نمایش داشبورد مدیریتی پروژه
    - تهیه گزارش‌های جامع برای مدیران
    - تحلیل سلامت مالی پروژه
    - تصمیم‌گیری‌های استراتژیک
    - ارائه گزارش به سرمایه‌گذاران
    
    مثال استفاده:
    GET /api/v1/Project/comprehensive_analysis/
    GET /api/v1/Project/comprehensive_analysis/?project_id=1
    
    مثال خروجی:
    {
        "project": {
            "id": 1,
            "name": "پروژه نمونه",
            "start_date": "1402-05-01",
            "end_date": "1405-05-01"
        },
        "investors": {
            "total_count": 5,
            "total_deposits": 500000000,
            "total_withdrawals": 20000000,
            "net_principal": 480000000,
            "total_profits": 75000000
        },
        "expenses": {
            "total_amount": 300000000,
            "by_type": {...}
        },
        "financial_summary": {
            "grand_total": 555000000,
            "fund_balance": 255000000
        }
    }
    
    نکات مهم:
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - تمام محاسبات بر اساس داده‌های واقعی انجام می‌شود
    - مبالغ به تومان هستند

    این Tool از API endpoint GET /api/v1/Project/comprehensive_analysis/ استفاده می‌کند.
    Operation ID: Project_comprehensive_analysis_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/comprehensive_analysis/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_comprehensive_analysis_retrieve') or get_viewset_class_from_path('/api/v1/Project/comprehensive_analysis/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_comprehensive_analysis_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='comprehensive_analysis_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Project/cost_metrics/ استفاده می‌کند.
    Operation ID: Project_cost_metrics_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/cost_metrics/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_cost_metrics_retrieve') or get_viewset_class_from_path('/api/v1/Project/cost_metrics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_cost_metrics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='cost_metrics_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Project/current/ استفاده می‌کند.
    Operation ID: Project_current_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/current/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_current_retrieve') or get_viewset_class_from_path('/api/v1/Project/current/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_current_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='current_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_profit_metrics_retrieve(request=None) -> str:
    """
    دریافت متریک‌های سود پروژه

    این endpoint متریک‌های مختلف سود پروژه را محاسبه و برمی‌گرداند.
    
    پارامترها:
    - project_id (query param, اختیاری): شناسه پروژه (در صورت عدم ارسال از پروژه جاری استفاده می‌شود)
    
    خروجی شامل:
    - مجموع کل سود
    - سود سالانه (میانگین)
    - سود ماهانه (میانگین)
    - سود روزانه (میانگین)
    - نرخ بازدهی
    - ترند سود در طول زمان
    
    سناریوهای استفاده:
    - نمایش عملکرد مالی پروژه
    - مقایسه سودآوری پروژه‌های مختلف
    - تحلیل روند سوددهی
    - محاسبه نرخ بازدهی سرمایه‌گذاری
    - تهیه گزارش‌های تحلیلی
    
    مثال استفاده:
    GET /api/v1/Project/profit_metrics/
    GET /api/v1/Project/profit_metrics/?project_id=1
    
    مثال خروجی:
    {
        "total_profit": 75000000,
        "annual_profit": 25000000,
        "monthly_profit": 2083333.33,
        "daily_profit": 69444.44,
        "return_rate": 15.6,
        "profit_trend": [...]
    }
    
    نکات مهم:
    - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
    - محاسبات بر اساس تاریخ شروع و پایان پروژه انجام می‌شود
    - مبالغ به تومان هستند

    این Tool از API endpoint GET /api/v1/Project/profit_metrics/ استفاده می‌کند.
    Operation ID: Project_profit_metrics_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/profit_metrics/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_profit_metrics_retrieve') or get_viewset_class_from_path('/api/v1/Project/profit_metrics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_profit_metrics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='profit_metrics_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint GET /api/v1/Project/project_statistics_detailed/ استفاده می‌کند.
    Operation ID: Project_project_statistics_detailed_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/project_statistics_detailed/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_project_statistics_detailed_retrieve') or get_viewset_class_from_path('/api/v1/Project/project_statistics_detailed/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_project_statistics_detailed_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='project_statistics_detailed_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_timeline_retrieve(request=None) -> str:
    """
    محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ امروز

    این Tool از API endpoint GET /api/v1/Project/project_timeline/ استفاده می‌کند.
    Operation ID: Project_project_timeline_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/project_timeline/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_project_timeline_retrieve') or get_viewset_class_from_path('/api/v1/Project/project_timeline/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_project_timeline_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='project_timeline_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_set_active_create(name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, request=None) -> str:
    """
    تنظیم پروژه فعال

    این Tool از API endpoint POST /api/v1/Project/set_active/ استفاده می‌کند.
    Operation ID: Project_set_active_create
    دسته‌بندی: Project

    Args:
        name (str): نام پروژه
        start_date_shamsi (str): تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure (str): زیر بنای کل پروژه به متر مربع
        correction_factor (str): ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage (str): درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description (str): توضیحات اضافی درباره پروژه
        color (str): رنگ نمایش پروژه (فرمت HEX)
        icon (str): نام کلاس آیکون Font Awesome (مثال: fa-building)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Project/set_active/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_set_active_create') or get_viewset_class_from_path('/api/v1/Project/set_active/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_set_active_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='set_active_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار کامل پروژه جاری شامل اطلاعات پروژه و آمار واحدها

    این Tool از API endpoint GET /api/v1/Project/statistics/ استفاده می‌کند.
    Operation ID: Project_statistics_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    مثال استفاده:
        GET /api/v1/Project/statistics/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_statistics_retrieve') or get_viewset_class_from_path('/api/v1/Project/statistics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_statistics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='statistics_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def project_switch_create(name: str, start_date_shamsi: str, end_date_shamsi: str, start_date_gregorian: str, end_date_gregorian: str, total_infrastructure: Optional[str] = None, correction_factor: Optional[str] = None, construction_contractor_percentage: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None, icon: Optional[str] = None, request=None) -> str:
    """
    تغییر پروژه جاری کاربر

    این Tool از API endpoint POST /api/v1/Project/switch/ استفاده می‌کند.
    Operation ID: Project_switch_create
    دسته‌بندی: Project

    Args:
        name (str): نام پروژه
        start_date_shamsi (str): تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi (str): تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian (str): تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian (str): تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure (str): زیر بنای کل پروژه به متر مربع
        correction_factor (str): ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage (str): درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description (str): توضیحات اضافی درباره پروژه
        color (str): رنگ نمایش پروژه (فرمت HEX)
        icon (str): نام کلاس آیکون Font Awesome (مثال: fa-building)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Project

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Project/switch/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Project_switch_create') or get_viewset_class_from_path('/api/v1/Project/switch/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Project_switch_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='switch_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Sale (7 endpoint) =====

@tool
def sale_list(request=None) -> str:
    """
    ViewSet for the Sale class

    این Tool از API endpoint GET /api/v1/Sale/ استفاده می‌کند.
    Operation ID: Sale_list
    دسته‌بندی: Sale

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Sale/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_list') or get_viewset_class_from_path('/api/v1/Sale/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_create(project: int, period: int, amount: str, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Sale class

    این Tool از API endpoint POST /api/v1/Sale/ استفاده می‌کند.
    Operation ID: Sale_create
    دسته‌بندی: Sale

    Args:
        project (int): پروژه
        period (int): دوره
        amount (str): مبلغ
        description (str): توضیحات
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Sale

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Sale/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_create') or get_viewset_class_from_path('/api/v1/Sale/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_retrieve(id: int, request=None) -> str:
    """
    ViewSet for the Sale class

    این Tool از API endpoint GET /api/v1/Sale/{id}/ استفاده می‌کند.
    Operation ID: Sale_retrieve
    دسته‌بندی: Sale

    Args:
        id (int): یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Sale

    مثال استفاده:
        GET /api/v1/Sale/1/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_retrieve') or get_viewset_class_from_path('/api/v1/Sale/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_update(id: int, project: int, period: int, amount: str, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Sale class

    این Tool از API endpoint PUT /api/v1/Sale/{id}/ استفاده می‌کند.
    Operation ID: Sale_update
    دسته‌بندی: Sale

    Args:
        id (int): یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        project (int): پروژه
        period (int): دوره
        amount (str): مبلغ
        description (str): توضیحات
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Sale

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Sale/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_update') or get_viewset_class_from_path('/api/v1/Sale/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_partial_update(id: int, project: Optional[int] = None, period: Optional[int] = None, amount: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Sale class

    این Tool از API endpoint PATCH /api/v1/Sale/{id}/ استفاده می‌کند.
    Operation ID: Sale_partial_update
    دسته‌بندی: Sale

    Args:
        id (int): یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        project (int): پروژه
        period (int): دوره
        amount (str): مبلغ
        description (str): توضیحات
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Sale

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Sale/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_partial_update') or get_viewset_class_from_path('/api/v1/Sale/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_destroy(id: int, request=None) -> str:
    """
    ViewSet for the Sale class

    این Tool از API endpoint DELETE /api/v1/Sale/{id}/ استفاده می‌کند.
    Operation ID: Sale_destroy
    دسته‌بندی: Sale

    Args:
        id (int): یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Sale/{id}/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_destroy') or get_viewset_class_from_path('/api/v1/Sale/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def sale_total_sales_retrieve(request=None) -> str:
    """
    دریافت مجموع فروش‌ها

    این Tool از API endpoint GET /api/v1/Sale/total_sales/ استفاده می‌کند.
    Operation ID: Sale_total_sales_retrieve
    دسته‌بندی: Sale

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Sale

    مثال استفاده:
        GET /api/v1/Sale/total_sales/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Sale_total_sales_retrieve') or get_viewset_class_from_path('/api/v1/Sale/total_sales/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Sale_total_sales_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='total_sales_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for Transaction (10 endpoint) =====

@tool
def transaction_list(investor: Optional[int] = None, period: Optional[int] = None, project: Optional[int] = None, transaction_type: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the Transaction class

    این Tool از API endpoint GET /api/v1/Transaction/ استفاده می‌کند.
    Operation ID: Transaction_list
    دسته‌بندی: Transaction

    Args:
        investor (int): (اختیاری)
        period (int): (اختیاری)
        project (int): (اختیاری)
        transaction_type (str): * `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Transaction/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_list') or get_viewset_class_from_path('/api/v1/Transaction/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_list یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_create(amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    ViewSet for the Transaction class

    این Tool از API endpoint POST /api/v1/Transaction/ استفاده می‌کند.
    Operation ID: Transaction_create
    دسته‌بندی: Transaction

    Args:
        date_shamsi_input (str): (اختیاری)
        date_shamsi_raw (str): (اختیاری)
        amount (str): مبلغ
        transaction_type (str): نوع تراکنش
        description (str): توضیحات
        investor (int): (اختیاری)
        period (int): (اختیاری)
        investor_id (int): (اختیاری)
        period_id (int): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Transaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Transaction/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_create') or get_viewset_class_from_path('/api/v1/Transaction/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_retrieve(id: int, request=None) -> str:
    """
    دریافت اطلاعات کامل یک تراکنش خاص بر اساس شناسه (ID) آن.

    ⚠️ **هشدار مهم:** این ابزار نیاز به پارامتر id دارد که باید یک عدد صحیح (int) باشد.
    هیچ‌وقت این ابزار را بدون id فراخوانی نکنید - این کار باعث خطا می‌شود.

    این Tool از API endpoint GET /api/v1/Transaction/{id}/ استفاده می‌کند.
    Operation ID: Transaction_retrieve
    دسته‌بندی: Transaction

    Args:
        id (int): شناسه عددی تراکنش (مثلاً 1، 2، 3 و غیره).
                 ⚠️ این پارامتر الزامی است و نمی‌تواند None یا خالی باشد.
                 اگر کاربر سوالی درباره "تراکنش شماره X" یا "تراکنش X" پرسید،
                 ابتدا عدد X را از سوال استخراج کنید، سپس آن را به عنوان id پاس دهید.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: اطلاعات کامل تراکنش شامل: نوع، مبلغ، تاریخ، سرمایه‌گذار و سایر جزئیات

    مثال‌های استفاده صحیح:
        - سوال: "تراکنش شماره 1" → transaction_retrieve(id=1) ✅
        - سوال: "تراکنش 5" → transaction_retrieve(id=5) ✅
        - سوال: "اطلاعات تراکنش 10" → transaction_retrieve(id=10) ✅

    مثال‌های استفاده نادرست (هرگز این کار را نکنید):
        - transaction_retrieve() ❌ (بدون id - خطا می‌دهد)
        - transaction_retrieve(id=None) ❌ (id نمی‌تواند None باشد)
        - transaction_retrieve(id="1") ❌ (id باید int باشد، نه string)

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
        - id باید یک عدد صحیح مثبت باشد (int)
        - اگر تراکنشی با این id وجود نداشته باشد، خطا برمی‌گرداند
        - اگر id را از سوال کاربر پیدا نکردید، ابتدا از transaction_list استفاده کنید
        - انواع تراکنش: principal_deposit, principal_withdrawal, profit, withdrawal
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_retrieve') or get_viewset_class_from_path('/api/v1/Transaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_update(id: int, amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    ViewSet for the Transaction class

    این Tool از API endpoint PUT /api/v1/Transaction/{id}/ استفاده می‌کند.
    Operation ID: Transaction_update
    دسته‌بندی: Transaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        date_shamsi_input (str): (اختیاری)
        date_shamsi_raw (str): (اختیاری)
        amount (str): مبلغ
        transaction_type (str): نوع تراکنش
        description (str): توضیحات
        investor (int): (اختیاری)
        period (int): (اختیاری)
        investor_id (int): (اختیاری)
        period_id (int): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Transaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Transaction/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_update') or get_viewset_class_from_path('/api/v1/Transaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_partial_update(id: int, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, amount: Optional[str] = None, transaction_type: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    ViewSet for the Transaction class

    این Tool از API endpoint PATCH /api/v1/Transaction/{id}/ استفاده می‌کند.
    Operation ID: Transaction_partial_update
    دسته‌بندی: Transaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        date_shamsi_input (str): (اختیاری)
        date_shamsi_raw (str): (اختیاری)
        amount (str): مبلغ
        transaction_type (str): نوع تراکنش
        description (str): توضیحات
        investor (int): (اختیاری)
        period (int): (اختیاری)
        investor_id (int): (اختیاری)
        period_id (int): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Transaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Transaction/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_partial_update') or get_viewset_class_from_path('/api/v1/Transaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_destroy(id: int, request=None) -> str:
    """
    ViewSet for the Transaction class

    این Tool از API endpoint DELETE /api/v1/Transaction/{id}/ استفاده می‌کند.
    Operation ID: Transaction_destroy
    دسته‌بندی: Transaction

    Args:
        id (int): یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Transaction/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_destroy') or get_viewset_class_from_path('/api/v1/Transaction/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_detailed_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار تفصیلی تراکنش‌ها با فیلترهای پیشرفته

    این Tool از API endpoint GET /api/v1/Transaction/detailed_statistics/ استفاده می‌کند.
    Operation ID: Transaction_detailed_statistics_retrieve
    دسته‌بندی: Transaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Transaction

    مثال استفاده:
        GET /api/v1/Transaction/detailed_statistics/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_detailed_statistics_retrieve') or get_viewset_class_from_path('/api/v1/Transaction/detailed_statistics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_detailed_statistics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='detailed_statistics_retrieve',
            request=request,
            method='GET',
            pk=pk,
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

    این Tool از API endpoint POST /api/v1/Transaction/recalculate_construction_contractor/ استفاده می‌کند.
    Operation ID: Transaction_recalculate_construction_contractor_create
    دسته‌بندی: Transaction

    Args:
        date_shamsi_input (str): (اختیاری)
        date_shamsi_raw (str): (اختیاری)
        amount (str): مبلغ
        transaction_type (str): نوع تراکنش
        description (str): توضیحات
        investor (int): (اختیاری)
        period (int): (اختیاری)
        investor_id (int): (اختیاری)
        period_id (int): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Transaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Transaction/recalculate_construction_contractor/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_recalculate_construction_contractor_create') or get_viewset_class_from_path('/api/v1/Transaction/recalculate_construction_contractor/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_recalculate_construction_contractor_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='recalculate_construction_contractor_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_recalculate_profits_create(amount: str, transaction_type: str, date_shamsi_input: Optional[str] = None, date_shamsi_raw: Optional[str] = None, description: Optional[str] = None, investor: Optional[int] = None, period: Optional[int] = None, investor_id: Optional[int] = None, period_id: Optional[int] = None, request=None) -> str:
    """
    محاسبه مجدد سودها با نرخ سود فعال فعلی برای پروژه فعال

    این Tool از API endpoint POST /api/v1/Transaction/recalculate_profits/ استفاده می‌کند.
    Operation ID: Transaction_recalculate_profits_create
    دسته‌بندی: Transaction

    Args:
        date_shamsi_input (str): (اختیاری)
        date_shamsi_raw (str): (اختیاری)
        amount (str): مبلغ
        transaction_type (str): نوع تراکنش
        description (str): توضیحات
        investor (int): (اختیاری)
        period (int): (اختیاری)
        investor_id (int): (اختیاری)
        period_id (int): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Transaction

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Transaction/recalculate_profits/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_recalculate_profits_create') or get_viewset_class_from_path('/api/v1/Transaction/recalculate_profits/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_recalculate_profits_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='recalculate_profits_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def transaction_statistics_retrieve(request=None) -> str:
    """
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

    این Tool از API endpoint GET /api/v1/Transaction/statistics/ استفاده می‌کند.
    Operation ID: Transaction_statistics_retrieve
    دسته‌بندی: Transaction

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Transaction

    مثال استفاده:
        GET /api/v1/Transaction/statistics/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Transaction_statistics_retrieve') or get_viewset_class_from_path('/api/v1/Transaction/statistics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Transaction_statistics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='statistics_retrieve',
            request=request,
            method='GET',
            pk=pk,
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
    ViewSet for the Unit class

    این Tool از API endpoint GET /api/v1/Unit/ استفاده می‌کند.
    Operation ID: Unit_list
    دسته‌بندی: Unit

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/Unit/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_list') or get_viewset_class_from_path('/api/v1/Unit/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_create(name: str, area: str, price_per_meter: str, total_price: str, project: int, request=None) -> str:
    """
    ViewSet for the Unit class

    این Tool از API endpoint POST /api/v1/Unit/ استفاده می‌کند.
    Operation ID: Unit_create
    دسته‌بندی: Unit

    Args:
        name (str): نام واحد
        area (str): متراژ
        price_per_meter (str): قیمت هر متر
        total_price (str): قیمت نهایی
        project (int): پروژه
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: Unit

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/Unit/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_create') or get_viewset_class_from_path('/api/v1/Unit/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_retrieve(id: int, request=None) -> str:
    """
    دریافت اطلاعات کامل یک واحد خاص بر اساس شناسه (ID) آن.

    ⚠️ **هشدار مهم:** این ابزار نیاز به پارامتر id دارد که باید یک عدد صحیح (int) باشد.
    هیچ‌وقت این ابزار را بدون id فراخوانی نکنید - این کار باعث خطا می‌شود.

    این Tool از API endpoint GET /api/v1/Unit/{id}/ استفاده می‌کند.
    Operation ID: Unit_retrieve
    دسته‌بندی: Unit

    Args:
        id (int): شناسه عددی واحد (مثلاً 1، 2، 3 و غیره). 
                 ⚠️ این پارامتر الزامی است و نمی‌تواند None یا خالی باشد.
                 اگر کاربر سوالی درباره "واحد شماره X" یا "واحد X" پرسید، 
                 ابتدا عدد X را از سوال استخراج کنید، سپس آن را به عنوان id پاس دهید.
                 مثال: "واحد شماره 1" → id=1
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: اطلاعات کامل واحد شامل: نام، متراژ، قیمت، پروژه، مالکین و سایر جزئیات

    مثال‌های استفاده صحیح:
        - سوال: "اطلاعات واحد شماره 1" → unit_retrieve(id=1) ✅
        - سوال: "واحد 5" → unit_retrieve(id=5) ✅
        - سوال: "اطلاعات کامل واحد 10" → unit_retrieve(id=10) ✅

    مثال‌های استفاده نادرست (هرگز این کار را نکنید):
        - unit_retrieve() ❌ (بدون id - خطا می‌دهد)
        - unit_retrieve(id=None) ❌ (id نمی‌تواند None باشد)
        - unit_retrieve(id="1") ❌ (id باید int باشد، نه string)

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
        - id باید یک عدد صحیح مثبت باشد (int)
        - اگر واحدی با این id وجود نداشته باشد، خطا برمی‌گرداند
        - اگر id را از سوال کاربر پیدا نکردید، ابتدا از unit_list استفاده کنید
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_retrieve') or get_viewset_class_from_path('/api/v1/Unit/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_update(id: int, name: str, area: str, price_per_meter: str, total_price: str, project: int, request=None) -> str:
    """
    ViewSet for the Unit class

    این Tool از API endpoint PUT /api/v1/Unit/{id}/ استفاده می‌کند.
    Operation ID: Unit_update
    دسته‌بندی: Unit

    Args:
        id (int): یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        name (str): نام واحد
        area (str): متراژ
        price_per_meter (str): قیمت هر متر
        total_price (str): قیمت نهایی
        project (int): پروژه
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Unit

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/Unit/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_update') or get_viewset_class_from_path('/api/v1/Unit/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_partial_update(id: int, name: Optional[str] = None, area: Optional[str] = None, price_per_meter: Optional[str] = None, total_price: Optional[str] = None, project: Optional[int] = None, request=None) -> str:
    """
    ViewSet for the Unit class

    این Tool از API endpoint PATCH /api/v1/Unit/{id}/ استفاده می‌کند.
    Operation ID: Unit_partial_update
    دسته‌بندی: Unit

    Args:
        id (int): یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        name (str): نام واحد
        area (str): متراژ
        price_per_meter (str): قیمت هر متر
        total_price (str): قیمت نهایی
        project (int): پروژه
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Unit

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/Unit/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_partial_update') or get_viewset_class_from_path('/api/v1/Unit/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_destroy(id: int, request=None) -> str:
    """
    ViewSet for the Unit class

    این Tool از API endpoint DELETE /api/v1/Unit/{id}/ استفاده می‌کند.
    Operation ID: Unit_destroy
    دسته‌بندی: Unit

    Args:
        id (int): یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/Unit/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_destroy') or get_viewset_class_from_path('/api/v1/Unit/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unit_statistics_retrieve(request=None) -> str:
    """
    دریافت آمار کلی واحدها

    این Tool از API endpoint GET /api/v1/Unit/statistics/ استفاده می‌کند.
    Operation ID: Unit_statistics_retrieve
    دسته‌بندی: Unit

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: Unit

    مثال استفاده:
        GET /api/v1/Unit/statistics/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('Unit_statistics_retrieve') or get_viewset_class_from_path('/api/v1/Unit/statistics/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای Unit_statistics_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='statistics_retrieve',
            request=request,
            method='GET',
            pk=pk,
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
    ViewSet for the UnitSpecificExpense class

    این Tool از API endpoint GET /api/v1/UnitSpecificExpense/ استفاده می‌کند.
    Operation ID: UnitSpecificExpense_list
    دسته‌بندی: UnitSpecificExpense

    Args:
        project (int): (اختیاری)
        unit (int): (اختیاری)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: array

    مثال استفاده:
        GET /api/v1/UnitSpecificExpense/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('UnitSpecificExpense_list') or get_viewset_class_from_path('/api/v1/UnitSpecificExpense/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای UnitSpecificExpense_list یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}
        if project is not None:
            kwargs['project'] = project
        if unit is not None:
            kwargs['unit'] = unit
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='list',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_create(title: str, amount: str, project: Optional[int] = None, project_id: Optional[int] = None, unit: Optional[int] = None, unit_id: Optional[int] = None, date_shamsi_input: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the UnitSpecificExpense class

    این Tool از API endpoint POST /api/v1/UnitSpecificExpense/ استفاده می‌کند.
    Operation ID: UnitSpecificExpense_create
    دسته‌بندی: UnitSpecificExpense

    Args:
        project (int): (اختیاری)
        project_id (int): (اختیاری)
        unit (int): (اختیاری)
        unit_id (int): (اختیاری)
        title (str): عنوان
        date_shamsi_input (str): (اختیاری)
        amount (str): مبلغ
        description (str): توضیحات
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 201: UnitSpecificExpense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/UnitSpecificExpense/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('UnitSpecificExpense_create') or get_viewset_class_from_path('/api/v1/UnitSpecificExpense/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای UnitSpecificExpense_create یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_retrieve(id: int, request=None) -> str:
    """
    ViewSet for the UnitSpecificExpense class

    این Tool از API endpoint GET /api/v1/UnitSpecificExpense/{id}/ استفاده می‌کند.
    Operation ID: UnitSpecificExpense_retrieve
    دسته‌بندی: UnitSpecificExpense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: UnitSpecificExpense

    مثال استفاده:
        GET /api/v1/UnitSpecificExpense/1/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('UnitSpecificExpense_retrieve') or get_viewset_class_from_path('/api/v1/UnitSpecificExpense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای UnitSpecificExpense_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_update(id: int, title: str, amount: str, project: Optional[int] = None, project_id: Optional[int] = None, unit: Optional[int] = None, unit_id: Optional[int] = None, date_shamsi_input: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the UnitSpecificExpense class

    این Tool از API endpoint PUT /api/v1/UnitSpecificExpense/{id}/ استفاده می‌کند.
    Operation ID: UnitSpecificExpense_update
    دسته‌بندی: UnitSpecificExpense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        project (int): (اختیاری)
        project_id (int): (اختیاری)
        unit (int): (اختیاری)
        unit_id (int): (اختیاری)
        title (str): عنوان
        date_shamsi_input (str): (اختیاری)
        amount (str): مبلغ
        description (str): توضیحات
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: UnitSpecificExpense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PUT /api/v1/UnitSpecificExpense/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('UnitSpecificExpense_update') or get_viewset_class_from_path('/api/v1/UnitSpecificExpense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای UnitSpecificExpense_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='update',
            request=request,
            method='PUT',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_partial_update(id: int, project: Optional[int] = None, project_id: Optional[int] = None, unit: Optional[int] = None, unit_id: Optional[int] = None, title: Optional[str] = None, date_shamsi_input: Optional[str] = None, amount: Optional[str] = None, description: Optional[str] = None, request=None) -> str:
    """
    ViewSet for the UnitSpecificExpense class

    این Tool از API endpoint PATCH /api/v1/UnitSpecificExpense/{id}/ استفاده می‌کند.
    Operation ID: UnitSpecificExpense_partial_update
    دسته‌بندی: UnitSpecificExpense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        project (int): (اختیاری)
        project_id (int): (اختیاری)
        unit (int): (اختیاری)
        unit_id (int): (اختیاری)
        title (str): عنوان
        date_shamsi_input (str): (اختیاری)
        amount (str): مبلغ
        description (str): توضیحات
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی
        - 200: UnitSpecificExpense

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        PATCH /api/v1/UnitSpecificExpense/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('UnitSpecificExpense_partial_update') or get_viewset_class_from_path('/api/v1/UnitSpecificExpense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای UnitSpecificExpense_partial_update یافت نشد"
        
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
        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='partial_update',
            request=request,
            method='PATCH',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def unitspecificexpense_destroy(id: int, request=None) -> str:
    """
    ViewSet for the UnitSpecificExpense class

    این Tool از API endpoint DELETE /api/v1/UnitSpecificExpense/{id}/ استفاده می‌کند.
    Operation ID: UnitSpecificExpense_destroy
    دسته‌بندی: UnitSpecificExpense

    Args:
        id (int): یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        DELETE /api/v1/UnitSpecificExpense/{id}/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('UnitSpecificExpense_destroy') or get_viewset_class_from_path('/api/v1/UnitSpecificExpense/{id}/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای UnitSpecificExpense_destroy یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = id if id is not None else None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='destroy',
            request=request,
            method='DELETE',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for auth (6 endpoint) =====

@tool
def auth_change_password_create(request=None) -> str:
    """
    تغییر رمز عبور

    این Tool از API endpoint POST /api/v1/auth/change-password/ استفاده می‌کند.
    Operation ID: auth_change_password_create
    دسته‌بندی: auth

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/auth/change-password/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('auth_change_password_create') or get_viewset_class_from_path('/api/v1/auth/change-password/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای auth_change_password_create یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='change_password_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_csrf_retrieve(request=None) -> str:
    """
    دریافت CSRF Token

    این Tool از API endpoint GET /api/v1/auth/csrf/ استفاده می‌کند.
    Operation ID: auth_csrf_retrieve
    دسته‌بندی: auth

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    مثال استفاده:
        GET /api/v1/auth/csrf/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('auth_csrf_retrieve') or get_viewset_class_from_path('/api/v1/auth/csrf/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای auth_csrf_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='csrf_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_login_create(request=None) -> str:
    """
    ورود به API

    این Tool از API endpoint POST /api/v1/auth/login/ استفاده می‌کند.
    Operation ID: auth_login_create
    دسته‌بندی: auth

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/auth/login/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('auth_login_create') or get_viewset_class_from_path('/api/v1/auth/login/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای auth_login_create یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='login_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_logout_create(request=None) -> str:
    """
    خروج از API

    این Tool از API endpoint POST /api/v1/auth/logout/ استفاده می‌کند.
    Operation ID: auth_logout_create
    دسته‌بندی: auth

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/auth/logout/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('auth_logout_create') or get_viewset_class_from_path('/api/v1/auth/logout/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای auth_logout_create یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='logout_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_register_create(request=None) -> str:
    """
    ثبت‌نام کاربر جدید (فقط برای ادمین‌ها)

    این Tool از API endpoint POST /api/v1/auth/register/ استفاده می‌کند.
    Operation ID: auth_register_create
    دسته‌بندی: auth

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    Raises:
        ValidationError: اگر ورودی‌ها نامعتبر باشند
        PermissionDenied: اگر کاربر دسترسی نداشته باشد

    مثال استفاده:
        POST /api/v1/auth/register/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('auth_register_create') or get_viewset_class_from_path('/api/v1/auth/register/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای auth_register_create یافت نشد"
        
        # ساخت data برای request body
        data = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='register_create',
            request=request,
            method='POST',
            data=data,
            pk=pk
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

@tool
def auth_user_retrieve(request=None) -> str:
    """
    دریافت اطلاعات کاربر فعلی

    این Tool از API endpoint GET /api/v1/auth/user/ استفاده می‌کند.
    Operation ID: auth_user_retrieve
    دسته‌بندی: auth

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    مثال استفاده:
        GET /api/v1/auth/user/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('auth_user_retrieve') or get_viewset_class_from_path('/api/v1/auth/user/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای auth_user_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='user_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for comprehensive (1 endpoint) =====

@tool
def comprehensive_analysis_retrieve(request=None) -> str:
    """
    دریافت تحلیل جامع پروژه

    این Tool از API endpoint GET /api/v1/comprehensive/comprehensive_analysis/ استفاده می‌کند.
    Operation ID: comprehensive_comprehensive_analysis_retrieve
    دسته‌بندی: comprehensive

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    مثال استفاده:
        GET /api/v1/comprehensive/comprehensive_analysis/
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('comprehensive_comprehensive_analysis_retrieve') or get_viewset_class_from_path('/api/v1/comprehensive/comprehensive_analysis/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای comprehensive_comprehensive_analysis_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='comprehensive_analysis_retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# ===== Tools for status (1 endpoint) =====

@tool
def status_retrieve(request=None) -> str:
    """
    بررسی وضعیت API

    این Tool از API endpoint GET /api/v1/status/ استفاده می‌کند.
    Operation ID: status_retrieve
    دسته‌بندی: status

    Args:
        (بدون پارامتر)
        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        str: نتیجه عملیات به صورت رشته متنی

    مثال استفاده:
        GET /api/v1/status/

    نکات مهم:
        - نیاز به احراز هویت: cookieAuth, tokenAuth
    """
    try:
        # پیدا کردن ViewSet class
        from assistant.viewset_helper import (
            get_viewset_class_from_operation_id,
            get_viewset_class_from_path,
            call_viewset_action,
            response_to_string
        )
        
        viewset_class = get_viewset_class_from_operation_id('status_retrieve') or get_viewset_class_from_path('/api/v1/status/')
        
        if not viewset_class:
            return f"❌ خطا: ViewSet برای status_retrieve یافت نشد"
        
        # ساخت kwargs برای query parameters
        kwargs = {}

        
        # فراخوانی ViewSet action
        pk = None
        response = call_viewset_action(
            viewset_class=viewset_class,
            action_name='retrieve',
            request=request,
            method='GET',
            pk=pk,
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {str(e)}"

