from django.db import models

# Create your models here.

class Project(models.Model):
    """
    مدل پروژه ساختمانی
    شامل اطلاعات کلی پروژه مانند نام، تاریخ شروع و پایان (شمسی و میلادی)
    """
    name = models.CharField(max_length=200, verbose_name="نام پروژه")
    start_date_shamsi = models.DateField(verbose_name="تاریخ شروع (شمسی)")
    end_date_shamsi = models.DateField(verbose_name="تاریخ پایان (شمسی)")
    start_date_gregorian = models.DateField(verbose_name="تاریخ شروع (میلادی)")
    end_date_gregorian = models.DateField(verbose_name="تاریخ پایان (میلادی)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"

    def __str__(self):
        return self.name

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

class Investor(models.Model):
    """
    مدل سرمایه‌گذار
    افرادی که در پروژه سرمایه‌گذاری می‌کنند و می‌توانند مالک چندین واحد باشند
    """
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    email = models.EmailField(verbose_name="ایمیل")
    units = models.ManyToManyField(Unit, verbose_name="واحدها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "سرمایه‌گذار"
        verbose_name_plural = "سرمایه‌گذاران"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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
    start_date_shamsi = models.DateField(verbose_name="تاریخ شروع شمسی")
    end_date_shamsi = models.DateField(verbose_name="تاریخ پایان شمسی")
    start_date_gregorian = models.DateField(verbose_name="تاریخ شروع میلادی")
    end_date_gregorian = models.DateField(verbose_name="تاریخ پایان میلادی")

    class Meta:
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"
        unique_together = ['project', 'year', 'month_number']

    def __str__(self):
        return f"{self.label} - {self.project.name}"

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
    date_shamsi = models.DateField(verbose_name="تاریخ شمسی")
    date_gregorian = models.DateField(verbose_name="تاریخ میلادی")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="مبلغ")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    day_remaining = models.IntegerField(verbose_name="روز مانده تا پایان پروژه")
    day_from_start = models.IntegerField(verbose_name="روز از ابتدای پروژه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"

    def save(self, *args, **kwargs):
        # محاسبه روز مانده تا پایان پروژه
        if self.project.end_date_gregorian and self.date_gregorian:
            self.day_remaining = (self.project.end_date_gregorian - self.date_gregorian).days
        
        # محاسبه روز از ابتدای پروژه
        if self.project.start_date_gregorian and self.date_gregorian:
            self.day_from_start = (self.date_gregorian - self.project.start_date_gregorian).days
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.investor} - {self.amount} - {self.get_transaction_type_display()}"

class Expense(models.Model):
    """
    مدل هزینه‌های پروژه
    انواع مختلف هزینه‌های ماهانه مانند مدیر پروژه، تأسیسات، کارپرداز و غیره
    """
    EXPENSE_TYPES = [
        ('project_manager', 'مدیر پروژه'),
        ('facilities_manager', 'مسئول تأسیسات'),
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