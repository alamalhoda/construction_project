from rest_framework import viewsets, permissions

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


class PeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for the Period class"""

    queryset = models.Period.objects.all()
    serializer_class = serializers.PeriodSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for the Project class"""

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Transaction class"""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.AllowAny]  # موقتاً برای داشبورد
    filterset_fields = ['investor', 'project', 'period', 'transaction_type']


class UnitViewSet(viewsets.ModelViewSet):
    """ViewSet for the Unit class"""

    queryset = models.Unit.objects.all()
    serializer_class = serializers.UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
