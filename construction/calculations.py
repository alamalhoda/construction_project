"""
سرویس محاسبات مالی پروژه
این فایل شامل تمام محاسبات مالی است که قبلاً در JavaScript انجام می‌شد
"""

from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, Count, Q
from django.utils import timezone
import jdatetime
import logging
from typing import Dict, List, Optional, Tuple
from . import models

logger = logging.getLogger(__name__)


class FinancialCalculationService:
    """سرویس محاسبات مالی پروژه"""
    
    @staticmethod
    def format_number(number: float, decimal_places: int = 2) -> str:
        """فرمت اعداد با جداکننده هزارگان"""
        return f"{number:,.{decimal_places}f}"
    
    @staticmethod
    def format_percentage(number: float, decimal_places: int = 2) -> str:
        """فرمت درصد"""
        return f"{number:.{decimal_places}f}%"
    
    @staticmethod
    def convert_to_toman(amount: float) -> float:
        """تبدیل به تومان (تقسیم بر 10)"""
        return amount / 10

    @staticmethod
    def compute_fund_balance(total_capital: float, total_expenses: float, total_sales: float) -> float:
        """محاسبه مانده صندوق = سرمایه - هزینه + فروش"""
        return float(total_capital) - float(total_expenses) + float(total_sales)

    @staticmethod
    def compute_period_fund_balance(net_capital: float, period_expenses: float, period_sales: float) -> float:
        """محاسبه مانده صندوق دوره = سرمایه دوره - هزینه دوره + فروش دوره"""
        return float(net_capital) - float(period_expenses) + float(period_sales)


class ProjectCalculations(FinancialCalculationService):
    """محاسبات مربوط به پروژه"""
    
    @staticmethod
    def calculate_project_statistics(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه آمار کامل پروژه
        
        Args:
            project_id: شناسه پروژه (الزامی - باید از API endpoint با request ارسال شود)
            
        Returns:
            Dict: آمار کامل پروژه
        """
        logger.info("Calculating project statistics for project_id: %s", project_id)
        if not project_id:
            logger.warning("calculate_project_statistics called without project_id")
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found: project_id=%s", project_id)
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # آمار واحدها (مرجع واحد)
        units_stats = models.Unit.objects.project_stats(project)
        
        # آمار تراکنش‌ها (مرجع واحد)
        tx_totals = models.Transaction.objects.project_totals(project)
        
        # آمار هزینه‌ها
        expense_stats = models.Expense.objects.filter(project=project).aggregate(
            total_expenses=Sum('amount')
        )
        
        # آمار فروش‌ها
        sale_stats = models.Sale.objects.filter(project=project).aggregate(
            total_sales=Sum('amount')
        )
        
        # محاسبات اصلی
        total_deposits = float(tx_totals['deposits'] or 0)  # مجموع آورده‌ها
        total_withdrawals = float(tx_totals['withdrawals'] or 0)  # مجموع برداشت‌ها
        total_profits = float(tx_totals['profits'] or 0)  # مجموع سود
        total_expenses = float(expense_stats['total_expenses'] or 0)  # مجموع هزینه‌ها
        total_sales = float(sale_stats['total_sales'] or 0)  # مجموع فروش/مرجوعی
        
        # سرمایه موجود (برداشت‌ها منفی هستند)
        net_principal = float(tx_totals['net_capital'])  # سرمایه خالص
        
        # موجودی کل
        grand_total = net_principal + total_profits  # مجموع کل (سرمایه خالص + سود)
        
        # هزینه نهایی
        final_cost = total_expenses - total_sales  # هزینه نهایی (هزینه‌ها - فروش)
        
        # آمار سرمایه‌گذاران (از طریق تراکنش‌ها)
        investor_ids = models.Transaction.objects.filter(project=project).values_list('investor_id', flat=True).distinct()  # لیست شناسه‌های سرمایه‌گذاران
        investors_count = len(investor_ids)  # تعداد کل سرمایه‌گذاران
        owners_count = models.Investor.objects.filter(id__in=investor_ids, participation_type='owner').count()  # تعداد مالکان
        investors_only_count = models.Investor.objects.filter(id__in=investor_ids, participation_type='investor').count()  # تعداد سرمایه‌گذاران (غیر مالک)
        
        # محاسبه مدت پروژه
        project_duration = 0  # مدت پروژه (روز)
        if project.start_date_gregorian and project.end_date_gregorian:
            delta = project.end_date_gregorian - project.start_date_gregorian  # تفاوت تاریخ‌ها
            project_duration = delta.days  # مدت پروژه (روز)
        
        # تعداد روزهای فعال (روزهایی که تراکنش انجام شده)
        active_days = models.Transaction.objects.filter(project=project).values('date_gregorian').distinct().count()  # تعداد روزهای فعال
        
        return {
            'project': {
                'id': project.id,  # شناسه پروژه
                'name': project.name,  # نام پروژه
                'total_infrastructure': float(project.total_infrastructure),  # مساحت کل زیربنا
                'correction_factor': float(project.correction_factor),  # ضریب اصلاحی
                'start_date_shamsi': str(project.start_date_shamsi),  # تاریخ شروع (شمسی)
                'end_date_shamsi': str(project.end_date_shamsi),  # تاریخ پایان (شمسی)
                'start_date_gregorian': str(project.start_date_gregorian),  # تاریخ شروع (میلادی)
                'end_date_gregorian': str(project.end_date_gregorian),  # تاریخ پایان (میلادی)
                # فیلد is_active حذف شد - مدل Project این فیلد را ندارد
            },
            'units_statistics': units_stats,  # آمار واحدها
            'transaction_statistics': {
                'total_deposits': total_deposits,  # مجموع آورده‌ها
                'total_withdrawals': total_withdrawals,  # مجموع برداشت‌ها
                'total_profits': total_profits,  # مجموع سود
                'net_principal': net_principal,  # سرمایه خالص
                'grand_total': grand_total  # مجموع کل
            },
            'expense_statistics': {
                'total_expenses': total_expenses,  # مجموع هزینه‌ها
                'total_sales': total_sales,  # مجموع فروش/مرجوعی
                'final_cost': final_cost  # هزینه نهایی
            },
            'investor_statistics': {
                'total_investors': investors_count,  # تعداد کل سرمایه‌گذاران
                'owners_count': owners_count,  # تعداد مالکان
                'investors_count': investors_only_count  # تعداد سرمایه‌گذاران (غیر مالک)
            },
            'project_timing': {
                'project_duration_days': project_duration,  # مدت پروژه (روز)
                'active_days': active_days  # تعداد روزهای فعال
            }
        }
    
    @staticmethod
    def calculate_cost_metrics(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه متریک‌های هزینه
        
        Args:
            project_id: شناسه پروژه (اگر None باشد از پروژه فعال استفاده می‌شود)
            
        Returns:
            Dict: متریک‌های هزینه
        """
        logger.info("Calculating profit percentages for project_id: %s", project_id)
        # اگر project_id مشخص نشده، از پروژه فعال استفاده کن
        if project_id:
            try:
                project = models.Project.objects.get(id=project_id)
                logger.debug("Project found: %s (id: %s)", project.name, project_id)
            except models.Project.DoesNotExist:
                logger.error("Project not found in calculate_profit_percentages: project_id=%s", project_id)
                return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        else:
            logger.warning("calculate_profit_percentages called without project_id")
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        # آمار هزینه‌ها و فروش‌ها
        expense_stats = models.Expense.objects.filter(project=project).aggregate(
            total_expenses=Sum('amount')
        )
        sale_stats = models.Sale.objects.filter(project=project).aggregate(
            total_sales=Sum('amount')
        )
        
        # آمار واحدها (مرجع واحد)
        units_stats = models.Unit.objects.project_stats(project)  # آمار واحدها
        
        total_expenses = float(expense_stats['total_expenses'] or 0)  # مجموع هزینه‌ها
        total_sales = float(sale_stats['total_sales'] or 0)  # مجموع فروش/مرجوعی
        total_area = float(units_stats['total_area'] or 0)  # مجموع مساحت واحدها
        total_value = float(units_stats['total_price'] or 0)  # مجموع ارزش واحدها
        total_infrastructure = float(project.total_infrastructure)  # مساحت کل زیربنا
        
        # محاسبات
        final_cost = total_expenses - total_sales  # هزینه نهایی (هزینه‌ها - فروش)
        final_profit_amount = total_value - final_cost  # مبلغ سود نهایی (ارزش - هزینه)
        
        # محاسبه هزینه و ارزش هر متر
        net_cost_per_meter = final_cost / total_area if total_area > 0 else 0  # هزینه خالص هر متر مربع (بر اساس مساحت واحدها)
        gross_cost_per_meter = final_cost / total_infrastructure if total_infrastructure > 0 else 0  # هزینه ناخالص هر متر مربع (بر اساس زیربنا)
        value_per_meter = total_value / total_area if total_area > 0 else 0  # ارزش هر متر مربع
        
        # محاسبه درصد سود کل
        total_profit_percentage = (final_profit_amount / final_cost * 100) if final_cost > 0 else 0  # درصد سود کل
        
        # محاسبه مانده صندوق ساختمان
        # فرمول: مجموع کل سرمایه + فروش/مرجوع - کل هزینه
        # یا: مجموع کل سرمایه - مجموع هزینه خالص
        # مجموع کل سرمایه = مجموع آورده - مجموع برداشت
        
        # دریافت آمار تراکنش‌ها از مرجع واحد برای محاسبه مجموع کل سرمایه
        tx_totals = models.Transaction.objects.project_totals(project)  # محاسبه مجموع تراکنش‌ها
        total_capital = float(tx_totals['net_capital'])  # مجموع کل سرمایه (سرمایه خالص)
        
        # محاسبه هزینه خالص
        net_cost = total_expenses - total_sales  # هزینه خالص
        
        # محاسبه مانده صندوق ساختمان (مرجع واحد)
        building_fund_balance = FinancialCalculationService.compute_fund_balance(total_capital, total_expenses, total_sales)  # مانده صندوق ساختمان
        
        return {
            'final_cost': final_cost,  # هزینه نهایی
            'final_profit_amount': final_profit_amount,  # مبلغ سود نهایی
            'total_profit_percentage': total_profit_percentage,  # درصد سود کل
            'net_cost_per_meter': net_cost_per_meter,  # هزینه خالص هر متر مربع
            'gross_cost_per_meter': gross_cost_per_meter,  # هزینه ناخالص هر متر مربع
            'value_per_meter': value_per_meter,  # ارزش هر متر مربع
            'total_expenses': total_expenses,  # مجموع هزینه‌ها
            'total_sales': total_sales,  # مجموع فروش/مرجوعی
            'total_value': total_value,  # مجموع ارزش واحدها
            'total_area': total_area,  # مجموع مساحت واحدها
            'total_infrastructure': total_infrastructure,  # مساحت کل زیربنا
            'total_capital': total_capital,  # مجموع کل سرمایه
            'net_cost': net_cost,  # هزینه خالص
            'building_fund_balance': building_fund_balance  # مانده صندوق ساختمان
        }
    
    @staticmethod
    def calculate_current_cost_metrics(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه متریک‌های هزینه تا دوره جاری (نه هزینه نهایی کل پروژه)
        
        این متد هزینه‌ها و فروش‌های تا دوره جاری را محاسبه می‌کند و هزینه هر متر خالص
        فعلی را برمی‌گرداند که برای محاسبه هزینه فعلی واحد استفاده می‌شود.
        
        این متد از متدهای cumulative_until موجود در مدل‌های Expense و Sale استفاده می‌کند.
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            Dict: متریک‌های هزینه فعلی شامل net_cost_per_meter_current
        """
        if not project_id:
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        logger.info("Calculating cost metrics for project_id: %s", project_id)
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in calculate_cost_metrics: project_id=%s", project_id)
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # یافتن دوره جاری
        current_period = None
        try:
            import jdatetime
            today_jalali = jdatetime.datetime.now()
            current_year = today_jalali.year
            current_month = today_jalali.month
            
            current_period = models.Period.objects.filter(
                project=project,
                year=current_year,
                month_number=current_month
            ).first()
            if current_period:
                logger.debug("Current period found: %s", current_period.label)
        except Exception as e:
            logger.warning("Error finding current period: %s", e)
            pass
        
        # اگر دوره جاری پیدا نشد، از آخرین دوره استفاده می‌کنیم
        if not current_period:
            current_period = models.Period.objects.filter(
                project=project
            ).order_by('-year', '-month_number').first()
        
        if not current_period:
            # اگر هیچ دوره‌ای وجود ندارد، از هزینه نهایی استفاده می‌کنیم
            return ProjectCalculations.calculate_cost_metrics(project_id)
        
        # استفاده از متد cumulative_until موجود برای محاسبه هزینه‌های تجمعی تا دوره جاری
        total_expenses_current = models.Expense.objects.cumulative_until(project, current_period)  # مجموع هزینه‌های تجمعی تا دوره جاری
        total_sales_current = models.Sale.objects.cumulative_until(project, current_period)  # مجموع فروش/مرجوعی تجمعی تا دوره جاری
        
        # محاسبه هزینه نهایی تا دوره جاری
        current_final_cost = total_expenses_current - total_sales_current  # هزینه نهایی تا دوره جاری
        
        # آمار واحدها (مساحت واحدها برای محاسبه هزینه هر متر)
        units_stats = models.Unit.objects.project_stats(project)  # آمار واحدها
        total_area = float(units_stats['total_area'] or 0)  # مجموع مساحت واحدها
        total_infrastructure = float(project.total_infrastructure)  # مساحت کل زیربنا
        
        # محاسبه هزینه هر متر خالص و ناخالص تا دوره جاری
        net_cost_per_meter_current = current_final_cost / total_area if total_area > 0 else 0  # هزینه خالص هر متر مربع تا دوره جاری
        gross_cost_per_meter_current = current_final_cost / total_infrastructure if total_infrastructure > 0 else 0  # هزینه ناخالص هر متر مربع تا دوره جاری
        
        return {
            'net_cost_per_meter_current': net_cost_per_meter_current,  # هزینه خالص هر متر مربع تا دوره جاری
            'gross_cost_per_meter_current': gross_cost_per_meter_current,  # هزینه ناخالص هر متر مربع تا دوره جاری
            'current_final_cost': current_final_cost,  # هزینه نهایی تا دوره جاری
            'total_expenses_current': total_expenses_current,  # مجموع هزینه‌های تجمعی تا دوره جاری
            'total_sales_current': total_sales_current,  # مجموع فروش/مرجوعی تجمعی تا دوره جاری
            'current_period_id': current_period.id,  # شناسه دوره جاری
            'current_period_label': current_period.label  # برچسب دوره جاری
        }


class ProfitCalculations(FinancialCalculationService):
    """محاسبات مربوط به سود"""
    
    @staticmethod
    def calculate_average_construction_period(project_id: Optional[int] = None) -> float:
        """
        محاسبه دوره متوسط ساخت
        
        فرمول: مجموع (هزینه هر دوره × وزن آن دوره) ÷ مجموع کل هزینه‌ها
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            float: دوره متوسط ساخت (روز)
        """
        logger.debug("Calculating average construction period for project_id: %s", project_id)
        if not project_id:
            logger.warning("calculate_average_construction_period called without project_id")
            return 0.0
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in calculate_average_construction_period: project_id=%s", project_id)
            return 0.0
        
        # دریافت هزینه‌ها با اطلاعات دوره
        expenses = models.Expense.objects.filter(
            project=project
        ).select_related('period').exclude(period__isnull=True)
        
        if not expenses.exists():
            return 0.0
        
        # محاسبه مجموع (هزینه × وزن)
        weighted_sum = 0
        total_expenses = 0
        
        for expense in expenses:
            if expense.period and expense.period.weight:
                weighted_sum += float(expense.amount) * float(expense.period.weight)
                total_expenses += float(expense.amount)
        
        # محاسبه دوره متوسط
        average_period = weighted_sum / total_expenses if total_expenses > 0 else 0
        
        return round(average_period, 10)
    
    @staticmethod
    def calculate_profit_percentages(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه درصدهای سود (کل، سالانه، ماهانه، روزانه)
        
        Args:
            project_id: شناسه پروژه (اگر None باشد از پروژه فعال استفاده می‌شود)
            
        Returns:
            Dict: درصدهای سود
        """
        # اگر project_id مشخص نشده، از پروژه فعال استفاده کن
        if project_id:
            try:
                project = models.Project.objects.get(id=project_id)
            except models.Project.DoesNotExist:
                return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        else:
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        # محاسبه متریک‌های هزینه
        cost_metrics = ProjectCalculations.calculate_cost_metrics(project_id)
        
        if 'error' in cost_metrics:
            return cost_metrics
        
        total_profit_percentage = cost_metrics['total_profit_percentage']  # درصد سود کل
        
        # محاسبه دوره متوسط ساخت
        average_period = ProfitCalculations.calculate_average_construction_period(project_id)  # دوره متوسط ساخت (ماه)
        
        # محاسبه درصد سود سالانه
        annual_profit_percentage = (total_profit_percentage / average_period * 12) if average_period > 0 else 0  # درصد سود سالانه
        
        # محاسبه درصد سود ماهانه
        monthly_profit_percentage = annual_profit_percentage / 12  # درصد سود ماهانه
        
        # محاسبه درصد سود روزانه با ضریب اصلاحی
        correction_factor = float(project.correction_factor)  # ضریب اصلاحی
        daily_profit_percentage = (annual_profit_percentage / 365) * correction_factor  # درصد سود روزانه (با ضریب اصلاحی)
        
        return {
            'total_profit_percentage': round(total_profit_percentage,10),  # درصد سود کل
            'annual_profit_percentage': round(annual_profit_percentage, 10),  # درصد سود سالانه
            'monthly_profit_percentage': round(monthly_profit_percentage, 10),  # درصد سود ماهانه
            'daily_profit_percentage': round(daily_profit_percentage, 8),  # درصد سود روزانه (8 رقم اعشار برای دقت)
            'average_construction_period': average_period,  # دوره متوسط ساخت (ماه)
            'correction_factor': correction_factor  # ضریب اصلاحی
        }


class InvestorCalculations(FinancialCalculationService):
    """محاسبات مربوط به سرمایه‌گذاران"""
    
    @staticmethod
    def calculate_investor_statistics(investor_id: int, project_id: Optional[int] = None) -> Dict:
        """
        محاسبه آمار سرمایه‌گذار
        
        Args:
            investor_id: شناسه سرمایه‌گذار
            project_id: شناسه پروژه
            
        Returns:
            Dict: آمار سرمایه‌گذار
        """
        if not project_id:
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        try:
            project = models.Project.objects.get(id=project_id)
        except models.Project.DoesNotExist:
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # دریافت سرمایه‌گذار
        try:
            investor = models.Investor.objects.get(id=investor_id)
        except models.Investor.DoesNotExist:
            return {'error': 'سرمایه‌گذار یافت نشد'}
        
        # آمار تراکنش‌های سرمایه‌گذار از مرجع واحد
        totals = models.Transaction.objects.totals(project, {'investor_id': investor.id})  # محاسبه مجموع تراکنش‌های سرمایه‌گذار
        total_principal_deposit = totals.get('principal_deposit', 0.0)  # مجموع آورده اصلی (فقط آورده عادی)
        total_loan_deposit = totals.get('loan_deposit', 0.0)  # مجموع آورده وام
        total_principal = totals.get('deposits', 0.0)  # مجموع کل آورده‌ها (آورده اصلی + آورده وام)
        total_withdrawal = totals.get('withdrawals', 0.0)  # مجموع برداشت‌ها
        total_profit = totals.get('profits', 0.0)  # مجموع سود
        net_principal = totals.get('net_capital', 0.0)  # سرمایه خالص
        total_balance = net_principal + float(total_profit)  # مانده کل (سرمایه خالص + سود)
        
        return {
            'investor': {
                'id': investor.id,  # شناسه سرمایه‌گذار
                'name': f"{investor.first_name} {investor.last_name}",  # نام کامل سرمایه‌گذار
                'first_name': investor.first_name,  # نام سرمایه‌گذار
                'last_name': investor.last_name,  # نام خانوادگی سرمایه‌گذار
                'participation_type': investor.participation_type  # نوع مشارکت
            },
            'amounts': {
                'total_principal_deposit': float(total_principal_deposit),  # مجموع آورده اصلی
                'total_loan_deposit': float(total_loan_deposit),  # مجموع آورده وام
                'total_principal': float(total_principal),  # مجموع کل آورده‌ها
                'total_withdrawal': float(total_withdrawal),  # مجموع برداشت‌ها
                'total_profit': float(total_profit),  # مجموع سود
                'net_principal': float(net_principal),  # سرمایه خالص
                'total_balance': float(total_balance)  # مانده کل
            },
            'amounts_toman': {
                # حالا که داده‌ها در دیتابیس به تومان هستند، نیازی به تقسیم بر 10 نیست
                'total_principal_deposit': float(total_principal_deposit),  # مجموع آورده اصلی (تومان)
                'total_loan_deposit': float(total_loan_deposit),  # مجموع آورده وام (تومان)
                'total_principal': float(total_principal),  # مجموع کل آورده‌ها (تومان)
                'total_withdrawal': abs(float(total_withdrawal)),  # مجموع برداشت‌ها (تومان - مقدار مثبت)
                'total_profit': float(total_profit),  # مجموع سود (تومان)
                'net_principal': float(net_principal),  # سرمایه خالص (تومان)
                'total_balance': float(total_balance)  # مانده کل (تومان)
            }
        }
    
    @staticmethod
    def calculate_investor_ratios(investor_id: int, project_id: Optional[int] = None) -> Dict:
        """
        محاسبه نسبت‌های سرمایه‌گذار
        
        Args:
            investor_id: شناسه سرمایه‌گذار
            project_id: شناسه پروژه
            
        Returns:
            Dict: نسبت‌های سرمایه‌گذار
        """
        logger.info("Calculating investor ratios for investor_id: %s, project_id: %s", investor_id, project_id)
        if not project_id:
            logger.warning("calculate_investor_ratios called without project_id")
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in calculate_investor_ratios: project_id=%s", project_id)
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # آمار سرمایه‌گذار
        logger.debug("Fetching investor statistics for ratios calculation")
        investor_stats = InvestorCalculations.calculate_investor_statistics(investor_id, project_id)
        
        if 'error' in investor_stats:
            return investor_stats
        
        # دریافت نوع مشارکت
        participation_type = investor_stats['investor']['participation_type']  # نوع مشارکت (owner/investor)
        
        # آمار کل پروژه
        project_stats = ProjectCalculations.calculate_project_statistics(project_id)
        
        if 'error' in project_stats:
            return project_stats
        
        # مقادیر سرمایه‌گذار
        net_principal = investor_stats['amounts']['net_principal']  # سرمایه خالص سرمایه‌گذار
        total_profit = investor_stats['amounts']['total_profit']  # مجموع سود سرمایه‌گذار
        total_balance = investor_stats['amounts']['total_balance']  # مانده کل سرمایه‌گذار
        
        # مقادیر کل پروژه
        project_net_principal = project_stats['transaction_statistics']['net_principal']  # سرمایه خالص کل پروژه
        project_total_profits = project_stats['transaction_statistics']['total_profits']  # مجموع سود کل پروژه
        project_grand_total = project_stats['transaction_statistics']['grand_total']  # مجموع کل پروژه
        
        # محاسبه نسبت‌ها
        capital_ratio = (net_principal / project_net_principal * 100) if project_net_principal > 0 else 0  # نسبت سرمایه
        profit_ratio = (total_profit / project_total_profits * 100) if project_total_profits > 0 else 0  # نسبت سود
        total_ratio = (total_balance / project_grand_total * 100) if project_grand_total > 0 else 0  # نسبت کل
        
        # محاسبه شاخص نفع (فقط برای مالکان - owner)
        profit_index = 0  # شاخص نفع
        if participation_type == 'owner':  # فقط برای مالکان محاسبه می‌شود
            if project_net_principal > 0 and project_total_profits > 0 and net_principal > 0:
                capital_ratio_decimal = net_principal / project_net_principal  # نسبت سرمایه (اعشاری)
                profit_ratio_decimal = total_profit / project_total_profits  # نسبت سود (اعشاری)
                
                if capital_ratio_decimal > 0:
                    profit_index = profit_ratio_decimal / capital_ratio_decimal  # شاخص نفع (نسبت سود به سرمایه)
        
        return {
            'capital_ratio': round(capital_ratio, 10),  # نسبت سرمایه
            'profit_ratio': round(profit_ratio, 10),  # نسبت سود
            'total_ratio': round(total_ratio, 10),  # نسبت کل
            'profit_index': round(profit_index, 10),  # شاخص نفع (فقط برای مالکان، برای سرمایه‌گذاران صفر)
            'capital_ratio_formatted': FinancialCalculationService.format_percentage(capital_ratio),  # نسبت سرمایه (فرمت شده)
            'profit_ratio_formatted': FinancialCalculationService.format_percentage(profit_ratio),  # نسبت سود (فرمت شده)
            'total_ratio_formatted': FinancialCalculationService.format_percentage(total_ratio)  # نسبت کل (فرمت شده)
        }
    
    @staticmethod
    def calculate_investor_ownership(investor_id: int, project_id: Optional[int] = None) -> Dict:
        """
        محاسبه مالکیت سرمایه‌گذار به متر مربع
        
        فرمول: (آورده + سود) / قیمت هر متر مربع واحد انتخابی
        
        Args:
            investor_id: شناسه سرمایه‌گذار
            project_id: شناسه پروژه
            
        Returns:
            Dict: اطلاعات مالکیت سرمایه‌گذار
        """
        logger.info("Calculating investor ownership for investor_id: %s, project_id: %s", investor_id, project_id)
        if not project_id:
            logger.warning("calculate_investor_ownership called without project_id")
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in calculate_investor_ownership: project_id=%s", project_id)
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # دریافت سرمایه‌گذار
        try:
            investor = models.Investor.objects.get(id=investor_id)
            logger.debug("Investor found: %s %s (id: %s)", investor.first_name, investor.last_name, investor_id)
        except models.Investor.DoesNotExist:
            logger.error("Investor not found in calculate_investor_ownership: investor_id=%s", investor_id)
            return {'error': 'سرمایه‌گذار یافت نشد'}
        
        # آمار مالی سرمایه‌گذار
        logger.debug("Fetching investor statistics for ownership calculation")
        investor_stats = InvestorCalculations.calculate_investor_statistics(investor_id, project_id)
        
        if 'error' in investor_stats:
            return investor_stats
        
        # محاسبه آورده + سود
        net_principal = investor_stats['amounts']['net_principal']
        total_profit = investor_stats['amounts']['total_profit']
        total_amount = net_principal + total_profit
        
        # دریافت واحدهای سرمایه‌گذار
        units = investor.units.all()
        
        if not units.exists():
            # برای سرمایه‌گذارانی که واحد ندارند، از ارزش ساختمان(متری) استفاده می‌کنیم
            # فرمول: ownership_area = (آورده + سود) / value_per_meter
            # value_per_meter = ارزش کل ساختمان / مجموع متراژ مفید
            
            cost_metrics = ProjectCalculations.calculate_cost_metrics(project.id)
            
            if 'error' in cost_metrics:
                return cost_metrics
                
            value_per_meter = cost_metrics.get('value_per_meter', 0)
            
            if value_per_meter <= 0:
                return {
                    'ownership_area': 0,  # مساحت مالکیت
                    'total_amount': total_amount,  # مبلغ کل (سرمایه خالص + سود)
                    'net_principal': net_principal,  # سرمایه خالص
                    'total_profit': total_profit,  # مجموع سود
                    'value_per_meter': value_per_meter,  # ارزش هر متر مربع ساختمان
                    'units_count': 0,  # تعداد واحدهای مالکیت
                    'units': [],  # لیست واحدهای مالکیت
                    'message': 'ارزش ساختمان(متری) صحیح محاسبه نشده است'  # پیام توضیحی
                }
            
            # محاسبه متراژ مالکیت بر اساس ارزش ساختمان(متری)
            ownership_area = total_amount / value_per_meter
            
            # محاسبه هزینه فعلی واحد (برای سرمایه‌گذارانی که واحد ندارند، هزینه فعلی مالکیت محاسبه می‌شود)
            # استفاده از هزینه فعلی (تا دوره جاری) به جای هزینه نهایی کل پروژه
            current_cost_metrics = ProjectCalculations.calculate_current_cost_metrics(project.id)
            if 'error' not in current_cost_metrics:
                net_cost_per_meter_current = current_cost_metrics.get('net_cost_per_meter_current', 0)
            else:
                # در صورت خطا، از هزینه نهایی استفاده می‌کنیم
                net_cost_per_meter_current = cost_metrics.get('net_cost_per_meter', 0)
            
            current_unit_cost = net_cost_per_meter_current * ownership_area if ownership_area > 0 else 0
            
            return {
                'ownership_area': round(ownership_area, 10),  # مساحت مالکیت
                'total_amount': total_amount,  # مبلغ کل (سرمایه خالص + سود)
                'net_principal': net_principal,  # سرمایه خالص
                'total_profit': total_profit,  # مجموع سود
                'value_per_meter': round(value_per_meter, 10),  # ارزش هر متر مربع ساختمان
                'units_count': 0,  # تعداد واحدهای مالکیت
                'units': [],  # لیست واحدهای مالکیت
                'current_unit_cost': round(current_unit_cost, 10),  # هزینه فعلی واحد (تا دوره جاری)
                'calculation_method': 'value_per_meter',  # روش محاسبه (بر اساس ارزش متری)
                'message': 'محاسبه بر اساس ارزش ساختمان(متری)'  # پیام توضیحی
            }
        
        # محاسبه میانگین وزنی قیمت هر متر
        total_area = 0
        total_value = 0
        units_list = []
        
        for unit in units:
            unit_area = float(unit.area)
            unit_price_per_meter = float(unit.price_per_meter)
            
            total_area += unit_area
            total_value += unit_area * unit_price_per_meter
            
            units_list.append({
                'id': unit.id,
                'name': unit.name,
                'area': unit_area,
                'price_per_meter': unit_price_per_meter,
                'total_price': float(unit.total_price)
            })
        
        # محاسبه میانگین وزنی قیمت هر متر
        average_price_per_meter = total_value / total_area if total_area > 0 else 0
        
        # محاسبه مالکیت (متر مربع)
        ownership_area = total_amount / average_price_per_meter if average_price_per_meter > 0 else 0
        
        # محاسبه قیمت کل واحدها (مجموع قیمت نهایی همه واحدها)
        total_units_price = sum(float(unit.total_price) for unit in units)
        
        # محاسبه پرداخت نهایی جهت تسویه حساب
        # فرمول: (آورده + سود) - قیمت کل واحد
        final_payment = total_amount - total_units_price
        
        # محاسبه قیمت واگذار شده (متر/تومان)
        # فرمول: (کل آورده + پرداخت نهایی) / متراژ واحد
        # توجه: اگر پرداخت نهایی منفی باشد (یعنی باید بپردازد)، باید به آورده اضافه شود
        actual_paid = net_principal - final_payment
        transfer_price_per_meter = actual_paid / total_area if total_area > 0 else 0
        
        # محاسبه هزینه فعلی واحد
        # فرمول: هزینه هر متر مربع خالص فعلی × مساحت واحد
        # استفاده از هزینه فعلی (تا دوره جاری) به جای هزینه نهایی کل پروژه
        current_cost_metrics = ProjectCalculations.calculate_current_cost_metrics(project.id)
        if 'error' not in current_cost_metrics:
            net_cost_per_meter_current = current_cost_metrics.get('net_cost_per_meter_current', 0)
            current_unit_cost = net_cost_per_meter_current * total_area if total_area > 0 else 0
        else:
            # در صورت خطا، از هزینه نهایی استفاده می‌کنیم
            cost_metrics = ProjectCalculations.calculate_cost_metrics(project.id)
            if 'error' not in cost_metrics:
                net_cost_per_meter = cost_metrics.get('net_cost_per_meter', 0)
                current_unit_cost = net_cost_per_meter * total_area if total_area > 0 else 0
            else:
                current_unit_cost = 0
        
        return {
            'ownership_area': round(ownership_area, 10),  # مساحت مالکیت
            'total_amount': total_amount,  # مبلغ کل (سرمایه خالص + سود)
            'net_principal': net_principal,  # سرمایه خالص
            'total_profit': total_profit,  # مجموع سود
            'average_price_per_meter': round(average_price_per_meter, 10),  # میانگین قیمت هر متر مربع
            'units_count': units.count(),  # تعداد واحدهای مالکیت
            'units': units_list,  # لیست واحدهای مالکیت
            'total_units_area': total_area,  # مجموع مساحت واحدها
            'total_units_price': total_units_price,  # مجموع قیمت واحدها
            'ownership_percentage': round((ownership_area / total_area * 100), 10) if total_area > 0 else 0,  # درصد مالکیت
            'final_payment': round(final_payment, 10),  # پرداخت نهایی
            'transfer_price_per_meter': round(transfer_price_per_meter, 10),  # قیمت انتقال هر متر مربع
            'actual_paid': round(actual_paid, 10),  # مقدار پرداخت شده واقعی
            'current_unit_cost': round(current_unit_cost, 10),  # هزینه فعلی واحد
            'calculation_method': 'unit_based',  # روش محاسبه (بر اساس واحدها)
            'message': 'محاسبه بر اساس واحدهای مالکیت'  # پیام توضیحی
        }
    
    @staticmethod
    def get_all_investors_summary(project_id: Optional[int] = None) -> List[Dict]:
        """
        دریافت خلاصه آمار تمام سرمایه‌گذاران شامل اطلاعات مالکیت
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            List[Dict]: لیست آمار سرمایه‌گذاران شامل:
                - اطلاعات مالی (آورده، برداشت، سود)
                - نسبت‌ها (capital_ratio, profit_ratio, profit_index)
                - اطلاعات مالکیت (متراژ، واحدها، قیمت‌ها)
        """
        logger.info("Getting all investors summary for project_id: %s", project_id)
        # اگر project_id None باشد، خطا برگردان (باید از API endpoint تنظیم شود)
        if not project_id:
            logger.warning("get_all_investors_summary called without project_id")
            return []
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in get_all_investors_summary: project_id=%s", project_id)
            return []
        
        # دریافت سرمایه‌گذاران پروژه جاری (فیلتر بر اساس پروژه)
        investors = models.Investor.objects.filter(project=project)
        summary = []
        
        print(f"🔍 تعداد کل سرمایه‌گذاران: {investors.count()}")
        
        for investor in investors:
            try:
                # آمار سرمایه‌گذار
                investor_stats = InvestorCalculations.calculate_investor_statistics(investor.id, project_id)
                investor_ratios = InvestorCalculations.calculate_investor_ratios(investor.id, project_id)
                investor_ownership = InvestorCalculations.calculate_investor_ownership(investor.id, project_id)
                
                if 'error' not in investor_stats and 'error' not in investor_ratios:
                    # محاسبه مجموع کل (سرمایه + سود)
                    grand_total = investor_stats['amounts']['net_principal'] + investor_stats['amounts']['total_profit']
                    
                    # ساخت خلاصه اطلاعات
                    investor_summary = {
                        'id': investor.id,  # شناسه سرمایه‌گذار
                        'name': f"{investor.first_name} {investor.last_name}",  # نام کامل سرمایه‌گذار
                        'participation_type': investor.participation_type,  # نوع مشارکت
                        'total_principal_deposit': investor_stats['amounts']['total_principal_deposit'],  # مجموع آورده اصلی (فقط آورده عادی)
                        'total_loan_deposit': investor_stats['amounts']['total_loan_deposit'],  # مجموع آورده وام
                        'total_deposits': investor_stats['amounts']['total_principal'],  # مجموع کل آورده‌ها (آورده اصلی + آورده وام)
                        'total_withdrawals': abs(investor_stats['amounts']['total_withdrawal']),  # مجموع برداشت‌ها (مقدار مثبت)
                        'net_principal': investor_stats['amounts']['net_principal'],  # سرمایه خالص
                        'total_profit': investor_stats['amounts']['total_profit'],  # مجموع سود
                        'grand_total': grand_total,  # مجموع کل (سرمایه خالص + سود)
                        'capital_ratio': investor_ratios.get('capital_ratio', 0),  # نسبت سرمایه
                        'profit_ratio': investor_ratios.get('profit_ratio', 0),  # نسبت سود
                        'profit_index': investor_ratios.get('profit_index', 0),  # شاخص سود
                        'contract_date': str(investor.contract_date_shamsi) if investor.contract_date_shamsi else None  # تاریخ قرارداد (شمسی)
                    }
                    
                    # افزودن اطلاعات مالکیت (در صورت عدم خطا)
                    if 'error' not in investor_ownership:
                        investor_summary['ownership'] = {
                            'ownership_area': investor_ownership.get('ownership_area', 0),  # مساحت مالکیت
                            'average_price_per_meter': investor_ownership.get('average_price_per_meter', 0),  # میانگین قیمت هر متر مربع
                            'units_count': investor_ownership.get('units_count', 0),  # تعداد واحدهای مالکیت
                            'units': investor_ownership.get('units', []),  # لیست واحدهای مالکیت
                            'total_units_area': investor_ownership.get('total_units_area', 0),  # مجموع مساحت واحدها
                            'total_units_price': investor_ownership.get('total_units_price', 0),  # مجموع قیمت واحدها
                            'ownership_percentage': investor_ownership.get('ownership_percentage', 0),  # درصد مالکیت
                            'final_payment': investor_ownership.get('final_payment', 0),  # پرداخت نهایی
                            'transfer_price_per_meter': investor_ownership.get('transfer_price_per_meter', 0),  # قیمت انتقال هر متر مربع
                            'actual_paid': investor_ownership.get('actual_paid', 0)  # مقدار پرداخت شده واقعی
                        }
                    else:
                        # اگر خطا داشت، اطلاعات پیش‌فرض قرار بده
                        investor_summary['ownership'] = {
                            'ownership_area': 0,  # مساحت مالکیت
                            'average_price_per_meter': 0,  # میانگین قیمت هر متر مربع
                            'units_count': 0,  # تعداد واحدهای مالکیت
                            'units': [],  # لیست واحدهای مالکیت
                            'total_units_area': 0,  # مجموع مساحت واحدها
                            'total_units_price': 0,  # مجموع قیمت واحدها
                            'ownership_percentage': 0,  # درصد مالکیت
                            'final_payment': 0,  # پرداخت نهایی
                            'transfer_price_per_meter': 0,  # قیمت انتقال هر متر مربع
                            'actual_paid': 0,  # مقدار پرداخت شده واقعی
                            'message': investor_ownership.get('message', 'اطلاعات مالکیت موجود نیست')  # پیام توضیحی
                        }
                    
                    summary.append(investor_summary)
            except Exception as e:
                logger.error(f"خطا در محاسبه آمار سرمایه‌گذار {investor.id}: {e}")
                continue
        
        return summary
    
    @staticmethod
    def calculate_investor_trend_chart(investor_id: int, project_id: Optional[int] = None) -> Dict:
        """
        محاسبه داده‌های نمودار ترند سرمایه موجود و هزینه واحد برای سرمایه‌گذار
        
        Args:
            investor_id: شناسه سرمایه‌گذار
            project_id: شناسه پروژه
            
        Returns:
            Dict: داده‌های نمودار شامل:
                - periods: لیست دوره‌ها با فرمت YYYY-MM
                - cumulative_capital: سرمایه موجود تجمعی به میلیون تومان
                - unit_cost: هزینه واحد به میلیون تومان
        """
        if not project_id:
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        try:
            project = models.Project.objects.get(id=project_id)
        except models.Project.DoesNotExist:
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # دریافت سرمایه‌گذار
        try:
            investor = models.Investor.objects.get(id=investor_id)
        except models.Investor.DoesNotExist:
            return {'error': 'سرمایه‌گذار یافت نشد'}
        
        # دریافت تمام دوره‌ها
        periods = models.Period.objects.filter(project=project).order_by('year', 'month_number')
        
        # دریافت تراکنش‌های سرمایه‌گذار
        transactions = models.Transaction.objects.filter(
            investor=investor,
            project=project
        ).order_by('date_gregorian')
        
        # پردازش تراکنش‌ها به صورت ماهانه
        monthly_data = {}
        for transaction in transactions:
            if not transaction.date_shamsi:
                continue
                
            # استخراج ماه از تاریخ شمسی (jdatetime.date object)
            month = f"{transaction.date_shamsi.year}-{str(transaction.date_shamsi.month).zfill(2)}"  # YYYY-MM
            
            if month not in monthly_data:
                monthly_data[month] = {
                    'principal': 0,
                    'withdrawal': 0,
                    'profit': 0
                }
            
            amount = float(transaction.amount or 0)
            
            if transaction.transaction_type in ['principal_deposit', 'loan_deposit']:
                monthly_data[month]['principal'] += amount
            elif transaction.transaction_type == 'principal_withdrawal':
                monthly_data[month]['withdrawal'] += amount
            elif transaction.transaction_type == 'profit_accrual':
                monthly_data[month]['profit'] += amount
        
        # تبدیل دوره‌ها به فرمت ماهانه
        all_months = [f"{p.year}-{str(p.month_number).zfill(2)}" for p in periods]
        
        # محاسبه سرمایه موجود تجمعی
        cumulative_capital_data = []
        cumulative_sum = 0
        
        for month in all_months:
            if month in monthly_data:
                monthly_net = monthly_data[month]['principal'] + monthly_data[month]['withdrawal']
                cumulative_sum += monthly_net
            cumulative_capital_data.append(cumulative_sum / 1000000)  # تبدیل به میلیون تومان
        
        # محاسبه متراژ واحد سرمایه‌گذار
        units = investor.units.all()
        investor_unit_area = sum(float(unit.area) for unit in units)
        
        # دریافت کل متراژ مفید پروژه
        total_net_area = models.Unit.objects.project_total_area(project)
        
        # محاسبه هزینه واحد برای هر دوره
        unit_cost_data = []
        
        cumulative_expenses_total = 0
        cumulative_sales_total = 0
        
        for period in periods:
            # محاسبه هزینه‌ها و فروش‌های تجمعی تا این دوره
            period_expenses = models.Expense.objects.period_totals(project, period)
            period_sales = models.Sale.objects.period_totals(project, period)
            
            cumulative_expenses_total += period_expenses
            cumulative_sales_total += period_sales
            
            # محاسبه هزینه خالص تجمعی
            cumulative_net_cost = cumulative_expenses_total - cumulative_sales_total
            
            # محاسبه هزینه واحد مشارکت کننده
            # فرمول: (هزینه خالص تجمعی ÷ کل متراژ مفید) × متراژ واحد مشارکت کننده
            unit_cost_per_meter = (cumulative_net_cost / total_net_area) * investor_unit_area if total_net_area > 0 else 0
            unit_cost_in_millions = unit_cost_per_meter / 1000000  # تبدیل به میلیون تومان
            
            unit_cost_data.append(unit_cost_in_millions)
        
        return {
            'success': True,
            'investor_id': investor_id,
            'investor_name': f"{investor.first_name} {investor.last_name}",
            'periods': all_months,
            'cumulative_capital': cumulative_capital_data,
            'unit_cost': unit_cost_data,
            'active_project': project.name
        }


class TransactionCalculations(FinancialCalculationService):
    """محاسبات مربوط به تراکنش‌ها"""
    
    @staticmethod
    def calculate_transaction_statistics(project_id: Optional[int] = None, filters: Optional[Dict] = None) -> Dict:
        """
        محاسبه آمار تراکنش‌ها
        
        Args:
            project_id: شناسه پروژه
            filters: فیلترهای اضافی (اختیاری)
            
        Returns:
            Dict: آمار تراکنش‌ها
        """
        logger.info("Calculating transaction statistics for project_id: %s", project_id)
        if not project_id:
            logger.warning("calculate_transaction_statistics called without project_id")
            return {'error': 'شناسه پروژه الزامی است. لطفاً project_id را ارسال کنید.'}
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in calculate_transaction_statistics: project_id=%s", project_id)
            return {'error': f'پروژه با شناسه {project_id} یافت نشد'}
        
        # محاسبه آمار از مرجع واحد
        logger.debug("Calculating transaction totals with filters: %s", filters)
        totals = models.Transaction.objects.totals(project, filters or {})  # محاسبه مجموع تراکنش‌ها
        
        total_deposits = float(totals['deposits'] or 0)  # مجموع آورده‌ها
        total_withdrawals = float(totals['withdrawals'] or 0)  # مجموع برداشت‌ها
        total_profits = float(totals['profits'] or 0)  # مجموع سود
        net_capital = float(totals['net_capital'])  # سرمایه خالص
        
        return {
            'total_transactions': totals.get('total_transactions', 0),  # تعداد کل تراکنش‌ها
            'total_deposits': total_deposits,  # مجموع آورده‌ها
            'total_withdrawals': total_withdrawals,  # مجموع برداشت‌ها
            'total_profits': total_profits,  # مجموع سود
            'net_capital': net_capital,  # سرمایه خالص
            'total_deposits_formatted': FinancialCalculationService.format_number(total_deposits),  # مجموع آورده‌ها (فرمت شده)
            'total_withdrawals_formatted': FinancialCalculationService.format_number(abs(total_withdrawals)),  # مجموع برداشت‌ها (فرمت شده)
            'total_profits_formatted': FinancialCalculationService.format_number(total_profits),  # مجموع سود (فرمت شده)
            'net_capital_formatted': FinancialCalculationService.format_number(net_capital)  # سرمایه خالص (فرمت شده)
        }


class ComprehensiveCalculations(FinancialCalculationService):
    """محاسبات جامع و ترکیبی"""
    
    @staticmethod
    def get_comprehensive_project_analysis(project_id: Optional[int] = None) -> Dict:
        """
        دریافت تحلیل جامع پروژه
        
        Args:
            project_id: شناسه پروژه (الزامی است)
            
        Returns:
            Dict: تحلیل جامع پروژه
        """
        logger.info("Getting comprehensive project analysis for project_id: %s", project_id)
        # project_id باید از API endpoint تنظیم شود (از پروژه جاری از session)
        if not project_id:
            logger.warning("get_comprehensive_project_analysis called without project_id")
            return {'error': 'شناسه پروژه الزامی است'}
        
        try:
            project = models.Project.objects.get(id=project_id)
            logger.debug("Project found: %s (id: %s)", project.name, project_id)
        except models.Project.DoesNotExist:
            logger.error("Project not found in get_comprehensive_project_analysis: project_id=%s", project_id)
            return {'error': 'پروژه یافت نشد'}
        
        # جمع‌آوری تمام آمار
        logger.debug("Collecting all project statistics and metrics")
        project_stats = ProjectCalculations.calculate_project_statistics(project_id)  # آمار کلی پروژه
        cost_metrics = ProjectCalculations.calculate_cost_metrics(project_id)  # معیارهای هزینه
        profit_percentages = ProfitCalculations.calculate_profit_percentages(project_id)  # درصدهای سود
        transaction_stats = TransactionCalculations.calculate_transaction_statistics(project_id)  # آمار تراکنش‌ها
        # investors_summary = InvestorCalculations.get_all_investors_summary(project_id)  # موقتاً غیرفعال
        investors_summary = []  # خلاصه اطلاعات سرمایه‌گذاران
        
        # دریافت نرخ سود فعلی
        # توجه: get_current_rate نیاز به project دارد
        current_rate = models.InterestRate.get_current_rate(project=project) if project else None  # دریافت نرخ سود فعلی
        current_interest_rate = float(current_rate.rate * 100) if current_rate else 0  # نرخ سود فعلی (درصد)
        
        return {
            'project_info': project_stats.get('project', {}),  # اطلاعات پروژه
            'project_statistics': project_stats,  # آمار کلی پروژه
            'cost_metrics': cost_metrics,  # معیارهای هزینه
            'profit_percentages': profit_percentages,  # درصدهای سود
            'transaction_statistics': transaction_stats,  # آمار تراکنش‌ها
            'investors_summary': investors_summary,  # خلاصه اطلاعات سرمایه‌گذاران
            'current_interest_rate': current_interest_rate,  # نرخ سود فعلی (درصد)
            'current_interest_rate_formatted': FinancialCalculationService.format_percentage(current_interest_rate, 15),  # نرخ سود فعلی (فرمت شده)
            'generated_at': timezone.now().isoformat()  # زمان تولید گزارش
        }
