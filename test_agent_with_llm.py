#!/usr/bin/env python3
"""
اسکریپت تست Agent با LLM واقعی
این اسکریپت Agent را با LLM واقعی (OpenRouter) تست می‌کند و سوالات واقعی از آن می‌پرسد.
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# بارگذاری متغیرهای محیطی از .env
load_dotenv()

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# تنظیم Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"⚠️  هشدار: نتوانست Django را راه‌اندازی کنم: {e}")
    sys.exit(1)

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from construction.models import Project, Expense, Period, Investor, Transaction
from construction.assistant.agent import ConstructionAssistantAgent


class Colors:
    """کلاس برای رنگ‌های ترمینال"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """چاپ هدر با رنگ"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")


def print_success(text: str):
    """چاپ پیام موفقیت"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text: str):
    """چاپ پیام خطا"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_info(text: str):
    """چاپ پیام اطلاعاتی"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def print_warning(text: str):
    """چاپ پیام هشدار"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def setup_test_environment():
    """تنظیم محیط تست"""
    print_info("در حال تنظیم محیط تست...")
    
    # ایجاد یا دریافت کاربر تست
    user, created = User.objects.get_or_create(
        username='test_agent_user',
        defaults={
            'email': 'test_agent@test.com',
            'first_name': 'کاربر',
            'last_name': 'تست'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print_success(f"کاربر تست ایجاد شد: {user.username}")
    else:
        print_info(f"کاربر تست موجود است: {user.username}")
    
    # ایجاد یا دریافت پروژه تست
    project, created = Project.objects.get_or_create(
        name='پروژه تست Agent',
        defaults={
            'start_date_shamsi': '1400-01-01',
            'end_date_shamsi': '1405-12-29',
            'start_date_gregorian': '2021-03-21',
            'end_date_gregorian': '2027-03-20',
            'description': 'پروژه تست برای Agent'
        }
    )
    
    if created:
        print_success(f"پروژه تست ایجاد شد: {project.name}")
    else:
        print_info(f"پروژه تست موجود است: {project.name}")
    
    # ایجاد request با session
    factory = RequestFactory()
    request = factory.get('/assistant/chat/')
    
    # اضافه کردن session
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    request.user = user
    
    # تنظیم پروژه جاری در session
    request.session['current_project_id'] = project.id
    request.session.save()
    
    print_success("محیط تست آماده است!")
    return request, user, project


def create_test_data(project):
    """ایجاد داده‌های تست"""
    print_info("در حال ایجاد داده‌های تست...")
    
    # ایجاد دوره تست
    import jdatetime
    from datetime import datetime as dt
    
    # تاریخ‌های شمسی
    start_jdate = jdatetime.date(1400, 1, 1)
    end_jdate = jdatetime.date(1400, 3, 29)
    
    # تبدیل به میلادی
    start_gregorian = start_jdate.togregorian()
    end_gregorian = end_jdate.togregorian()
    
    period, created = Period.objects.get_or_create(
        project=project,
        year=1400,
        month_number=1,
        defaults={
            'label': 'دوره تست 1',
            'month_name': 'فروردین',
            'weight': 1,
            'start_date_shamsi': start_jdate,
            'end_date_shamsi': end_jdate,
            'start_date_gregorian': start_gregorian,
            'end_date_gregorian': end_gregorian
        }
    )
    
    if created:
        print_success(f"دوره تست ایجاد شد: {period.label}")
    
    # ایجاد سرمایه‌گذار تست
    investor, created = Investor.objects.get_or_create(
        project=project,
        first_name='سرمایه',
        last_name='گذار تست',
        defaults={
            'phone': '09123456789',
            'email': 'investor@test.com'
        }
    )
    
    if created:
        print_success(f"سرمایه‌گذار تست ایجاد شد: {investor.first_name} {investor.last_name}")
    
    # ایجاد هزینه تست
    expense, created = Expense.objects.get_or_create(
        project=project,
        period=period,
        expense_type='other',
        defaults={
            'amount': 1000000,
            'description': 'هزینه تست برای Agent'
        }
    )
    
    if created:
        print_success(f"هزینه تست ایجاد شد: {expense.amount:,} تومان")
    
    # ایجاد تراکنش تست (اختیاری - اگر خطا داد، ادامه می‌دهیم)
    transaction = None
    try:
        import jdatetime
        transaction_date_shamsi = jdatetime.date(1400, 1, 15)
        transaction_date_gregorian = transaction_date_shamsi.togregorian()
        
        transaction, created = Transaction.objects.get_or_create(
            project=project,
            investor=investor,
            period=period,
            date_shamsi=transaction_date_shamsi,
            transaction_type='principal_deposit',
            defaults={
                'date_gregorian': transaction_date_gregorian,
                'amount': 5000000,
                'description': 'تراکنش تست برای Agent'
            }
        )
        
        if created:
            print_success(f"تراکنش تست ایجاد شد: {transaction.amount:,} تومان")
    except Exception as e:
        print_warning(f"نتوانست تراکنش تست ایجاد کند: {str(e)}")
        print_info("ادامه بدون تراکنش...")
    
    print_success("داده‌های تست آماده است!")
    return period, investor, expense, transaction


def test_agent_with_questions(agent, questions):
    """تست Agent با سوالات"""
    print_header("🧪 تست Agent با سوالات واقعی")
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'─' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}سوال {i}/{len(questions)}:{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{question}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'─' * 80}{Colors.RESET}\n")
        
        start_time = datetime.now()
        
        try:
            print_info("در حال پردازش...")
            result = agent.invoke(question)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.get('success'):
                print_success(f"پاسخ دریافت شد (زمان: {duration:.2f} ثانیه)")
                print(f"\n{Colors.GREEN}{Colors.BOLD}پاسخ Agent:{Colors.RESET}")
                print(f"{Colors.GREEN}{result.get('output', '')}{Colors.RESET}\n")
                
                results.append({
                    'question': question,
                    'success': True,
                    'response': result.get('output', ''),
                    'duration': duration
                })
            else:
                print_error("خطا در دریافت پاسخ")
                print(f"{Colors.RED}{result.get('error', 'خطای نامشخص')}{Colors.RESET}\n")
                
                results.append({
                    'question': question,
                    'success': False,
                    'error': result.get('error', 'خطای نامشخص'),
                    'duration': duration
                })
        
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print_error(f"خطا در پردازش: {str(e)}")
            import traceback
            print(f"{Colors.RED}{traceback.format_exc()}{Colors.RESET}\n")
            
            results.append({
                'question': question,
                'success': False,
                'error': str(e),
                'duration': duration
            })
    
    return results


def print_summary(results):
    """چاپ خلاصه نتایج"""
    print_header("📊 خلاصه نتایج تست")
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n{Colors.BOLD}آمار کلی:{Colors.RESET}")
    print(f"  ✅ موفق: {Colors.GREEN}{len(successful)}{Colors.RESET}")
    print(f"  ❌ ناموفق: {Colors.RED}{len(failed)}{Colors.RESET}")
    print(f"  📊 کل: {len(results)}\n")
    
    if successful:
        total_duration = sum(r.get('duration', 0) for r in successful)
        avg_duration = total_duration / len(successful) if successful else 0
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ سوالات موفق:{Colors.RESET}")
        for i, result in enumerate(successful, 1):
            print(f"\n  {i}. {result['question']}")
            print(f"     ⏱️  زمان: {result.get('duration', 0):.2f} ثانیه")
            response_preview = result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
            print(f"     📝 پاسخ: {response_preview}")
        
        print(f"\n  ⏱️  میانگین زمان پاسخ: {avg_duration:.2f} ثانیه")
        print(f"  ⏱️  کل زمان: {total_duration:.2f} ثانیه")
    
    if failed:
        print(f"\n{Colors.BOLD}{Colors.RED}❌ سوالات ناموفق:{Colors.RESET}")
        for i, result in enumerate(failed, 1):
            print(f"\n  {i}. {result['question']}")
            if result.get('error'):
                error_preview = result['error'][:100] + "..." if len(result['error']) > 100 else result['error']
                print(f"     ⚠️  خطا: {error_preview}")


def main():
    """تابع اصلی"""
    print_header("🚀 تست Agent با LLM واقعی")
    
    print(f"📅 تاریخ تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # تنظیم محیط تست
        request, user, project = setup_test_environment()
        
        # ایجاد داده‌های تست
        period, investor, expense, transaction = create_test_data(project)
        
        # ایجاد Agent با OpenRouter
        print_info("در حال ایجاد Agent با OpenRouter...")
        agent = ConstructionAssistantAgent(
            request=request,
            provider_type='openrouter',
            use_rag=False
        )
        
        print_success("Agent با موفقیت ایجاد شد!")
        print_info(f"تعداد ابزارها: {len(agent.tools)}")
        print_info(f"مدل LLM: {agent.provider.get_model_name()}")
        
        # تعریف سوالات تست (شروع با سوالات ساده)
        test_questions = [
            "سلام! لطفاً خودت را معرفی کن.",
            "چند پروژه در سیستم وجود دارد؟",
            "لیست پروژه‌ها را نمایش بده.",
            "چند هزینه در پروژه جاری وجود دارد؟",
        ]
        
        # اجرای تست‌ها
        results = test_agent_with_questions(agent, test_questions)
        
        # نمایش خلاصه
        print_summary(results)
        
        # نتیجه نهایی
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        if len([r for r in results if r.get('success')]) > 0:
            print_success("🎉 تست‌ها با موفقیت انجام شد!")
            sys.exit(0)
        else:
            print_error("❌ همه تست‌ها ناموفق بودند!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  تست توسط کاربر متوقف شد.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ خطای غیرمنتظره: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

