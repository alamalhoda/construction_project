"""
Helper برای فراخوانی ViewSet methods
این ماژول امکان فراخوانی ViewSet methods را از طریق HTTP فراهم می‌کند
و Single Source of Truth را حفظ می‌کند
"""

from django.test import Client
from rest_framework.response import Response
import json
import logging

logger = logging.getLogger(__name__)


def _copy_session_to_client(client, request):
    """
    کپی کردن session از request به Test Client
    
    نکته مهم: باید session را در یک متغیر ذخیره کنیم
    چون هر بار که client.session را فراخوانی می‌کنیم، Test Client یک SessionStore جدید می‌سازد
    """
    if not request or not hasattr(request, 'session'):
        return None
    
    # اطمینان از وجود session_key
    if not request.session.session_key:
        request.session.save()
    
    original_project_id = request.session.get('current_project_id')
    
    try:
        from django.contrib.sessions.backends.db import SessionStore
        session_store = SessionStore(session_key=request.session.session_key)
        
        # ⭐ کلید: ذخیره session در متغیر
        session = client.session
        for key, value in session_store.items():
            session[key] = value
        session.modified = True
        session.save()
        
        return original_project_id
    except Exception as e:
        logger.error(f"خطا در بارگذاری session: {e}")
        return None


def call_api_via_http(url, request=None, method='GET', data=None, **kwargs):
    """
    فراخوانی API endpoint از طریق HTTP
    
    این تابع یکپارچه برای تمام API calls استفاده می‌شود و با Single Source of Truth سازگار است:
    - از همان مسیر HTTP استفاده می‌کند که frontend استفاده می‌کند
    - تمام middleware، authentication و permissions اجرا می‌شوند
    
    Args:
        url: مسیر کامل API (مثل '/api/v1/Expense/' یا '/api/v1/auth/user/')
        request: درخواست HTTP (برای احراز هویت و session)
        method: متد HTTP (GET, POST, PUT, PATCH, DELETE)
        data: داده‌های request body (dict)
        **kwargs: query parameters
    
    Returns:
        DRF Response object
    """
    # اضافه کردن query parameters
    if kwargs:
        query_string = '&'.join([f"{k}={v}" for k, v in kwargs.items()])
        url = f"{url}?{query_string}"
    
    client = Client()
    
    # کپی session
    original_project_id = _copy_session_to_client(client, request)
    
    # احراز هویت کاربر
    if request and request.user.is_authenticated:
        client.force_login(request.user)
        
        # اطمینان از حفظ project_id بعد از force_login
        if original_project_id:
            session = client.session
            if session.get('current_project_id') != original_project_id:
                session['current_project_id'] = original_project_id
                session.modified = True
                session.save()
    
    # ارسال درخواست HTTP
    try:
        if method == 'GET':
            response = client.get(url, follow=True)
        elif method == 'POST':
            response = client.post(url, data=json.dumps(data) if data else '{}', 
                                 content_type='application/json', follow=True)
        elif method == 'PUT':
            response = client.put(url, data=json.dumps(data) if data else '{}', 
                                content_type='application/json', follow=True)
        elif method == 'PATCH':
            response = client.patch(url, data=json.dumps(data) if data else '{}', 
                                  content_type='application/json', follow=True)
        elif method == 'DELETE':
            response = client.delete(url, follow=True)
        else:
            raise ValueError(f"متد HTTP نامعتبر: {method}")
        
        # تبدیل Django HttpResponse به DRF Response
        try:
            response_data = json.loads(response.content.decode('utf-8')) if hasattr(response, 'content') else {}
        except (json.JSONDecodeError, AttributeError):
            response_data = {'error': 'پاسخ نامعتبر از سرور'}
        
        drf_response = Response(response_data, status=response.status_code)
        
        if response.status_code >= 400:
            logger.warning(f"خطا در {method} {url}: {response.status_code}")
        
        return drf_response
        
    except Exception as e:
        logger.error(f"خطا در فراخوانی {url}: {str(e)}")
        return Response({'error': str(e)}, status=500)


def translate_participation_type(data):
    """تبدیل participation_type از انگلیسی به فارسی"""
    PARTICIPATION_TYPE_MAP = {
        'owner': 'مالک',
        'investor': 'سرمایه‌گذار'
    }
    
    if isinstance(data, dict):
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
    
    status_code = response.status_code
    
    # خطا
    if status_code >= 400:
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
        data = translate_participation_type(response.data)
        
        if isinstance(data, dict):
            if 'success' in data and data['success']:
                success_msg = data.get('message', success_msg)
            
            if 'id' in data:
                success_msg += f"\n📋 شناسه: #{data['id']}"
            
            if 'name' in data:
                success_msg += f"\n📝 نام: {data['name']}"
            
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
                success_msg += f"\n\n📊 جزئیات:\n{data_str}"
            except:
                success_msg += f"\n\n📊 جزئیات: {str(data)}"
        
        elif isinstance(data, list):
            count = len(data)
            success_msg = f"📋 تعداد نتایج: {count}"
            if count > 0:
                try:
                    all_data_str = json.dumps(data, ensure_ascii=False, indent=2)
                    success_msg += f"\n\n📊 نتایج:\n{all_data_str}"
                except:
                    success_msg += f"\n\n📊 نتایج: {str(data)}"
        else:
            success_msg += f"\n\n📊 نتیجه: {str(data)}"
    
    return success_msg
