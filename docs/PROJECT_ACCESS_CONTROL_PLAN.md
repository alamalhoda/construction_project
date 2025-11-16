# برنامه جامع: سیستم مدیریت دسترسی به پروژه‌ها با تعریف نقش

## 📋 فهرست مطالب
1. [وضعیت فعلی سیستم](#وضعیت-فعلی-سیستم)
2. [اهداف و نیازمندی‌ها](#اهداف-و-نیازمندی‌ها)
3. [طراحی مدل‌های داده](#طراحی-مدل‌های-داده)
4. [سیستم نقش‌ها و مجوزها](#سیستم-نقش‌ها-و-مجوزها)
5. [Backend Implementation](#backend-implementation)
6. [API Development](#api-development)
7. [Frontend Implementation](#frontend-implementation)
8. [Testing Strategy](#testing-strategy)
9. [Migration Plan](#migration-plan)
10. [مراحل پیاده‌سازی](#مراحل-پیاده‌سازی)
11. [نکات امنیتی](#نکات-امنیتی)

---

## 🎯 وضعیت فعلی سیستم

### ✅ پیاده‌سازی شده:
- سیستم چند پروژه‌ای با `ProjectManager` برای مدیریت پروژه جاری
- همه مدل‌ها دارای فیلد `project` هستند
- `ProjectFilterMixin` برای فیلتر خودکار queryset
- `ProjectFormMixin` برای تنظیم خودکار پروژه در فرم‌ها
- فیلتر پروژه در تمام APIها و Views
- مدل `UserProfile` با فیلد `project` (اما محدود به یک پروژه)

### ❌ نیاز به پیاده‌سازی:
- سیستم مدیریت دسترسی کاربران به پروژه‌ها
- تعریف نقش برای هر کاربر در هر پروژه
- بررسی دسترسی قبل از دسترسی به پروژه
- محدود کردن لیست پروژه‌ها به پروژه‌های مجاز
- UI برای مدیریت دسترسی‌ها
- API برای مدیریت دسترسی‌ها

---

## 🎯 اهداف و نیازمندی‌ها

### اهداف اصلی:
1. **کنترل دسترسی**: هر کاربر فقط به پروژه‌هایی دسترسی داشته باشد که به او اختصاص داده شده
2. **نقش‌های مختلف**: تعریف نقش برای هر کاربر در هر پروژه (مالک، مدیر، ناظر، عضو)
3. **مجوزهای تفکیک شده**: تعریف مجوزهای ویرایش، حذف، مشاهده برای هر نقش
4. **مدیریت آسان**: امکان اضافه/حذف کاربران به پروژه‌ها از طریق UI
5. **سازگاری با سیستم فعلی**: عدم تغییر در عملکرد سیستم فعلی

### نیازمندی‌های کاربری:
- کاربران فقط پروژه‌های مجاز خود را ببینند
- مدیران پروژه بتوانند کاربران را به پروژه اضافه/حذف کنند
- Superuser و Staff به همه پروژه‌ها دسترسی داشته باشند
- کاربران عادی نتوانند پروژه‌های دیگر را ببینند

---

## 📊 طراحی مدل‌های داده

### 1. مدل ProjectAccess

**فایل:** `construction/models.py`

```python
class ProjectAccess(models.Model):
    """
    مدل دسترسی کاربران به پروژه‌ها
    هر رکورد نشان‌دهنده دسترسی یک کاربر به یک پروژه با نقش مشخص است
    """
    ROLE_CHOICES = [
        ('owner', 'مالک پروژه'),
        ('manager', 'مدیر پروژه'),
        ('viewer', 'ناظر'),
        ('member', 'عضو'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='project_accesses',
        verbose_name="کاربر"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='accesses',
        verbose_name="پروژه"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name="نقش"
    )
    can_view = models.BooleanField(
        default=True,
        verbose_name="مجوز مشاهده",
        help_text="آیا کاربر می‌تواند پروژه را مشاهده کند؟"
    )
    can_edit = models.BooleanField(
        default=False,
        verbose_name="مجوز ویرایش",
        help_text="آیا کاربر می‌تواند داده‌های پروژه را ویرایش کند؟"
    )
    can_delete = models.BooleanField(
        default=False,
        verbose_name="مجوز حذف",
        help_text="آیا کاربر می‌تواند داده‌های پروژه را حذف کند؟"
    )
    can_manage_access = models.BooleanField(
        default=False,
        verbose_name="مجوز مدیریت دسترسی",
        help_text="آیا کاربر می‌تواند دسترسی سایر کاربران را مدیریت کند؟"
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_accesses',
        verbose_name="اعطا شده توسط",
        help_text="کاربری که این دسترسی را اعطا کرده است"
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ اعطا"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="یادداشت",
        help_text="یادداشت‌های اضافی درباره این دسترسی"
    )
    
    class Meta:
        verbose_name = "دسترسی به پروژه"
        verbose_name_plural = "دسترسی‌های پروژه"
        unique_together = ['user', 'project']
        indexes = [
            models.Index(fields=['user', 'project']),
            models.Index(fields=['project', 'role']),
        ]
        ordering = ['-granted_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        # تنظیم خودکار مجوزها بر اساس نقش
        if not kwargs.get('skip_role_permissions', False):
            self.set_permissions_by_role()
        super().save(*args, **kwargs)
    
    def set_permissions_by_role(self):
        """تنظیم خودکار مجوزها بر اساس نقش"""
        role_permissions = {
            'owner': {
                'can_view': True,
                'can_edit': True,
                'can_delete': True,
                'can_manage_access': True,
            },
            'manager': {
                'can_view': True,
                'can_edit': True,
                'can_delete': False,
                'can_manage_access': True,
            },
            'viewer': {
                'can_view': True,
                'can_edit': False,
                'can_delete': False,
                'can_manage_access': False,
            },
            'member': {
                'can_view': True,
                'can_edit': False,
                'can_delete': False,
                'can_manage_access': False,
            },
        }
        
        permissions = role_permissions.get(self.role, {})
        self.can_view = permissions.get('can_view', True)
        self.can_edit = permissions.get('can_edit', False)
        self.can_delete = permissions.get('can_delete', False)
        self.can_manage_access = permissions.get('can_manage_access', False)
```

### 2. مدل UserProjectPreference

**فایل:** `construction/models.py`

```python
class UserProjectPreference(models.Model):
    """
    تنظیمات و ترجیحات کاربر برای پروژه‌ها
    شامل پروژه پیش‌فرض، پروژه‌های اخیر، و پروژه‌های مورد علاقه
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='project_preferences',
        verbose_name="کاربر"
    )
    default_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_users',
        verbose_name="پروژه پیش‌فرض",
        help_text="پروژه‌ای که به صورت پیش‌فرض برای کاربر انتخاب می‌شود"
    )
    last_viewed_projects = models.JSONField(
        default=list,
        verbose_name="پروژه‌های اخیر",
        help_text="لیست ID پروژه‌های اخیری که کاربر مشاهده کرده (حداکثر 10)"
    )
    favorite_projects = models.ManyToManyField(
        Project,
        related_name='favorited_by',
        blank=True,
        verbose_name="پروژه‌های مورد علاقه"
    )
    
    class Meta:
        verbose_name = "تنظیمات پروژه کاربر"
        verbose_name_plural = "تنظیمات پروژه کاربران"
    
    def __str__(self):
        return f"تنظیمات پروژه {self.user.get_full_name()}"
    
    def add_to_recent(self, project_id):
        """اضافه کردن پروژه به لیست اخیر"""
        if not self.last_viewed_projects:
            self.last_viewed_projects = []
        
        # حذف اگر قبلاً وجود داشت
        if project_id in self.last_viewed_projects:
            self.last_viewed_projects.remove(project_id)
        
        # اضافه کردن به ابتدای لیست
        self.last_viewed_projects.insert(0, project_id)
        
        # نگه داشتن فقط 10 پروژه اخیر
        self.last_viewed_projects = self.last_viewed_projects[:10]
        self.save()
```

---

## 🔐 سیستم نقش‌ها و مجوزها

### نقش‌های پیش‌فرض:

#### 1. **Owner (مالک پروژه)**
- ✅ مشاهده کامل پروژه
- ✅ ویرایش همه داده‌ها
- ✅ حذف داده‌ها
- ✅ مدیریت دسترسی سایر کاربران
- ✅ حذف پروژه

#### 2. **Manager (مدیر پروژه)**
- ✅ مشاهده کامل پروژه
- ✅ ویرایش داده‌ها
- ❌ حذف داده‌ها
- ✅ مدیریت دسترسی سایر کاربران
- ❌ حذف پروژه

#### 3. **Viewer (ناظر)**
- ✅ مشاهده داده‌ها
- ❌ ویرایش
- ❌ حذف
- ❌ مدیریت دسترسی

#### 4. **Member (عضو)**
- ✅ مشاهده داده‌ها (محدود)
- ❌ ویرایش
- ❌ حذف
- ❌ مدیریت دسترسی

### قوانین دسترسی:

1. **Superuser/Staff**: به همه پروژه‌ها دسترسی کامل دارند
2. **کاربر عادی**: فقط پروژه‌هایی که `ProjectAccess` دارند
3. **پروژه جدید**: فقط سازنده پروژه به عنوان Owner دسترسی دارد
4. **بدون دسترسی**: اگر کاربر `ProjectAccess` نداشته باشد، پروژه را نمی‌بیند

---

## 🛠️ Backend Implementation

### 1. به‌روزرسانی ProjectManager

**فایل:** `construction/project_manager.py`

```python
from .models import Project, ProjectAccess, UserProjectPreference

class ProjectManager:
    """کلاس helper برای مدیریت پروژه کاربر"""
    
    @staticmethod
    def get_current_project(request):
        """دریافت پروژه جاری از session"""
        project_id = request.session.get('current_project_id')
        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if project:
                # بررسی دسترسی کاربر به پروژه
                if ProjectManager.has_project_access(request.user, project):
                    return project
        return None
    
    @staticmethod
    def set_current_project(request, project_id):
        """تنظیم پروژه جاری در session با بررسی دسترسی"""
        project = Project.objects.filter(id=project_id).first()
        if not project:
            raise ValueError("پروژه یافت نشد")
        
        # بررسی دسترسی
        if not ProjectManager.has_project_access(request.user, project):
            raise PermissionError("شما به این پروژه دسترسی ندارید")
        
        request.session['current_project_id'] = project_id
        
        # اضافه به لیست پروژه‌های اخیر
        ProjectManager.add_to_recent_projects(request.user, project_id)
    
    @staticmethod
    def has_project_access(user, project):
        """بررسی دسترسی کاربر به پروژه"""
        # Superuser و Staff به همه پروژه‌ها دسترسی دارند
        if user.is_superuser or user.is_staff:
            return True
        
        # بررسی وجود ProjectAccess
        return ProjectAccess.objects.filter(
            user=user,
            project=project,
            can_view=True
        ).exists()
    
    @staticmethod
    def can_edit_project(user, project):
        """بررسی مجوز ویرایش پروژه"""
        if user.is_superuser or user.is_staff:
            return True
        
        return ProjectAccess.objects.filter(
            user=user,
            project=project,
            can_edit=True
        ).exists()
    
    @staticmethod
    def can_delete_project(user, project):
        """بررسی مجوز حذف پروژه"""
        if user.is_superuser or user.is_staff:
            return True
        
        return ProjectAccess.objects.filter(
            user=user,
            project=project,
            can_delete=True
        ).exists()
    
    @staticmethod
    def can_manage_access(user, project):
        """بررسی مجوز مدیریت دسترسی"""
        if user.is_superuser or user.is_staff:
            return True
        
        return ProjectAccess.objects.filter(
            user=user,
            project=project,
            can_manage_access=True
        ).exists()
    
    @staticmethod
    def get_user_projects(user):
        """دریافت پروژه‌های مجاز کاربر"""
        if user.is_superuser or user.is_staff:
            return Project.objects.all().order_by('name')
        
        # دریافت پروژه‌هایی که کاربر به آن‌ها دسترسی دارد
        project_ids = ProjectAccess.objects.filter(
            user=user,
            can_view=True
        ).values_list('project_id', flat=True)
        
        return Project.objects.filter(id__in=project_ids).order_by('name')
    
    @staticmethod
    def get_user_role(user, project):
        """دریافت نقش کاربر در پروژه"""
        if user.is_superuser or user.is_staff:
            return 'owner'
        
        access = ProjectAccess.objects.filter(
            user=user,
            project=project
        ).first()
        
        return access.role if access else None
    
    @staticmethod
    def add_to_recent_projects(user, project_id):
        """اضافه کردن پروژه به لیست اخیر"""
        pref, created = UserProjectPreference.objects.get_or_create(user=user)
        pref.add_to_recent(project_id)
    
    @staticmethod
    def get_default_project(user):
        """دریافت پروژه پیش‌فرض کاربر"""
        try:
            pref = UserProjectPreference.objects.get(user=user)
            if pref.default_project:
                # بررسی دسترسی
                if ProjectManager.has_project_access(user, pref.default_project):
                    return pref.default_project
        except UserProjectPreference.DoesNotExist:
            pass
        
        # اگر پروژه پیش‌فرض نبود، اولین پروژه مجاز را برگردان
        user_projects = ProjectManager.get_user_projects(user)
        return user_projects.first() if user_projects.exists() else None
```

### 2. ایجاد Permission Classes

**فایل:** `construction/permissions.py` (ایجاد جدید)

```python
"""
Permission Classes برای کنترل دسترسی به پروژه‌ها
"""
from rest_framework import permissions
from .models import ProjectAccess
from .project_manager import ProjectManager

class ProjectAccessPermission(permissions.BasePermission):
    """بررسی دسترسی کاربر به پروژه"""
    
    def has_permission(self, request, view):
        # Superuser و Staff همیشه دسترسی دارند
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # دریافت project_id از query params یا session
        project_id = request.query_params.get('project_id')
        if not project_id:
            project_id = request.session.get('current_project_id')
        
        if project_id:
            from .models import Project
            try:
                project = Project.objects.get(id=project_id)
                return ProjectManager.has_project_access(request.user, project)
            except Project.DoesNotExist:
                return False
        
        return True  # اگر project_id نبود، اجازه بده (ممکن است برای list view باشد)

class ProjectEditPermission(permissions.BasePermission):
    """بررسی مجوز ویرایش پروژه"""
    
    def has_permission(self, request, view):
        # فقط GET, HEAD, OPTIONS نیاز به check ندارند
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        project_id = request.data.get('project_id') or request.query_params.get('project_id')
        if project_id:
            from .models import Project
            try:
                project = Project.objects.get(id=project_id)
                return ProjectManager.can_edit_project(request.user, project)
            except Project.DoesNotExist:
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # اگر object فیلد project دارد
        if hasattr(obj, 'project'):
            return ProjectManager.can_edit_project(request.user, obj.project)
        return True

class ProjectDeletePermission(permissions.BasePermission):
    """بررسی مجوز حذف پروژه"""
    
    def has_permission(self, request, view):
        if request.method != 'DELETE':
            return True
        
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # بررسی برای DELETE request
        return False  # به صورت پیش‌فرض، نیاز به بررسی object دارد
    
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True
        
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        if hasattr(obj, 'project'):
            return ProjectManager.can_delete_project(request.user, obj.project)
        return False

class ProjectManageAccessPermission(permissions.BasePermission):
    """بررسی مجوز مدیریت دسترسی پروژه"""
    
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        project_id = request.data.get('project_id') or request.query_params.get('project_id')
        if project_id:
            from .models import Project
            try:
                project = Project.objects.get(id=project_id)
                return ProjectManager.can_manage_access(request.user, project)
            except Project.DoesNotExist:
                return False
        
        return False
```

### 3. به‌روزرسانی Mixins

**فایل:** `construction/mixins.py`

```python
class ProjectFilterMixin:
    """Mixin برای فیلتر خودکار queryset بر اساس پروژه جاری"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # بررسی اینکه مدل فیلد project دارد
        if not hasattr(queryset.model, 'project'):
            return queryset
        
        # دریافت پروژه‌های مجاز کاربر
        from .project_manager import ProjectManager
        user_projects = ProjectManager.get_user_projects(self.request.user)
        
        # فیلتر بر اساس پروژه‌های مجاز
        if user_projects.exists():
            queryset = queryset.filter(project__in=user_projects)
        else:
            # اگر کاربر هیچ پروژه‌ای ندارد، queryset خالی برگردان
            queryset = queryset.none()
        
        # اگر پروژه جاری مشخص بود، فقط آن را برگردان
        current_project = ProjectManager.get_current_project(self.request)
        if current_project:
            queryset = queryset.filter(project=current_project)
        
        return queryset

class ProjectAccessMixin:
    """Mixin برای بررسی دسترسی به پروژه"""
    
    def dispatch(self, request, *args, **kwargs):
        from .project_manager import ProjectManager
        current_project = ProjectManager.get_current_project(request)
        
        if current_project and not ProjectManager.has_project_access(request.user, current_project):
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, 'شما به این پروژه دسترسی ندارید')
            return redirect('user_dashboard')
        
        return super().dispatch(request, *args, **kwargs)
```

### 4. به‌روزرسانی Views

**فایل:** `construction/views.py`

```python
from .mixins import ProjectFilterMixin, ProjectAccessMixin

class InvestorListView(ProjectAccessMixin, ProjectFilterMixin, generic.ListView):
    model = models.Investor
    # ...

class ExpenseListView(ProjectAccessMixin, ProjectFilterMixin, generic.ListView):
    model = models.Expense
    # ...
```

### 5. Signal برای ایجاد ProjectAccess

**فایل:** `construction/signals.py` (ایجاد جدید)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Project, ProjectAccess

@receiver(post_save, sender=Project)
def create_project_access_for_creator(sender, instance, created, **kwargs):
    """ایجاد دسترسی Owner برای سازنده پروژه"""
    if created:
        # اگر در request context هستیم، سازنده را از request بگیر
        # در غیر این صورت، اولین superuser را به عنوان owner قرار بده
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # این کار بهتر است در view انجام شود، اما اگر نیاز بود:
        # owner = User.objects.filter(is_superuser=True).first()
        # if owner:
        #     ProjectAccess.objects.create(
        #         user=owner,
        #         project=instance,
        #         role='owner'
        #     )
        pass
```

---

## 🌐 API Development

### 1. Serializers

**فایل:** `construction/serializers.py`

```python
class ProjectAccessSerializer(serializers.ModelSerializer):
    """Serializer برای ProjectAccess"""
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = models.ProjectAccess
        fields = [
            'id', 'user', 'user_full_name', 'user_username',
            'project', 'project_name', 'role', 'role_display',
            'can_view', 'can_edit', 'can_delete', 'can_manage_access',
            'granted_by', 'granted_at', 'notes'
        ]
        read_only_fields = ['granted_at']

class UserProjectPreferenceSerializer(serializers.ModelSerializer):
    """Serializer برای UserProjectPreference"""
    default_project_name = serializers.CharField(source='default_project.name', read_only=True)
    
    class Meta:
        model = models.UserProjectPreference
        fields = [
            'id', 'user', 'default_project', 'default_project_name',
            'last_viewed_projects', 'favorite_projects'
        ]
```

### 2. ViewSets

**فایل:** `construction/api.py`

```python
from .models import ProjectAccess, UserProjectPreference
from .serializers import ProjectAccessSerializer, UserProjectPreferenceSerializer
from .permissions import ProjectManageAccessPermission

class ProjectAccessViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت دسترسی‌های پروژه"""
    queryset = ProjectAccess.objects.all()
    serializer_class = ProjectAccessSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectManageAccessPermission]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # کاربران فقط دسترسی‌های پروژه‌هایی که می‌توانند مدیریت کنند را ببینند
        if not self.request.user.is_superuser and not self.request.user.is_staff:
            from .project_manager import ProjectManager
            manageable_projects = Project.objects.filter(
                accesses__user=self.request.user,
                accesses__can_manage_access=True
            ).values_list('id', flat=True)
            queryset = queryset.filter(project_id__in=manageable_projects)
        
        return queryset.select_related('user', 'project', 'granted_by')
    
    def perform_create(self, serializer):
        """تنظیم granted_by به کاربر فعلی"""
        serializer.save(granted_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def user_projects(self, request):
        """دریافت لیست پروژه‌های کاربر با نقش‌ها"""
        from .project_manager import ProjectManager
        user_projects = ProjectManager.get_user_projects(request.user)
        
        projects_data = []
        for project in user_projects:
            role = ProjectManager.get_user_role(request.user, project)
            access = ProjectAccess.objects.filter(user=request.user, project=project).first()
            
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'role': role,
                'can_edit': access.can_edit if access else False,
                'can_delete': access.can_delete if access else False,
                'can_manage_access': access.can_manage_access if access else False,
            })
        
        return Response({'projects': projects_data})

class UserProjectPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet برای تنظیمات پروژه کاربر"""
    queryset = UserProjectPreference.objects.all()
    serializer_class = UserProjectPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # کاربران فقط تنظیمات خود را ببینند
        if self.request.user.is_superuser or self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)
```

### 3. به‌روزرسانی ProjectViewSet

**فایل:** `construction/api.py`

```python
class ProjectViewSet(viewsets.ModelViewSet):
    # ...
    
    def get_queryset(self):
        """فیلتر پروژه‌ها بر اساس دسترسی کاربر"""
        queryset = super().get_queryset()
        
        # Superuser و Staff همه پروژه‌ها را می‌بینند
        if self.request.user.is_superuser or self.request.user.is_staff:
            return queryset
        
        # کاربران عادی فقط پروژه‌های مجاز را می‌بینند
        from .project_manager import ProjectManager
        return ProjectManager.get_user_projects(self.request.user)
    
    @action(detail=False, methods=['post'])
    def switch(self, request):
        """تغییر پروژه جاری با بررسی دسترسی"""
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response({'error': 'project_id الزامی است'}, status=400)
        
        try:
            from .project_manager import ProjectManager
            ProjectManager.set_current_project(request, project_id)
            project = Project.objects.get(id=project_id)
            
            return Response({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                },
                'message': 'پروژه با موفقیت تغییر کرد'
            })
        except PermissionError as e:
            return Response({'error': str(e)}, status=403)
        except Project.DoesNotExist:
            return Response({'error': 'پروژه یافت نشد'}, status=404)
```

---

## 🎨 Frontend Implementation

### 1. Project Switcher Component (به‌روزرسانی)

**فایل:** `templates/components/project_switcher.html`

```html
<div class="project-switcher">
    <div class="current-project" onclick="toggleProjectDropdown()">
        <i class="fas fa-project-diagram"></i>
        <span class="project-name">{{ current_project.name|default:"هیچ پروژه‌ای انتخاب نشده" }}</span>
        {% if current_project %}
            <span class="role-badge">{{ current_role|default:"عضو" }}</span>
        {% endif %}
        <i class="fas fa-chevron-down"></i>
    </div>
    
    <div class="project-dropdown" id="projectDropdown" style="display: none;">
        <div class="project-list">
            {% for project in user_projects %}
            <div class="project-item {% if project.id == current_project.id %}active{% endif %}" 
                 onclick="switchProject({{ project.id }})">
                <div class="project-info">
                    <span class="project-name">{{ project.name }}</span>
                    {% with access=project.accesses.all|first %}
                        {% if access %}
                            <span class="role-badge role-{{ access.role }}">{{ access.get_role_display }}</span>
                        {% endif %}
                    {% endwith %}
                </div>
                {% if project.id == current_project.id %}
                <i class="fas fa-check"></i>
                {% endif %}
            </div>
            {% empty %}
            <div class="no-projects">
                <p>شما به هیچ پروژه‌ای دسترسی ندارید</p>
            </div>
            {% endfor %}
        </div>
        
        {% if can_create_project %}
        <div class="project-actions">
            <a href="/construction/Project/create/">
                <i class="fas fa-plus"></i>
                پروژه جدید
            </a>
        </div>
        {% endif %}
    </div>
</div>
```

### 2. Project Access Management Page

**فایل:** `templates/construction/project_access_list.html` (ایجاد جدید)

```html
{% extends 'base.html' %}
{% block title %}مدیریت دسترسی‌های پروژه{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h1>
                <i class="fas fa-users-cog"></i>
                مدیریت دسترسی‌های پروژه: {{ project.name }}
            </h1>
            
            <!-- فرم افزودن کاربر -->
            <div class="card mb-4">
                <div class="card-header">
                    <h3>افزودن کاربر به پروژه</h3>
                </div>
                <div class="card-body">
                    <form id="addUserForm">
                        {% csrf_token %}
                        <div class="row">
                            <div class="col-md-4">
                                <label for="user_id">کاربر:</label>
                                <select id="user_id" name="user_id" class="form-control" required>
                                    <option value="">-- انتخاب کاربر --</option>
                                    <!-- لیست کاربران -->
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label for="role">نقش:</label>
                                <select id="role" name="role" class="form-control" required>
                                    <option value="member">عضو</option>
                                    <option value="viewer">ناظر</option>
                                    <option value="manager">مدیر پروژه</option>
                                    <option value="owner">مالک پروژه</option>
                                </select>
                            </div>
                            <div class="col-md-5">
                                <label>&nbsp;</label>
                                <button type="submit" class="btn btn-primary btn-block">
                                    <i class="fas fa-plus"></i>
                                    افزودن کاربر
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- لیست دسترسی‌ها -->
            <div class="card">
                <div class="card-header">
                    <h3>لیست کاربران و دسترسی‌ها</h3>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>کاربر</th>
                                <th>نقش</th>
                                <th>مشاهده</th>
                                <th>ویرایش</th>
                                <th>حذف</th>
                                <th>مدیریت دسترسی</th>
                                <th>تاریخ اعطا</th>
                                <th>عملیات</th>
                            </tr>
                        </thead>
                        <tbody id="accessList">
                            <!-- لیست از طریق API بارگذاری می‌شود -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// JavaScript برای مدیریت دسترسی‌ها
// ...
</script>
{% endblock %}
```

### 3. Context Processor (به‌روزرسانی)

**فایل:** `construction_project/context_processors.py`

```python
def project_context(request):
    """اضافه کردن اطلاعات پروژه به تمام templates"""
    from construction.project_manager import ProjectManager
    from construction.models import Project
    
    context = {
        'current_project': None,
        'current_role': None,
        'user_projects': [],
    }
    
    if request.user.is_authenticated:
        current_project = ProjectManager.get_current_project(request)
        context['current_project'] = current_project
        
        if current_project:
            context['current_role'] = ProjectManager.get_user_role(request.user, current_project)
        
        context['user_projects'] = ProjectManager.get_user_projects(request.user)
    
    return context
```

---

## 🧪 Testing Strategy

### 1. Unit Tests

**فایل:** `construction/tests/test_project_access.py` (ایجاد جدید)

```python
from django.test import TestCase
from django.contrib.auth.models import User
from construction.models import Project, ProjectAccess
from construction.project_manager import ProjectManager

class ProjectAccessTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', password='test')
        self.user2 = User.objects.create_user('user2', password='test')
        self.superuser = User.objects.create_superuser('admin', password='test')
        self.project = Project.objects.create(name='پروژه تست')
    
    def test_create_project_access(self):
        """تست ایجاد دسترسی"""
        access = ProjectAccess.objects.create(
            user=self.user1,
            project=self.project,
            role='manager'
        )
        self.assertEqual(access.role, 'manager')
        self.assertTrue(access.can_view)
        self.assertTrue(access.can_edit)
    
    def test_has_project_access(self):
        """تست بررسی دسترسی"""
        ProjectAccess.objects.create(
            user=self.user1,
            project=self.project,
            role='viewer'
        )
        
        self.assertTrue(ProjectManager.has_project_access(self.user1, self.project))
        self.assertFalse(ProjectManager.has_project_access(self.user2, self.project))
        self.assertTrue(ProjectManager.has_project_access(self.superuser, self.project))
    
    def test_get_user_projects(self):
        """تست دریافت پروژه‌های کاربر"""
        ProjectAccess.objects.create(
            user=self.user1,
            project=self.project,
            role='member'
        )
        
        user_projects = ProjectManager.get_user_projects(self.user1)
        self.assertIn(self.project, user_projects)
```

### 2. Integration Tests

```python
class ProjectAccessIntegrationTestCase(TestCase):
    """تست‌های یکپارچه برای دسترسی به پروژه"""
    
    def test_project_filter_in_view(self):
        """تست فیلتر پروژه در View"""
        # ...
    
    def test_api_project_access(self):
        """تست دسترسی به API پروژه"""
        # ...
```

---

## 🔄 Migration Plan

### 1. Migration برای مدل‌های جدید

**فایل:** `construction/migrations/XXXX_add_project_access.py`

```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('construction', 'XXXX_previous_migration'),
        ('auth', 'XXXX_previous_auth_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAccess',
            fields=[
                ('id', models.AutoField(...)),
                ('role', models.CharField(...)),
                ('can_view', models.BooleanField(...)),
                # ...
            ],
        ),
        migrations.CreateModel(
            name='UserProjectPreference',
            fields=[
                # ...
            ],
        ),
        migrations.AddIndex(
            model_name='projectaccess',
            index=models.Index(fields=['user', 'project'], name='project_access_user_project_idx'),
        ),
    ]
```

### 2. Data Migration

**فایل:** `construction/migrations/XXXX_populate_project_access.py`

```python
def populate_project_access(apps, schema_editor):
    """ایجاد دسترسی پیش‌فرض برای کاربران موجود"""
    User = apps.get_model('auth', 'User')
    Project = apps.get_model('construction', 'Project')
    ProjectAccess = apps.get_model('construction', 'ProjectAccess')
    UserProfile = apps.get_model('construction', 'UserProfile')
    
    # برای هر UserProfile که project دارد، ProjectAccess ایجاد کن
    for profile in UserProfile.objects.exclude(project__isnull=True):
        ProjectAccess.objects.get_or_create(
            user=profile.user,
            project=profile.project,
            defaults={
                'role': 'owner' if profile.is_technical_admin else 'member',
            }
        )
    
    # برای superuserها، دسترسی به همه پروژه‌ها
    for user in User.objects.filter(is_superuser=True):
        for project in Project.objects.all():
            ProjectAccess.objects.get_or_create(
                user=user,
                project=project,
                defaults={'role': 'owner'}
            )
```

---

## 📋 مراحل پیاده‌سازی

### مرحله 1: Backend Foundation (هفته 1)

**اولویت: بالا**

1. ✅ ایجاد مدل‌های `ProjectAccess` و `UserProjectPreference`
2. ✅ ایجاد Migration ها
3. ✅ به‌روزرسانی `ProjectManager` با متدهای بررسی دسترسی
4. ✅ ایجاد `permissions.py` با Permission Classes
5. ✅ به‌روزرسانی Mixins
6. ✅ تست Backend

**تخمین زمان:** 3-4 روز

**فایل‌های جدید:**
- `construction/models.py` (افزودن مدل‌ها)
- `construction/permissions.py` (ایجاد جدید)
- `construction/migrations/XXXX_add_project_access.py`
- `construction/migrations/XXXX_populate_project_access.py`

**فایل‌های به‌روزرسانی:**
- `construction/project_manager.py`
- `construction/mixins.py`
- `construction/views.py` (افزودن ProjectAccessMixin)

### مرحله 2: API Development (هفته 1-2)

**اولویت: بالا**

1. ✅ ایجاد Serializers برای ProjectAccess و UserProjectPreference
2. ✅ ایجاد ViewSet برای ProjectAccess
3. ✅ ایجاد ViewSet برای UserProjectPreference
4. ✅ به‌روزرسانی ProjectViewSet برای فیلتر دسترسی
5. ✅ تست API

**تخمین زمان:** 2-3 روز

**فایل‌های به‌روزرسانی:**
- `construction/serializers.py`
- `construction/api.py`
- `construction/urls.py`

### مرحله 3: Frontend Components (هفته 2)

**اولویت: متوسط**

1. ✅ به‌روزرسانی Project Switcher برای نمایش نقش
2. ✅ ایجاد صفحه مدیریت دسترسی‌های پروژه
3. ✅ به‌روزرسانی Context Processor
4. ✅ اضافه کردن JavaScript برای مدیریت دسترسی‌ها
5. ✅ تست UI

**تخمین زمان:** 3-4 روز

**فایل‌های جدید:**
- `templates/construction/project_access_list.html`
- `static/js/project-access-manager.js`

**فایل‌های به‌روزرسانی:**
- `templates/components/project_switcher.html`
- `construction_project/context_processors.py`

### مرحله 4: Testing & Security (هفته 2-3)

**اولویت: بالا**

1. ✅ نوشتن Unit Tests
2. ✅ نوشتن Integration Tests
3. ✅ تست امنیتی (Security Testing)
4. ✅ بررسی Edge Cases
5. ✅ Load Testing

**تخمین زمان:** 2-3 روز

**فایل‌های جدید:**
- `construction/tests/test_project_access.py`
- `construction/tests/test_project_access_integration.py`

### مرحله 5: Documentation & Deployment (هفته 3)

**اولویت: متوسط**

1. ✅ نوشتن مستندات
2. ✅ به‌روزرسانی README
3. ✅ Migration به Production
4. ✅ تست در Production
5. ✅ آموزش کاربران

**تخمین زمان:** 2-3 روز

---

## 🔒 نکات امنیتی

### 1. بررسی دسترسی در همه لایه‌ها:
- ✅ Backend (Models, Views, APIs)
- ✅ Frontend (UI محدودیت‌ها)
- ✅ Middleware (اگر نیاز بود)

### 2. CSRF Protection:
- ✅ همه فرم‌ها از CSRF token استفاده کنند
- ✅ API ها از CSRF protection استفاده کنند

### 3. Audit Logging:
- ✅ ثبت تغییرات دسترسی‌ها
- ✅ ثبت تغییر نقش کاربران
- ✅ ثبت تلاش‌های دسترسی غیرمجاز

### 4. Rate Limiting:
- ✅ محدودیت تعداد درخواست‌های API
- ✅ محدودیت تلاش‌های تغییر دسترسی

### 5. Validation:
- ✅ بررسی اعتبار project_id در همه درخواست‌ها
- ✅ بررسی وجود کاربر و پروژه قبل از ایجاد دسترسی
- ✅ جلوگیری از ایجاد دسترسی تکراری

---

## 📊 چک‌لیست پیاده‌سازی

### Backend:
- [ ] مدل ProjectAccess ایجاد شده
- [ ] مدل UserProjectPreference ایجاد شده
- [ ] Migration ها ایجاد و تست شده
- [ ] ProjectManager به‌روزرسانی شده
- [ ] Permission Classes ایجاد شده
- [ ] Mixins به‌روزرسانی شده
- [ ] Views به‌روزرسانی شده
- [ ] Unit Tests نوشته شده

### API:
- [ ] Serializers ایجاد شده
- [ ] ProjectAccessViewSet ایجاد شده
- [ ] UserProjectPreferenceViewSet ایجاد شده
- [ ] ProjectViewSet به‌روزرسانی شده
- [ ] API Tests نوشته شده

### Frontend:
- [ ] Project Switcher به‌روزرسانی شده
- [ ] صفحه مدیریت دسترسی ایجاد شده
- [ ] Context Processor به‌روزرسانی شده
- [ ] JavaScript برای مدیریت دسترسی‌ها

### Testing:
- [ ] Unit Tests pass می‌شوند
- [ ] Integration Tests pass می‌شوند
- [ ] Security Tests انجام شده
- [ ] Load Tests انجام شده

### Documentation:
- [ ] مستندات API نوشته شده
- [ ] مستندات کاربری نوشته شده
- [ ] README به‌روزرسانی شده

---

## 🎯 نتیجه نهایی

بعد از پیاده‌سازی کامل این برنامه، سیستم شما قابلیت‌های زیر را خواهد داشت:

1. ✅ **مدیریت دسترسی**: کنترل کامل دسترسی کاربران به پروژه‌ها
2. ✅ **نقش‌های مختلف**: تعریف نقش برای هر کاربر در هر پروژه
3. ✅ **مجوزهای تفکیک شده**: کنترل دقیق مجوزهای مشاهده، ویرایش، حذف
4. ✅ **UI مدیریت**: رابط کاربری برای مدیریت دسترسی‌ها
5. ✅ **API کامل**: API های کامل برای مدیریت دسترسی‌ها
6. ✅ **امنیت بالا**: بررسی دسترسی در همه لایه‌ها
7. ✅ **سازگاری**: سازگار با سیستم فعلی

---

**تاریخ ایجاد برنامه:** 2025-01-28  
**وضعیت:** آماده پیاده‌سازی  
**نسخه:** 1.0  
**اولویت:** برای پیاده‌سازی در آینده

