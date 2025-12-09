from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from . import models
from .project_manager import ProjectManager


class PeriodSerializer(serializers.ModelSerializer):
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای دوره (فقط خواندنی)'
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.'
    )
    label = serializers.CharField(
        max_length=50,
        required=True,
        help_text='عنوان دوره (مثال: "مهر 1403"). (الزامی)'
    )
    year = serializers.IntegerField(
        required=True,
        help_text='سال شمسی دوره (مثال: 1403). (الزامی)'
    )
    month_number = serializers.IntegerField(
        required=True,
        help_text='شماره ماه شمسی (1 تا 12). (الزامی)'
    )
    month_name = serializers.CharField(
        max_length=20,
        required=True,
        help_text='نام ماه شمسی (مثال: "مهر"). (الزامی)'
    )
    weight = serializers.IntegerField(
        required=True,
        help_text='وزن دوره برای محاسبات مالی. هرچه بیشتر باشد، تأثیر بیشتری در محاسبات دارد. (الزامی)'
    )
    start_date_shamsi = serializers.DateField(
        required=True,
        help_text='تاریخ شروع دوره به شمسی. (الزامی)'
    )
    end_date_shamsi = serializers.DateField(
        required=True,
        help_text='تاریخ پایان دوره به شمسی. (الزامی)'
    )
    start_date_gregorian = serializers.DateField(
        required=True,
        help_text='تاریخ شروع دوره به میلادی. (الزامی)'
    )
    end_date_gregorian = serializers.DateField(
        required=True,
        help_text='تاریخ پایان دوره به میلادی. (الزامی)'
    )

    class Meta:
        model = models.Period
        fields = [
            "id",
            "label",
            "year",
            "month_number",
            "month_name",
            "weight",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
            "project",
        ]
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه جاری session استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({"project": "فیلد project الزامی است."})
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
            validated_data['project'] = current_project
        
        return super().create(validated_data)

class ExpenseSerializer(serializers.ModelSerializer):
    period_data = PeriodSerializer(source='period', read_only=True)
    period_weight = serializers.SerializerMethodField()
    
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(read_only=True, help_text='شناسه یکتای هزینه (فقط خواندنی)')
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.'
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=models.Period.objects.all(),
        required=True,
        help_text='شناسه دوره‌ای که هزینه برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)'
    )
    expense_type = serializers.ChoiceField(
        choices=models.Expense.EXPENSE_TYPES,
        required=True,
        help_text='نوع هزینه. مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)'
    )
    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=True,
        help_text='مبلغ هزینه به تومان. باید مقدار مثبت باشد. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='توضیحات تکمیلی درباره هزینه. حداکثر 500 کاراکتر. (اختیاری)'
    )
    created_at = serializers.DateTimeField(read_only=True, help_text='تاریخ و زمان ایجاد هزینه (فقط خواندنی)')

    class Meta:
        model = models.Expense
        fields = [
            "id",
            "project",
            "expense_type",
            "amount",
            "description",
            "period",
            "period_data",
            "period_weight",
            "created_at",
        ]

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_period_weight(self, obj):
        """دریافت وزن دوره"""
        if obj.period:
            return obj.period.weight
        return 0
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه جاری session استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({"project": "فیلد project الزامی است."})
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
            validated_data['project'] = current_project
        
        return super().create(validated_data)

class InvestorSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()
    
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای سرمایه‌گذار (فقط خواندنی)'
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.'
    )
    first_name = serializers.CharField(
        max_length=100,
        required=True,
        help_text='نام سرمایه‌گذار. (الزامی)'
    )
    last_name = serializers.CharField(
        max_length=100,
        required=True,
        help_text='نام خانوادگی سرمایه‌گذار. (الزامی)'
    )
    phone = serializers.CharField(
        max_length=20,
        required=True,
        help_text='شماره تماس سرمایه‌گذار. (الزامی)'
    )
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text='آدرس ایمیل سرمایه‌گذار. (اختیاری)'
    )
    participation_type = serializers.ChoiceField(
        choices=models.Investor.PARTICIPATION_TYPE_CHOICES,
        required=False,
        default='owner',
        help_text='نوع مشارکت. مقادیر معتبر: owner (مالک), investor (سرمایه‌گذار). (پیش‌فرض: owner)'
    )
    contract_date_shamsi = serializers.DateField(
        required=False,
        allow_null=True,
        help_text='تاریخ قرارداد به شمسی. (اختیاری)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='توضیحات تکمیلی درباره سرمایه‌گذار. (اختیاری)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد سرمایه‌گذار (فقط خواندنی)'
    )

    class Meta:
        model = models.Investor
        fields = [
            "id",
            "project",
            "first_name",
            "last_name",
            "phone",
            "email",
            "participation_type",
            "units",
            "contract_date_shamsi",
            "description",
            "created_at",
        ]
    
    @extend_schema_field({'type': 'array', 'items': {'type': 'object'}})
    def get_units(self, obj):
        """دریافت اطلاعات کامل واحدها"""
        from .serializers import UnitSerializer
        return UnitSerializer(obj.units.all(), many=True).data
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه جاری session استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({"project": "فیلد project الزامی است."})
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
            validated_data['project'] = current_project
        
        return super().create(validated_data)

class UnitSerializer(serializers.ModelSerializer):
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای واحد (فقط خواندنی)'
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.'
    )
    name = serializers.CharField(
        max_length=200,
        required=True,
        help_text='نام واحد (مثال: "واحد 101" یا "آپارتمان 2A"). (الزامی)'
    )
    area = serializers.DecimalField(
        max_digits=12,
        decimal_places=4,
        required=True,
        help_text='متراژ واحد به متر مربع. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    price_per_meter = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        help_text='قیمت هر متر مربع به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    total_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        help_text='قیمت نهایی واحد به تومان (محاسبه شده: area × price_per_meter). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد واحد (فقط خواندنی)'
    )

    class Meta:
        model = models.Unit
        fields = [
            "id",
            "name",
            "area",
            "price_per_meter",
            "total_price",
            "project",
            "created_at",
        ]
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه جاری session استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({"project": "فیلد project الزامی است."})
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
            validated_data['project'] = current_project
        
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای پروژه (فقط خواندنی)'
    )
    name = serializers.CharField(
        max_length=200,
        required=True,
        help_text='نام پروژه ساختمانی. (الزامی)'
    )
    start_date_shamsi = serializers.DateField(
        required=True,
        help_text='تاریخ شروع پروژه به شمسی. (الزامی)'
    )
    end_date_shamsi = serializers.DateField(
        required=True,
        help_text='تاریخ پایان پروژه به شمسی. (الزامی)'
    )
    start_date_gregorian = serializers.DateField(
        required=True,
        help_text='تاریخ شروع پروژه به میلادی. (الزامی)'
    )
    end_date_gregorian = serializers.DateField(
        required=True,
        help_text='تاریخ پایان پروژه به میلادی. (الزامی)'
    )
    total_infrastructure = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        default=0.00,
        help_text='زیر بنای کل پروژه به متر مربع. (پیش‌فرض: 0.00)'
    )
    correction_factor = serializers.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=False,
        default=1.0000000000,
        help_text='ضریب اصلاحی برای محاسبات پروژه. (پیش‌فرض: 1.0000000000)'
    )
    construction_contractor_percentage = serializers.DecimalField(
        max_digits=6,
        decimal_places=3,
        required=False,
        default=0.100,
        help_text='درصد پیمان ساخت از مجموع سایر هزینه‌ها (به صورت اعشاری، مثلاً 0.100 برای 10%). (پیش‌فرض: 0.100)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='توضیحات اضافی درباره پروژه. (اختیاری)'
    )
    color = serializers.CharField(
        max_length=7,
        required=False,
        default='#667eea',
        help_text='رنگ نمایش پروژه (فرمت HEX، مثال: #667eea). (پیش‌فرض: #667eea)'
    )
    icon = serializers.CharField(
        max_length=50,
        required=False,
        default='fa-building',
        help_text='نام کلاس آیکون Font Awesome (مثال: fa-building). (پیش‌فرض: fa-building)'
    )
    gradient_primary_color = serializers.CharField(
        max_length=7,
        required=False,
        default='#667eea',
        help_text='رنگ اول گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #667eea)'
    )
    gradient_secondary_color = serializers.CharField(
        max_length=7,
        required=False,
        default='#764ba2',
        help_text='رنگ دوم گرادیانت پس‌زمینه (فرمت HEX). (پیش‌فرض: #764ba2)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد پروژه (فقط خواندنی)'
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان آخرین به‌روزرسانی پروژه (فقط خواندنی)'
    )

    class Meta:
        model = models.Project
        fields = [
            "id",
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
            "total_infrastructure",
            "correction_factor",
            "construction_contractor_percentage",
            "description",
            "color",
            "icon",
            "gradient_primary_color",
            "gradient_secondary_color",
            "created_at",
            "updated_at",
        ]

class SaleSerializer(serializers.ModelSerializer):
    project_data = ProjectSerializer(source='project', read_only=True)
    period_data = PeriodSerializer(source='period', read_only=True)
    
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای فروش/مرجوعی (فقط خواندنی)'
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.'
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=models.Period.objects.all(),
        required=True,
        help_text='شناسه دوره‌ای که فروش/مرجوعی برای آن ثبت می‌شود. دوره باید متعلق به پروژه جاری باشد. (الزامی)'
    )
    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=True,
        help_text='مبلغ فروش/مرجوعی به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='توضیحات تکمیلی درباره فروش/مرجوعی. (اختیاری)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد فروش/مرجوعی (فقط خواندنی)'
    )

    class Meta:
        model = models.Sale
        fields = [
            "id",
            "project",
            "period",
            "amount",
            "description",
            "created_at",
            "project_data",
            "period_data",
        ]
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه جاری session استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({"project": "فیلد project الزامی است."})
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
            validated_data['project'] = current_project
        
        return super().create(validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    # فیلدهای محاسبه شده - فقط برای خواندن
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای تراکنش (فقط خواندنی)'
    )
    date_gregorian = serializers.DateField(
        read_only=True,
        help_text='تاریخ میلادی تراکنش (فقط خواندنی - محاسبه شده)'
    )
    day_remaining = serializers.IntegerField(
        read_only=True,
        help_text='روز مانده تا پایان پروژه (فقط خواندنی - محاسبه شده)'
    )
    day_from_start = serializers.IntegerField(
        read_only=True,
        help_text='روز از ابتدای پروژه (فقط خواندنی - محاسبه شده)'
    )
    
    # فیلد date_shamsi برای نمایش (تبدیل میلادی به شمسی)
    date_shamsi = serializers.SerializerMethodField()
    
    # فیلد date_shamsi_input برای دریافت از frontend
    date_shamsi_input = serializers.CharField(
        write_only=True,
        required=False,
        help_text='تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)'
    )
    
    # فیلد date_shamsi_raw برای دریافت مستقیم از frontend
    date_shamsi_raw = serializers.CharField(
        write_only=True,
        required=False,
        help_text='تاریخ شمسی خام برای دریافت مستقیم از frontend. (اختیاری)'
    )
    
    # فیلدهای foreign key برای نوشتن
    investor_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه سرمایه‌گذار. می‌تواند از investor یا investor_id استفاده شود. (اختیاری)'
    )
    period_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه دوره. می‌تواند از period یا period_id استفاده شود. (اختیاری)'
    )
    
    # فیلدهای alternative برای frontend (write_only)
    investor = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه سرمایه‌گذار (جایگزین investor_id). (اختیاری)'
    )
    period = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه دوره (جایگزین period_id). (اختیاری)'
    )
    
    # فیلدهای اصلی
    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=True,
        help_text='مبلغ تراکنش به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    transaction_type = serializers.ChoiceField(
        choices=models.Transaction.TRANSACTION_TYPES,
        required=True,
        help_text='نوع تراکنش. مقادیر معتبر: principal_deposit (آورده), loan_deposit (آورده وام), principal_withdrawal (خروج از سرمایه), profit_accrual (سود). (الزامی)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='توضیحات تکمیلی درباره تراکنش. (اختیاری)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد تراکنش (فقط خواندنی)'
    )
    
    # فیلدهای nested برای خواندن (read_only)
    investor_data = InvestorSerializer(source='investor', read_only=True)
    project_data = ProjectSerializer(source='project', read_only=True)
    period_data = PeriodSerializer(source='period', read_only=True)
    
    # فیلد parent_transaction برای ردیابی تراکنش اصلی
    parent_transaction_id = serializers.IntegerField(read_only=True)
    parent_transaction_data = serializers.SerializerMethodField()

    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "date_shamsi",
            "date_shamsi_input",
            "date_shamsi_raw",
            "date_gregorian",
            "amount",
            "transaction_type",
            "description",
            "day_remaining",
            "day_from_start",
            "created_at",
            "investor",
            "period",
            "investor_id",
            "period_id",
            "investor_data",
            "project_data",
            "period_data",
            "parent_transaction_id",
            "parent_transaction_data",
        ]
    
    @extend_schema_field(OpenApiTypes.STR)
    def get_date_shamsi(self, obj):
        """تبدیل تاریخ میلادی به شمسی برای نمایش"""
        if obj.date_gregorian:
            from jdatetime import datetime as jdatetime
            # تبدیل تاریخ میلادی به شمسی
            jdate = jdatetime.fromgregorian(date=obj.date_gregorian)
            return jdate.strftime('%Y-%m-%d')
        return None
    
    @extend_schema_field({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'transaction_type': {'type': 'string'},
            'amount': {'type': 'number'},
            'date_gregorian': {'type': 'string', 'format': 'date'},
            'investor_name': {'type': 'string'}
        },
        'nullable': True
    })
    def get_parent_transaction_data(self, obj):
        """اطلاعات تراکنش اصلی برای تراکنش‌های سود"""
        if obj.parent_transaction:
            return {
                'id': obj.parent_transaction.id,
                'transaction_type': obj.parent_transaction.transaction_type,
                'amount': obj.parent_transaction.amount,
                'date_gregorian': obj.parent_transaction.date_gregorian,
                'investor_name': f"{obj.parent_transaction.investor.first_name} {obj.parent_transaction.investor.last_name}"
            }
        return None
        
    def create(self, validated_data):
        # تبدیل تاریخ شمسی به میلادی
        from jdatetime import datetime as jdatetime
        from datetime import datetime
        
        # دریافت تاریخ شمسی از frontend
        date_shamsi_input = validated_data.pop('date_shamsi_input', None)
        date_shamsi_raw = validated_data.pop('date_shamsi_raw', None)
        date_shamsi_direct = validated_data.pop('date_shamsi', None)
        
        # حذف date_shamsi از validated_data اگر وجود دارد
        validated_data.pop('date_shamsi', None)
        
        # استفاده از هر کدام که موجود باشد
        date_shamsi_value = date_shamsi_input or date_shamsi_raw or date_shamsi_direct
        
        if date_shamsi_value:
            # تبدیل تاریخ شمسی (string) به میلادی (date object)
            jdate = jdatetime.strptime(str(date_shamsi_value), '%Y-%m-%d')
            gregorian_datetime = jdate.togregorian()
            # تبدیل datetime به date
            validated_data['date_gregorian'] = gregorian_datetime.date()
            # date_shamsi باید تاریخ میلادی باشد (برای jmodels.jDateField)
            validated_data['date_shamsi'] = jdate.date()
        
        # Handle کردن فیلدهای مختلف از frontend
        # اگر investor_id وجود دارد، از آن استفاده کن
        if 'investor_id' in validated_data:
            validated_data['investor_id'] = validated_data.pop('investor_id')
        # اگر investor وجود دارد، آن را به investor_id تبدیل کن
        elif 'investor' in validated_data:
            validated_data['investor_id'] = validated_data.pop('investor')
        
        # تنظیم پروژه جاری از session
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("فیلد project الزامی است.")
        
        current_project = ProjectManager.get_current_project(request)
        if not current_project:
            raise serializers.ValidationError("هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.")
        validated_data['project_id'] = current_project.id
        
        # اگر period_id وجود دارد، از آن استفاده کن
        if 'period_id' in validated_data:
            validated_data['period_id'] = validated_data.pop('period_id')
        # اگر period وجود دارد، آن را به period_id تبدیل کن
        elif 'period' in validated_data:
            validated_data['period_id'] = validated_data.pop('period')
        
        # اطمینان از منفی بودن مبالغ برداشت
        if validated_data.get('transaction_type') == 'principal_withdrawal':
            if validated_data.get('amount') and validated_data['amount'] > 0:
                validated_data['amount'] = -validated_data['amount']
        
        # ایجاد تراکنش
        transaction = super().create(validated_data)
        
        # محاسبه مجدد روزها بعد از ایجاد
        if transaction.project and transaction.date_gregorian:
            if transaction.project.end_date_gregorian:
                transaction.day_remaining = (transaction.project.end_date_gregorian - transaction.date_gregorian).days
            if transaction.project.start_date_gregorian:
                transaction.day_from_start = (transaction.date_gregorian - transaction.project.start_date_gregorian).days
            transaction.save()
        
        return transaction
    
    def update(self, instance, validated_data):
        # تبدیل تاریخ شمسی به میلادی
        from jdatetime import datetime as jdatetime
        from datetime import datetime
        
        # دریافت تاریخ شمسی از frontend
        date_shamsi_input = validated_data.pop('date_shamsi_input', None)
        date_shamsi_raw = validated_data.pop('date_shamsi_raw', None)
        
        # استفاده از هر کدام که موجود باشد
        date_shamsi_value = date_shamsi_input or date_shamsi_raw
        
        if date_shamsi_value:
            # تبدیل تاریخ شمسی (string) به میلادی (date object)
            jdate = jdatetime.strptime(str(date_shamsi_value), '%Y-%m-%d')
            gregorian_datetime = jdate.togregorian()
            # تبدیل datetime به date
            validated_data['date_gregorian'] = gregorian_datetime.date()
            # date_shamsi باید تاریخ میلادی باشد (برای jmodels.jDateField)
            validated_data['date_shamsi'] = jdate.date()
        
        # Handle کردن فیلدهای مختلف از frontend
        # اگر investor_id وجود دارد، از آن استفاده کن
        if 'investor_id' in validated_data:
            validated_data['investor_id'] = validated_data.pop('investor_id')
        # اگر investor وجود دارد، آن را به investor_id تبدیل کن
        elif 'investor' in validated_data:
            validated_data['investor_id'] = validated_data.pop('investor')
        
        # تنظیم پروژه جاری از session (فقط اگر پروژه تغییر کرده باشد)
        if 'project_id' in validated_data or 'project' in validated_data:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError("فیلد project الزامی است.")
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError("هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.")
            validated_data['project_id'] = current_project.id
        
        # اگر period_id وجود دارد، از آن استفاده کن
        if 'period_id' in validated_data:
            validated_data['period_id'] = validated_data.pop('period_id')
        # اگر period وجود دارد، آن را به period_id تبدیل کن
        elif 'period' in validated_data:
            validated_data['period_id'] = validated_data.pop('period')
        
        # اطمینان از منفی بودن مبالغ برداشت
        if validated_data.get('transaction_type') == 'principal_withdrawal':
            if validated_data.get('amount') and validated_data['amount'] > 0:
                validated_data['amount'] = -validated_data['amount']
        
        # بروزرسانی تراکنش
        transaction = super().update(instance, validated_data)
        
        # محاسبه مجدد روزها بعد از بروزرسانی
        if transaction.project and transaction.date_gregorian:
            if transaction.project.end_date_gregorian:
                transaction.day_remaining = (transaction.project.end_date_gregorian - transaction.date_gregorian).days
            if transaction.project.start_date_gregorian:
                transaction.day_from_start = (transaction.date_gregorian - transaction.project.start_date_gregorian).days
            transaction.save(update_fields=['day_remaining', 'day_from_start'])
        
        return transaction


class CombinedTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer ترکیبی که تراکنش اصلی و تراکنش سود مرتبط را در یک رکورد برمی‌گرداند
    فقط تراکنش‌های اصلی (غیر سود) را می‌گیرد و اطلاعات سود مرتبط را در همان رکورد اضافه می‌کند
    """
    # فیلدهای تراکنش اصلی
    date_gregorian = serializers.DateField(read_only=True)
    day_remaining = serializers.IntegerField(read_only=True)
    day_from_start = serializers.IntegerField(read_only=True)
    date_shamsi = serializers.SerializerMethodField()
    
    # فیلدهای nested برای خواندن
    investor_data = InvestorSerializer(source='investor', read_only=True)
    project_data = ProjectSerializer(source='project', read_only=True)
    period_data = PeriodSerializer(source='period', read_only=True)
    
    # اطلاعات تراکنش سود مرتبط
    profit_transaction = serializers.SerializerMethodField()
    has_profit = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "date_shamsi",
            "date_gregorian",
            "amount",
            "transaction_type",
            "description",
            "day_remaining",
            "day_from_start",
            "created_at",
            "investor",
            "period",
            "investor_data",
            "project_data",
            "period_data",
            "profit_transaction",
            "has_profit",
        ]
    
    def get_date_shamsi(self, obj):
        """تبدیل تاریخ میلادی به شمسی برای نمایش"""
        if obj.date_gregorian:
            from jdatetime import datetime as jdatetime
            jdate = jdatetime.fromgregorian(date=obj.date_gregorian)
            return jdate.strftime('%Y-%m-%d')
        return None
    
    def get_profit_transaction(self, obj):
        """
        پیدا کردن تراکنش سود مرتبط با این تراکنش اصلی
        استفاده از prefetch_related برای بهینه‌سازی (بدون N+1 query)
        """
        # استفاده از profit_transactions که از prefetch_related آمده است
        # اگر prefetch نشده باشد، از transaction_set استفاده می‌کنیم (fallback)
        profit_transactions = getattr(obj, 'profit_transactions', None)
        if profit_transactions is None:
            # Fallback: اگر prefetch نشده باشد
            profit_transactions = [t for t in obj.transaction_set.all() if t.transaction_type == 'profit_accrual']
        
        if profit_transactions and len(profit_transactions) > 0:
            profit = profit_transactions[0]
            return {
                'id': profit.id,
                'amount': float(profit.amount),
                'date_shamsi': self.get_date_shamsi(profit),
                'date_gregorian': profit.date_gregorian.isoformat() if profit.date_gregorian else None,
                'description': profit.description,
                'day_remaining': profit.day_remaining,
                'day_from_start': profit.day_from_start,
                'is_system_generated': profit.is_system_generated,
                'interest_rate_id': profit.interest_rate.id if profit.interest_rate else None,
                'created_at': profit.created_at.isoformat() if profit.created_at else None,
            }
        return None
    
    def get_has_profit(self, obj):
        """بررسی وجود تراکنش سود برای این تراکنش اصلی"""
        # استفاده از prefetch_related برای بهینه‌سازی
        profit_transactions = getattr(obj, 'profit_transactions', None)
        if profit_transactions is not None:
            return len(profit_transactions) > 0
        # Fallback: اگر prefetch نشده باشد
        return any(t.transaction_type == 'profit_accrual' for t in obj.transaction_set.all())


class InterestRateSerializer(serializers.ModelSerializer):
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای نرخ سود (فقط خواندنی)'
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        allow_null=True,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود.'
    )
    rate = serializers.DecimalField(
        max_digits=20,
        decimal_places=15,
        required=True,
        help_text='نرخ سود روزانه (به صورت اعشاری، مثال: 0.000481925679775). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    effective_date = serializers.CharField(
        write_only=True,
        required=True,
        help_text='تاریخ اعمال نرخ سود به شمسی به فرمت YYYY-MM-DD (مثال: 1403-01-01). (الزامی)'
    )
    effective_date_display = serializers.SerializerMethodField(
        read_only=True,
        help_text='تاریخ شمسی برای نمایش (فقط خواندنی)'
    )
    effective_date_gregorian = serializers.DateField(
        read_only=True,
        allow_null=True,
        help_text='تاریخ اعمال نرخ سود به میلادی (فقط خواندنی - محاسبه شده)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='توضیحات درباره تغییر نرخ سود. (اختیاری)'
    )
    is_active = serializers.BooleanField(
        required=False,
        default=True,
        help_text='آیا این نرخ در حال حاضر فعال است؟ (پیش‌فرض: True)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد نرخ سود (فقط خواندنی)'
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان آخرین به‌روزرسانی نرخ سود (فقط خواندنی)'
    )

    class Meta:
        model = models.InterestRate
        fields = [
            "id",
            "project",
            "rate",
            "effective_date",
            "effective_date_display",
            "effective_date_gregorian",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        # اگر project ارسال نشده یا None باشد، از پروژه فعال استفاده کن
        project = validated_data.pop('project', None)
        
        if project is None:
            # استفاده از پروژه جاری از session
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({"project": "فیلد project الزامی است."})
            
            project = ProjectManager.get_current_project(request)
            if not project:
                raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
        elif not isinstance(project, models.Project):
            # اگر project یک instance نیست، آن را تبدیل کن
            try:
                project = models.Project.objects.get(id=int(project))
            except (models.Project.DoesNotExist, ValueError, TypeError):
                # در صورت خطا، از پروژه جاری session استفاده کن
                request = self.context.get('request')
                if request:
                    project = ProjectManager.get_current_project(request)
                    if not project:
                        raise serializers.ValidationError({"project": "پروژه معتبر نیست"})
                else:
                    raise serializers.ValidationError({"project": "پروژه معتبر نیست"})
        
        # تبدیل تاریخ شمسی به میلادی
        effective_date_str = validated_data.pop('effective_date')
        
        # Parse تاریخ شمسی
        from jdatetime import datetime as jdatetime
        jdate = jdatetime.strptime(effective_date_str, '%Y-%m-%d')
        
        # تبدیل به میلادی
        gregorian_date = jdate.togregorian().date()
        
        # ایجاد instance با save() method
        instance = models.InterestRate(
            project=project,
            effective_date=jdate.date(),
            effective_date_gregorian=gregorian_date,
            **validated_data
        )
        instance.save()  # این save() method مدل را فراخوانی می‌کند
        
        return instance

    def update(self, instance, validated_data):
        # تبدیل تاریخ شمسی به میلادی اگر ارائه شده باشد
        if 'effective_date' in validated_data:
            effective_date_str = validated_data.pop('effective_date')
            
            # Parse تاریخ شمسی
            from jdatetime import datetime as jdatetime
            jdate = jdatetime.strptime(effective_date_str, '%Y-%m-%d')
            
            # تبدیل به میلادی
            gregorian_date = jdate.togregorian().date()
            
            # به‌روزرسانی فیلدها
            instance.effective_date = jdate.date()
            instance.effective_date_gregorian = gregorian_date
        
        # به‌روزرسانی سایر فیلدها
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    @extend_schema_field(OpenApiTypes.STR)
    def get_effective_date_display(self, obj):
        """نمایش تاریخ شمسی برای frontend"""
        if obj.effective_date:
            return str(obj.effective_date)
        return None

class UnitSpecificExpenseSerializer(serializers.ModelSerializer):
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای هزینه اختصاصی واحد (فقط خواندنی)'
    )
    # فیلدهای محاسبه شده - فقط برای خواندن
    date_gregorian = serializers.DateField(
        read_only=True,
        help_text='تاریخ میلادی هزینه (فقط خواندنی - محاسبه شده)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد هزینه (فقط خواندنی)'
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان آخرین به‌روزرسانی هزینه (فقط خواندنی)'
    )
    
    # فیلد date_shamsi برای نمایش (تبدیل میلادی به شمسی)
    date_shamsi = serializers.SerializerMethodField()
    
    # فیلد date_shamsi_input برای دریافت از frontend
    date_shamsi_input = serializers.CharField(
        write_only=True,
        required=False,
        help_text='تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)'
    )
    
    # فیلدهای foreign key برای نوشتن
    unit_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه واحد. می‌تواند از unit یا unit_id استفاده شود. (اختیاری)'
    )
    project_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه پروژه. اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)'
    )
    
    # فیلدهای alternative برای frontend (write_only)
    unit = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه واحد (جایگزین unit_id). (اختیاری)'
    )
    project = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='شناسه پروژه (جایگزین project_id). اگر مشخص نشود، از پروژه جاری session استفاده می‌شود. (اختیاری)'
    )
    
    # فیلدهای اصلی
    title = serializers.CharField(
        max_length=200,
        required=True,
        help_text='عنوان هزینه اختصاصی واحد (مثال: "نصب کولر گازی"). (الزامی)'
    )
    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=True,
        help_text='مبلغ هزینه به تومان. برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='توضیحات تکمیلی درباره هزینه. (اختیاری)'
    )
    
    # فیلدهای nested برای خواندن (read_only)
    unit_data = UnitSerializer(source='unit', read_only=True)
    project_data = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = models.UnitSpecificExpense
        fields = [
            'id',
            'project',
            'project_id',
            'project_data',
            'unit',
            'unit_id',
            'unit_data',
            'title',
            'date_shamsi',
            'date_shamsi_input',
            'date_gregorian',
            'amount',
            'description',
            'created_at',
            'updated_at',
        ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_date_shamsi(self, obj):
        """تبدیل تاریخ میلادی به شمسی برای نمایش"""
        if obj.date_shamsi:
            return str(obj.date_shamsi)
        elif obj.date_gregorian:
            import jdatetime
            try:
                gdate = obj.date_gregorian
                jdate = jdatetime.date.fromgregorian(date=gdate)
                return str(jdate)
            except:
                return None
        return None

    def create(self, validated_data):
        # تبدیل تاریخ شمسی به میلادی
        date_shamsi_input = validated_data.pop('date_shamsi_input', None)
        if date_shamsi_input:
            import jdatetime
            try:
                # پارس کردن تاریخ شمسی (فرمت: YYYY-MM-DD)
                parts = date_shamsi_input.split('-')
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    jdate = jdatetime.date(year, month, day)
                    validated_data['date_shamsi'] = jdate
                    validated_data['date_gregorian'] = jdate.togregorian()
            except Exception as e:
                raise serializers.ValidationError({
                    'date_shamsi_input': f'فرمت تاریخ نامعتبر است: {str(e)}'
                })
        
        # مدیریت unit_id و unit
        unit_id = validated_data.pop('unit_id', None) or validated_data.pop('unit', None)
        if unit_id:
            try:
                validated_data['unit'] = models.Unit.objects.get(pk=unit_id)
            except models.Unit.DoesNotExist:
                raise serializers.ValidationError({'unit': 'واحد یافت نشد'})
        
        # مدیریت project_id و project - اگر ارسال نشده، از پروژه فعال استفاده کن
        project_id = validated_data.pop('project_id', None) or validated_data.pop('project', None)
        if project_id:
            try:
                validated_data['project'] = models.Project.objects.get(pk=project_id)
            except models.Project.DoesNotExist:
                raise serializers.ValidationError({'project': 'پروژه یافت نشد'})
        else:
            # استفاده از پروژه جاری از session
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError({'project': 'فیلد project الزامی است.'})
            
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                raise serializers.ValidationError({
                    'project': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                })
            validated_data['project'] = current_project
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # تبدیل تاریخ شمسی به میلادی اگر ارائه شده باشد
        date_shamsi_input = validated_data.pop('date_shamsi_input', None)
        if date_shamsi_input:
            import jdatetime
            try:
                # پارس کردن تاریخ شمسی (فرمت: YYYY-MM-DD)
                parts = date_shamsi_input.split('-')
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    jdate = jdatetime.date(year, month, day)
                    validated_data['date_shamsi'] = jdate
                    validated_data['date_gregorian'] = jdate.togregorian()
            except Exception as e:
                raise serializers.ValidationError({
                    'date_shamsi_input': f'فرمت تاریخ نامعتبر است: {str(e)}'
                })
        
        # مدیریت unit_id و unit
        unit_id = validated_data.pop('unit_id', None) or validated_data.pop('unit', None)
        if unit_id:
            try:
                validated_data['unit'] = models.Unit.objects.get(pk=unit_id)
            except models.Unit.DoesNotExist:
                raise serializers.ValidationError({'unit': 'واحد یافت نشد'})
        
        # مدیریت project_id و project
        project_id = validated_data.pop('project_id', None) or validated_data.pop('project', None)
        if project_id:
            try:
                validated_data['project'] = models.Project.objects.get(pk=project_id)
            except models.Project.DoesNotExist:
                raise serializers.ValidationError({'project': 'پروژه یافت نشد'})
        
        return super().update(instance, validated_data)


class PettyCashTransactionSerializer(serializers.ModelSerializer):
    # تعریف صریح فیلدها برای اطمینان از اضافه شدن help_text به schema
    id = serializers.IntegerField(
        read_only=True,
        help_text='شناسه یکتای تراکنش تنخواه (فقط خواندنی)'
    )
    project = serializers.IntegerField(
        read_only=True,
        help_text='شناسه پروژه (فقط خواندنی - به صورت خودکار از session تنظیم می‌شود)'
    )
    expense_type = serializers.ChoiceField(
        choices=models.Expense.EXPENSE_TYPES,
        required=True,
        help_text='عامل اجرایی (نوع هزینه). مقادیر معتبر: project_manager (مدیر پروژه), facilities_manager (سرپرست کارگاه), procurement (کارپرداز), warehouse (انباردار), construction_contractor (پیمان ساختمان), other (سایر). (الزامی)'
    )
    expense_type_label = serializers.CharField(
        source='get_expense_type_display',
        read_only=True,
        help_text='برچسب عامل اجرایی برای نمایش (فقط خواندنی)'
    )
    transaction_type = serializers.ChoiceField(
        choices=models.PettyCashTransaction.TRANSACTION_TYPES,
        required=True,
        help_text='نوع تراکنش. مقادیر معتبر: receipt (دریافت تنخواه از صندوق به عامل اجرایی), return (عودت تنخواه از عامل اجرایی به صندوق). (الزامی)'
    )
    transaction_type_label = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True,
        help_text='برچسب نوع تراکنش برای نمایش (فقط خواندنی)'
    )
    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=True,
        help_text='مبلغ تراکنش به تومان (همیشه مثبت ذخیره می‌شود). برای جلوگیری از مشکلات دقت، به صورت string ارسال شود. (الزامی)'
    )
    signed_amount = serializers.SerializerMethodField(
        help_text='مبلغ با علامت (مثبت برای receipt، منفی برای return) (فقط خواندنی)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='توضیحات تکمیلی درباره تراکنش تنخواه. (اختیاری)'
    )
    receipt_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='شماره فیش یا رسید تراکنش. (اختیاری)'
    )
    date_shamsi = serializers.SerializerMethodField(
        help_text='تاریخ شمسی برای نمایش (فقط خواندنی)'
    )
    date_shamsi_input = serializers.CharField(
        write_only=True,
        required=False,
        help_text='تاریخ شمسی به فرمت YYYY-MM-DD برای دریافت از frontend. (اختیاری)'
    )
    date_gregorian = serializers.DateField(
        read_only=True,
        help_text='تاریخ میلادی تراکنش (فقط خواندنی - محاسبه شده)'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان ایجاد تراکنش (فقط خواندنی)'
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text='تاریخ و زمان آخرین به‌روزرسانی تراکنش (فقط خواندنی)'
    )
  
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
            'date_shamsi_input',
            'date_gregorian',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'date_gregorian', 'project']
  
    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_signed_amount(self, obj):
        """مبلغ با علامت"""
        return float(obj.get_signed_amount())

    @extend_schema_field(OpenApiTypes.STR)
    def get_date_shamsi(self, obj):
        """تبدیل تاریخ میلادی به شمسی برای نمایش"""
        if obj.date_shamsi:
            return str(obj.date_shamsi)
        elif obj.date_gregorian:
            from jdatetime import datetime as jdatetime
            jdate = jdatetime.fromgregorian(date=obj.date_gregorian)
            return jdate.strftime('%Y-%m-%d')
        return None
    
    def create(self, validated_data):
        # تبدیل تاریخ شمسی به میلادی
        from jdatetime import datetime as jdatetime
        
        date_shamsi_input = validated_data.pop('date_shamsi_input', None)
        if date_shamsi_input:
            jdate = jdatetime.strptime(str(date_shamsi_input), '%Y-%m-%d')
            validated_data['date_gregorian'] = jdate.togregorian().date()
            validated_data['date_shamsi'] = jdate.date()
        
        # تنظیم پروژه جاری از session
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError({"project": "فیلد project الزامی است."})
        
        current_project = ProjectManager.get_current_project(request)
        if not current_project:
            raise serializers.ValidationError({"project": "هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."})
        validated_data['project'] = current_project
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # تبدیل تاریخ شمسی به میلادی
        from jdatetime import datetime as jdatetime
        
        date_shamsi_input = validated_data.pop('date_shamsi_input', None)
        if date_shamsi_input:
            jdate = jdatetime.strptime(str(date_shamsi_input), '%Y-%m-%d')
            validated_data['date_gregorian'] = jdate.togregorian().date()
            validated_data['date_shamsi'] = jdate.date()
        
        # project در read_only_fields است، پس از instance.project استفاده می‌شود
        # اما اگر instance.project نباشد، از session استفاده می‌کنیم
        if not instance.project:
            request = self.context.get('request')
            if request:
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    validated_data['project'] = current_project
        
        return super().update(instance, validated_data)

