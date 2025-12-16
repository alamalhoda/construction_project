"""
Helper functions برای ذخیره‌سازی ChatLog

این ماژول مسئولیت ذخیره‌سازی چت‌ها را بر عهده دارد (Separation of Concerns)
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from construction.models import Project
from assistant.models import ChatLog

logger = logging.getLogger(__name__)


def save_chat_log(
    user: User,
    user_message: str,
    assistant_response: str,
    response_data: Dict[str, Any],
    project: Optional[Project] = None
) -> Optional[ChatLog]:
    """
    ذخیره‌سازی لاگ چت در دیتابیس
    
    این تابع Single Responsibility دارد: فقط ذخیره‌سازی
    و Single Source of Truth است: تمام اطلاعات از response_data می‌آید
    
    Args:
        user: کاربری که چت را انجام داده
        user_message: پیام کاربر
        assistant_response: پاسخ دستیار
        response_data: داده‌های کامل برگردانده شده از agent (شامل token_usage, tools, etc.)
        project: پروژه مرتبط (اختیاری)
    
    Returns:
        ChatLog instance در صورت موفقیت، None در صورت خطا
    """
    try:
        # لاگ کردن برای دیباگ: بررسی داده‌های دریافتی
        logger.info(f"📥 شروع ذخیره‌سازی ChatLog - User: {user.username}, Project: {project.id if project else None}")
        logger.debug(f"📥 داده‌های دریافتی برای ChatLog: keys={list(response_data.keys())}")
        logger.debug(f"   token_usage: {response_data.get('token_usage')}")
        logger.debug(f"   tools_used: {response_data.get('tools_used')}")
        logger.debug(f"   duration_seconds: {response_data.get('duration_seconds')}")
        logger.debug(f"   llm_provider: {response_data.get('llm_provider')}")
        logger.debug(f"   llm_model: {response_data.get('llm_model')}")
        logger.debug(f"   success: {response_data.get('success')}")
        
        # استخراج اطلاعات از response_data
        token_usage = response_data.get('token_usage', {}) or {}
        tools_used = response_data.get('tools_used', []) or []
        
        # تبدیل tools_used به لیست ساده از نام‌ها (برای ذخیره‌سازی)
        tools_list = []
        if tools_used:
            for tool in tools_used:
                if isinstance(tool, dict):
                    tools_list.append({
                        'name': tool.get('name', 'unknown'),
                        'args': tool.get('args', {}),
                        'index': tool.get('index', 0),
                    })
                else:
                    tools_list.append({'name': str(tool)})
        
        # ایجاد و ذخیره ChatLog
        logger.debug(f"💾 در حال ایجاد ChatLog object...")
        try:
            chat_log = ChatLog.objects.create(
                user=user,
                project=project,
                llm_provider=response_data.get('llm_provider', 'Unknown'),
                llm_model=response_data.get('llm_model', 'Unknown'),
                user_message=user_message,
                assistant_response=assistant_response,
                tools_used=tools_list,
                tools_count=response_data.get('tools_count', 0),
                input_tokens=token_usage.get('input_tokens', 0),
                output_tokens=token_usage.get('output_tokens', 0),
                total_tokens=token_usage.get('total_tokens', 0),
                # استفاده از None فقط اگر کلید وجود نداشته باشد
                # اگر کلید وجود دارد و مقدار آن 0 است، باید 0 ذخیره شود نه None
                cached_tokens=token_usage.get('cached_tokens') if 'cached_tokens' in token_usage else None,
                reasoning_tokens=token_usage.get('reasoning_tokens') if 'reasoning_tokens' in token_usage else None,
                duration_seconds=response_data.get('duration_seconds', 0.0),
                success=response_data.get('success', True),
                error_message=response_data.get('error') if not response_data.get('success', True) else None,
            )
            logger.debug(f"✅ ChatLog object با موفقیت ایجاد شد: ID={chat_log.id}")
        except Exception as create_error:
            logger.error(f"❌ خطا در ایجاد ChatLog object: {str(create_error)}", exc_info=True)
            raise
        
        logger.info(
            f"✅ ChatLog ذخیره شد: ID={chat_log.id}, "
            f"User={user.username}, "
            f"Tokens={chat_log.total_tokens} (in={chat_log.input_tokens}, out={chat_log.output_tokens}), "
            f"Tools={chat_log.tools_count}, "
            f"Duration={chat_log.duration_seconds}s"
        )
        
        return chat_log
    
    except Exception as e:
        logger.error(f"❌ خطا در ذخیره‌سازی ChatLog: {str(e)}", exc_info=True)
        # در صورت خطا، لاگ می‌کنیم اما خطا را propagate نمی‌کنیم
        # تا فرآیند اصلی چت مختل نشود
        return None

