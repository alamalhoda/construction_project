from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.db import connection

from . import serializers
from . import models
from .api_security import APISecurityPermission, ReadOnlyPermission, AdminOnlyPermission


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for the Expense class"""

    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """دریافت داده‌های داشبورد هزینه‌ها"""
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # دریافت تمام دوره‌ها از مرداد 1402 تا مرداد 1405
            periods = models.Period.objects.filter(
                project=active_project,
                year__gte=1402,
                year__lte=1405
            ).order_by('year', 'month_number')

            # دریافت تمام هزینه‌ها برای پروژه فعال
            expenses = models.Expense.objects.filter(project=active_project)

            # ساختار داده‌ها
            expense_types = [
                ('project_manager', 'مدیر پروژه'),
                ('facilities_manager', 'مسئول تأسیسات'),
                ('procurement', 'کارپرداز'),
                ('warehouse', 'انباردار'),
                ('construction_contractor', 'پیمان ساختمان'),
                ('other', 'سایر'),
            ]

            # ایجاد ماتریس داده‌ها
            dashboard_data = []
            cumulative_total = 0

            for period in periods:
                period_data = {
                    'period_id': period.id,
                    'period_label': period.label,
                    'year': period.year,
                    'month_name': period.month_name,
                    'expenses': {},
                    'period_total': 0,
                    'cumulative_total': 0
                }

                # محاسبه هزینه‌های هر نوع برای این دوره
                for expense_type, expense_label in expense_types:
                    expense_amount = expenses.filter(
                        period=period,
                        expense_type=expense_type
                    ).aggregate(total=Sum('amount'))['total'] or 0

                    period_data['expenses'][expense_type] = {
                        'amount': float(expense_amount),
                        'label': expense_label
                    }
                    period_data['period_total'] += float(expense_amount)

                # محاسبه مجموع تجمیعی
                cumulative_total += period_data['period_total']
                period_data['cumulative_total'] = cumulative_total

                dashboard_data.append(period_data)

            # محاسبه مجموع ستون‌ها
            column_totals = {}
            for expense_type, _ in expense_types:
                column_totals[expense_type] = sum(
                    period['expenses'][expense_type]['amount'] 
                    for period in dashboard_data
                )

            # مجموع کل
            grand_total = sum(period['period_total'] for period in dashboard_data)

            return Response({
                'success': True,
                'data': {
                    'periods': dashboard_data,
                    'expense_types': expense_types,
                    'column_totals': column_totals,
                    'grand_total': grand_total,
                    'project_name': active_project.name
                }
            })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت داده‌ها: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['post'])
    def update_expense(self, request):
        """به‌روزرسانی هزینه"""
        try:
            period_id = request.data.get('period_id')
            expense_type = request.data.get('expense_type')
            amount = request.data.get('amount')

            if not all([period_id, expense_type, amount is not None]):
                return Response({
                    'error': 'پارامترهای مورد نیاز ارسال نشده است'
                }, status=400)

            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # دریافت دوره
            try:
                period = models.Period.objects.get(id=period_id, project=active_project)
            except models.Period.DoesNotExist:
                return Response({
                    'error': 'دوره مورد نظر یافت نشد'
                }, status=404)

            # تبدیل amount به Decimal
            from decimal import Decimal
            amount = Decimal(str(amount))

            # یافتن یا ایجاد هزینه
            expense, created = models.Expense.objects.get_or_create(
                project=active_project,
                period=period,
                expense_type=expense_type,
                defaults={'amount': amount}
            )

            if not created:
                expense.amount = amount
                expense.save()

            return Response({
                'success': True,
                'message': 'هزینه با موفقیت به‌روزرسانی شد',
                'data': {
                    'expense_id': expense.id,
                    'amount': float(expense.amount),
                    'created': created
                }
            })

        except Exception as e:
            return Response({
                'error': f'خطا در به‌روزرسانی هزینه: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def total_expenses(self, request):
        """دریافت مجموع کل هزینه‌های پروژه"""
        try:
            project_id = request.query_params.get('project_id')
            
            if project_id:
                try:
                    project = models.Project.objects.get(id=project_id)
                    expenses = models.Expense.objects.filter(project=project)
                except models.Project.DoesNotExist:
                    return Response({
                        'error': f'پروژه با شناسه {project_id} یافت نشد'
                    }, status=404)
            else:
                # اگر project_id مشخص نشده، از پروژه فعال استفاده کن
                active_project = models.Project.get_active_project()
                if not active_project:
                    return Response({
                        'error': 'هیچ پروژه فعالی یافت نشد'
                    }, status=404)
                expenses = models.Expense.objects.filter(project=active_project)
                project = active_project
            
            # محاسبه مجموع کل هزینه‌ها
            total_amount = sum(expense.amount for expense in expenses)
            
            # محاسبه تعداد هزینه‌ها
            total_count = expenses.count()
            
            # محاسبه مجموع هزینه‌ها بر اساس نوع
            expenses_by_type = {}
            for expense_type, display_name in models.Expense.EXPENSE_TYPES:
                type_expenses = expenses.filter(expense_type=expense_type)
                type_total = sum(expense.amount for expense in type_expenses)
                type_count = type_expenses.count()
                
                if type_total > 0 or type_count > 0:
                    expenses_by_type[expense_type] = {
                        'display_name': display_name,
                        'total_amount': float(type_total),
                        'count': type_count
                    }
            
            return Response({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name
                },
                'total_expenses': {
                    'total_amount': float(total_amount),
                    'total_count': total_count
                },
                'expenses_by_type': expenses_by_type
            })
                
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت مجموع هزینه‌ها: {str(e)}'
            }, status=500)


class InvestorViewSet(viewsets.ModelViewSet):
    """ViewSet for the Investor class"""

    queryset = models.Investor.objects.all()
    serializer_class = serializers.InvestorSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """محاسبه خلاصه مالی تمام سرمایه‌گذاران با استفاده از SQL"""
        
        # استفاده از Raw SQL برای محاسبه دقیق
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    (i.first_name || ' ' || i.last_name) as name,
                    COALESCE(principal_deposits.total, 0) as total_deposits,
                    COALESCE(ABS(principal_withdrawals.total), 0) as total_withdrawals,
                    COALESCE(principal_deposits.total, 0) - COALESCE(ABS(principal_withdrawals.total), 0) as net_principal,
                    COALESCE(profits.total, 0) as total_profit,
                    COALESCE(principal_deposits.total, 0) - COALESCE(ABS(principal_withdrawals.total), 0) + COALESCE(profits.total, 0) as grand_total
                FROM 
                    construction_investor i
                LEFT JOIN (
                    SELECT 
                        investor_id, 
                        SUM(amount) as total
                    FROM construction_transaction 
                    WHERE transaction_type = 'principal_deposit'
                    GROUP BY investor_id
                ) as principal_deposits ON i.id = principal_deposits.investor_id
                LEFT JOIN (
                    SELECT 
                        investor_id, 
                        SUM(amount) as total
                    FROM construction_transaction 
                    WHERE transaction_type = 'principal_withdrawal'
                    GROUP BY investor_id
                ) as principal_withdrawals ON i.id = principal_withdrawals.investor_id
                LEFT JOIN (
                    SELECT 
                        investor_id, 
                        SUM(amount) as total
                    FROM construction_transaction 
                    WHERE transaction_type = 'profit_accrual'
                    GROUP BY investor_id
                ) as profits ON i.id = profits.investor_id
                ORDER BY net_principal DESC
            """)
            
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                # تبدیل None به 0
                for key in ['total_deposits', 'total_withdrawals', 'net_principal', 'total_profit', 'grand_total']:
                    if row_dict[key] is None:
                        row_dict[key] = 0
                        
                # فقط سرمایه‌گذارانی که فعالیت داشته‌اند
                if row_dict['total_deposits'] > 0 or row_dict['total_withdrawals'] > 0 or row_dict['total_profit'] > 0:
                    results.append(row_dict)
        
        return Response(results)


class PeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for the Period class"""

    queryset = models.Period.objects.all()
    serializer_class = serializers.PeriodSerializer
    permission_classes = [APISecurityPermission]



class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for the Project class"""

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """دریافت پروژه فعال"""
        active_project = models.Project.get_active_project()
        if active_project:
            serializer = self.get_serializer(active_project)
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=404)

    @action(detail=False, methods=['post'])
    def set_active(self, request):
        """تنظیم پروژه فعال"""
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'شناسه پروژه الزامی است'}, status=400)
        
        try:
            project = models.Project.set_active_project(project_id)
            if project:
                serializer = self.get_serializer(project)
                return Response({
                    'success': True,
                    'message': f'پروژه "{project.name}" به عنوان پروژه فعال تنظیم شد',
                    'project': serializer.data
                })
            else:
                return Response({'error': 'پروژه یافت نشد'}, status=404)
        except Exception as e:
            return Response({'error': f'خطا در تنظیم پروژه فعال: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def project_timeline(self, request):
        """محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ امروز"""
        from datetime import date
        
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # تاریخ امروز
            today = date.today()
            
            # محاسبه روزهای مانده تا پایان پروژه
            days_remaining = 0
            if active_project.end_date_gregorian:
                end_date = active_project.end_date_gregorian
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                days_remaining = (end_date - today).days
            
            # محاسبه روزهای گذشته از ابتدای پروژه
            days_from_start = 0
            if active_project.start_date_gregorian:
                start_date = active_project.start_date_gregorian
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_from_start = (today - start_date).days
            
            # محاسبه مدت کل پروژه
            total_project_days = 0
            if (active_project.start_date_gregorian and 
                active_project.end_date_gregorian):
                start_date = active_project.start_date_gregorian
                end_date = active_project.end_date_gregorian
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                total_project_days = (end_date - start_date).days

            return Response({
                'success': True,
                'project': {
                    'id': active_project.id,
                    'name': active_project.name,
                    'start_date_shamsi': str(active_project.start_date_shamsi),
                    'end_date_shamsi': str(active_project.end_date_shamsi),
                    'start_date_gregorian': str(active_project.start_date_gregorian),
                    'end_date_gregorian': str(active_project.end_date_gregorian)
                },
                'today': str(today),
                'timeline': {
                    'days_remaining': days_remaining,
                    'days_from_start': days_from_start,
                    'total_project_days': total_project_days,
                    'progress_percentage': round((days_from_start / total_project_days * 100), 2) if total_project_days > 0 else 0
                }
            })

        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه زمان‌بندی پروژه: {str(e)}'
            }, status=500)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Transaction class"""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    permission_classes = [APISecurityPermission]
    filterset_fields = ['investor', 'project', 'period', 'transaction_type']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """آمار کلی تراکنش‌ها"""
        from django.db.models import Count, Sum, Q
        
        # محاسبه آمار کلی
        total_transactions = models.Transaction.objects.count()
        total_deposits = models.Transaction.objects.filter(
            transaction_type='principal_deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_withdrawals = models.Transaction.objects.filter(
            transaction_type='principal_withdrawal'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_profits = models.Transaction.objects.filter(
            transaction_type='profit_accrual'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        unique_investors = models.Transaction.objects.values('investor').distinct().count()
        
        return Response({
            'total_transactions': total_transactions,
            'total_deposits': float(total_deposits),
            'total_withdrawals': float(total_withdrawals),
            'total_profits': float(total_profits),
            'unique_investors': unique_investors
        })

    # کدهای قبلی برای تغییر نرخ سود - کامنت شده برای مراجعه آینده
    """
    @action(detail=False, methods=['post'])
    def update_interest_rate(self, request):
        \"\"\"تغییر نرخ سود و محاسبه مجدد همه سودها\"\"\"
        from decimal import Decimal
        
        new_interest_rate = request.data.get('new_interest_rate')
        description = request.data.get('description', '')
        
        if not new_interest_rate:
            return Response({'error': 'نرخ سود جدید الزامی است'}, status=400)
        
        try:
            new_rate = Decimal(str(new_interest_rate))
            if new_rate <= 0:
                return Response({'error': 'نرخ سود باید مثبت باشد'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'نرخ سود نامعتبر است'}, status=400)
        
        try:
            # اجرای عملیات تغییر نرخ سود
            result = models.Transaction.recalculate_all_profits_with_new_rate(new_rate)
            
            # ذخیره نرخ جدید در InterestRate
            from django.utils import timezone
            import jdatetime
            
            now_gregorian = timezone.now().date()
            now_shamsi = jdatetime.date.fromgregorian(date=now_gregorian)
            
            models.InterestRate.objects.create(
                rate=new_rate,
                effective_date=now_shamsi,
                effective_date_gregorian=now_gregorian,
                description=description,
                is_active=True
            )
            
            return Response({
                'success': True,
                'message': 'نرخ سود با موفقیت تغییر کرد',
                'deleted_count': result['deleted_count'],
                'new_count': result['new_count'],
                'total_affected': result['total_affected'],
                'new_rate': float(new_rate)
            })
            
        except Exception as e:
            return Response({
                'error': f'خطا در تغییر نرخ سود: {str(e)}'
            }, status=500)
    """

    @action(detail=False, methods=['post'])
    def recalculate_profits(self, request):
        """محاسبه مجدد سودها با نرخ سود فعال فعلی"""
        try:
            # دریافت نرخ سود فعال فعلی
            current_rate = models.InterestRate.get_current_rate()
            if not current_rate:
                return Response({
                    'error': 'هیچ نرخ سود فعالی یافت نشد. لطفاً ابتدا نرخ سود را تنظیم کنید.'
                }, status=400)
            
            # اجرای عملیات محاسبه مجدد
            result = models.Transaction.recalculate_all_profits_with_new_rate(current_rate)
            
            return Response({
                'success': True,
                'message': 'سودها با موفقیت محاسبه مجدد شدند',
                'deleted_count': result['deleted_count'],
                'new_count': result['new_count'],
                'total_affected': result['total_affected'],
                'used_rate': float(current_rate.rate)
            })
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه مجدد سودها: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def recalculate_construction_contractor(self, request):
        """محاسبه مجدد همه هزینه‌های پیمان ساختمان"""
        try:
            project_id = request.data.get('project_id')
            
            if project_id:
                try:
                    project = models.Project.objects.get(id=project_id)
                    updated_count = models.Expense.recalculate_all_construction_contractor_expenses(project)
                    return Response({
                        'success': True,
                        'message': f'محاسبه مجدد برای پروژه "{project.name}" با موفقیت انجام شد',
                        'updated_periods': updated_count
                    })
                except models.Project.DoesNotExist:
                    return Response({
                        'error': f'پروژه با شناسه {project_id} یافت نشد'
                    }, status=404)
            else:
                updated_count = models.Expense.recalculate_all_construction_contractor_expenses()
                return Response({
                    'success': True,
                    'message': 'محاسبه مجدد برای همه پروژه‌ها با موفقیت انجام شد',
                    'updated_periods': updated_count
                })
                
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه مجدد هزینه‌های پیمان ساختمان: {str(e)}'
            }, status=500)
    


class InterestRateViewSet(viewsets.ModelViewSet):
    """ViewSet for the InterestRate class"""

    queryset = models.InterestRate.objects.all()
    serializer_class = serializers.InterestRateSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """دریافت نرخ سود فعال فعلی"""
        current_rate = models.InterestRate.get_current_rate()
        if current_rate:
            serializer = self.get_serializer(current_rate)
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ نرخ سود فعالی یافت نشد'}, status=404)


class UnitViewSet(viewsets.ModelViewSet):
    """ViewSet for the Unit class"""

    queryset = models.Unit.objects.all()
    serializer_class = serializers.UnitSerializer
    permission_classes = [APISecurityPermission]
