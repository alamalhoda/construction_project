# برنامه جامع: مدیریت همزمان چند پروژه

## 🎯 وضعیت فعلی (Baseline)

**✅ کارهای انجام شده:**
- همه مدل‌ها دارای فیلد `project` هستند
- سیستم پروژه فعال (یک پروژه active) موجود است
- داده‌ها به صورت جداگانه برای هر پروژه ذخیره می‌شوند
- فرم‌ها به صورت خودکار پروژه فعال را انتخاب می‌کنند

**❌ محدودیت‌های فعلی:**
- کاربر نمی‌تواند همزمان چند پروژه را ببیند
- سوییچ بین پروژه‌ها دشوار است (نیاز به مراجعه به `/construction/active_project/`)
- امکان مقایسه پروژه‌ها وجود ندارد
- دسترسی کاربران به پروژه‌ها مدیریت نمی‌شود

---

## 📋 فاز 1: Backend Infrastructure (پایه)

### 1.1: مدل‌های جدید

**فایل:** `construction/models.py`

#### 1.1.1: مدل ProjectAccess (دسترسی کاربر به پروژه)
```python
class ProjectAccess(models.Model):
    """مدل دسترسی کاربران به پروژه‌ها"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'مالک پروژه'),
        ('manager', 'مدیر پروژه'),
        ('viewer', 'ناظر'),
    ])
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'project']
        verbose_name = "دسترسی به پروژه"
        verbose_name_plural = "دسترسی‌های پروژه"
```

#### 1.1.2: مدل UserProjectPreference (تنظیمات کاربر)
```python
class UserProjectPreference(models.Model):
    """تنظیمات و ترجیحات کاربر برای پروژه‌ها"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    last_viewed_projects = models.JSONField(default=list)  # لیست ID پروژه‌های اخیر
    favorite_projects = models.ManyToManyField(Project, related_name='favorited_by', blank=True)
    
    class Meta:
        verbose_name = "تنظیمات پروژه کاربر"
        verbose_name_plural = "تنظیمات پروژه کاربران"
```

### 1.2: Middleware جدید

**فایل:** `construction/project_context_middleware.py` (ایجاد جدید)

```python
from .models import Project
from .project_manager import ProjectManager

class ProjectContextMiddleware:
    """
    Middleware برای مدیریت context پروژه در session
    - ذخیره پروژه انتخابی کاربر در session
    - دسترسی به پروژه فعلی از طریق request.current_project
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # تنظیم پروژه فعلی در request
        if request.user.is_authenticated:
            request.current_project = ProjectManager.get_current_project(request)
        else:
            request.current_project = None
        
        response = self.get_response(request)
        return response
```

### 1.3: Context Processor

**فایل:** `construction_project/context_processors.py` (به‌روزرسانی)

```python
def project_context(request):
    """
    اضافه کردن اطلاعات پروژه به تمام templates:
    - current_project: پروژه فعلی کاربر
    - user_projects: لیست پروژه‌هایی که کاربر دسترسی دارد
    - active_project: پروژه فعال سیستم
    """
    from construction.project_manager import ProjectManager
    from construction.models import Project
    
    context = {
        'current_project': None,
        'user_projects': [],
        'active_project': Project.get_active_project(),
    }
    
    if request.user.is_authenticated:
        context['current_project'] = ProjectManager.get_current_project(request)
        context['user_projects'] = ProjectManager.get_user_projects(request.user)
    
    return context
```

### 1.4: API Updates

**فایل:** `construction/api.py`

- اضافه کردن فیلتر `project` به تمام ViewSetها
- پشتیبانی از query parameter `?project_id=X`
- اضافه کردن endpoint جدید: `/api/v1/Project/user_projects/` (پروژه‌های کاربر)
- اضافه کردن endpoint: `/api/v1/Project/switch/` (تغییر پروژه فعلی)
- اضافه کردن endpoint: `/api/v1/Project/compare/` (مقایسه پروژه‌ها)

---

## 🎨 فاز 2: UI/UX Components (کامپوننت‌های رابط کاربری)

### 2.1: Project Switcher Component

**فایل:** `templates/components/project_switcher.html` (ایجاد جدید)

**قابلیت‌ها:**
- Dropdown برای انتخاب سریع پروژه
- نمایش پروژه فعلی با badge
- لیست پروژه‌های اخیر
- دکمه "مشاهده همه پروژه‌ها"
- نمایش در navbar تمام صفحات

**موقعیت:** بالای صفحه، کنار منوی کاربری

### 2.2: Project Card Component

**فایل:** `templates/components/project_card.html` (ایجاد جدید)

**استفاده:** در داشبورد چند پروژه‌ای

**محتوا:**
- نام پروژه
- وضعیت (فعال/غیرفعال/تکمیل شده)
- آمار کوتاه (سرمایه، هزینه، سود)
- دکمه‌های عملیات (مشاهده، گزارش، تنظیمات)

### 2.3: Project Comparison Component

**فایل:** `templates/components/project_comparison.html` (ایجاد جدید)

**قابلیت‌ها:**
- جدول مقایسه‌ای پروژه‌ها
- نمودارهای مقایسه‌ای
- فیلترهای پیشرفته

---

## 📱 فاز 3: صفحات Construction (به‌روزرسانی)

### 3.1: صفحات List (فهرست)

**فایل‌های تأثیرگرفته:**
- `construction/templates/construction/investor_list.html`
- `construction/templates/construction/transaction_list.html`
- `construction/templates/construction/expense_list.html`
- `construction/templates/construction/sale_list.html`
- `construction/templates/construction/period_list.html`
- `construction/templates/construction/unit_list.html`

**تغییرات:**
1. **اضافه کردن Project Switcher** به بالای صفحه
2. **فیلتر پروژه** در sidebar (در صورت نیاز)
3. **نمایش نام پروژه** در کنار عنوان صفحه
4. **Badge پروژه فعلی** در هر رکورد (اختیاری)

**مثال کد:**
```html
{% include 'components/project_switcher.html' %}

<div class="page-header">
    <h1>
        <i class="fas fa-users"></i>
        لیست مشارکت کنندگان
        <span class="project-badge">{{ current_project.name }}</span>
    </h1>
</div>
```

### 3.2: صفحات Form (فرم)

**فایل‌های تأثیرگرفته:**
- `construction/templates/construction/investor_form.html`
- `construction/templates/construction/transaction_form.html`
- `construction/templates/construction/expense_form.html`
- و سایر فرم‌ها...

**تغییرات:**
1. **نمایش پروژه فعلی** به صورت read-only در بالای فرم
2. **هشدار** اگر کاربر در حال ایجاد رکورد در پروژه غیرفعال باشد
3. **امکان انتخاب پروژه** برای کاربران با دسترسی چند پروژه (اختیاری)

### 3.3: صفحه مدیریت پروژه‌ها

**فایل:** `construction/templates/construction/project_list.html` (به‌روزرسانی)

**قابلیت‌های جدید:**
1. **کارت‌های پروژه** به جای جدول ساده
2. **فیلتر وضعیت:** همه / فعال / تکمیل شده / آرشیو
3. **مرتب‌سازی:** تاریخ / نام / وضعیت
4. **دکمه "مشاهده داشبورد"** برای هر پروژه
5. **آمار سریع** در هر کارت (سرمایه، هزینه، واحدها)

### 3.4: صفحه جدید: Project Dashboard

**فایل:** `construction/templates/construction/project_dashboard_multi.html` (ایجاد جدید)

**محتوا:**
- نمای کلی همه پروژه‌ها
- کارت‌های آماری برای هر پروژه
- نمودار مقایسه‌ای
- لینک سریع به جزئیات هر پروژه

---

## 📊 فاز 4: صفحات Dashboard (به‌روزرسانی و ایجاد)

### 4.1: صفحه اصلی داشبورد

**فایل:** `dashboard/view/user_dashboard.html` (به‌روزرسانی)

**تغییرات:**
1. **اضافه کردن Project Switcher** در navbar
2. **نمایش نام پروژه فعلی** در عنوان
3. **دکمه "مشاهده همه پروژه‌ها"**
4. **Badge تعداد پروژه‌های کاربر**

### 4.2: صفحه جدید: Multi-Project Dashboard

**فایل:** `dashboard/view/multi_project_dashboard.html` (ایجاد جدید)

**بخش‌ها:**

1. **Overview Cards:**
   - تعداد کل پروژه‌ها
   - پروژه‌های فعال
   - کل سرمایه (همه پروژه‌ها)
   - کل سود (همه پروژه‌ها)

2. **Projects Grid:**
   - کارت برای هر پروژه با آمار کلیدی
   - Progress bar برای پیشرفت پروژه
   - وضعیت (فعال/تکمیل شده/آرشیو)

3. **Comparison Section:**
   - نمودار ستونی مقایسه سود
   - نمودار خطی مقایسه پیشرفت
   - جدول مقایسه‌ای دقیق

### 4.3: صفحات موجود Dashboard (به‌روزرسانی)

**فایل‌های تأثیرگرفته:**
- `dashboard/view/project_dashboard.html`
- `dashboard/view/expense_dashboard.html`
- `dashboard/view/transaction_manager.html`
- `dashboard/view/investor_profile.html`
- `dashboard/view/period_summary.html`
- `dashboard/view/interestrate_manager.html`

**تغییرات یکسان برای همه:**
1. **اضافه کردن Project Switcher** در unified header
2. **نمایش نام پروژه فعلی** در navigation links
3. **فیلتر پروژه** در APIها (پشتیبانی از `?project_id=X`)
4. **پیام هشدار** اگر پروژه فعال نباشد

**مثال تغییر در unified header:**
```html
<div class="unified-header">
    <div class="unified-header-content">
        <!-- اضافه کردن Project Switcher -->
        <div class="project-selector-container">
            {% include 'components/project_switcher.html' %}
        </div>
        
        <h1>
            <i class="fas fa-chart-line"></i>
            خلاصه مالی
            <span class="current-project-badge">{{ current_project.name }}</span>
        </h1>
        ...
    </div>
</div>
```

### 4.4: صفحات چاپی (به‌روزرسانی)

**فایل‌های تأثیرگرفته:**
- `dashboard/view/period_summary_print.html`
- `dashboard/view/investors_summary_print.html`
- `dashboard/view/investor_pdf.html`

**تغییرات:**
- نمایش واضح نام پروژه در هدر
- امکان چاپ گزارش چند پروژه‌ای

---

## 🔐 فاز 5: Authentication & Authorization (احراز هویت و مجوزها)

### 5.1: Permission Classes جدید

**فایل:** `construction/permissions.py` (ایجاد جدید)

```python
from rest_framework import permissions
from .models import ProjectAccess

class ProjectAccessPermission(permissions.BasePermission):
    """بررسی دسترسی کاربر به پروژه"""
    
    def has_permission(self, request, view):
        # superuser همیشه دسترسی دارد
        if request.user.is_superuser:
            return True
        
        # بررسی دسترسی به پروژه
        project_id = request.query_params.get('project_id') or request.session.get('current_project_id')
        if project_id:
            return ProjectAccess.objects.filter(
                user=request.user,
                project_id=project_id
            ).exists()
        
        return True
    
class ProjectEditPermission(permissions.BasePermission):
    """بررسی مجوز ویرایش پروژه"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        return ProjectAccess.objects.filter(
            user=request.user,
            project=obj.project,
            can_edit=True
        ).exists()
    
class ProjectDeletePermission(permissions.BasePermission):
    """بررسی مجوز حذف پروژه"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        return ProjectAccess.objects.filter(
            user=request.user,
            project=obj.project,
            can_delete=True
        ).exists()
```

### 5.2: به‌روزرسانی Views

**فایل:** `construction/views.py`

**تغییرات:**
- اضافه کردن چک دسترسی به `get_queryset()` در همه ListView ها
- فیلتر رکوردها بر اساس پروژه‌های مجاز کاربر
- Validation در CreateView و UpdateView

**مثال:**
```python
def get_queryset(self):
    queryset = super().get_queryset()
    # فیلتر بر اساس پروژه فعلی کاربر
    current_project_id = self.request.session.get('current_project_id')
    if current_project_id:
        queryset = queryset.filter(project_id=current_project_id)
    return queryset
```

### 5.3: به‌روزرسانی API Permissions

**فایل:** `construction/api.py`

- اضافه کردن `ProjectAccessPermission` به ViewSetها
- فیلتر داده‌ها بر اساس دسترسی کاربر

---

## 🎨 فاز 6: UI Components (کامپوننت‌های رابط کاربری)

### 6.1: Project Switcher (کامپوننت اصلی)

**فایل:** `templates/components/project_switcher.html`

**طراحی:**
```html
<div class="project-switcher">
    <div class="current-project" onclick="toggleProjectDropdown()">
        <i class="fas fa-project-diagram"></i>
        <span class="project-name">{{ current_project.name }}</span>
        <i class="fas fa-chevron-down"></i>
    </div>
    
    <div class="project-dropdown" id="projectDropdown" style="display: none;">
        <!-- لیست پروژه‌ها -->
        <div class="project-list">
            {% for project in user_projects %}
            <div class="project-item {% if project.id == current_project.id %}active{% endif %}" 
                 onclick="switchProject({{ project.id }})">
                <span class="project-name">{{ project.name }}</span>
                {% if project.is_active %}
                <span class="badge badge-success">فعال</span>
                {% endif %}
                {% if project.id == current_project.id %}
                <i class="fas fa-check"></i>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <div class="project-actions">
            <a href="/dashboard/projects/">
                <i class="fas fa-th"></i>
                مشاهده همه پروژه‌ها
            </a>
            <a href="/construction/Project/create/">
                <i class="fas fa-plus"></i>
                پروژه جدید
            </a>
        </div>
    </div>
</div>

<script>
function toggleProjectDropdown() {
    const dropdown = document.getElementById('projectDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

// بستن dropdown با کلیک بیرون
document.addEventListener('click', function(e) {
    if (!e.target.closest('.project-switcher')) {
        document.getElementById('projectDropdown').style.display = 'none';
    }
});

async function switchProject(projectId) {
    try {
        const response = await fetch('/api/v1/Project/switch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ project_id: projectId })
        });
        
        if (response.ok) {
            const result = await response.json();
            // رفرش صفحه برای نمایش داده‌های پروژه جدید
            location.reload();
        } else {
            alert('خطا در تغییر پروژه');
        }
    } catch (error) {
        console.error('Error switching project:', error);
        alert('خطا در ارتباط با سرور');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
```

**استایل:** Fixed position در بالای صفحه یا در navbar

### 6.2: Project Stats Widget

**فایل:** `templates/components/project_stats_widget.html`

**محتوا:**
- سرمایه کل
- هزینه کل
- سود/زیان
- تعداد واحدها
- پیشرفت (%)

**استفاده:** در کارت‌های پروژه و داشبورد چند پروژه‌ای

### 6.3: Project Comparison Table

**فایل:** `templates/components/project_comparison_table.html`

**ستون‌ها:**
- نام پروژه
- سرمایه
- هزینه
- سود/زیان
- تعداد واحدها
- وضعیت
- عملیات

---

## 📄 فاز 7: صفحات جدید Dashboard

### 7.1: Multi-Project Dashboard

**فایل:** `dashboard/view/multi_project_dashboard.html`

**URL:** `/dashboard/projects/`

**بخش‌ها:**

1. **Header Section:**
   - عنوان: "مدیریت پروژه‌ها"
   - فیلتر وضعیت
   - دکمه "پروژه جدید"

2. **Overview Cards:**
```html
<div class="overview-grid">
    <div class="stat-card">
        <h3>{{ total_projects }}</h3>
        <p>کل پروژه‌ها</p>
    </div>
    <div class="stat-card">
        <h3>{{ active_projects }}</h3>
        <p>پروژه‌های فعال</p>
    </div>
    <div class="stat-card">
        <h3>{{ total_capital }}</h3>
        <p>سرمایه کل</p>
    </div>
    <div class="stat-card">
        <h3>{{ total_profit }}</h3>
        <p>سود کل</p>
    </div>
</div>
```

3. **Projects Grid:**
```html
<div class="projects-grid">
    {% for project in projects %}
    <div class="project-card">
        <div class="project-header">
            <h3>{{ project.name }}</h3>
            <span class="status-badge">{{ project.status }}</span>
        </div>
        <div class="project-stats">
            <!-- آمار پروژه -->
        </div>
        <div class="project-actions">
            <button onclick="switchToProject({{ project.id }})">انتخاب</button>
            <a href="/dashboard/project/?id={{ project.id }}">داشبورد</a>
        </div>
    </div>
    {% endfor %}
</div>
```

4. **Comparison Section:**
   - نمودار ستونی مقایسه سود
   - نمودار خطی مقایسه پیشرفت
   - جدول مقایسه‌ای دقیق

### 7.2: Project Comparison Page

**فایل:** `dashboard/view/project_comparison.html`

**URL:** `/dashboard/projects/compare/`

**Query Parameters:** `?projects=1,2,3`

**محتوا:**
1. **انتخابگر پروژه‌ها** (چند انتخابی)
2. **جدول مقایسه جامع**
3. **نمودارهای مقایسه‌ای:**
   - مقایسه سرمایه
   - مقایسه هزینه‌ها
   - مقایسه سود
   - مقایسه پیشرفت زمانی

### 7.3: Project Reports (گزارش چند پروژه‌ای)

**فایل:** `dashboard/view/multi_project_reports.html`

**محتوا:**
- گزارش کل پرتفوی پروژه‌ها
- نمودارهای ترند کلی
- جداول خلاصه
- دکمه صادرات Excel/PDF

---

## 🔄 فاز 8: Backend Logic (منطق Backend)

### 8.1: Session Management

**فایل:** `construction/project_manager.py` (ایجاد جدید)

```python
from django.db import models as django_models
from .models import Project, ProjectAccess

class ProjectManager:
    """کلاس helper برای مدیریت پروژه کاربر"""
    
    @staticmethod
    def get_current_project(request):
        """دریافت پروژه فعلی کاربر از session"""
        project_id = request.session.get('current_project_id')
        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if project:
                return project
        # اگر در session نبود، از پروژه فعال استفاده کن
        return Project.get_active_project()
    
    @staticmethod
    def set_current_project(request, project_id):
        """تنظیم پروژه فعلی کاربر در session"""
        request.session['current_project_id'] = project_id
        
        # اضافه به لیست پروژه‌های اخیر
        ProjectManager.add_to_recent_projects(request.user, project_id)
    
    @staticmethod
    def get_user_projects(user):
        """دریافت پروژه‌های مجاز کاربر"""
        if user.is_superuser or user.is_staff:
            return Project.objects.all()
        
        # برای کاربران عادی، فقط پروژه‌هایی که دسترسی دارند
        return Project.objects.filter(
            projectaccess__user=user
        ).distinct()
    
    @staticmethod
    def has_project_access(user, project):
        """بررسی دسترسی کاربر به پروژه"""
        if user.is_superuser or user.is_staff:
            return True
        
        return ProjectAccess.objects.filter(
            user=user,
            project=project
        ).exists()
    
    @staticmethod
    def add_to_recent_projects(user, project_id):
        """اضافه کردن پروژه به لیست پروژه‌های اخیر کاربر"""
        from .models import UserProjectPreference
        
        pref, created = UserProjectPreference.objects.get_or_create(user=user)
        recent = pref.last_viewed_projects or []
        
        # حذف project_id قبلی اگر وجود دارد
        if project_id in recent:
            recent.remove(project_id)
        
        # اضافه کردن به ابتدای لیست
        recent.insert(0, project_id)
        
        # نگه داشتن فقط 5 پروژه اخیر
        pref.last_viewed_projects = recent[:5]
        pref.save()
```

### 8.2: View Mixins

**فایل:** `construction/mixins.py` (ایجاد جدید)

```python
from .project_manager import ProjectManager

class ProjectFilterMixin:
    """Mixin برای فیلتر خودکار بر اساس پروژه فعلی"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        current_project = ProjectManager.get_current_project(self.request)
        if current_project and hasattr(queryset.model, 'project'):
            queryset = queryset.filter(project=current_project)
        return queryset

class ProjectContextMixin:
    """Mixin برای اضافه کردن context پروژه"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_project'] = ProjectManager.get_current_project(self.request)
        context['user_projects'] = ProjectManager.get_user_projects(self.request.user)
        return context

class ProjectAccessMixin:
    """Mixin برای بررسی دسترسی به پروژه"""
    
    def dispatch(self, request, *args, **kwargs):
        current_project = ProjectManager.get_current_project(request)
        if current_project and not ProjectManager.has_project_access(request.user, current_project):
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, 'شما به این پروژه دسترسی ندارید')
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)
```

### 8.3: به‌روزرسانی همه Views

**فایل:** `construction/views.py`

**تغییرات:**
- اضافه کردن `ProjectFilterMixin` و `ProjectContextMixin` به همه views

**مثال:**
```python
from .mixins import ProjectFilterMixin, ProjectContextMixin, ProjectAccessMixin

class InvestorListView(ProjectFilterMixin, ProjectContextMixin, generic.ListView):
    model = models.Investor
    form_class = forms.InvestorForm

class InvestorCreateView(ProjectContextMixin, generic.CreateView):
    model = models.Investor
    form_class = forms.InvestorForm
```

### 8.4: API ViewSets Updates

**فایل:** `construction/api.py`

**تغییرات در همه ViewSetها:**
```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # پشتیبانی از query parameter project_id
    project_id = self.request.query_params.get('project_id')
    
    if project_id:
        queryset = queryset.filter(project_id=project_id)
    else:
        # استفاده از پروژه session یا پروژه فعال
        from .project_manager import ProjectManager
        current_project = ProjectManager.get_current_project(self.request)
        if current_project:
            queryset = queryset.filter(project=current_project)
    
    return queryset
```

---

## 📊 فاز 9: Multi-Project APIs (APIهای جدید)

### 9.1: Project Switch API

**Endpoint:** `POST /api/v1/Project/switch/`

**Implementation در `construction/api.py`:**
```python
@action(detail=False, methods=['post'])
def switch(self, request):
    """تغییر پروژه فعلی کاربر"""
    project_id = request.data.get('project_id')
    
    if not project_id:
        return Response({'error': 'project_id الزامی است'}, status=400)
    
    try:
        project = Project.objects.get(id=project_id)
        
        # بررسی دسترسی
        if not ProjectManager.has_project_access(request.user, project):
            return Response({'error': 'شما به این پروژه دسترسی ندارید'}, status=403)
        
        # تنظیم پروژه جدید
        ProjectManager.set_current_project(request, project_id)
        
        return Response({
            'success': True,
            'project': {
                'id': project.id,
                'name': project.name,
                'is_active': project.is_active
            },
            'message': 'پروژه با موفقیت تغییر کرد'
        })
    except Project.DoesNotExist:
        return Response({'error': 'پروژه یافت نشد'}, status=404)
```

### 9.2: User Projects API

**Endpoint:** `GET /api/v1/Project/user_projects/`

**Implementation:**
```python
@action(detail=False, methods=['get'])
def user_projects(self, request):
    """دریافت لیست پروژه‌های کاربر با آمار"""
    projects = ProjectManager.get_user_projects(request.user)
    current_project = ProjectManager.get_current_project(request)
    
    projects_data = []
    for project in projects:
        # محاسبه آمار هر پروژه
        stats = {
            'total_capital': Transaction.objects.filter(
                project=project,
                transaction_type='principal_deposit'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'total_expense': Expense.objects.filter(
                project=project
            ).aggregate(total=Sum('amount'))['total'] or 0,
        }
        
        projects_data.append({
            'id': project.id,
            'name': project.name,
            'is_active': project.is_active,
            'is_current': project.id == current_project.id if current_project else False,
            'stats': stats
        })
    
    return Response({
        'projects': projects_data,
        'current_project_id': current_project.id if current_project else None
    })
```

### 9.3: Project Comparison API

**Endpoint:** `GET /api/v1/Project/compare/?projects=1,2,3`

**Implementation:**
```python
@action(detail=False, methods=['get'])
def compare(self, request):
    """مقایسه چند پروژه"""
    project_ids = request.query_params.get('projects', '').split(',')
    
    if not project_ids:
        return Response({'error': 'لطفاً حداقل یک پروژه انتخاب کنید'}, status=400)
    
    projects = Project.objects.filter(id__in=project_ids)
    comparison_data = []
    
    for project in projects:
        # محاسبات برای هر پروژه
        metrics = ProjectCalculations.calculate_all_metrics(project)
        
        comparison_data.append({
            'id': project.id,
            'name': project.name,
            'metrics': metrics
        })
    
    return Response({
        'projects': comparison_data,
        'comparison_charts': {
            'profit_comparison': [p['metrics']['total_profit'] for p in comparison_data],
            'expense_comparison': [p['metrics']['total_expense'] for p in comparison_data],
        }
    })
```

### 9.4: Multi-Project Statistics API

**Endpoint:** `GET /api/v1/Dashboard/multi_project_stats/`

**Implementation:**
```python
@action(detail=False, methods=['get'])
def multi_project_stats(self, request):
    """آمار کلی همه پروژه‌ها"""
    projects = ProjectManager.get_user_projects(request.user)
    
    total_capital = 0
    total_expense = 0
    total_profit = 0
    
    for project in projects:
        stats = ProjectCalculations.calculate_financial_summary(project)
        total_capital += stats['total_capital']
        total_expense += stats['total_expense']
        total_profit += stats['total_profit']
    
    return Response({
        'total_projects': projects.count(),
        'active_projects': projects.filter(is_active=True).count(),
        'total_capital_all': total_capital,
        'total_expense_all': total_expense,
        'total_profit_all': total_profit,
    })
```

---

## 🛠️ فاز 10: Database Updates

### 10.1: Migrations

**فایل:** `construction/migrations/00XX_add_multi_project_support.py`

**عملیات:**
1. ایجاد جدول `ProjectAccess`
2. ایجاد جدول `UserProjectPreference`
3. اضافه کردن Index به فیلد `project` در همه مدل‌ها
4. ایجاد Unique Constraint: `(user, project)` در `ProjectAccess`

```python
operations = [
    migrations.CreateModel(
        name='ProjectAccess',
        fields=[...],
    ),
    migrations.CreateModel(
        name='UserProjectPreference',
        fields=[...],
    ),
    # اضافه کردن Index
    migrations.AddIndex(
        model_name='investor',
        index=models.Index(fields=['project'], name='investor_project_idx'),
    ),
    # و مشابه برای سایر مدل‌ها
]
```

### 10.2: Data Migration

**فایل:** `construction/migrations/00XX_populate_project_access.py`

**منطق:**
```python
def populate_project_access(apps, schema_editor):
    """ایجاد دسترسی پیش‌فرض برای کاربران موجود"""
    User = apps.get_model('auth', 'User')
    Project = apps.get_model('construction', 'Project')
    ProjectAccess = apps.get_model('construction', 'ProjectAccess')
    
    for user in User.objects.all():
        for project in Project.objects.all():
            if user.is_superuser:
                role = 'owner'
                can_edit = True
                can_delete = True
            elif user.is_staff:
                role = 'manager'
                can_edit = True
                can_delete = False
            else:
                role = 'viewer'
                can_edit = False
                can_delete = False
            
            ProjectAccess.objects.get_or_create(
                user=user,
                project=project,
                defaults={
                    'role': role,
                    'can_edit': can_edit,
                    'can_delete': can_delete
                }
            )
```

---

## 📱 فاز 11: Frontend Assets

### 11.1: JavaScript Files

**فایل:** `static/js/project-switcher.js` (ایجاد جدید)

```javascript
class ProjectSwitcher {
    constructor() {
        this.currentProject = null;
        this.userProjects = [];
        this.init();
    }
    
    async init() {
        await this.loadUserProjects();
        this.setupEventListeners();
    }
    
    async loadUserProjects() {
        const response = await fetch('/api/v1/Project/user_projects/');
        const data = await response.json();
        this.userProjects = data.projects;
        this.currentProject = data.current_project_id;
    }
    
    async switchProject(projectId) {
        // Show loading
        this.showLoading();
        
        const response = await fetch('/api/v1/Project/switch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify({ project_id: projectId })
        });
        
        if (response.ok) {
            // ذخیره در localStorage
            localStorage.setItem('last_project_id', projectId);
            
            // Reload page
            location.reload();
        } else {
            alert('خطا در تغییر پروژه');
            this.hideLoading();
        }
    }
    
    getCookie(name) {
        // implementation...
    }
    
    showLoading() {
        // implementation...
    }
    
    hideLoading() {
        // implementation...
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.projectSwitcher = new ProjectSwitcher();
});
```

**فایل:** `static/js/multi-project.js` (ایجاد جدید)

```javascript
class MultiProjectManager {
    async loadAllProjects() {
        // بارگذاری همه پروژه‌ها
    }
    
    async compareProjects(projectIds) {
        // مقایسه پروژه‌ها
    }
    
    renderProjectCards(projects) {
        // نمایش کارت‌های پروژه
    }
    
    renderComparisonCharts(data) {
        // نمودارهای مقایسه‌ای
    }
}
```

### 11.2: CSS Files

**فایل:** `static/css/project-switcher.css` (ایجاد جدید)

```css
.project-switcher {
    position: relative;
    display: inline-block;
    margin: 0 15px;
}

.project-switcher .current-project {
    background: rgba(255, 255, 255, 0.2);
    padding: 10px 20px;
    border-radius: 25px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.3s ease;
}

.project-switcher .current-project:hover {
    background: rgba(255, 255, 255, 0.3);
}

.project-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 10px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    min-width: 300px;
    z-index: 1000;
}

.project-list {
    max-height: 400px;
    overflow-y: auto;
}

.project-item {
    padding: 15px 20px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    transition: all 0.3s ease;
}

.project-item:hover {
    background: #f8f9fa;
}

.project-item.active {
    background: #e7f3ff;
    border-right: 4px solid #667eea;
}

.project-actions {
    padding: 15px 20px;
    border-top: 2px solid #f0f0f0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.project-actions a {
    padding: 10px;
    text-align: center;
    background: #f8f9fa;
    border-radius: 8px;
    text-decoration: none;
    color: #667eea;
    transition: all 0.3s ease;
}

.project-actions a:hover {
    background: #667eea;
    color: white;
}
```

---

## 🧪 فاز 12: Testing & Validation

### 12.1: Backend Tests

**فایل:** `construction/tests/test_multi_project.py`

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from construction.models import Project, ProjectAccess
from construction.project_manager import ProjectManager

class ProjectManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass')
        self.project1 = Project.objects.create(name='پروژه 1', ...)
        self.project2 = Project.objects.create(name='پروژه 2', ...)
    
    def test_get_user_projects(self):
        # تست دریافت پروژه‌های کاربر
        pass
    
    def test_switch_project(self):
        # تست تغییر پروژه
        pass
    
    def test_project_access(self):
        # تست دسترسی به پروژه
        pass

class ProjectAccessTestCase(TestCase):
    # تست‌های دسترسی
    pass
```

### 12.2: Frontend Tests

**فایل:** `tests/frontend/test_project_switcher.js`

```javascript
describe('Project Switcher', () => {
    test('should load user projects', async () => {
        // تست بارگذاری پروژه‌ها
    });
    
    test('should switch project', async () => {
        // تست تغییر پروژه
    });
    
    test('should show current project', () => {
        // تست نمایش پروژه فعلی
    });
});
```

---

## 🗺️ فاز 13: URLs & Routing

### 13.1: URLs جدید

**فایل:** `construction/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... URLهای موجود
    
    # Multi-project URLs
    path('projects/switch/<int:pk>/', views.switch_project_view, name='switch_project'),
    path('projects/multi-dashboard/', views.multi_project_dashboard, name='multi_project_dashboard'),
    path('projects/compare/', views.project_comparison, name='project_comparison'),
]
```

**فایل:** `dashboard/urls.py`

```python
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ... URLهای موجود
    
    # Multi-project dashboard URLs
    path('projects/', views.multi_project_dashboard, name='multi_project_dashboard'),
    path('projects/compare/', views.project_comparison, name='project_comparison'),
    path('projects/reports/', views.multi_project_reports, name='multi_project_reports'),
]
```

---

## 📋 فاز 14: مراحل پیاده‌سازی (اولویت‌بندی شده)

### مرحله 1: Backend Foundation (هفته 1)
1. ایجاد مدل‌های `ProjectAccess` و `UserProjectPreference`
2. ایجاد migrations
3. ایجاد `ProjectManager` utility class
4. ایجاد Middleware و Context Processor

**تخمین زمان:** 3-4 روز

### مرحله 2: API Development (هفته 1-2)
1. اضافه کردن فیلتر `project` به APIها
2. ایجاد API `/Project/switch/`
3. ایجاد API `/Project/user_projects/`
4. ایجاد API `/Project/compare/`

**تخمین زمان:** 3-4 روز

### مرحله 3: UI Components (هفته 2)
1. ایجاد `project_switcher.html`
2. ایجاد CSS و JavaScript مربوطه
3. تست component در یک صفحه نمونه

**تخمین زمان:** 2-3 روز

### مرحله 4: Construction Templates (هفته 2-3)
1. به‌روزرسانی `base.html` برای افزودن project switcher
2. به‌روزرسانی همه List views (7 صفحه)
3. به‌روزرسانی همه Form views (7 صفحه)
4. تست عملکرد

**تخمین زمان:** 5-6 روز

### مرحله 5: Dashboard Templates (هفته 3-4)
1. اضافه کردن project switcher به unified header
2. به‌روزرسانی 6 صفحه dashboard موجود
3. ایجاد `multi_project_dashboard.html`
4. ایجاد `project_comparison.html`

**تخمین زمان:** 5-7 روز

### مرحله 6: Permissions & Security (هفته 4)
1. پیاده‌سازی Permission Classes
2. اضافه کردن چک‌های دسترسی به Views
3. محدود کردن APIها بر اساس دسترسی
4. تست امنیتی

**تخمین زمان:** 3-4 روز

### مرحله 7: Testing & Bug Fixes (هفته 5)
1. تست کامل سیستم
2. رفع باگ‌ها
3. بهینه‌سازی Performance
4. مستندسازی

**تخمین زمان:** 4-5 روز

---

## 📊 تحلیل تأثیر (Impact Analysis)

### Backend:
- **فایل‌های جدید:** 5 فایل
  - `construction/project_manager.py`
  - `construction/mixins.py`
  - `construction/permissions.py`
  - `construction/project_context_middleware.py`
  - `construction/tests/test_multi_project.py`
- **فایل‌های به‌روزرسانی:** 10 فایل
  - `construction/models.py`
  - `construction/views.py`
  - `construction/api.py`
  - `construction/serializers.py`
  - `construction/urls.py`
  - `construction_project/context_processors.py`
  - `construction_project/settings.py`
  - و 3 فایل دیگر
- **Migrations:** 2 migration

### Frontend (Construction Templates):
- **فایل‌های جدید:** 3 component
  - `templates/components/project_switcher.html`
  - `templates/components/project_card.html`
  - `templates/components/project_comparison.html`
- **فایل‌های به‌روزرسانی:** 28 template
  - همه صفحات list (7 فایل)
  - همه صفحات form (7 فایل)
  - همه صفحات detail (7 فایل)
  - همه صفحات delete (7 فایل)

### Frontend (Dashboard):
- **فایل‌های جدید:** 5 صفحه
  - `dashboard/view/multi_project_dashboard.html`
  - `dashboard/view/project_comparison.html`
  - `dashboard/view/multi_project_reports.html`
  - `dashboard/view/project_selector.html`
  - `dashboard/view/project_overview.html`
- **فایل‌های به‌روزرسانی:** 13 صفحه
  - تمام صفحات dashboard موجود

### JavaScript/CSS:
- **فایل‌های جدید:** 4 فایل
  - `static/js/project-switcher.js`
  - `static/js/multi-project.js`
  - `static/css/project-switcher.css`
  - `static/css/multi-project.css`
- **فایل‌های به‌روزرسانی:** 2 فایل
  - `static/js/financial-calculations.js`
  - ستایل‌های global

### جمع کل:
- **ایجاد جدید:** 17 فایل
- **به‌روزرسانی:** 53 فایل
- **مجموع:** 70 فایل

### تخمین زمان کلی: **4-5 هفته** (با فرض کار full-time)

---

## 🎯 نکات کلیدی

### 1. Backward Compatibility:
- سیستم فعلی باید بدون تغییر کار کند
- پروژه فعال همچنان به عنوان fallback استفاده شود
- APIهای قدیمی همچنان کار کنند
- کاربرانی که فقط یک پروژه دارند، تفاوتی نبینند

### 2. Performance:
- استفاده از caching برای لیست پروژه‌ها
- Lazy loading برای آمار پروژه‌ها
- Pagination در لیست پروژه‌ها
- Select_related و Prefetch_related در queries
- Index روی فیلد `project` در همه جداول

### 3. UX Best Practices:
- Project switcher همیشه قابل دسترس باشد
- نمایش واضح پروژه فعلی
- Confirmation برای تغییر پروژه (اگر تغییرات ذخیره نشده دارد)
- Loading states و Progress indicators
- Keyboard shortcuts برای سوییچ سریع
- Toast notifications برای تغییر موفق

### 4. Security:
- همیشه چک دسترسی کاربر
- Validation در سمت server
- Audit log برای تغییر پروژه
- CSRF Protection
- Rate limiting برای API های حساس

---

## 📁 فایل‌های کلیدی برای شروع

### Backend (اولویت بالا):
1. `construction/models.py` - افزودن مدل‌های جدید
2. `construction/project_manager.py` - ایجاد (کلاس helper اصلی)
3. `construction/mixins.py` - ایجاد
4. `construction/project_context_middleware.py` - ایجاد

### Frontend Components (اولویت بالا):
1. `templates/components/project_switcher.html` - ایجاد (کامپوننت اصلی)
2. `static/js/project-switcher.js` - ایجاد
3. `static/css/project-switcher.css` - ایجاد

### Dashboard Pages (اولویت متوسط):
1. `dashboard/view/multi_project_dashboard.html` - ایجاد
2. `dashboard/view/project_comparison.html` - ایجاد

### APIs (اولویت بالا):
1. `construction/api.py` - به‌روزرسانی ViewSetها
2. `construction/serializers.py` - افزودن serializers جدید

---

## 🌳 استراتژی Git Branch (توصیه شده)

### چرا Git Branch؟

**✅ مزایا:**
1. **ایزوله کردن تغییرات:** کد production روی `master` ایمن می‌ماند
2. **تست و Review:** قبل از merge، feature را کامل تست کنید
3. **Rollback آسان:** اگر مشکلی پیش آمد، راحت برمی‌گردید
4. **کار تیمی:** امکان همکاری و review توسط چند نفر
5. **تاریخچه واضح:** ثبت دقیق تغییرات و commits

### استراتژی: چند Branch فازی ⭐ **پیشنهاد**

```bash
# 1. ایجاد branch اصلی feature
git checkout -b feature/multi-project-management

# 2. ایجاد tag برای backup
git tag backup-before-multi-project-$(date +%Y%m%d)

# 3. Branch برای هر فاز مهم

# فاز 1: Backend Infrastructure
git checkout -b feature/mp-backend
# کار روی backend (models, migrations, utilities)
git add construction/models.py construction/project_manager.py construction/mixins.py
git commit -m "feat(multi-project): Add ProjectAccess and UserProjectPreference models"
git commit -m "feat(multi-project): Add ProjectManager utility class"
git commit -m "feat(multi-project): Add view mixins for project filtering"
git checkout feature/multi-project-management
git merge feature/mp-backend --no-ff
git branch -d feature/mp-backend

# فاز 2: API Development
git checkout -b feature/mp-api
# کار روی API
git add construction/api.py construction/serializers.py
git commit -m "feat(multi-project): Add project filter to all ViewSets"
git commit -m "feat(multi-project): Add Project/switch API endpoint"
git commit -m "feat(multi-project): Add Project/user_projects API endpoint"
git commit -m "feat(multi-project): Add Project/compare API endpoint"
git checkout feature/multi-project-management
git merge feature/mp-api --no-ff
git branch -d feature/mp-api

# فاز 3: UI Components
git checkout -b feature/mp-ui-components
# کار روی components
git add templates/components/ static/js/project-switcher.js static/css/project-switcher.css
git commit -m "feat(multi-project): Add project switcher component"
git commit -m "feat(multi-project): Add project card component"
git commit -m "feat(multi-project): Add project comparison component"
git commit -m "style(multi-project): Add CSS for project switcher"
git checkout feature/multi-project-management
git merge feature/mp-ui-components --no-ff
git branch -d feature/mp-ui-components

# فاز 4: Construction Templates
git checkout -b feature/mp-construction-templates
# به‌روزرسانی templates
git add construction/templates/construction/
git commit -m "refactor(construction): Update investor templates for multi-project"
git commit -m "refactor(construction): Update transaction templates for multi-project"
git commit -m "refactor(construction): Update expense and sale templates for multi-project"
git commit -m "refactor(construction): Update unit and period templates for multi-project"
git checkout feature/multi-project-management
git merge feature/mp-construction-templates --no-ff
git branch -d feature/mp-construction-templates

# فاز 5: Dashboard Templates
git checkout -b feature/mp-dashboard-templates
# به‌روزرسانی و ایجاد صفحات dashboard
git add dashboard/view/
git commit -m "feat(dashboard): Add multi-project dashboard page"
git commit -m "feat(dashboard): Add project comparison page"
git commit -m "refactor(dashboard): Update project_dashboard for multi-project"
git commit -m "refactor(dashboard): Update expense_dashboard for multi-project"
git commit -m "refactor(dashboard): Update transaction_manager for multi-project"
git commit -m "refactor(dashboard): Update investor_profile for multi-project"
git checkout feature/multi-project-management
git merge feature/mp-dashboard-templates --no-ff
git branch -d feature/mp-dashboard-templates

# فاز 6: Permissions & Security
git checkout -b feature/mp-permissions
# پیاده‌سازی permissions
git add construction/permissions.py construction/views.py
git commit -m "feat(multi-project): Add permission classes"
git commit -m "feat(multi-project): Add access control to views"
git commit -m "feat(multi-project): Add access control to APIs"
git checkout feature/multi-project-management
git merge feature/mp-permissions --no-ff
git branch -d feature/mp-permissions

# فاز 7: Testing
git checkout -b feature/mp-testing
# اضافه کردن تست‌ها
git add construction/tests/ tests/
git commit -m "test(multi-project): Add ProjectManager tests"
git commit -m "test(multi-project): Add ProjectAccess tests"
git commit -m "test(multi-project): Add API tests"
git commit -m "test(multi-project): Add frontend tests"
git checkout feature/multi-project-management
git merge feature/mp-testing --no-ff
git branch -d feature/mp-testing

# 4. تست نهایی
python manage.py test
python manage.py check
python manage.py migrate --check

# 5. Merge نهایی به master
git checkout master
git merge feature/multi-project-management --no-ff -m "Merge feature: Multi-Project Management System

- Add ProjectAccess and UserProjectPreference models
- Add ProjectManager utility for session management
- Add project switcher UI component
- Update all templates for multi-project support
- Add multi-project dashboard and comparison
- Add permission system for project access
- Add comprehensive tests"

# 6. Push و cleanup
git push origin master
git branch -d feature/multi-project-management  # اختیاری - می‌توانید نگه دارید
```

### نام‌گذاری Branches:

```
feature/multi-project-management          # Branch اصلی (parent)
├── feature/mp-backend                    # Backend Infrastructure (فاز 1)
├── feature/mp-api                        # API Development (فاز 2)
├── feature/mp-ui-components              # UI Components (فاز 3)
├── feature/mp-construction-templates     # Construction Templates (فاز 4)
├── feature/mp-dashboard-templates        # Dashboard Templates (فاز 5)
├── feature/mp-permissions                # Permissions & Security (فاز 6)
└── feature/mp-testing                    # Testing (فاز 7)
```

### Commit Message Convention:

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat:     قابلیت جدید
refactor: بازنویسی کد (بدون تغییر عملکرد)
fix:      رفع باگ
test:     اضافه کردن تست
docs:     مستندات
style:    فرمت‌بندی کد
perf:     بهبود Performance
chore:    تغییرات عمومی (dependencies, configs)

# Examples:
git commit -m "feat(multi-project): Add ProjectAccess model"
git commit -m "feat(api): Add project switcher endpoint"
git commit -m "refactor(dashboard): Update templates for multi-project support"
git commit -m "test(multi-project): Add ProjectManager tests"
git commit -m "docs(multi-project): Add implementation guide"
git commit -m "fix(multi-project): Fix project filter in InvestorListView"
git commit -m "perf(api): Optimize project comparison query"
```

### Workflow پیشنهادی کامل:

```bash
# 🔹 مرحله آماده‌سازی
git checkout master
git pull origin master
git tag backup-before-multi-project-$(date +%Y%m%d)
git push origin backup-before-multi-project-$(date +%Y%m%d)

# 🔹 ایجاد branch feature اصلی
git checkout -b feature/multi-project-management

# 🔹 کار روی هر فاز
# برای هر فاز:
# 1. ایجاد sub-branch
# 2. پیاده‌سازی
# 3. commit های کوچک و معنی‌دار
# 4. merge به parent branch
# 5. حذف sub-branch

# 🔹 تست مرحله‌ای
# بعد از هر merge:
python manage.py test construction
python manage.py check

# 🔹 تست نهایی قبل از merge به master
git checkout feature/multi-project-management
source env/bin/activate
python manage.py test
python manage.py check
python manage.py migrate --check
python manage.py collectstatic --noinput --dry-run

# 🔹 Merge به master
git checkout master
git merge feature/multi-project-management --no-ff

# 🔹 Push
git push origin master

# 🔹 Cleanup (اختیاری)
git branch -d feature/multi-project-management
# یا نگه دارید برای مرجع
```

### چک‌لیست قبل از Merge به Master:

**⚠️ الزامی:**
- ✅ همه تست‌ها pass شوند (`python manage.py test`)
- ✅ `python manage.py check` بدون خطا
- ✅ در محیط development کامل تست شود
- ✅ Migration ها بدون مشکل اجرا شوند
- ✅ Backup از production گرفته شود
- ✅ لیست تغییرات (CHANGELOG) نوشته شود
- ✅ مستندات به‌روز شود

**📋 توصیه شده:**
- ✅ Code review توسط فرد دیگر
- ✅ تست در محیط staging
- ✅ بررسی Performance
- ✅ بررسی امنیتی
- ✅ تست در مرورگرهای مختلف
- ✅ تست Responsive design

### در صورت مشکل:

```bash
# 🔴 لغو merge (اگر هنوز push نشده)
git merge --abort

# 🔴 بازگشت به قبل از merge (اگر push شده)
git reset --hard backup-before-multi-project-YYYYMMDD

# 🔴 بازگشت یک commit (اگر فقط یک commit مشکل دارد)
git revert HEAD

# 🔴 بازگشت چند commit
git revert HEAD~3..HEAD
```

### استراتژی Deploy:

```bash
# 📍 محیط Development (Local)
git checkout feature/multi-project-management
source env/bin/activate
python manage.py migrate
python manage.py runserver
# تست کامل

# 📍 محیط Staging (اختیاری ولی توصیه شده)
git checkout feature/multi-project-management
# Deploy به staging server
python manage.py migrate
# تست کامل با داده‌های واقعی
# Load testing
# Security testing

# 📍 محیط Production
# 1. Backup
python manage.py dumpdata > backup_before_multi_project.json

# 2. Merge
git checkout master
git merge feature/multi-project-management --no-ff

# 3. Deploy
git pull origin master
source env/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
# Restart server (gunicorn/uwsgi)
sudo systemctl restart gunicorn

# 4. Verify
# بررسی لاگ‌ها
# تست صفحات اصلی
# مانیتور کردن Performance
```

---

## 🚀 Quick Win: مرحله اول (2-3 ساعت)

برای شروع سریع و دیدن نتیجه اولیه:

### هدف:
اضافه کردن Project Switcher ساده به یک صفحه نمونه و تست عملکرد اولیه

### Git Workflow:

```bash
# 1. ایجاد branch اصلی (اگر هنوز ایجاد نشده)
git checkout master
git checkout -b feature/multi-project-management

# 2. ایجاد sub-branch برای Quick Win
git checkout -b feature/mp-quick-win

# 3. پیاده‌سازی فایل‌های اولیه
# ... کار

# 4. Commit های مرحله‌ای
git add construction/project_manager.py
git commit -m "feat(multi-project): Add ProjectManager utility class"

git add templates/components/project_switcher.html static/css/project-switcher.css
git commit -m "feat(multi-project): Add basic project switcher component"

git add construction/api.py
git commit -m "feat(api): Add Project/switch endpoint"

git add dashboard/view/user_dashboard.html
git commit -m "refactor(dashboard): Integrate project switcher in user dashboard"

# 5. Merge به parent branch
git checkout feature/multi-project-management
git merge feature/mp-quick-win --no-ff -m "Merge: Quick Win - Basic project switcher"

# 6. حذف sub-branch
git branch -d feature/mp-quick-win

# 7. تست
source env/bin/activate
python manage.py migrate
python manage.py runserver
# باز کردن http://localhost:8000/user-dashboard/

# 8. اگر موفق بود، ادامه به فازهای بعدی
# اگر مشکل داشت:
git reset --hard HEAD~1  # بازگشت یک مرحله
```

### فایل‌های Quick Win (حداقل برای شروع):

1. **Backend:**
   - `construction/project_manager.py` (کلاس ProjectManager ساده)
   
2. **API:**
   - به‌روزرسانی `construction/api.py` (افزودن endpoint switch)

3. **Frontend:**
   - `templates/components/project_switcher.html` (component ساده)
   - `static/css/project-switcher.css` (استایل پایه)

4. **Integration:**
   - به‌روزرسانی `dashboard/view/user_dashboard.html` (اضافه کردن component)

### نتیجه Quick Win:

بعد از این مرحله:
- ✅ کاربر می‌تواند پروژه را عوض کند
- ✅ سیستم session-based project switching کار می‌کند
- ✅ UI اولیه قابل مشاهده است
- ✅ می‌توانیم feedback بگیریم و ادامه دهیم

---

## 📝 نکات مهم برای پیاده‌سازی

### 1. ترتیب توصیه شده:
```
Backend → API → UI Components → Templates → Permissions → Testing
```

### 2. هر فاز باید:
- ✅ مستقل باشد (تا حد امکان)
- ✅ قابل تست باشد
- ✅ Backward compatible باشد
- ✅ مستند شود

### 3. بعد از هر Merge:
- ✅ تست کل سیستم
- ✅ بررسی لاگ‌های Django
- ✅ بررسی عملکرد صفحات
- ✅ تست در مرورگر

### 4. قبل از Merge به Master:
- ✅ تست کامل در development
- ✅ Review کد
- ✅ بررسی امنیتی
- ✅ تست Performance
- ✅ آماده‌سازی مستندات
- ✅ Backup از production

---

## 📚 مستندات مورد نیاز

### 1. فایل‌های مستندات جدید:

**`docs/MULTI_PROJECT_GUIDE.md`:**
- راهنمای کاربر نهایی
- نحوه سوییچ بین پروژه‌ها
- نحوه مقایسه پروژه‌ها
- FAQ

**`docs/MULTI_PROJECT_API.md`:**
- مستندات APIهای جدید
- نمونه requestها و responseها
- راهنمای استفاده

**`docs/MULTI_PROJECT_DEVELOPMENT.md`:**
- راهنمای توسعه‌دهنده
- ساختار کد
- Best practices

### 2. به‌روزرسانی مستندات موجود:

- `docs/API_REFERENCE.md` - افزودن APIهای جدید
- `README.md` - ذکر قابلیت چند پروژه‌ای
- `CHANGELOG.md` - ثبت تغییرات

---

## 🎊 نتیجه نهایی

بعد از اتمام همه فازها، سیستم شما قابلیت‌های زیر را خواهد داشت:

### ✅ قابلیت‌های جدید:

1. **مدیریت چند پروژه:**
   - ایجاد و مدیریت پروژه‌های متعدد
   - سوییچ سریع بین پروژه‌ها
   - داده‌های مجزا برای هر پروژه

2. **Dashboard چند پروژه‌ای:**
   - نمای کلی همه پروژه‌ها
   - کارت‌های آماری
   - نمودارهای مقایسه‌ای

3. **مقایسه پروژه‌ها:**
   - مقایسه سرمایه، هزینه، سود
   - نمودارهای تحلیلی
   - گزارش‌های مقایسه‌ای

4. **مدیریت دسترسی:**
   - کنترل دسترسی کاربران
   - نقش‌های مختلف (مالک، مدیر، ناظر)
   - مجوزهای ویرایش و حذف

5. **UX بهبود یافته:**
   - Project switcher همه‌جا
   - نمایش واضح پروژه فعلی
   - پروژه‌های اخیر
   - Keyboard shortcuts

### 📊 آمار نهایی:

- **فایل‌های جدید:** 17
- **فایل‌های به‌روزرسانی:** 53
- **مجموع:** 70 فایل
- **Migrations:** 2
- **APIهای جدید:** 4
- **Components:** 3
- **تخمین زمان:** 4-5 هفته

---

**تاریخ ایجاد برنامه:** 2025-10-12  
**Branch:** feature/multi-project-management  
**وضعیت:** آماده پیاده‌سازی  
**نسخه:** 1.0

