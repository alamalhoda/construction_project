from django import forms
from django_jalali.forms import jDateField
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import jdatetime
from . import models
from .project_manager import ProjectManager


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
            "contract_date_shamsi",
            "description",
        ]
        # project فیلد را حذف کردیم تا خودکار از پروژه فعال استفاده شود
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # request بعداً در set_request تنظیم می‌شود
        self._request = None
    
    def set_request(self, request):
        """تنظیم request برای فیلتر کردن queryset واحدها"""
        self._request = request
        # فیلتر کردن واحدها بر اساس پروژه جاری
        if request:
            current_project = ProjectManager.get_current_project(request)
            if current_project:
                self.fields['units'].queryset = models.Unit.objects.filter(project=current_project)
            else:
                # اگر پروژه جاری وجود نداشت، queryset خالی برگردان
                self.fields['units'].queryset = models.Unit.objects.none()
    
    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند


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
    # is_active field removed - using session-based project selection instead
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
    construction_contractor_percentage = forms.DecimalField(
        label="درصد پیمان ساخت",
        max_digits=6,
        decimal_places=3,
        required=False,
        initial=0.100,
        help_text="درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'درصد پیمان ساخت را وارد کنید...',
            'step': '0.001',
            'min': '0',
            'max': '1'
        })
    )
    
    color = forms.CharField(
        label="رنگ پروژه",
        required=False,
        initial='#667eea',
        help_text="رنگ نمایش پروژه (فرمت HEX)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'color',
            'style': 'width: 100px; height: 40px; cursor: pointer;'
        })
    )
    
    icon = forms.ChoiceField(
        label="آیکون پروژه",
        required=False,
        initial='fa-building',
        help_text="انتخاب آیکون Font Awesome برای پروژه",
        choices=[
            ('fa-building', 'ساختمان'),
            ('fa-home', 'خانه'),
            ('fa-city', 'شهر'),
            ('fa-landmark', 'بنا'),
            ('fa-store', 'مغازه'),
            ('fa-warehouse', 'انبار'),
            ('fa-industry', 'صنعت'),
            ('fa-hospital', 'بیمارستان'),
            ('fa-school', 'مدرسه'),
            ('fa-hotel', 'هتل'),
            ('fa-university', 'دانشگاه'),
            ('fa-church', 'کلیسا'),
            ('fa-mosque', 'مسجد'),
            ('fa-monument', 'بنای یادبود'),
            ('fa-tower-broadcast', 'برج'),
            ('fa-bridge', 'پل'),
            ('fa-warehouse-full', 'انبار بزرگ'),
            ('fa-construction', 'ساخت و ساز'),
            ('fa-hard-hat', 'کلاه ایمنی'),
            ('fa-tools', 'ابزار'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_icon',
        })
    )
    
    class Meta:
        model = models.Project
        fields = [
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "total_infrastructure",
            "correction_factor",
            "construction_contractor_percentage",
            "description",
            "color",
            "icon",
        ]
    
    def save(self, commit=True):
        """ذخیره پروژه با تبدیل خودکار تاریخ‌های شمسی به میلادی"""
        project = super().save(commit=False)
        
        # تبدیل تاریخ شروع شمسی به میلادی
        if project.start_date_shamsi:
            project.start_date_gregorian = project.start_date_shamsi.togregorian()
        
        # تبدیل تاریخ پایان شمسی به میلادی
        if project.end_date_shamsi:
            project.end_date_gregorian = project.end_date_shamsi.togregorian()
        
        if commit:
            project.save()
        
        return project


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
    
    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند


class UnitForm(forms.ModelForm):
    area = forms.CharField(
        label="مساحت (متر مربع)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 150.50',
            'style': 'direction: ltr;',
            'oninput': 'formatNumber(this)',
            'onblur': 'validateNumber(this)'
        })
    )
    
    price_per_meter = forms.CharField(
        label="قیمت هر متر",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 5000000',
            'oninput': 'formatNumber(this)',
            'onblur': 'validateNumber(this)'
        })
    )
    
    total_price = forms.CharField(
        label="قیمت کل",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 750000000',
            'oninput': 'formatNumber(this)',
            'onblur': 'validateNumber(this)'
        })
    )
    
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
    
    def clean_area(self):
        """تمیز کردن فیلد area - حذف کاماها و اعتبارسنجی"""
        area = self.cleaned_data.get('area')
        if area:
            # حذف تمام کاراکترهای غیرعددی به جز نقطه و منفی
            cleaned_area = ''.join(c for c in str(area) if c.isdigit() or c == '.' or c == '-')
            if not cleaned_area:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            try:
                area_decimal = Decimal(cleaned_area)
            except InvalidOperation:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            # اعتبارسنجی مقدار
            if area_decimal <= 0:
                raise forms.ValidationError("مساحت باید بزرگتر از صفر باشد.")
            
            return area_decimal
        return area
    
    def clean_price_per_meter(self):
        """تمیز کردن فیلد price_per_meter - حذف کاماها و اعتبارسنجی"""
        price = self.cleaned_data.get('price_per_meter')
        if price:
            # حذف تمام کاراکترهای غیرعددی به جز نقطه
            cleaned_price = ''.join(c for c in str(price) if c.isdigit() or c == '.')
            if not cleaned_price:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            try:
                price_decimal = Decimal(cleaned_price)
            except InvalidOperation:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            # اعتبارسنجی مقدار
            if price_decimal <= 0:
                raise forms.ValidationError("قیمت هر متر باید بزرگتر از صفر باشد.")
            
            return price_decimal
        return price
    
    def clean_total_price(self):
        """تمیز کردن فیلد total_price - حذف کاماها و اعتبارسنجی"""
        total_price = self.cleaned_data.get('total_price')
        if total_price:
            # حذف تمام کاراکترهای غیرعددی به جز نقطه
            cleaned_total_price = ''.join(c for c in str(total_price) if c.isdigit() or c == '.')
            if not cleaned_total_price:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            try:
                total_price_decimal = Decimal(cleaned_total_price)
            except InvalidOperation:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            # اعتبارسنجی مقدار
            if total_price_decimal <= 0:
                raise forms.ValidationError("قیمت کل باید بزرگتر از صفر باشد.")
            
            return total_price_decimal
        return total_price

    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند


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
        # project فیلد را حذف کردیم تا خودکار از پروژه فعال استفاده شود
    
    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند


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
    
    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند

class UnitSpecificExpenseForm(forms.ModelForm):
    date_shamsi = CustomJDateField(
        label="تاریخ (شمسی)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    
    class Meta:
        model = models.UnitSpecificExpense
        fields = [
            "unit",
            "title",
            "date_shamsi",
            "amount",
            "description",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تنظیم استایل‌ها برای فیلدها
        self.fields['unit'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'عنوان هزینه را وارد کنید...'
        })
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'مبلغ را وارد کنید...',
            'oninput': 'formatNumber(this)',
            'onblur': 'validateNumber(this)'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات هزینه...'
        })
        # request بعداً در set_request تنظیم می‌شود
        self._request = None
    
    def set_request(self, request):
        """تنظیم request برای فیلتر کردن queryset"""
        self._request = request
        # فیلتر کردن واحدها بر اساس پروژه جاری
        if request:
            current_project = ProjectManager.get_current_project(request)
            if current_project:
                self.fields['unit'].queryset = models.Unit.objects.filter(project=current_project)
    
    def save(self, commit=True):
        """ذخیره هزینه اختصاصی واحد با تبدیل خودکار تاریخ شمسی به میلادی"""
        expense = super().save(commit=False)
        
        # تبدیل تاریخ شمسی به میلادی
        if expense.date_shamsi and not expense.date_gregorian:
            import jdatetime
            try:
                jdate = jdatetime.date(
                    expense.date_shamsi.year,
                    expense.date_shamsi.month,
                    expense.date_shamsi.day
                )
                expense.date_gregorian = jdate.togregorian()
            except Exception as e:
                pass
        
        # نکته: ProjectFormMixin به صورت خودکار project را تنظیم می‌کند
        
        if commit:
            expense.save()
        
        return expense


class PettyCashTransactionForm(forms.ModelForm):
    date_shamsi = CustomJDateField(
        label="تاریخ شمسی",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    
    class Meta:
        model = models.PettyCashTransaction
        fields = [
            "expense_type",
            "transaction_type",
            "amount",
            "description",
            "receipt_number",
            "date_shamsi",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # فیلتر کردن expense_type بر اساس EXPENSE_TYPES (به جز construction_contractor و other)
        self.fields['expense_type'].choices = [
            (choice[0], choice[1]) 
            for choice in models.Expense.EXPENSE_TYPES 
            if choice[0] not in ['construction_contractor', 'other']
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # حذف فیلد project از فرم چون خودکار تنظیم می‌شود
        if 'project' in self.fields:
            del self.fields['project']
    
    def clean_area(self):
        """تمیز کردن فیلد area - حذف کاماها و اعتبارسنجی"""
        area = self.cleaned_data.get('area')
        if area:
            # حذف تمام کاراکترهای غیرعددی به جز نقطه و منفی
            cleaned_area = ''.join(c for c in str(area) if c.isdigit() or c == '.' or c == '-')
            if not cleaned_area:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            try:
                area_decimal = Decimal(cleaned_area)
            except InvalidOperation:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            # اعتبارسنجی مقدار
            if area_decimal <= 0:
                raise forms.ValidationError("مساحت باید بزرگتر از صفر باشد.")
            
            return area_decimal
        return area
    
    def clean_price_per_meter(self):
        """تمیز کردن فیلد price_per_meter - حذف کاماها و اعتبارسنجی"""
        price = self.cleaned_data.get('price_per_meter')
        if price:
            # حذف تمام کاراکترهای غیرعددی به جز نقطه
            cleaned_price = ''.join(c for c in str(price) if c.isdigit() or c == '.')
            if not cleaned_price:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            try:
                price_decimal = Decimal(cleaned_price)
            except InvalidOperation:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            # اعتبارسنجی مقدار
            if price_decimal <= 0:
                raise forms.ValidationError("قیمت هر متر باید بزرگتر از صفر باشد.")
            
            return price_decimal
        return price
    
    def clean_total_price(self):
        """تمیز کردن فیلد total_price - حذف کاماها و اعتبارسنجی"""
        total_price = self.cleaned_data.get('total_price')
        if total_price:
            # حذف تمام کاراکترهای غیرعددی به جز نقطه
            cleaned_total_price = ''.join(c for c in str(total_price) if c.isdigit() or c == '.')
            if not cleaned_total_price:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            try:
                total_price_decimal = Decimal(cleaned_total_price)
            except InvalidOperation:
                raise forms.ValidationError("یک عدد وارد کنید.")
            
            # اعتبارسنجی مقدار
            if total_price_decimal <= 0:
                raise forms.ValidationError("قیمت کل باید بزرگتر از صفر باشد.")
            
            return total_price_decimal
        return total_price

    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند


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
        # project فیلد را حذف کردیم تا خودکار از پروژه فعال استفاده شود
    
    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند


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
    
    # متد save() حذف شده - ProjectFormMixin به صورت خودکار project را تنظیم می‌کند

class UnitSpecificExpenseForm(forms.ModelForm):
    date_shamsi = CustomJDateField(
        label="تاریخ (شمسی)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'انتخاب تاریخ شمسی...'
        })
    )
    
    class Meta:
        model = models.UnitSpecificExpense
        fields = [
            "unit",
            "title",
            "date_shamsi",
            "amount",
            "description",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تنظیم استایل‌ها برای فیلدها
        self.fields['unit'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'عنوان هزینه را وارد کنید...'
        })
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'مبلغ را وارد کنید...',
            'oninput': 'formatNumber(this)',
            'onblur': 'validateNumber(this)'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات هزینه...'
        })
        # request بعداً در set_request تنظیم می‌شود
        self._request = None
    
    def set_request(self, request):
        """تنظیم request برای فیلتر کردن queryset"""
        self._request = request
        # فیلتر کردن واحدها بر اساس پروژه جاری
        if request:
            current_project = ProjectManager.get_current_project(request)
            if current_project:
                self.fields['unit'].queryset = models.Unit.objects.filter(project=current_project)
    
    def save(self, commit=True):
        """ذخیره هزینه اختصاصی واحد با تبدیل خودکار تاریخ شمسی به میلادی"""
        expense = super().save(commit=False)
        
        # تبدیل تاریخ شمسی به میلادی
        if expense.date_shamsi and not expense.date_gregorian:
            import jdatetime
            try:
                jdate = jdatetime.date(
                    expense.date_shamsi.year,
                    expense.date_shamsi.month,
                    expense.date_shamsi.day
                )
                expense.date_gregorian = jdate.togregorian()
            except Exception as e:
                pass
        
        # نکته: ProjectFormMixin به صورت خودکار project را تنظیم می‌کند
        
        if commit:
            expense.save()
        
        return expense
