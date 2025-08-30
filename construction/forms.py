from django import forms
from . import models


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = models.Expense
        fields = [
            "expense_type",
            "amount",
            "description",
        ]


class InvestorForm(forms.ModelForm):
    class Meta:
        model = models.Investor
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
        ]


class PeriodForm(forms.ModelForm):
    class Meta:
        model = models.Period
        fields = [
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


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
        ]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = [
            "date_shamsi",
            "date_gregorian",
            "amount",
            "transaction_type",
            "description",
        ]


class UnitForm(forms.ModelForm):
    class Meta:
        model = models.Unit
        fields = [
            "name",
            "area",
            "price_per_meter",
            "total_price",
        ]
