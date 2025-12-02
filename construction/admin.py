from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
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
    autocomplete_fields = ["project", "period"]
    date_hierarchy = "created_at"
    list_per_page = 50
    ordering = ["-created_at"]


class InvestorAdminForm(forms.ModelForm):

    class Meta:
        model = models.Investor
        fields = "__all__"


class InvestorAdmin(admin.ModelAdmin):
    form = InvestorAdminForm
    list_display = [
        "full_name",
        "project",
        "phone",
        "email",
        "participation_type",
        "contract_date_shamsi",
        "units_count",
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
    autocomplete_fields = ["project"]
    list_per_page = 50
    ordering = ["-created_at"]
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "نام کامل"
    full_name.admin_order_field = "last_name"
    
    def units_count(self, obj):
        count = obj.units.count()
        return count
    units_count.short_description = "تعداد واحدها"
    units_count.admin_order_field = "units"


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
    autocomplete_fields = ["project"]
    list_per_page = 50
    ordering = ["project", "-year", "-month_number"]


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
    list_per_page = 50
    ordering = ["-created_at"]
    save_on_top = True


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
        "transaction_type_display",
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
    autocomplete_fields = ["project", "investor", "period", "interest_rate"]
    date_hierarchy = "date_gregorian"
    list_per_page = 100
    ordering = ["-date_gregorian", "-created_at"]
    list_editable = ["amount"]
    
    def transaction_type_display(self, obj):
        colors = {
            'principal_deposit': '#2185d0',
            'loan_deposit': '#5ca5e8',
            'principal_withdrawal': '#db2828',
            'profit_accrual': '#21ba45',
        }
        labels = {
            'principal_deposit': 'آورده',
            'loan_deposit': 'آورده وام',
            'principal_withdrawal': 'خروج از سرمایه',
            'profit_accrual': 'سود',
        }
        color = colors.get(obj.transaction_type, '#6c757d')
        label = labels.get(obj.transaction_type, obj.transaction_type)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )
    transaction_type_display.short_description = "نوع تراکنش"
    transaction_type_display.admin_order_field = "transaction_type"


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
        "investors_count",
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
    autocomplete_fields = ["project"]
    list_per_page = 50
    ordering = ["project", "name"]
    
    def investors_count(self, obj):
        count = obj.investor_set.count()
        return count
    investors_count.short_description = "تعداد سرمایه‌گذاران"


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
        "is_active_display",
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
        "project__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["project"]
    ordering = ['-effective_date']
    list_per_page = 50
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: #21ba45; font-weight: bold;">✓ فعال</span>'
            )
        return format_html(
            '<span style="color: #db2828; font-weight: bold;">✗ غیرفعال</span>'
        )
    is_active_display.short_description = "وضعیت"
    is_active_display.admin_order_field = "is_active"


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
    autocomplete_fields = ["project", "period"]
    date_hierarchy = "created_at"
    list_per_page = 50
    ordering = ["-created_at"]


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
    autocomplete_fields = ["project", "unit"]
    date_hierarchy = "date_gregorian"
    list_per_page = 50
    ordering = ["-date_gregorian"]


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
        "project",
        "expense_type",
        "transaction_type",
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
    autocomplete_fields = ["project"]
    date_hierarchy = "date_gregorian"
    list_per_page = 100
    ordering = ["-date_gregorian", "-created_at"]


class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = "__all__"


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
    list_display = [
        "user",
        "project",
        "role_display",
        "phone",
        "department",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "project",
        "role",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
        "department",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["project"]
    raw_id_fields = ["user"]
    list_per_page = 50
    ordering = ["-created_at"]
    
    def role_display(self, obj):
        colors = {
            'technical_admin': '#2185d0',
            'end_user': '#6c757d',
        }
        labels = {
            'technical_admin': 'مدیر فنی',
            'end_user': 'کاربر نهایی',
        }
        color = colors.get(obj.role, '#6c757d')
        label = labels.get(obj.role, obj.role)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )
    role_display.short_description = "نقش"
    role_display.admin_order_field = "role"


# ثبت مدل‌ها
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
admin.site.register(models.UserProfile, UserProfileAdmin)
