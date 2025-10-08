"""
سرویس محاسبات مالی پروژه
این فایل شامل تمام محاسبات مالی است که قبلاً در JavaScript انجام می‌شد
"""

from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, Count, Q
from django.utils import timezone
import jdatetime
from typing import Dict, List, Optional, Tuple
from . import models


class FinancialCalculationService:
    """سرویس محاسبات مالی پروژه"""
    
    @staticmethod
    def get_active_project() -> Optional[models.Project]:
        """دریافت پروژه فعال"""
        return models.Project.get_active_project()
    
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


class ProjectCalculations(FinancialCalculationService):
    """محاسبات مربوط به پروژه"""
    
    @staticmethod
    def calculate_project_statistics(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه آمار کامل پروژه
        
        Args:
            project_id: شناسه پروژه (اختیاری، اگر None باشد از پروژه فعال استفاده می‌شود)
            
        Returns:
            Dict: آمار کامل پروژه
        """
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # آمار واحدها
        units_stats = models.Unit.objects.filter(project=project).aggregate(
            total_units=Count('id'),
            total_area=Sum('area'),
            total_price=Sum('total_price')
        )
        
        # آمار تراکنش‌ها
        transaction_stats = models.Transaction.objects.filter(project=project).aggregate(
            total_deposits=Sum('amount', filter=Q(transaction_type='principal_deposit')),
            total_withdrawals=Sum('amount', filter=Q(transaction_type='principal_withdrawal')),
            total_profits=Sum('amount', filter=Q(transaction_type='profit_accrual'))
        )
        
        # آمار هزینه‌ها
        expense_stats = models.Expense.objects.filter(project=project).aggregate(
            total_expenses=Sum('amount')
        )
        
        # آمار فروش‌ها
        sale_stats = models.Sale.objects.filter(project=project).aggregate(
            total_sales=Sum('amount')
        )
        
        # محاسبات اصلی
        total_deposits = float(transaction_stats['total_deposits'] or 0)
        total_withdrawals = float(transaction_stats['total_withdrawals'] or 0)
        total_profits = float(transaction_stats['total_profits'] or 0)
        total_expenses = float(expense_stats['total_expenses'] or 0)
        total_sales = float(sale_stats['total_sales'] or 0)
        
        # سرمایه موجود (برداشت‌ها منفی هستند)
        net_principal = total_deposits + total_withdrawals
        
        # موجودی کل
        grand_total = net_principal + total_profits
        
        # هزینه نهایی
        final_cost = total_expenses - total_sales
        
        # آمار سرمایه‌گذاران (از طریق تراکنش‌ها)
        investor_ids = models.Transaction.objects.filter(project=project).values_list('investor_id', flat=True).distinct()
        investors_count = len(investor_ids)
        owners_count = models.Investor.objects.filter(id__in=investor_ids, participation_type='owner').count()
        investors_only_count = models.Investor.objects.filter(id__in=investor_ids, participation_type='investor').count()
        
        # محاسبه مدت پروژه
        project_duration = 0
        if project.start_date_gregorian and project.end_date_gregorian:
            delta = project.end_date_gregorian - project.start_date_gregorian
            project_duration = delta.days
        
        # تعداد روزهای فعال (روزهایی که تراکنش انجام شده)
        active_days = models.Transaction.objects.filter(project=project).values('date_gregorian').distinct().count()
        
        return {
            'project': {
                'id': project.id,
                'name': project.name,
                'total_infrastructure': float(project.total_infrastructure),
                'correction_factor': float(project.correction_factor),
                'start_date_shamsi': str(project.start_date_shamsi),
                'end_date_shamsi': str(project.end_date_shamsi),
                'start_date_gregorian': str(project.start_date_gregorian),
                'end_date_gregorian': str(project.end_date_gregorian),
                'is_active': project.is_active
            },
            'units_statistics': {
                'total_units': units_stats['total_units'] or 0,
                'total_area': float(units_stats['total_area'] or 0),
                'total_price': float(units_stats['total_price'] or 0)
            },
            'transaction_statistics': {
                'total_deposits': total_deposits,
                'total_withdrawals': total_withdrawals,
                'total_profits': total_profits,
                'net_principal': net_principal,
                'grand_total': grand_total
            },
            'expense_statistics': {
                'total_expenses': total_expenses,
                'total_sales': total_sales,
                'final_cost': final_cost
            },
            'investor_statistics': {
                'total_investors': investors_count,
                'owners_count': owners_count,
                'investors_count': investors_only_count
            },
            'project_timing': {
                'project_duration_days': project_duration,
                'active_days': active_days
            }
        }
    
    @staticmethod
    def calculate_cost_metrics(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه متریک‌های هزینه
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            Dict: متریک‌های هزینه
        """
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # آمار هزینه‌ها و فروش‌ها
        expense_stats = models.Expense.objects.filter(project=project).aggregate(
            total_expenses=Sum('amount')
        )
        sale_stats = models.Sale.objects.filter(project=project).aggregate(
            total_sales=Sum('amount')
        )
        
        # آمار واحدها
        units_stats = models.Unit.objects.filter(project=project).aggregate(
            total_area=Sum('area'),
            total_price=Sum('total_price')
        )
        
        total_expenses = float(expense_stats['total_expenses'] or 0)
        total_sales = float(sale_stats['total_sales'] or 0)
        total_area = float(units_stats['total_area'] or 0)
        total_value = float(units_stats['total_price'] or 0)
        total_infrastructure = float(project.total_infrastructure)
        
        # محاسبات
        final_cost = total_expenses - total_sales
        final_profit_amount = total_value - final_cost
        
        # محاسبه هزینه و ارزش هر متر
        net_cost_per_meter = final_cost / total_area if total_area > 0 else 0
        gross_cost_per_meter = final_cost / total_infrastructure if total_infrastructure > 0 else 0
        value_per_meter = total_value / total_area if total_area > 0 else 0
        
        # محاسبه درصد سود کل
        total_profit_percentage = (final_profit_amount / final_cost * 100) if final_cost > 0 else 0
        
        # محاسبه مانده صندوق ساختمان
        # فرمول: مجموع کل سرمایه + فروش/مرجوع - کل هزینه
        # یا: مجموع کل سرمایه - مجموع هزینه خالص
        # مجموع کل سرمایه = مجموع آورده - مجموع برداشت
        
        # دریافت آمار تراکنش‌ها برای محاسبه مجموع کل سرمایه
        transaction_stats = models.Transaction.objects.filter(project=project).aggregate(
            total_deposits=Sum('amount', filter=Q(transaction_type='principal_deposit')),
            total_withdrawals=Sum('amount', filter=Q(transaction_type='principal_withdrawal'))
        )
        
        total_deposits = float(transaction_stats['total_deposits'] or 0)
        total_withdrawals = float(transaction_stats['total_withdrawals'] or 0)
        total_capital = total_deposits + total_withdrawals  # withdrawal منفی است
        
        # محاسبه هزینه خالص
        net_cost = total_expenses - total_sales
        
        # محاسبه مانده صندوق ساختمان
        building_fund_balance = total_capital - net_cost
        
        return {
            'final_cost': final_cost,
            'final_profit_amount': final_profit_amount,
            'total_profit_percentage': total_profit_percentage,
            'net_cost_per_meter': net_cost_per_meter,
            'gross_cost_per_meter': gross_cost_per_meter,
            'value_per_meter': value_per_meter,
            'total_expenses': total_expenses,
            'total_sales': total_sales,
            'total_value': total_value,
            'total_area': total_area,
            'total_infrastructure': total_infrastructure,
            'total_capital': total_capital,
            'net_cost': net_cost,
            'building_fund_balance': building_fund_balance
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
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
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
        
        return round(average_period, 2)
    
    @staticmethod
    def calculate_profit_percentages(project_id: Optional[int] = None) -> Dict:
        """
        محاسبه درصدهای سود (کل، سالانه، ماهانه، روزانه)
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            Dict: درصدهای سود
        """
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # محاسبه متریک‌های هزینه
        cost_metrics = ProjectCalculations.calculate_cost_metrics(project_id)
        
        if 'error' in cost_metrics:
            return cost_metrics
        
        total_profit_percentage = cost_metrics['total_profit_percentage']
        
        # محاسبه دوره متوسط ساخت
        average_period = ProfitCalculations.calculate_average_construction_period(project_id)
        
        # محاسبه درصد سود سالانه
        annual_profit_percentage = (total_profit_percentage / average_period * 12) if average_period > 0 else 0
        
        # محاسبه درصد سود ماهانه
        monthly_profit_percentage = annual_profit_percentage / 12
        
        # محاسبه درصد سود روزانه با ضریب اصلاحی
        correction_factor = float(project.correction_factor)
        daily_profit_percentage = (annual_profit_percentage / 365) * correction_factor
        
        return {
            'total_profit_percentage': round(total_profit_percentage, 2),
            'annual_profit_percentage': round(annual_profit_percentage, 2),
            'monthly_profit_percentage': round(monthly_profit_percentage, 2),
            'daily_profit_percentage': round(daily_profit_percentage, 8),  # 8 رقم اعشار برای دقت
            'average_construction_period': average_period,
            'correction_factor': correction_factor
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
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # دریافت سرمایه‌گذار
        try:
            investor = models.Investor.objects.get(id=investor_id)
        except models.Investor.DoesNotExist:
            return {'error': 'سرمایه‌گذار یافت نشد'}
        
        # آمار تراکنش‌های سرمایه‌گذار
        transactions = models.Transaction.objects.filter(
            investor=investor
        ).filter(project=project)
        
        # محاسبه مجموع‌ها
        total_principal = transactions.filter(
            transaction_type='principal_deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_withdrawal = transactions.filter(
            transaction_type='principal_withdrawal'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_profit = transactions.filter(
            transaction_type='profit_accrual'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # محاسبات اصلی
        net_principal = float(total_principal) + float(total_withdrawal)  # withdrawal منفی است
        total_balance = net_principal + float(total_profit)
        
        return {
            'investor': {
                'id': investor.id,
                'name': f"{investor.first_name} {investor.last_name}",
                'first_name': investor.first_name,
                'last_name': investor.last_name,
                'participation_type': investor.participation_type
            },
            'amounts': {
                'total_principal': float(total_principal),
                'total_withdrawal': float(total_withdrawal),
                'total_profit': float(total_profit),
                'net_principal': net_principal,
                'total_balance': total_balance
            },
            'amounts_toman': {
                # حالا که داده‌ها در دیتابیس به تومان هستند، نیازی به تقسیم بر 10 نیست
                'total_principal': float(total_principal),
                'total_withdrawal': abs(float(total_withdrawal)),
                'total_profit': float(total_profit),
                'net_principal': net_principal,
                'total_balance': total_balance
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
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # آمار سرمایه‌گذار
        investor_stats = InvestorCalculations.calculate_investor_statistics(investor_id, project_id)
        
        if 'error' in investor_stats:
            return investor_stats
        
        # آمار کل پروژه
        project_stats = ProjectCalculations.calculate_project_statistics(project_id)
        
        if 'error' in project_stats:
            return project_stats
        
        # مقادیر سرمایه‌گذار
        net_principal = investor_stats['amounts']['net_principal']
        total_profit = investor_stats['amounts']['total_profit']
        total_balance = investor_stats['amounts']['total_balance']
        
        # مقادیر کل پروژه
        project_net_principal = project_stats['transaction_statistics']['net_principal']
        project_total_profits = project_stats['transaction_statistics']['total_profits']
        project_grand_total = project_stats['transaction_statistics']['grand_total']
        
        # محاسبه نسبت‌ها
        capital_ratio = (net_principal / project_net_principal * 100) if project_net_principal > 0 else 0
        profit_ratio = (total_profit / project_total_profits * 100) if project_total_profits > 0 else 0
        total_ratio = (total_balance / project_grand_total * 100) if project_grand_total > 0 else 0
        
        # محاسبه شاخص نفع
        profit_index = 0
        if project_net_principal > 0 and project_total_profits > 0 and net_principal > 0:
            capital_ratio_decimal = net_principal / project_net_principal
            profit_ratio_decimal = total_profit / project_total_profits
            
            if capital_ratio_decimal > 0:
                profit_index = profit_ratio_decimal / capital_ratio_decimal
        
        return {
            'capital_ratio': round(capital_ratio, 2),
            'profit_ratio': round(profit_ratio, 2),
            'total_ratio': round(total_ratio, 2),
            'profit_index': round(profit_index, 2),
            'capital_ratio_formatted': FinancialCalculationService.format_percentage(capital_ratio),
            'profit_ratio_formatted': FinancialCalculationService.format_percentage(profit_ratio),
            'total_ratio_formatted': FinancialCalculationService.format_percentage(total_ratio)
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
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # دریافت سرمایه‌گذار
        try:
            investor = models.Investor.objects.get(id=investor_id)
        except models.Investor.DoesNotExist:
            return {'error': 'سرمایه‌گذار یافت نشد'}
        
        # آمار مالی سرمایه‌گذار
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
            return {
                'ownership_area': 0,
                'total_amount': total_amount,
                'average_price_per_meter': 0,
                'units_count': 0,
                'units': [],
                'message': 'این سرمایه‌گذار هیچ واحدی ندارد'
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
        
        return {
            'ownership_area': round(ownership_area, 2),
            'total_amount': total_amount,
            'net_principal': net_principal,
            'total_profit': total_profit,
            'average_price_per_meter': round(average_price_per_meter, 2),
            'units_count': units.count(),
            'units': units_list,
            'total_units_area': total_area,
            'ownership_percentage': round((ownership_area / total_area * 100), 2) if total_area > 0 else 0
        }
    
    @staticmethod
    def get_all_investors_summary(project_id: Optional[int] = None) -> List[Dict]:
        """
        دریافت خلاصه آمار تمام سرمایه‌گذاران
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            List[Dict]: لیست آمار سرمایه‌گذاران
        """
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return []
        
        # دریافت سرمایه‌گذاران از طریق تراکنش‌ها
        investor_ids = models.Transaction.objects.filter(project=project).values_list('investor_id', flat=True).distinct()
        investors = models.Investor.objects.filter(id__in=investor_ids)
        summary = []
        
        print(f"🔍 تعداد سرمایه‌گذاران یافت شده: {investors.count()}")
        print(f"🔍 investor_ids: {list(investor_ids)}")
        
        for investor in investors:
            try:
                print(f"🔍 پردازش سرمایه‌گذار: {investor.id} - {investor.first_name} {investor.last_name}")
                
                # آمار سرمایه‌گذار
                investor_stats = InvestorCalculations.calculate_investor_statistics(investor.id, project_id)
                investor_ratios = InvestorCalculations.calculate_investor_ratios(investor.id, project_id)
                
                print(f"🔍 investor_stats: {investor_stats}")
                print(f"🔍 investor_ratios: {investor_ratios}")
                
                if 'error' not in investor_stats and 'error' not in investor_ratios:
                    # محاسبه مجموع کل (سرمایه + سود)
                    grand_total = investor_stats['amounts']['net_principal'] + investor_stats['amounts']['total_profit']
                    
                    summary.append({
                        'id': investor.id,
                        'name': f"{investor.first_name} {investor.last_name}",
                        'participation_type': investor.participation_type,
                        'total_deposits': investor_stats['amounts']['total_principal'],
                        'total_withdrawals': abs(investor_stats['amounts']['total_withdrawal']),  # مقدار مثبت
                        'net_principal': investor_stats['amounts']['net_principal'],
                        'total_profit': investor_stats['amounts']['total_profit'],
                        'grand_total': grand_total,
                        'capital_ratio': investor_ratios.get('capital_ratio', 0),
                        'profit_ratio': investor_ratios.get('profit_ratio', 0),
                        'profit_index': investor_ratios.get('profit_index', 0)
                    })
            except Exception as e:
                print(f"خطا در محاسبه آمار سرمایه‌گذار {investor.id}: {e}")
                continue
        
        return summary


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
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # پایه کوئری
        queryset = models.Transaction.objects.filter(project=project)
        
        # اعمال فیلترها
        if filters:
            if 'investor_id' in filters:
                queryset = queryset.filter(investor_id=filters['investor_id'])
            if 'date_from' in filters:
                queryset = queryset.filter(date_gregorian__gte=filters['date_from'])
            if 'date_to' in filters:
                queryset = queryset.filter(date_gregorian__lte=filters['date_to'])
            if 'transaction_type' in filters:
                queryset = queryset.filter(transaction_type=filters['transaction_type'])
        
        # محاسبه آمار
        stats = queryset.aggregate(
            total_deposits=Sum('amount', filter=Q(transaction_type='principal_deposit')),
            total_withdrawals=Sum('amount', filter=Q(transaction_type='principal_withdrawal')),
            total_profits=Sum('amount', filter=Q(transaction_type='profit_accrual')),
            total_transactions=Count('id')
        )
        
        # محاسبات
        total_deposits = float(stats['total_deposits'] or 0)
        total_withdrawals = float(stats['total_withdrawals'] or 0)
        total_profits = float(stats['total_profits'] or 0)
        net_capital = total_deposits + total_withdrawals  # withdrawal منفی است
        
        return {
            'total_transactions': stats['total_transactions'],
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_profits': total_profits,
            'net_capital': net_capital,
            'total_deposits_formatted': FinancialCalculationService.format_number(total_deposits),
            'total_withdrawals_formatted': FinancialCalculationService.format_number(abs(total_withdrawals)),
            'total_profits_formatted': FinancialCalculationService.format_number(total_profits),
            'net_capital_formatted': FinancialCalculationService.format_number(net_capital)
        }


class ComprehensiveCalculations(FinancialCalculationService):
    """محاسبات جامع و ترکیبی"""
    
    @staticmethod
    def get_comprehensive_project_analysis(project_id: Optional[int] = None) -> Dict:
        """
        دریافت تحلیل جامع پروژه
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            Dict: تحلیل جامع پروژه
        """
        project = models.Project.objects.get(id=project_id) if project_id else FinancialCalculationService.get_active_project()
        
        if not project:
            return {'error': 'هیچ پروژه فعالی یافت نشد'}
        
        # جمع‌آوری تمام آمار
        project_stats = ProjectCalculations.calculate_project_statistics(project_id)
        cost_metrics = ProjectCalculations.calculate_cost_metrics(project_id)
        profit_percentages = ProfitCalculations.calculate_profit_percentages(project_id)
        transaction_stats = TransactionCalculations.calculate_transaction_statistics(project_id)
        # investors_summary = InvestorCalculations.get_all_investors_summary(project_id)  # موقتاً غیرفعال
        investors_summary = []
        
        # دریافت نرخ سود فعلی
        current_rate = models.InterestRate.get_current_rate()
        current_interest_rate = float(current_rate.rate * 100) if current_rate else 0
        
        return {
            'project_info': project_stats.get('project', {}),
            'project_statistics': project_stats,
            'cost_metrics': cost_metrics,
            'profit_percentages': profit_percentages,
            'transaction_statistics': transaction_stats,
            'investors_summary': investors_summary,
            'current_interest_rate': current_interest_rate,
            'current_interest_rate_formatted': FinancialCalculationService.format_percentage(current_interest_rate, 15),
            'generated_at': timezone.now().isoformat()
        }
