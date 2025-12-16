from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.db.models import Sum, Q, Count
from django.db import connection
import logging
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from . import serializers
from . import models
from . import calculations
from .calculations import InvestorCalculations
from .api_security import APISecurityPermission, ReadOnlyPermission, AdminOnlyPermission, JWTAuthentication
from .mixins import ProjectFilterMixin

# ایجاد logger برای API
logger = logging.getLogger('construction.api')


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication که CSRF را بر اساس محیط (DEBUG/Production) مدیریت می‌کند
    
    - در محیط DEBUG: CSRF را نادیده می‌گیرد (برای سهولت توسعه)
    - در محیط Production: CSRF را اعمال می‌کند (برای امنیت)
    """
    def enforce_csrf(self, request):
        from django.conf import settings
        
        # در محیط DEBUG، CSRF را نادیده بگیر
        if settings.DEBUG:
            return  # CSRF را نادیده بگیر در development
        
        # در محیط Production، CSRF را اعمال کن
        # اما به جای استفاده از enforce_csrf که ممکن است مشکل ایجاد کند،
        # از parent class استفاده می‌کنیم که CSRF را به صورت صحیح مدیریت می‌کند
        return super().enforce_csrf(request)


class CsrfExemptSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    OpenAPI schema extension برای CsrfExemptSessionAuthentication
    """
    target_class = 'construction.api.CsrfExemptSessionAuthentication'
    name = 'SessionAuthentication'
    
    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid',
            'description': 'Session-based authentication (CSRF exempt in DEBUG mode)'
        }


# Authentication classes مشترک برای همه viewsets
# شامل JWT Authentication برای پشتیبانی از دستیار هوشمند
DEFAULT_AUTHENTICATION_CLASSES = [
    JWTAuthentication,  # اولویت اول: JWT برای دستیار هوشمند
    CsrfExemptSessionAuthentication,
    TokenAuthentication
]


class ExpenseViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت هزینه‌های پروژه
    
    این ViewSet امکان مدیریت کامل هزینه‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌ها
    - دریافت آمار و گزارش‌های مالی
    - محاسبه مجموع هزینه‌ها بر اساس نوع و دوره
    - مدیریت هزینه‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت هزینه‌های مواد اولیه (material)
    - ثبت هزینه‌های نیروی کار (labor)
    - ثبت هزینه‌های اداری و عمومی (administrative)
    - دریافت گزارش‌های مالی برای تحلیل پروژه
    - محاسبه هزینه‌های تجمعی برای هر دوره
    
    مثال‌های کاربرد:
    - برای ثبت خرید سیمان و آجر: expense_type='material', amount='5000000'
    - برای ثبت حقوق کارگران: expense_type='labor', amount='3000000'
    - برای دریافت لیست تمام هزینه‌ها: GET /api/v1/Expense/
    - برای دریافت آمار هزینه‌ها: GET /api/v1/Expense/dashboard_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها می‌توانند به یک دوره خاص مرتبط باشند
    - انواع هزینه: project_manager, facilities_manager, procurement, warehouse, construction_contractor, other
    """

    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام هزینه‌های پروژه جاری

        این متد لیست هزینه‌های مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی با پیشوند "-" برای نزولی (پیش‌فرض: -created_at)

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Expense/?page=1&page_size=20&ordering=-amount

        نکات:
            - فقط هزینه‌های پروژه جاری برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد هزینه جدید برای پروژه جاری

        این متد هزینه جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - period (الزامی): شناسه دوره متعلق به پروژه جاری
            - expense_type (الزامی): نوع هزینه (project_manager, facilities_manager, procurement, warehouse, construction_contractor, other)
            - amount (الزامی): مبلغ هزینه به تومان (به صورت string)
            - description (اختیاری): توضیحات تکمیلی

        Returns:
            Response با اطلاعات هزینه ایجاد شده (status 201)

        مثال:
            POST /api/v1/Expense/
            {
                "period": 1,
                "expense_type": "project_manager",
                "amount": "5000000",
                "description": "حقوق مدیر پروژه برای ماه دسامبر"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک هزینه خاص

        این متد اطلاعات کامل هزینه با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای هزینه

        Returns:
            Response با اطلاعات کامل هزینه شامل period_data و period_weight

        مثال:
            GET /api/v1/Expense/1/

        نکات:
            - فقط هزینه‌های پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل هزینه

        این متد امکان تغییر همه فیلدهای یک هزینه را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای هزینه

        Request Body:
            - تمام فیلدهای قابل ویرایش (period, expense_type, amount, description)

        Returns:
            Response با اطلاعات به‌روزرسانی شده هزینه (status 200)

        مثال:
            PUT /api/v1/Expense/1/
            {
                "period": 1,
                "expense_type": "project_manager",
                "amount": "6000000",
                "description": "حقوق مدیر پروژه - به‌روزرسانی شده"
            }

        نکات:
            - همه فیلدها باید ارسال شوند (به جز project که خودکار تنظیم می‌شود)
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی هزینه

        این متد امکان تغییر بخشی از فیلدهای هزینه را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای هزینه

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی (period, expense_type, amount, description)

        Returns:
            Response با اطلاعات به‌روزرسانی شده هزینه (status 200)

        مثال:
            PATCH /api/v1/Expense/1/
            {
                "amount": "7000000"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف هزینه

        این متد هزینه را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای هزینه

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Expense/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط هزینه‌های پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
            - در صورت وجود وابستگی، ممکن است حذف ناموفق باشد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def with_periods(self, request):
        """دریافت هزینه‌ها با اطلاعات دوره‌ها برای محاسبه دوره متوسط ساخت"""
        logger.info("User %s requesting expenses with periods", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                logger.warning("No active project found for user %s in with_periods", request.user.username)
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام هزینه‌ها برای پروژه فعال با اطلاعات دوره
            expenses = models.Expense.objects.filter(
                project=active_project
            ).select_related('period')  # لیست هزینه‌های پروژه فعال با اطلاعات دوره

            # بررسی آمار دوره‌ها
            total_expenses = expenses.count()  # تعداد کل هزینه‌ها
            expenses_with_period = expenses.exclude(period__isnull=True).count()  # تعداد هزینه‌های دارای دوره
            expenses_without_period = expenses.filter(period__isnull=True).count()  # تعداد هزینه‌های بدون دوره

            # استفاده از serializer مخصوص
            serializer = serializers.ExpenseSerializer(expenses, many=True)  # سریالایزر هزینه‌ها
            
            logger.info("Successfully returned %d expenses with periods for user %s (project: %s)", 
                       total_expenses, request.user.username, active_project.name)
            return Response({
                'expenses': serializer.data,
                'total_count': total_expenses,
                'expenses_with_period': expenses_with_period,
                'expenses_without_period': expenses_without_period,
                'active_project': active_project.name
            })

        except Exception as e:
            logger.exception("Error in with_periods for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت داده‌ها: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """
        دریافت داده‌های لیست هزینه‌ها
        
        این endpoint داده‌های کامل داشبورد هزینه‌ها را بر اساس دوره‌ها و انواع هزینه
        برمی‌گرداند. شامل:
        - لیست تمام دوره‌ها با هزینه‌های هر نوع
        - مجموع تجمعی هزینه‌ها
        - مجموع هر ستون (هر نوع هزینه)
        - مجموع کل همه هزینه‌ها
        
        Returns:
            Response: شامل:
                - periods: لیست دوره‌ها با هزینه‌های هر نوع
                - expense_types: انواع هزینه‌ها
                - column_totals: مجموع هر نوع هزینه در تمام دوره‌ها
                - grand_total: مجموع کل همه هزینه‌ها
        
        نکات مهم:
        - فقط هزینه‌های پروژه جاری را برمی‌گرداند
        - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
        - داده‌ها بر اساس دوره مرتب می‌شوند
        """
        logger.info("User %s requesting expense dashboard data", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام دوره‌ها از مرداد 1402 تا مرداد 1405
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')  # لیست دوره‌ها از سال 1402 تا 1405

            # دریافت تمام هزینه‌ها برای پروژه فعال
            expenses = models.Expense.objects.filter(project=active_project)  # لیست هزینه‌های پروژه فعال

            # ساختار داده‌ها
            expense_types = [  # انواع هزینه‌ها
                ('project_manager', 'مدیر پروژه'),
                ('facilities_manager', 'سرپرست کارگاه'),
                ('procurement', 'کارپرداز'),
                ('warehouse', 'انباردار'),
                ('construction_contractor', 'پیمان ساختمان'),
                ('other', 'سایر'),
            ]

            # ایجاد ماتریس داده‌ها
            dashboard_data = []  # داده‌های داشبورد
            cumulative_total = 0  # مجموع تجمعی کل

            for period in periods:
                period_data = {
                    'period_id': period.id,  # شناسه دوره
                    'period_label': period.label,  # برچسب دوره
                    'year': period.year,  # سال دوره
                    'month_name': period.month_name,  # نام ماه دوره
                    'is_current_period': period.is_current(),  # آیا دوره جاری است
                    'expenses': {},  # هزینه‌های دوره
                    'period_total': 0,  # مجموع هزینه‌های دوره
                    'cumulative_total': 0  # مجموع تجمعی تا این دوره
                }

                # محاسبه هزینه‌های هر نوع برای این دوره
                for expense_type, expense_label in expense_types:
                    expense_amount = expenses.filter(
                        period=period,
                        expense_type=expense_type
                    ).aggregate(total=Sum('amount'))['total'] or 0  # مبلغ هزینه این نوع برای این دوره

                    # دریافت توضیحات هزینه - ابتدا رکورد دستی
                    expense_obj = expenses.filter(
                        period=period,
                        expense_type=expense_type
                    ).exclude(
                        description__icontains='محاسبه خودکار'
                    ).first()  # رکورد دستی هزینه
                    
                    # اگر رکورد دستی نباشد، رکورد خودکار را بردار
                    if not expense_obj:
                        expense_obj = expenses.filter(
                            period=period,
                            expense_type=expense_type
                        ).first()  # رکورد خودکار هزینه
                    
                    period_data['expenses'][expense_type] = {
                        'amount': float(expense_amount),  # مبلغ هزینه
                        'label': expense_label,  # برچسب هزینه
                        'description': expense_obj.description if expense_obj else '',  # توضیحات هزینه
                        'expense_id': expense_obj.id if expense_obj else None  # شناسه هزینه
                    }
                    period_data['period_total'] += float(expense_amount)

                # محاسبه مجموع تجمیعی
                cumulative_total += period_data['period_total']  # افزودن به مجموع تجمعی
                period_data['cumulative_total'] = cumulative_total  # ذخیره مجموع تجمعی

                dashboard_data.append(period_data)

            # محاسبه مجموع ستون‌ها
            column_totals = {}  # مجموع هر ستون (هر نوع هزینه)
            for expense_type, _ in expense_types:
                column_totals[expense_type] = sum(
                    period['expenses'][expense_type]['amount'] 
                    for period in dashboard_data
                )  # مجموع هزینه‌های این نوع در تمام دوره‌ها

            # مجموع کل
            grand_total = sum(period['period_total'] for period in dashboard_data)  # مجموع کل همه هزینه‌ها

            logger.info("Successfully returned dashboard data for user %s (project: %s, periods: %d)", 
                       request.user.username, active_project.name, len(dashboard_data))
            return Response({
                'success': True,
                'data': {
                    'periods': dashboard_data,
                    'expense_types': expense_types,
                    'column_totals': column_totals,
                    'grand_total': grand_total,
                    'project_name': active_project.name
                }
            })

        except Exception as e:
            logger.exception("Error in dashboard_data for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت داده‌ها: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['post'])
    def update_expense(self, request):
        """
        به‌روزرسانی یا ایجاد هزینه برای یک دوره و نوع خاص
        
        این endpoint امکان به‌روزرسانی یا ایجاد هزینه برای یک دوره و نوع خاص را فراهم می‌کند.
        اگر هزینه وجود داشته باشد، به‌روزرسانی می‌شود؛ در غیر این صورت ایجاد می‌شود.
        
        Parameters:
            period_id (int): شناسه دوره
            expense_type (str): نوع هزینه (project_manager, facilities_manager, ...)
            amount (float/str): مبلغ هزینه
            description (str, optional): توضیحات هزینه
        
        Returns:
            Response: شامل:
                - success: وضعیت موفقیت
                - message: پیام پاسخ
                - data: شامل expense_id, amount, description, created
        
        نکات مهم:
        - هزینه بر اساس پروژه جاری (active project) از session شناسایی می‌شود
        - اگر هزینه وجود داشته باشد، به‌روزرسانی می‌شود؛ در غیر این صورت ایجاد می‌شود
        - مبلغ باید به صورت string ارسال شود تا از مشکلات precision جلوگیری شود
        - نیاز به احراز هویت دارد (IsAuthenticated)
        """
        logger.info("User %s updating expense", request.user.username)
        try:
            period_id = request.data.get('period_id')  # شناسه دوره
            expense_type = request.data.get('expense_type')  # نوع هزینه
            amount = request.data.get('amount')  # مبلغ هزینه
            description = request.data.get('description', '')  # توضیحات هزینه

            if not all([period_id, expense_type, amount is not None]):
                return Response({
                    'error': 'پارامترهای مورد نیاز ارسال نشده است'
                }, status=400)

            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت دوره
            try:
                period = models.Period.objects.get(id=period_id, project=active_project)  # دوره مورد نظر
            except models.Period.DoesNotExist:
                return Response({
                    'error': 'دوره مورد نظر یافت نشد'
                }, status=404)

            # تبدیل amount به Decimal
            from decimal import Decimal
            amount = Decimal(str(amount))  # مبلغ به صورت Decimal

            # یافتن یا ایجاد هزینه
            expense, created = models.Expense.objects.get_or_create(
                project=active_project,
                period=period,
                expense_type=expense_type,
                defaults={'amount': amount, 'description': description}
            )  # هزینه (expense) و وضعیت ایجاد (created)

            if not created:
                expense.amount = amount
                expense.description = description
                expense.save()
                logger.info("Expense %d updated by user %s (amount: %s)", expense.id, request.user.username, amount)
            else:
                logger.info("Expense %d created by user %s (amount: %s)", expense.id, request.user.username, amount)

            return Response({
                'success': True,
                'message': 'هزینه با موفقیت به‌روزرسانی شد',
                'data': {
                    'expense_id': expense.id,
                    'amount': float(expense.amount),
                    'description': expense.description,
                    'created': created
                }
            })

        except Exception as e:
            logger.exception("Error updating expense for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در به‌روزرسانی هزینه: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_expense_details(self, request):
        """دریافت جزئیات هزینه برای ویرایش"""
        logger.debug("User %s requesting expense details", request.user.username)
        try:
            period_id = request.query_params.get('period_id')  # شناسه دوره از پارامترهای درخواست
            expense_type = request.query_params.get('expense_type')  # نوع هزینه از پارامترهای درخواست

            if not all([period_id, expense_type]):
                return Response({
                    'error': 'پارامترهای مورد نیاز ارسال نشده است'
                }, status=400)

            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت دوره
            try:
                period = models.Period.objects.get(id=period_id, project=active_project)  # دوره مورد نظر
            except models.Period.DoesNotExist:
                return Response({
                    'error': 'دوره مورد نظر یافت نشد'
                }, status=404)

            # یافتن هزینه - ابتدا رکورد دستی (بدون توضیحات خودکار)
            manual_expense = models.Expense.objects.filter(
                project=active_project,
                period=period,
                expense_type=expense_type
            ).exclude(
                description__icontains='محاسبه خودکار'
            ).first()  # هزینه دستی (بدون محاسبه خودکار)
            
            if manual_expense:
                expense = manual_expense  # استفاده از هزینه دستی
            else:
                # اگر رکورد دستی نباشد، رکورد خودکار را بردار
                expense = models.Expense.objects.filter(
                    project=active_project,
                    period=period,
                    expense_type=expense_type
                ).first()  # هزینه خودکار
            
            if expense:
                return Response({
                    'success': True,
                    'data': {
                        'amount': float(expense.amount),
                        'description': expense.description or '',
                        'expense_id': expense.id,
                        'is_manual': not ('محاسبه خودکار' in (expense.description or ''))
                    }
                })
            else:
                return Response({
                    'success': True,
                    'data': {
                        'amount': 0,
                        'description': '',
                        'expense_id': None,
                        'is_manual': True
                    }
                })

        except Exception as e:
            logger.exception("Error getting expense details for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت جزئیات هزینه: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def total_expenses(self, request):
        """دریافت مجموع کل هزینه‌های پروژه"""
        logger.info("User %s requesting total expenses", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            if project_id:
                try:
                    project = models.Project.objects.get(id=project_id)  # پروژه با شناسه مشخص شده
                    expenses = models.Expense.objects.filter(project=project)  # هزینه‌های این پروژه
                except models.Project.DoesNotExist:
                    return Response({
                        'error': f'پروژه با شناسه {project_id} یافت نشد'
                    }, status=404)
            else:
                # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
                from construction.project_manager import ProjectManager
                active_project = ProjectManager.get_current_project(request)  # پروژه جاری
                if not active_project:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=404)
                expenses = models.Expense.objects.filter(project=active_project)  # هزینه‌های پروژه جاری
                project = active_project  # استفاده از پروژه جاری
            
            # محاسبه مجموع کل هزینه‌ها (مرجع واحد)
            total_amount = models.Expense.objects.project_totals(project)  # مجموع کل هزینه‌های پروژه
            
            # محاسبه تعداد هزینه‌ها
            total_count = expenses.count()  # تعداد کل هزینه‌ها
            
            # محاسبه مجموع هزینه‌ها بر اساس نوع
            expenses_by_type = {}  # هزینه‌ها به تفکیک نوع
            for expense_type, display_name in models.Expense.EXPENSE_TYPES:
                type_expenses = expenses.filter(expense_type=expense_type)  # هزینه‌های این نوع
                type_total = sum(expense.amount for expense in type_expenses)  # مجموع هزینه‌های این نوع
                type_count = type_expenses.count()  # تعداد هزینه‌های این نوع
                
                if type_total > 0 or type_count > 0:
                    expenses_by_type[expense_type] = {
                        'display_name': display_name,  # نام نمایشی نوع هزینه
                        'total_amount': float(type_total),  # مجموع مبلغ این نوع
                        'count': type_count  # تعداد این نوع
                    }
            
            return Response({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name
                },
                'total_expenses': {
                    'total_amount': float(total_amount),
                    'total_count': total_count
                },
                'expenses_by_type': expenses_by_type
            })
                
        except Exception as e:
            logger.exception("Error getting total expenses for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت مجموع هزینه‌ها: {str(e)}'
            }, status=500)


class InvestorViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت سرمایه‌گذاران پروژه
    
    این ViewSet امکان مدیریت کامل سرمایه‌گذاران و مالکان پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف سرمایه‌گذاران
    - دریافت خلاصه مالی سرمایه‌گذاران
    - مدیریت واحدهای مرتبط با هر سرمایه‌گذار
    - مدیریت نوع مشارکت (مالک یا سرمایه‌گذار)
    
    سناریوهای استفاده:
    - ثبت اطلاعات مالکان واحدها
    - ثبت اطلاعات سرمایه‌گذاران
    - دریافت خلاصه مالی سرمایه‌گذاران
    - مدیریت واحدهای هر سرمایه‌گذار
    
    مثال‌های کاربرد:
    - برای ثبت مالک جدید: participation_type='owner', first_name='علی', last_name='احمدی'
    - برای دریافت خلاصه مالی: GET /api/v1/Investor/summary/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - سرمایه‌گذاران می‌توانند مالک چندین واحد باشند
    - انواع مشارکت: owner (مالک), investor (سرمایه‌گذار)
    """

    queryset = models.Investor.objects.all()
    serializer_class = serializers.InvestorSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام سرمایه‌گذاران پروژه جاری

        این متد لیست سرمایه‌گذاران مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی با پیشوند "-" برای نزولی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Investor/?page=1&page_size=20

        نکات:
            - فقط سرمایه‌گذاران پروژه جاری برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد سرمایه‌گذار جدید برای پروژه جاری

        این متد سرمایه‌گذار جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - first_name (الزامی): نام سرمایه‌گذار
            - last_name (الزامی): نام خانوادگی سرمایه‌گذار
            - phone (الزامی): شماره تماس
            - email (اختیاری): آدرس ایمیل
            - participation_type (اختیاری): نوع مشارکت (owner, investor)
            - contract_date_shamsi (اختیاری): تاریخ قرارداد شمسی
            - description (اختیاری): توضیحات

        Returns:
            Response با اطلاعات سرمایه‌گذار ایجاد شده (status 201)

        مثال:
            POST /api/v1/Investor/
            {
                "first_name": "علی",
                "last_name": "احمدی",
                "phone": "09123456789",
                "email": "ali@example.com",
                "participation_type": "owner",
                "description": "مالک واحد 101"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک سرمایه‌گذار خاص

        این متد اطلاعات کامل سرمایه‌گذار با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای سرمایه‌گذار

        Returns:
            Response با اطلاعات کامل سرمایه‌گذار شامل units

        مثال:
            GET /api/v1/Investor/1/

        نکات:
            - فقط سرمایه‌گذاران پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل سرمایه‌گذار

        این متد امکان تغییر همه فیلدهای یک سرمایه‌گذار را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای سرمایه‌گذار

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده سرمایه‌گذار (status 200)

        مثال:
            PUT /api/v1/Investor/1/
            {
                "first_name": "علی",
                "last_name": "احمدی",
                "phone": "09123456789",
                "participation_type": "owner"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی سرمایه‌گذار

        این متد امکان تغییر بخشی از فیلدهای سرمایه‌گذار را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای سرمایه‌گذار

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده سرمایه‌گذار (status 200)

        مثال:
            PATCH /api/v1/Investor/1/
            {
                "phone": "09123456789"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف سرمایه‌گذار

        این متد سرمایه‌گذار را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای سرمایه‌گذار

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Investor/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط سرمایه‌گذاران پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
            - در صورت وجود وابستگی، ممکن است حذف ناموفق باشد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        خلاصه مالی تمام سرمایه‌گذاران پروژه
        
        این endpoint خلاصه مالی تمام سرمایه‌گذاران پروژه جاری را محاسبه و برمی‌گرداند.
        
        خروجی شامل:
        - شناسه و نام هر سرمایه‌گذار
        - نوع مشارکت (مالک یا سرمایه‌گذار)
        - مجموع آورده‌ها
        - مجموع برداشت‌ها
        - سرمایه خالص
        - مجموع سود
        - مجموع کل (سرمایه + سود)
        
        سناریوهای استفاده:
        - نمایش لیست خلاصه تمام سرمایه‌گذاران
        - مقایسه عملکرد سرمایه‌گذاران
        - تهیه گزارش‌های مدیریتی
        - نمایش داشبورد سرمایه‌گذاران
        
        مثال استفاده:
        GET /api/v1/Investor/summary/
        
        مثال خروجی:
        [
            {
                "investor_id": 1,
                "name": "علی احمدی",
                "participation_type": "owner",
                "total_deposits": 100000000,
                "total_withdrawals": 0,
                "net_principal": 100000000,
                "total_profit": 15000000,
                "grand_total": 115000000
            },
            {
                "investor_id": 2,
                "name": "محمد رضایی",
                "participation_type": "investor",
                "total_deposits": 50000000,
                "total_withdrawals": 10000000,
                "net_principal": 40000000,
                "total_profit": 7500000,
                "grand_total": 47500000
            }
        ]
        
        نکات مهم:
        - نتایج بر اساس سرمایه خالص (net_principal) به صورت نزولی مرتب می‌شوند
        - فقط سرمایه‌گذاران پروژه جاری را شامل می‌شود
        - اگر پروژه جاری وجود نداشته باشد، تمام سرمایه‌گذاران را برمی‌گرداند
        - تمام مبالغ به تومان هستند
        """
        try:
            def norm_num(x):  # تابع نرمال‌سازی عدد (حذف اعشار در صورت امکان)
                try:
                    xf = float(x)  # تبدیل به float
                    xi = int(xf)  # تبدیل به int
                    return xi if xf == xi else xf  # برگرداندن int اگر اعشار نداشت، در غیر این صورت float
                except Exception:
                    return x

            # فیلتر بر اساس پروژه جاری
            from construction.project_manager import ProjectManager
            current_project = ProjectManager.get_current_project(request)
            if current_project:
                investors = models.Investor.objects.filter(project=current_project)  # لیست سرمایه‌گذاران پروژه جاری
            else:
                investors = models.Investor.objects.all()  # اگر پروژه جاری نبود، همه را برگردان
            results = []  # لیست نتایج

            for inv in investors:
                # استفاده از پروژه جاری برای فیلتر تراکنش‌ها
                totals = models.Transaction.objects.totals(project=current_project, filters={'investor_id': inv.id})  # محاسبه مجموع تراکنش‌های سرمایه‌گذار
                deposits = float(totals.get('deposits', 0) or 0)  # مجموع آورده‌ها
                withdrawals = float(totals.get('withdrawals', 0) or 0)  # مجموع برداشت‌ها (منفی)
                profits = float(totals.get('profits', 0) or 0)  # مجموع سود

                total_deposits = deposits  # مجموع آورده‌ها
                total_withdrawals_abs = abs(withdrawals)  # مجموع برداشت‌ها (مقدار مثبت)
                net_principal = deposits + withdrawals  # سرمایه خالص (آورده + برداشت که منفی است)
                total_profit = profits  # مجموع سود
                grand_total = net_principal + total_profit  # مجموع کل (سرمایه خالص + سود)

                results.append({
                    'investor_id': inv.id,
                    'name': f"{inv.first_name} {inv.last_name}",
                    'participation_type': inv.participation_type,
                    'total_deposits': norm_num(total_deposits),
                    'total_withdrawals': norm_num(total_withdrawals_abs),
                    'net_principal': norm_num(net_principal),
                    'total_profit': norm_num(total_profit),
                    'grand_total': norm_num(grand_total),
                })

            results.sort(key=lambda x: x['net_principal'], reverse=True)
            logger.info("Successfully returned investor summary for user %s (%d investors)", 
                       request.user.username, len(results))
            return Response(results)
        except Exception as e:
            logger.exception("Error in summary for user %s: %s", request.user.username, e)
            return Response({'error': f'خطا در خلاصه سرمایه‌گذاران: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def summary_ssot(self, request):
        """خلاصه مالی تمام سرمایه‌گذاران با مرجع واحد (بدون SQL خام)"""
        try:
            # فیلتر بر اساس پروژه جاری
            from construction.project_manager import ProjectManager
            current_project = ProjectManager.get_current_project(request)
            if not current_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)
            
            investors = models.Investor.objects.filter(project=current_project)  # لیست سرمایه‌گذاران پروژه جاری
            results = []  # لیست نتایج

            for inv in investors:
                # استفاده از پروژه جاری برای فیلتر تراکنش‌ها
                totals = models.Transaction.objects.totals(project=current_project, filters={'investor_id': inv.id})  # محاسبه مجموع تراکنش‌های سرمایه‌گذار
                deposits = float(totals.get('deposits', 0) or 0)  # مجموع آورده‌ها
                withdrawals = float(totals.get('withdrawals', 0) or 0)  # مجموع برداشت‌ها (منفی است)
                profits = float(totals.get('profits', 0) or 0)  # مجموع سود

                total_deposits = deposits  # مجموع آورده‌ها
                total_withdrawals_abs = abs(withdrawals)  # مجموع برداشت‌ها (مقدار مثبت)
                net_principal = deposits + withdrawals  # سرمایه خالص (آورده + برداشت که منفی است)
                total_profit = profits  # مجموع سود
                grand_total = net_principal + total_profit  # مجموع کل (سرمایه خالص + سود)

                def norm_num(x):  # تابع نرمال‌سازی عدد (حذف اعشار در صورت امکان)
                    xf = float(x)  # تبدیل به float
                    xi = int(xf)  # تبدیل به int
                    return xi if xf == xi else xf  # برگرداندن int اگر اعشار نداشت، در غیر این صورت float

                results.append({
                    'investor_id': inv.id,
                    'name': f"{inv.first_name} {inv.last_name}",
                    'participation_type': inv.participation_type,
                    'total_deposits': norm_num(total_deposits),
                    'total_withdrawals': norm_num(total_withdrawals_abs),
                    'net_principal': norm_num(net_principal),
                    'total_profit': norm_num(total_profit),
                    'grand_total': norm_num(grand_total),
                })

            # مرتب‌سازی مشابه نسخه SQL: بر اساس net_principal نزولی
            results.sort(key=lambda x: x['net_principal'], reverse=True)
            logger.info("Successfully returned investor summary_ssot for user %s (%d investors)", 
                       request.user.username, len(results))
            return Response(results)

        except Exception as e:
            logger.exception("Error in summary_ssot for user %s: %s", request.user.username, e)
            return Response({'error': f'خطا در خلاصه SSOT سرمایه‌گذاران: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def participation_stats(self, request):
        """دریافت آمار مشارکت کنندگان بر اساس نوع (مالک و سرمایه گذار)"""
        
        # فیلتر بر اساس پروژه جاری
        from construction.project_manager import ProjectManager
        current_project = ProjectManager.get_current_project(request)
        
        if current_project:
            investors_queryset = models.Investor.objects.filter(project=current_project)
        else:
            investors_queryset = models.Investor.objects.all()
        
        # شمارش کل مشارکت کنندگان
        total_count = investors_queryset.count()  # تعداد کل سرمایه‌گذاران
        
        # شمارش مشارکت کنندگان بر اساس نوع
        owner_count = investors_queryset.filter(participation_type='owner').count()  # تعداد مالکان
        investor_count = investors_queryset.filter(participation_type='investor').count()  # تعداد سرمایه‌گذاران (غیر مالک)
        
        return Response({
            'total_count': total_count,
            'owner_count': owner_count,
            'investor_count': investor_count
        })

    @action(detail=True, methods=['get'])
    def detailed_statistics(self, request, pk=None):
        """
        دریافت آمار تفصیلی سرمایه‌گذار
        
        این endpoint آمار کامل و تفصیلی برای یک سرمایه‌گذار خاص را محاسبه و برمی‌گرداند.
        شامل اطلاعات مالی، سرمایه، سود، نسبت‌ها و سایر متریک‌های مرتبط.
        
        Parameters:
            pk (int): شناسه سرمایه‌گذار
            project_id (int, optional): شناسه پروژه (از query parameter یا پروژه جاری)
        
        Returns:
            Response: شامل آمار تفصیلی سرمایه‌گذار
        
        مثال Response:
        {
            "total_investment": 50000000,
            "total_profit": 15000000,
            "grand_total": 115000000,
            "ownership_percentage": 25.5,
            "unit_cost": 5000000
        }
        
        نکات مهم:
        - اگر سرمایه‌گذار یافت نشود، خطای 404 برمی‌گرداند
        - محاسبات بر اساس پروژه جاری یا project_id ارسالی انجام می‌شود
        - تمام مبالغ به تومان هستند
        """
        logger.info("User %s requesting detailed statistics for investor %s", request.user.username, pk)
        try:
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            stats = calculations.InvestorCalculations.calculate_investor_statistics(pk, project_id)  # محاسبه آمار تفصیلی سرمایه‌گذار
            
            if 'error' in stats:
                logger.warning("Error in detailed_statistics for investor %s: %s", pk, stats.get('error'))
                return Response(stats, status=400)
            
            logger.info("Successfully returned detailed statistics for investor %s (user: %s)", pk, request.user.username)
            return Response(stats)
            
        except Exception as e:
            logger.exception("Error in detailed_statistics for investor %s (user: %s): %s", pk, request.user.username, e)
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=True, methods=['get'])
    def ratios(self, request, pk=None):
        """دریافت نسبت‌های سرمایه‌گذار"""
        logger.info("User %s requesting ratios for investor %s", request.user.username, pk)
        try:
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            ratios = calculations.InvestorCalculations.calculate_investor_ratios(pk, project_id)  # محاسبه نسبت‌های سرمایه‌گذار
            
            if 'error' in ratios:
                logger.warning("Error in ratios for investor %s: %s", pk, ratios.get('error'))
                return Response(ratios, status=400)
            
            logger.info("Successfully returned ratios for investor %s (user: %s)", pk, request.user.username)
            return Response(ratios)
            
        except Exception as e:
            logger.exception("Error in ratios for investor %s (user: %s): %s", pk, request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه نسبت‌های سرمایه‌گذار: {str(e)}'
            }, status=500)
    
    @action(detail=True, methods=['get'])
    def ownership(self, request, pk=None):
        """
        دریافت مالکیت سرمایه‌گذار به متر مربع
        
        محاسبه: (آورده + سود) / قیمت هر متر مربع واحد انتخابی
        """
        logger.info("User %s requesting ownership for investor %s", request.user.username, pk)
        try:
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            ownership = calculations.InvestorCalculations.calculate_investor_ownership(pk, project_id)  # محاسبه مالکیت سرمایه‌گذار
            
            if 'error' in ownership:
                logger.warning("Error in ownership for investor %s: %s", pk, ownership.get('error'))
                return Response(ownership, status=400)
            
            logger.info("Successfully returned ownership for investor %s (user: %s)", pk, request.user.username)
            return Response(ownership)
            
        except Exception as e:
            logger.exception("Error in ownership for investor %s (user: %s): %s", pk, request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه مالکیت سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=True, methods=['get'])
    def investor_cumulative_capital_and_unit_cost_chart(self, request, pk=None):
        """
        دریافت داده‌های نمودار ترند سرمایه موجود و هزینه واحد برای سرمایه‌گذار
        
        این endpoint داده‌های لازم برای نمودار ترند را محاسبه می‌کند:
        - سرمایه موجود تجمعی به میلیون تومان
        - هزینه واحد به میلیون تومان برای هر دوره
        """
        logger.info("User %s requesting trend chart for investor %s", request.user.username, pk)
        try:
            # دریافت project_id از query parameter یا از پروژه جاری از session
            project_id = request.query_params.get('project_id')
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            trend_data = calculations.InvestorCalculations.calculate_investor_trend_chart(pk, project_id)  # محاسبه داده‌های نمودار ترند سرمایه‌گذار
            
            if 'error' in trend_data:
                logger.warning("Error in trend chart for investor %s: %s", pk, trend_data.get('error'))
                return Response(trend_data, status=400)
            
            logger.info("Successfully returned trend chart for investor %s (user: %s)", pk, request.user.username)
            return Response(trend_data)
            
        except Exception as e:
            logger.exception("Error in trend chart for investor %s (user: %s): %s", pk, request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه داده‌های نمودار ترند سرمایه‌گذار: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def all_investors_summary(self, request):
        """
        دریافت خلاصه آمار تمام سرمایه‌گذاران
        
        این endpoint از سرویس محاسباتی InvestorCalculations استفاده می‌کند
        تا آمار کامل شامل نسبت‌های سرمایه، سود و شاخص نفع را ارائه دهد.
        """
        logger.info("User %s requesting all investors summary", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # تبدیل project_id به عدد در صورت وجود
            if project_id:
                project_id = int(project_id)  # تبدیل به عدد صحیح
            else:
                # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            # استفاده از تابع محاسباتی برای دریافت خلاصه سرمایه‌گذاران
            summary = InvestorCalculations.get_all_investors_summary(project_id)  # دریافت خلاصه تمام سرمایه‌گذاران
            
            if not summary:
                logger.warning("No investors summary found for user %s", request.user.username)
                return Response({
                    'error': 'هیچ سرمایه‌گذاری یافت نشد یا پروژه فعالی وجود ندارد'
                }, status=404)
            
            logger.info("Successfully returned all investors summary for user %s (%d investors)", 
                       request.user.username, len(summary) if isinstance(summary, list) else 0)
            return Response(summary)
            
        except ValueError as e:
            logger.warning("Invalid project_id in all_investors_summary for user %s: %s", request.user.username, e)
            return Response({
                'error': 'شناسه پروژه نامعتبر است'
            }, status=400)
        except Exception as e:
            logger.exception("Error in all_investors_summary for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت خلاصه سرمایه‌گذاران: {str(e)}'
            }, status=500)


class ComprehensiveAnalysisViewSet(viewsets.ViewSet):
    """ViewSet for comprehensive project analysis"""
    
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]
    
    @extend_schema(
        summary='تحلیل جامع پروژه',
        description='دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی',
        parameters=[
            OpenApiParameter(
                name='project_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='شناسه پروژه (اختیاری - اگر مشخص نشود از پروژه جاری استفاده می‌شود)',
                required=False
            )
        ],
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'description': 'تحلیل جامع پروژه شامل تمام محاسبات مالی'
                },
                description='تحلیل جامع پروژه'
            ),
            400: OpenApiResponse(
                response={'type': 'object', 'properties': {'error': {'type': 'string'}}},
                description='خطا در دریافت تحلیل (پروژه یافت نشد یا شناسه نامعتبر)'
            ),
            500: OpenApiResponse(
                response={'type': 'object', 'properties': {'error': {'type': 'string'}}},
                description='خطا در دریافت تحلیل جامع'
            )
        },
        tags=['Analysis']
    )
    @action(detail=False, methods=['get'])
    def comprehensive_analysis(self, request):
        """
        دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی
        
        این endpoint تحلیل کامل و جامع پروژه را با تمام محاسبات مالی
        شامل سرمایه، سود، هزینه‌ها، فروش‌ها و سایر متریک‌های مرتبط برمی‌گرداند.
        
        Parameters:
            project_id (int, optional): شناسه پروژه (از query parameter یا پروژه جاری)
        
        Returns:
            Response: شامل تحلیل جامع پروژه
        
        نکات مهم:
        - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
        - تمام محاسبات بر اساس داده‌های واقعی انجام می‌شود
        - مبالغ به تومان هستند
        """
        logger.info("User %s requesting comprehensive analysis", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            # تبدیل project_id به عدد
            project_id = int(project_id)  # تبدیل به عدد صحیح
            
            # استفاده از تابع محاسباتی برای دریافت تحلیل جامع
            from .calculations import ComprehensiveCalculations
            analysis = ComprehensiveCalculations.get_comprehensive_project_analysis(project_id)  # دریافت تحلیل جامع پروژه
            
            if 'error' in analysis:
                logger.warning("Error in comprehensive_analysis: %s", analysis.get('error'))
                return Response(analysis, status=400)
            
            logger.info("Successfully returned comprehensive analysis for user %s", request.user.username)
            return Response(analysis)
            
        except ValueError as e:
            logger.warning("Invalid project_id in comprehensive_analysis for user %s: %s", request.user.username, e)
            return Response({
                'error': 'شناسه پروژه نامعتبر است'
            }, status=400)
        except Exception as e:
            logger.exception("Error in comprehensive_analysis for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت تحلیل جامع: {str(e)}'
            }, status=500)


class PeriodViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت دوره‌های زمانی پروژه
    
    این ViewSet امکان مدیریت کامل دوره‌های ماهانه پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف دوره‌ها
    - دریافت داده‌های دوره‌ای برای نمودارها
    - مدیریت وزن دوره‌ها برای محاسبات مالی
    - مرتب‌سازی دوره‌ها بر اساس سال و ماه
    
    سناریوهای استفاده:
    - تعریف دوره‌های ماهانه پروژه
    - تنظیم وزن دوره‌ها برای محاسبات
    - دریافت داده‌های نمودار برای تحلیل مالی
    - مدیریت تاریخ‌های شمسی و میلادی
    
    مثال‌های کاربرد:
    - برای ایجاد دوره جدید: label='مهر 1403', year=1403, month_number=7
    - برای دریافت داده‌های نمودار: GET /api/v1/Period/chart_data/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هر دوره باید یکتا باشد (project, year, month_number)
    - وزن دوره برای محاسبات مالی مهم است
    """

    queryset = models.Period.objects.all().order_by('-year', '-month_number')
    serializer_class = serializers.PeriodSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام دوره‌های پروژه جاری

        این متد لیست دوره‌های مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت مرتب شده بر اساس سال و ماه (نزولی) هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Period/?page=1&page_size=12

        نکات:
            - فقط دوره‌های پروژه جاری برگردانده می‌شود
            - دوره‌ها به صورت نزولی (جدیدترین اول) مرتب می‌شوند
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد دوره جدید برای پروژه جاری

        این متد دوره جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - label (الزامی): عنوان دوره
            - year (الزامی): سال شمسی
            - month_number (الزامی): شماره ماه (1-12)
            - month_name (الزامی): نام ماه
            - weight (الزامی): وزن دوره
            - start_date_shamsi (الزامی): تاریخ شروع شمسی
            - end_date_shamsi (الزامی): تاریخ پایان شمسی
            - start_date_gregorian (الزامی): تاریخ شروع میلادی
            - end_date_gregorian (الزامی): تاریخ پایان میلادی

        Returns:
            Response با اطلاعات دوره ایجاد شده (status 201)

        مثال:
            POST /api/v1/Period/
            {
                "label": "مهر 1403",
                "year": 1403,
                "month_number": 7,
                "month_name": "مهر",
                "weight": 1,
                "start_date_shamsi": "1403-07-01",
                "end_date_shamsi": "1403-07-29",
                "start_date_gregorian": "2024-09-22",
                "end_date_gregorian": "2024-10-20"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - هر ترکیب (project, year, month_number) باید یکتا باشد
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک دوره خاص

        این متد اطلاعات کامل دوره با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای دوره

        Returns:
            Response با اطلاعات کامل دوره

        مثال:
            GET /api/v1/Period/1/

        نکات:
            - فقط دوره‌های پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل دوره

        این متد امکان تغییر همه فیلدهای یک دوره را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای دوره

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده دوره (status 200)

        مثال:
            PUT /api/v1/Period/1/
            {
                "label": "مهر 1403",
                "year": 1403,
                "month_number": 7,
                "weight": 2
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی دوره

        این متد امکان تغییر بخشی از فیلدهای دوره را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای دوره

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده دوره (status 200)

        مثال:
            PATCH /api/v1/Period/1/
            {
                "weight": 2
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف دوره

        این متد دوره را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای دوره

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Period/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط دوره‌های پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
            - در صورت وجود وابستگی (هزینه‌ها، تراکنش‌ها)، ممکن است حذف ناموفق باشد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """دریافت داده‌های دوره‌ای برای نمودارها (سرمایه، هزینه، فروش، مانده صندوق)"""
        logger.info("User %s requesting period chart data", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام دوره‌ها مرتب شده
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')  # لیست دوره‌های پروژه فعال

            chart_data = []  # داده‌های نمودار
            cumulative_capital = 0  # سرمایه تجمعی
            cumulative_expenses = 0  # هزینه‌های تجمعی
            cumulative_sales = 0  # فروش/مرجوعی تجمعی

            for period in periods:
                # محاسبه سرمایه دوره از مرجع واحد تراکنش‌ها
                tx_totals = models.Transaction.objects.period_totals(active_project, period)  # محاسبه مجموع تراکنش‌های دوره
                period_capital = float(tx_totals['net_capital'])  # سرمایه خالص دوره
                cumulative_capital += period_capital  # افزودن به سرمایه تجمعی

                # محاسبه هزینه‌های دوره (مرجع واحد)
                period_expenses = models.Expense.objects.period_totals(active_project, period)  # مجموع هزینه‌های دوره
                cumulative_expenses += period_expenses  # افزودن به هزینه‌های تجمعی

                # محاسبه فروش/مرجوعی دوره (مرجع واحد)
                period_sales = models.Sale.objects.period_totals(active_project, period)  # مجموع فروش/مرجوعی دوره
                cumulative_sales += period_sales  # افزودن به فروش/مرجوعی تجمعی

                # محاسبه مانده صندوق (مرجع واحد)
                from .calculations import FinancialCalculationService
                fund_balance = FinancialCalculationService.compute_fund_balance(
                    cumulative_capital, cumulative_expenses, cumulative_sales
                )  # مانده صندوق ساختمان

                chart_data.append({
                    'period_id': period.id,
                    'period_label': period.label,
                    'year': period.year,
                    'month_number': period.month_number,
                    'capital': period_capital,
                    'expenses': period_expenses,
                    'sales': period_sales,
                    'fund_balance': fund_balance,
                    'cumulative_capital': cumulative_capital,
                    'cumulative_expenses': cumulative_expenses,
                    'cumulative_sales': cumulative_sales
                })

            return Response({
                'success': True,
                'data': chart_data,
                'active_project': active_project.name
            })

        except Exception as e:
            logger.exception("Error in chart_data for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت داده‌های نمودار: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def period_summary(self, request):
        """
        دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقادیر تجمعی
        
        این endpoint خلاصه کامل تمام دوره‌های پروژه را با تمام اطلاعات مالی
        شامل آورده‌ها، برداشت‌ها، سرمایه خالص، سود، هزینه‌ها و فروش‌ها برمی‌گرداند.
        
        Returns:
            Response: شامل:
                - data: لیست خلاصه هر دوره
                - totals: مجموع‌های کلی
                - current: خلاصه دوره جاری
        
        نکات مهم:
        - فقط دوره‌های پروژه جاری را شامل می‌شود
        - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
        - دوره‌ها به ترتیب زمانی مرتب می‌شوند
        - تمام مبالغ به تومان هستند
        """
        logger.info("User %s requesting period summary", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # دریافت تمام دوره‌ها مرتب شده
            periods = models.Period.objects.filter(
                project=active_project
            ).order_by('year', 'month_number')  # لیست دوره‌های پروژه فعال

            summary_data = []  # داده‌های خلاصه دوره‌ای
            
            # متغیرهای تجمعی
            cumulative_deposits = 0  # آورده‌های تجمعی
            cumulative_withdrawals = 0  # برداشت‌های تجمعی
            cumulative_net_capital = 0  # سرمایه خالص تجمعی
            cumulative_profits = 0  # سود تجمعی
            cumulative_expenses = 0  # هزینه‌های تجمعی
            cumulative_sales = 0  # فروش/مرجوعی تجمعی
            final_fund_balance = 0  # مانده صندوق نهایی

            # خلاصه ویژه دوره جاری
            current_summary = None  # خلاصه دوره جاری

            for period in periods:
                # محاسبات تراکنش‌های دوره از مرجع واحد
                tx_totals = models.Transaction.objects.period_totals(active_project, period)  # محاسبه مجموع تراکنش‌های دوره
                deposits = tx_totals['deposits']  # آورده‌های دوره
                withdrawals = tx_totals['withdrawals']  # برداشت‌های دوره
                profits = tx_totals['profits']  # سود دوره
                net_capital = tx_totals['net_capital']  # سرمایه خالص دوره

                cumulative_deposits += deposits  # افزودن به آورده‌های تجمعی
                cumulative_withdrawals += withdrawals  # افزودن به برداشت‌های تجمعی
                cumulative_profits += profits  # افزودن به سود تجمعی
                cumulative_net_capital += net_capital  # افزودن به سرمایه خالص تجمعی

                # هزینه‌های دوره (مرجع واحد)
                expenses = models.Expense.objects.period_totals(active_project, period)  # مجموع هزینه‌های دوره
                cumulative_expenses += expenses  # افزودن به هزینه‌های تجمعی

                # فروش/مرجوعی دوره (مرجع واحد)
                sales = models.Sale.objects.period_totals(active_project, period)  # مجموع فروش/مرجوعی دوره
                cumulative_sales += sales  # افزودن به فروش/مرجوعی تجمعی

                # محاسبه مانده صندوق (مرجع واحد)
                from .calculations import FinancialCalculationService
                fund_balance = FinancialCalculationService.compute_fund_balance(
                    cumulative_net_capital, cumulative_expenses, cumulative_sales
                )  # مانده صندوق ساختمان
                final_fund_balance = fund_balance  # ذخیره آخرین مقدار

                # اضافه کردن داده‌های دوره
                summary_data.append({
                    'period_id': period.id,
                    'period_label': period.label,
                    'year': period.year,
                    'month_number': period.month_number,
                    'month_name': period.month_name,
                    'weight': period.weight,
                    'is_current_period': period.is_current(),
                    
                    # فاکتورهای دوره
                    'deposits': deposits,
                    'withdrawals': withdrawals,
                    'net_capital': net_capital,
                    'profits': profits,
                    'expenses': expenses,
                    'sales': sales,
                    'period_fund_balance': (net_capital - expenses + sales),
                    'fund_balance': fund_balance,
                    
                    # مقادیر تجمعی
                    'cumulative_deposits': cumulative_deposits,
                    'cumulative_withdrawals': cumulative_withdrawals,
                    'cumulative_net_capital': cumulative_net_capital,
                    'cumulative_profits': cumulative_profits,
                    'cumulative_expenses': cumulative_expenses,
                    'cumulative_sales': cumulative_sales,
                    'cumulative_fund_balance': fund_balance
                })

                # اگر این دوره جاری است، خلاصه ویژه current را بساز
                if period.is_current():
                    # هزینه نهایی تجمعی تا دوره جاری (نه هزینه کل پروژه)
                    # این مقدار از تفاضل هزینه‌های تجمعی و فروش‌های تجمعی تا این دوره محاسبه می‌شود
                    current_final_cost = cumulative_expenses - cumulative_sales  # هزینه نهایی تا دوره جاری
                    
                    # آمار واحدها برای محاسبه هزینه هر متر (مرجع واحد)
                    # مساحت خالص واحدها: مجموع مساحت تمام واحدهای ثبت‌شده در سیستم
                    # شامل فقط واحدهای مسکونی/تجاری که به مالکین تعلق دارند
                    total_area_current = models.Unit.objects.project_total_area(active_project)  # مجموع مساحت واحدها تا دوره جاری
                    
                    # زیربنای کل پروژه: تمام زیربنای ساختمان از جمله واحدها، راهرو، پارکینگ، انباری، پله‌ها و...
                    # این مقدار به صورت دستی در تنظیمات پروژه تعریف می‌شود
                    total_infrastructure = float(active_project.total_infrastructure)  # مساحت کل زیربنا
                    
                    # هزینه هر متر خالص تا دوره جاری (Net Current): هزینه تجمعی تا دوره جاری تقسیم بر مساحت واحدها
                    # این شاخص نشان می‌دهد برای هر متر مربع واحد، چه هزینه‌ای تا این دوره شده است
                    # نکته: این هزینه نهایی کل پروژه نیست، بلکه هزینه تا دوره جاری است
                    # کاربرد: محاسبه سهم هزینه هر واحد بر اساس مساحت آن (تا دوره جاری)
                    cost_per_meter_net_current = (current_final_cost / total_area_current) if total_area_current > 0 else 0  # هزینه خالص هر متر مربع تا دوره جاری
                    
                    # هزینه هر متر ناخالص تا دوره جاری (Gross Current): هزینه تجمعی تا دوره جاری تقسیم بر زیربنای کل پروژه
                    # این شاخص نشان می‌دهد برای هر متر مربع از کل ساختمان (شامل فضاهای مشترک)، چه هزینه‌ای تا این دوره شده است
                    # نکته: این هزینه نهایی کل پروژه نیست، بلکه هزینه تا دوره جاری است
                    # کاربرد: ارزیابی هزینه‌های پروژه تا دوره جاری و مقایسه با پروژه‌های مشابه
                    cost_per_meter_gross_current = (current_final_cost / total_infrastructure) if total_infrastructure > 0 else 0  # هزینه ناخالص هر متر مربع تا دوره جاری

                    current_summary = {
                        'period': {
                            'id': period.id,
                            'label': period.label,
                            'year': period.year,
                            'month_number': period.month_number,
                            'month_name': period.month_name
                        },
                        'current_period_factors': {
                            'deposits': deposits,
                            'withdrawals': withdrawals,
                            'net_capital': net_capital,
                            'profits': profits,
                            'expenses': expenses,
                            'sales': sales,
                            'period_fund_balance': FinancialCalculationService.compute_period_fund_balance(net_capital, expenses, sales),
                            'fund_balance': fund_balance
                        },
                        'current_cumulative_totals': {
                            'total_deposits': cumulative_deposits,
                            'total_withdrawals': cumulative_withdrawals,
                            'total_net_capital': cumulative_net_capital,
                            'total_profits': cumulative_profits,
                            'total_expenses': cumulative_expenses,
                            'total_sales': cumulative_sales,
                            'final_fund_balance': fund_balance,
                            'final_cost': current_final_cost,
                            'cost_per_meter_net': cost_per_meter_net_current,
                            'cost_per_meter_gross': cost_per_meter_gross_current
                        }
                    }

            # محاسبه هزینه هر متر خالص و ناخالص
            # دریافت آمار واحدها
            units_stats = models.Unit.objects.filter(project=active_project).aggregate(
                total_area=Sum('area'),  # مجموع مساحت واحدها
                total_price=Sum('total_price')  # مجموع قیمت واحدها
            )
            
            total_area = float(units_stats['total_area'] or 0)  # مجموع مساحت واحدها
            total_infrastructure = float(active_project.total_infrastructure)  # مساحت کل زیربنا
            final_cost = cumulative_expenses - cumulative_sales  # هزینه نهایی (هزینه‌ها - فروش)
            
            # محاسبه هزینه هر متر
            cost_per_meter_net = final_cost / total_area if total_area > 0 else 0  # هزینه خالص هر متر مربع
            cost_per_meter_gross = final_cost / total_infrastructure if total_infrastructure > 0 else 0  # هزینه ناخالص هر متر مربع

            # محاسبه خلاصه کلی
            totals = {
                'total_deposits': cumulative_deposits,  # مجموع آورده‌ها
                'total_withdrawals': cumulative_withdrawals,  # مجموع برداشت‌ها
                'total_net_capital': cumulative_net_capital,  # مجموع سرمایه خالص
                'total_profits': cumulative_profits,  # مجموع سود
                'total_expenses': cumulative_expenses,  # مجموع هزینه‌ها
                'total_sales': cumulative_sales,  # مجموع فروش/مرجوعی
                'final_fund_balance': final_fund_balance,  # مانده صندوق نهایی
                'total_periods': periods.count(),  # تعداد دوره‌ها
                'cost_per_meter_net': cost_per_meter_net,  # هزینه خالص هر متر مربع
                'cost_per_meter_gross': cost_per_meter_gross,  # هزینه ناخالص هر متر مربع
                'final_cost': final_cost  # هزینه نهایی
            }

            return Response({
                'success': True,
                'data': summary_data,
                'totals': totals,
                'active_project': active_project.name,
                'current': current_summary
            })

        except Exception as e:
            logger.exception("Error in period_summary for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت خلاصه دوره‌ای: {str(e)}'
            }, status=500)



class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت پروژه‌های ساختمانی
    
    این ViewSet امکان مدیریت کامل پروژه‌های ساختمانی را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف پروژه‌ها
    - دریافت پروژه جاری (active project)
    - دریافت آمار کامل پروژه
    - دریافت تحلیل جامع پروژه
    - دریافت متریک‌های سود و هزینه
    - مدیریت تنظیمات پروژه (رنگ، آیکون، گرادیانت)
    
    سناریوهای استفاده:
    - ایجاد پروژه جدید
    - انتخاب پروژه جاری
    - دریافت آمار و گزارش‌های مالی
    - تحلیل عملکرد پروژه
    - تنظیم پارامترهای محاسباتی
    
    مثال‌های کاربرد:
    - برای دریافت پروژه جاری: GET /api/v1/Project/active/
    - برای دریافت آمار: GET /api/v1/Project/statistics/
    - برای دریافت تحلیل جامع: GET /api/v1/Project/comprehensive_analysis/
    
    نکات مهم:
    - پروژه جاری از session کاربر تعیین می‌شود
    - تمام محاسبات مالی بر اساس پروژه جاری انجام می‌شود
    - تنظیمات پروژه (رنگ، آیکون) برای نمایش در UI استفاده می‌شود
    """

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام پروژه‌ها

        این متد لیست تمام پروژه‌های موجود را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Project/?page=1&page_size=10

        نکات:
            - تمام پروژه‌ها برگردانده می‌شوند
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد پروژه جدید

        این متد پروژه جدید را ثبت می‌کند.

        Request Body:
            - name (الزامی): نام پروژه
            - start_date_shamsi (الزامی): تاریخ شروع شمسی
            - end_date_shamsi (الزامی): تاریخ پایان شمسی
            - start_date_gregorian (الزامی): تاریخ شروع میلادی
            - end_date_gregorian (الزامی): تاریخ پایان میلادی
            - total_infrastructure (اختیاری): زیر بنای کل
            - correction_factor (اختیاری): ضریب اصلاحی
            - construction_contractor_percentage (اختیاری): درصد پیمان ساخت
            - description (اختیاری): توضیحات
            - color (اختیاری): رنگ پروژه
            - icon (اختیاری): آیکون پروژه

        Returns:
            Response با اطلاعات پروژه ایجاد شده (status 201)

        مثال:
            POST /api/v1/Project/
            {
                "name": "پروژه ساختمانی نمونه",
                "start_date_shamsi": "1403-01-01",
                "end_date_shamsi": "1405-12-29",
                "start_date_gregorian": "2024-03-20",
                "end_date_gregorian": "2027-03-19",
                "total_infrastructure": "5000.00",
                "correction_factor": "1.0000000000"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک پروژه خاص

        این متد اطلاعات کامل پروژه با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای پروژه

        Returns:
            Response با اطلاعات کامل پروژه

        مثال:
            GET /api/v1/Project/1/

        نکات:
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل پروژه

        این متد امکان تغییر همه فیلدهای یک پروژه را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای پروژه

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده پروژه (status 200)

        مثال:
            PUT /api/v1/Project/1/
            {
                "name": "پروژه به‌روزرسانی شده",
                "start_date_shamsi": "1403-01-01",
                "end_date_shamsi": "1405-12-29"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی پروژه

        این متد امکان تغییر بخشی از فیلدهای پروژه را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای پروژه

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده پروژه (status 200)

        مثال:
            PATCH /api/v1/Project/1/
            {
                "name": "نام جدید پروژه"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف پروژه

        این متد پروژه را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای پروژه

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Project/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
            - در صورت وجود وابستگی (هزینه‌ها، تراکنش‌ها، واحدها)، ممکن است حذف ناموفق باشد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """دریافت پروژه جاری (از session)"""
        from construction.project_manager import ProjectManager
        active_project = ProjectManager.get_current_project(request)  # پروژه جاری
        if active_project:
            serializer = self.get_serializer(active_project)  # سریالایزر پروژه
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'}, status=404)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """دریافت آمار کامل پروژه جاری شامل اطلاعات پروژه و آمار واحدها"""
        logger.info("User %s requesting project statistics", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # آمار واحدها برای پروژه فعال (مرجع واحد)
            units_stats = models.Unit.objects.project_stats(active_project)  # آمار واحدهای پروژه فعال

            # اطلاعات پروژه
            project_data = {
                'id': active_project.id,  # شناسه پروژه
                'name': active_project.name,  # نام پروژه
                'total_infrastructure': float(active_project.total_infrastructure),  # مساحت کل زیربنا
                'correction_factor': float(active_project.correction_factor),  # ضریب اصلاحی
                'start_date_shamsi': str(active_project.start_date_shamsi),  # تاریخ شروع (شمسی)
                'end_date_shamsi': str(active_project.end_date_shamsi),  # تاریخ پایان (شمسی)
                'start_date_gregorian': str(active_project.start_date_gregorian),  # تاریخ شروع (میلادی)
                'end_date_gregorian': str(active_project.end_date_gregorian),  # تاریخ پایان (میلادی)
                # فیلد is_active حذف شد - مدل Project این فیلد را ندارد
            }

            return Response({
                'project': project_data,
                'units_statistics': units_stats
            })

        except Exception as e:
            logger.exception("Error in statistics for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت آمار پروژه: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['post'])
    def set_active(self, request):
        """تنظیم پروژه فعال"""
        project_id = request.data.get('project_id')  # شناسه پروژه از داده‌های درخواست
        if not project_id:
            logger.warning("set_active called without project_id by user %s", request.user.username)
            return Response({'error': 'شناسه پروژه الزامی است'}, status=400)
        
        logger.info("User %s setting active project to %s", request.user.username, project_id)
        try:
            project = models.Project.set_active_project(project_id)  # تنظیم پروژه به عنوان فعال
            if project:
                serializer = self.get_serializer(project)  # سریالایزر پروژه
                return Response({
                    'success': True,
                    'message': f'پروژه "{project.name}" به عنوان پروژه فعال تنظیم شد',
                    'project': serializer.data
                })
            else:
                logger.warning("Project %s not found for user %s", project_id, request.user.username)
                return Response({'error': 'پروژه یافت نشد'}, status=404)
        except Exception as e:
            logger.exception("Error in set_active for user %s (project_id: %s): %s", request.user.username, project_id, e)
            return Response({'error': f'خطا در تنظیم پروژه فعال: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """دریافت پروژه جاری کاربر از session"""
        from construction.project_manager import ProjectManager
        
        current_project = ProjectManager.get_current_project(request)
        if current_project:
            serializer = self.get_serializer(current_project)
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ پروژه جاری یافت نشد'}, status=404)
    
    @action(detail=False, methods=['post'])
    def switch(self, request):
        """تغییر پروژه جاری کاربر"""
        from construction.project_manager import ProjectManager
        
        project_id = request.data.get('project_id')
        if not project_id:
            logger.warning("switch called without project_id by user %s", request.user.username)
            return Response({'error': 'project_id الزامی است'}, status=400)
        
        logger.info("User %s switching to project %s", request.user.username, project_id)
        try:
            project = models.Project.objects.get(id=project_id)
            
            # تنظیم پروژه در session
            ProjectManager.set_current_project(request, project_id)
            
            return Response({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'color': project.color or '#667eea',
                    'icon': project.icon or 'fa-building'
                },
                'message': 'پروژه با موفقیت تغییر کرد'
            })
        except models.Project.DoesNotExist:
            logger.warning("Project %s not found for user %s in switch", project_id, request.user.username)
            return Response({'error': 'پروژه یافت نشد'}, status=404)
        except Exception as e:
            logger.exception("Error in switch for user %s (project_id: %s): %s", request.user.username, project_id, e)
            return Response({'error': f'خطا در تغییر پروژه: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def project_timeline(self, request):
        """محاسبه روزهای مانده و گذشته پروژه بر اساس تاریخ امروز"""
        from datetime import date
        
        logger.info("User %s requesting project timeline", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # تاریخ امروز
            today = date.today()  # تاریخ امروز
            
            # محاسبه روزهای مانده تا پایان پروژه
            days_remaining = 0  # روزهای مانده تا پایان پروژه
            if active_project.end_date_gregorian:
                end_date = active_project.end_date_gregorian  # تاریخ پایان پروژه
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()  # تبدیل به date
                days_remaining = (end_date - today).days  # محاسبه روزهای مانده
            
            # محاسبه روزهای گذشته از ابتدای پروژه
            days_from_start = 0  # روزهای گذشته از ابتدای پروژه
            if active_project.start_date_gregorian:
                start_date = active_project.start_date_gregorian  # تاریخ شروع پروژه
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()  # تبدیل به date
                days_from_start = (today - start_date).days  # محاسبه روزهای گذشته
            
            # محاسبه مدت کل پروژه
            total_project_days = 0  # مدت کل پروژه (روز)
            if (active_project.start_date_gregorian and 
                active_project.end_date_gregorian):
                start_date = active_project.start_date_gregorian  # تاریخ شروع پروژه
                end_date = active_project.end_date_gregorian  # تاریخ پایان پروژه
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()  # تبدیل به date
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()  # تبدیل به date
                total_project_days = (end_date - start_date).days  # محاسبه مدت کل پروژه

            return Response({
                'success': True,
                'project': {
                    'id': active_project.id,
                    'name': active_project.name,
                    'start_date_shamsi': str(active_project.start_date_shamsi),
                    'end_date_shamsi': str(active_project.end_date_shamsi),
                    'start_date_gregorian': str(active_project.start_date_gregorian),
                    'end_date_gregorian': str(active_project.end_date_gregorian)
                },
                'today': str(today),
                'timeline': {
                    'days_remaining': days_remaining,
                    'days_from_start': days_from_start,
                    'total_project_days': total_project_days,
                    'progress_percentage': round((days_from_start / total_project_days * 100), 2) if total_project_days > 0 else 0
                }
            })

        except Exception as e:
            logger.exception("Error in project_timeline for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه زمان‌بندی پروژه: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def comprehensive_analysis(self, request):
        """دریافت تحلیل جامع پروژه شامل تمام محاسبات مالی"""
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            analysis = calculations.ComprehensiveCalculations.get_comprehensive_project_analysis(project_id)  # دریافت تحلیل جامع پروژه
            
            if 'error' in analysis:
                logger.warning("Error in comprehensive_analysis: %s", analysis.get('error'))
                return Response(analysis, status=400)
            
            logger.info("Successfully returned comprehensive analysis for user %s", request.user.username)
            return Response(analysis)
            
        except Exception as e:
            logger.exception("Error in comprehensive_analysis for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت تحلیل جامع: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def profit_metrics(self, request):
        """
        دریافت متریک‌های سود (کل، سالانه، ماهانه، روزانه)
        
        این endpoint متریک‌های مختلف سود شامل سود کل، سالانه، ماهانه و روزانه
        را برای پروژه محاسبه و برمی‌گرداند.
        
        Parameters:
            project_id (int, optional): شناسه پروژه (از query parameter یا پروژه جاری)
        
        Returns:
            Response: شامل متریک‌های سود
        
        نکات مهم:
        - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
        - محاسبات بر اساس تاریخ شروع و پایان پروژه انجام می‌شود
        - مبالغ به تومان هستند
        """
        logger.info("User %s requesting profit metrics", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            metrics = calculations.ProfitCalculations.calculate_profit_percentages(project_id)  # محاسبه متریک‌های سود
            
            if 'error' in metrics:
                logger.warning("Error in profit_metrics: %s", metrics.get('error'))
                return Response(metrics, status=400)
            
            logger.info("Successfully returned profit metrics for user %s", request.user.username)
            return Response(metrics)
            
        except Exception as e:
            logger.exception("Error in profit_metrics for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه متریک‌های سود: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def cost_metrics(self, request):
        """دریافت متریک‌های هزینه"""
        logger.info("User %s requesting cost metrics", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            metrics = calculations.ProjectCalculations.calculate_cost_metrics(project_id)  # محاسبه متریک‌های هزینه
            
            if 'error' in metrics:
                logger.warning("Error in cost_metrics: %s", metrics.get('error'))
                return Response(metrics, status=400)
            
            logger.info("Successfully returned cost metrics for user %s", request.user.username)
            return Response(metrics)
            
        except Exception as e:
            logger.exception("Error in cost_metrics for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه متریک‌های هزینه: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def project_statistics_detailed(self, request):
        """دریافت آمار تفصیلی پروژه"""
        logger.info("User %s requesting detailed project statistics", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # اگر project_id مشخص نشده، از پروژه جاری استفاده کن
            if not project_id:
                from construction.project_manager import ProjectManager
                current_project = ProjectManager.get_current_project(request)
                if current_project:
                    project_id = current_project.id
                else:
                    return Response({
                        'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                    }, status=400)
            
            stats = calculations.ProjectCalculations.calculate_project_statistics(project_id)  # محاسبه آمار تفصیلی پروژه
            
            if 'error' in stats:
                logger.warning("Error in project_statistics_detailed: %s", stats.get('error'))
                return Response(stats, status=400)
            
            logger.info("Successfully returned detailed project statistics for user %s", request.user.username)
            return Response(stats)
            
        except Exception as e:
            logger.exception("Error in project_statistics_detailed for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی: {str(e)}'
            }, status=500)

    # ========================================
    # Excel Export Endpoints - موقتاً غیرفعال
    # برای فعال‌سازی، کامنت را بردارید
    # ========================================
    
    # @action(detail=False, methods=['get'], url_path='export_excel_static')
    # def export_excel_static(self, request):
    #     """
    #     Export کامل اطلاعات پروژه به فرمت Excel
    #     
    #     این endpoint فایل Excel شامل موارد زیر را تولید می‌کند:
    #     - 9 شیت داده پایه (Project, Units, Investors, Periods, InterestRates, Transactions, Expenses, Sales, UserProfiles)
    #     - 6 شیت محاسباتی (Dashboard, Profit_Metrics, Cost_Metrics, Investor_Analysis, Period_Summary, Transaction_Summary)
    #     
    #     نوع محاسبات: Static (تمام محاسبات در سرور انجام می‌شود)
    #     
    #     Returns:
    #         فایل Excel با 15 شیت
    #     """
    #     from .excel_export import ExcelExportService
    #     from django.http import HttpResponse
    #     
    #     try:
    #         # دریافت پروژه جاری از session
    #         from construction.project_manager import ProjectManager
    #         project = ProjectManager.get_current_project(request)
    #         if not project:
    #             return Response({'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'}, status=400)
    #         
    #         # تولید فایل Excel
    #         excel_service = ExcelExportService(project)
    #         workbook = excel_service.generate_excel()
    #         
    #         # نام فایل با تاریخ و زمان
    #         from django.utils import timezone
    #         import re
    #         # پاک کردن کاراکترهای غیرمجاز از نام پروژه
    #         safe_project_name = re.sub(r'[^\w\-_\.]', '_', project.name)
    #         timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    #         filename = f'project_{safe_project_name}_{timestamp}.xlsx'
    #         
    #         # آماده‌سازی response
    #         response = HttpResponse(
    #             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         )
    #         
    #         # تنظیم header برای اطمینان از نام فایل صحیح
    #         response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
    #         
    #         # ذخیره workbook در response
    #         workbook.save(response)
    #         
    #         return response
    #         
    #     except ValueError as e:
    #         return Response({
    #             'error': str(e)
    #         }, status=400)
    #     except Exception as e:
    #         return Response({
    #             'error': f'خطا در تولید فایل Excel: {str(e)}'
    #         }, status=500)
    
    # @action(detail=False, methods=['get'], url_path='export_excel_dynamic')
    # def export_excel_dynamic(self, request):
    #     """
    #     Export کامل اطلاعات پروژه به فرمت Excel با فرمول‌های محاسباتی
    #     
    #     این endpoint فایل Excel شامل موارد زیر را تولید می‌کند:
    #     - شیت راهنمای فرمول‌ها
    #     - 9 شیت داده پایه (بدون فرمول)
    #     - 6 شیت محاسباتی (با فرمول‌های Excel)
    #     - Named Ranges برای خوانایی بهتر
    #     
    #     نوع محاسبات: Dynamic (فرمول‌های Excel)
    #     
    #     Returns:
    #         فایل Excel با فرمول‌های محاسباتی
    #     """
    #     from .excel_export_dynamic import ExcelDynamicExportService
    #     from django.http import HttpResponse
    #     
    #     try:
    #         # دریافت پروژه جاری از session
    #         from construction.project_manager import ProjectManager
    #         project = ProjectManager.get_current_project(request)
    #         if not project:
    #             return Response({'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'}, status=400)
    #         
    #         # تولید فایل Excel با فرمول
    #         excel_service = ExcelDynamicExportService(project)
    #         workbook = excel_service.generate_excel()
    #         
    #         # نام فایل با تاریخ و زمان
    #         from django.utils import timezone
    #         import re
    #         # پاک کردن کاراکترهای غیرمجاز از نام پروژه
    #         safe_project_name = re.sub(r'[^\w\-_\.]', '_', project.name)
    #         timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    #         filename = f'project_dynamic_{safe_project_name}_{timestamp}.xlsx'
    #         
    #         # آماده‌سازی response
    #         response = HttpResponse(
    #             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         )
    #         
    #         # تنظیم header برای اطمینان از نام فایل صحیح
    #         response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
    #         
    #         # ذخیره workbook در response
    #         workbook.save(response)
    #         
    #         return response
    #         
    #     except ValueError as e:
    #         return Response({
    #             'error': str(e)
    #         }, status=400)
    #     except Exception as e:
    #         return Response({
    #             'error': f'خطا در تولید فایل Excel Dynamic: {str(e)}'
    #         }, status=500)


class SaleViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت فروش/مرجوعی‌های پروژه
    
    این ViewSet امکان مدیریت کامل فروش و مرجوعی‌های پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف فروش/مرجوعی‌ها
    - دریافت مجموع فروش/مرجوعی‌ها
    - مدیریت فروش/مرجوعی‌های دوره‌ای
    
    سناریوهای استفاده:
    - ثبت فروش واحدها
    - ثبت مرجوعی واحدها
    - دریافت آمار فروش/مرجوعی
    - تحلیل روند فروش در دوره‌های مختلف
    
    مثال‌های کاربرد:
    - برای ثبت فروش: period=1, amount='100000000'
    - برای دریافت مجموع: GET /api/v1/Sale/total_sales/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - فروش/مرجوعی‌ها به یک دوره خاص مرتبط هستند
    - مبلغ می‌تواند مثبت (فروش) یا منفی (مرجوعی) باشد
    """

    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام فروش/مرجوعی‌های پروژه جاری

        این متد لیست فروش/مرجوعی‌های مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Sale/?page=1&page_size=20

        نکات:
            - فقط فروش/مرجوعی‌های پروژه جاری برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد فروش/مرجوعی جدید برای پروژه جاری

        این متد فروش/مرجوعی جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - period (الزامی): شناسه دوره
            - amount (الزامی): مبلغ فروش/مرجوعی (به صورت string)
            - description (اختیاری): توضیحات

        Returns:
            Response با اطلاعات فروش/مرجوعی ایجاد شده (status 201)

        مثال:
            POST /api/v1/Sale/
            {
                "period": 1,
                "amount": "100000000",
                "description": "فروش واحد 101"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک فروش/مرجوعی خاص

        این متد اطلاعات کامل فروش/مرجوعی با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای فروش/مرجوعی

        Returns:
            Response با اطلاعات کامل فروش/مرجوعی شامل project_data و period_data

        مثال:
            GET /api/v1/Sale/1/

        نکات:
            - فقط فروش/مرجوعی‌های پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل فروش/مرجوعی

        این متد امکان تغییر همه فیلدهای یک فروش/مرجوعی را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای فروش/مرجوعی

        Request Body:
            - تمام فیلدهای قابل ویرایش (period, amount, description)

        Returns:
            Response با اطلاعات به‌روزرسانی شده فروش/مرجوعی (status 200)

        مثال:
            PUT /api/v1/Sale/1/
            {
                "period": 1,
                "amount": "120000000",
                "description": "فروش واحد 101 - به‌روزرسانی شده"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی فروش/مرجوعی

        این متد امکان تغییر بخشی از فیلدهای فروش/مرجوعی را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای فروش/مرجوعی

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده فروش/مرجوعی (status 200)

        مثال:
            PATCH /api/v1/Sale/1/
            {
                "amount": "120000000"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف فروش/مرجوعی

        این متد فروش/مرجوعی را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای فروش/مرجوعی

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Sale/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط فروش/مرجوعی‌های پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def total_sales(self, request):
        """دریافت مجموع فروش‌ها"""
        logger.info("User %s requesting total sales", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)

            # محاسبه مجموع فروش‌ها برای پروژه فعال (مرجع واحد)
            total_amount = models.Sale.objects.project_totals(active_project)  # مجموع کل فروش/مرجوعی پروژه

            # تعداد فروش‌ها
            sales_count = models.Sale.objects.filter(
                project=active_project
            ).count()  # تعداد فروش/مرجوعی‌های پروژه

            # فروش‌ها به تفکیک دوره (بدون تغییر)
            sales_by_period = models.Sale.objects.filter(
                project=active_project
            ).values('period__label', 'period__id').annotate(
                period_total=Sum('amount'),  # مجموع فروش/مرجوعی هر دوره
                period_count=Count('id')  # تعداد فروش/مرجوعی هر دوره
            ).order_by('period__id')  # لیست فروش/مرجوعی‌ها به تفکیک دوره

            # محاسبه تجمعی فروش‌ها در هر دوره
            cumulative_sales = []  # لیست فروش/مرجوعی تجمعی
            cumulative_total = 0  # مجموع تجمعی کل
            
            for period_data in sales_by_period:
                period_amount = period_data['period_total'] or 0  # مبلغ فروش/مرجوعی این دوره
                cumulative_total += period_amount  # افزودن به مجموع تجمعی
                
                cumulative_sales.append({
                    'period_id': period_data['period__id'],  # شناسه دوره
                    'period_label': period_data['period__label'],  # برچسب دوره
                    'period_amount': period_amount,  # مبلغ فروش/مرجوعی دوره
                    'period_count': period_data['period_count'],  # تعداد فروش/مرجوعی دوره
                    'cumulative_amount': cumulative_total  # مبلغ تجمعی تا این دوره
                })

            return Response({
                'project_name': active_project.name,
                'total_amount': total_amount,
                'sales_count': sales_count,
                'sales_by_period': list(sales_by_period),
                'cumulative_sales_by_period': cumulative_sales,
                'currency': 'تومان'
            })

        except Exception as e:
            logger.exception("Error in total_sales for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه مجموع فروش‌ها: {str(e)}'
            }, status=500)


class TransactionViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت تراکنش‌های مالی پروژه
    
    این ViewSet امکان مدیریت کامل تراکنش‌های مالی سرمایه‌گذاران را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف تراکنش‌ها
    - دریافت آمار کلی تراکنش‌ها
    - مدیریت انواع تراکنش (آورده، برداشت، سود)
    - محاسبه خودکار روز مانده و روز از شروع
    - فیلتر بر اساس سرمایه‌گذار، دوره و نوع تراکنش
    
    سناریوهای استفاده:
    - ثبت آورده سرمایه‌گذاران
    - ثبت برداشت از سرمایه
    - ثبت سود تعلق گرفته
    - دریافت آمار تراکنش‌ها
    - تحلیل روند تراکنش‌ها
    
    مثال‌های کاربرد:
    - برای ثبت آورده: transaction_type='principal_deposit', amount='50000000'
    - برای دریافت آمار: GET /api/v1/Transaction/statistics/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - تراکنش‌ها به یک سرمایه‌گذار و دوره خاص مرتبط هستند
    - انواع تراکنش: principal_deposit, loan_deposit, principal_withdrawal, profit_accrual
    - روز مانده و روز از شروع به صورت خودکار محاسبه می‌شوند
    """

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]
    filterset_fields = ['investor', 'project', 'period', 'transaction_type']

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام تراکنش‌های پروژه جاری

        این متد لیست تراکنش‌های مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل فیلتر و مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی
            - investor: فیلتر بر اساس شناسه سرمایه‌گذار
            - period: فیلتر بر اساس شناسه دوره
            - transaction_type: فیلتر بر اساس نوع تراکنش

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Transaction/?investor=1&transaction_type=principal_deposit

        نکات:
            - فقط تراکنش‌های پروژه جاری برگردانده می‌شود
            - امکان فیلتر بر اساس سرمایه‌گذار، دوره و نوع تراکنش
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد تراکنش جدید برای پروژه جاری

        این متد تراکنش جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - investor/investor_id (الزامی): شناسه سرمایه‌گذار
            - period/period_id (الزامی): شناسه دوره
            - date_shamsi_input یا date_shamsi_raw (الزامی): تاریخ شمسی
            - amount (الزامی): مبلغ تراکنش (به صورت string)
            - transaction_type (الزامی): نوع تراکنش
            - description (اختیاری): توضیحات

        Returns:
            Response با اطلاعات تراکنش ایجاد شده (status 201)

        مثال:
            POST /api/v1/Transaction/
            {
                "investor": 1,
                "period": 1,
                "date_shamsi_input": "1403-07-15",
                "amount": "50000000",
                "transaction_type": "principal_deposit",
                "description": "آورده اولیه"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - روز مانده و روز از شروع به صورت خودکار محاسبه می‌شوند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک تراکنش خاص

        این متد اطلاعات کامل تراکنش با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش

        Returns:
            Response با اطلاعات کامل تراکنش شامل investor_data, period_data, project_data

        مثال:
            GET /api/v1/Transaction/1/

        نکات:
            - فقط تراکنش‌های پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل تراکنش

        این متد امکان تغییر همه فیلدهای یک تراکنش را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده تراکنش (status 200)

        مثال:
            PUT /api/v1/Transaction/1/
            {
                "investor": 1,
                "period": 1,
                "date_shamsi_input": "1403-07-15",
                "amount": "60000000",
                "transaction_type": "principal_deposit"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی تراکنش

        این متد امکان تغییر بخشی از فیلدهای تراکنش را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده تراکنش (status 200)

        مثال:
            PATCH /api/v1/Transaction/1/
            {
                "amount": "60000000"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف تراکنش

        این متد تراکنش را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Transaction/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط تراکنش‌های پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        دریافت آمار کلی تراکنش‌های پروژه
        
        این endpoint آمار جامع و کلی تمام تراکنش‌های پروژه جاری را برمی‌گرداند.
        
        خروجی شامل:
        - تعداد کل تراکنش‌ها
        - مجموع آورده‌ها (deposits)
        - مجموع برداشت‌ها (withdrawals)
        - مجموع سود (profits)
        - سرمایه خالص (net principal)
        - مجموع کل (grand total)
        - تعداد سرمایه‌گذاران منحصر به فرد
        
        سناریوهای استفاده:
        - نمایش خلاصه مالی پروژه
        - نمایش داشبورد تراکنش‌ها
        - تحلیل جریان نقدی پروژه
        - محاسبه شاخص‌های مالی کلیدی
        - تهیه گزارش‌های مدیریتی
        
        مثال استفاده:
        GET /api/v1/Transaction/statistics/
        
        مثال خروجی:
        {
            "total_transactions": 150,
            "total_deposits": 500000000,
            "total_withdrawals": -20000000,
            "total_profits": 75000000,
            "net_principal": 480000000,
            "grand_total": 555000000,
            "unique_investors": 5
        }
        
        نکات مهم:
        - فقط تراکنش‌های پروژه جاری را شامل می‌شود
        - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
        - مجموع برداشت‌ها به صورت منفی محاسبه می‌شود
        - تمام مبالغ به تومان هستند
        """
        from django.db.models import Count, Sum, Q
        
        # دریافت پروژه جاری از session
        from construction.project_manager import ProjectManager
        current_project = ProjectManager.get_current_project(request)  # پروژه جاری
        
        if not current_project:
            return Response({
                'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
            }, status=400)
        
        # محاسبه آمار کلی برای پروژه جاری
        total_transactions = models.Transaction.objects.filter(project=current_project).count()  # تعداد کل تراکنش‌های پروژه جاری
        tx_totals_all = models.Transaction.objects.project_totals(project=current_project)  # محاسبه مجموع تراکنش‌های پروژه جاری
        total_deposits = tx_totals_all['deposits']  # مجموع آورده‌ها
        total_withdrawals = tx_totals_all['withdrawals']  # مجموع برداشت‌ها (منفی)
        total_profits = tx_totals_all['profits']  # مجموع سود
        
        unique_investors = models.Transaction.objects.filter(project=current_project).values('investor').distinct().count()  # تعداد سرمایه‌گذاران منحصر به فرد پروژه جاری
        
        # محاسبه مجموع سرمایه (آورده منهای برداشت)
        # total_withdrawals منفی است پس به جای تفریق باید جمع بشه
        # net_principal = float(total_deposits) - float(total_withdrawals)
        net_principal = float(total_deposits) + float(total_withdrawals)  # سرمایه خالص (آورده + برداشت که منفی است)
        
        # محاسبه مجموع سرمایه + سود
        grand_total = net_principal + float(total_profits)  # مجموع کل (سرمایه خالص + سود)
        
        return Response({
            'total_transactions': total_transactions,
            'total_deposits': float(total_deposits),
            'total_withdrawals': float(total_withdrawals),
            'total_profits': float(total_profits),
            'net_principal': net_principal,
            'grand_total': grand_total,
            'unique_investors': unique_investors
        })

    @action(detail=False, methods=['get'])
    def combined(self, request):
        """
        دریافت تراکنش‌های اصلی به همراه تراکنش‌های سود مرتبط در یک رکورد
        فقط تراکنش‌های اصلی (غیر سود) را برمی‌گرداند
        """
        # فیلتر کردن فقط تراکنش‌های اصلی (غیر سود)
        from django.db.models import Prefetch
        queryset = self.get_queryset().exclude(
            transaction_type='profit_accrual'
        ).select_related(
            'investor', 'project', 'period', 'interest_rate'
        ).prefetch_related(
            # بهینه‌سازی: فقط تراکنش‌های سود را prefetch می‌کنیم
            Prefetch(
                'transaction_set',
                queryset=models.Transaction.objects.filter(transaction_type='profit_accrual').select_related('interest_rate'),
                to_attr='profit_transactions'
            )
        )
        
        # اعمال فیلترهای پروژه (از ProjectFilterMixin)
        queryset = self.filter_queryset(queryset)
        
        # استفاده از serializer جدید
        serializer = serializers.CombinedTransactionSerializer(queryset, many=True)
        return Response(serializer.data)

    # کدهای قبلی برای تغییر نرخ سود - کامنت شده برای مراجعه آینده
    """
    @action(detail=False, methods=['post'])
    def update_interest_rate(self, request):
        \"\"\"تغییر نرخ سود و محاسبه مجدد همه سودها\"\"\"
        from decimal import Decimal
        
        new_interest_rate = request.data.get('new_interest_rate')
        description = request.data.get('description', '')
        
        if not new_interest_rate:
            return Response({'error': 'نرخ سود جدید الزامی است'}, status=400)
        
        try:
            new_rate = Decimal(str(new_interest_rate))
            if new_rate <= 0:
                return Response({'error': 'نرخ سود باید مثبت باشد'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'نرخ سود نامعتبر است'}, status=400)
        
        try:
            # اجرای عملیات تغییر نرخ سود
            result = models.Transaction.recalculate_all_profits_with_new_rate(new_rate)
            
            # ذخیره نرخ جدید در InterestRate
            from django.utils import timezone
            import jdatetime
            
            now_gregorian = timezone.now().date()
            now_shamsi = jdatetime.date.fromgregorian(date=now_gregorian)
            
            models.InterestRate.objects.create(
                rate=new_rate,
                effective_date=now_shamsi,
                effective_date_gregorian=now_gregorian,
                description=description,
                is_active=True
            )
            
            return Response({
                'success': True,
                'message': 'نرخ سود با موفقیت تغییر کرد',
                'deleted_count': result['deleted_count'],
                'new_count': result['new_count'],
                'total_affected': result['total_affected'],
                'new_rate': float(new_rate)
            })
            
        except Exception as e:
            return Response({
                'error': f'خطا در تغییر نرخ سود: {str(e)}'
            }, status=500)
    """

    @action(detail=False, methods=['post'])
    def recalculate_profits(self, request):
        """محاسبه مجدد سودها با نرخ سود فعال فعلی برای پروژه فعال"""
        logger.info("User %s requesting profit recalculation", request.user.username)
        try:
            # دریافت پروژه جاری از session
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)  # پروژه جاری
            if not active_project:
                return Response({
                    'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
                }, status=400)
            
            # دریافت نرخ سود فعال فعلی برای پروژه فعال
            current_rate = models.InterestRate.get_current_rate(project=active_project)  # نرخ سود فعال فعلی
            if not current_rate:
                return Response({
                    'error': 'هیچ نرخ سود فعالی یافت نشد. لطفاً ابتدا نرخ سود را تنظیم کنید.'
                }, status=400)
            
            # اجرای عملیات محاسبه مجدد برای پروژه فعال
            result = models.Transaction.recalculate_all_profits_with_new_rate(current_rate, project=active_project)  # محاسبه مجدد سودها با نرخ فعلی
            
            return Response({
                'success': True,
                'message': 'سودها با موفقیت محاسبه مجدد شدند',
                'deleted_count': result['deleted_count'],
                'new_count': result['new_count'],
                'total_affected': result['total_affected'],
                'used_rate': float(current_rate.rate)
            })
            
        except Exception as e:
            logger.exception("Error in recalculate_profits for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه مجدد سودها: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'])
    def detailed_statistics(self, request):
        """دریافت آمار تفصیلی تراکنش‌ها با فیلترهای پیشرفته"""
        logger.info("User %s requesting detailed transaction statistics", request.user.username)
        try:
            project_id = request.query_params.get('project_id')  # شناسه پروژه از پارامترهای درخواست
            
            # فیلترهای اضافی
            filters = {}  # دیکشنری فیلترها
            if request.query_params.get('investor_id'):
                filters['investor_id'] = int(request.query_params.get('investor_id'))  # فیلتر شناسه سرمایه‌گذار
            if request.query_params.get('date_from'):
                filters['date_from'] = request.query_params.get('date_from')  # فیلتر تاریخ از
            if request.query_params.get('date_to'):
                filters['date_to'] = request.query_params.get('date_to')  # فیلتر تاریخ تا
            if request.query_params.get('transaction_type'):
                filters['transaction_type'] = request.query_params.get('transaction_type')  # فیلتر نوع تراکنش
            
            stats = calculations.TransactionCalculations.calculate_transaction_statistics(project_id, filters)  # محاسبه آمار تفصیلی تراکنش‌ها
            
            if 'error' in stats:
                logger.warning("Error in detailed_statistics: %s", stats.get('error'))
                return Response(stats, status=400)
            
            logger.info("Successfully returned detailed transaction statistics for user %s", request.user.username)
            return Response(stats)
            
        except Exception as e:
            logger.exception("Error in detailed_statistics for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در دریافت آمار تفصیلی تراکنش‌ها: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def recalculate_construction_contractor(self, request):
        """محاسبه مجدد همه هزینه‌های پیمان ساختمان"""
        logger.info("User %s requesting construction contractor recalculation", request.user.username)
        try:
            project_id = request.data.get('project_id')  # شناسه پروژه از داده‌های درخواست
            
            if project_id:
                try:
                    project = models.Project.objects.get(id=project_id)  # دریافت پروژه
                    updated_count = models.Expense.recalculate_all_construction_contractor_expenses(project)  # محاسبه مجدد هزینه‌های پیمان ساختمان برای پروژه
                    return Response({
                        'success': True,
                        'message': f'محاسبه مجدد برای پروژه "{project.name}" با موفقیت انجام شد',
                        'updated_periods': updated_count  # تعداد دوره‌های به‌روزرسانی شده
                    })
                except models.Project.DoesNotExist:
                    return Response({
                        'error': f'پروژه با شناسه {project_id} یافت نشد'
                    }, status=404)
            else:
                updated_count = models.Expense.recalculate_all_construction_contractor_expenses()  # محاسبه مجدد هزینه‌های پیمان ساختمان برای همه پروژه‌ها
                return Response({
                    'success': True,
                    'message': 'محاسبه مجدد برای همه پروژه‌ها با موفقیت انجام شد',
                    'updated_periods': updated_count  # تعداد دوره‌های به‌روزرسانی شده
                })
                
        except Exception as e:
            logger.exception("Error in recalculate_construction_contractor for user %s: %s", request.user.username, e)
            return Response({
                'error': f'خطا در محاسبه مجدد هزینه‌های پیمان ساختمان: {str(e)}'
            }, status=500)
    


class InterestRateViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت نرخ‌های سود پروژه
    
    این ViewSet امکان مدیریت کامل نرخ‌های سود روزانه پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف نرخ‌های سود
    - دریافت نرخ سود فعال فعلی
    - مدیریت تاریخ اعمال نرخ‌های سود
    - فعال/غیرفعال کردن نرخ‌های سود
    
    سناریوهای استفاده:
    - تعریف نرخ سود جدید برای پروژه
    - تغییر نرخ سود در تاریخ مشخص
    - دریافت نرخ سود فعال
    - مدیریت تاریخچه تغییرات نرخ سود
    
    مثال‌های کاربرد:
    - برای ایجاد نرخ سود: rate='0.000481925679775', effective_date='1403-01-01'
    - برای دریافت نرخ فعال: GET /api/v1/InterestRate/current/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - نرخ سود به صورت روزانه محاسبه می‌شود
    - فقط یک نرخ سود می‌تواند در هر زمان فعال باشد
    """

    queryset = models.InterestRate.objects.all()
    serializer_class = serializers.InterestRateSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام نرخ‌های سود پروژه جاری

        این متد لیست نرخ‌های سود مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/InterestRate/?page=1

        نکات:
            - فقط نرخ‌های سود پروژه جاری برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد نرخ سود جدید برای پروژه جاری

        این متد نرخ سود جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - rate (الزامی): نرخ سود روزانه (به صورت string)
            - effective_date (الزامی): تاریخ اعمال شمسی (YYYY-MM-DD)
            - description (اختیاری): توضیحات
            - is_active (اختیاری): فعال/غیرفعال (پیش‌فرض: True)

        Returns:
            Response با اطلاعات نرخ سود ایجاد شده (status 201)

        مثال:
            POST /api/v1/InterestRate/
            {
                "rate": "0.000481925679775",
                "effective_date": "1403-01-01",
                "description": "نرخ سود جدید از ابتدای سال 1403",
                "is_active": true
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - تاریخ میلادی به صورت خودکار محاسبه می‌شود
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک نرخ سود خاص

        این متد اطلاعات کامل نرخ سود با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای نرخ سود

        Returns:
            Response با اطلاعات کامل نرخ سود

        مثال:
            GET /api/v1/InterestRate/1/

        نکات:
            - فقط نرخ‌های سود پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل نرخ سود

        این متد امکان تغییر همه فیلدهای یک نرخ سود را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای نرخ سود

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده نرخ سود (status 200)

        مثال:
            PUT /api/v1/InterestRate/1/
            {
                "rate": "0.000500000000000",
                "effective_date": "1403-07-01",
                "is_active": true
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی نرخ سود

        این متد امکان تغییر بخشی از فیلدهای نرخ سود را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای نرخ سود

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده نرخ سود (status 200)

        مثال:
            PATCH /api/v1/InterestRate/1/
            {
                "is_active": false
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف نرخ سود

        این متد نرخ سود را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای نرخ سود

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/InterestRate/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط نرخ‌های سود پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
            - در صورت وجود وابستگی (تراکنش‌ها)، ممکن است حذف ناموفق باشد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """دریافت نرخ سود فعال فعلی برای پروژه فعال"""
        # دریافت پروژه جاری از session
        from construction.project_manager import ProjectManager
        active_project = ProjectManager.get_current_project(request)  # پروژه جاری
        if not active_project:
            return Response({
                'error': 'هیچ پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید.'
            }, status=400)
        
        current_rate = models.InterestRate.get_current_rate(project=active_project)  # نرخ سود فعال فعلی
        if current_rate:
            serializer = self.get_serializer(current_rate)  # سریالایزر نرخ سود
            return Response(serializer.data)
        else:
            return Response({'error': 'هیچ نرخ سود فعالی یافت نشد'}, status=404)


class UnitViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت واحدهای مسکونی پروژه
    
    این ViewSet امکان مدیریت کامل واحدهای مسکونی پروژه را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف واحدها
    - دریافت آمار واحدها
    - مدیریت متراژ و قیمت واحدها
    - ارتباط واحدها با سرمایه‌گذاران
    
    سناریوهای استفاده:
    - تعریف واحدهای مسکونی پروژه
    - تنظیم متراژ و قیمت واحدها
    - دریافت آمار کل واحدها
    - مدیریت مالکیت واحدها
    
    مثال‌های کاربرد:
    - برای ایجاد واحد: name='واحد 101', area='120.5', price_per_meter='5000000'
    - برای دریافت آمار: GET /api/v1/Unit/statistics/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - قیمت نهایی به صورت خودکار محاسبه می‌شود (area × price_per_meter)
    - واحدها می‌توانند به چندین سرمایه‌گذار مرتبط باشند
    """

    queryset = models.Unit.objects.all()
    serializer_class = serializers.UnitSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام واحدهای پروژه جاری

        این متد لیست واحدهای مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/Unit/?page=1&page_size=20

        نکات:
            - فقط واحدهای پروژه جاری برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد واحد جدید برای پروژه جاری

        این متد واحد جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - name (الزامی): نام واحد
            - area (الزامی): متراژ واحد (به صورت string)
            - price_per_meter (الزامی): قیمت هر متر (به صورت string)
            - total_price (الزامی): قیمت نهایی (به صورت string)

        Returns:
            Response با اطلاعات واحد ایجاد شده (status 201)

        مثال:
            POST /api/v1/Unit/
            {
                "name": "واحد 101",
                "area": "120.5",
                "price_per_meter": "5000000",
                "total_price": "602500000"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - قیمت نهایی باید برابر area × price_per_meter باشد
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک واحد خاص

        این متد اطلاعات کامل واحد با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای واحد

        Returns:
            Response با اطلاعات کامل واحد

        مثال:
            GET /api/v1/Unit/1/

        نکات:
            - فقط واحدهای پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل واحد

        این متد امکان تغییر همه فیلدهای یک واحد را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای واحد

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده واحد (status 200)

        مثال:
            PUT /api/v1/Unit/1/
            {
                "name": "واحد 101",
                "area": "125.0",
                "price_per_meter": "5500000",
                "total_price": "687500000"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی واحد

        این متد امکان تغییر بخشی از فیلدهای واحد را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای واحد

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده واحد (status 200)

        مثال:
            PATCH /api/v1/Unit/1/
            {
                "price_per_meter": "5500000"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف واحد

        این متد واحد را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای واحد

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/Unit/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط واحدهای پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
            - در صورت وجود وابستگی (سرمایه‌گذاران)، ممکن است حذف ناموفق باشد
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """دریافت آمار کلی واحدها"""
        from django.db.models import Sum, Count
        
        # محاسبه آمار کلی
        stats = self.queryset.aggregate(
            total_units=Count('id'),  # تعداد کل واحدها
            total_area=Sum('area'),  # مجموع مساحت واحدها
            total_price=Sum('total_price')  # مجموع قیمت واحدها
        )  # آمار کلی واحدها
        
        # محاسبه آمار به تفکیک پروژه
        project_stats = []  # لیست آمار به تفکیک پروژه
        for project in models.Project.objects.all():
            project_units = self.queryset.filter(project=project)  # واحدهای این پروژه
            project_stat = project_units.aggregate(
                units_count=Count('id'),  # تعداد واحدهای این پروژه
                total_area=Sum('area'),  # مجموع مساحت واحدهای این پروژه
                total_price=Sum('total_price')  # مجموع قیمت واحدهای این پروژه
            )  # آمار واحدهای این پروژه
            project_stats.append({
                'project_name': project.name,  # نام پروژه
                'project_id': project.id,  # شناسه پروژه
                'units_count': project_stat['units_count'] or 0,  # تعداد واحدها
                'total_area': float(project_stat['total_area'] or 0),  # مجموع مساحت
                'total_price': float(project_stat['total_price'] or 0)  # مجموع قیمت
            })
        
        return Response({
            'total_units': stats['total_units'] or 0,
            'total_area': float(stats['total_area'] or 0),
            'total_price': float(stats['total_price'] or 0),
            'project_breakdown': project_stats
        })

class UnitSpecificExpenseViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت هزینه‌های اختصاصی واحدها
    
    این ViewSet امکان مدیریت کامل هزینه‌های اختصاصی هر واحد را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف هزینه‌های اختصاصی
    - مدیریت هزینه‌های هر واحد به صورت جداگانه
    - فیلتر بر اساس واحد و پروژه
    
    سناریوهای استفاده:
    - ثبت هزینه‌های اختصاصی مالک برای واحد خودش
    - مدیریت هزینه‌های نصب تجهیزات
    - ثبت هزینه‌های تعمیرات اختصاصی
    - دریافت لیست هزینه‌های یک واحد خاص
    
    مثال‌های کاربرد:
    - برای ثبت هزینه نصب کولر: unit=1, title='نصب کولر گازی', amount='5000000'
    - برای فیلتر بر اساس واحد: GET /api/v1/UnitSpecificExpense/?unit=1
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - هزینه‌ها به یک واحد خاص مرتبط هستند
    - این هزینه‌ها جدا از هزینه‌های عمومی پروژه هستند
    """

    queryset = models.UnitSpecificExpense.objects.all()
    serializer_class = serializers.UnitSpecificExpenseSerializer
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]
    filterset_fields = ['unit', 'project']

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام هزینه‌های اختصاصی واحدهای پروژه جاری

        این متد لیست هزینه‌های اختصاصی مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل فیلتر و مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی
            - unit: فیلتر بر اساس شناسه واحد
            - project: فیلتر بر اساس شناسه پروژه

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/UnitSpecificExpense/?unit=1&page=1

        نکات:
            - فقط هزینه‌های اختصاصی پروژه جاری برگردانده می‌شود
            - امکان فیلتر بر اساس واحد
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد هزینه اختصاصی جدید برای واحد

        این متد هزینه اختصاصی جدید را برای یک واحد ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - unit/unit_id (الزامی): شناسه واحد
            - title (الزامی): عنوان هزینه
            - date_shamsi_input (الزامی): تاریخ شمسی (YYYY-MM-DD)
            - amount (الزامی): مبلغ هزینه (به صورت string)
            - description (اختیاری): توضیحات

        Returns:
            Response با اطلاعات هزینه اختصاصی ایجاد شده (status 201)

        مثال:
            POST /api/v1/UnitSpecificExpense/
            {
                "unit": 1,
                "title": "نصب کولر گازی",
                "date_shamsi_input": "1403-07-15",
                "amount": "5000000",
                "description": "نصب کولر گازی در واحد 101"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - تاریخ میلادی به صورت خودکار محاسبه می‌شود
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک هزینه اختصاصی خاص

        این متد اطلاعات کامل هزینه اختصاصی با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای هزینه اختصاصی

        Returns:
            Response با اطلاعات کامل هزینه اختصاصی شامل unit_data و project_data

        مثال:
            GET /api/v1/UnitSpecificExpense/1/

        نکات:
            - فقط هزینه‌های اختصاصی پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل هزینه اختصاصی

        این متد امکان تغییر همه فیلدهای یک هزینه اختصاصی را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای هزینه اختصاصی

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده هزینه اختصاصی (status 200)

        مثال:
            PUT /api/v1/UnitSpecificExpense/1/
            {
                "unit": 1,
                "title": "نصب کولر گازی - به‌روزرسانی شده",
                "date_shamsi_input": "1403-07-15",
                "amount": "6000000"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی هزینه اختصاصی

        این متد امکان تغییر بخشی از فیلدهای هزینه اختصاصی را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای هزینه اختصاصی

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده هزینه اختصاصی (status 200)

        مثال:
            PATCH /api/v1/UnitSpecificExpense/1/
            {
                "amount": "6000000"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف هزینه اختصاصی

        این متد هزینه اختصاصی را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای هزینه اختصاصی

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/UnitSpecificExpense/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط هزینه‌های اختصاصی پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().destroy(request, *args, **kwargs)


class PettyCashTransactionViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت تراکنش‌های تنخواه عوامل اجرایی
    
    این ViewSet امکان مدیریت کامل تراکنش‌های تنخواه عوامل اجرایی را فراهم می‌کند.
    
    قابلیت‌ها:
    - ایجاد، خواندن، به‌روزرسانی و حذف تراکنش‌های تنخواه
    - دریافت وضعیت مالی همه عوامل اجرایی
    - مدیریت دریافت و عودت تنخواه
    - ردیابی تراکنش‌های تنخواه هر عامل اجرایی
    
    سناریوهای استفاده:
    - ثبت دریافت تنخواه توسط عوامل اجرایی
    - ثبت عودت تنخواه به صندوق
    - دریافت وضعیت مالی عوامل اجرایی
    - مدیریت تنخواه مدیر پروژه، سرپرست کارگاه و...
    
    مثال‌های کاربرد:
    - برای ثبت دریافت تنخواه: expense_type='project_manager', transaction_type='receipt', amount='10000000'
    - برای دریافت وضعیت مالی: GET /api/v1/PettyCashTransaction/balances/
    
    نکات مهم:
    - تمام عملیات بر اساس پروژه جاری (active project) انجام می‌شود
    - تراکنش‌ها به یک عامل اجرایی (expense_type) مرتبط هستند
    - انواع تراکنش: receipt (دریافت از صندوق), return (عودت به صندوق)
    - هزینه‌های عوامل اجرایی در Expense ثبت می‌شوند، نه در اینجا
    """
  
    queryset = models.PettyCashTransaction.objects.all()
    authentication_classes = DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [APISecurityPermission]
    serializer_class = serializers.PettyCashTransactionSerializer

    # ===== عملیات CRUD با توضیحات جداگانه =====

    def list(self, request, *args, **kwargs):
        """
        دریافت لیست تمام تراکنش‌های تنخواه پروژه جاری

        این متد لیست تراکنش‌های تنخواه مرتبط با پروژه فعال را برمی‌گرداند.
        نتایج به صورت صفحه‌بندی شده و قابل مرتب‌سازی هستند.

        Query Parameters:
            - page: شماره صفحه (پیش‌فرض: 1)
            - page_size: تعداد رکورد در هر صفحه (پیش‌فرض: 10)
            - ordering: فیلد مرتب‌سازی

        Returns:
            Response با ساختار paginated شامل results, count, next, previous

        مثال:
            GET /api/v1/PettyCashTransaction/?page=1&page_size=20

        نکات:
            - فقط تراکنش‌های تنخواه پروژه جاری برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        ایجاد تراکنش تنخواه جدید برای پروژه جاری

        این متد تراکنش تنخواه جدید را برای پروژه فعال ثبت می‌کند.
        پروژه به صورت خودکار از session کاربر تعیین می‌شود.

        Request Body:
            - expense_type (الزامی): عامل اجرایی (project_manager, facilities_manager, procurement, warehouse, construction_contractor, other)
            - transaction_type (الزامی): نوع تراکنش (receipt, return)
            - amount (الزامی): مبلغ تراکنش (به صورت string)
            - date_shamsi_input (اختیاری): تاریخ شمسی (YYYY-MM-DD)
            - description (اختیاری): توضیحات
            - receipt_number (اختیاری): شماره فیش/رسید

        Returns:
            Response با اطلاعات تراکنش تنخواه ایجاد شده (status 201)

        مثال:
            POST /api/v1/PettyCashTransaction/
            {
                "expense_type": "project_manager",
                "transaction_type": "receipt",
                "amount": "10000000",
                "date_shamsi_input": "1403-07-15",
                "description": "دریافت تنخواه برای خرید مواد اولیه",
                "receipt_number": "F-12345"
            }

        نکات:
            - جزئیات فیلدها در serializer descriptions موجود است
            - پروژه به صورت خودکار از session تنظیم می‌شود
            - تاریخ میلادی به صورت خودکار محاسبه می‌شود
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        دریافت جزئیات یک تراکنش تنخواه خاص

        این متد اطلاعات کامل تراکنش تنخواه با شناسه مشخص شده را برمی‌گرداند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش تنخواه

        Returns:
            Response با اطلاعات کامل تراکنش تنخواه شامل signed_amount

        مثال:
            GET /api/v1/PettyCashTransaction/1/

        نکات:
            - فقط تراکنش‌های تنخواه پروژه جاری قابل دسترسی هستند
            - در صورت عدم دسترسی، خطای 403 برگردانده می‌شود
            - نیاز به احراز هویت دارد
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی کامل تراکنش تنخواه

        این متد امکان تغییر همه فیلدهای یک تراکنش تنخواه را فراهم می‌کند.
        تمام فیلدهای قابل ویرایش باید ارسال شوند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش تنخواه

        Request Body:
            - تمام فیلدهای قابل ویرایش

        Returns:
            Response با اطلاعات به‌روزرسانی شده تراکنش تنخواه (status 200)

        مثال:
            PUT /api/v1/PettyCashTransaction/1/
            {
                "expense_type": "project_manager",
                "transaction_type": "receipt",
                "amount": "12000000",
                "description": "به‌روزرسانی شده"
            }

        نکات:
            - همه فیلدها باید ارسال شوند
            - برای به‌روزرسانی جزئی از PATCH استفاده کنید
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        به‌روزرسانی جزئی تراکنش تنخواه

        این متد امکان تغییر بخشی از فیلدهای تراکنش تنخواه را فراهم می‌کند.
        فقط فیلدهای ارسال شده تغییر می‌کنند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش تنخواه

        Request Body:
            - فیلدهای انتخابی برای به‌روزرسانی

        Returns:
            Response با اطلاعات به‌روزرسانی شده تراکنش تنخواه (status 200)

        مثال:
            PATCH /api/v1/PettyCashTransaction/1/
            {
                "amount": "12000000"
            }

        نکات:
            - فقط فیلدهای ارسال شده تغییر می‌کنند
            - فیلدهای ارسال نشده حفظ می‌شوند
            - انعطاف بیشتری نسبت به PUT دارد
            - جزئیات فیلدها در serializer descriptions موجود است
            - نیاز به احراز هویت دارد
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        حذف تراکنش تنخواه

        این متد تراکنش تنخواه را به‌طور کامل و برگشت‌ناپذیری حذف می‌کند.

        URL Parameters:
            - pk: شناسه یکتای تراکنش تنخواه

        Returns:
            Response خالی با status 204 No Content در صورت موفقیت

        مثال:
            DELETE /api/v1/PettyCashTransaction/1/

        نکات:
            - حذف برگشت‌ناپذیر است
            - فقط تراکنش‌های تنخواه پروژه جاری قابل حذف هستند
            - نیاز به احراز هویت و دسترسی APISecurityPermission دارد
        """
        return super().destroy(request, *args, **kwargs)
  
    @action(detail=False, methods=['get'])
    def balances(self, request):
        """دریافت وضعیت مالی همه عوامل اجرایی"""
        logger.info("User %s requesting petty cash balances", request.user.username)
        try:
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
          
            balances = models.PettyCashTransaction.objects.get_all_balances(active_project)
            logger.info("Successfully returned balances for user %s (project: %s)", request.user.username, active_project.name)
            return Response({'success': True, 'data': balances})
        except Exception as e:
            logger.exception("Error in balances for user %s: %s", request.user.username, e)
            return Response({'error': str(e)}, status=500)
  
    @action(detail=False, methods=['get'])
    def balance_detail(self, request):
        """
        دریافت وضعیت مالی یک عامل اجرایی خاص
        
        این endpoint وضعیت مالی کامل یک عامل اجرایی (expense_type) را
        شامل مانده، مجموع دریافت‌ها، هزینه‌ها و مرجوعی‌ها برمی‌گرداند.
        
        Parameters:
            expense_type (str): نوع عامل اجرایی (الزامی)
        
        Returns:
            Response: شامل:
                - expense_type: نوع عامل اجرایی
                - expense_type_label: برچسب نوع عامل
                - balance: مانده فعلی
                - total_receipts: مجموع دریافت‌ها
                - total_expenses: مجموع هزینه‌ها
                - total_returns: مجموع مرجوعی‌ها
        
        نکات مهم:
        - فقط تراکنش‌های پروژه جاری را شامل می‌شود
        - اگر پروژه جاری وجود نداشته باشد، خطای 400 برمی‌گرداند
        - اگر expense_type ارسال نشود، خطای 400 برمی‌گرداند
        - مانده مثبت = بدهکار (پول در دست دارد)
        - مانده منفی = بستانکار (بدهکار است)
        - تمام مبالغ به تومان هستند
        """
        expense_type = request.query_params.get('expense_type')
        logger.info("User %s requesting balance detail for expense_type: %s", request.user.username, expense_type)
        try:
            if not expense_type:
                return Response({'error': 'expense_type الزامی است'}, status=400)
          
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)
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
                    'expense_type_label': dict(models.Expense.EXPENSE_TYPES)[expense_type],
                    'balance': balance,
                    'total_receipts': total_receipts,
                    'total_expenses': total_expenses,
                    'total_returns': total_returns,
                    'is_creditor': balance < 0,  # بستانکار (طلبکار)
                    'is_debtor': balance > 0,    # بدهکار
                }
            })
        except Exception as e:
            logger.exception("Error in balance_detail for user %s (expense_type: %s): %s", 
                           request.user.username, expense_type, e)
            return Response({'error': str(e)}, status=500)
  
    @action(detail=False, methods=['get'])
    def period_balance(self, request):
        """دریافت وضعیت مالی عامل اجرایی در یک دوره"""
        logger.debug("User %s requesting period balance", request.user.username)
        try:
            expense_type = request.query_params.get('expense_type')
            period_id = request.query_params.get('period_id')
          
            if not all([expense_type, period_id]):
                return Response({'error': 'expense_type و period_id الزامی است'}, status=400)
          
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)
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
            logger.exception("Error in period_balance for user %s: %s", request.user.username, e)
            return Response({'error': str(e)}, status=500)
  
    @action(detail=False, methods=['get'])
    def balance_trend(self, request):
        """ترند زمانی وضعیت مالی عامل اجرایی"""
        logger.info("User %s requesting balance trend", request.user.username)
        try:
            expense_type = request.query_params.get('expense_type')
            if not expense_type:
                return Response({'error': 'expense_type الزامی است'}, status=400)
          
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)
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
          
            # محاسبه آمار کلی (Single Source of Truth) - استفاده از متدهای اصلی برای سازگاری با /balances/
            stats_total_receipts = models.PettyCashTransaction.objects.get_total_receipts(active_project, expense_type)
            stats_total_returns = models.PettyCashTransaction.objects.get_total_returns(active_project, expense_type)
            stats_total_expenses = models.PettyCashTransaction.objects.get_total_expenses(active_project, expense_type)
            final_balance = models.PettyCashTransaction.objects.get_balance(active_project, expense_type)
            
            # محاسبه مجموع مانده دوره‌ای (برای نمایش در نمودار)
            total_period_balance = sum(float(item.get('period_balance', 0) or 0) for item in trend)
          
            return Response({
                'success': True,
                'data': trend,
                'summary': {
                    'total_receipts': stats_total_receipts,
                    'total_returns': stats_total_returns,
                    'total_expenses': stats_total_expenses,
                    'total_period_balance': total_period_balance,
                    'final_balance': final_balance
                }
            })
        except Exception as e:
            logger.exception("Error in balance_trend for user %s: %s", request.user.username, e)
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def detailed_report(self, request):
        """گزارش تفصیلی تراکنش‌های تنخواه با فیلتر و جستجو"""
        logger.info("User %s requesting detailed petty cash report", request.user.username)
        try:
            from construction.project_manager import ProjectManager
            active_project = ProjectManager.get_current_project(request)
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
            logger.exception("Error in detailed_report for user %s: %s", request.user.username, e)
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """آمار کلی تراکنش‌های تنخواه (Single Source of Truth)"""
        logger.info("User %s requesting petty cash statistics", request.user.username)
        try:
            from construction.project_manager import ProjectManager
            from django.db.models import Sum
            
            active_project = ProjectManager.get_current_project(request)
            if not active_project:
                return Response({'error': 'هیچ پروژه فعالی یافت نشد'}, status=400)
            
            # دریافت فیلترها
            expense_type = request.query_params.get('expense_type')
            transaction_type = request.query_params.get('transaction_type')
            
            # QuerySet اولیه
            queryset = models.PettyCashTransaction.objects.filter(project=active_project)
            
            # اعمال فیلترها
            if expense_type:
                queryset = queryset.filter(expense_type=expense_type)
            if transaction_type:
                queryset = queryset.filter(transaction_type=transaction_type)
            
            # محاسبه آمار با استفاده از Manager (Single Source of Truth)
            total_receipts = queryset.filter(transaction_type='receipt').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            total_returns = queryset.filter(transaction_type='return').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            total_receipts = float(total_receipts)
            total_returns = float(total_returns)
            net_amount = total_receipts - total_returns
            
            return Response({
                'success': True,
                'data': {
                    'total_receipts': total_receipts,
                    'total_returns': total_returns,
                    'net_amount': net_amount,
                    'count': queryset.count()
                }
            })
        except Exception as e:
            logger.exception("Error in statistics for user %s: %s", request.user.username, e)
            return Response({'error': str(e)}, status=500)