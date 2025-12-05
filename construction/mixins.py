"""
Mixin classes for construction app ViewSets and Views
"""
from rest_framework.response import Response
from .project_manager import ProjectManager


class ProjectFilterMixin:
    """
    Mixin برای فیلتر خودکار queryset بر اساس پروژه جاری
    
    این mixin به صورت خودکار queryset را بر اساس پروژه جاری کاربر فیلتر می‌کند.
    اگر پروژه جاری وجود نداشته باشد، queryset خالی برمی‌گرداند.
    
    Usage for Django REST Framework ViewSets:
        class MyViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
            queryset = MyModel.objects.all()
            ...
    
    Usage for Django Generic Views (ListView):
        class MyListView(ProjectFilterMixin, generic.ListView):
            model = MyModel
            ...
    """
    
    def get_queryset(self):
        """فیلتر خودکار بر اساس پروژه جاری"""
        import logging
        logger = logging.getLogger(__name__)
        
        queryset = super().get_queryset()
        
        # بررسی اینکه مدل فیلد project دارد
        # این بررسی برای مدل‌هایی که فیلد project ندارند (مثل Project) ضروری است
        if not hasattr(queryset.model, 'project'):
            return queryset
        
        # دریافت پروژه جاری از session
        # این متد ممکن است None برگرداند اگر هیچ پروژه جاری یا فعالی وجود نداشته باشد
        current_project = ProjectManager.get_current_project(self.request)
        
        # لاگ کردن برای دیباگ
        if hasattr(self.request, 'session'):
            project_id_from_session = self.request.session.get('current_project_id')
            logger.debug(f"🔍 ProjectFilterMixin.get_queryset - مدل: {queryset.model.__name__}, project_id از session: {project_id_from_session}, current_project: {current_project}")
        else:
            logger.warning(f"⚠️ ProjectFilterMixin.get_queryset - request.session وجود ندارد")
        
        # فیلتر کردن بر اساس پروژه جاری
        if current_project is not None:
            # اگر پروژه جاری وجود دارد، فقط داده‌های آن پروژه را برگردان
            queryset = queryset.filter(project=current_project)
            logger.debug(f"✅ فیلتر اعمال شد: project={current_project.id} ({current_project.name})")
        else:
            # اگر پروژه جاری وجود ندارد، queryset خالی برگردان
            # این برای جلوگیری از نمایش داده‌های همه پروژه‌ها ضروری است
            queryset = queryset.none()
            logger.warning(f"⚠️ هیچ پروژه جاری یافت نشد - queryset خالی برگردانده شد")
        
        return queryset


class ProjectFormMixin:
    """
    Mixin برای تنظیم خودکار فیلد project در فرم‌ها
    
    این mixin به صورت خودکار فیلد project را در فرم Create و Update تنظیم می‌کند.
    همچنین queryset فیلدهای مرتبط (مثل unit در UnitSpecificExpenseForm) را فیلتر می‌کند.
    
    Usage:
        class MyCreateView(ProjectFormMixin, generic.CreateView):
            model = MyModel
            form_class = MyForm
            ...
    """
    
    def get_form(self, form_class=None):
        """دریافت فرم و تنظیم request برای فرم‌هایی که نیاز دارند"""
        form = super().get_form(form_class)
        # اگر فرم متد set_request دارد، request را تنظیم کن
        if hasattr(form, 'set_request'):
            form.set_request(self.request)
        # همچنین اگر فرم در __init__ می‌تواند request را بپذیرد، از طریق instance تنظیم کن
        # اما بیشتر فرم‌ها request را در __init__ نمی‌پذیرند، پس از form_valid استفاده می‌کنیم
        return form
    
    def form_valid(self, form):
        """تنظیم پروژه جاری در فرم قبل از ذخیره"""
        # دریافت پروژه جاری
        current_project = ProjectManager.get_current_project(self.request)
        
        # بررسی وجود پروژه جاری
        if not current_project:
            from django.contrib import messages
            messages.error(self.request, "لطفاً ابتدا یک پروژه را انتخاب کنید.")
            return self.form_invalid(form)
        
        # بررسی اینکه مدل فیلد project دارد (با استفاده از _meta)
        model = form.instance.__class__
        has_project_field = False
        try:
            from django.core.exceptions import FieldDoesNotExist
            # بررسی وجود فیلد project در مدل
            model._meta.get_field('project')
            has_project_field = True
        except (AttributeError, FieldDoesNotExist, Exception):
            # اگر فیلد project وجود نداشت یا خطایی رخ داد، از super استفاده کن
            has_project_field = False
        
        # اگر مدل فیلد project ندارد، از super استفاده کن
        if not has_project_field:
            return super().form_valid(form)
        
        # تنظیم پروژه جاری در form.instance قبل از save
        # این مهم است که قبل از form.save(commit=False) انجام شود
        form.instance.project = current_project
        
        # استفاده از form.save(commit=False) برای کنترل کامل بر ذخیره
        # این به ما اجازه می‌دهد project را قبل از ذخیره تنظیم کنیم
        self.object = form.save(commit=False)
        
        # اطمینان از اینکه project تنظیم شده است
        # چون form.save(commit=False) فقط فیلدهای form.fields را منتقل می‌کند
        # و project در form.fields نیست، ممکن است reset شده باشد
        if not self.object.project_id:
            self.object.project = current_project
        
        # بررسی نهایی قبل از ذخیره - باید project_id تنظیم شده باشد
        if not self.object.project_id:
            from django.contrib import messages
            messages.error(self.request, "خطا: پروژه تنظیم نشد. لطفاً یک پروژه را انتخاب کنید.")
            return self.form_invalid(form)
        
        # ذخیره instance
        self.object.save()
        
        # ذخیره ManyToMany fields (مثل units در Investor)
        form.save_m2m()
        
        # برگرداندن HttpResponseRedirect
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        messages.success(self.request, 'با موفقیت ذخیره شد.')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_initial(self):
        """تنظیم مقدار اولیه پروژه در فرم"""
        initial = super().get_initial()
        
        # بررسی اینکه مدل فیلد project دارد
        # اگر مدل فیلد project دارد، مقدار اولیه را تنظیم می‌کنیم
        if hasattr(self, 'model'):
            # بررسی اینکه مدل فیلد project دارد
            # استفاده از getattr برای بررسی امن
            if hasattr(self.model, '_meta') and hasattr(self.model._meta, 'get_field'):
                try:
                    field = self.model._meta.get_field('project')
                    current_project = ProjectManager.get_current_project(self.request)
                    if current_project:
                        initial['project'] = current_project.id
                except:
                    # اگر فیلد project وجود نداشت، هیچ کاری انجام نده
                    pass
            elif hasattr(self.model, 'project'):
                # روش جایگزین برای بررسی
                current_project = ProjectManager.get_current_project(self.request)
                if current_project:
                    initial['project'] = current_project.id
        
        return initial

