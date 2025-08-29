from django.contrib import admin
from django import forms

from . import models


class ExpenseAdminForm(forms.ModelForm):

    class Meta:
        model = models.Expense
        fields = "__all__"


class ExpenseAdmin(admin.ModelAdmin):
    form = ExpenseAdminForm
    list_display = [
        "expense_type",
        "amount",
        "description",
        "created_at",
    ]
    readonly_fields = [
        "expense_type",
        "amount",
        "description",
        "created_at",
    ]


class InvestorAdminForm(forms.ModelForm):

    class Meta:
        model = models.Investor
        fields = "__all__"


class InvestorAdmin(admin.ModelAdmin):
    form = InvestorAdminForm
    list_display = [
        "first_name",
        "last_name",
        "phone",
        "email",
        "created_at",
    ]
    readonly_fields = [
        "first_name",
        "last_name",
        "phone",
        "email",
        "created_at",
    ]


class PeriodAdminForm(forms.ModelForm):

    class Meta:
        model = models.Period
        fields = "__all__"


class PeriodAdmin(admin.ModelAdmin):
    form = PeriodAdminForm
    list_display = [
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
    readonly_fields = [
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


class ProjectAdminForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = "__all__"


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = [
        "name",
        "start_date_shamsi",
        "end_date_shamsi",
        "start_date_gregorian",
        "end_date_gregorian",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "name",
        "start_date_shamsi",
        "end_date_shamsi",
        "start_date_gregorian",
        "end_date_gregorian",
        "created_at",
        "updated_at",
    ]


class TransactionAdminForm(forms.ModelForm):

    class Meta:
        model = models.Transaction
        fields = "__all__"


class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    list_display = [
        "date_shamsi",
        "date_gregorian",
        "amount",
        "transaction_type",
        "description",
        "day_remaining",
        "day_from_start",
        "created_at",
    ]
    readonly_fields = [
        "date_shamsi",
        "date_gregorian",
        "amount",
        "transaction_type",
        "description",
        "day_remaining",
        "day_from_start",
        "created_at",
    ]


class UnitAdminForm(forms.ModelForm):

    class Meta:
        model = models.Unit
        fields = "__all__"


class UnitAdmin(admin.ModelAdmin):
    form = UnitAdminForm
    list_display = [
        "name",
        "area",
        "price_per_meter",
        "total_price",
        "created_at",
    ]
    readonly_fields = [
        "name",
        "area",
        "price_per_meter",
        "total_price",
        "created_at",
    ]


admin.site.register(models.Expense, ExpenseAdmin)
admin.site.register(models.Investor, InvestorAdmin)
admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.Unit, UnitAdmin)
