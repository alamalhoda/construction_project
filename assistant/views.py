"""
Views برای AI Assistant
با پشتیبانی از حالت بدون دستیار (graceful degradation)
"""

import json
import logging
import os
import httpx
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.conf import settings
from construction.project_manager import ProjectManager
from assistant.jwt_helper import generate_jwt_token
from assistant.chat_logger import save_chat_log

logger = logging.getLogger(__name__)


def _is_assistant_enabled():
    """بررسی اینکه آیا دستیار فعال است یا نه"""
    enabled = os.getenv('AI_ASSISTANT_ENABLED', 'false').lower() == 'true'
    service_url = os.getenv('AI_ASSISTANT_SERVICE_URL', '')
    return enabled and bool(service_url)


def _get_assistant_service_url():
    """دریافت URL سرویس دستیار"""
    return os.getenv('AI_ASSISTANT_SERVICE_URL', '')


@login_required
@ensure_csrf_cookie
def chat_view(request):
    """صفحه چت با Assistant"""
    # بررسی اینکه آیا دستیار فعال است
    assistant_enabled = _is_assistant_enabled()
    
    return render(request, 'assistant/chat.html', {
        'assistant_enabled': assistant_enabled,
        'assistant_url': _get_assistant_service_url() if assistant_enabled else None
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint برای ارسال پیام به Assistant"""
    try:
        # بررسی اینکه آیا دستیار فعال است
        if not _is_assistant_enabled():
            return JsonResponse({
                'error': 'سرویس دستیار هوشمند در حال حاضر در دسترس نیست',
                'success': False,
                'assistant_unavailable': True
            }, status=503)
        
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'error': 'پیام خالی است',
                'success': False
            }, status=400)
        
        # دریافت تاریخچه چت از session
        chat_history = request.session.get('chat_history', [])
        
        # نگه داشتن فقط 5 سوال و جواب آخر
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
        
        # نمایش سوال کاربر در کنسول
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.info("=" * 80)
        logger.info(f"👤 کاربر: {username}")
        logger.info(f"❓ سوال: {user_message}")
        logger.info("=" * 80)
        
        # دریافت پروژه جاری
        current_project = ProjectManager.get_current_project(request)
        
        # تولید JWT Token
        api_token = generate_jwt_token(
            user_id=request.user.id,
            project_id=current_project.id if current_project else None
        )
        
        # لاگ برای دیباگ: بررسی توکن تولید شده
        logger.debug(f"🔐 JWT Token تولید شد: {api_token[:50] if api_token else 'None'}...")
        logger.debug(f"📌 Project ID: {current_project.id if current_project else None}")
        logger.debug(f"👤 User ID: {request.user.id}")
        
        # ارسال درخواست به سرویس دستیار
        assistant_url = _get_assistant_service_url()
        logger.debug(f"🌐 ارسال درخواست به: {assistant_url}/api/v1/chat")
        
        try:
            # استفاده از httpx برای async call
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            async def send_request():
                # افزایش timeout به 180 ثانیه (3 دقیقه) برای درخواست‌های طولانی
                async with httpx.AsyncClient(timeout=180.0) as client:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_token}"  # ارسال token در header (اولویت اول)
                    }
                    logger.debug(f"📤 Headers ارسالی: Authorization={headers.get('Authorization', '')[:50]}...")
                    
                    response = await client.post(
                        f"{assistant_url}/api/v1/chat",
                        json={
                            "message": user_message,
                            "user_id": request.user.id,
                            "project_id": current_project.id if current_project else None,
                            "chat_history": chat_history,
                            "api_token": api_token  # برای backward compatibility
                        },
                        headers=headers
                    )
                    return response
            
            # اجرای async request با مدیریت event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # اگر loop در حال اجرا است، از ThreadPoolExecutor استفاده می‌کنیم
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, send_request())
                        response = future.result()
                else:
                    # اگر loop در حال اجرا نیست، از run_until_complete استفاده می‌کنیم
                    response = loop.run_until_complete(send_request())
            except RuntimeError:
                # اگر loop وجود ندارد، یک loop جدید ایجاد می‌کنیم
                response = asyncio.run(send_request())
            
            if response.status_code == 200:
                result = response.json()
                
                # ذخیره‌سازی ChatLog در دیتابیس (Separation of Concerns)
                # این کار به صورت non-blocking انجام می‌شود تا سرعت پاسخ را کاهش ندهد
                try:
                    save_chat_log(
                        user=request.user,
                        user_message=user_message,
                        assistant_response=result.get('output', ''),
                        response_data=result,
                        project=current_project
                    )
                except Exception as e:
                    # در صورت خطا در ذخیره‌سازی، فقط لاگ می‌کنیم
                    # اما پاسخ را به کاربر برمی‌گردانیم
                    logger.warning(f"⚠️ خطا در ذخیره‌سازی ChatLog (غیر بحرانی): {str(e)}")
                
                # اضافه کردن به تاریخچه session
                if result.get('success'):
                    chat_history.append({
                        'role': 'user',
                        'content': user_message
                    })
                    chat_history.append({
                        'role': 'assistant',
                        'content': result.get('output', '')
                    })
                    if len(chat_history) > 10:
                        chat_history = chat_history[-10:]
                    request.session['chat_history'] = chat_history
                
                return JsonResponse(result)
            else:
                logger.error(f"خطا از سمت دستیار: {response.status_code}")
                return JsonResponse({
                    'error': 'خطا در ارتباط با سرویس دستیار',
                    'success': False,
                    'status_code': response.status_code
                }, status=503)
        
        except httpx.TimeoutException:
            logger.error("Timeout در ارتباط با سرویس دستیار")
            return JsonResponse({
                'error': 'زمان انتظار به پایان رسید. لطفاً دوباره تلاش کنید.',
                'success': False
            }, status=504)
        
        except httpx.ConnectError:
            logger.error("خطا در اتصال به سرویس دستیار")
            return JsonResponse({
                'error': 'سرویس دستیار در دسترس نیست. لطفاً بعداً تلاش کنید.',
                'success': False,
                'assistant_unavailable': True
            }, status=503)
        
        except Exception as e:
            logger.error(f"خطا در ارتباط با دستیار: {str(e)}")
            return JsonResponse({
                'error': f'خطا در ارتباط با سرویس دستیار: {str(e)}',
                'success': False
            }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'فرمت JSON نامعتبر است',
            'success': False
        }, status=400)
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"❌ خطا در chat_api: {error_traceback}")
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

