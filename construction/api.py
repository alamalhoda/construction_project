from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django.db import connection

from . import serializers
from . import models
from . import calculations
from .api_security import APISecurityPermission, ReadOnlyPermission, AdminOnlyPermission


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for the Expense class"""

    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def with_periods(self, request):
        """دریافت هزینه‌ها با اطلاعات دوره‌ها برای محاسبه دوره متوسط ساخت"""
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # دریافت تمام هزینه‌ها برای پروژه فعال با اطلاعات دوره
            expenses = models.Expense.objects.filter(
                project=active_project
            ).select_related('period')

            # بررسی آمار دوره‌ها
            total_expenses = expenses.count()
            expenses_with_period = expenses.exclude(period__isnull=True).count()
            expenses_without_period = expenses.filter(period__isnull=True).count()

            # استفاده از serializer مخصوص
            serializer = serializers.ExpenseSerializer(expenses, many=True)
            
            return Response({
                'expenses': serializer.data,
                'total_count': total_expenses,
                'expenses_with_period': expenses_with_period,
                'expenses_without_period': expenses_without_period,
                'active_project': active_project.name
            })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت داده‌ها: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """دریافت داده‌های لیست هزینه ها"""
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
                ('facilities_manager', 'سرپرست کارگاه'),
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

                    # دریافت توضیحات هزینه
                    expense_obj = expenses.filter(
                        period=period,
                        expense_type=expense_type
                    ).first()
                    
                    period_data['expenses'][expense_type] = {
                        'amount': float(expense_amount),
                        'label': expense_label,
                        'description': expense_obj.description if expense_obj else '',
                        'expense_id': expense_obj.id if expense_obj else None
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
            description = request.data.get('description', '')

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
                defaults={'amount': amount, 'description': description}
            )

            if not created:
                expense.amount = amount
                expense.description = description
                expense.save()

            return Response({
                'success': True,
                'message': 'هزینه با موفقیت به‌روزرسانی شد',
                'data': {
                    'expense_id': expense.id,
                    'amount': float(expense.amount),
                    'description': expense.description,
                    'created': created
                }
            })

        except Exception as e:
            return Response({
                'error': f'خطا در به‌روزرسانی هزینه: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_expense_details(self, request):
        """دریافت جزئیات هزینه برای ویرایش"""
        try:
            period_id = request.query_params.get('period_id')
            expense_type = request.query_params.get('expense_type')

            if not all([period_id, expense_type]):
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

            # یافتن هزینه
            try:
                expense = models.Expense.objects.get(
                    project=active_project,
                    period=period,
                    expense_type=expense_type
                )
                return Response({
                    'success': True,
                    'data': {
                        'amount': float(expense.amount),
                        'description': expense.description or '',
                        'expense_id': expense.id
                    }
                })
            except models.Expense.DoesNotExist:
                return Response({
                    'success': True,
                    'data': {
                        'amount': 0,
                        'description': '',
                        'expense_id': None
                    }
                })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت جزئیات هزینه: {str(e)}'
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

    @action(detail=False, methods=['get'])
    def participation_stats(self, request):
        """دریافت آمار مشارکت کنندگان بر اساس نوع (مالک و سرمایه گذار)"""
        from django.db.models import Count, Q
        
        # شمارش کل مشارکت کنندگان
        total_count = models.Investor.objects.count()
        
        # شمارش مشارکت کنندگان بر اساس نوع
        owner_count = models.Investor.objects.filter(participation_type='owner').count()
        investor_count = models.Investor.objects.filter(participation_type='investor').count()
        
        # شمارش مشارکت کنندگان فعال (کسانی که تراکنش داشته‌اند)
        active_investor_ids = models.Transaction.objects.values_list('investor_id', flat=True).distinct()
        active_total = models.Investor.objects.filter(id__in=active_investor_ids).count()
        active_owner = models.Investor.objects.filter(
            id__in=active_investor_ids, 
            participation_type='owner'
        ).count()
        active_investor = models.Investor.objects.filter(
            id__in=active_investor_ids, 
            participation_type='investor'
        ).count()
        
        return Response({
            'total_count': total_count,
            'owner_count': owner_count,
            'investor_count': investor_count,
            'active_total': active_total,
            'active_owner': active_owner,
            'active_investor': active_investor
        })

    @action(detail=True, methods=['get'])
    def detailed_statistics(self, request, pk=None):
        """دریافت آمار تفصیلی سرمایه‌گذار"""
        try:
            project_id = request.query_params.get('project_id')
            stats = calculations.InvestorCalculations.calculate_investor_statistics(pk, project_id)
            
            if 'error' in stats:
                return Response(stats, status=400)
            
            return Response(stats)
            
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=True, methods=['get'])
    def ratios(self, request, pk=None):
        """دریافت نسبت‌های سرمایه‌گذار"""
        try:
            project_id = request.query_params.get('project_id')
            ratios = calculations.InvestorCalculations.calculate_investor_ratios(pk, project_id)
            
            if 'error' in ratios:
                return Response(ratios, status=400)
            
            return Response(ratios)
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه نسبت‌های سرمایه‌گذار: {str(e)}'
            }, status=500)
    
    @action(detail=True, methods=['get'])
    def ownership(self, request, pk=None):
        """
        دریافت مالکیت سرمایه‌گذار به متر مربع
        
        محاسبه: (آورده + سود) / قیمت هر متر مربع واحد انتخابی
        """
        try:
            project_id = request.query_params.get('project_id')
            ownership = calculations.InvestorCalculations.calculate_investor_ownership(pk, project_id)
            
            if 'error' in ownership:
                return Response(ownership, status=400)
            
            return Response(ownership)
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه مالکیت سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def all_investors_summary(self, request):
        """دریافت خلاصه آمار تمام سرمایه‌گذاران"""
        try:
            project_id = request.query_params.get('project_id')
            
            # دریافت پروژه فعال
            project = models.Project.get_active_project() if not project_id else models.Project.objects.get(id=project_id)
            
            if not project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=404)
            
            # دریافت سرمایه‌گذاران از طریق تراکنش‌ها
            investor_ids = models.Transaction.objects.filter(project=project).values_list('investor_id', flat=True).distinct()
            investors = models.Investor.objects.filter(id__in=investor_ids)
            
            summary = []
            
            for investor in investors:
                try:
                    # محاسبه آمار ساده
                    transactions = models.Transaction.objects.filter(investor=investor, project=project)
                    
                    from django.db.models import Sum
                    
                    total_deposits = transactions.filter(transaction_type='principal_deposit').aggregate(
                        total=Sum('amount'))['total'] or 0
                    
                    total_withdrawals = transactions.filter(transaction_type='principal_withdrawal').aggregate(
                        total=Sum('amount'))['total'] or 0
                    
                    total_profits = transactions.filter(transaction_type='profit_accrual').aggregate(
                        total=Sum('amount'))['total'] or 0
                    
                    net_principal = float(total_deposits) + float(total_withdrawals)  # withdrawal منفی است
                    grand_total = net_principal + float(total_profits)
                    
                    summary.append({
                        'id': investor.id,
                        'name': f"{investor.first_name} {investor.last_name}",
                        'participation_type': investor.participation_type,
                        'total_deposits': float(total_deposits),
                        'total_withdrawals': abs(float(total_withdrawals)),  # مقدار مثبت
                        'net_principal': net_principal,
                        'total_profit': float(total_profits),
                        'grand_total': grand_total,
                        'capital_ratio': 0,  # موقتاً 0
                        'profit_ratio': 0,   # موقتاً 0
                        'profit_index': 0    # موقتاً 0
                    })
                    
                except Exception as e:
                    print(f"خطا در محاسبه آمار سرمایه‌گذار {investor.id}: {e}")
                    continue
            
            return Response(summary)
            
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت خلاصه سرمایه‌گذاران: {str(e)}'
            }, status=500)


class PeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for the Period class"""

    queryset = models.Period.objects.all()
    serializer_class = serializers.PeriodSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """دریافت داده‌های دوره‌ای برای نمودارها (سرمایه، هزینه، فروش، مانده صندوق)"""
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # دریافت تمام دوره‌ها مرتب شده
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')

            chart_data = []
            cumulative_capital = 0
            cumulative_expenses = 0
            cumulative_sales = 0

            for period in periods:
                # محاسبه سرمایه دوره (آورده + برداشت، چون برداشت در دیتابیس منفی است)
                period_transactions = models.Transaction.objects.filter(
                    project=active_project,
                    period=period
                )
                
                deposits = period_transactions.filter(
                    transaction_type='principal_deposit'
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                withdrawals = period_transactions.filter(
                    transaction_type='principal_withdrawal'
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                # توجه: withdrawals در دیتابیس منفی است، پس از جمع استفاده می‌کنیم
                period_capital = float(deposits + withdrawals)
                cumulative_capital += period_capital

                # محاسبه هزینه‌های دوره
                period_expenses = models.Expense.objects.filter(
                    project=active_project,
                    period=period
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                period_expenses = float(period_expenses)
                cumulative_expenses += period_expenses

                # محاسبه فروش/مرجوعی دوره
                period_sales = models.Sale.objects.filter(
                    project=active_project,
                    period=period
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                period_sales = float(period_sales)
                cumulative_sales += period_sales

                # محاسبه مانده صندوق (سرمایه موجود - هزینه‌ها + فروش)
                fund_balance = cumulative_capital - cumulative_expenses + cumulative_sales

                chart_data.append({
                    'period_id': period.id,
                    'period_label': period.label,
                    'year': period.year,
                    'month_number': period.month_number,
                    'capital': period_capital,
                    'expenses': period_expenses,
                    'sales': period_sales,
                    'fund_balance': fund_balance,
                    'cumulative_capital': cumulative_capital,
                    'cumulative_expenses': cumulative_expenses,
                    'cumulative_sales': cumulative_sales
                })

            return Response({
                'success': True,
                'data': chart_data,
                'active_project': active_project.name
            })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت داده‌های نمودار: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def period_summary(self, request):
        """دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقادیر تجمعی"""
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # دریافت تمام دوره‌ها مرتب شده
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')

            summary_data = []
            
            # متغیرهای تجمعی
            cumulative_deposits = 0
            cumulative_withdrawals = 0
            cumulative_net_capital = 0
            cumulative_profits = 0
            cumulative_expenses = 0
            cumulative_sales = 0
            cumulative_fund_balance = 0

            for period in periods:
                # محاسبه تراکنش‌های دوره
                period_transactions = models.Transaction.objects.filter(
                    project=active_project,
                    period=period
                )
                
                # آورده (deposits)
                deposits = period_transactions.filter(
                    transaction_type='principal_deposit'
                ).aggregate(total=Sum('amount'))['total'] or 0
                deposits = float(deposits)
                cumulative_deposits += deposits
                
                # برداشت (withdrawals)
                withdrawals = period_transactions.filter(
                    transaction_type='principal_withdrawal'
                ).aggregate(total=Sum('amount'))['total'] or 0
                withdrawals = float(withdrawals)
                cumulative_withdrawals += withdrawals
                
                # سود (profits)
                profits = period_transactions.filter(
                    transaction_type='profit_payment'
                ).aggregate(total=Sum('amount'))['total'] or 0
                profits = float(profits)
                cumulative_profits += profits
                
                # سرمایه خالص دوره (net capital)
                # توجه: withdrawals در دیتابیس منفی است، پس از جمع استفاده می‌کنیم
                net_capital = deposits + withdrawals
                cumulative_net_capital += net_capital

                # هزینه‌های دوره
                expenses = models.Expense.objects.filter(
                    project=active_project,
                    period=period
                ).aggregate(total=Sum('amount'))['total'] or 0
                expenses = float(expenses)
                cumulative_expenses += expenses

                # فروش/مرجوعی دوره
                sales = models.Sale.objects.filter(
                    project=active_project,
                    period=period
                ).aggregate(total=Sum('amount'))['total'] or 0
                sales = float(sales)
                cumulative_sales += sales

                # محاسبه مانده صندوق
                # مانده صندوق = سرمایه موجود - هزینه‌ها + فروش
                fund_balance = cumulative_net_capital - cumulative_expenses + cumulative_sales

                # اضافه کردن داده‌های دوره
                summary_data.append({
                    'period_id': period.id,
                    'period_label': period.label,
                    'year': period.year,
                    'month_number': period.month_number,
                    'month_name': period.month_name,
                    'weight': period.weight,
                    
                    # فاکتورهای دوره
                    'deposits': deposits,
                    'withdrawals': withdrawals,
                    'net_capital': net_capital,
                    'profits': profits,
                    'expenses': expenses,
                    'sales': sales,
                    'fund_balance': fund_balance,
                    
                    # مقادیر تجمعی
                    'cumulative_deposits': cumulative_deposits,
                    'cumulative_withdrawals': cumulative_withdrawals,
                    'cumulative_net_capital': cumulative_net_capital,
                    'cumulative_profits': cumulative_profits,
                    'cumulative_expenses': cumulative_expenses,
                    'cumulative_sales': cumulative_sales,
                    'cumulative_fund_balance': fund_balance
                })

            # محاسبه خلاصه کلی
            totals = {
                'total_deposits': cumulative_deposits,
                'total_withdrawals': cumulative_withdrawals,
                'total_net_capital': cumulative_net_capital,
                'total_profits': cumulative_profits,
                'total_expenses': cumulative_expenses,
                'total_sales': cumulative_sales,
                'final_fund_balance': cumulative_fund_balance,
                'total_periods': periods.count()
            }

            return Response({
                'success': True,
                'data': summary_data,
                'totals': totals,
                'active_project': active_project.name
            })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت خلاصه دوره‌ای: {str(e)}'
            }, status=500)



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

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """دریافت آمار کامل پروژه فعال شامل اطلاعات پروژه و آمار واحدها"""
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # آمار واحدها برای پروژه فعال
            from django.db.models import Sum, Count
            units_stats = models.Unit.objects.filter(project=active_project).aggregate(
                total_units=Count('id'),
                total_area=Sum('area'),
                total_price=Sum('total_price')
            )

            # اطلاعات پروژه
            project_data = {
                'id': active_project.id,
                'name': active_project.name,
                'total_infrastructure': float(active_project.total_infrastructure),
                'correction_factor': float(active_project.correction_factor),
                'start_date_shamsi': str(active_project.start_date_shamsi),
                'end_date_shamsi': str(active_project.end_date_shamsi),
                'start_date_gregorian': str(active_project.start_date_gregorian),
                'end_date_gregorian': str(active_project.end_date_gregorian),
                'is_active': active_project.is_active
            }

            return Response({
                'project': project_data,
                'units_statistics': {
                    'total_units': units_stats['total_units'] or 0,
                    'total_area': float(units_stats['total_area'] or 0),
                    'total_price': float(units_stats['total_price'] or 0)
                }
            })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت آمار پروژه: {str(e)}'
            }, status=500)

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

    @action(detail=False, methods=['get'])
    def comprehensive_analysis(self, request):
        """دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی"""
        try:
            project_id = request.query_params.get('project_id')
            analysis = calculations.ComprehensiveCalculations.get_comprehensive_project_analysis(project_id)
            
            if 'error' in analysis:
                return Response(analysis, status=400)
            
            return Response(analysis)
            
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت تحلیل جامع: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def profit_metrics(self, request):
        """دریافت متریک‌های سود (کل، سالانه، ماهانه، روزانه)"""
        try:
            project_id = request.query_params.get('project_id')
            metrics = calculations.ProfitCalculations.calculate_profit_percentages(project_id)
            
            if 'error' in metrics:
                return Response(metrics, status=400)
            
            return Response(metrics)
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه متریک‌های سود: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def cost_metrics(self, request):
        """دریافت متریک‌های هزینه"""
        try:
            project_id = request.query_params.get('project_id')
            metrics = calculations.ProjectCalculations.calculate_cost_metrics(project_id)
            
            if 'error' in metrics:
                return Response(metrics, status=400)
            
            return Response(metrics)
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه متریک‌های هزینه: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def project_statistics_detailed(self, request):
        """دریافت آمار تفصیلی پروژه"""
        try:
            project_id = request.query_params.get('project_id')
            stats = calculations.ProjectCalculations.calculate_project_statistics(project_id)
            
            if 'error' in stats:
                return Response(stats, status=400)
            
            return Response(stats)
            
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی: {str(e)}'
            }, status=500)


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet for the Sale class"""

    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def total_sales(self, request):
        """دریافت مجموع فروش‌ها"""
        try:
            # دریافت پروژه فعال
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه فعالی یافت نشد'
                }, status=400)

            # محاسبه مجموع فروش‌ها برای پروژه فعال
            total_amount = models.Sale.objects.filter(
                project=active_project
            ).aggregate(total=Sum('amount'))['total'] or 0

            # تعداد فروش‌ها
            sales_count = models.Sale.objects.filter(
                project=active_project
            ).count()

            # فروش‌ها به تفکیک دوره
            sales_by_period = models.Sale.objects.filter(
                project=active_project
            ).values('period__label', 'period__id').annotate(
                period_total=Sum('amount'),
                period_count=Count('id')
            ).order_by('period__id')

            # محاسبه تجمعی فروش‌ها در هر دوره
            cumulative_sales = []
            cumulative_total = 0
            
            for period_data in sales_by_period:
                period_amount = period_data['period_total'] or 0
                cumulative_total += period_amount
                
                cumulative_sales.append({
                    'period_id': period_data['period__id'],
                    'period_label': period_data['period__label'],
                    'period_amount': period_amount,
                    'period_count': period_data['period_count'],
                    'cumulative_amount': cumulative_total
                })

            return Response({
                'project_name': active_project.name,
                'total_amount': total_amount,
                'sales_count': sales_count,
                'sales_by_period': list(sales_by_period),
                'cumulative_sales_by_period': cumulative_sales,
                'currency': 'تومان'
            })

        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه مجموع فروش‌ها: {str(e)}'
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
        
        # محاسبه مجموع سرمایه (آورده منهای برداشت)
        # total_withdrawals منفی است پس به جای تفریق باید جمع بشه
        # net_principal = float(total_deposits) - float(total_withdrawals)
        net_principal = float(total_deposits) + float(total_withdrawals)
        
        # محاسبه مجموع سرمایه + سود
        grand_total = net_principal + float(total_profits)
        
        return Response({
            'total_transactions': total_transactions,
            'total_deposits': float(total_deposits),
            'total_withdrawals': float(total_withdrawals),
            'total_profits': float(total_profits),
            'net_principal': net_principal,
            'grand_total': grand_total,
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

    @action(detail=False, methods=['get'])
    def detailed_statistics(self, request):
        """دریافت آمار تفصیلی تراکنش‌ها با فیلترهای پیشرفته"""
        try:
            project_id = request.query_params.get('project_id')
            
            # فیلترهای اضافی
            filters = {}
            if request.query_params.get('investor_id'):
                filters['investor_id'] = int(request.query_params.get('investor_id'))
            if request.query_params.get('date_from'):
                filters['date_from'] = request.query_params.get('date_from')
            if request.query_params.get('date_to'):
                filters['date_to'] = request.query_params.get('date_to')
            if request.query_params.get('transaction_type'):
                filters['transaction_type'] = request.query_params.get('transaction_type')
            
            stats = calculations.TransactionCalculations.calculate_transaction_statistics(project_id, filters)
            
            if 'error' in stats:
                return Response(stats, status=400)
            
            return Response(stats)
            
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی تراکنش‌ها: {str(e)}'
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

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """دریافت آمار کلی واحدها"""
        from django.db.models import Sum, Count
        
        # محاسبه آمار کلی
        stats = self.queryset.aggregate(
            total_units=Count('id'),
            total_area=Sum('area'),
            total_price=Sum('total_price')
        )
        
        # محاسبه آمار به تفکیک پروژه
        project_stats = []
        for project in models.Project.objects.all():
            project_units = self.queryset.filter(project=project)
            project_stat = project_units.aggregate(
                units_count=Count('id'),
                total_area=Sum('area'),
                total_price=Sum('total_price')
            )
            project_stats.append({
                'project_name': project.name,
                'project_id': project.id,
                'units_count': project_stat['units_count'] or 0,
                'total_area': float(project_stat['total_area'] or 0),
                'total_price': float(project_stat['total_price'] or 0)
            })
        
        return Response({
            'total_units': stats['total_units'] or 0,
            'total_area': float(stats['total_area'] or 0),
            'total_price': float(stats['total_price'] or 0),
            'project_breakdown': project_stats
        })
