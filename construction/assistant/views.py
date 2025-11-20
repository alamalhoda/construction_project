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
from construction.assistant.agent import create_assistant_agent

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
        load_dotenv()  # اطمینان از لود شدن .env
        
        # خواندن مستقیم از .env برای اطمینان
        provider_type_from_env = os.getenv('AI_ASSISTANT_PROVIDER', 'openai')
        provider_type_from_settings = getattr(settings, 'AI_ASSISTANT_PROVIDER', 'openai')
        
        # استفاده از مقدار .env (اولویت اول)
        provider_type = provider_type_from_env
        
        # اگر provider_type از request آمده، لاگ می‌کنیم اما از تنظیمات استفاده می‌کنیم
        provider_type_from_request = data.get('provider_type')
        if provider_type_from_request and provider_type_from_request.lower() != provider_type.lower():
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
        
        # اجرای Agent
        result = agent.invoke(user_message)
        
        return JsonResponse(result)
    
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

