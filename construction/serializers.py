from rest_framework import serializers

from . import models


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Expense
        fields = [
            "expense_type",
            "amount",
            "description",
            "created_at",
        ]

class InvestorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Investor
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "created_at",
        ]

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
        ]

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
            "created_at",
            "updated_at",
        ]

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
    project_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    period_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # فیلدهای alternative برای frontend (write_only)
    investor = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project = serializers.IntegerField(write_only=True, required=False, allow_null=True)
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
            "project", 
            "period",
            "investor_id",
            "project_id",
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
        
        # اگر project_id وجود دارد، از آن استفاده کن
        if 'project_id' in validated_data:
            validated_data['project_id'] = validated_data.pop('project_id')
        # اگر project وجود دارد، آن را به project_id تبدیل کن
        elif 'project' in validated_data:
            validated_data['project_id'] = validated_data.pop('project')
        
        # اگر period_id وجود دارد، از آن استفاده کن
        if 'period_id' in validated_data:
            validated_data['period_id'] = validated_data.pop('period_id')
        # اگر period وجود دارد، آن را به period_id تبدیل کن
        elif 'period' in validated_data:
            validated_data['period_id'] = validated_data.pop('period')
        
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
        
        # اگر project_id وجود دارد، از آن استفاده کن
        if 'project_id' in validated_data:
            validated_data['project_id'] = validated_data.pop('project_id')
        # اگر project وجود دارد، آن را به project_id تبدیل کن
        elif 'project' in validated_data:
            validated_data['project_id'] = validated_data.pop('project')
        
        # اگر period_id وجود دارد، از آن استفاده کن
        if 'period_id' in validated_data:
            validated_data['period_id'] = validated_data.pop('period_id')
        # اگر period وجود دارد، آن را به period_id تبدیل کن
        elif 'period' in validated_data:
            validated_data['period_id'] = validated_data.pop('period')
        
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

    class Meta:
        model = models.InterestRate
        fields = [
            "id",
            "rate",
            "effective_date",
            "effective_date_gregorian",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Unit
        fields = [
            "id",
            "name",
            "area",
            "price_per_meter",
            "total_price",
            "created_at",
        ]
