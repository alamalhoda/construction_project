"""
Views برای AI Assistant
"""

import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.conf import settings
from assistant.agent import create_assistant_agent

logger = logging.getLogger(__name__)


@login_required
@ensure_csrf_cookie
def chat_view(request):
    """صفحه چت با Assistant"""
    return render(request, 'assistant/chat.html')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint برای ارسال پیام به Assistant"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'error': 'پیام خالی است',
                'success': False
            }, status=400)
        
        # دریافت تاریخچه چت از session
        chat_history = request.session.get('chat_history', [])
        
        # نگه داشتن فقط 5 سوال و جواب آخر (10 پیام = 5 جفت)
        # این کار را قبل از ارسال انجام می‌دهیم تا فقط تاریخچه قبلی را بفرستیم
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
        
        # نمایش سوال کاربر در کنسول
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.info("=" * 80)
        logger.info(f"👤 کاربر: {username}")
        logger.info(f"❓ سوال: {user_message}")
        logger.info("=" * 80)
        print("=" * 80)
        print(f"👤 کاربر: {username}")
        print(f"❓ سوال: {user_message}")
        print("=" * 80)
        
        # دریافت نوع provider از تنظیمات
        # همیشه از تنظیمات استفاده می‌کنیم (نه از request) تا مطمئن شویم که از کلید API صحیح استفاده می‌کنیم
        import os
        from dotenv import load_dotenv
        
        # استفاده از override=True تا مطمئن شویم که .env اصلی override می‌کند
        # و مشخص کردن مسیر دقیق .env برای جلوگیری از خواندن فایل‌های دیگر
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        # پاک کردن environment variable قبل از load_dotenv تا مطمئن شویم از .env خوانده می‌شود
        # (اگر از جای دیگری تنظیم شده باشد، پاک می‌شود)
        if 'AI_ASSISTANT_PROVIDER' in os.environ:
            del os.environ['AI_ASSISTANT_PROVIDER']
        # حالا load_dotenv را صدا می‌زنیم تا از .env بخواند
        load_dotenv(dotenv_path=env_path, override=True)  # اطمینان از لود شدن .env اصلی
        
        # خواندن مستقیم از .env برای اطمینان
        provider_type_from_env_raw = os.getenv('AI_ASSISTANT_PROVIDER')
        if not provider_type_from_env_raw:
            # اگر از .env خوانده نشد، از settings استفاده می‌کنیم
            provider_type_from_env_raw = getattr(settings, 'AI_ASSISTANT_PROVIDER', 'openai')
        # پاک کردن کامنت‌ها از provider_type (اگر وجود داشته باشد)
        if provider_type_from_env_raw:
            provider_type_from_env = str(provider_type_from_env_raw).split('#')[0].strip()
        else:
            provider_type_from_env = 'openai'
        provider_type_from_settings = getattr(settings, 'AI_ASSISTANT_PROVIDER', 'openai')
        
        # Debug: نمایش مقادیر خوانده شده
        print(f"🔍 Debug - env_path: {repr(env_path)}")
        print(f"🔍 Debug - file exists: {os.path.exists(env_path)}")
        print(f"🔍 Debug - provider_type_from_env_raw: {repr(provider_type_from_env_raw)}")
        print(f"🔍 Debug - provider_type_from_env: {repr(provider_type_from_env)}")
        print(f"🔍 Debug - provider_type_from_settings: {repr(provider_type_from_settings)}")
        print(f"🔍 Debug - os.environ.get('AI_ASSISTANT_PROVIDER'): {repr(os.environ.get('AI_ASSISTANT_PROVIDER'))}")
        
        # اگر از .env خوانده نشد، از settings استفاده می‌کنیم
        if not provider_type_from_env_raw or provider_type_from_env_raw == 'openai':
            print(f"⚠️  Warning: Could not read from .env, using settings: {provider_type_from_settings}")
            provider_type_from_env = provider_type_from_settings
        
        # استفاده از مقدار .env (اولویت اول)
        # اما اگر از .env خوانده نشد یا مقدار پیش‌فرض بود، از settings استفاده می‌کنیم
        if provider_type_from_env and provider_type_from_env != 'openai':
            provider_type = provider_type_from_env
        elif provider_type_from_settings:
            provider_type = provider_type_from_settings
            print(f"ℹ️  Using provider from settings: {provider_type}")
        else:
            provider_type = 'openai'
        
        # اگر provider_type از request آمده، لاگ می‌کنیم اما از تنظیمات استفاده می‌کنیم
        provider_type_from_request = data.get('provider_type')
        if provider_type_from_request:
            print(f"🔍 Debug - provider_type_from_request: {repr(provider_type_from_request)}")
            if provider_type_from_request.lower() != provider_type.lower():
                print(f"⚠️  Warning: Provider type from request ({provider_type_from_request}) ignored, using {provider_type} from .env")
        
        print(f"🔧 Using provider: {provider_type}")
        
        # RAG را به صورت پیش‌فرض غیرفعال می‌کنیم تا از خطای quota جلوگیری کنیم
        use_rag = data.get('use_rag', False)
        
        # ایجاد Agent
        agent = create_assistant_agent(
            request=request,
            provider_type=provider_type,
            use_rag=use_rag
        )
        
        # اجرای Agent با تاریخچه (بدون پیام فعلی - agent خودش آن را اضافه می‌کند)
        try:
            result = agent.invoke(user_message, chat_history=chat_history)
            
            # بررسی اینکه result معتبر است
            if not result or not isinstance(result, dict):
                logger.error("نتیجه agent معتبر نیست")
                return JsonResponse({
                    'error': 'نتیجه پردازش نامعتبر است',
                    'success': False
                }, status=500)
            
            # اضافه کردن پیام کاربر و پاسخ به تاریخچه
            if result.get('success'):
                chat_history.append({
                    'role': 'user',
                    'content': user_message
                })
                chat_history.append({
                    'role': 'assistant',
                    'content': result.get('output', '')
                })
                # نگه داشتن فقط 5 سوال و جواب آخر (10 پیام = 5 جفت)
                if len(chat_history) > 10:
                    chat_history = chat_history[-10:]
                # ذخیره تاریخچه در session
                request.session['chat_history'] = chat_history
            
            # اطمینان از اینکه result ساختار درستی دارد
            if 'success' not in result:
                result['success'] = False
            if 'output' not in result and result.get('success'):
                result['output'] = 'پاسخ دریافت نشد.'
            
            return JsonResponse(result)
            
        except Exception as agent_error:
            # اگر خطایی در agent رخ داد، آن را catch می‌کنیم
            import traceback
            error_traceback = traceback.format_exc()
            logger.error("❌ خطا در اجرای agent:")
            logger.error(error_traceback)
            print("❌ خطا در اجرای agent:")
            print(error_traceback)
            
            return JsonResponse({
                'error': f'خطا در پردازش درخواست: {str(agent_error)}',
                'success': False,
                'traceback': error_traceback if settings.DEBUG else None
            }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'فرمت JSON نامعتبر است',
            'success': False
        }, status=400)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error("❌ خطا در chat_api:")
        logger.error(error_traceback)
        print("❌ خطا در chat_api:")
        print(error_traceback)
        return JsonResponse({
            'error': f'خطا در پردازش درخواست: {str(e)}',
            'success': False,
            'traceback': error_traceback if settings.DEBUG else None
        }, status=500)


@login_required
def chat_history(request):
    """تاریخچه چت (اختیاری - برای آینده)"""
    # TODO: پیاده‌سازی ذخیره و بازیابی تاریخچه چت
    return JsonResponse({
        'message': 'این قابلیت در حال توسعه است',
        'history': []
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def clear_chat_history(request):
    """پاک کردن تاریخچه چت از session"""
    try:
        if 'chat_history' in request.session:
            del request.session['chat_history']
            request.session.modified = True
        return JsonResponse({
            'success': True,
            'message': 'تاریخچه چت پاک شد'
        })
    except Exception as e:
        logger.error(f"خطا در پاک کردن تاریخچه: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

