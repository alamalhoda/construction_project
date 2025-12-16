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
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from construction.project_manager import ProjectManager
from assistant.jwt_helper import generate_jwt_token
from assistant.chat_logger import save_chat_log

logger = logging.getLogger(__name__)


def _is_assistant_enabled():
    """بررسی اینکه آیا دستیار فعال است یا نه"""
    return settings.AI_ASSISTANT_ENABLED and bool(settings.AI_ASSISTANT_SERVICE_URL)


def _get_assistant_service_url():
    """دریافت URL سرویس دستیار"""
    return settings.AI_ASSISTANT_SERVICE_URL


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
                # استفاده از verify=True برای SSL verification (پیش‌فرض)
                timeout = httpx.Timeout(180.0, connect=30.0)  # 30 ثانیه برای اتصال، 180 ثانیه برای کل درخواست
                async with httpx.AsyncClient(timeout=timeout, verify=True, follow_redirects=True) as client:
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
                    # ایجاد یک event loop جدید در thread جداگانه
                    def run_in_thread():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(send_request())
                        finally:
                            new_loop.close()
                    
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        response = future.result()
                else:
                    # اگر loop در حال اجرا نیست، از run_until_complete استفاده می‌کنیم
                    response = loop.run_until_complete(send_request())
            except RuntimeError:
                # اگر loop وجود ندارد، یک loop جدید ایجاد می‌کنیم
                response = asyncio.run(send_request())
            
            # تلاش برای parse کردن response
            try:
                result = response.json()
            except:
                result = {
                    'output': f'خطا در پردازش پاسخ از سرویس دستیار (Status: {response.status_code})',
                    'success': False,
                    'error': f'Invalid response format (Status: {response.status_code})'
                }
            
            # بررسی اینکه آیا پاسخ موفق است یا نه
            # ذخیره‌سازی ChatLog در دیتابیس برای تمام پاسخ‌های موفق (status_code 200)
            # حتی اگر success=False باشد، باز هم ذخیره می‌کنیم تا خطاها هم ثبت شوند
            logger.debug(f"🔍 بررسی شرایط ذخیره‌سازی: status_code={response.status_code}, success={result.get('success')}")
            
            # ذخیره‌سازی برای تمام پاسخ‌های 200 (حتی اگر success=False باشد)
            if response.status_code == 200:
                # ذخیره‌سازی ChatLog در دیتابیس (Separation of Concerns)
                # این کار به صورت non-blocking انجام می‌شود تا سرعت پاسخ را کاهش ندهد
                logger.info(f"💾 شروع ذخیره‌سازی ChatLog برای کاربر {request.user.username}")
                try:
                    chat_log = save_chat_log(
                        user=request.user,
                        user_message=user_message,
                        assistant_response=result.get('output', ''),
                        response_data=result,
                        project=current_project
                    )
                    if chat_log:
                        logger.info(f"✅ ChatLog با موفقیت ذخیره شد: ID={chat_log.id}")
                    else:
                        logger.warning(f"⚠️ ChatLog ذخیره نشد (تابع None برگرداند)")
                except Exception as e:
                    # در صورت خطا در ذخیره‌سازی، فقط لاگ می‌کنیم
                    # اما پاسخ را به کاربر برمی‌گردانیم
                    logger.error(f"❌ خطا در ذخیره‌سازی ChatLog: {str(e)}", exc_info=True)
            else:
                logger.warning(
                    f"⚠️ ChatLog ذخیره نشد - status_code نامعتبر: {response.status_code}"
                )
            
            # بررسی اینکه آیا پاسخ موفق است یا نه (برای return)
            if response.status_code == 200 and result.get('success', False):
                
                # اضافه کردن به تاریخچه session
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
                # لاگ کردن جزئیات خطا از سمت دستیار
                logger.error(f"خطا از سمت دستیار: {response.status_code}")
                logger.error(f"جزئیات خطا: {result}")
                
                # اگر response شامل پیام خطا است، آن را به کاربر نشان می‌دهیم
                error_message = result.get('error', result.get('output', 'خطا در ارتباط با سرویس دستیار'))
                
                return JsonResponse({
                    'error': error_message,
                    'success': False,
                    'status_code': response.status_code,
                    'details': result
                }, status=503)
        
        except httpx.TimeoutException:
            logger.error("Timeout در ارتباط با سرویس دستیار")
            return JsonResponse({
                'error': 'زمان انتظار به پایان رسید. لطفاً دوباره تلاش کنید.',
                'success': False
            }, status=504)
        
        except httpx.ConnectError as e:
            logger.error(f"خطا در اتصال به سرویس دستیار: {str(e)}")
            logger.error(f"URL سرویس: {assistant_url}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'error': 'سرویس دستیار در دسترس نیست. لطفاً بعداً تلاش کنید.',
                'success': False,
                'assistant_unavailable': True
            }, status=503)
        
        except Exception as e:
            logger.error(f"خطا در ارتباط با دستیار: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
    """نمایش تاریخچه چت‌های کاربر با دستیار هوشمند"""
    from assistant.models import ChatLog
    from django.core.paginator import Paginator
    from construction.project_manager import ProjectManager
    
    # دریافت پروژه جاری (اختیاری)
    current_project = ProjectManager.get_current_project(request)
    project_id = request.GET.get('project_id')
    
    # دریافت فیلترها
    search_query = request.GET.get('search', '').strip()
    llm_provider = request.GET.get('llm_provider', '')
    success_filter = request.GET.get('success', '')
    
    # ساخت query
    chat_logs = ChatLog.objects.filter(user=request.user)
    
    # فیلتر بر اساس پروژه
    if project_id:
        chat_logs = chat_logs.filter(project_id=project_id)
    elif current_project:
        # اگر پروژه جاری وجود دارد، فقط چت‌های آن پروژه را نشان بده
        chat_logs = chat_logs.filter(project=current_project)
    
    # فیلتر بر اساس جستجو
    if search_query:
        chat_logs = chat_logs.filter(
            Q(user_message__icontains=search_query) |
            Q(assistant_response__icontains=search_query)
        )
    
    # فیلتر بر اساس ارائه‌دهنده LLM
    if llm_provider:
        chat_logs = chat_logs.filter(llm_provider=llm_provider)
    
    # فیلتر بر اساس موفقیت
    if success_filter == 'true':
        chat_logs = chat_logs.filter(success=True)
    elif success_filter == 'false':
        chat_logs = chat_logs.filter(success=False)
    
    # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
    chat_logs = chat_logs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(chat_logs, 20)  # 20 چت در هر صفحه
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # دریافت لیست ارائه‌دهندگان منحصر به فرد برای فیلتر
    llm_providers = ChatLog.objects.filter(user=request.user).values_list(
        'llm_provider', flat=True
    ).distinct().order_by('llm_provider')
    
    # آمار کلی
    total_chats = ChatLog.objects.filter(user=request.user).count()
    successful_chats = ChatLog.objects.filter(user=request.user, success=True).count()
    total_tokens = ChatLog.objects.filter(user=request.user).aggregate(
        total=Sum('total_tokens')
    )['total'] or 0
    
    return render(request, 'assistant/chat_history.html', {
        'chat_logs': page_obj,
        'llm_providers': llm_providers,
        'current_project': current_project,
        'search_query': search_query,
        'llm_provider_filter': llm_provider,
        'success_filter': success_filter,
        'total_chats': total_chats,
        'successful_chats': successful_chats,
        'total_tokens': total_tokens,
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

