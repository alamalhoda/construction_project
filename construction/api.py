from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.db import connection

from . import serializers
from . import models


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for the Expense class"""

    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]


class InvestorViewSet(viewsets.ModelViewSet):
    """ViewSet for the Investor class"""

    queryset = models.Investor.objects.all()
    serializer_class = serializers.InvestorSerializer
    permission_classes = [permissions.AllowAny]  # موقتاً برای داشبورد

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
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]  # موقتاً برای داشبورد



class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for the Project class"""

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]  # موقتاً برای داشبورد


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Transaction class"""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.AllowAny]  # موقتاً برای داشبورد
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


class InterestRateViewSet(viewsets.ModelViewSet):
    """ViewSet for the InterestRate class"""

    queryset = models.InterestRate.objects.all()
    serializer_class = serializers.InterestRateSerializer
    permission_classes = [permissions.AllowAny]  # موقتاً برای داشبورد

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
    permission_classes = [permissions.IsAuthenticated]
