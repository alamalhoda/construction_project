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
        "phone",
        "email",
        "participation_type",
        "created_at",
    ]
    list_filter = [
        "participation_type",
        "created_at",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "phone",
        "email",
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
        "is_active",
        "start_date_shamsi",
        "end_date_shamsi",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_active",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    actions = ['set_as_active_project']
    
    def set_as_active_project(self, request, queryset):
        """تنظیم پروژه انتخاب شده به عنوان پروژه فعال"""
        if queryset.count() != 1:
            self.message_user(request, "لطفاً فقط یک پروژه را انتخاب کنید.", level='ERROR')
            return
        
        project = queryset.first()
        project.is_active = True
        project.save()
        
        self.message_user(request, f"پروژه '{project.name}' به عنوان پروژه فعال تنظیم شد.")
    
    set_as_active_project.short_description = "تنظیم به عنوان پروژه فعال"


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


class InterestRateAdminForm(forms.ModelForm):

    class Meta:
        model = models.InterestRate
        fields = "__all__"


class InterestRateAdmin(admin.ModelAdmin):
    form = InterestRateAdminForm
    list_display = [
        "rate",
        "effective_date",
        "effective_date_gregorian",
        "is_active",
        "description",
        "created_at",
        "updated_at",
    ]
    list_filter = [
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


admin.site.register(models.Expense, ExpenseAdmin)
admin.site.register(models.Investor, InvestorAdmin)
admin.site.register(models.InterestRate, InterestRateAdmin)
admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.UserProfile)
