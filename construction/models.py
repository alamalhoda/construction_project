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
    construction_contractor_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0.100,
        verbose_name="درصد پیمان ساخت",
        help_text="درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%)"
    )
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات", help_text="توضیحات اضافی درباره پروژه")
    color = models.CharField(
        max_length=7,
        default='#667eea',
        verbose_name="رنگ پروژه",
        help_text="رنگ نمایش پروژه (فرمت HEX)"
    )
    icon = models.CharField(
        max_length=50,
        default='fa-building',
        verbose_name="آیکون پروژه",
        help_text="نام کلاس آیکون Font Awesome (مثال: fa-building)"
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
        super().save(*args, **kwargs)
    


 
class UnitManager(models.Manager):
    """مرجع واحد برای آمار واحدها (بدون تغییر رفتار مصرف‌کننده‌ها)."""
    def project_stats(self, project: Project = None):
        from django.db.models import Sum, Count
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        stats = qs.aggregate(
            total_units=Count('id'),
            total_area=Sum('area'),
            total_price=Sum('total_price')
        )
        return {
            'total_units': stats['total_units'] or 0,
            'total_area': float(stats['total_area'] or 0),
            'total_price': float(stats['total_price'] or 0),
        }

    def project_total_area(self, project: Project = None):
        from django.db.models import Sum
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        return float(qs.aggregate(total=Sum('area'))['total'] or 0)


class Unit(models.Model):
    """
    مدل واحد مسکونی
    هر پروژه شامل چندین واحد است که هر واحد دارای متراژ، قیمت و مالکین است
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    name = models.CharField(max_length=200, verbose_name="نام واحد")
    area = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="متراژ")
    price_per_meter = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="قیمت هر متر")
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="قیمت نهایی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    # Manager سفارشی آمار واحدها
    objects = UnitManager()

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
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات", help_text="توضیحات اضافی درباره این سرمایه‌گذار")
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
    
    def is_current(self):
        """بررسی اینکه آیا این دوره، دوره جاری است"""
        import jdatetime
        today_jalali = jdatetime.datetime.now()
        current_year = today_jalali.year
        current_month = today_jalali.month
        return self.year == current_year and self.month_number == current_month
    


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
    def get_current_rate(cls, project):
        """دریافت نرخ سود فعلی برای پروژه"""
        if not project:
            raise ValueError("پارامتر project الزامی است")
        
        try:
            return cls.objects.filter(is_active=True, project=project).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_rate_for_date(cls, date, project):
        """دریافت نرخ سود برای تاریخ و پروژه مشخص"""
        if not project:
            raise ValueError("پارامتر project الزامی است")
        
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

class TransactionManager(models.Manager):
    """
    مرجع واحد برای تجمیع تراکنش‌ها در سرتاسر سیستم.
    قوانین ثابت:
    - deposits = principal_deposit + loan_deposit
    - withdrawals = principal_withdrawal (منفی)
    - profits = profit_accrual
    - net_capital = deposits + withdrawals
    """

    def get_queryset(self):
        return super().get_queryset()

    def project_totals(self, project: Project = None):
        from django.db.models import Sum, Q
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        deposits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type__in=['principal_deposit', 'loan_deposit'])))['total'] or 0
        withdrawals = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0
        profits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0
        deposits = float(deposits)
        withdrawals = float(withdrawals)
        profits = float(profits)
        net_capital = deposits + withdrawals
        return {
            'deposits': deposits,
            'withdrawals': withdrawals,
            'profits': profits,
            'net_capital': net_capital,
        }

    def period_totals(self, project: Project, period: 'Period'):
        from django.db.models import Sum, Q
        qs = self.get_queryset().filter(project=project, period=period)
        deposits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type__in=['principal_deposit', 'loan_deposit'])))['total'] or 0
        withdrawals = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0
        profits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0
        deposits = float(deposits)
        withdrawals = float(withdrawals)
        profits = float(profits)
        net_capital = deposits + withdrawals
        return {
            'deposits': deposits,
            'withdrawals': withdrawals,
            'profits': profits,
            'net_capital': net_capital,
        }

    def cumulative_until(self, project: Project, upto_period: 'Period'):
        from django.db.models import Sum, Q
        qs = self.get_queryset().filter(project=project).filter(
            Q(period__year__lt=upto_period.year) |
            Q(period__year=upto_period.year, period__month_number__lte=upto_period.month_number)
        )
        deposits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type__in=['principal_deposit', 'loan_deposit'])))['total'] or 0
        withdrawals = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0
        profits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0
        deposits = float(deposits)
        withdrawals = float(withdrawals)
        profits = float(profits)
        net_capital = deposits + withdrawals
        return {
            'deposits': deposits,
            'withdrawals': withdrawals,
            'profits': profits,
            'net_capital': net_capital,
        }

    def totals(self, project: Project = None, filters: dict = None):
        """
        مرجع واحدِ انعطاف‌پذیر برای تجمیع تراکنش‌ها با فیلترهای اختیاری.
        خروجی شامل تفکیک principal_deposit و loan_deposit نیز هست تا استاندارد deposits حفظ شود.
        """
        from django.db.models import Sum, Q
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        if filters:
            if 'investor_id' in filters and filters['investor_id'] is not None:
                qs = qs.filter(investor_id=filters['investor_id'])
            if 'date_from' in filters and filters['date_from']:
                qs = qs.filter(date_gregorian__gte=filters['date_from'])
            if 'date_to' in filters and filters['date_to']:
                qs = qs.filter(date_gregorian__lte=filters['date_to'])
            if 'transaction_type' in filters and filters['transaction_type']:
                qs = qs.filter(transaction_type=filters['transaction_type'])

        principal_deposit = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_deposit')))['total'] or 0
        loan_deposit = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='loan_deposit')))['total'] or 0
        withdrawals = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0
        profits = qs.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0

        principal_deposit = float(principal_deposit)
        loan_deposit = float(loan_deposit)
        withdrawals = float(withdrawals)
        profits = float(profits)
        deposits = principal_deposit + loan_deposit
        net_capital = deposits + withdrawals  # withdrawals منفی است

        return {
            'principal_deposit': principal_deposit,
            'loan_deposit': loan_deposit,
            'deposits': deposits,
            'withdrawals': withdrawals,
            'profits': profits,
            'net_capital': net_capital,
            'total_transactions': qs.count(),
        }


class Transaction(models.Model):
    """
    مدل تراکنش مالی
    شامل آورده، خروج از سرمایه و سود با محاسبه خودکار روز مانده و روز از شروع
    """
    TRANSACTION_TYPES = [
        ('principal_deposit', 'آورده'),
        ('loan_deposit', 'آورده وام'),
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
    
    # Manager سفارشی
    objects = TransactionManager()

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
        
        Args:
            interest_rate: نرخ سود (اگر None باشد، از نرخ فعال پروژه این تراکنش استفاده می‌شود)
        """
        if self.transaction_type not in ['principal_deposit', 'loan_deposit', 'principal_withdrawal']:
            return Decimal('0')
        
        if not interest_rate:
            # استفاده از نرخ سود فعال پروژه این تراکنش
            interest_rate = InterestRate.get_current_rate(project=self.project)
        
        if not interest_rate:
            return Decimal('0')
        
        if self.day_remaining <= 0:
            return Decimal('0')
        
        # محاسبه سود (مبلغ می‌تواند مثبت یا منفی باشد)
        profit = self.amount * self.day_remaining * interest_rate.rate
        
        return profit.quantize(Decimal('0.01'))  # گرد کردن به 2 رقم اعشار

    @classmethod
    def calculate_all_profits(cls, project, interest_rate=None):
        """
        محاسبه سود برای همه آورده‌ها
        
        Args:
            project: پروژه (الزامی)
            interest_rate: نرخ سود (در صورت None، از نرخ فعال پروژه استفاده می‌شود)
        """
        if not project:
            raise ValueError("پارامتر project الزامی است")
        
        if not interest_rate:
            interest_rate = InterestRate.get_current_rate(project=project)
        
        if not interest_rate:
            return []
        
        # دریافت همه تراکنش‌های سرمایه (آورده و خروج) برای پروژه مشخص
        capital_transactions = cls.objects.filter(
            project=project,
            transaction_type__in=['principal_deposit', 'loan_deposit', 'principal_withdrawal'],
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
    def recalculate_profits_with_new_rate(cls, new_interest_rate, project):
        """
        محاسبه مجدد سودها با نرخ جدید
        
        Args:
            new_interest_rate: نرخ سود جدید (InterestRate instance)
            project: پروژه (الزامی)
        """
        if not project:
            raise ValueError("پارامتر project الزامی است")
        
        # حذف سودهای قبلی که توسط سیستم تولید شده‌اند برای پروژه
        cls.objects.filter(
            project=project,
            transaction_type='profit_accrual',
            is_system_generated=True
        ).delete()
        
        # محاسبه سودهای جدید برای پروژه
        new_profit_transactions = cls.calculate_all_profits(project=project, interest_rate=new_interest_rate)
        
        # ذخیره سودهای جدید
        for profit_transaction in new_profit_transactions:
            profit_transaction.save()
        
        return len(new_profit_transactions)
    
    @classmethod
    def delete_all_profit_transactions(cls, project):
        """
        حذف همه رکوردهای سود (اعم از سیستم‌ی و دستی) برای پروژه مشخص
        
        Args:
            project: پروژه (الزامی)
        """
        if not project:
            raise ValueError("پارامتر project الزامی است")
        
        deleted_count = cls.objects.filter(
            project=project,
            transaction_type='profit_accrual'
        ).count()
        
        cls.objects.filter(
            project=project,
            transaction_type='profit_accrual'
        ).delete()
        
        return deleted_count
    
    @classmethod
    def recalculate_all_profits_with_new_rate(cls, new_interest_rate, project):
        """
        سناریوی کامل: حذف همه سودهای قبلی و محاسبه مجدد با نرخ جدید
        
        این تابع:
        1. همه رکوردهای سود قبلی را حذف می‌کند
        2. سودهای جدید را با نرخ جدید محاسبه می‌کند
        3. سودهای جدید را ذخیره می‌کند
        
        Args:
            new_interest_rate: نرخ سود جدید (InterestRate instance)
            project: پروژه (الزامی)
            
        Returns:
            dict: شامل تعداد رکوردهای حذف شده و تعداد رکوردهای جدید
        """
        if not project:
            raise ValueError("پارامتر project الزامی است")
        
        # مرحله 1: حذف همه رکوردهای سود قبلی برای پروژه
        deleted_count = cls.delete_all_profit_transactions(project=project)
        
        # مرحله 2: محاسبه سودهای جدید با نرخ جدید برای پروژه
        new_profit_transactions = cls.calculate_all_profits(project=project, interest_rate=new_interest_rate)
        
        # مرحله 3: ذخیره سودهای جدید
        for profit_transaction in new_profit_transactions:
            profit_transaction.save()
        
        return {
            'deleted_count': deleted_count,
            'new_count': len(new_profit_transactions),
            'total_affected': deleted_count + len(new_profit_transactions)
        }


 


# الصاق Manager سفارشی به مدل Transaction
# حذف add_to_class؛ Manager سفارشی در کلاس تنظیم شد

# Managers برای Expense و Sale (قبل از تعریف مدل‌ها برای جلوگیری از ارجاع نامشخص)
class ExpenseManager(models.Manager):
    """مرجع واحد برای تجمیع هزینه‌ها (بدون تغییر رفتار مصرف‌کننده‌ها)."""
    def project_totals(self, project: Project = None):
        from django.db.models import Sum
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        total_expenses = qs.aggregate(total=Sum('amount'))['total'] or 0
        return float(total_expenses)

    def period_totals(self, project: Project, period: Period):
        from django.db.models import Sum
        qs = self.get_queryset().filter(project=project, period=period)
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return float(total)

    def cumulative_until(self, project: Project, upto_period: Period):
        from django.db.models import Sum, Q
        qs = self.get_queryset().filter(project=project).filter(
            Q(period__year__lt=upto_period.year) |
            Q(period__year=upto_period.year, period__month_number__lte=upto_period.month_number)
        )
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return float(total)

    def totals(self, project: Project = None, filters: dict = None):
        from django.db.models import Sum
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        if filters:
            if 'period_id' in filters and filters['period_id']:
                qs = qs.filter(period_id=filters['period_id'])
            if 'expense_type' in filters and filters['expense_type']:
                qs = qs.filter(expense_type=filters['expense_type'])
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return {
            'total_expenses': float(total),
            'count': qs.count(),
        }


class SaleManager(models.Manager):
    """مرجع واحد برای تجمیع فروش/مرجوعی‌ها (بدون تغییر رفتار مصرف‌کننده‌ها)."""
    def project_totals(self, project: Project = None):
        from django.db.models import Sum
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        total_sales = qs.aggregate(total=Sum('amount'))['total'] or 0
        return float(total_sales)

    def period_totals(self, project: Project, period: Period):
        from django.db.models import Sum
        qs = self.get_queryset().filter(project=project, period=period)
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return float(total)

    def cumulative_until(self, project: Project, upto_period: Period):
        from django.db.models import Sum, Q
        qs = self.get_queryset().filter(project=project).filter(
            Q(period__year__lt=upto_period.year) |
            Q(period__year=upto_period.year, period__month_number__lte=upto_period.month_number)
        )
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return float(total)

    def totals(self, project: Project = None, filters: dict = None):
        from django.db.models import Sum
        qs = self.get_queryset()
        if project is not None:
            qs = qs.filter(project=project)
        if filters:
            if 'period_id' in filters and filters['period_id']:
                qs = qs.filter(period_id=filters['period_id'])
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return {
            'total_sales': float(total),
            'count': qs.count(),
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

    # Manager سفارشی برای تجمیع هزینه‌ها
    objects = ExpenseManager()

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
        
        # دریافت همه هزینه‌های همان دوره به جز construction_contractor و other
        other_expenses = Expense.objects.filter(
            period=self.period,
            project=self.project
        ).exclude(expense_type__in=['construction_contractor', 'other'])
        
        # محاسبه مجموع سایر هزینه‌ها
        total_other_expenses = sum(expense.amount for expense in other_expenses)
        
        # محاسبه درصد پیمان ساخت از مجموع سایر هزینه‌ها
        construction_contractor_amount = total_other_expenses * Decimal(str(self.project.construction_contractor_percentage))
        
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
                description=f'محاسبه خودکار: {project.construction_contractor_percentage * 100:.1f}% مجموع سایر هزینه‌های دوره'
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

    # Manager سفارشی برای تجمیع فروش/مرجوعی‌ها
    objects = SaleManager()
    
    class Meta:
        verbose_name = "فروش/مرجوعی"
        verbose_name_plural = "فروش/مرجوعیها"
    
    def __str__(self):
        return f"{self.project.name} - {self.period.label} - {self.amount}"
    
    def get_update_url(self):
        return reverse('construction_Sale_update', kwargs={'pk': self.pk})
    
    def get_absolute_url(self):
        return reverse('construction_Sale_detail', kwargs={'pk': self.pk})

class UnitSpecificExpense(models.Model):
    """
    مدل هزینه‌های اختصاصی هر واحد
    هزینه‌هایی که مالک واحد برای واحد خودش انجام می‌دهد
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="واحد")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    date_shamsi = jmodels.jDateField(verbose_name="تاریخ (شمسی)")
    date_gregorian = models.DateField(verbose_name="تاریخ (میلادی)")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="مبلغ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "هزینه اختصاصی واحد"
        verbose_name_plural = "هزینه‌های اختصاصی واحد"
        ordering = ['-date_shamsi', '-created_at']

    def __str__(self):
        return f"{self.unit.name} - {self.title} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('construction_UnitSpecificExpense_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_UnitSpecificExpense_update', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # تبدیل تاریخ شمسی به میلادی
        if self.date_shamsi and not self.date_gregorian:
            import jdatetime
            try:
                # تبدیل تاریخ شمسی به میلادی
                jdate = jdatetime.date(
                    self.date_shamsi.year,
                    self.date_shamsi.month,
                    self.date_shamsi.day
                )
                self.date_gregorian = jdate.togregorian()
            except Exception as e:
                # در صورت خطا، تاریخ میلادی را تنظیم نکن
                pass
        
        super().save(*args, **kwargs)

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


class PettyCashTransactionManager(models.Manager):
    """مرجع واحد برای محاسبه موجودی و آمار تنخواه"""
  
    def get_balance(self, project: Project, expense_type: str):
        """
        محاسبه وضعیت مالی عامل اجرایی
        وضعیت = مجموع دریافت‌ها - مجموع هزینه‌ها - مجموع عودت‌ها
      
        مقدار مثبت: عامل اجرایی بدهکار (باید به صندوق برگرداند)
        مقدار منفی: عامل اجرایی بستانکار (طلبکار) - صندوق باید به او بدهد
        """
        from django.db.models import Sum, Q
        from decimal import Decimal
      
        # مجموع دریافت‌ها
        total_receipts = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='receipt'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # مجموع عودت‌ها
        total_returns = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='return'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # مجموع هزینه‌ها از Expense
        total_expenses = Expense.objects.filter(
            project=project,
            expense_type=expense_type
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # محاسبه وضعیت مالی
        balance = total_receipts - total_expenses - total_returns
      
        return float(balance)
  
    def get_total_receipts(self, project: Project, expense_type: str):
        """مجموع تنخواه‌های دریافتی"""
        from django.db.models import Sum
      
        total = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='receipt'
        ).aggregate(total=Sum('amount'))['total'] or 0
      
        return float(total)
  
    def get_total_returns(self, project: Project, expense_type: str):
        """مجموع عودت‌های تنخواه"""
        from django.db.models import Sum
      
        total = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='return'
        ).aggregate(total=Sum('amount'))['total'] or 0
      
        return float(total)
  
    def get_total_expenses(self, project: Project, expense_type: str):
        """مجموع هزینه‌های ثبت شده (از Expense)"""
        from django.db.models import Sum
      
        total = Expense.objects.filter(
            project=project,
            expense_type=expense_type
        ).aggregate(total=Sum('amount'))['total'] or 0
      
        return float(total)
  
    def get_balance_by_period(self, project: Project, expense_type: str, period: Period):
        """
        وضعیت مالی عامل اجرایی تا پایان یک دوره خاص
        """
        from django.db.models import Sum, Q
        from decimal import Decimal
      
        # دریافت‌های قبل از پایان دوره (بر اساس تاریخ میلادی)
        total_receipts = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='receipt',
            date_gregorian__lte=period.end_date_gregorian
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # عودت‌های قبل از پایان دوره (بر اساس تاریخ میلادی)
        total_returns = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='return',
            date_gregorian__lte=period.end_date_gregorian
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # هزینه‌های قبل از پایان دوره (بر اساس تاریخ میلادی یا period)
        # هزینه‌هایی که period دارند: فقط دوره‌های قبل یا شامل این دوره
        # استفاده از Q object برای مقایسه صحیح سال و ماه
        from django.db.models import Q
        
        expenses_with_period = Expense.objects.filter(
            project=project,
            expense_type=expense_type,
            period__isnull=False
        ).filter(
            Q(period__year__lt=period.year) |
            Q(period__year=period.year, period__month_number__lte=period.month_number)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # هزینه‌های بدون period که قبل از پایان این دوره ایجاد شده‌اند
        # استفاده از created_at برای هزینه‌های بدون period
        expenses_without_period = Expense.objects.filter(
            project=project,
            expense_type=expense_type,
            period__isnull=True,
            created_at__date__lte=period.end_date_gregorian
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        total_expenses = expenses_with_period + expenses_without_period
      
        balance = total_receipts - total_expenses - total_returns
        return float(balance)
  
    def get_all_balances(self, project: Project):
        """وضعیت مالی همه عوامل اجرایی"""
        balances = {}
        for expense_type, label in Expense.EXPENSE_TYPES:
            # فیلتر کردن construction_contractor و other
            if expense_type not in ['construction_contractor', 'other']:
                balances[expense_type] = {
                    'label': label,
                    'balance': self.get_balance(project, expense_type),
                    'total_receipts': self.get_total_receipts(project, expense_type),
                    'total_expenses': self.get_total_expenses(project, expense_type),
                    'total_returns': self.get_total_returns(project, expense_type),
                }
        return balances
  
    def get_period_balance_trend(self, project: Project, expense_type: str, start_period: Period = None, end_period: Period = None):
        """
        ترند زمانی وضعیت مالی عامل اجرایی با جزئیات کامل
        شامل: دریافت‌ها، عودت‌ها، هزینه‌ها، مانده دوره‌ای و تجمعی
        """
        from django.db.models import Sum, Q
        from decimal import Decimal
      
        periods = Period.objects.filter(project=project).order_by('year', 'month_number')
      
        if start_period:
            periods = periods.filter(
                Q(year__gt=start_period.year) |
                Q(year=start_period.year, month_number__gte=start_period.month_number)
            )
      
        if end_period:
            periods = periods.filter(
                Q(year__lt=end_period.year) |
                Q(year=end_period.year, month_number__lte=end_period.month_number)
            )
      
        trend_data = []
        cumulative_balance = Decimal('0')  # مانده تجمعی کلی
        
        for period in periods:
            # دریافت‌های دوره‌ای (همان دوره)
            period_receipts = self.get_queryset().filter(
                project=project,
                expense_type=expense_type,
                transaction_type='receipt',
                date_gregorian__gte=period.start_date_gregorian,
                date_gregorian__lte=period.end_date_gregorian
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # عودت‌های دوره‌ای (همان دوره)
            period_returns = self.get_queryset().filter(
                project=project,
                expense_type=expense_type,
                transaction_type='return',
                date_gregorian__gte=period.start_date_gregorian,
                date_gregorian__lte=period.end_date_gregorian
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # هزینه‌های دوره‌ای (همان دوره)
            period_expenses = Expense.objects.filter(
                project=project,
                expense_type=expense_type,
                period=period
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # مانده دوره‌ای (receipts - expenses - returns)
            period_balance = period_receipts - period_expenses - period_returns
            
            # مانده تجمعی تا این دوره (از ابتدا تا پایان این دوره)
            cumulative_balance = self.get_balance_by_period(project, expense_type, period)
            
            trend_data.append({
                'period_id': period.id,
                'period_label': period.label,
                'year': period.year,
                'month_number': period.month_number,
                'period_receipts': float(period_receipts),      # تنخواه دریافتی دوره
                'period_returns': float(period_returns),        # عودت تنخواه دوره
                'period_expenses': float(period_expenses),      # هزینه دوره
                'period_balance': float(period_balance),        # مانده ماهانه (دوره‌ای)
                'cumulative_balance': float(cumulative_balance), # مانده تجمعی کلی (تا پایان این دوره)
                'balance': float(cumulative_balance),            # برای سازگاری با کد قبلی
            })
      
        return trend_data


class PettyCashTransaction(models.Model):
    """
    تراکنش‌های تنخواه عوامل اجرایی
    Single Source of Truth برای همه اطلاعات تنخواه
    """
    TRANSACTION_TYPES = [
        ('receipt', 'دریافت تنخواه'),      # از صندوق به عامل اجرایی
        ('return', 'عودت تنخواه'),         # از عامل اجرایی به صندوق
        # توجه: هزینه‌ها در Expense ثبت می‌شوند، نه اینجا
    ]
  
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    expense_type = models.CharField(
        max_length=30, 
        choices=Expense.EXPENSE_TYPES,
        verbose_name="عامل اجرایی",
        help_text="نوع هزینه که به عنوان عامل اجرایی استفاده می‌شود"
    )
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPES,
        verbose_name="نوع تراکنش"
    )
    amount = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        verbose_name="مبلغ",
        help_text="همیشه مثبت ذخیره می‌شود"
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )
    receipt_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شماره فیش/رسید"
    )
    date_shamsi = jmodels.jDateField(verbose_name="تاریخ شمسی")
    date_gregorian = models.DateField(verbose_name="تاریخ میلادی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
    # Manager سفارشی
    objects = PettyCashTransactionManager()
  
    class Meta:
        verbose_name = "تراکنش تنخواه"
        verbose_name_plural = "تراکنش‌های تنخواه"
        ordering = ['-date_gregorian', '-created_at']
        indexes = [
            models.Index(fields=['project', 'expense_type', 'date_gregorian']),
        ]
  
    def __str__(self):
        type_display = 'دریافت' if self.transaction_type == 'receipt' else 'عودت'
        return f"{self.get_expense_type_display()} - {type_display} - {self.amount}"
  
    def save(self, *args, **kwargs):
        # تبدیل تاریخ شمسی به میلادی
        if self.date_shamsi and not self.date_gregorian:
            from jdatetime import datetime as jdatetime
            if isinstance(self.date_shamsi, str):
                jdate = jdatetime.strptime(str(self.date_shamsi), '%Y-%m-%d')
                self.date_gregorian = jdate.togregorian().date()
                self.date_shamsi = jdate.date()
            elif hasattr(self.date_shamsi, 'year'):
                self.date_gregorian = self.date_shamsi.togregorian()
      
        # اطمینان از مثبت بودن مبلغ
        if self.amount < 0:
            self.amount = abs(self.amount)
      
        super().save(*args, **kwargs)
  
    def get_signed_amount(self):
        """
        برگرداندن مبلغ با علامت صحیح
        دریافت: مثبت (+)
        عودت: منفی (-)
        """
        if self.transaction_type == 'receipt':
            return self.amount
        else:  # return
            return -self.amount
    
    def get_absolute_url(self):
        return reverse('construction_PettyCashTransaction_detail', kwargs={'pk': self.pk})
    
    def get_update_url(self):
        return reverse('construction_PettyCashTransaction_update', kwargs={'pk': self.pk})