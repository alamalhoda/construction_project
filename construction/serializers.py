from rest_framework import serializers

from . import models


class PeriodSerializer(serializers.ModelSerializer):

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
        # اگر project ارسال نشده، از پروژه فعال استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            active_project = models.Project.get_active_project()
            if not active_project:
                raise serializers.ValidationError({"project": "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."})
            validated_data['project'] = active_project
        
        return super().create(validated_data)

class ExpenseSerializer(serializers.ModelSerializer):
    period_data = PeriodSerializer(source='period', read_only=True)
    period_weight = serializers.SerializerMethodField()

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

    def get_period_weight(self, obj):
        """دریافت وزن دوره"""
        if obj.period:
            return obj.period.weight
        return 0
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه فعال استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            active_project = models.Project.get_active_project()
            if not active_project:
                raise serializers.ValidationError({"project": "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."})
            validated_data['project'] = active_project
        
        return super().create(validated_data)

class InvestorSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()

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
            "created_at",
        ]
    
    def get_units(self, obj):
        """دریافت اطلاعات کامل واحدها"""
        from .serializers import UnitSerializer
        return UnitSerializer(obj.units.all(), many=True).data
    
    def create(self, validated_data):
        # اگر project ارسال نشده، از پروژه فعال استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            active_project = models.Project.get_active_project()
            if not active_project:
                raise serializers.ValidationError({"project": "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."})
            validated_data['project'] = active_project
        
        return super().create(validated_data)

class UnitSerializer(serializers.ModelSerializer):

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
        # اگر project ارسال نشده، از پروژه فعال استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            active_project = models.Project.get_active_project()
            if not active_project:
                raise serializers.ValidationError({"project": "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."})
            validated_data['project'] = active_project
        
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = [
            "id",
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
            "is_active",
            "total_infrastructure",
            "correction_factor",
            "construction_contractor_percentage",
            "created_at",
            "updated_at",
        ]

class SaleSerializer(serializers.ModelSerializer):
    project_data = ProjectSerializer(source='project', read_only=True)
    period_data = PeriodSerializer(source='period', read_only=True)

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
        # اگر project ارسال نشده، از پروژه فعال استفاده کن
        if 'project' not in validated_data or validated_data.get('project') is None:
            active_project = models.Project.get_active_project()
            if not active_project:
                raise serializers.ValidationError({"project": "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."})
            validated_data['project'] = active_project
        
        return super().create(validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    # فیلدهای محاسبه شده - فقط برای خواندن
    date_gregorian = serializers.DateField(read_only=True)
    day_remaining = serializers.IntegerField(read_only=True)
    day_from_start = serializers.IntegerField(read_only=True)
    
    # فیلد date_shamsi برای نمایش (تبدیل میلادی به شمسی)
    date_shamsi = serializers.SerializerMethodField()
    
    # فیلد date_shamsi_input برای دریافت از frontend
    date_shamsi_input = serializers.CharField(write_only=True, required=False)
    
    # فیلد date_shamsi_raw برای دریافت مستقیم از frontend
    date_shamsi_raw = serializers.CharField(write_only=True, required=False)
    
    # فیلدهای foreign key برای نوشتن
    investor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # project_id حذف شد چون خودکار از پروژه فعال تنظیم می‌شود
    period_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # فیلدهای alternative برای frontend (write_only)
    investor = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # project حذف شد چون خودکار از پروژه فعال تنظیم می‌شود
    period = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
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
    
    def get_date_shamsi(self, obj):
        """تبدیل تاریخ میلادی به شمسی برای نمایش"""
        if obj.date_gregorian:
            from jdatetime import datetime as jdatetime
            # تبدیل تاریخ میلادی به شمسی
            jdate = jdatetime.fromgregorian(date=obj.date_gregorian)
            return jdate.strftime('%Y-%m-%d')
        return None
    
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
        
        # تنظیم پروژه فعال خودکار
        active_project = models.Project.get_active_project()
        if not active_project:
            raise serializers.ValidationError("هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید.")
        validated_data['project_id'] = active_project.id
        
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
        
        # تنظیم پروژه فعال خودکار (فقط اگر پروژه تغییر کرده باشد)
        if 'project_id' in validated_data or 'project' in validated_data:
            active_project = models.Project.get_active_project()
            if not active_project:
                raise serializers.ValidationError("هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید.")
            validated_data['project_id'] = active_project.id
        
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

class InterestRateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(),
        required=False,
        allow_null=True,
        help_text="پروژه (در صورت خالی بودن، از پروژه پیش‌فرض استفاده می‌شود)"
    )
    effective_date = serializers.CharField(
        write_only=True,
        help_text="تاریخ شمسی به فرمت YYYY-MM-DD"
    )
    effective_date_display = serializers.SerializerMethodField(
        read_only=True,
        help_text="تاریخ شمسی برای نمایش"
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
            # استفاده از get_active_project() که مستقیماً instance برمی‌گرداند
            project = models.Project.get_active_project()
            if not project:
                raise serializers.ValidationError({"project": "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."})
        elif not isinstance(project, models.Project):
            # اگر project یک instance نیست، آن را تبدیل کن
            try:
                project = models.Project.objects.get(id=int(project))
            except (models.Project.DoesNotExist, ValueError, TypeError):
                # در صورت خطا، از پروژه فعال استفاده کن
                project = models.Project.get_active_project()
                if not project:
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

    def get_effective_date_display(self, obj):
        """نمایش تاریخ شمسی برای frontend"""
        if obj.effective_date:
            return str(obj.effective_date)
        return None

