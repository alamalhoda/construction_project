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
    ViewSet for the Expense class

    این Tool از API endpoint GET /api/v1/Expense/ استفاده می‌کند.
    Operation ID: Expense_list
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Expense class

    این Tool از API endpoint POST /api/v1/Expense/ استفاده می‌کند.
    Operation ID: Expense_create
    دسته‌بندی: Expense

    Args:
        project: int - پروژه
        expense_type: str - نوع هزینه
        amount: str - مبلغ
        description: str - توضیحات
        period: int - دوره
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Expense class

    این Tool از API endpoint GET /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_retrieve
    دسته‌بندی: Expense

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Expense class

    این Tool از API endpoint PUT /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_update
    دسته‌بندی: Expense

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        project: int - پروژه
        expense_type: str - نوع هزینه
        amount: str - مبلغ
        description: str - توضیحات
        period: int - دوره
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Expense class

    این Tool از API endpoint PATCH /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_partial_update
    دسته‌بندی: Expense

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        project: int - پروژه
        expense_type: str - نوع هزینه
        amount: str - مبلغ
        description: str - توضیحات
        period: int - دوره
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Expense class

    این Tool از API endpoint DELETE /api/v1/Expense/{id}/ استفاده می‌کند.
    Operation ID: Expense_destroy
    دسته‌بندی: Expense

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    دریافت داده‌های لیست هزینه ها

    این Tool از API endpoint GET /api/v1/Expense/dashboard_data/ استفاده می‌کند.
    Operation ID: Expense_dashboard_data_retrieve
    دسته‌بندی: Expense

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    به‌روزرسانی هزینه

    این Tool از API endpoint POST /api/v1/Expense/update_expense/ استفاده می‌کند.
    Operation ID: Expense_update_expense_create
    دسته‌بندی: Expense

    Args:
        project: int - پروژه
        expense_type: str - نوع هزینه
        amount: str - مبلغ
        description: str - توضیحات
        period: int - دوره
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Expense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        project: int - پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)
        rate: str - مثال: 0.000481925679775
        effective_date: str - تاریخ شمسی به فرمت YYYY-MM-DD
        effective_date_gregorian: str - تاریخ اعمال (میلادی) (فرمت: YYYY-MM-DD)
        description: str - دلیل تغییر نرخ سود
        is_active: bool - آیا این نرخ در حال حاضر فعال است؟
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: InterestRate
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: InterestRate
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        project: int - پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)
        rate: str - مثال: 0.000481925679775
        effective_date: str - تاریخ شمسی به فرمت YYYY-MM-DD
        effective_date_gregorian: str - تاریخ اعمال (میلادی) (فرمت: YYYY-MM-DD)
        description: str - دلیل تغییر نرخ سود
        is_active: bool - آیا این نرخ در حال حاضر فعال است؟
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: InterestRate
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        project: int - پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)
        rate: str - مثال: 0.000481925679775
        effective_date: str - تاریخ شمسی به فرمت YYYY-MM-DD
        effective_date_gregorian: str - تاریخ اعمال (میلادی) (فرمت: YYYY-MM-DD)
        description: str - دلیل تغییر نرخ سود
        is_active: bool - آیا این نرخ در حال حاضر فعال است؟
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: InterestRate
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این نرخ سود را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: InterestRate
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        project: int - پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد
        first_name: str - نام
        last_name: str - نام خانوادگی
        phone: str - شماره تماس
        email: str - ایمیل (ایمیل)
        participation_type: str - نوع مشارکت
        contract_date_shamsi: str - تاریخ قرارداد (شمسی) (فرمت: YYYY-MM-DD)
        description: str - توضیحات اضافی درباره این سرمایه‌گذار
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Investor class

    این Tool از API endpoint GET /api/v1/Investor/{id}/ استفاده می‌کند.
    Operation ID: Investor_retrieve
    دسته‌بندی: Investor
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        project: int - پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد
        first_name: str - نام
        last_name: str - نام خانوادگی
        phone: str - شماره تماس
        email: str - ایمیل (ایمیل)
        participation_type: str - نوع مشارکت
        contract_date_shamsi: str - تاریخ قرارداد (شمسی) (فرمت: YYYY-MM-DD)
        description: str - توضیحات اضافی درباره این سرمایه‌گذار
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        project: int - پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد
        first_name: str - نام
        last_name: str - نام خانوادگی
        phone: str - شماره تماس
        email: str - ایمیل (ایمیل)
        participation_type: str - نوع مشارکت
        contract_date_shamsi: str - تاریخ قرارداد (شمسی) (فرمت: YYYY-MM-DD)
        description: str - توضیحات اضافی درباره این سرمایه‌گذار
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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

    این Tool از API endpoint GET /api/v1/Investor/{id}/detailed_statistics/ استفاده می‌کند.
    Operation ID: Investor_detailed_statistics_retrieve
    دسته‌بندی: Investor
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
def investor_investor_cumulative_capital_and_unit_cost_chart_retrieve(id: int, request=None) -> str:
    """
    دریافت داده‌های نمودار ترند سرمایه موجود و هزینه واحد برای سرمایه‌گذار

این endpoint داده‌های لازم برای نمودار ترند را محاسبه می‌کند:
- سرمایه موجود تجمعی به میلیون تومان
- هزینه واحد به میلیون تومان برای هر دوره

    این Tool از API endpoint GET /api/v1/Investor/{id}/investor_cumulative_capital_and_unit_cost_chart/ استفاده می‌کند.
    Operation ID: Investor_investor_cumulative_capital_and_unit_cost_chart_retrieve
    دسته‌بندی: Investor
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این سرمایه‌گذار را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    خلاصه مالی تمام سرمایه‌گذاران - نسخه مرجع واحد (جایگزین SQL خام)

    این Tool از API endpoint GET /api/v1/Investor/summary/ استفاده می‌کند.
    Operation ID: Investor_summary_retrieve
    دسته‌بندی: Investor
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Investor
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        label: str - عنوان دوره
        year: int - سال شمسی
        month_number: int - شماره ماه
        month_name: str - نام ماه
        weight: int - وزن دوره
        start_date_shamsi: str - تاریخ شروع شمسی (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان شمسی (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع میلادی (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان میلادی (فرمت: YYYY-MM-DD)
        project: int - پروژه
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Period
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Period class

    این Tool از API endpoint GET /api/v1/Period/{id}/ استفاده می‌کند.
    Operation ID: Period_retrieve
    دسته‌بندی: Period
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Period
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        label: str - عنوان دوره
        year: int - سال شمسی
        month_number: int - شماره ماه
        month_name: str - نام ماه
        weight: int - وزن دوره
        start_date_shamsi: str - تاریخ شروع شمسی (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان شمسی (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع میلادی (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان میلادی (فرمت: YYYY-MM-DD)
        project: int - پروژه
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Period
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        label: str - عنوان دوره
        year: int - سال شمسی
        month_number: int - شماره ماه
        month_name: str - نام ماه
        weight: int - وزن دوره
        start_date_shamsi: str - تاریخ شروع شمسی (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان شمسی (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع میلادی (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان میلادی (فرمت: YYYY-MM-DD)
        project: int - پروژه
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Period
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این دوره را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Period
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
def period_period_summary_retrieve(request=None) -> str:
    """
    دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقادیر تجمعی

    این Tool از API endpoint GET /api/v1/Period/period_summary/ استفاده می‌کند.
    Operation ID: Period_period_summary_retrieve
    دسته‌بندی: Period
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Period
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        expense_type: str - نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
        transaction_type: str - نوع تراکنش
        amount: str - همیشه مثبت ذخیره می‌شود
        description: str - توضیحات
        receipt_number: str - شماره فیش/رسید
        date_shamsi_input: str - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        expense_type: str - نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
        transaction_type: str - نوع تراکنش
        amount: str - همیشه مثبت ذخیره می‌شود
        description: str - توضیحات
        receipt_number: str - شماره فیش/رسید
        date_shamsi_input: str - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        expense_type: str - نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود

* `project_manager` - مدیر پروژه
* `facilities_manager` - سرپرست کارگاه
* `procurement` - کارپرداز
* `warehouse` - انباردار
* `construction_contractor` - پیمان ساختمان
* `other` - سایر
        transaction_type: str - نوع تراکنش
        amount: str - همیشه مثبت ذخیره می‌شود
        description: str - توضیحات
        receipt_number: str - شماره فیش/رسید
        date_shamsi_input: str - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این تراکنش تنخواه را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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

    این Tool از API endpoint GET /api/v1/PettyCashTransaction/balance_detail/ استفاده می‌کند.
    Operation ID: PettyCashTransaction_balance_detail_retrieve
    دسته‌بندی: PettyCashTransaction

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: PettyCashTransaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        name: str - نام پروژه
        start_date_shamsi: str - تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure: str - زیر بنای کل پروژه به متر مربع
        correction_factor: str - ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage: str - درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description: str - توضیحات اضافی درباره پروژه
        color: str - رنگ نمایش پروژه (فرمت HEX)
        icon: str - نام کلاس آیکون Font Awesome (مثال: fa-building)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        name: str - نام پروژه
        start_date_shamsi: str - تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure: str - زیر بنای کل پروژه به متر مربع
        correction_factor: str - ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage: str - درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description: str - توضیحات اضافی درباره پروژه
        color: str - رنگ نمایش پروژه (فرمت HEX)
        icon: str - نام کلاس آیکون Font Awesome (مثال: fa-building)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        name: str - نام پروژه
        start_date_shamsi: str - تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure: str - زیر بنای کل پروژه به متر مربع
        correction_factor: str - ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage: str - درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description: str - توضیحات اضافی درباره پروژه
        color: str - رنگ نمایش پروژه (فرمت HEX)
        icon: str - نام کلاس آیکون Font Awesome (مثال: fa-building)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این پروژه را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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

    این Tool از API endpoint GET /api/v1/Project/comprehensive_analysis/ استفاده می‌کند.
    Operation ID: Project_comprehensive_analysis_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    دریافت متریک‌های سود (کل، سالانه، ماهانه، روزانه)

    این Tool از API endpoint GET /api/v1/Project/profit_metrics/ استفاده می‌کند.
    Operation ID: Project_profit_metrics_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
def project_project_statistics_detailed_retrieve(request=None) -> str:
    """
    دریافت آمار تفصیلی پروژه

    این Tool از API endpoint GET /api/v1/Project/project_statistics_detailed/ استفاده می‌کند.
    Operation ID: Project_project_statistics_detailed_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
def project_project_timeline_retrieve(request=None) -> str:
    """
    محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ امروز

    این Tool از API endpoint GET /api/v1/Project/project_timeline/ استفاده می‌کند.
    Operation ID: Project_project_timeline_retrieve
    دسته‌بندی: Project

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        name: str - نام پروژه
        start_date_shamsi: str - تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure: str - زیر بنای کل پروژه به متر مربع
        correction_factor: str - ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage: str - درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description: str - توضیحات اضافی درباره پروژه
        color: str - رنگ نمایش پروژه (فرمت HEX)
        icon: str - نام کلاس آیکون Font Awesome (مثال: fa-building)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        name: str - نام پروژه
        start_date_shamsi: str - تاریخ شروع (شمسی) (فرمت: YYYY-MM-DD)
        end_date_shamsi: str - تاریخ پایان (شمسی) (فرمت: YYYY-MM-DD)
        start_date_gregorian: str - تاریخ شروع (میلادی) (فرمت: YYYY-MM-DD)
        end_date_gregorian: str - تاریخ پایان (میلادی) (فرمت: YYYY-MM-DD)
        total_infrastructure: str - زیر بنای کل پروژه به متر مربع
        correction_factor: str - ضریب اصلاحی برای محاسبات پروژه
        construction_contractor_percentage: str - درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)
        description: str - توضیحات اضافی درباره پروژه
        color: str - رنگ نمایش پروژه (فرمت HEX)
        icon: str - نام کلاس آیکون Font Awesome (مثال: fa-building)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Project
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        project: int - پروژه
        period: int - دوره
        amount: str - مبلغ
        description: str - توضیحات
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Sale
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Sale
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        project: int - پروژه
        period: int - دوره
        amount: str - مبلغ
        description: str - توضیحات
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Sale
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        project: int - پروژه
        period: int - دوره
        amount: str - مبلغ
        description: str - توضیحات
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Sale
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        id: int - یک مقداد عدد یکتا که این فروش/مرجوعی را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Sale
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        investor: int - (اختیاری)
        period: int - (اختیاری)
        project: int - (اختیاری)
        transaction_type: str - * `principal_deposit` - آورده
* `loan_deposit` - آورده وام
* `principal_withdrawal` - خروج از سرمایه
* `profit_accrual` - سود
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        date_shamsi_input: str - (اختیاری)
        date_shamsi_raw: str - (اختیاری)
        amount: str - مبلغ
        transaction_type: str - نوع تراکنش
        description: str - توضیحات
        investor: int - (اختیاری)
        period: int - (اختیاری)
        investor_id: int - (اختیاری)
        period_id: int - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Transaction class

    این Tool از API endpoint GET /api/v1/Transaction/{id}/ استفاده می‌کند.
    Operation ID: Transaction_retrieve
    دسته‌بندی: Transaction
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        date_shamsi_input: str - (اختیاری)
        date_shamsi_raw: str - (اختیاری)
        amount: str - مبلغ
        transaction_type: str - نوع تراکنش
        description: str - توضیحات
        investor: int - (اختیاری)
        period: int - (اختیاری)
        investor_id: int - (اختیاری)
        period_id: int - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        date_shamsi_input: str - (اختیاری)
        date_shamsi_raw: str - (اختیاری)
        amount: str - مبلغ
        transaction_type: str - نوع تراکنش
        description: str - توضیحات
        investor: int - (اختیاری)
        period: int - (اختیاری)
        investor_id: int - (اختیاری)
        period_id: int - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این تراکنش را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        date_shamsi_input: str - (اختیاری)
        date_shamsi_raw: str - (اختیاری)
        amount: str - مبلغ
        transaction_type: str - نوع تراکنش
        description: str - توضیحات
        investor: int - (اختیاری)
        period: int - (اختیاری)
        investor_id: int - (اختیاری)
        period_id: int - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        date_shamsi_input: str - (اختیاری)
        date_shamsi_raw: str - (اختیاری)
        amount: str - مبلغ
        transaction_type: str - نوع تراکنش
        description: str - توضیحات
        investor: int - (اختیاری)
        period: int - (اختیاری)
        investor_id: int - (اختیاری)
        period_id: int - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    آمار کلی تراکنش‌ها برای پروژه جاری

    این Tool از API endpoint GET /api/v1/Transaction/statistics/ استفاده می‌کند.
    Operation ID: Transaction_statistics_retrieve
    دسته‌بندی: Transaction
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Transaction
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        name: str - نام واحد
        area: str - متراژ
        price_per_meter: str - قیمت هر متر
        total_price: str - قیمت نهایی
        project: int - پروژه
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: Unit
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    ViewSet for the Unit class

    این Tool از API endpoint GET /api/v1/Unit/{id}/ استفاده می‌کند.
    Operation ID: Unit_retrieve
    دسته‌بندی: Unit
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Unit
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        name: str - نام واحد
        area: str - متراژ
        price_per_meter: str - قیمت هر متر
        total_price: str - قیمت نهایی
        project: int - پروژه
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Unit
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        name: str - نام واحد
        area: str - متراژ
        price_per_meter: str - قیمت هر متر
        total_price: str - قیمت نهایی
        project: int - پروژه
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Unit
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این واحد را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: Unit
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        project: int - (اختیاری)
        unit: int - (اختیاری)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: array
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        project: int - (اختیاری)
        project_id: int - (اختیاری)
        unit: int - (اختیاری)
        unit_id: int - (اختیاری)
        title: str - عنوان
        date_shamsi_input: str - (اختیاری)
        amount: str - مبلغ
        description: str - توضیحات
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 201: UnitSpecificExpense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: UnitSpecificExpense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        project: int - (اختیاری)
        project_id: int - (اختیاری)
        unit: int - (اختیاری)
        unit_id: int - (اختیاری)
        title: str - عنوان
        date_shamsi_input: str - (اختیاری)
        amount: str - مبلغ
        description: str - توضیحات
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: UnitSpecificExpense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        project: int - (اختیاری)
        project_id: int - (اختیاری)
        unit: int - (اختیاری)
        unit_id: int - (اختیاری)
        title: str - عنوان
        date_shamsi_input: str - (اختیاری)
        amount: str - مبلغ
        description: str - توضیحات
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
        کدهای وضعیت ممکن:
        - 200: UnitSpecificExpense
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        id: int - یک مقداد عدد یکتا که این هزینه اختصاصی واحد را شناسایی میکند.
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
def comprehensive_comprehensive_analysis_retrieve(request=None) -> str:
    """
    دریافت تحلیل جامع پروژه

    این Tool از API endpoint GET /api/v1/comprehensive/comprehensive_analysis/ استفاده می‌کند.
    Operation ID: comprehensive_comprehensive_analysis_retrieve
    دسته‌بندی: comprehensive

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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
    نیاز به احراز هویت: cookieAuth, tokenAuth

    Args:
        (بدون پارامتر)
        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)

    Returns:
        نتیجه عملیات به صورت رشته متنی
    """
    try:
        # پیدا کردن ViewSet class
        from construction.assistant.viewset_helper import (
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

