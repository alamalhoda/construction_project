# راهنمای تأیید جداسازی پروژه‌ها

## بررسی دستی جداسازی پروژه‌ها

برای اطمینان از اینکه ساختار چند پروژه‌ای به درستی کار می‌کند و پروژه‌ها بر روی یکدیگر تأثیر ندارند، می‌توانید مراحل زیر را انجام دهید:

### 1. بررسی فیلتر ViewSetها

همه ViewSetهای زیر باید `get_queryset()` داشته باشند که بر اساس پروژه جاری فیلتر می‌کنند:

- ✅ `ExpenseViewSet` - خط 21-28 در `construction/api.py`
- ✅ `InvestorViewSet` - خط 381-388 در `construction/api.py`
- ✅ `PeriodViewSet` - خط 646-653 در `construction/api.py`
- ✅ `SaleViewSet` - خط 1296-1303 در `construction/api.py`
- ✅ `TransactionViewSet` - خط 1370-1377 در `construction/api.py`
- ✅ `InterestRateViewSet` - خط 1564-1571 در `construction/api.py`
- ✅ `UnitViewSet` - خط 1591-1598 در `construction/api.py`
- ✅ `UnitSpecificExpenseViewSet` - خط 1644-1651 در `construction/api.py`

**نحوه بررسی:**
```python
# در shell Django:
python manage.py shell

from construction.api import ExpenseViewSet, InvestorViewSet
from construction.project_manager import ProjectManager
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User

# ایجاد request
factory = RequestFactory()
request = factory.get('/')
request.user = User.objects.first()

# اضافه کردن session
middleware = SessionMiddleware(lambda x: x)
middleware.process_request(request)
request.session.save()

# تنظیم پروژه 1
from construction.models import Project
project1 = Project.objects.first()
ProjectManager.set_current_project(request, project1.id)

# بررسی ExpenseViewSet
viewset = ExpenseViewSet()
viewset.request = request
expenses = list(viewset.get_queryset())
print(f"هزینه‌های پروژه {project1.name}: {len(expenses)} مورد")

# تنظیم پروژه 2
project2 = Project.objects.all()[1] if Project.objects.count() > 1 else None
if project2:
    ProjectManager.set_current_project(request, project2.id)
    expenses = list(viewset.get_queryset())
    print(f"هزینه‌های پروژه {project2.name}: {len(expenses)} مورد")
```

### 2. بررسی API Endpoints

بررسی کنید که APIها فقط داده‌های پروژه جاری را برمی‌گردانند:

**Test با curl یا Postman:**

```bash
# 1. لاگین و دریافت session
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' \
  -c cookies.txt

# 2. تنظیم پروژه 1
curl -X POST http://localhost:8000/api/v1/Project/switch/ \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1}' \
  -b cookies.txt

# 3. دریافت سرمایه‌گذاران
curl http://localhost:8000/api/v1/Investor/ \
  -b cookies.txt

# 4. تنظیم پروژه 2
curl -X POST http://localhost:8000/api/v1/Project/switch/ \
  -H "Content-Type: application/json" \
  -d '{"project_id": 2}' \
  -b cookies.txt

# 5. دریافت سرمایه‌گذاران (باید متفاوت باشد)
curl http://localhost:8000/api/v1/Investor/ \
  -b cookies.txt
```

### 3. بررسی Session Management

بررسی کنید که `ProjectManager` به درستی کار می‌کند:

```python
# در shell Django:
from construction.project_manager import ProjectManager
from construction.models import Project
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User

factory = RequestFactory()
request = factory.get('/')
request.user = User.objects.first()

# اضافه کردن session
middleware = SessionMiddleware(lambda x: x)
middleware.process_request(request)
request.session.save()

# تست get_current_project بدون session
project = ProjectManager.get_current_project(request)
print(f"پروژه بدون session: {project}")

# تست set_current_project
project1 = Project.objects.first()
ProjectManager.set_current_project(request, project1.id)
project = ProjectManager.get_current_project(request)
print(f"پروژه بعد از set: {project.name} (ID: {project.id})")

# بررسی session
print(f"Session current_project_id: {request.session.get('current_project_id')}")
```

### 4. بررسی UI (Frontend)

بررسی کنید که:
1. Project Switcher پروژه جاری را نمایش می‌دهد
2. با تغییر پروژه، داده‌های صفحه تغییر می‌کنند
3. رنگ و آیکون پروژه به درستی نمایش داده می‌شوند

**مراحل تست:**

1. باز کردن صفحه داشبورد (`/dashboard/project/`)
2. مشاهده Project Switcher در گوشه بالا-راست
3. کلیک روی Project Switcher و مشاهده لیست پروژه‌ها
4. تغییر پروژه
5. بررسی اینکه:
   - صفحه reload می‌شود
   - داده‌های جدید (مثل سرمایه‌گذاران، هزینه‌ها) نمایش داده می‌شوند
   - رنگ و آیکون پروژه تغییر می‌کند

### 5. بررسی Context Processor

بررسی کنید که `project_context` در همه templateها در دسترس است:

```python
# در shell Django:
from construction_project.context_processors import project_context
from django.test import RequestFactory
from django.contrib.auth.models import User

factory = RequestFactory()
request = factory.get('/')
request.user = User.objects.first()

# اضافه کردن session
from django.contrib.sessions.middleware import SessionMiddleware
middleware = SessionMiddleware(lambda x: x)
middleware.process_request(request)
request.session.save()

# تنظیم پروژه
from construction.project_manager import ProjectManager
from construction.models import Project
project = Project.objects.first()
ProjectManager.set_current_project(request, project.id)

# دریافت context
context = project_context(request)
print(f"current_project: {context['current_project'].name if context['current_project'] else None}")
print(f"all_projects count: {context['all_projects'].count()}")
```

### 6. بررسی Forms

بررسی کنید که فرم‌ها به صورت خودکار پروژه جاری را تنظیم می‌کنند:

1. باز کردن صفحه ایجاد سرمایه‌گذار (`/construction/Investor/create/`)
2. بررسی اینکه فیلد پروژه (اگر visible است) به درستی پر شده است
3. ایجاد یک سرمایه‌گذار جدید
4. بررسی اینکه پروژه به درستی ذخیره شده است

### 7. بررسی Database

بررسی کنید که داده‌های پروژه‌ها در دیتابیس جدا هستند:

```sql
-- بررسی سرمایه‌گذاران هر پروژه
SELECT 
    p.name as project_name,
    COUNT(i.id) as investor_count
FROM construction_project p
LEFT JOIN construction_investor i ON i.project_id = p.id
GROUP BY p.id, p.name;

-- بررسی هزینه‌های هر پروژه
SELECT 
    p.name as project_name,
    COUNT(e.id) as expense_count,
    SUM(e.amount) as total_expense
FROM construction_project p
LEFT JOIN construction_expense e ON e.project_id = p.id
GROUP BY p.id, p.name;

-- بررسی تراکنش‌های هر پروژه
SELECT 
    p.name as project_name,
    COUNT(t.id) as transaction_count,
    SUM(t.amount) as total_amount
FROM construction_project p
LEFT JOIN construction_transaction t ON t.project_id = p.id
GROUP BY p.id, p.name;
```

### 8. تست تغییر پروژه

1. وارد سیستم شوید
2. به صفحه لیست سرمایه‌گذاران بروید
3. تعداد سرمایه‌گذاران را یادداشت کنید
4. پروژه را تغییر دهید
5. بررسی کنید که:
   - تعداد سرمایه‌گذاران تغییر کرده است (یا حداقل لیست متفاوت است)
   - داده‌های جدید متعلق به پروژه جدید هستند

### 9. تست همزمان چند کاربر

برای اطمینان از اینکه session هر کاربر جدا است:

1. دو مرورگر مختلف (یا incognito mode) باز کنید
2. در هر دو لاگین کنید
3. در مرورگر اول پروژه 1 را انتخاب کنید
4. در مرورگر دوم پروژه 2 را انتخاب کنید
5. بررسی کنید که هر کاربر داده‌های پروژه خودش را می‌بیند

## مشکلات احتمالی و راه‌حل

### مشکل: همه داده‌ها در همه پروژه‌ها نمایش داده می‌شوند

**راه‌حل:**
1. بررسی کنید که `get_queryset()` در ViewSetها به درستی فیلتر می‌کند
2. بررسی کنید که `ProjectManager.get_current_project()` به درستی کار می‌کند
3. بررسی کنید که session به درستی ذخیره می‌شود

### مشکل: تغییر پروژه کار نمی‌کند

**راه‌حل:**
1. بررسی کنید که endpoint `/api/v1/Project/switch/` به درستی کار می‌کند
2. بررسی کنید که JavaScript به درستی `location.reload()` را صدا می‌زند
3. بررسی کنید که session middleware فعال است

### مشکل: رنگ و آیکون پروژه نمایش داده نمی‌شود

**راه‌حل:**
1. بررسی کنید که `ProjectSerializer` شامل فیلدهای `color` و `icon` است
2. بررسی کنید که JavaScript به درستی این فیلدها را می‌خواند
3. بررسی کنید که فونت Awesome لود شده است

## نتیجه

اگر همه تست‌های بالا PASS شوند، ساختار چند پروژه‌ای به درستی فعال شده است و پروژه‌ها بر روی یکدیگر تأثیر ندارند.

