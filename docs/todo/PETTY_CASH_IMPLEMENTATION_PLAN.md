# برنامه پیاده‌سازی حسابداری تنخواه (Petty Cash Accounting)

**تاریخ ایجاد:** 2025-01-28
**وضعیت:** در حال بررسی
**نسخه:** 1.0

---

## 📋 خلاصه نیازمندی‌ها

### مفاهیم کلیدی

- **عامل اجرایی**: از `EXPENSE_TYPES` استفاده می‌شود (مدیر پروژه، سرپرست کارگاه، کارپرداز، انباردار)
- **صندوق ساختمان**: منبع و مقصد تنخواه
- **تراکنش‌های تنخواه**:
  - **دریافت تنخواه**: از صندوق به عامل اجرایی (چندین بار در زمان‌های مختلف)
  - **عودت تنخواه**: از عامل اجرایی به صندوق (برگشت بخشی از تنخواه)
  - **هزینه‌ها**: در نرم‌افزار حسابداری دیگر ثبت می‌شوند و کاربر در انتهای ماه در `Expense` ثبت می‌کند

### فرمول وضعیت مالی

```
وضعیت مالی عامل اجرایی = 
    مجموع تنخواه‌های دریافت شده 
    - مجموع هزینه‌های ثبت شده 
    - مجموع عودت تنخواه
```

#### تفسیر وضعیت مالی:

- **مقدار مثبت (+)** : عامل اجرایی **بدهکار** است
  - یعنی: پول بیشتری از صندوق دریافت کرده نسبت به هزینه‌هایی که انجام داده
  - یعنی: هنوز پول نزد عامل اجرایی باقی مانده که باید به صندوق برگرداند

- **مقدار منفی (-)** : عامل اجرایی **بستانکار (طلبکار)** است
  - یعنی: هزینه‌های انجام شده بیشتر از پولی است که از صندوق دریافت کرده
  - یعنی: صندوق باید به عامل اجرایی پول بدهد

#### مثال‌های عملی:

**مثال 1: وضعیت مثبت (بدهکار)**
```
دریافت تنخواه: 10,000,000 تومان
هزینه‌های ثبت شده: 7,000,000 تومان
عودت تنخواه: 0 تومان

وضعیت مالی = 10,000,000 - 7,000,000 - 0 = +3,000,000 تومان
```
**تفسیر:** عامل اجرایی 10 میلیون دریافت کرده، 7 میلیون هزینه کرده، پس **3 میلیون هنوز نزد اوست**. 
عامل اجرایی **بدهکار** است و باید 3 میلیون را به صندوق برگرداند.

---

**مثال 2: وضعیت منفی (بستانکار/طلبکار)**
```
دریافت تنخواه: 10,000,000 تومان
هزینه‌های ثبت شده: 12,000,000 تومان
عودت تنخواه: 0 تومان

وضعیت مالی = 10,000,000 - 12,000,000 - 0 = -2,000,000 تومان
```
**تفسیر:** عامل اجرایی 10 میلیون دریافت کرده، اما 12 میلیون هزینه کرده. 
یعنی **2 میلیون بیشتر** از آنچه دریافت کرده هزینه کرده. 
صندوق باید 2 میلیون به عامل اجرایی بدهد. عامل اجرایی **بستانکار (طلبکار)** است.

---

**مثال 3: وضعیت صفر (تسویه شده)**
```
دریافت تنخواه: 10,000,000 تومان
هزینه‌های ثبت شده: 8,000,000 تومان
عودت تنخواه: 2,000,000 تومان

وضعیت مالی = 10,000,000 - 8,000,000 - 2,000,000 = 0 تومان
```
**تفسیر:** عامل اجرایی 10 میلیون دریافت کرده، 8 میلیون هزینه کرده و 2 میلیون را برگردانده. 
حساب **تسویه شده** است.

---

**مثال 4: وضعیت مثبت با عودت**
```
دریافت تنخواه: 10,000,000 تومان
هزینه‌های ثبت شده: 6,000,000 تومان
عودت تنخواه: 2,000,000 تومان

وضعیت مالی = 10,000,000 - 6,000,000 - 2,000,000 = +2,000,000 تومان
```
**تفسیر:** عامل اجرایی 10 میلیون دریافت کرده، 6 میلیون هزینه کرده و 2 میلیون برگردانده. 
هنوز **2 میلیون نزد اوست**. عامل اجرایی **بدهکار** است و باید 2 میلیون را برگرداند.

### گزارش‌های مورد نیاز

1. **وضعیت مالی عوامل اجرایی**: گزارش کلی وضعیت مالی همه عوامل اجرایی
2. **گزارش دوره‌ای (ماهانه)**: وضعیت مالی در هر دوره
3. **ترند زمانی**: تغییرات وضعیت مالی در طول زمان

---

## 🏗️ فاز 1: طراحی مدل‌ها

### 1.1 مدل PettyCashTransaction

**مسیر:** `construction/models.py`

```python
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
```

### 1.2 Manager برای محاسبات

**مسیر:** `construction/models.py`

```python
class PettyCashTransactionManager(models.Manager):
    """مرجع واحد برای محاسبه موجودی و آمار تنخواه"""
  
    def get_balance(self, project: Project, expense_type: str):
        """
        محاسبه وضعیت مالی عامل اجرایی
        وضعیت = مجموع دریافت‌ها - مجموع هزینه‌ها - مجموع عودت‌ها
      
        مقدار مثبت: عامل اجرایی بستانکار (طلبکار)
        مقدار منفی: عامل اجرایی بدهکار
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
      
        # دریافت‌های قبل از پایان دوره
        total_receipts = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='receipt',
            date_gregorian__lte=period.end_date_gregorian
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # عودت‌های قبل از پایان دوره
        total_returns = self.get_queryset().filter(
            project=project,
            expense_type=expense_type,
            transaction_type='return',
            date_gregorian__lte=period.end_date_gregorian
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        # هزینه‌های دوره‌های قبل و شامل این دوره
        total_expenses = Expense.objects.filter(
            project=project,
            expense_type=expense_type,
            period__year__lte=period.year,
            period__month_number__lte=period.month_number
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      
        balance = total_receipts - total_expenses - total_returns
        return float(balance)
  
    def get_all_balances(self, project: Project):
        """وضعیت مالی همه عوامل اجرایی"""
        balances = {}
        for expense_type, label in Expense.EXPENSE_TYPES:
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
        ترند زمانی وضعیت مالی عامل اجرایی
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
        for period in periods:
            balance = self.get_balance_by_period(project, expense_type, period)
            trend_data.append({
                'period_id': period.id,
                'period_label': period.label,
                'year': period.year,
                'month_number': period.month_number,
                'balance': balance,
            })
      
        return trend_data
```

---

## 🔌 فاز 2: API Endpoints

### 2.1 Serializer

**مسیر:** `construction/serializers.py`

```python
class PettyCashTransactionSerializer(serializers.ModelSerializer):
    expense_type_label = serializers.CharField(source='get_expense_type_display', read_only=True)
    transaction_type_label = serializers.CharField(source='get_transaction_type_display', read_only=True)
    signed_amount = serializers.SerializerMethodField()
  
    class Meta:
        model = models.PettyCashTransaction
        fields = [
            'id',
            'project',
            'expense_type',
            'expense_type_label',
            'transaction_type',
            'transaction_type_label',
            'amount',
            'signed_amount',
            'description',
            'receipt_number',
            'date_shamsi',
            'date_gregorian',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'date_gregorian']
  
    def get_signed_amount(self, obj):
        """مبلغ با علامت"""
        return obj.get_signed_amount()
```

### 2.2 ViewSet

**مسیر:** `construction/api.py`

```python
class PettyCashTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت تراکنش‌های تنخواه"""
  
    queryset = models.PettyCashTransaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PettyCashTransactionSerializer
  
    @action(detail=False, methods=['get'])
    def balances(self, request):
        """دریافت وضعیت مالی همه عوامل اجرایی"""
        try:
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
          
            balances = models.PettyCashTransaction.objects.get_all_balances(active_project)
            return Response({'success': True, 'data': balances})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
  
    @action(detail=False, methods=['get'])
    def balance_detail(self, request):
        """دریافت وضعیت مالی یک عامل اجرایی خاص"""
        try:
            expense_type = request.query_params.get('expense_type')
            if not expense_type:
                return Response({'error': 'expense_type الزامی است'}, status=400)
          
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
          
            balance = models.PettyCashTransaction.objects.get_balance(active_project, expense_type)
            total_receipts = models.PettyCashTransaction.objects.get_total_receipts(active_project, expense_type)
            total_expenses = models.PettyCashTransaction.objects.get_total_expenses(active_project, expense_type)
            total_returns = models.PettyCashTransaction.objects.get_total_returns(active_project, expense_type)
          
            return Response({
                'success': True,
                'data': {
                    'expense_type': expense_type,
                    'expense_type_label': dict(Expense.EXPENSE_TYPES)[expense_type],
                    'balance': balance,
                    'total_receipts': total_receipts,
                    'total_expenses': total_expenses,
                    'total_returns': total_returns,
                    'is_creditor': balance < 0,  # بستانکار (طلبکار)
                    'is_debtor': balance > 0,    # بدهکار
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
  
    @action(detail=False, methods=['get'])
    def period_balance(self, request):
        """دریافت وضعیت مالی عامل اجرایی در یک دوره"""
        try:
            expense_type = request.query_params.get('expense_type')
            period_id = request.query_params.get('period_id')
          
            if not all([expense_type, period_id]):
                return Response({'error': 'expense_type و period_id الزامی است'}, status=400)
          
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
          
            period = models.Period.objects.get(id=period_id, project=active_project)
            balance = models.PettyCashTransaction.objects.get_balance_by_period(active_project, expense_type, period)
          
            return Response({
                'success': True,
                'data': {
                    'period_id': period.id,
                    'period_label': period.label,
                    'balance': balance,
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
  
    @action(detail=False, methods=['get'])
    def balance_trend(self, request):
        """ترند زمانی وضعیت مالی عامل اجرایی"""
        try:
            expense_type = request.query_params.get('expense_type')
            if not expense_type:
                return Response({'error': 'expense_type الزامی است'}, status=400)
          
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
          
            start_period_id = request.query_params.get('start_period_id')
            end_period_id = request.query_params.get('end_period_id')
          
            start_period = None
            end_period = None
          
            if start_period_id:
                start_period = models.Period.objects.get(id=start_period_id, project=active_project)
            if end_period_id:
                end_period = models.Period.objects.get(id=end_period_id, project=active_project)
          
            trend = models.PettyCashTransaction.objects.get_period_balance_trend(
                active_project, expense_type, start_period, end_period
            )
          
            return Response({'success': True, 'data': trend})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def detailed_report(self, request):
        """گزارش تفصیلی تراکنش‌های تنخواه با فیلتر و جستجو"""
        try:
            active_project = models.Project.get_active_project()
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
            
            # دریافت پارامترهای فیلتر
            expense_type = request.query_params.get('expense_type')
            transaction_type = request.query_params.get('transaction_type')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            min_amount = request.query_params.get('min_amount')
            max_amount = request.query_params.get('max_amount')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering', '-date_gregorian')
            
            # QuerySet اولیه
            queryset = models.PettyCashTransaction.objects.filter(project=active_project)
            
            # فیلترها
            if expense_type:
                queryset = queryset.filter(expense_type=expense_type)
            
            if transaction_type:
                queryset = queryset.filter(transaction_type=transaction_type)
            
            if start_date:
                queryset = queryset.filter(date_gregorian__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(date_gregorian__lte=end_date)
            
            if min_amount:
                queryset = queryset.filter(amount__gte=min_amount)
            
            if max_amount:
                queryset = queryset.filter(amount__lte=max_amount)
            
            # جستجو
            if search:
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(description__icontains=search) |
                    Q(receipt_number__icontains=search)
                )
            
            # مرتب‌سازی
            queryset = queryset.order_by(ordering)
            
            # Serialize
            serializer = serializers.PettyCashTransactionSerializer(queryset, many=True)
            
            # محاسبه مجموع‌ها
            total_receipts = queryset.filter(transaction_type='receipt').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            total_returns = queryset.filter(transaction_type='return').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            net_amount = float(total_receipts) - float(total_returns)
            
            return Response({
                'success': True,
                'data': {
                    'transactions': serializer.data,
                    'summary': {
                        'total_receipts': float(total_receipts),
                        'total_returns': float(total_returns),
                        'net_amount': net_amount,
                        'count': queryset.count()
                    }
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
```

### 2.3 URL Routing

**مسیر:** `construction/urls.py`

```python
router.register("PettyCashTransaction", api.PettyCashTransactionViewSet)
```

### 2.4 Admin Interface

**مسیر:** `construction/admin.py`

```python
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

admin.site.register(models.PettyCashTransaction, PettyCashTransactionAdmin)
```

### 2.5 Form

**مسیر:** `construction/forms.py`

```python
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
```

### 2.6 View Classes (برای Django Admin Views)

**مسیر:** `construction/views.py`

```python
@method_decorator(login_required, name='dispatch')
class PettyCashTransactionListView(ProjectFilterMixin, generic.ListView):
    model = models.PettyCashTransaction
    template_name = 'construction/petty_cash_transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date_gregorian', '-created_at']

@method_decorator(login_required, name='dispatch')
class PettyCashTransactionCreateView(ProjectFormMixin, generic.CreateView):
    model = models.PettyCashTransaction
    form_class = forms.PettyCashTransactionForm
    template_name = 'construction/petty_cash_transaction_form.html'

@method_decorator(login_required, name='dispatch')
class PettyCashTransactionUpdateView(ProjectFormMixin, generic.UpdateView):
    model = models.PettyCashTransaction
    form_class = forms.PettyCashTransactionForm
    template_name = 'construction/petty_cash_transaction_form.html'
    pk_url_kwarg = "pk"

@method_decorator(login_required, name='dispatch')
class PettyCashTransactionDetailView(ProjectFilterMixin, generic.DetailView):
    model = models.PettyCashTransaction
    template_name = 'construction/petty_cash_transaction_detail.html'
    pk_url_kwarg = "pk"

@method_decorator(login_required, name='dispatch')
class PettyCashTransactionDeleteView(ProjectFilterMixin, generic.DeleteView):
    model = models.PettyCashTransaction
    template_name = 'construction/petty_cash_transaction_confirm_delete.html'
    pk_url_kwarg = "pk"
```

### 2.7 URL Patterns (برای Views)

**مسیر:** `construction/urls.py`

```python
urlpatterns = (
    # ... URL patterns موجود ...
    path("construction/PettyCashTransaction/", views.PettyCashTransactionListView.as_view(), name="construction_PettyCashTransaction_list"),
    path("construction/PettyCashTransaction/create/", views.PettyCashTransactionCreateView.as_view(), name="construction_PettyCashTransaction_create"),
    path("construction/PettyCashTransaction/detail/<int:pk>/", views.PettyCashTransactionDetailView.as_view(), name="construction_PettyCashTransaction_detail"),
    path("construction/PettyCashTransaction/update/<int:pk>/", views.PettyCashTransactionUpdateView.as_view(), name="construction_PettyCashTransaction_update"),
    path("construction/PettyCashTransaction/delete/<int:pk>/", views.PettyCashTransactionDeleteView.as_view(), name="construction_PettyCashTransaction_delete"),
)
```

### 2.8 Templates (صفحات HTML)

**مسیر:** `construction/templates/construction/`

#### 2.8.1 Template لیست تراکنش‌ها

**فایل:** `petty_cash_transaction_list.html`

**ویژگی‌ها:**
- نمایش لیست تمام تراکنش‌های تنخواه
- فیلتر بر اساس عامل اجرایی و نوع تراکنش
- جستجو در توضیحات و شماره فیش
- دکمه افزودن تراکنش جدید
- لینک به جزئیات، ویرایش و حذف
- رنگ‌بندی بر اساس نوع تراکنش (دریافت/عودت)
- فرمت اعداد با جداکننده هزارگان

#### 2.8.2 Template فرم تراکنش

**فایل:** `petty_cash_transaction_form.html`

**ویژگی‌ها:**
- فرم ایجاد/ویرایش تراکنش
- فیلدهای: عامل اجرایی، نوع تراکنش، مبلغ، توضیحات، شماره فیش، تاریخ شمسی
- اعتبارسنجی فرم
- دکمه‌های ذخیره و انصراف
- استفاده از CustomJDateField برای تاریخ شمسی

#### 2.8.3 Template جزئیات تراکنش

**فایل:** `petty_cash_transaction_detail.html`

**ویژگی‌ها:**
- نمایش جزئیات کامل تراکنش
- نمایش تمام فیلدها
- دکمه‌های ویرایش و حذف
- لینک بازگشت به لیست
- فرمت اعداد با جداکننده هزارگان

#### 2.8.4 Template تأیید حذف

**فایل:** `petty_cash_transaction_confirm_delete.html`

**ویژگی‌ها:**
- پیام هشدار برای حذف
- نمایش اطلاعات تراکنش
- دکمه‌های تأیید حذف و انصراف
- فرم POST برای حذف

**نکته:** تمام templates باید مشابه templates موجود (مثل `expense_list.html`, `expense_form.html` و غیره) طراحی شوند و از همان استایل و ساختار استفاده کنند.

---

## 🎨 فاز 3: UI/Dashboard

### 3.1 صفحه مدیریت تراکنش‌های تنخواه

**مسیر:** `dashboard/view/petty_cash_dashboard.html`

**ویژگی‌ها:**

- لیست تراکنش‌های تنخواه (دریافت/عودت)
- فرم ثبت دریافت تنخواه
- فرم ثبت عودت تنخواه
- فیلتر بر اساس عامل اجرایی و تاریخ
- جستجو در توضیحات و شماره فیش

### 3.2 گزارش وضعیت مالی

**مسیر:** `dashboard/view/petty_cash_balance_report.html`

**ویژگی‌ها:**

- کارت‌های وضعیت مالی هر عامل اجرایی
- جدول خلاصه: دریافت‌ها، هزینه‌ها، عودت‌ها، وضعیت
- رنگ‌بندی بر اساس بدهکار/بستانکار بودن
- نمودار ترند زمانی وضعیت مالی

### 3.3 گزارش دوره‌ای

**مسیر:** `dashboard/view/petty_cash_period_report.html`

**ویژگی‌ها:**

- وضعیت مالی در هر دوره
- مقایسه دوره‌ای
- نمودار تغییرات دوره‌ای

### 3.4 گزارش تفصیلی تراکنش‌ها

**مسیر:** `dashboard/view/petty_cash_detail_report.html`

**ویژگی‌ها:**

- لیست کامل تمام تراکنش‌های یک عامل اجرایی
- فیلتر بر اساس:
  - عامل اجرایی (expense_type)
  - نوع تراکنش (receipt/return)
  - بازه تاریخ (از تاریخ - تا تاریخ)
  - مبلغ (حداقل - حداکثر)
- جستجو در:
  - توضیحات
  - شماره فیش/رسید
- مرتب‌سازی بر اساس:
  - تاریخ (صعودی/نزولی)
  - مبلغ (صعودی/نزولی)
  - نوع تراکنش
- نمایش اطلاعات:
  - تاریخ شمسی و میلادی
  - نوع تراکنش با رنگ‌بندی
  - مبلغ با علامت (مثبت/منفی)
  - توضیحات
  - شماره فیش/رسید
  - تاریخ ایجاد و به‌روزرسانی
- محاسبه مجموع:
  - مجموع دریافت‌ها
  - مجموع عودت‌ها
  - خالص (دریافت - عودت)
- Export به Excel/PDF

### 3.5 URL Routing (Dashboard)

**مسیر:** `dashboard/urls.py`

```python
urlpatterns = [
    # ... URL patterns موجود ...
    path('petty-cash/', views.petty_cash_dashboard, name='petty_cash_dashboard'),
    path('petty-cash/balance/', views.petty_cash_balance_report, name='petty_cash_balance_report'),
    path('petty-cash/period/', views.petty_cash_period_report, name='petty_cash_period_report'),
    path('petty-cash/detail/', views.petty_cash_detail_report, name='petty_cash_detail_report'),
]
```

**مسیر:** `dashboard/views.py`

```python
def petty_cash_dashboard(request):
    """صفحه مدیریت تراکنش‌های تنخواه"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_dashboard.html')
    return render(request, file_path)

def petty_cash_balance_report(request):
    """صفحه گزارش وضعیت مالی"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_balance_report.html')
    return render(request, file_path)

def petty_cash_period_report(request):
    """صفحه گزارش دوره‌ای"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_period_report.html')
    return render(request, file_path)

def petty_cash_detail_report(request):
    """صفحه گزارش تفصیلی"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'petty_cash_detail_report.html')
    return render(request, file_path)
```

### 3.6 Navigation Links

**مسیر:** `dashboard/view/*.html` (صفحات داشبورد)

**لینک‌های اضافه شده به navigation:**
- لینک به صفحه مدیریت تراکنش‌های تنخواه
- لینک به گزارش وضعیت مالی
- لینک به گزارش دوره‌ای
- لینک به گزارش تفصیلی

**مثال:**
```html
<a href="/dashboard/petty-cash/" class="nav-link">
    <i class="fas fa-wallet"></i>
    مدیریت تنخواه
</a>
<a href="/dashboard/petty-cash/balance/" class="nav-link">
    <i class="fas fa-chart-pie"></i>
    گزارش وضعیت مالی
</a>
```

### 3.7 رنگ‌بندی بر اساس استاندارد پروژه

**رنگ‌های استفاده شده:**
- **دریافت تنخواه**: از رنگ استاندارد پروژه برای آورده (آبی - `--deposit-color`)
- **عودت تنخواه**: از رنگ استاندارد پروژه برای برداشت (قرمز - `--withdrawal-color`)
- **وضعیت مثبت (بدهکار)**: از رنگ استاندارد پروژه برای بدهی (قرمز - `--withdrawal-color`)
- **وضعیت منفی (بستانکار)**: از رنگ استاندارد پروژه برای طلب (سبز - `--profit-color`)
- **وضعیت صفر (تسویه شده)**: از رنگ استاندارد پروژه برای مجموع (خاکستری - `--total-color`)

**استفاده از CSS Variables:**
```css
.petty-cash-receipt {
    color: var(--deposit-color);
    background-color: var(--deposit-color-light);
}

.petty-cash-return {
    color: var(--withdrawal-color);
    background-color: var(--withdrawal-color-light);
}

.balance-positive {
    color: var(--withdrawal-color);
    background-color: var(--withdrawal-color-light);
}

.balance-negative {
    color: var(--profit-color);
    background-color: var(--profit-color-light);
}
```

---

## 🗄️ فاز 4: Migration

### 4.1 ایجاد Migration

**دستور:**

```bash
python manage.py makemigrations construction
python manage.py migrate
```

### 4.2 محتوای Migration

- ایجاد جدول `PettyCashTransaction`
- ایجاد Index‌ها
- تنظیم Foreign Key‌ها

### 4.3 به‌روزرسانی اسکریپت بک‌آپ

**مسیر:** `scripts/create_backup.py`

**تغییرات اعمال شده:**
- ✅ اضافه شدن `PettyCashTransaction` به imports
- ✅ اضافه شدن به `get_database_stats()` برای آمارگیری
- ✅ اضافه شدن به `create_complete_fixture()` برای fixture کامل
- ✅ اضافه شدن به `create_individual_fixtures()` برای fixture جداگانه
- ✅ اضافه شدن به `create_stats_file()` برای گزارش
- ✅ به‌روزرسانی تعداد مورد انتظار fixtures (18 به جای 17)

**فایل ایجاد شده:** `petty_cash_transactions.json`

---

## 🧪 فاز 5: تست‌ها

### 5.1 تست‌های واحد (Unit Tests)

**مسیر:** `tests/construction/test_petty_cash.py`

**تست‌های مورد نیاز:**

- ✅ تست محاسبه وضعیت مالی
- ✅ تست محاسبه مجموع دریافت‌ها
- ✅ تست محاسبه مجموع عودت‌ها
- ✅ تست محاسبه مجموع هزینه‌ها
- ✅ تست محاسبه وضعیت مالی دوره‌ای
- ✅ تست ترند زمانی
- ✅ تست تبدیل تاریخ شمسی به میلادی
- ✅ تست اعتبارسنجی مبلغ مثبت

### 5.2 تست‌های یکپارچگی (Integration Tests)

- ✅ تست API endpoints
- ✅ تست ارتباط با Expense
- ✅ تست گزارش‌ها

---

## 📚 فاز 6: مستندسازی

### 6.1 مستندات API

- مستندات تمام endpoints
- مثال‌های درخواست/پاسخ
- کدهای خطا

### 6.2 راهنمای کاربر

- نحوه ثبت دریافت تنخواه
- نحوه ثبت عودت تنخواه
- نحوه مشاهده گزارش‌ها

---

## ✅ تصمیم‌گیری‌ها

### 1. محدودیت‌ها
**تصمیم:** ❌ نیاز به محدودیت در ثبت تراکنش‌ها نیست
- کاربر می‌تواند بدون محدودیت تراکنش ثبت کند
- عودت می‌تواند بیشتر از موجودی باشد (برای ثبت بدهی)

### 2. تایید تراکنش‌ها
**تصمیم:** ❌ نیاز به سیستم تایید تراکنش‌ها نیست
- تراکنش‌ها بلافاصله ثبت می‌شوند
- نیاز به workflow تایید نیست

### 3. گزارش تفصیلی
**تصمیم:** ✅ نیاز به گزارش تفصیلی تراکنش‌ها داریم
- لیست تمام تراکنش‌های یک عامل اجرایی
- فیلتر بر اساس تاریخ، نوع تراکنش و غیره
- جستجو در توضیحات و شماره فیش
- مرتب‌سازی بر اساس تاریخ، مبلغ و غیره

### 4. اتصال به نرم‌افزار حسابداری
**تصمیم:** ❌ نیاز به اتصال به نرم‌افزار حسابداری دیگر نیست
- هزینه‌ها به صورت دستی در `Expense` ثبت می‌شوند
- Import/Export خودکار نیاز نیست

### 5. ذخیره مبالغ
**تصمیم:** ✅ **گزینه 1**: همه مبالغ مثبت، علامت از transaction_type
- تمام مبالغ در دیتابیس به صورت مثبت ذخیره می‌شوند
- علامت از `transaction_type` مشخص می‌شود:
  - `receipt` (دریافت): مثبت (+)
  - `return` (عودت): منفی (-)

---

## 📋 چک‌لیست پیاده‌سازی

### فاز 1: مدل‌ها

- [ ] ایجاد مدل `PettyCashTransaction`
- [ ] ایجاد `PettyCashTransactionManager`
- [ ] تست مدل‌ها

### فاز 2: API

- [ ] ایجاد Serializer
- [ ] ایجاد ViewSet
- [ ] اضافه کردن endpoint `balances`
- [ ] اضافه کردن endpoint `balance_detail`
- [ ] اضافه کردن endpoint `period_balance`
- [ ] اضافه کردن endpoint `balance_trend`
- [ ] اضافه کردن endpoint `detailed_report`
- [ ] اضافه کردن URL routing (API)
- [ ] ایجاد Admin Interface
- [ ] ایجاد Form
- [ ] ایجاد View Classes (ListView, CreateView, UpdateView, DetailView, DeleteView)
- [ ] اضافه کردن URL patterns (Views)
- [ ] ایجاد Templates (list, form, detail, confirm_delete)
- [ ] تست API endpoints

### فاز 3: UI

- [ ] صفحه مدیریت تراکنش‌ها
- [ ] صفحه گزارش وضعیت مالی
- [ ] صفحه گزارش دوره‌ای
- [ ] صفحه گزارش تفصیلی تراکنش‌ها
- [ ] اضافه کردن URL routing (Dashboard)
- [ ] اضافه کردن View functions (Dashboard)
- [ ] اضافه کردن Navigation Links
- [ ] پیاده‌سازی رنگ‌بندی بر اساس استاندارد پروژه
- [ ] تست UI

### فاز 4: Migration

- [ ] ایجاد Migration
- [ ] اجرای Migration
- [ ] تست Migration
- [ ] اضافه کردن PettyCashTransaction به اسکریپت بک‌آپ

### فاز 5: تست‌ها

- [ ] تست‌های واحد
- [ ] تست‌های یکپارچگی
- [ ] تست‌های UI

### فاز 6: مستندسازی

- [ ] مستندات API
- [ ] راهنمای کاربر

---

## 🔄 تغییرات آینده (Future Enhancements)

1. **هشدارها**: هشدار برای موجودی منفی یا کم
2. **تایید تراکنش‌ها**: سیستم workflow برای تایید
3. **گزارش‌های پیشرفته**: گزارش‌های تحلیلی بیشتر
4. **Export**: Export به Excel/PDF
5. **Import**: Import از نرم‌افزار حسابداری

---

## 📝 یادداشت‌ها

- تمام مبالغ در دیتابیس به صورت مثبت ذخیره می‌شوند
- علامت از `transaction_type` مشخص می‌شود
- هزینه‌ها همچنان در `Expense` ثبت می‌شوند
- وضعیت مالی از سه منبع محاسبه می‌شود: دریافت‌ها، هزینه‌ها، عودت‌ها

---

**آخرین به‌روزرسانی:** 2025-01-28
