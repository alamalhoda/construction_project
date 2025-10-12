from django.db import models
from django.urls import reverse
from django_jalali.db import models as jmodels
from decimal import Decimal
from django.contrib.auth.models import User

class Project(models.Model):
    """
    مدل پروژه ساختمانی
    شامل اطلاعات کلی پروژه مانند نام، تاریخ شروع و پایان (شمسی و میلادی)
    """
    name = models.CharField(max_length=200, verbose_name="نام پروژه")
    start_date_shamsi = jmodels.jDateField(verbose_name="تاریخ شروع (شمسی)")
    end_date_shamsi = jmodels.jDateField(verbose_name="تاریخ پایان (شمسی)")
    start_date_gregorian = models.DateField(verbose_name="تاریخ شروع (میلادی)")
    end_date_gregorian = models.DateField(verbose_name="تاریخ پایان (میلادی)")
    is_active = models.BooleanField(
        default=False, 
        verbose_name="پروژه فعال",
        help_text="آیا این پروژه در حال حاضر فعال است؟ (فقط یک پروژه می‌تواند فعال باشد)"
    )
    total_infrastructure = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="زیر بنای کل",
        help_text="زیر بنای کل پروژه به متر مربع"
    )
    correction_factor = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        default=1.0000000000,
        verbose_name="ضریب اصلاحی",
        help_text="ضریب اصلاحی برای محاسبات پروژه"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('construction_Project_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_Project_update', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # اگر این پروژه فعال شود، همه پروژه‌های دیگر را غیرفعال کن
        if self.is_active:
            Project.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_project(cls):
        """دریافت پروژه فعال (فقط یک پروژه می‌تواند فعال باشد)"""
        try:
            return cls.objects.filter(is_active=True).first()
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_active_project(cls, project_id):
        """تنظیم پروژه فعال (همه پروژه‌های دیگر غیرفعال می‌شوند)"""
        # غیرفعال کردن همه پروژه‌ها
        cls.objects.filter(is_active=True).update(is_active=False)
        
        # فعال کردن پروژه انتخاب شده
        try:
            project = cls.objects.get(pk=project_id)
            project.is_active = True
            project.save()
            return project
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_default_project(cls):
        """دریافت پروژه پیش‌فرض (پروژه فعال یا اولین پروژه)"""
        # ابتدا پروژه فعال را جستجو کن
        active_project = cls.objects.filter(is_active=True).first()
        if active_project:
            return active_project.id
        
        # اگر پروژه فعالی نبود، اولین پروژه را برگردان
        first_project = cls.objects.first()
        if first_project:
            return first_project.id
        
        # اگر هیچ پروژه‌ای نبود، None برگردان (برای migration)
        return None
    


class Unit(models.Model):
    """
    مدل واحد مسکونی
    هر پروژه شامل چندین واحد است که هر واحد دارای متراژ، قیمت و مالکین است
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    name = models.CharField(max_length=200, verbose_name="نام واحد")
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="متراژ")
    price_per_meter = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="قیمت هر متر")
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="قیمت نهایی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "واحد"
        verbose_name_plural = "واحدها"

    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('construction_Unit_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_Unit_update', kwargs={'pk': self.pk})
    


class Investor(models.Model):
    """
    مدل سرمایه‌گذار
    افرادی که در پروژه سرمایه‌گذاری می‌کنند و می‌توانند مالک چندین واحد باشند
    """
    PARTICIPATION_TYPE_CHOICES = [
        ('owner', 'مالک'),
        ('investor', 'سرمایه‌گذار'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        verbose_name="پروژه",
        help_text="پروژه‌ای که این سرمایه‌گذار در آن مشارکت دارد"
    )
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    email = models.EmailField(blank=True, null=True, verbose_name="ایمیل")
    participation_type = models.CharField(
        max_length=20, 
        choices=PARTICIPATION_TYPE_CHOICES, 
        default='owner',
        verbose_name="نوع مشارکت"
    )
    units = models.ManyToManyField(Unit, blank=True, verbose_name="واحدها")
    contract_date_shamsi = jmodels.jDateField(null=True, blank=True, verbose_name="تاریخ قرارداد (شمسی)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "سرمایه‌گذار"
        verbose_name_plural = "سرمایه‌گذاران"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('construction_Investor_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_Investor_update', kwargs={'pk': self.pk})
    


class Period(models.Model):
    """
    مدل دوره زمانی
    دوره‌های ماهانه پروژه با وزن‌دهی برای محاسبات مالی
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    label = models.CharField(max_length=50, verbose_name="عنوان دوره")
    year = models.IntegerField(verbose_name="سال شمسی")
    month_number = models.IntegerField(verbose_name="شماره ماه")
    month_name = models.CharField(max_length=20, verbose_name="نام ماه")
    weight = models.IntegerField(verbose_name="وزن دوره")
    start_date_shamsi = jmodels.jDateField(verbose_name="تاریخ شروع شمسی")
    end_date_shamsi = jmodels.jDateField(verbose_name="تاریخ پایان شمسی")
    start_date_gregorian = models.DateField(verbose_name="تاریخ شروع میلادی")
    end_date_gregorian = models.DateField(verbose_name="تاریخ پایان میلادی")

    class Meta:
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"
        unique_together = ['project', 'year', 'month_number']

    def __str__(self):
        return f"{self.label} - {self.project.name}"
    
    def get_absolute_url(self):
        return reverse('construction_Period_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_Period_update', kwargs={'pk': self.pk})
    


class InterestRate(models.Model):
    """
    مدل نرخ سود روزانه
    شامل نرخ سود و تاریخ اعمال آن
    """
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        verbose_name="پروژه",
        help_text="پروژه‌ای که این نرخ سود برای آن اعمال می‌شود"
    )
    rate = models.DecimalField(
        max_digits=20, 
        decimal_places=15, 
        verbose_name="نرخ سود روزانه",
        help_text="مثال: 0.000481925679775"
    )
    effective_date = jmodels.jDateField(
        verbose_name="تاریخ اعمال (شمسی)",
        help_text="تاریخی که این نرخ از آن اعمال می‌شود"
    )
    effective_date_gregorian = models.DateField(
        verbose_name="تاریخ اعمال (میلادی)",
        null=True, blank=True
    )
    description = models.TextField(
        blank=True, 
        verbose_name="توضیحات",
        help_text="دلیل تغییر نرخ سود"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="فعال",
        help_text="آیا این نرخ در حال حاضر فعال است؟"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "نرخ سود"
        verbose_name_plural = "نرخ‌های سود"
        ordering = ['-effective_date']

    def __str__(self):
        return f"نرخ {self.rate}% از {self.effective_date}"

    def save(self, *args, **kwargs):
        # تبدیل تاریخ شمسی به میلادی
        if self.effective_date and not self.effective_date_gregorian:
            from jdatetime import datetime as jdatetime
            if isinstance(self.effective_date, str):
                jdate = jdatetime.strptime(self.effective_date, '%Y-%m-%d')
            else:
                jdate = self.effective_date
            self.effective_date_gregorian = jdate.togregorian().date()
        
        # غیرفعال کردن نرخ‌های قبلی (به جز خود این instance) در همان پروژه
        if self.is_active:
            InterestRate.objects.filter(
                is_active=True,
                project=self.project
            ).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)

    @classmethod
    def get_current_rate(cls, project=None):
        """دریافت نرخ سود فعلی برای پروژه"""
        if not project:
            project = Project.get_active_project()
        
        try:
            return cls.objects.filter(is_active=True, project=project).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_rate_for_date(cls, date, project=None):
        """دریافت نرخ سود برای تاریخ و پروژه مشخص"""
        if not project:
            project = Project.get_active_project()
        
        try:
            return cls.objects.filter(
                effective_date__lte=date,
                is_active=True,
                project=project
            ).order_by('-effective_date').first()
        except cls.DoesNotExist:
            return None

    def get_absolute_url(self):
        """URL برای نمایش جزئیات نرخ سود"""
        from django.urls import reverse
        return reverse('construction_InterestRate_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        """URL برای ویرایش نرخ سود"""
        from django.urls import reverse
        return reverse('construction_InterestRate_update', kwargs={'pk': self.pk})

class Transaction(models.Model):
    """
    مدل تراکنش مالی
    شامل آورده، خروج از سرمایه و سود با محاسبه خودکار روز مانده و روز از شروع
    """
    TRANSACTION_TYPES = [
        ('principal_deposit', 'آورده'),
        ('principal_withdrawal', 'خروج از سرمایه'),
        ('profit_accrual', 'سود'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, verbose_name="سرمایه‌گذار")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name="دوره")
    date_shamsi = jmodels.jDateField(verbose_name="تاریخ شمسی")
    date_gregorian = models.DateField(verbose_name="تاریخ میلادی")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="مبلغ")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    day_remaining = models.IntegerField(verbose_name="روز مانده تا پایان پروژه", default=0)
    day_from_start = models.IntegerField(verbose_name="روز از ابتدای پروژه", default=0)
    interest_rate = models.ForeignKey(
        InterestRate, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        verbose_name="نرخ سود اعمال شده",
        help_text="نرخ سودی که برای محاسبه این تراکنش استفاده شده"
    )
    is_system_generated = models.BooleanField(
        default=False,
        verbose_name="تولید شده توسط سیستم",
        help_text="آیا این تراکنش توسط سیستم محاسبه شده است؟"
    )
    parent_transaction = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="تراکنش اصلی",
        help_text="برای تراکنش‌های سود: تراکنش آورده یا خروج از سرمایه مربوطه"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"

    def save(self, *args, **kwargs):
        # تبدیل تاریخ شمسی به میلادی اگر لازم باشد
        if self.date_shamsi and not self.date_gregorian:
            from jdatetime import datetime as jdatetime
            from datetime import date
            # اگر date_shamsi string است (از frontend آمده)
            if isinstance(self.date_shamsi, str):
                jdate = jdatetime.strptime(str(self.date_shamsi), '%Y-%m-%d')
                gregorian_datetime = jdate.togregorian()
                # تبدیل datetime به date
                self.date_gregorian = gregorian_datetime.date()
                # date_shamsi باید تاریخ شمسی باشد (برای jmodels.jDateField)
                self.date_shamsi = jdate.date()
            # اگر date_shamsi از قبل date object است (از serializer آمده)
            elif hasattr(self.date_shamsi, 'year'):
                self.date_gregorian = self.date_shamsi
        
        # محاسبه روز مانده تا پایان پروژه
        if hasattr(self, 'project') and self.project and self.project.end_date_gregorian and self.date_gregorian:
            # اطمینان از اینکه هر دو تاریخ از نوع date هستند
            end_date = self.project.end_date_gregorian
            if isinstance(end_date, str):
                from datetime import datetime
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            self.day_remaining = (end_date - self.date_gregorian).days
        
        # محاسبه روز از ابتدای پروژه
        if hasattr(self, 'project') and self.project and self.project.start_date_gregorian and self.date_gregorian:
            # اطمینان از اینکه هر دو تاریخ از نوع date هستند
            start_date = self.project.start_date_gregorian
            if isinstance(start_date, str):
                from datetime import datetime
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            self.day_from_start = (self.date_gregorian - start_date).days
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.investor} - {self.amount} - {self.get_transaction_type_display()} - {self.period} - {self.date_shamsi} - {self.date_gregorian} - {self.day_remaining} - {self.day_from_start}"
    
    def get_absolute_url(self):
        return reverse('construction_Transaction_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_Transaction_update', kwargs={'pk': self.pk})
    


    def calculate_profit(self, interest_rate=None):
        """
        محاسبه سود بر اساس فرمول:
        سود = مبلغ تراکنش × روز مانده تا پایان پروژه × نرخ سود روزانه
        
        برای آورده: سود مثبت
        برای خروج از سرمایه: سود منفی
        """
        if self.transaction_type not in ['principal_deposit', 'principal_withdrawal']:
            return Decimal('0')
        
        if not interest_rate:
            interest_rate = InterestRate.get_current_rate()
        
        if not interest_rate:
            return Decimal('0')
        
        if self.day_remaining <= 0:
            return Decimal('0')
        
        # محاسبه سود (مبلغ می‌تواند مثبت یا منفی باشد)
        profit = self.amount * self.day_remaining * interest_rate.rate
        
        return profit.quantize(Decimal('0.01'))  # گرد کردن به 2 رقم اعشار

    @classmethod
    def calculate_all_profits(cls, interest_rate=None):
        """
        محاسبه سود برای همه آورده‌ها
        """
        if not interest_rate:
            interest_rate = InterestRate.get_current_rate()
        
        if not interest_rate:
            return []
        
        # دریافت همه تراکنش‌های سرمایه (آورده و خروج)
        capital_transactions = cls.objects.filter(
            transaction_type__in=['principal_deposit', 'principal_withdrawal'],
            day_remaining__gt=0
        )
        
        profit_transactions = []
        
        for transaction in capital_transactions:
            profit_amount = transaction.calculate_profit(interest_rate)
            
            if profit_amount != 0:  # سود مثبت یا منفی
                # ایجاد تراکنش سود
                profit_transaction = cls(
                    project=transaction.project,
                    investor=transaction.investor,
                    period=transaction.period,
                    date_shamsi=transaction.date_shamsi,
                    date_gregorian=transaction.date_gregorian,
                    amount=profit_amount,
                    transaction_type='profit_accrual',
                    description=f'سود محاسبه شده برای {transaction.get_transaction_type_display()} {transaction.amount}',
                    day_remaining=transaction.day_remaining,
                    day_from_start=transaction.day_from_start,
                    interest_rate=interest_rate,
                    is_system_generated=True,
                    parent_transaction=transaction  # ردیابی تراکنش اصلی
                )
                profit_transactions.append(profit_transaction)
        
        return profit_transactions

    @classmethod
    def recalculate_profits_with_new_rate(cls, new_interest_rate):
        """
        محاسبه مجدد سودها با نرخ جدید
        """
        # حذف سودهای قبلی که توسط سیستم تولید شده‌اند
        cls.objects.filter(
            transaction_type='profit_accrual',
            is_system_generated=True
        ).delete()
        
        # محاسبه سودهای جدید
        new_profit_transactions = cls.calculate_all_profits(new_interest_rate)
        
        # ذخیره سودهای جدید
        for profit_transaction in new_profit_transactions:
            profit_transaction.save()
        
        return len(new_profit_transactions)
    
    @classmethod
    def delete_all_profit_transactions(cls):
        """
        حذف همه رکوردهای سود (اعم از سیستم‌ی و دستی)
        """
        deleted_count = cls.objects.filter(
            transaction_type='profit_accrual'
        ).count()
        
        cls.objects.filter(
            transaction_type='profit_accrual'
        ).delete()
        
        return deleted_count
    
    @classmethod
    def recalculate_all_profits_with_new_rate(cls, new_interest_rate):
        """
        سناریوی کامل: حذف همه سودهای قبلی و محاسبه مجدد با نرخ جدید
        
        این تابع:
        1. همه رکوردهای سود قبلی را حذف می‌کند
        2. سودهای جدید را با نرخ جدید محاسبه می‌کند
        3. سودهای جدید را ذخیره می‌کند
        
        Args:
            new_interest_rate (Decimal): نرخ سود جدید
            
        Returns:
            dict: شامل تعداد رکوردهای حذف شده و تعداد رکوردهای جدید
        """
        # مرحله 1: حذف همه رکوردهای سود قبلی
        deleted_count = cls.delete_all_profit_transactions()
        
        # مرحله 2: محاسبه سودهای جدید با نرخ جدید
        new_profit_transactions = cls.calculate_all_profits(new_interest_rate)
        
        # مرحله 3: ذخیره سودهای جدید
        for profit_transaction in new_profit_transactions:
            profit_transaction.save()
        
        return {
            'deleted_count': deleted_count,
            'new_count': len(new_profit_transactions),
            'total_affected': deleted_count + len(new_profit_transactions)
        }

class Expense(models.Model):
    """
    مدل هزینه‌های پروژه
    انواع مختلف هزینه‌های ماهانه مانند مدیر پروژه، تأسیسات، کارپرداز و غیره
    """
    EXPENSE_TYPES = [
        ('project_manager', 'مدیر پروژه'),
        ('facilities_manager', 'سرپرست کارگاه'),
        ('procurement', 'کارپرداز'),
        ('warehouse', 'انباردار'),
        ('construction_contractor', 'پیمان ساختمان'),
        ('other', 'سایر'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name="دوره")
    expense_type = models.CharField(max_length=30, choices=EXPENSE_TYPES, verbose_name="نوع هزینه")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="مبلغ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "هزینه"
        verbose_name_plural = "هزینه‌ها"

    def __str__(self):
        return f"{self.project.name} - {self.get_expense_type_display()} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('construction_Expense_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_Expense_update', kwargs={'pk': self.pk})
    
    def calculate_construction_contractor_amount(self):
        """
        محاسبه مبلغ هزینه پیمان ساختمان بر اساس 10% مجموع سایر هزینه‌های همان دوره
        """
        if self.expense_type != 'construction_contractor':
            return Decimal('0')
        
        # دریافت همه هزینه‌های همان دوره به جز construction_contractor
        other_expenses = Expense.objects.filter(
            period=self.period,
            project=self.project
        ).exclude(expense_type='construction_contractor')
        
        # محاسبه مجموع سایر هزینه‌ها
        total_other_expenses = sum(expense.amount for expense in other_expenses)
        
        # محاسبه 10% مجموع
        construction_contractor_amount = total_other_expenses * Decimal('0.1')
        
        return construction_contractor_amount.quantize(Decimal('0.01'))
    
    @classmethod
    def update_construction_contractor_for_period(cls, period, project):
        """
        به‌روزرسانی یا ایجاد هزینه پیمان ساختمان برای یک دوره مشخص
        """
        # حذف هزینه‌های پیمان ساختمان قبلی برای این دوره
        cls.objects.filter(
            period=period,
            project=project,
            expense_type='construction_contractor'
        ).delete()
        
        # محاسبه مبلغ جدید
        temp_expense = cls(period=period, project=project, expense_type='construction_contractor')
        new_amount = temp_expense.calculate_construction_contractor_amount()
        
        # اگر مبلغ محاسبه شده بیشتر از صفر باشد، رکورد جدید ایجاد کن
        if new_amount > 0:
            cls.objects.create(
                period=period,
                project=project,
                expense_type='construction_contractor',
                amount=new_amount,
                description='محاسبه خودکار: 10% مجموع سایر هزینه‌های دوره'
            )
            return new_amount
        
        return Decimal('0')
    
    @classmethod
    def recalculate_all_construction_contractor_expenses(cls, project=None):
        """
        محاسبه مجدد همه هزینه‌های پیمان ساختمان برای یک پروژه یا همه پروژه‌ها
        """
        if project:
            periods = Period.objects.filter(project=project)
        else:
            periods = Period.objects.all()
        
        total_updated = 0
        for period in periods:
            amount = cls.update_construction_contractor_for_period(period, period.project)
            if amount > 0:
                total_updated += 1
        
        return total_updated
    

class Sale(models.Model):
    """
    مدل فروش/مرجوعی
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name="دوره")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="مبلغ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "فروش/مرجوعی"
        verbose_name_plural = "فروش/مرجوعیها"
    
    def __str__(self):
        return f"{self.project.name} - {self.period.label} - {self.amount}"
    
    def get_update_url(self):
        return reverse('construction_Sale_update', kwargs={'pk': self.pk})
    
    def get_absolute_url(self):
        return reverse('construction_Sale_detail', kwargs={'pk': self.pk})

class UserProfile(models.Model):
    """
    مدل پروفایل کاربر برای مدیریت نقش‌ها و دسترسی‌ها
    """
    ROLE_CHOICES = [
        ('technical_admin', 'مدیر فنی'),
        ('end_user', 'کاربر نهایی/بهره‌بردار'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر")
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        verbose_name="پروژه",
        help_text="پروژه‌ای که این کاربر به آن دسترسی دارد",
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='end_user',
        verbose_name="نقش کاربر"
    )
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="شماره تلفن")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="بخش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    
    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل‌های کاربران"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    @property
    def is_technical_admin(self):
        """بررسی اینکه آیا کاربر مدیر فنی است یا نه"""
        return self.role == 'technical_admin'
    
    @property
    def is_end_user(self):
        """بررسی اینکه آیا کاربر نهایی است یا نه"""
        return self.role == 'end_user'
    
    def can_access_admin(self):
        """بررسی دسترسی به پنل ادمین"""
        return self.is_technical_admin or self.user.is_staff
    
    def can_access_dashboard(self):
        """بررسی دسترسی به داشبورد"""
        return True  # همه کاربران می‌توانند به داشبورد دسترسی داشته باشند
    
    def can_manage_projects(self):
        """بررسی دسترسی به مدیریت پروژه‌ها"""
        return self.is_technical_admin
    
    def can_manage_investors(self):
        """بررسی دسترسی به مدیریت سرمایه‌گذاران"""
        return self.is_technical_admin
    
    def can_manage_transactions(self):
        """بررسی دسترسی به مدیریت تراکنش‌ها"""
        return self.is_technical_admin
    
    def can_view_reports(self):
        """بررسی دسترسی به گزارش‌ها"""
        return self.is_technical_admin
    
    def get_allowed_pages(self):
        """دریافت لیست صفحات مجاز برای کاربر"""
        if self.is_technical_admin:
            return [
                'dashboard',
                'projects',
                'investors', 
                'transactions',
                'reports',
                'admin',
                'api'
            ]
        else:
            return [
                'dashboard',
                'profile'
            ]