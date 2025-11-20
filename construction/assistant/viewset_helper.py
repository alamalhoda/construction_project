"""
Helper برای فراخوانی مستقیم ViewSet methods
این ماژول امکان فراخوانی ViewSet methods را بدون HTTP overhead فراهم می‌کند
و Single Source of Truth را حفظ می‌کند
"""

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import force_authenticate
from rest_framework.response import Response
import json
import importlib


def get_viewset_class_from_operation_id(operation_id: str):
    """
    پیدا کردن ViewSet class از operation_id
    
    Args:
        operation_id: Operation ID از OpenAPI schema (مثل Expense_list, Investor_create)
    
    Returns:
        ViewSet class یا None
    """
    try:
        # استخراج نام ViewSet از operation_id
        # مثال: Expense_list -> ExpenseViewSet
        parts = operation_id.split('_')
        if len(parts) >= 2:
            viewset_name = parts[0] + 'ViewSet'
            
            # Import کردن api module
            from construction import api
            
            # پیدا کردن ViewSet class
            viewset_class = getattr(api, viewset_name, None)
            return viewset_class
    except Exception:
        pass
    
    return None


def get_viewset_class_from_path(path: str):
    """
    پیدا کردن ViewSet class از API path
    
    Args:
        path: API path (مثل /api/v1/Expense/)
    
    Returns:
        ViewSet class یا None
    """
    try:
        # استخراج نام resource از path
        # مثال: /api/v1/Expense/ -> ExpenseViewSet
        parts = path.strip('/').split('/')
        if len(parts) >= 3:
            resource_name = parts[-1]  # Expense
            
            # تبدیل به ViewSet name
            viewset_name = resource_name + 'ViewSet'
            
            # Import کردن api module
            from construction import api
            
            # پیدا کردن ViewSet class
            viewset_class = getattr(api, viewset_name, None)
            return viewset_class
    except Exception:
        pass
    
    return None


def call_viewset_action(viewset_class, action_name, request=None, method='GET', data=None, pk=None, **kwargs):
    """
    فراخوانی مستقیم یک ViewSet action
    
    این تابع از Single Source of Truth استفاده می‌کند و مستقیماً ViewSet methods را فراخوانی می‌کند.
    این کار باعث می‌شود که:
    - منطق فقط در ViewSets باشد (SST)
    - تغییرات در ViewSets خودکار در Tools اعمال شود
    - بدون HTTP overhead کار کند
    
    Args:
        viewset_class: کلاس ViewSet
        action_name: نام action (list, retrieve, create, update, destroy, یا custom action)
        request: درخواست HTTP (اگر None باشد، یک request mock ساخته می‌شود)
        method: متد HTTP (GET, POST, PUT, PATCH, DELETE)
        data: داده‌های request body (برای POST, PUT, PATCH)
        pk: primary key (برای retrieve, update, destroy)
        **kwargs: پارامترهای اضافی برای action (مثل query parameters)
    
    Returns:
        Response object از ViewSet
    """
    from rest_framework.request import Request
    from rest_framework.parsers import JSONParser
    
    # ساخت request factory
    factory = RequestFactory()
    
    # ساخت URL path
    resource_name = viewset_class.__name__.replace("ViewSet", "")
    if pk:
        path = f'/api/v1/{resource_name}/{pk}/'
    else:
        path = f'/api/v1/{resource_name}/'
    
    # ساخت request بر اساس method
    if method == 'GET':
        request_obj = factory.get(path, kwargs)
    elif method == 'POST':
        request_obj = factory.post(path, data=data or {}, content_type='application/json')
    elif method == 'PUT':
        request_obj = factory.put(path, data=data or {}, content_type='application/json')
    elif method == 'PATCH':
        request_obj = factory.patch(path, data=data or {}, content_type='application/json')
    elif method == 'DELETE':
        request_obj = factory.delete(path)
    else:
        request_obj = factory.get(path)
    
    # اگر request اصلی داده شده، از user و session آن استفاده کن
    if request:
        request_obj.user = request.user if hasattr(request, 'user') and request.user.is_authenticated else AnonymousUser()
        request_obj.session = request.session if hasattr(request, 'session') else {}
    else:
        request_obj.user = AnonymousUser()
        request_obj.session = {}
    
    # اضافه کردن query parameters به request
    if kwargs:
        request_obj.GET = request_obj.GET.copy()
        for key, value in kwargs.items():
            request_obj.GET[key] = value
    
    # تبدیل به DRF Request object
    drf_request = Request(request_obj)
    
    # تنظیم data برای POST/PUT/PATCH
    if data and method in ['POST', 'PUT', 'PATCH']:
        drf_request._full_data = data
    
    # Instantiate ViewSet
    viewset = viewset_class()
    viewset.request = drf_request
    viewset.format_kwarg = None
    viewset.action = action_name
    
    # تنظیم kwargs برای actions که نیاز به pk دارند
    if pk:
        viewset.kwargs = {'pk': pk}
    
    # فراخوانی action
    try:
        if action_name == 'list':
            response = viewset.list(drf_request)
        elif action_name == 'retrieve':
            response = viewset.retrieve(drf_request, pk=pk)
        elif action_name == 'create':
            response = viewset.create(drf_request)
        elif action_name == 'update':
            response = viewset.update(drf_request, pk=pk)
        elif action_name == 'partial_update':
            response = viewset.partial_update(drf_request, pk=pk)
        elif action_name == 'destroy':
            response = viewset.destroy(drf_request, pk=pk)
        else:
            # Custom action
            action_method = getattr(viewset, action_name, None)
            if action_method:
                if pk:
                    response = action_method(drf_request, pk=pk)
                else:
                    response = action_method(drf_request)
            else:
                raise ValueError(f"Action '{action_name}' not found in {viewset_class.__name__}")
    except Exception as e:
        # در صورت خطا، یک Response با خطا برگردان
        from rest_framework.response import Response
        return Response({'error': str(e)}, status=500)
    
    return response


def translate_participation_type(data):
    """
    تبدیل participation_type از انگلیسی به فارسی در داده‌ها
    
    Args:
        data: داده‌های dict یا list
    
    Returns:
        داده‌های تبدیل شده
    """
    PARTICIPATION_TYPE_MAP = {
        'owner': 'مالک',
        'investor': 'سرمایه‌گذار'
    }
    
    if isinstance(data, dict):
        # اگر dict است، به صورت recursive تبدیل کن
        result = {}
        for key, value in data.items():
            if key == 'participation_type' and value in PARTICIPATION_TYPE_MAP:
                result[key] = PARTICIPATION_TYPE_MAP[value]
            elif isinstance(value, (dict, list)):
                result[key] = translate_participation_type(value)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        # اگر list است، هر آیتم را تبدیل کن
        return [translate_participation_type(item) for item in data]
    else:
        return data


def response_to_string(response: Response) -> str:
    """
    تبدیل Response object به string برای نمایش به کاربر
    
    Args:
        response: Response object از ViewSet
    
    Returns:
        رشته متنی قابل نمایش
    """
    if not isinstance(response, Response):
        return str(response)
    
    # بررسی status code
    status_code = response.status_code
    
    if status_code >= 400:
        # خطا
        error_msg = "❌ خطا: "
        if hasattr(response, 'data'):
            if isinstance(response.data, dict):
                error = response.data.get('error', response.data.get('detail', str(response.data)))
                error_msg += str(error)
            else:
                error_msg += str(response.data)
        else:
            error_msg += f"خطای {status_code}"
        return error_msg
    
    # موفقیت
    success_msg = "✅ عملیات با موفقیت انجام شد"
    
    if hasattr(response, 'data'):
        data = response.data
        
        # تبدیل participation_type به فارسی
        data = translate_participation_type(data)
        
        # اگر data یک dict است، اطلاعات مفید را استخراج کن
        if isinstance(data, dict):
            # اگر success message دارد
            if 'success' in data and data['success']:
                success_msg = data.get('message', success_msg)
            
            # اگر id دارد (برای create)
            if 'id' in data:
                success_msg += f"\n📋 شناسه: #{data['id']}"
            
            # اگر اطلاعات مفید دیگری دارد
            if 'name' in data:
                success_msg += f"\n📝 نام: {data['name']}"
            
            # تبدیل به JSON برای نمایش کامل
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
                success_msg += f"\n\n📊 جزئیات:\n{data_str}"
            except:
                success_msg += f"\n\n📊 جزئیات: {str(data)}"
        
        elif isinstance(data, list):
            # لیست
            count = len(data)
            success_msg = f"📋 تعداد نتایج: {count}"
            if count > 0:
                # نمایش همه نتایج
                try:
                    all_data_str = json.dumps(data, ensure_ascii=False, indent=2)
                    success_msg += f"\n\n📊 نتایج:\n{all_data_str}"
                except:
                    success_msg += f"\n\n📊 نتایج: {str(data)}"
        
        else:
            success_msg += f"\n\n📊 نتیجه: {str(data)}"
    
    return success_msg

