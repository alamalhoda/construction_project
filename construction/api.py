from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django.db import connection

from . import serializers
from . import models
from . import calculations
from .calculations import InvestorCalculations
from .api_security import APISecurityPermission, ReadOnlyPermission, AdminOnlyPermission
from .mixins import ProjectFilterMixin


class ExpenseViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the Expense class"""

    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def with_periods(self, request):
        """دریافت هزینه‌ها با اطلاعات دوره‌ها برای محاسبه دوره متوسط ساخت"""
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام هزینه‌ها برای پروژه فعال با اطلاعات دوره
            expenses = models.Expense.objects.filter(
                project=active_project
            ).select_related('period')  # لیست هزینه‌های پروژه فعال با اطلاعات دوره

            # بررسی آمار دوره‌ها
            total_expenses = expenses.count()  # تعداد کل هزینه‌ها
            expenses_with_period = expenses.exclude(period__isnull=True).count()  # تعداد هزینه‌های دارای دوره
            expenses_without_period = expenses.filter(period__isnull=True).count()  # تعداد هزینه‌های بدون دوره

            # استفاده از serializer مخصوص
            serializer = serializers.ExpenseSerializer(expenses, many=True)  # سریالایزر هزینه‌ها
            
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
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام دوره‌ها از مرداد 1402 تا مرداد 1405
            periods = models.Period.objects.filter(
                project=active_project,
                year__gte=1402,
                year__lte=1405
            ).order_by('year', 'month_number')  # لیست دوره‌ها از سال 1402 تا 1405

            # دریافت تمام هزینه‌ها برای پروژه فعال
            expenses = models.Expense.objects.filter(project=active_project)  # لیست هزینه‌های پروژه فعال

            # ساختار داده‌ها
            expense_types = [  # انواع هزینه‌ها
                ('project_manager', 'مدیر پروژه'),
                ('facilities_manager', 'سرپرست کارگاه'),
                ('procurement', 'کارپرداز'),
                ('warehouse', 'انباردار'),
                ('construction_contractor', 'پیمان ساختمان'),
                ('other', 'سایر'),
            ]

            # ایجاد ماتریس داده‌ها
            dashboard_data = []  # داده‌های داشبورد
            cumulative_total = 0  # مجموع تجمعی کل

            for period in periods:
                period_data = {
                    'period_id': period.id,  # شناسه دوره
                    'period_label': period.label,  # برچسب دوره
                    'year': period.year,  # سال دوره
                    'month_name': period.month_name,  # نام ماه دوره
                    'is_current_period': period.is_current(),  # آیا دوره جاری است
                    'expenses': {},  # هزینه‌های دوره
                    'period_total': 0,  # مجموع هزینه‌های دوره
                    'cumulative_total': 0  # مجموع تجمعی تا این دوره
                }

                # محاسبه هزینه‌های هر نوع برای این دوره
                for expense_type, expense_label in expense_types:
                    expense_amount = expenses.filter(
                        period=period,
                        expense_type=expense_type
                    ).aggregate(total=Sum('amount'))['total'] or 0  # مبلغ هزینه این نوع برای این دوره

                    # دریافت توضیحات هزینه - ابتدا رکورد دستی
                    expense_obj = expenses.filter(
                        period=period,
                        expense_type=expense_type
                    ).exclude(
                        description__icontains='محاسبه خودکار'
                    ).first()  # رکورد دستی هزینه
                    
                    # اگر رکورد دستی نباشد، رکورد خودکار را بردار
                    if not expense_obj:
                        expense_obj = expenses.filter(
                            period=period,
                            expense_type=expense_type
                        ).first()  # رکورد خودکار هزینه
                    
                    period_data['expenses'][expense_type] = {
                        'amount': float(expense_amount),  # مبلغ هزینه
                        'label': expense_label,  # برچسب هزینه
                        'description': expense_obj.description if expense_obj else '',  # توضیحات هزینه
                        'expense_id': expense_obj.id if expense_obj else None  # شناسه هزینه
                    }
                    period_data['period_total'] += float(expense_amount)

                # محاسبه مجموع تجمیعی
                cumulative_total += period_data['period_total']  # افزودن به مجموع تجمعی
                period_data['cumulative_total'] = cumulative_total  # ذخیره مجموع تجمعی

                dashboard_data.append(period_data)

            # محاسبه مجموع ستون‌ها
            column_totals = {}  # مجموع هر ستون (هر نوع هزینه)
            for expense_type, _ in expense_types:
                column_totals[expense_type] = sum(
                    period['expenses'][expense_type]['amount'] 
                    for period in dashboard_data
                )  # مجموع هزینه‌های این نوع در تمام دوره‌ها

            # مجموع کل
            grand_total = sum(period['period_total'] for period in dashboard_data)  # مجموع کل همه هزینه‌ها

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
            period_id = request.data.get('period_id')  # شناسه دوره
            expense_type = request.data.get('expense_type')  # نوع هزینه
            amount = request.data.get('amount')  # مبلغ هزینه
            description = request.data.get('description', '')  # توضیحات هزینه

            if not all([period_id, expense_type, amount is not None]):
                return Response({
                    'error': 'پارامترهای مورد نیاز ارسال نشده است'
                }, status=400)

            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت دوره
            try:
                period = models.Period.objects.get(id=period_id, project=active_project)  # دوره مورد نظر
            except models.Period.DoesNotExist:
                return Response({
                    'error': 'دوره مورد نظر یافت نشد'
                }, status=404)

            # تبدیل amount به Decimal
            from decimal import Decimal
            amount = Decimal(str(amount))  # مبلغ به صورت Decimal

            # یافتن یا ایجاد هزینه
            expense, created = models.Expense.objects.get_or_create(
                project=active_project,
                period=period,
                expense_type=expense_type,
                defaults={'amount': amount, 'description': description}
            )  # هزینه (expense) و وضعیت ایجاد (created)

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
            period_id = request.query_params.get('period_id')  # شناسه دوره از پارامترهای درخواست
            expense_type = request.query_params.get('expense_type')  # نوع هزینه از پارامترهای درخواست

            if not all([period_id, expense_type]):
                return Response({
                    'error': 'پارامترهای مورد نیاز ارسال نشده است'
                }, status=400)

            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت دوره
            try:
                period = models.Period.objects.get(id=period_id, project=active_project)  # دوره مورد نظر
            except models.Period.DoesNotExist:
                return Response({
                    'error': 'دوره مورد نظر یافت نشد'
                }, status=404)

            # یافتن هزینه - ابتدا رکورد دستی (بدون توضیحات خودکار)
            manual_expense = models.Expense.objects.filter(
                project=active_project,
                period=period,
                expense_type=expense_type
            ).exclude(
                description__icontains='محاسبه خودکار'
            ).first()  # هزینه دستی (بدون محاسبه خودکار)
            
            if manual_expense:
                expense = manual_expense  # استفاده از هزینه دستی
            else:
                # اگر رکورد دستی نباشد، رکورد خودکار را بردار
                expense = models.Expense.objects.filter(
                    project=active_project,
                    period=period,
                    expense_type=expense_type
                ).first()  # هزینه خودکار
            
            if expense:
                return Response({
                    'success': True,
                    'data': {
                        'amount': float(expense.amount),
                        'description': expense.description or '',
                        'expense_id': expense.id,
                        'is_manual': not ('محاسبه خودکار' in (expense.description or ''))
                    }
                })
            else:
                return Response({
                    'success': True,
                    'data': {
                        'amount': 0,
                        'description': '',
                        'expense_id': None,
                        'is_manual': True
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
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            if project_id:
                try:
                    project = models.Project.objects.get(id=project_id)  # پروژه با شناسه مشخص شده
                    expenses = models.Expense.objects.filter(project=project)  # هزینه‌های این پروژه
                except models.Project.DoesNotExist:
                    return Response({
                        'error': f'پروژه با شناسه {project_id} یافت نشد'
                    }, status=404)
            else:
                # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
                from construction.project_manager import ProjectManager
                active_project = ProjectManager.get_current_project(request)  # پروژه جاری
                if not active_project:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=404)
                expenses = models.Expense.objects.filter(project=active_project)  # هزینه‌های پروژه جاری
                project = active_project  # استفاده از پروژه جاری
            
            # محاسبه مجموع کل هزینه‌ها (مرجع واحد)
            total_amount = models.Expense.objects.project_totals(project)  # مجموع کل هزینه‌های پروژه
            
            # محاسبه تعداد هزینه‌ها
            total_count = expenses.count()  # تعداد کل هزینه‌ها
            
            # محاسبه مجموع هزینه‌ها بر اساس نوع
            expenses_by_type = {}  # هزینه‌ها به تفکیک نوع
            for expense_type, display_name in models.Expense.EXPENSE_TYPES:
                type_expenses = expenses.filter(expense_type=expense_type)  # هزینه‌های این نوع
                type_total = sum(expense.amount for expense in type_expenses)  # مجموع هزینه‌های این نوع
                type_count = type_expenses.count()  # تعداد هزینه‌های این نوع
                
                if type_total > 0 or type_count > 0:
                    expenses_by_type[expense_type] = {
                        'display_name': display_name,  # نام نمایشی نوع هزینه
                        'total_amount': float(type_total),  # مجموع مبلغ این نوع
                        'count': type_count  # تعداد این نوع
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


class InvestorViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the Investor class"""

    queryset = models.Investor.objects.all()
    serializer_class = serializers.InvestorSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """خلاصه مالی تمام سرمایه‌گذاران - نسخه مرجع واحد (جایگزین SQL خام)"""
        try:
            def norm_num(x):  # تابع نرمال‌سازی عدد (حذف اعشار در صورت امکان)
                try:
                    xf = float(x)  # تبدیل به float
                    xi = int(xf)  # تبدیل به int
                    return xi if xf == xi else xf  # برگرداندن int اگر اعشار نداشت، در غیر این صورت float
                except Exception:
                    return x

            # فیلتر بر اساس پروژه جاری
            from construction.project_manager import ProjectManager
            current_project = ProjectManager.get_current_project(request)
            if current_project:
                investors = models.Investor.objects.filter(project=current_project)  # لیست سرمایه‌گذاران پروژه جاری
            else:
                investors = models.Investor.objects.all()  # اگر پروژه جاری نبود، همه را برگردان
            results = []  # لیست نتایج

            for inv in investors:
                totals = models.Transaction.objects.totals(project=None, filters={'investor_id': inv.id})  # محاسبه مجموع تراکنش‌های سرمایه‌گذار
                deposits = float(totals.get('deposits', 0) or 0)  # مجموع آورده‌ها
                withdrawals = float(totals.get('withdrawals', 0) or 0)  # مجموع برداشت‌ها (منفی)
                profits = float(totals.get('profits', 0) or 0)  # مجموع سود

                total_deposits = deposits  # مجموع آورده‌ها
                total_withdrawals_abs = abs(withdrawals)  # مجموع برداشت‌ها (مقدار مثبت)
                net_principal = deposits + withdrawals  # سرمایه خالص (آورده + برداشت که منفی است)
                total_profit = profits  # مجموع سود
                grand_total = net_principal + total_profit  # مجموع کل (سرمایه خالص + سود)

                results.append({
                    'investor_id': inv.id,
                    'name': f"{inv.first_name} {inv.last_name}",
                    'participation_type': inv.participation_type,
                    'total_deposits': norm_num(total_deposits),
                    'total_withdrawals': norm_num(total_withdrawals_abs),
                    'net_principal': norm_num(net_principal),
                    'total_profit': norm_num(total_profit),
                    'grand_total': norm_num(grand_total),
                })

            results.sort(key=lambda x: x['net_principal'], reverse=True)
            return Response(results)
        except Exception as e:
            return Response({'error': f'خطا در خلاصه سرمایه‌گذاران: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def summary_ssot(self, request):
        """خلاصه مالی تمام سرمایه‌گذاران با مرجع واحد (بدون SQL خام)"""
        try:
            # فیلتر بر اساس پروژه جاری
            from construction.project_manager import ProjectManager
            current_project = ProjectManager.get_current_project(request)
            if current_project:
                investors = models.Investor.objects.filter(project=current_project)  # لیست سرمایه‌گذاران پروژه جاری
            else:
                investors = models.Investor.objects.all()  # اگر پروژه جاری نبود، همه را برگردان
            results = []  # لیست نتایج

            for inv in investors:
                totals = models.Transaction.objects.totals(project=None, filters={'investor_id': inv.id})  # محاسبه مجموع تراکنش‌های سرمایه‌گذار
                deposits = float(totals.get('deposits', 0) or 0)  # مجموع آورده‌ها
                withdrawals = float(totals.get('withdrawals', 0) or 0)  # مجموع برداشت‌ها (منفی است)
                profits = float(totals.get('profits', 0) or 0)  # مجموع سود

                total_deposits = deposits  # مجموع آورده‌ها
                total_withdrawals_abs = abs(withdrawals)  # مجموع برداشت‌ها (مقدار مثبت)
                net_principal = deposits + withdrawals  # سرمایه خالص (آورده + برداشت که منفی است)
                total_profit = profits  # مجموع سود
                grand_total = net_principal + total_profit  # مجموع کل (سرمایه خالص + سود)

                def norm_num(x):  # تابع نرمال‌سازی عدد (حذف اعشار در صورت امکان)
                    xf = float(x)  # تبدیل به float
                    xi = int(xf)  # تبدیل به int
                    return xi if xf == xi else xf  # برگرداندن int اگر اعشار نداشت، در غیر این صورت float

                results.append({
                    'investor_id': inv.id,
                    'name': f"{inv.first_name} {inv.last_name}",
                    'participation_type': inv.participation_type,
                    'total_deposits': norm_num(total_deposits),
                    'total_withdrawals': norm_num(total_withdrawals_abs),
                    'net_principal': norm_num(net_principal),
                    'total_profit': norm_num(total_profit),
                    'grand_total': norm_num(grand_total),
                })

            # مرتب‌سازی مشابه نسخه SQL: بر اساس net_principal نزولی
            results.sort(key=lambda x: x['net_principal'], reverse=True)
            return Response(results)

        except Exception as e:
            return Response({'error': f'خطا در خلاصه SSOT سرمایه‌گذاران: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def participation_stats(self, request):
        """دریافت آمار مشارکت کنندگان بر اساس نوع (مالک و سرمایه گذار)"""
        
        # فیلتر بر اساس پروژه جاری
        from construction.project_manager import ProjectManager
        current_project = ProjectManager.get_current_project(request)
        
        if current_project:
            investors_queryset = models.Investor.objects.filter(project=current_project)
        else:
            investors_queryset = models.Investor.objects.all()
        
        # شمارش کل مشارکت کنندگان
        total_count = investors_queryset.count()  # تعداد کل سرمایه‌گذاران
        
        # شمارش مشارکت کنندگان بر اساس نوع
        owner_count = investors_queryset.filter(participation_type='owner').count()  # تعداد مالکان
        investor_count = investors_queryset.filter(participation_type='investor').count()  # تعداد سرمایه‌گذاران (غیر مالک)
        
        return Response({
            'total_count': total_count,
            'owner_count': owner_count,
            'investor_count': investor_count
        })

    @action(detail=True, methods=['get'])
    def detailed_statistics(self, request, pk=None):
        """دریافت آمار تفصیلی سرمایه‌گذار"""
        try:
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            stats = calculations.InvestorCalculations.calculate_investor_statistics(pk, project_id)  # محاسبه آمار تفصیلی سرمایه‌گذار
            
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
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            ratios = calculations.InvestorCalculations.calculate_investor_ratios(pk, project_id)  # محاسبه نسبت‌های سرمایه‌گذار
            
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
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            ownership = calculations.InvestorCalculations.calculate_investor_ownership(pk, project_id)  # محاسبه مالکیت سرمایه‌گذار
            
            if 'error' in ownership:
                return Response(ownership, status=400)
            
            return Response(ownership)
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه مالکیت سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=True, methods=['get'])
    def investor_cumulative_capital_and_unit_cost_chart(self, request, pk=None):
        """
        دریافت داده‌های نمودار ترند سرمایه موجود و هزینه واحد برای سرمایه‌گذار
        
        این endpoint داده‌های لازم برای نمودار ترند را محاسبه می‌کند:
        - سرمایه موجود تجمعی به میلیون تومان
        - هزینه واحد به میلیون تومان برای هر دوره
        """
        try:
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            trend_data = calculations.InvestorCalculations.calculate_investor_trend_chart(pk, project_id)  # محاسبه داده‌های نمودار ترند سرمایه‌گذار
            
            if 'error' in trend_data:
                return Response(trend_data, status=400)
            
            return Response(trend_data)
            
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه داده‌های نمودار ترند سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def all_investors_summary(self, request):
        """
        دریافت خلاصه آمار تمام سرمایه‌گذاران
        
        این endpoint از سرویس محاسباتی InvestorCalculations استفاده می‌کند
        تا آمار کامل شامل نسبت‌های سرمایه، سود و شاخص نفع را ارائه دهد.
        """
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # تبدیل project_id به عدد در صورت وجود
            if project_id:
                project_id = int(project_id)  # تبدیل به عدد صحیح
            else:
                # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            # استفاده از تابع محاسباتی برای دریافت خلاصه سرمایه‌گذاران
            summary = InvestorCalculations.get_all_investors_summary(project_id)  # دریافت خلاصه تمام سرمایه‌گذاران
            
            if not summary:
                return Response({
                    'error': 'هیچ سرمایه‌گذاری یافت نشد یا پروژه فعالی وجود ندارد'
                }, status=404)
            
            return Response(summary)
            
        except ValueError:
            return Response({
                'error': 'شناسه پروژه نامعتبر است'
            }, status=400)
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت خلاصه سرمایه‌گذاران: {str(e)}'
            }, status=500)


class ComprehensiveAnalysisViewSet(viewsets.ViewSet):
    """ViewSet for comprehensive project analysis"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def comprehensive_analysis(self, request):
        """دریافت تحلیل جامع پروژه"""
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            # تبدیل project_id به عدد
            project_id = int(project_id)  # تبدیل به عدد صحیح
            
            # استفاده از تابع محاسباتی برای دریافت تحلیل جامع
            from .calculations import ComprehensiveCalculations
            analysis = ComprehensiveCalculations.get_comprehensive_project_analysis(project_id)  # دریافت تحلیل جامع پروژه
            
            if 'error' in analysis:
                return Response(analysis, status=400)
            
            return Response(analysis)
            
        except ValueError:
            return Response({
                'error': 'شناسه پروژه نامعتبر است'
            }, status=400)
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت تحلیل جامع: {str(e)}'
            }, status=500)


class PeriodViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the Period class"""

    queryset = models.Period.objects.all().order_by('-year', '-month_number')
    serializer_class = serializers.PeriodSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """دریافت داده‌های دوره‌ای برای نمودارها (سرمایه، هزینه، فروش، مانده صندوق)"""
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام دوره‌ها مرتب شده
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')  # لیست دوره‌های پروژه فعال

            chart_data = []  # داده‌های نمودار
            cumulative_capital = 0  # سرمایه تجمعی
            cumulative_expenses = 0  # هزینه‌های تجمعی
            cumulative_sales = 0  # فروش/مرجوعی تجمعی

            for period in periods:
                # محاسبه سرمایه دوره از مرجع واحد تراکنش‌ها
                tx_totals = models.Transaction.objects.period_totals(active_project, period)  # محاسبه مجموع تراکنش‌های دوره
                period_capital = float(tx_totals['net_capital'])  # سرمایه خالص دوره
                cumulative_capital += period_capital  # افزودن به سرمایه تجمعی

                # محاسبه هزینه‌های دوره (مرجع واحد)
                period_expenses = models.Expense.objects.period_totals(active_project, period)  # مجموع هزینه‌های دوره
                cumulative_expenses += period_expenses  # افزودن به هزینه‌های تجمعی

                # محاسبه فروش/مرجوعی دوره (مرجع واحد)
                period_sales = models.Sale.objects.period_totals(active_project, period)  # مجموع فروش/مرجوعی دوره
                cumulative_sales += period_sales  # افزودن به فروش/مرجوعی تجمعی

                # محاسبه مانده صندوق (مرجع واحد)
                from .calculations import FinancialCalculationService
                fund_balance = FinancialCalculationService.compute_fund_balance(
                    cumulative_capital, cumulative_expenses, cumulative_sales
                )  # مانده صندوق ساختمان

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
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام دوره‌ها مرتب شده
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')  # لیست دوره‌های پروژه فعال

            summary_data = []  # داده‌های خلاصه دوره‌ای
            
            # متغیرهای تجمعی
            cumulative_deposits = 0  # آورده‌های تجمعی
            cumulative_withdrawals = 0  # برداشت‌های تجمعی
            cumulative_net_capital = 0  # سرمایه خالص تجمعی
            cumulative_profits = 0  # سود تجمعی
            cumulative_expenses = 0  # هزینه‌های تجمعی
            cumulative_sales = 0  # فروش/مرجوعی تجمعی
            final_fund_balance = 0  # مانده صندوق نهایی

            # خلاصه ویژه دوره جاری
            current_summary = None  # خلاصه دوره جاری

            for period in periods:
                # محاسبات تراکنش‌های دوره از مرجع واحد
                tx_totals = models.Transaction.objects.period_totals(active_project, period)  # محاسبه مجموع تراکنش‌های دوره
                deposits = tx_totals['deposits']  # آورده‌های دوره
                withdrawals = tx_totals['withdrawals']  # برداشت‌های دوره
                profits = tx_totals['profits']  # سود دوره
                net_capital = tx_totals['net_capital']  # سرمایه خالص دوره

                cumulative_deposits += deposits  # افزودن به آورده‌های تجمعی
                cumulative_withdrawals += withdrawals  # افزودن به برداشت‌های تجمعی
                cumulative_profits += profits  # افزودن به سود تجمعی
                cumulative_net_capital += net_capital  # افزودن به سرمایه خالص تجمعی

                # هزینه‌های دوره (مرجع واحد)
                expenses = models.Expense.objects.period_totals(active_project, period)  # مجموع هزینه‌های دوره
                cumulative_expenses += expenses  # افزودن به هزینه‌های تجمعی

                # فروش/مرجوعی دوره (مرجع واحد)
                sales = models.Sale.objects.period_totals(active_project, period)  # مجموع فروش/مرجوعی دوره
                cumulative_sales += sales  # افزودن به فروش/مرجوعی تجمعی

                # محاسبه مانده صندوق (مرجع واحد)
                from .calculations import FinancialCalculationService
                fund_balance = FinancialCalculationService.compute_fund_balance(
                    cumulative_net_capital, cumulative_expenses, cumulative_sales
                )  # مانده صندوق ساختمان
                final_fund_balance = fund_balance  # ذخیره آخرین مقدار

                # اضافه کردن داده‌های دوره
                summary_data.append({
                    'period_id': period.id,
                    'period_label': period.label,
                    'year': period.year,
                    'month_number': period.month_number,
                    'month_name': period.month_name,
                    'weight': period.weight,
                    'is_current_period': period.is_current(),
                    
                    # فاکتورهای دوره
                    'deposits': deposits,
                    'withdrawals': withdrawals,
                    'net_capital': net_capital,
                    'profits': profits,
                    'expenses': expenses,
                    'sales': sales,
                    'period_fund_balance': (net_capital - expenses + sales),
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

                # اگر این دوره جاری است، خلاصه ویژه current را بساز
                if period.is_current():
                    # هزینه نهایی تجمعی تا دوره جاری (نه هزینه کل پروژه)
                    # این مقدار از تفاضل هزینه‌های تجمعی و فروش‌های تجمعی تا این دوره محاسبه می‌شود
                    current_final_cost = cumulative_expenses - cumulative_sales  # هزینه نهایی تا دوره جاری
                    
                    # آمار واحدها برای محاسبه هزینه هر متر (مرجع واحد)
                    # مساحت خالص واحدها: مجموع مساحت تمام واحدهای ثبت‌شده در سیستم
                    # شامل فقط واحدهای مسکونی/تجاری که به مالکین تعلق دارند
                    total_area_current = models.Unit.objects.project_total_area(active_project)  # مجموع مساحت واحدها تا دوره جاری
                    
                    # زیربنای کل پروژه: تمام زیربنای ساختمان از جمله واحدها، راهرو، پارکینگ، انباری، پله‌ها و...
                    # این مقدار به صورت دستی در تنظیمات پروژه تعریف می‌شود
                    total_infrastructure = float(active_project.total_infrastructure)  # مساحت کل زیربنا
                    
                    # هزینه هر متر خالص تا دوره جاری (Net Current): هزینه تجمعی تا دوره جاری تقسیم بر مساحت واحدها
                    # این شاخص نشان می‌دهد برای هر متر مربع واحد، چه هزینه‌ای تا این دوره شده است
                    # نکته: این هزینه نهایی کل پروژه نیست، بلکه هزینه تا دوره جاری است
                    # کاربرد: محاسبه سهم هزینه هر واحد بر اساس مساحت آن (تا دوره جاری)
                    cost_per_meter_net_current = (current_final_cost / total_area_current) if total_area_current > 0 else 0  # هزینه خالص هر متر مربع تا دوره جاری
                    
                    # هزینه هر متر ناخالص تا دوره جاری (Gross Current): هزینه تجمعی تا دوره جاری تقسیم بر زیربنای کل پروژه
                    # این شاخص نشان می‌دهد برای هر متر مربع از کل ساختمان (شامل فضاهای مشترک)، چه هزینه‌ای تا این دوره شده است
                    # نکته: این هزینه نهایی کل پروژه نیست، بلکه هزینه تا دوره جاری است
                    # کاربرد: ارزیابی هزینه‌های پروژه تا دوره جاری و مقایسه با پروژه‌های مشابه
                    cost_per_meter_gross_current = (current_final_cost / total_infrastructure) if total_infrastructure > 0 else 0  # هزینه ناخالص هر متر مربع تا دوره جاری

                    current_summary = {
                        'period': {
                            'id': period.id,
                            'label': period.label,
                            'year': period.year,
                            'month_number': period.month_number,
                            'month_name': period.month_name
                        },
                        'current_period_factors': {
                            'deposits': deposits,
                            'withdrawals': withdrawals,
                            'net_capital': net_capital,
                            'profits': profits,
                            'expenses': expenses,
                            'sales': sales,
                            'period_fund_balance': FinancialCalculationService.compute_period_fund_balance(net_capital, expenses, sales),
                            'fund_balance': fund_balance
                        },
                        'current_cumulative_totals': {
                            'total_deposits': cumulative_deposits,
                            'total_withdrawals': cumulative_withdrawals,
                            'total_net_capital': cumulative_net_capital,
                            'total_profits': cumulative_profits,
                            'total_expenses': cumulative_expenses,
                            'total_sales': cumulative_sales,
                            'final_fund_balance': fund_balance,
                            'final_cost': current_final_cost,
                            'cost_per_meter_net': cost_per_meter_net_current,
                            'cost_per_meter_gross': cost_per_meter_gross_current
                        }
                    }

            # محاسبه هزینه هر متر خالص و ناخالص
            # دریافت آمار واحدها
            units_stats = models.Unit.objects.filter(project=active_project).aggregate(
                total_area=Sum('area'),  # مجموع مساحت واحدها
                total_price=Sum('total_price')  # مجموع قیمت واحدها
            )
            
            total_area = float(units_stats['total_area'] or 0)  # مجموع مساحت واحدها
            total_infrastructure = float(active_project.total_infrastructure)  # مساحت کل زیربنا
            final_cost = cumulative_expenses - cumulative_sales  # هزینه نهایی (هزینه‌ها - فروش)
            
            # محاسبه هزینه هر متر
            cost_per_meter_net = final_cost / total_area if total_area > 0 else 0  # هزینه خالص هر متر مربع
            cost_per_meter_gross = final_cost / total_infrastructure if total_infrastructure > 0 else 0  # هزینه ناخالص هر متر مربع

            # محاسبه خلاصه کلی
            totals = {
                'total_deposits': cumulative_deposits,  # مجموع آورده‌ها
                'total_withdrawals': cumulative_withdrawals,  # مجموع برداشت‌ها
                'total_net_capital': cumulative_net_capital,  # مجموع سرمایه خالص
                'total_profits': cumulative_profits,  # مجموع سود
                'total_expenses': cumulative_expenses,  # مجموع هزینه‌ها
                'total_sales': cumulative_sales,  # مجموع فروش/مرجوعی
                'final_fund_balance': final_fund_balance,  # مانده صندوق نهایی
                'total_periods': periods.count(),  # تعداد دوره‌ها
                'cost_per_meter_net': cost_per_meter_net,  # هزینه خالص هر متر مربع
                'cost_per_meter_gross': cost_per_meter_gross,  # هزینه ناخالص هر متر مربع
                'final_cost': final_cost  # هزینه نهایی
            }

            return Response({
                'success': True,
                'data': summary_data,
                'totals': totals,
                'active_project': active_project.name,
                'current': current_summary
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
        """دریافت پروژه جاری (از session)"""
        from construction.project_manager import ProjectManager
        active_project = ProjectManager.get_current_project(request)  # پروژه جاری
        if active_project:
            serializer = self.get_serializer(active_project)  # سریالایزر پروژه
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'}, status=404)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """دریافت آمار کامل پروژه جاری شامل اطلاعات پروژه و آمار واحدها"""
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # آمار واحدها برای پروژه فعال (مرجع واحد)
            units_stats = models.Unit.objects.project_stats(active_project)  # آمار واحدهای پروژه فعال

            # اطلاعات پروژه
            project_data = {
                'id': active_project.id,  # شناسه پروژه
                'name': active_project.name,  # نام پروژه
                'total_infrastructure': float(active_project.total_infrastructure),  # مساحت کل زیربنا
                'correction_factor': float(active_project.correction_factor),  # ضریب اصلاحی
                'start_date_shamsi': str(active_project.start_date_shamsi),  # تاریخ شروع (شمسی)
                'end_date_shamsi': str(active_project.end_date_shamsi),  # تاریخ پایان (شمسی)
                'start_date_gregorian': str(active_project.start_date_gregorian),  # تاریخ شروع (میلادی)
                'end_date_gregorian': str(active_project.end_date_gregorian),  # تاریخ پایان (میلادی)
                'is_active': active_project.is_active  # وضعیت فعال بودن پروژه
            }

            return Response({
                'project': project_data,
                'units_statistics': units_stats
            })

        except Exception as e:
            return Response({
                'error': f'خطا در دریافت آمار پروژه: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['post'])
    def set_active(self, request):
        """تنظیم پروژه فعال"""
        project_id = request.data.get('project_id')  # شناسه پروژه از داده‌های درخواست
        if not project_id:
            return Response({'error': 'شناسه پروژه الزامی است'}, status=400)
        
        try:
            project = models.Project.set_active_project(project_id)  # تنظیم پروژه به عنوان فعال
            if project:
                serializer = self.get_serializer(project)  # سریالایزر پروژه
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
    def current(self, request):
        """دریافت پروژه جاری کاربر از session"""
        from construction.project_manager import ProjectManager
        
        current_project = ProjectManager.get_current_project(request)
        if current_project:
            serializer = self.get_serializer(current_project)
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ پروژه جاری یافت نشد'}, status=404)
    
    @action(detail=False, methods=['post'])
    def switch(self, request):
        """تغییر پروژه جاری کاربر"""
        from construction.project_manager import ProjectManager
        
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'project_id الزامی است'}, status=400)
        
        try:
            project = models.Project.objects.get(id=project_id)
            ProjectManager.set_current_project(request, project_id)
            return Response({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'color': project.color or '#667eea',
                    'icon': project.icon or 'fa-building'
                },
                'message': 'پروژه با موفقیت تغییر کرد'
            })
        except models.Project.DoesNotExist:
            return Response({'error': 'پروژه یافت نشد'}, status=404)
        except Exception as e:
            return Response({'error': f'خطا در تغییر پروژه: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def project_timeline(self, request):
        """محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ امروز"""
        from datetime import date
        
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # تاریخ امروز
            today = date.today()  # تاریخ امروز
            
            # محاسبه روزهای مانده تا پایان پروژه
            days_remaining = 0  # روزهای مانده تا پایان پروژه
            if active_project.end_date_gregorian:
                end_date = active_project.end_date_gregorian  # تاریخ پایان پروژه
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()  # تبدیل به date
                days_remaining = (end_date - today).days  # محاسبه روزهای مانده
            
            # محاسبه روزهای گذشته از ابتدای پروژه
            days_from_start = 0  # روزهای گذشته از ابتدای پروژه
            if active_project.start_date_gregorian:
                start_date = active_project.start_date_gregorian  # تاریخ شروع پروژه
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()  # تبدیل به date
                days_from_start = (today - start_date).days  # محاسبه روزهای گذشته
            
            # محاسبه مدت کل پروژه
            total_project_days = 0  # مدت کل پروژه (روز)
            if (active_project.start_date_gregorian and 
                active_project.end_date_gregorian):
                start_date = active_project.start_date_gregorian  # تاریخ شروع پروژه
                end_date = active_project.end_date_gregorian  # تاریخ پایان پروژه
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()  # تبدیل به date
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()  # تبدیل به date
                total_project_days = (end_date - start_date).days  # محاسبه مدت کل پروژه

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
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            analysis = calculations.ComprehensiveCalculations.get_comprehensive_project_analysis(project_id)  # دریافت تحلیل جامع پروژه
            
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
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            metrics = calculations.ProfitCalculations.calculate_profit_percentages(project_id)  # محاسبه متریک‌های سود
            
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
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            metrics = calculations.ProjectCalculations.calculate_cost_metrics(project_id)  # محاسبه متریک‌های هزینه
            
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
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            stats = calculations.ProjectCalculations.calculate_project_statistics(project_id)  # محاسبه آمار تفصیلی پروژه
            
            if 'error' in stats:
                return Response(stats, status=400)
            
            return Response(stats)
            
        except Exception as e:
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی: {str(e)}'
            }, status=500)

    # ========================================
    # Excel Export Endpoints - موقتاً غیرفعال
    # برای فعال‌سازی، کامنت را بردارید
    # ========================================
    
    # @action(detail=False, methods=['get'], url_path='export_excel_static')
    # def export_excel_static(self, request):
    #     """
    #     Export کامل اطلاعات پروژه به فرمت Excel
    #     
    #     این endpoint فایل Excel شامل موارد زیر را تولید می‌کند:
    #     - 9 شیت داده پایه (Project, Units, Investors, Periods, InterestRates, Transactions, Expenses, Sales, UserProfiles)
    #     - 6 شیت محاسباتی (Dashboard, Profit_Metrics, Cost_Metrics, Investor_Analysis, Period_Summary, Transaction_Summary)
    #     
    #     نوع محاسبات: Static (تمام محاسبات در سرور انجام می‌شود)
    #     
    #     Returns:
    #         فایل Excel با 15 شیت
    #     """
    #     from .excel_export import ExcelExportService
    #     from django.http import HttpResponse
    #     
    #     try:
    #         # دریافت پروژه فعال
    #         project = models.Project.get_active_project()
    #         if not project:
    #             return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
    #         
    #         # تولید فایل Excel
    #         excel_service = ExcelExportService(project)
    #         workbook = excel_service.generate_excel()
    #         
    #         # نام فایل با تاریخ و زمان
    #         from django.utils import timezone
    #         import re
    #         # پاک کردن کاراکترهای غیرمجاز از نام پروژه
    #         safe_project_name = re.sub(r'[^\w\-_\.]', '_', project.name)
    #         timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    #         filename = f'project_{safe_project_name}_{timestamp}.xlsx'
    #         
    #         # آماده‌سازی response
    #         response = HttpResponse(
    #             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         )
    #         
    #         # تنظیم header برای اطمینان از نام فایل صحیح
    #         response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
    #         
    #         # ذخیره workbook در response
    #         workbook.save(response)
    #         
    #         return response
    #         
    #     except ValueError as e:
    #         return Response({
    #             'error': str(e)
    #         }, status=400)
    #     except Exception as e:
    #         return Response({
    #             'error': f'خطا در تولید فایل Excel: {str(e)}'
    #         }, status=500)
    
    # @action(detail=False, methods=['get'], url_path='export_excel_dynamic')
    # def export_excel_dynamic(self, request):
    #     """
    #     Export کامل اطلاعات پروژه به فرمت Excel با فرمول‌های محاسباتی
    #     
    #     این endpoint فایل Excel شامل موارد زیر را تولید می‌کند:
    #     - شیت راهنمای فرمول‌ها
    #     - 9 شیت داده پایه (بدون فرمول)
    #     - 6 شیت محاسباتی (با فرمول‌های Excel)
    #     - Named Ranges برای خوانایی بهتر
    #     
    #     نوع محاسبات: Dynamic (فرمول‌های Excel)
    #     
    #     Returns:
    #         فایل Excel با فرمول‌های محاسباتی
    #     """
    #     from .excel_export_dynamic import ExcelDynamicExportService
    #     from django.http import HttpResponse
    #     
    #     try:
    #         # دریافت پروژه فعال
    #         project = models.Project.get_active_project()
    #         if not project:
    #             return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
    #         
    #         # تولید فایل Excel با فرمول
    #         excel_service = ExcelDynamicExportService(project)
    #         workbook = excel_service.generate_excel()
    #         
    #         # نام فایل با تاریخ و زمان
    #         from django.utils import timezone
    #         import re
    #         # پاک کردن کاراکترهای غیرمجاز از نام پروژه
    #         safe_project_name = re.sub(r'[^\w\-_\.]', '_', project.name)
    #         timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    #         filename = f'project_dynamic_{safe_project_name}_{timestamp}.xlsx'
    #         
    #         # آماده‌سازی response
    #         response = HttpResponse(
    #             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         )
    #         
    #         # تنظیم header برای اطمینان از نام فایل صحیح
    #         response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
    #         
    #         # ذخیره workbook در response
    #         workbook.save(response)
    #         
    #         return response
    #         
    #     except ValueError as e:
    #         return Response({
    #             'error': str(e)
    #         }, status=400)
    #     except Exception as e:
    #         return Response({
    #             'error': f'خطا در تولید فایل Excel Dynamic: {str(e)}'
    #         }, status=500)


class SaleViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the Sale class"""

    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def total_sales(self, request):
        """دریافت مجموع فروش‌ها"""
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # محاسبه مجموع فروش‌ها برای پروژه فعال (مرجع واحد)
            total_amount = models.Sale.objects.project_totals(active_project)  # مجموع کل فروش/مرجوعی پروژه

            # تعداد فروش‌ها
            sales_count = models.Sale.objects.filter(
                project=active_project
            ).count()  # تعداد فروش/مرجوعی‌های پروژه

            # فروش‌ها به تفکیک دوره (بدون تغییر)
            sales_by_period = models.Sale.objects.filter(
                project=active_project
            ).values('period__label', 'period__id').annotate(
                period_total=Sum('amount'),  # مجموع فروش/مرجوعی هر دوره
                period_count=Count('id')  # تعداد فروش/مرجوعی هر دوره
            ).order_by('period__id')  # لیست فروش/مرجوعی‌ها به تفکیک دوره

            # محاسبه تجمعی فروش‌ها در هر دوره
            cumulative_sales = []  # لیست فروش/مرجوعی تجمعی
            cumulative_total = 0  # مجموع تجمعی کل
            
            for period_data in sales_by_period:
                period_amount = period_data['period_total'] or 0  # مبلغ فروش/مرجوعی این دوره
                cumulative_total += period_amount  # افزودن به مجموع تجمعی
                
                cumulative_sales.append({
                    'period_id': period_data['period__id'],  # شناسه دوره
                    'period_label': period_data['period__label'],  # برچسب دوره
                    'period_amount': period_amount,  # مبلغ فروش/مرجوعی دوره
                    'period_count': period_data['period_count'],  # تعداد فروش/مرجوعی دوره
                    'cumulative_amount': cumulative_total  # مبلغ تجمعی تا این دوره
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


class TransactionViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the Transaction class"""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    permission_classes = [APISecurityPermission]
    filterset_fields = ['investor', 'project', 'period', 'transaction_type']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """آمار کلی تراکنش‌ها برای پروژه جاری"""
        from django.db.models import Count, Sum, Q
        
        # دریافت پروژه جاری از session
        from construction.project_manager import ProjectManager
        current_project = ProjectManager.get_current_project(request)  # پروژه جاری
        
        if not current_project:
            return Response({
                'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
            }, status=400)
        
        # محاسبه آمار کلی برای پروژه جاری
        total_transactions = models.Transaction.objects.filter(project=current_project).count()  # تعداد کل تراکنش‌های پروژه جاری
        tx_totals_all = models.Transaction.objects.project_totals(project=current_project)  # محاسبه مجموع تراکنش‌های پروژه جاری
        total_deposits = tx_totals_all['deposits']  # مجموع آورده‌ها
        total_withdrawals = tx_totals_all['withdrawals']  # مجموع برداشت‌ها (منفی)
        total_profits = tx_totals_all['profits']  # مجموع سود
        
        unique_investors = models.Transaction.objects.filter(project=current_project).values('investor').distinct().count()  # تعداد سرمایه‌گذاران منحصر به فرد پروژه جاری
        
        # محاسبه مجموع سرمایه (آورده منهای برداشت)
        # total_withdrawals منفی است پس به جای تفریق باید جمع بشه
        # net_principal = float(total_deposits) - float(total_withdrawals)
        net_principal = float(total_deposits) + float(total_withdrawals)  # سرمایه خالص (آورده + برداشت که منفی است)
        
        # محاسبه مجموع سرمایه + سود
        grand_total = net_principal + float(total_profits)  # مجموع کل (سرمایه خالص + سود)
        
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
            current_rate = models.InterestRate.get_current_rate()  # نرخ سود فعال فعلی
            if not current_rate:
                return Response({
                    'error': 'هیچ نرخ سود فعالی یافت نشد. لطفاً ابتدا نرخ سود را تنظیم کنید.'
                }, status=400)
            
            # اجرای عملیات محاسبه مجدد
            result = models.Transaction.recalculate_all_profits_with_new_rate(current_rate)  # محاسبه مجدد سودها با نرخ فعلی
            
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
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # فیلترهای اضافی
            filters = {}  # دیکشنری فیلترها
            if request.query_params.get('investor_id'):
                filters['investor_id'] = int(request.query_params.get('investor_id'))  # فیلتر شناسه سرمایه‌گذار
            if request.query_params.get('date_from'):
                filters['date_from'] = request.query_params.get('date_from')  # فیلتر تاریخ از
            if request.query_params.get('date_to'):
                filters['date_to'] = request.query_params.get('date_to')  # فیلتر تاریخ تا
            if request.query_params.get('transaction_type'):
                filters['transaction_type'] = request.query_params.get('transaction_type')  # فیلتر نوع تراکنش
            
            stats = calculations.TransactionCalculations.calculate_transaction_statistics(project_id, filters)  # محاسبه آمار تفصیلی تراکنش‌ها
            
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
            project_id = request.data.get('project_id')  # شناسه پروژه از داده‌های درخواست
            
            if project_id:
                try:
                    project = models.Project.objects.get(id=project_id)  # دریافت پروژه
                    updated_count = models.Expense.recalculate_all_construction_contractor_expenses(project)  # محاسبه مجدد هزینه‌های پیمان ساختمان برای پروژه
                    return Response({
                        'success': True,
                        'message': f'محاسبه مجدد برای پروژه "{project.name}" با موفقیت انجام شد',
                        'updated_periods': updated_count  # تعداد دوره‌های به‌روزرسانی شده
                    })
                except models.Project.DoesNotExist:
                    return Response({
                        'error': f'پروژه با شناسه {project_id} یافت نشد'
                    }, status=404)
            else:
                updated_count = models.Expense.recalculate_all_construction_contractor_expenses()  # محاسبه مجدد هزینه‌های پیمان ساختمان برای همه پروژه‌ها
                return Response({
                    'success': True,
                    'message': 'محاسبه مجدد برای همه پروژه‌ها با موفقیت انجام شد',
                    'updated_periods': updated_count  # تعداد دوره‌های به‌روزرسانی شده
                })
                
        except Exception as e:
            return Response({
                'error': f'خطا در محاسبه مجدد هزینه‌های پیمان ساختمان: {str(e)}'
            }, status=500)
    


class InterestRateViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the InterestRate class"""

    queryset = models.InterestRate.objects.all()
    serializer_class = serializers.InterestRateSerializer
    permission_classes = [APISecurityPermission]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """دریافت نرخ سود فعال فعلی"""
        current_rate = models.InterestRate.get_current_rate()  # نرخ سود فعال فعلی
        if current_rate:
            serializer = self.get_serializer(current_rate)  # سریالایزر نرخ سود
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ نرخ سود فعالی یافت نشد'}, status=404)


class UnitViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
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
            total_units=Count('id'),  # تعداد کل واحدها
            total_area=Sum('area'),  # مجموع مساحت واحدها
            total_price=Sum('total_price')  # مجموع قیمت واحدها
        )  # آمار کلی واحدها
        
        # محاسبه آمار به تفکیک پروژه
        project_stats = []  # لیست آمار به تفکیک پروژه
        for project in models.Project.objects.all():
            project_units = self.queryset.filter(project=project)  # واحدهای این پروژه
            project_stat = project_units.aggregate(
                units_count=Count('id'),  # تعداد واحدهای این پروژه
                total_area=Sum('area'),  # مجموع مساحت واحدهای این پروژه
                total_price=Sum('total_price')  # مجموع قیمت واحدهای این پروژه
            )  # آمار واحدهای این پروژه
            project_stats.append({
                'project_name': project.name,  # نام پروژه
                'project_id': project.id,  # شناسه پروژه
                'units_count': project_stat['units_count'] or 0,  # تعداد واحدها
                'total_area': float(project_stat['total_area'] or 0),  # مجموع مساحت
                'total_price': float(project_stat['total_price'] or 0)  # مجموع قیمت
            })
        
        return Response({
            'total_units': stats['total_units'] or 0,
            'total_area': float(stats['total_area'] or 0),
            'total_price': float(stats['total_price'] or 0),
            'project_breakdown': project_stats
        })

class UnitSpecificExpenseViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """ViewSet for the UnitSpecificExpense class"""

    queryset = models.UnitSpecificExpense.objects.all()
    serializer_class = serializers.UnitSpecificExpenseSerializer
    permission_classes = [APISecurityPermission]
    filterset_fields = ['unit', 'project']
