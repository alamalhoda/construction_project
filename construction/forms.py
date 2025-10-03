from django import forms
from django_jalali.forms import jDateField
from django.core.exceptions import ValidationError
import jdatetime
from . import models


class CustomJDateField(jDateField):
    """
    فیلد تاریخ شمسی سفارشی که فرمت‌های مختلف را پشتیبانی می‌کند
    """
    
    def clean(self, value):
        """
        تمیز کردن و اعتبارسنجی مقدار تاریخ
        """
        if not value:
            if self.required:
                raise ValidationError("این فیلد الزامی است.")
            return None
            
        # اگر value یک رشته است، تلاش برای تبدیل آن
        if isinstance(value, str):
            # حذف فاصله‌های اضافی
            value = value.strip()
            
            # فرمت‌های پشتیبانی شده
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y/%m/%d', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    # تلاش برای parse کردن تاریخ شمسی
                    parsed_date = jdatetime.datetime.strptime(value, fmt).date()
                    return parsed_date
                except ValueError:
                    continue
            
            # اگر هیچ فرمتی کار نکرد، خطا برگردان
            raise ValidationError("فرمت تاریخ نامعتبر است. لطفاً از فرمت YYYY-MM-DD استفاده کنید.")
        
        # اگر value از نوع date است، آن را برگردان
        if hasattr(value, 'year'):
            return value
            
        raise ValidationError("مقدار تاریخ نامعتبر است.")


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = models.Expense
        fields = [
            "period",
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
            "participation_type",
            "units",
        ]


class PeriodForm(forms.ModelForm):
    start_date_shamsi = CustomJDateField(
        label="تاریخ شروع شمسی",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    end_date_shamsi = CustomJDateField(
        label="تاریخ پایان شمسی",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    
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
    start_date_shamsi = CustomJDateField(
        label="تاریخ شروع (شمسی)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    end_date_shamsi = CustomJDateField(
        label="تاریخ پایان (شمسی)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    is_active = forms.BooleanField(
        label="پروژه فعال",
        required=False,
        help_text="آیا این پروژه در حال حاضر فعال است؟ (فقط یک پروژه می‌تواند فعال باشد)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    total_infrastructure = forms.DecimalField(
        label="زیر بنای کل",
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0.00,
        help_text="زیر بنای کل پروژه به متر مربع",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'زیر بنای کل را وارد کنید...',
            'step': '0.01'
        })
    )
    correction_factor = forms.DecimalField(
        label="ضریب اصلاحی",
        max_digits=20,
        decimal_places=10,
        required=False,
        initial=1.0000000000,
        help_text="ضریب اصلاحی برای محاسبات پروژه",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'ضریب اصلاحی را وارد کنید...',
            'step': '0.0000000001'
        })
    )
    
    class Meta:
        model = models.Project
        fields = [
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
            "is_active",
            "total_infrastructure",
            "correction_factor",
        ]


class TransactionForm(forms.ModelForm):
    date_shamsi = CustomJDateField(
        label="تاریخ شمسی",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    
    class Meta:
        model = models.Transaction
        fields = [
            "date_shamsi",
            "date_gregorian",
            "amount",
            "transaction_type",
            "description",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # حذف فیلد project از فرم چون خودکار تنظیم می‌شود
        if 'project' in self.fields:
            del self.fields['project']
    
    def save(self, commit=True):
        """ذخیره تراکنش با تنظیم خودکار پروژه فعال"""
        transaction = super().save(commit=False)
        
        # تنظیم پروژه فعال
        active_project = models.Project.get_active_project()
        if not active_project:
            raise forms.ValidationError("هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید.")
        
        transaction.project = active_project
        
        if commit:
            transaction.save()
        
        return transaction


class UnitForm(forms.ModelForm):
    class Meta:
        model = models.Unit
        fields = [
            "name",
            "area",
            "price_per_meter",
            "total_price",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # حذف فیلد project از فرم چون خودکار تنظیم می‌شود
        if 'project' in self.fields:
            del self.fields['project']
    
    def save(self, commit=True):
        """ذخیره واحد با تنظیم خودکار پروژه فعال"""
        unit = super().save(commit=False)
        
        # تنظیم پروژه فعال
        active_project = models.Project.get_active_project()
        if not active_project:
            raise forms.ValidationError("هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید.")
        
        unit.project = active_project
        
        if commit:
            unit.save()
        
        return unit


class InterestRateForm(forms.ModelForm):
    effective_date = CustomJDateField(
        label="تاریخ اعمال (شمسی)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    is_active = forms.BooleanField(
        label="فعال",
        required=False,
        help_text="آیا این نرخ در حال حاضر فعال است؟ (فقط یک نرخ می‌تواند فعال باشد)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = models.InterestRate
        fields = [
            "rate",
            "effective_date",
            "effective_date_gregorian",
            "description",
            "is_active",
        ]


class SaleForm(forms.ModelForm):
    class Meta:
        model = models.Sale
        fields = [
            "period",
            "amount",
            "description",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تنظیم استایل‌ها برای فیلدها
        self.fields['period'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'مبلغ فروش/مرجوعی را وارد کنید...'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات فروش/مرجوعی...'
        })
    
    def save(self, commit=True):
        """ذخیره فروش با تنظیم خودکار پروژه فعال"""
        sale = super().save(commit=False)
        
        # تنظیم پروژه فعال
        active_project = models.Project.get_active_project()
        if not active_project:
            raise forms.ValidationError("هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید.")
        
        sale.project = active_project
        
        if commit:
            sale.save()
        
        return sale
