from rest_framework import serializers

from . import models


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Expense
        fields = [
            "expense_type",
            "amount",
            "description",
            "created_at",
        ]

class InvestorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Investor
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "created_at",
        ]

class PeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Period
        fields = [
            "id",
            "label",
            "year",
            "month_number",
            "month_name",
            "weight",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
        ]

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = [
            "id",
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
            "created_at",
            "updated_at",
        ]

class TransactionSerializer(serializers.ModelSerializer):
    # اضافه کردن foreign key relationships برای داشبورد
    investor = InvestorSerializer(read_only=True)
    project = ProjectSerializer(read_only=True) 
    period = PeriodSerializer(read_only=True)

    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "date_shamsi",
            "date_gregorian",
            "amount",
            "transaction_type",
            "description",
            "day_remaining",
            "day_from_start",
            "created_at",
            "investor",
            "project", 
            "period",
        ]

class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Unit
        fields = [
            "id",
            "name",
            "area",
            "price_per_meter",
            "total_price",
            "created_at",
        ]
