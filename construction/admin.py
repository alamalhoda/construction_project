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
        "project",
        "period",
        "expense_type",
        "amount",
        "created_at",
    ]
    list_filter = [
        "expense_type",
        "project",
        "period",
        "created_at",
    ]
    search_fields = [
        "description",
        "project__name",
        "period__label",
    ]
    readonly_fields = [
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
        "project",
        "phone",
        "email",
        "participation_type",
        "contract_date_shamsi",
        "created_at",
    ]
    list_filter = [
        "project",
        "participation_type",
        "contract_date_shamsi",
        "created_at",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "phone",
        "email",
        "description",
    ]
    filter_horizontal = [
        "units",
    ]
    readonly_fields = [
        "created_at",
    ]


class PeriodAdminForm(forms.ModelForm):

    class Meta:
        model = models.Period
        fields = "__all__"


class PeriodAdmin(admin.ModelAdmin):
    form = PeriodAdminForm
    list_display = [
        "project",
        "label",
        "year",
        "month_number",
        "month_name",
        "weight",
        "start_date_shamsi",
        "end_date_shamsi",
    ]
    list_filter = [
        "project",
        "year",
        "month_number",
        "weight",
    ]
    search_fields = [
        "label",
        "project__name",
        "month_name",
    ]
    readonly_fields = []


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
        "total_infrastructure",
        "correction_factor",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "description",
    ]
    readonly_fields = [
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
        "project",
        "investor",
        "period",
        "date_shamsi",
        "amount",
        "transaction_type",
        "day_remaining",
        "day_from_start",
        "is_system_generated",
        "created_at",
    ]
    list_filter = [
        "project",
        "investor",
        "period",
        "transaction_type",
        "is_system_generated",
        "date_shamsi",
        "created_at",
    ]
    search_fields = [
        "description",
        "investor__first_name",
        "investor__last_name",
        "project__name",
    ]
    readonly_fields = [
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
        "project",
        "name",
        "area",
        "price_per_meter",
        "total_price",
        "created_at",
    ]
    list_filter = [
        "project",
        "created_at",
    ]
    search_fields = [
        "name",
        "project__name",
    ]
    readonly_fields = [
        "created_at",
    ]
    search_fields = [
        "name",
        "project__name",
    ]
    readonly_fields = [
        "created_at",
    ]


class InterestRateAdminForm(forms.ModelForm):

    class Meta:
        model = models.InterestRate
        fields = "__all__"


class InterestRateAdmin(admin.ModelAdmin):
    form = InterestRateAdminForm
    list_display = [
        "project",
        "rate",
        "effective_date",
        "effective_date_gregorian",
        "is_active",
        "description",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "project",
        "is_active",
        "effective_date",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "description",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    ordering = ['-effective_date']


class SaleAdminForm(forms.ModelForm):

    class Meta:
        model = models.Sale
        fields = "__all__"


class SaleAdmin(admin.ModelAdmin):
    form = SaleAdminForm
    list_display = [
        "project",
        "period",
        "amount",
        "description",
        "created_at",
    ]
    list_filter = [
        "project",
        "period",
        "created_at",
    ]
    search_fields = [
        "description",
        "project__name",
        "period__label",
    ]
    readonly_fields = [
        "created_at",
    ]


class UnitSpecificExpenseAdminForm(forms.ModelForm):

    class Meta:
        model = models.UnitSpecificExpense
        fields = "__all__"


class UnitSpecificExpenseAdmin(admin.ModelAdmin):
    form = UnitSpecificExpenseAdminForm
    list_display = [
        "project",
        "unit",
        "title",
        "date_shamsi",
        "amount",
        "created_at",
    ]
    list_filter = [
        "project",
        "unit",
        "created_at",
    ]
    search_fields = [
        "title",
        "description",
        "unit__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]


class InterestRateAdminForm(forms.ModelForm):

    class Meta:
        model = models.InterestRate
        fields = "__all__"


class InterestRateAdmin(admin.ModelAdmin):
    form = InterestRateAdminForm
    list_display = [
        "project",
        "rate",
        "effective_date",
        "effective_date_gregorian",
        "is_active",
        "description",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "project",
        "is_active",
        "effective_date",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "description",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    ordering = ['-effective_date']


class SaleAdminForm(forms.ModelForm):

    class Meta:
        model = models.Sale
        fields = "__all__"


class SaleAdmin(admin.ModelAdmin):
    form = SaleAdminForm
    list_display = [
        "project",
        "period",
        "amount",
        "description",
        "created_at",
    ]
    list_filter = [
        "project",
        "period",
        "created_at",
    ]
    search_fields = [
        "description",
        "project__name",
        "period__label",
    ]
    readonly_fields = [
        "created_at",
    ]


class UnitSpecificExpenseAdminForm(forms.ModelForm):

    class Meta:
        model = models.UnitSpecificExpense
        fields = "__all__"


class UnitSpecificExpenseAdmin(admin.ModelAdmin):
    form = UnitSpecificExpenseAdminForm
    list_display = [
        "project",
        "unit",
        "title",
        "date_shamsi",
        "amount",
        "created_at",
    ]
    list_filter = [
        "project",
        "unit",
        "created_at",
    ]
    search_fields = [
        "title",
        "description",
        "unit__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]


class PettyCashTransactionAdminForm(forms.ModelForm):
    class Meta:
        model = models.PettyCashTransaction
        fields = "__all__"

class PettyCashTransactionAdmin(admin.ModelAdmin):
    form = PettyCashTransactionAdminForm
    list_display = [
        "project",
        "expense_type",
        "transaction_type",
        "amount",
        "date_shamsi",
        "receipt_number",
        "created_at",
    ]
    list_filter = [
        "expense_type",
        "transaction_type",
        "project",
        "date_gregorian",
    ]
    search_fields = [
        "description",
        "receipt_number",
        "project__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "date_gregorian",
    ]
    date_hierarchy = "date_gregorian"


admin.site.register(models.Expense, ExpenseAdmin)
admin.site.register(models.Investor, InvestorAdmin)
admin.site.register(models.InterestRate, InterestRateAdmin)
admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Sale, SaleAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.UnitSpecificExpense, UnitSpecificExpenseAdmin)
admin.site.register(models.PettyCashTransaction, PettyCashTransactionAdmin)
admin.site.register(models.UserProfile)
