"""
Django Management Command برای تولید فایل Excel از اطلاعات پروژه

استفاده:
    python manage.py export_excel
    python manage.py export_excel --output /path/to/file.xlsx
    python manage.py export_excel --project-id 1
    python manage.py export_excel --open
    python manage.py export_excel --dynamic

مثال‌ها:
    # تولید فایل Static (پیش‌فرض) با نام پیش‌فرض
    python manage.py export_excel

    # تولید فایل Dynamic با فرمول‌های محاسباتی
    python manage.py export_excel --dynamic

    # تولید فایل با نام دلخواه
    python manage.py export_excel --output my_report.xlsx

    # تولید فایل برای پروژه خاص
    python manage.py export_excel --project-id 2

    # تولید فایل Dynamic و باز کردن خودکار
    python manage.py export_excel --dynamic --open
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from construction.models import Project
from construction.excel_export import ExcelExportService
from construction.excel_export_dynamic import ExcelDynamicExportService
import os
import re


class Command(BaseCommand):
    help = 'تولید فایل Excel شامل تمام اطلاعات و محاسبات پروژه (Static یا Dynamic)'

    def add_arguments(self, parser):
        """افزودن آرگومان‌های دستور"""
        parser.add_argument(
            '--output',
            '-o',
            type=str,
            help='مسیر و نام فایل خروجی (پیش‌فرض: project_<name>_<timestamp>.xlsx)',
        )
        
        parser.add_argument(
            '--project-id',
            '-p',
            type=int,
            help='شناسه پروژه (پیش‌فرض: پروژه فعال)',
        )
        
        parser.add_argument(
            '--open',
            action='store_true',
            help='باز کردن خودکار فایل بعد از تولید',
        )
        
        parser.add_argument(
            '--force',
            '-f',
            action='store_true',
            help='بازنویسی فایل در صورت وجود',
        )
        
        parser.add_argument(
            '--dynamic',
            '-d',
            action='store_true',
            help='تولید فایل Dynamic با فرمول‌های محاسباتی (پیش‌فرض: Static)',
        )

    def handle(self, *args, **options):
        """اجرای دستور"""
        try:
            # دریافت پروژه
            project = self._get_project(options.get('project_id'))
            
            # تعیین نوع Excel
            is_dynamic = options.get('dynamic', False)
            excel_type = 'Dynamic' if is_dynamic else 'Static'
            
            # نمایش اطلاعات پروژه
            self.stdout.write(self.style.SUCCESS(f'📊 پروژه: {project.name}'))
            self.stdout.write(f'   ID: {project.id}')
            if hasattr(project, 'start_date') and project.start_date:
                self.stdout.write(f'   تاریخ شروع: {project.start_date}')
            self.stdout.write(f'   نوع فایل: {excel_type}')
            self.stdout.write('')
            
            # تعیین نام فایل خروجی
            output_path = self._get_output_path(options.get('output'), project, is_dynamic)
            
            # بررسی وجود فایل
            if os.path.exists(output_path) and not options.get('force'):
                raise CommandError(
                    f'فایل {output_path} از قبل وجود دارد. '
                    'برای بازنویسی از --force استفاده کنید.'
                )
            
            # تولید فایل Excel
            self.stdout.write(f'🔄 در حال تولید فایل Excel {excel_type}...')
            
            if is_dynamic:
                excel_service = ExcelDynamicExportService(project)
            else:
                excel_service = ExcelExportService(project)
            
            workbook = excel_service.generate_excel()
            
            # ذخیره فایل
            workbook.save(output_path)
            
            # نمایش اطلاعات فایل
            file_size = os.path.getsize(output_path)
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ فایل با موفقیت تولید شد!'))
            self.stdout.write(f'   📁 مسیر: {output_path}')
            self.stdout.write(f'   📊 حجم: {file_size:,} bytes ({file_size/1024:.2f} KB)')
            self.stdout.write(f'   📅 زمان: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            # نمایش خلاصه محتویات
            self._show_summary(workbook)
            
            # باز کردن فایل
            if options.get('open'):
                self._open_file(output_path)
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🎉 عملیات با موفقیت انجام شد!'))
            
        except Exception as e:
            raise CommandError(f'❌ خطا در تولید فایل Excel: {str(e)}')

    def _get_project(self, project_id):
        """دریافت پروژه"""
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                self.stdout.write(f'✅ پروژه با ID {project_id} یافت شد')
                return project
            except Project.DoesNotExist:
                raise CommandError(f'❌ پروژه با ID {project_id} یافت نشد')
        else:
            # اگر project_id مشخص نشده، خطا بده
            raise CommandError('❌ شناسه پروژه الزامی است. لطفاً --project-id را مشخص کنید.')

    def _get_output_path(self, output, project, is_dynamic=False):
        """تعیین مسیر فایل خروجی"""
        if output:
            # اگر مسیر مشخص شده، از همان استفاده کن
            output_path = output
        else:
            # تولید نام پیش‌فرض
            safe_project_name = re.sub(r'[^\w\-_\.]', '_', project.name)
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            excel_type = 'dynamic' if is_dynamic else 'static'
            filename = f'project_{safe_project_name}_{excel_type}_{timestamp}.xlsx'
            output_path = filename
        
        # تبدیل به مسیر مطلق
        output_path = os.path.abspath(output_path)
        
        return output_path

    def _show_summary(self, workbook):
        """نمایش خلاصه محتویات فایل"""
        self.stdout.write('')
        self.stdout.write('📋 محتویات فایل:')
        
        # شناسایی نوع فایل
        is_dynamic = 'Comprehensive_Metrics' in workbook.sheetnames
        
        if is_dynamic:
            sheet_categories = {
                'شیت‌های راهنما': [
                    '📋 فهرست', '📖 راهنمای فرمول‌ها'
                ],
                'شیت‌های داده پایه': [
                    'Project', 'Units', 'Investors', 'Periods', 
                    'InterestRates', 'Transactions', 'Expenses', 'Sales', 'UserProfiles'
                ],
                'شیت‌های محاسباتی': [
                    'Comprehensive_Metrics', 'Transaction_Profit_Calculations',
                    'PeriodExpenseSummary', 'Investor_Analysis_Dynamic',
                    'Period_Summary_Dynamic', 'Transaction_Summary_Dynamic'
                ]
            }
        else:
            sheet_categories = {
                'شیت‌های داده پایه': [
                    'Project', 'Units', 'Investors', 'Periods', 
                    'InterestRates', 'Transactions', 'Expenses', 'Sales', 'UserProfiles'
                ],
                'شیت‌های محاسباتی': [
                    'Dashboard', 'Profit_Metrics', 'Cost_Metrics', 
                    'Investor_Analysis', 'Period_Summary', 'Transaction_Summary'
                ]
            }
        
        for category, sheets in sheet_categories.items():
            self.stdout.write(f'\n   {category}:')
            for sheet_name in sheets:
                if sheet_name in workbook.sheetnames:
                    sheet = workbook[sheet_name]
                    rows = sheet.max_row - 1 if sheet.max_row > 0 else 0  # منهای هدر
                    cols = sheet.max_column
                    self.stdout.write(f'     ✓ {sheet_name:30s} - {rows:4d} ردیف × {cols:2d} ستون')
        
        # نمایش اطلاعات اضافی برای Dynamic
        if is_dynamic:
            self.stdout.write(f'\n   📌 Named Ranges: {len(workbook.defined_names)} مورد')

    def _open_file(self, file_path):
        """باز کردن فایل با برنامه پیش‌فرض"""
        import platform
        import subprocess
        
        try:
            system = platform.system()
            if system == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            elif system == 'Windows':
                os.startfile(file_path)
            elif system == 'Linux':
                subprocess.run(['xdg-open', file_path], check=True)
            
            self.stdout.write(self.style.SUCCESS('   📂 فایل باز شد'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠️  نتوانستیم فایل را باز کنیم: {str(e)}'))

