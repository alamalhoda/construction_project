"""
Views برای AI Assistant
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from construction.assistant.agent import create_assistant_agent


@login_required
def chat_view(request):
    """صفحه چت با Assistant"""
    return render(request, 'assistant/chat.html')


@login_required
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
        
        # دریافت نوع provider از تنظیمات یا request
        provider_type = data.get('provider_type') or getattr(settings, 'AI_ASSISTANT_PROVIDER', 'openai')
        use_rag = data.get('use_rag', True)
        
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
        return JsonResponse({
            'error': f'خطا در پردازش درخواست: {str(e)}',
            'success': False
        }, status=500)


@login_required
def chat_history(request):
    """تاریخچه چت (اختیاری - برای آینده)"""
    # TODO: پیاده‌سازی ذخیره و بازیابی تاریخچه چت
    return JsonResponse({
        'message': 'این قابلیت در حال توسعه است',
        'history': []
    })

