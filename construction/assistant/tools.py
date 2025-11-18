"""
Tools برای AI Assistant
این فایل شامل تمام ابزارهایی است که Agent می‌تواند استفاده کند
"""

from langchain.tools import tool
from decimal import Decimal
from typing import Optional
from django.db.models import Sum, Count, Q
from construction.models import Expense, Period, Investor, Project
from construction.project_manager import ProjectManager


def get_current_project_from_request(request):
    """Helper function برای دریافت پروژه جاری از request"""
    return ProjectManager.get_current_project(request)


@tool
def create_expense(
    amount: float,
    period_id: int,
    expense_type: str,
    description: str = "",
    request=None
) -> str:
    """
    ایجاد یک هزینه جدید
    
    Args:
        amount: مبلغ هزینه (تومان)
        period_id: شناسه دوره
        expense_type: نوع هزینه (project_manager, facilities_manager, procurement, warehouse, other)
        description: توضیحات (اختیاری)
        request: درخواست HTTP برای دریافت پروژه جاری
    
    Returns:
        پیام موفقیت یا خطا
    """
    try:
        # دریافت دوره
        period = Period.objects.get(id=period_id)
        
        # دریافت پروژه از دوره یا از request
        project = period.project
        if request:
            current_project = ProjectManager.get_current_project(request)
            if current_project and current_project.id != project.id:
                return f"❌ خطا: دوره متعلق به پروژه دیگری است. پروژه جاری: {current_project.name}"
        
        # تبدیل expense_type به فارسی برای نمایش
        expense_type_map = {
            "مدیر پروژه": "project_manager",
            "سرپرست کارگاه": "facilities_manager",
            "کارپرداز": "procurement",
            "انباردار": "warehouse",
            "پیمان ساختمان": "construction_contractor",
            "سایر": "other"
        }
        
        # اگر به فارسی داده شده، تبدیل کن
        expense_type_code = expense_type_map.get(expense_type, expense_type)
        
        # بررسی معتبر بودن expense_type
        valid_types = [choice[0] for choice in Expense.EXPENSE_TYPES]
        if expense_type_code not in valid_types:
            return f"❌ خطا: نوع هزینه نامعتبر است. انواع معتبر: {', '.join([choice[1] for choice in Expense.EXPENSE_TYPES])}"
        
        # بررسی مبلغ
        if amount <= 0:
            return "❌ خطا: مبلغ باید بیشتر از صفر باشد"
        
        # ایجاد هزینه
        expense = Expense.objects.create(
            project=project,
            period=period,
            expense_type=expense_type_code,
            amount=Decimal(str(amount)),
            description=description
        )
        
        return f"✅ هزینه با موفقیت ایجاد شد!\n" \
               f"📋 شناسه: #{expense.id}\n" \
               f"💰 مبلغ: {amount:,.0f} تومان\n" \
               f"📅 دوره: {period.label}\n" \
               f"👤 نوع: {expense.get_expense_type_display()}\n" \
               f"📝 توضیحات: {description or 'ندارد'}"
    
    except Period.DoesNotExist:
        return f"❌ خطا: دوره با شناسه {period_id} یافت نشد"
    except Exception as e:
        return f"❌ خطا در ایجاد هزینه: {str(e)}"


@tool
def get_expense(expense_id: int) -> str:
    """
    دریافت اطلاعات یک هزینه
    
    Args:
        expense_id: شناسه هزینه
    
    Returns:
        اطلاعات هزینه
    """
    try:
        expense = Expense.objects.select_related('project', 'period').get(id=expense_id)
        return f"📋 اطلاعات هزینه #{expense.id}:\n" \
               f"💰 مبلغ: {expense.amount:,.0f} تومان\n" \
               f"📅 دوره: {expense.period.label}\n" \
               f"👤 نوع: {expense.get_expense_type_display()}\n" \
               f"📝 توضیحات: {expense.description or 'ندارد'}\n" \
               f"🏢 پروژه: {expense.project.name}\n" \
               f"📅 تاریخ ایجاد: {expense.created_at.strftime('%Y-%m-%d %H:%M')}"
    except Expense.DoesNotExist:
        return f"❌ خطا: هزینه با شناسه {expense_id} یافت نشد"
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def list_expenses(
    period_id: Optional[int] = None,
    expense_type: Optional[str] = None,
    limit: int = 20,
    request=None
) -> str:
    """
    لیست هزینه‌ها با فیلتر
    
    Args:
        period_id: شناسه دوره (اختیاری)
        expense_type: نوع هزینه (اختیاری)
        limit: تعداد نتایج (پیش‌فرض: 20)
        request: درخواست HTTP برای دریافت پروژه جاری
    
    Returns:
        لیست هزینه‌ها
    """
    try:
        # دریافت پروژه جاری
        project = None
        if request:
            project = ProjectManager.get_current_project(request)
            if not project:
                return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        # شروع query
        expenses = Expense.objects.select_related('project', 'period')
        
        # فیلتر بر اساس پروژه
        if project:
            expenses = expenses.filter(project=project)
        
        # فیلتر بر اساس دوره
        if period_id:
            expenses = expenses.filter(period_id=period_id)
        
        # فیلتر بر اساس نوع
        if expense_type:
            expense_type_map = {
                "مدیر پروژه": "project_manager",
                "سرپرست کارگاه": "facilities_manager",
                "کارپرداز": "procurement",
                "انباردار": "warehouse",
                "پیمان ساختمان": "construction_contractor",
                "سایر": "other"
            }
            expense_type_code = expense_type_map.get(expense_type, expense_type)
            expenses = expenses.filter(expense_type=expense_type_code)
        
        # محدود کردن تعداد
        expenses = expenses[:limit]
        
        if not expenses.exists():
            return "📭 هیچ هزینه‌ای یافت نشد."
        
        result = f"📋 لیست هزینه‌ها ({expenses.count()} مورد):\n\n"
        total = Decimal('0')
        
        for expense in expenses:
            result += f"  • #{expense.id}: {expense.get_expense_type_display()} - {expense.amount:,.0f} تومان ({expense.period.label})\n"
            total += expense.amount
        
        result += f"\n💰 مجموع: {total:,.0f} تومان"
        
        return result
    
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def get_investor_info(investor_id: int) -> str:
    """
    دریافت اطلاعات یک سرمایه‌گذار
    
    Args:
        investor_id: شناسه سرمایه‌گذار
    
    Returns:
        اطلاعات سرمایه‌گذار
    """
    try:
        investor = Investor.objects.select_related('project').prefetch_related('units').get(id=investor_id)
        
        units_info = ", ".join([unit.name for unit in investor.units.all()]) or "هیچ واحدی"
        
        return f"👤 اطلاعات سرمایه‌گذار:\n" \
               f"📋 نام: {investor.first_name} {investor.last_name}\n" \
               f"📞 تماس: {investor.phone}\n" \
               f"📧 ایمیل: {investor.email or 'ندارد'}\n" \
               f"🏢 پروژه: {investor.project.name}\n" \
               f"🏠 واحدها: {units_info}\n" \
               f"📅 نوع مشارکت: {investor.get_participation_type_display()}\n" \
               f"📝 توضیحات: {investor.description or 'ندارد'}"
    except Investor.DoesNotExist:
        return f"❌ خطا: سرمایه‌گذار با شناسه {investor_id} یافت نشد"
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def list_periods(project_id: Optional[int] = None, request=None) -> str:
    """
    دریافت لیست دوره‌های پروژه
    
    Args:
        project_id: شناسه پروژه (اختیاری - اگر نباشد از پروژه جاری استفاده می‌شود)
        request: درخواست HTTP برای دریافت پروژه جاری
    
    Returns:
        لیست دوره‌ها
    """
    try:
        # دریافت پروژه
        project = None
        if project_id:
            project = Project.objects.get(id=project_id)
        elif request:
            project = ProjectManager.get_current_project(request)
        
        if not project:
            return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        periods = Period.objects.filter(project=project).order_by('year', 'month_number')
        
        if not periods.exists():
            return f"📭 هیچ دوره‌ای برای پروژه {project.name} یافت نشد."
        
        result = f"📅 لیست دوره‌های پروژه {project.name}:\n\n"
        
        for period in periods:
            current_marker = " (دوره جاری)" if period.is_current() else ""
            result += f"  • {period.label} (شناسه: {period.id}){current_marker}\n"
        
        return result
    
    except Project.DoesNotExist:
        return f"❌ خطا: پروژه با شناسه {project_id} یافت نشد"
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def get_project_stats(project_id: Optional[int] = None, request=None) -> str:
    """
    دریافت آمار پروژه
    
    Args:
        project_id: شناسه پروژه (اختیاری)
        request: درخواست HTTP برای دریافت پروژه جاری
    
    Returns:
        آمار پروژه
    """
    try:
        # دریافت پروژه
        project = None
        if project_id:
            project = Project.objects.get(id=project_id)
        elif request:
            project = ProjectManager.get_current_project(request)
        
        if not project:
            return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        # آمار هزینه‌ها
        total_expenses = Expense.objects.filter(project=project).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # آمار سرمایه‌گذاران
        investor_count = Investor.objects.filter(project=project).count()
        
        # آمار واحدها
        unit_count = project.unit_set.count()
        
        # آمار دوره‌ها
        period_count = Period.objects.filter(project=project).count()
        
        result = f"📊 آمار پروژه {project.name}:\n\n"
        result += f"💰 مجموع هزینه‌ها: {total_expenses['total'] or 0:,.0f} تومان\n"
        result += f"📋 تعداد هزینه‌ها: {total_expenses['count'] or 0}\n"
        result += f"👥 تعداد سرمایه‌گذاران: {investor_count}\n"
        result += f"🏠 تعداد واحدها: {unit_count}\n"
        result += f"📅 تعداد دوره‌ها: {period_count}\n"
        
        return result
    
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def search_expenses(
    query: str,
    limit: int = 10,
    request=None
) -> str:
    """
    جستجوی هزینه‌ها بر اساس توضیحات
    
    Args:
        query: متن جستجو
        limit: تعداد نتایج (پیش‌فرض: 10)
        request: درخواست HTTP برای دریافت پروژه جاری
    
    Returns:
        نتایج جستجو
    """
    try:
        # دریافت پروژه جاری
        project = None
        if request:
            project = ProjectManager.get_current_project(request)
            if not project:
                return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        # شروع query
        expenses = Expense.objects.select_related('project', 'period')
        
        # فیلتر بر اساس پروژه
        if project:
            expenses = expenses.filter(project=project)
        
        # جستجو در توضیحات
        expenses = expenses.filter(
            Q(description__icontains=query) |
            Q(expense_type__icontains=query)
        )[:limit]
        
        if not expenses.exists():
            return f"📭 هیچ هزینه‌ای با جستجوی '{query}' یافت نشد."
        
        result = f"🔍 نتایج جستجو برای '{query}' ({expenses.count()} مورد):\n\n"
        
        for expense in expenses:
            result += f"  • #{expense.id}: {expense.get_expense_type_display()} - {expense.amount:,.0f} تومان\n"
            result += f"    📅 دوره: {expense.period.label}\n"
            if expense.description:
                result += f"    📝 توضیحات: {expense.description}\n"
            result += "\n"
        
        return result
    
    except Exception as e:
        return f"❌ خطا: {str(e)}"

