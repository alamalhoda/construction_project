"""
سرویس تولید فایل Excel برای export کامل اطلاعات و محاسبات پروژه
این فایل شامل کلاس‌های مختلفی است که هر کدام یک شیت از فایل Excel را تولید می‌کنند
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from . import models
from .calculations import (
    ProjectCalculations,
    ProfitCalculations,
    InvestorCalculations,
    TransactionCalculations
)


class ExcelStyleHelper:
    """کلاس کمکی برای استایل‌های Excel"""
    
    @staticmethod
    def normalize_datetime(dt):
        """حذف timezone از datetime برای سازگاری با Excel"""
        if dt is None:
            return None
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            # تبدیل به naive datetime (بدون timezone)
            return dt.replace(tzinfo=None)
        return dt
    
    @staticmethod
    def get_header_font():
        """فونت هدر"""
        return Font(name='Tahoma', size=11, bold=True, color='FFFFFF')
    
    @staticmethod
    def get_header_fill():
        """پس‌زمینه هدر"""
        return PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    
    @staticmethod
    def get_default_font():
        """فونت پیش‌فرض"""
        return Font(name='Tahoma', size=10)
    
    @staticmethod
    def get_border():
        """حاشیه سلول"""
        thin_border = Side(border_style='thin', color='000000')
        return Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
    
    @staticmethod
    def get_center_alignment():
        """تراز وسط"""
        return Alignment(horizontal='center', vertical='center')
    
    @staticmethod
    def apply_header_style(cell):
        """اعمال استایل به هدر"""
        cell.font = ExcelStyleHelper.get_header_font()
        cell.fill = ExcelStyleHelper.get_header_fill()
        cell.alignment = ExcelStyleHelper.get_center_alignment()
        cell.border = ExcelStyleHelper.get_border()
    
    @staticmethod
    def apply_cell_style(cell):
        """اعمال استایل به سلول عادی"""
        cell.font = ExcelStyleHelper.get_default_font()
        cell.border = ExcelStyleHelper.get_border()
    
    @staticmethod
    def auto_adjust_column_width(worksheet):
        """تنظیم خودکار عرض ستون‌ها"""
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # حداکثر 50
            worksheet.column_dimensions[column_letter].width = adjusted_width


class ProjectSheet:
    """شیت اطلاعات پروژه"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت اطلاعات پروژه"""
        ws = workbook.create_sheet(title="Project")
        
        # هدرها
        headers = [
            'ID', 'نام پروژه', 'تاریخ شروع (شمسی)', 'تاریخ شروع (میلادی)',
            'تاریخ پایان (شمسی)', 'تاریخ پایان (میلادی)', 'فعال',
            'زیربنای کل', 'ضریب اصلاحی', 'تاریخ ایجاد', 'تاریخ به‌روزرسانی'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # نوشتن داده‌ها
        data = [
            project.id,
            project.name,
            str(project.start_date_shamsi),
            project.start_date_gregorian,
            str(project.end_date_shamsi),
            project.end_date_gregorian,
            'بله' if project.is_active else 'خیر',
            float(project.total_infrastructure),
            float(project.correction_factor),
            ExcelStyleHelper.normalize_datetime(project.created_at),
            ExcelStyleHelper.normalize_datetime(project.updated_at)
        ]
        
        for col_num, value in enumerate(data, 1):
            cell = ws.cell(row=2, column=col_num, value=value)
            ExcelStyleHelper.apply_cell_style(cell)
            
            # فرمت اعداد
            if col_num == 8:  # زیربنای کل
                cell.number_format = '#,##0.00'
            elif col_num == 9:  # ضریب اصلاحی
                cell.number_format = '0.0000000000'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class UnitsSheet:
    """شیت واحدها"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت واحدها"""
        ws = workbook.create_sheet(title="Units")
        
        # هدرها
        headers = [
            'ID', 'شناسه پروژه', 'نام پروژه', 'نام واحد',
            'متراژ', 'قیمت هر متر', 'قیمت نهایی', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت واحدها
        units = models.Unit.objects.filter(project=project).order_by('id')
        
        # نوشتن داده‌ها
        for row_num, unit in enumerate(units, 2):
            data = [
                unit.id,
                unit.project.id,
                unit.project.name,
                unit.name,
                float(unit.area),
                float(unit.price_per_meter),
                float(unit.total_price),
                ExcelStyleHelper.normalize_datetime(unit.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت اعداد
                if col_num in [5, 6, 7]:  # متراژ، قیمت
                    cell.number_format = '#,##0.00'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class InvestorsSheet:
    """شیت سرمایه‌گذاران"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت سرمایه‌گذاران"""
        ws = workbook.create_sheet(title="Investors")
        
        # هدرها
        headers = [
            'ID', 'نام', 'نام خانوادگی', 'شماره تماس', 'ایمیل',
            'نوع مشارکت', 'واحدها', 'تاریخ قرارداد (شمسی)', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت همه سرمایه‌گذاران
        investors = models.Investor.objects.all().order_by('id')
        
        # نوشتن داده‌ها
        for row_num, investor in enumerate(investors, 2):
            # دریافت واحدهای این سرمایه‌گذار در این پروژه
            investor_units = investor.units.filter(project=project)
            units_str = ', '.join([unit.name for unit in investor_units])
            
            data = [
                investor.id,
                investor.first_name,
                investor.last_name,
                investor.phone,
                investor.email or '',
                investor.get_participation_type_display(),
                units_str,
                str(investor.contract_date_shamsi) if investor.contract_date_shamsi else '',
                ExcelStyleHelper.normalize_datetime(investor.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class PeriodsSheet:
    """شیت دوره‌ها"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت دوره‌ها"""
        ws = workbook.create_sheet(title="Periods")
        
        # هدرها
        headers = [
            'ID', 'شناسه پروژه', 'عنوان دوره', 'سال شمسی', 'شماره ماه',
            'نام ماه', 'وزن دوره', 'تاریخ شروع (شمسی)', 'تاریخ شروع (میلادی)',
            'تاریخ پایان (شمسی)', 'تاریخ پایان (میلادی)'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت دوره‌ها
        periods = models.Period.objects.filter(project=project).order_by('year', 'month_number')
        
        # نوشتن داده‌ها
        for row_num, period in enumerate(periods, 2):
            data = [
                period.id,
                period.project.id,
                period.label,
                period.year,
                period.month_number,
                period.month_name,
                period.weight,
                str(period.start_date_shamsi),
                period.start_date_gregorian,
                str(period.end_date_shamsi),
                period.end_date_gregorian
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class InterestRatesSheet:
    """شیت نرخ‌های سود"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت نرخ‌های سود"""
        ws = workbook.create_sheet(title="InterestRates")
        
        # هدرها
        headers = [
            'ID', 'نرخ سود روزانه', 'تاریخ اعمال (شمسی)',
            'تاریخ اعمال (میلادی)', 'توضیحات', 'فعال', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت نرخ‌های سود (همه نرخ‌ها، نه فقط مربوط به یک پروژه خاص)
        interest_rates = models.InterestRate.objects.all().order_by('-effective_date')
        
        # نوشتن داده‌ها
        for row_num, rate in enumerate(interest_rates, 2):
            data = [
                rate.id,
                float(rate.rate),
                str(rate.effective_date),
                rate.effective_date_gregorian,
                rate.description,
                'بله' if rate.is_active else 'خیر',
                ExcelStyleHelper.normalize_datetime(rate.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت نرخ سود
                if col_num == 2:
                    cell.number_format = '0.000000000000000'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class TransactionsSheet:
    """شیت تراکنش‌ها"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت تراکنش‌ها"""
        ws = workbook.create_sheet(title="Transactions")
        
        # هدرها
        headers = [
            'ID', 'شناسه پروژه', 'شناسه سرمایه‌گذار', 'نام سرمایه‌گذار',
            'شناسه دوره', 'عنوان دوره', 'تاریخ (شمسی)', 'تاریخ (میلادی)',
            'مبلغ', 'نوع تراکنش', 'توضیحات', 'روز مانده', 'روز از شروع',
            'شناسه نرخ سود', 'تولید سیستمی', 'شناسه تراکنش اصلی', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت تراکنش‌ها
        transactions = models.Transaction.objects.filter(project=project).select_related(
            'investor', 'period', 'interest_rate', 'parent_transaction'
        ).order_by('date_gregorian', 'id')
        
        # نوشتن داده‌ها
        for row_num, trans in enumerate(transactions, 2):
            data = [
                trans.id,
                trans.project.id,
                trans.investor.id,
                f"{trans.investor.first_name} {trans.investor.last_name}",
                trans.period.id,
                trans.period.label,
                str(trans.date_shamsi),
                trans.date_gregorian,
                float(trans.amount),
                trans.get_transaction_type_display(),
                trans.description,
                trans.day_remaining,
                trans.day_from_start,
                trans.interest_rate.id if trans.interest_rate else '',
                'بله' if trans.is_system_generated else 'خیر',
                trans.parent_transaction.id if trans.parent_transaction else '',
                ExcelStyleHelper.normalize_datetime(trans.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت مبلغ
                if col_num == 9:
                    cell.number_format = '#,##0.00'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class ExpensesSheet:
    """شیت هزینه‌ها"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت هزینه‌ها"""
        ws = workbook.create_sheet(title="Expenses")
        
        # هدرها
        headers = [
            'ID', 'شناسه پروژه', 'شناسه دوره', 'عنوان دوره',
            'نوع هزینه', 'مبلغ', 'توضیحات', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت هزینه‌ها
        expenses = models.Expense.objects.filter(project=project).select_related('period').order_by('period__year', 'period__month_number', 'id')
        
        # نوشتن داده‌ها
        for row_num, expense in enumerate(expenses, 2):
            data = [
                expense.id,
                expense.project.id,
                expense.period.id,
                expense.period.label,
                expense.get_expense_type_display(),
                float(expense.amount),
                expense.description,
                ExcelStyleHelper.normalize_datetime(expense.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت مبلغ
                if col_num == 6:
                    cell.number_format = '#,##0.00'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class SalesSheet:
    """شیت فروش/مرجوعی‌ها"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت فروش/مرجوعی‌ها"""
        ws = workbook.create_sheet(title="Sales")
        
        # هدرها
        headers = [
            'ID', 'شناسه پروژه', 'شناسه دوره', 'عنوان دوره',
            'مبلغ', 'توضیحات', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت فروش‌ها
        sales = models.Sale.objects.filter(project=project).select_related('period').order_by('period__year', 'period__month_number', 'id')
        
        # نوشتن داده‌ها
        for row_num, sale in enumerate(sales, 2):
            data = [
                sale.id,
                sale.project.id,
                sale.period.id,
                sale.period.label,
                float(sale.amount),
                sale.description,
                ExcelStyleHelper.normalize_datetime(sale.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت مبلغ
                if col_num == 5:
                    cell.number_format = '#,##0.00'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class UserProfilesSheet:
    """شیت پروفایل کاربران"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت پروفایل کاربران"""
        ws = workbook.create_sheet(title="UserProfiles")
        
        # هدرها
        headers = [
            'ID', 'شناسه کاربر', 'نام کاربری', 'نقش',
            'شماره تلفن', 'بخش', 'تاریخ ایجاد'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت پروفایل‌های کاربران
        user_profiles = models.UserProfile.objects.select_related('user').order_by('id')
        
        # نوشتن داده‌ها
        for row_num, profile in enumerate(user_profiles, 2):
            data = [
                profile.id,
                profile.user.id,
                profile.user.username,
                profile.get_role_display(),
                profile.phone or '',
                profile.department or '',
                ExcelStyleHelper.normalize_datetime(profile.created_at)
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class DashboardSheet:
    """شیت داشبورد - خلاصه کل پروژه"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت داشبورد"""
        ws = workbook.create_sheet(title="Dashboard")
        
        # دریافت محاسبات
        stats = ProjectCalculations.calculate_project_statistics(project.id)
        
        if 'error' in stats:
            # در صورت خطا، یک شیت خالی با پیام خطا
            ws.cell(row=1, column=1, value="خطا در دریافت اطلاعات")
            ws.cell(row=2, column=1, value=stats['error'])
            return ws
        
        # عنوان
        title_cell = ws.cell(row=1, column=1, value=f"داشبورد پروژه: {project.name}")
        title_cell.font = Font(name='Tahoma', size=14, bold=True)
        ws.merge_cells('A1:B1')
        
        # فاصله
        row = 3
        
        # بخش اطلاعات واحدها
        section_cell = ws.cell(row=row, column=1, value="اطلاعات واحدها")
        section_cell.font = Font(name='Tahoma', size=12, bold=True)
        section_cell.fill = PatternFill(start_color='E7E6E6', end_color='E7E6E6', fill_type='solid')
        ws.merge_cells(f'A{row}:B{row}')
        row += 1
        
        units_data = [
            ('تعداد واحدها', stats.get('units_statistics', {}).get('total_units', 0)),
            ('متراژ کل', f"{stats.get('units_statistics', {}).get('total_area', 0):,.2f}"),
            ('ارزش کل (تومان)', f"{stats.get('units_statistics', {}).get('total_price', 0):,.2f}"),
            ('زیربنای کل', f"{stats.get('project', {}).get('total_infrastructure', 0):,.2f}"),
        ]
        
        for label, value in units_data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        row += 1
        
        # بخش اطلاعات مالی
        section_cell = ws.cell(row=row, column=1, value="اطلاعات مالی")
        section_cell.font = Font(name='Tahoma', size=12, bold=True)
        section_cell.fill = PatternFill(start_color='E7E6E6', end_color='E7E6E6', fill_type='solid')
        ws.merge_cells(f'A{row}:B{row}')
        row += 1
        
        financial_data = [
            ('سرمایه موجود (تومان)', f"{stats.get('transaction_statistics', {}).get('net_principal', 0):,.2f}"),
            ('سود کل (تومان)', f"{stats.get('transaction_statistics', {}).get('total_profits', 0):,.2f}"),
            ('موجودی کل (تومان)', f"{stats.get('transaction_statistics', {}).get('grand_total', 0):,.2f}"),
            ('مجموع هزینه‌ها (تومان)', f"{stats.get('expense_statistics', {}).get('total_expenses', 0):,.2f}"),
            ('مجموع فروش (تومان)', f"{stats.get('expense_statistics', {}).get('total_sales', 0):,.2f}"),
            ('مانده صندوق (تومان)', f"{stats.get('expense_statistics', {}).get('final_cost', 0):,.2f}"),
        ]
        
        for label, value in financial_data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        row += 1
        
        # بخش سرمایه‌گذاران
        section_cell = ws.cell(row=row, column=1, value="اطلاعات سرمایه‌گذاران")
        section_cell.font = Font(name='Tahoma', size=12, bold=True)
        section_cell.fill = PatternFill(start_color='E7E6E6', end_color='E7E6E6', fill_type='solid')
        ws.merge_cells(f'A{row}:B{row}')
        row += 1
        
        investor_data = [
            ('تعداد کل سرمایه‌گذاران', stats.get('investor_statistics', {}).get('total_investors', 0)),
            ('تعداد مالکان', stats.get('investor_statistics', {}).get('owners_count', 0)),
        ]
        
        for label, value in investor_data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        # تنظیم عرض ستون‌ها
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 25
        
        # اعمال استایل به همه سلول‌ها
        for row_cells in ws.iter_rows():
            for cell in row_cells:
                if cell.value:
                    cell.font = ExcelStyleHelper.get_default_font()
                    cell.border = ExcelStyleHelper.get_border()
        
        return ws


class ProfitMetricsSheet:
    """شیت محاسبات سود"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت محاسبات سود"""
        ws = workbook.create_sheet(title="Profit_Metrics")
        
        # دریافت محاسبات
        metrics = ProfitCalculations.calculate_profit_percentages(project.id)
        
        if 'error' in metrics:
            ws.cell(row=1, column=1, value="خطا در دریافت اطلاعات")
            ws.cell(row=2, column=1, value=metrics['error'])
            return ws
        
        # عنوان
        title_cell = ws.cell(row=1, column=1, value="محاسبات سود")
        title_cell.font = Font(name='Tahoma', size=14, bold=True)
        ws.merge_cells('A1:B1')
        
        row = 3
        
        # داده‌ها
        data = [
            ('درصد سود کل', f"{metrics.get('total_profit_percentage', 0):.2f}%"),
            ('درصد سود سالانه', f"{metrics.get('annual_profit_percentage', 0):.2f}%"),
            ('درصد سود ماهانه', f"{metrics.get('monthly_profit_percentage', 0):.2f}%"),
            ('درصد سود روزانه', f"{metrics.get('daily_profit_percentage', 0):.6f}%"),
            ('دوره متوسط ساخت (ماه)', f"{metrics.get('average_construction_period', 0):.2f}"),
            ('ضریب اصلاحی', f"{metrics.get('correction_factor', 1):.10f}"),
        ]
        
        for label, value in data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        # تنظیم عرض ستون‌ها
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 20
        
        # اعمال استایل
        for row_cells in ws.iter_rows():
            for cell in row_cells:
                if cell.value:
                    cell.font = ExcelStyleHelper.get_default_font()
                    cell.border = ExcelStyleHelper.get_border()
        
        return ws


class CostMetricsSheet:
    """شیت محاسبات هزینه"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت محاسبات هزینه"""
        ws = workbook.create_sheet(title="Cost_Metrics")
        
        # دریافت محاسبات
        metrics = ProjectCalculations.calculate_cost_metrics(project.id)
        
        if 'error' in metrics:
            ws.cell(row=1, column=1, value="خطا در دریافت اطلاعات")
            ws.cell(row=2, column=1, value=metrics['error'])
            return ws
        
        # عنوان
        title_cell = ws.cell(row=1, column=1, value="محاسبات هزینه")
        title_cell.font = Font(name='Tahoma', size=14, bold=True)
        ws.merge_cells('A1:B1')
        
        row = 3
        
        # داده‌ها
        data = [
            ('مجموع هزینه‌ها (تومان)', f"{metrics.get('total_expenses', 0):,.2f}"),
            ('مجموع فروش (تومان)', f"{metrics.get('total_sales', 0):,.2f}"),
            ('هزینه نهایی (تومان)', f"{metrics.get('final_cost', 0):,.2f}"),
            ('ارزش کل (تومان)', f"{metrics.get('total_value', 0):,.2f}"),
            ('سود نهایی (تومان)', f"{metrics.get('final_profit_amount', 0):,.2f}"),
            ('درصد سود کل', f"{metrics.get('total_profit_percentage', 0):.2f}%"),
            ('', ''),
            ('هزینه هر متر خالص (تومان)', f"{metrics.get('net_cost_per_meter', 0):,.2f}"),
            ('هزینه هر متر ناخالص (تومان)', f"{metrics.get('gross_cost_per_meter', 0):,.2f}"),
            ('ارزش هر متر (تومان)', f"{metrics.get('value_per_meter', 0):,.2f}"),
            ('', ''),
            ('متراژ کل', f"{metrics.get('total_area', 0):,.2f}"),
            ('زیربنای کل', f"{metrics.get('total_infrastructure', 0):,.2f}"),
        ]
        
        for label, value in data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        # تنظیم عرض ستون‌ها
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 25
        
        # اعمال استایل
        for row_cells in ws.iter_rows():
            for cell in row_cells:
                if cell.value:
                    cell.font = ExcelStyleHelper.get_default_font()
                    cell.border = ExcelStyleHelper.get_border()
        
        return ws


class InvestorAnalysisSheet:
    """شیت تحلیل سرمایه‌گذاران"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت تحلیل سرمایه‌گذاران"""
        ws = workbook.create_sheet(title="Investor_Analysis")
        
        # هدرها
        headers = [
            'نام سرمایه‌گذار', 'آورده کل', 'برداشت کل', 'سرمایه خالص',
            'سود کل', 'موجودی کل', 'نسبت سرمایه (%)', 'نسبت سود (%)',
            'نسبت موجودی کل (%)', 'شاخص نفع'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت همه سرمایه‌گذاران
        investors = models.Investor.objects.all().order_by('last_name', 'first_name')
        
        # نوشتن داده‌ها
        for row_num, investor in enumerate(investors, 2):
            # محاسبات مستقیم برای سرمایه‌گذار
            transactions = models.Transaction.objects.filter(
                investor=investor,
                project=project
            )
            
            # محاسبه مبالغ
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
            
            # محاسبه نسبت‌ها (ساده)
            try:
                # دریافت آمار کل پروژه برای محاسبه نسبت‌ها
                project_stats = ProjectCalculations.calculate_project_statistics(project.id)
                total_project_principal = project_stats.get('transaction_statistics', {}).get('net_principal', 1)
                total_project_profits = project_stats.get('transaction_statistics', {}).get('total_profits', 1)
                total_project_balance = project_stats.get('transaction_statistics', {}).get('grand_total', 1)
                
                capital_ratio = (net_principal / total_project_principal * 100) if total_project_principal != 0 else 0
                profit_ratio = (float(total_profit) / total_project_profits * 100) if total_project_profits != 0 else 0
                total_ratio = (total_balance / total_project_balance * 100) if total_project_balance != 0 else 0
                
                # شاخص نفع
                profit_index = (profit_ratio / capital_ratio) if capital_ratio != 0 else 0
                
            except:
                capital_ratio = profit_ratio = total_ratio = profit_index = 0
            
            data = [
                f"{investor.first_name} {investor.last_name}",
                float(total_principal),
                float(total_withdrawal),
                net_principal,
                float(total_profit),
                total_balance,
                capital_ratio,
                profit_ratio,
                total_ratio,
                profit_index,
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت اعداد
                if col_num in [2, 3, 4, 5, 6]:  # مبالغ
                    cell.number_format = '#,##0.00'
                elif col_num in [7, 8, 9]:  # درصدها
                    cell.number_format = '0.00'
                elif col_num == 10:  # شاخص نفع
                    cell.number_format = '0.0000'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class PeriodSummarySheet:
    """شیت خلاصه دوره‌ای"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت خلاصه دوره‌ای"""
        ws = workbook.create_sheet(title="Period_Summary")
        
        # هدرها
        headers = [
            'عنوان دوره', 'آورده', 'برداشت', 'سرمایه خالص', 'سود',
            'هزینه‌ها', 'فروش', 'مانده صندوق',
            'آورده تجمعی', 'برداشت تجمعی', 'سرمایه تجمعی', 'سود تجمعی',
            'هزینه تجمعی', 'فروش تجمعی', 'مانده تجمعی'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # دریافت دوره‌ها
        periods = models.Period.objects.filter(project=project).order_by('year', 'month_number')
        
        # متغیرهای تجمعی
        cumulative_deposits = 0
        cumulative_withdrawals = 0
        cumulative_net_capital = 0
        cumulative_profits = 0
        cumulative_expenses = 0
        cumulative_sales = 0
        final_fund_balance = 0
        
        row_num = 2
        
        # نوشتن داده‌ها
        for period in periods:
            # محاسبه تراکنش‌های دوره
            period_transactions = models.Transaction.objects.filter(
                project=project,
                period=period
            )
            
            # آورده
            deposits = period_transactions.filter(
                transaction_type='principal_deposit'
            ).aggregate(total=Sum('amount'))['total'] or 0
            deposits = float(deposits)
            cumulative_deposits += deposits
            
            # برداشت
            withdrawals = period_transactions.filter(
                transaction_type='principal_withdrawal'
            ).aggregate(total=Sum('amount'))['total'] or 0
            withdrawals = float(withdrawals)
            cumulative_withdrawals += withdrawals
            
            # سود
            profits = period_transactions.filter(
                transaction_type='profit_accrual'
            ).aggregate(total=Sum('amount'))['total'] or 0
            profits = float(profits)
            cumulative_profits += profits
            
            # سرمایه خالص دوره (withdrawals منفی است)
            net_capital = deposits + withdrawals
            cumulative_net_capital += net_capital
            
            # هزینه‌های دوره
            expenses = models.Expense.objects.filter(
                project=project,
                period=period
            ).aggregate(total=Sum('amount'))['total'] or 0
            expenses = float(expenses)
            cumulative_expenses += expenses
            
            # فروش/مرجوعی دوره
            sales = models.Sale.objects.filter(
                project=project,
                period=period
            ).aggregate(total=Sum('amount'))['total'] or 0
            sales = float(sales)
            cumulative_sales += sales
            
            # مانده صندوق
            fund_balance = cumulative_net_capital - cumulative_expenses + cumulative_sales
            final_fund_balance = fund_balance
            
            # داده‌های ردیف
            data = [
                period.label,
                deposits,
                withdrawals,
                net_capital,
                profits,
                expenses,
                sales,
                fund_balance,
                cumulative_deposits,
                cumulative_withdrawals,
                cumulative_net_capital,
                cumulative_profits,
                cumulative_expenses,
                cumulative_sales,
                fund_balance
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت مبالغ
                if col_num > 1:
                    cell.number_format = '#,##0.00'
            
            row_num += 1
        
        # افزودن ردیف جمع کل
        total_data = [
            'جمع کل',
            cumulative_deposits,
            cumulative_withdrawals,
            cumulative_net_capital,
            cumulative_profits,
            cumulative_expenses,
            cumulative_sales,
            final_fund_balance,
            '', '', '', '', '', '', ''
        ]
        
        for col_num, value in enumerate(total_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.font = Font(name='Tahoma', size=10, bold=True)
            cell.border = ExcelStyleHelper.get_border()
            cell.fill = PatternFill(start_color='D9D9D9', end_color='D9D9D9', fill_type='solid')
            
            if col_num > 1 and value != '':
                cell.number_format = '#,##0.00'
        
        # تنظیم عرض ستون‌ها
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws


class TransactionSummarySheet:
    """شیت خلاصه تراکنش‌ها"""
    
    @staticmethod
    def create(workbook, project):
        """ایجاد شیت خلاصه تراکنش‌ها"""
        ws = workbook.create_sheet(title="Transaction_Summary")
        
        # دریافت محاسبات
        stats = TransactionCalculations.calculate_transaction_statistics(project_id=project.id)
        
        if 'error' in stats:
            ws.cell(row=1, column=1, value="خطا در دریافت اطلاعات")
            ws.cell(row=2, column=1, value=stats['error'])
            return ws
        
        # عنوان
        title_cell = ws.cell(row=1, column=1, value="خلاصه تراکنش‌ها")
        title_cell.font = Font(name='Tahoma', size=14, bold=True)
        ws.merge_cells('A1:B1')
        
        row = 3
        
        # داده‌ها
        data = [
            ('تعداد کل تراکنش‌ها', stats.get('total_transactions', 0)),
            ('', ''),
            ('مجموع آورده‌ها (تومان)', f"{stats.get('total_deposits', 0):,.2f}"),
            ('مجموع برداشت‌ها (تومان)', f"{stats.get('total_withdrawals', 0):,.2f}"),
            ('سرمایه موجود (تومان)', f"{stats.get('net_capital', 0):,.2f}"),
            ('', ''),
            ('مجموع سودها (تومان)', f"{stats.get('total_profits', 0):,.2f}"),
        ]
        
        for label, value in data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            row += 1
        
        # تنظیم عرض ستون‌ها
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 25
        
        # اعمال استایل
        for row_cells in ws.iter_rows():
            for cell in row_cells:
                if cell.value:
                    cell.font = ExcelStyleHelper.get_default_font()
                    cell.border = ExcelStyleHelper.get_border()
        
        return ws


class ExcelExportService:
    """سرویس اصلی تولید فایل Excel"""
    
    def __init__(self, project=None):
        """
        مقداردهی اولیه
        
        Args:
            project: پروژه مورد نظر (اگر None باشد، پروژه فعال استفاده می‌شود)
        """
        self.project = project or models.Project.get_active_project()
        self.workbook = Workbook()
    
    def generate_excel(self):
        """
        تولید فایل Excel کامل با تمام شیت‌ها
        
        Returns:
            Workbook: فایل Excel آماده
        """
        if not self.project:
            raise ValueError('هیچ پروژه‌ای برای export یافت نشد')
        
        # حذف شیت پیش‌فرض
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']
        
        # ایجاد شیت‌های پایه
        self.create_base_sheets()
        
        # ایجاد شیت‌های محاسباتی
        self.create_calculation_sheets()
        
        return self.workbook
    
    def create_base_sheets(self):
        """ایجاد شیت‌های داده پایه"""
        ProjectSheet.create(self.workbook, self.project)
        UnitsSheet.create(self.workbook, self.project)
        InvestorsSheet.create(self.workbook, self.project)
        PeriodsSheet.create(self.workbook, self.project)
        InterestRatesSheet.create(self.workbook, self.project)
        TransactionsSheet.create(self.workbook, self.project)
        ExpensesSheet.create(self.workbook, self.project)
        SalesSheet.create(self.workbook, self.project)
        UserProfilesSheet.create(self.workbook, self.project)
    
    def create_calculation_sheets(self):
        """ایجاد شیت‌های محاسباتی"""
        DashboardSheet.create(self.workbook, self.project)
        ProfitMetricsSheet.create(self.workbook, self.project)
        CostMetricsSheet.create(self.workbook, self.project)
        InvestorAnalysisSheet.create(self.workbook, self.project)
        PeriodSummarySheet.create(self.workbook, self.project)
        TransactionSummarySheet.create(self.workbook, self.project)

