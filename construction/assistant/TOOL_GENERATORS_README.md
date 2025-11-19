# راهنمای استفاده از Tool Generators

## 🌟 ویژگی عمومی (Generic)

**این generator ها برای استفاده در هر پروژه Django طراحی شده‌اند!**

هر دو generator به صورت خودکار تنظیمات Django را پیدا می‌کنند و می‌توانند در هر پروژه Django استفاده شوند.

---

این پروژه شامل دو generator جداگانه برای تولید خودکار Tools است:

## 📋 فهرست

1. [Schema Tool Generator](#schema-tool-generator) - بر اساس OpenAPI Schema
2. [Model Tool Generator](#model-tool-generator) - بر اساس Models, Views و Serializers

---

## 🔷 Schema Tool Generator

### فایل: `schema_tool_generator.py`

این generator از **OpenAPI Schema** تولید شده توسط `drf-spectacular` استفاده می‌کند.

### مزایا:
- ✅ شامل تمام endpoints (standard و custom actions)
- ✅ شامل تمام پارامترهای requestBody
- ✅ شامل descriptions و types کامل
- ✅ شامل enum values و format ها
- ✅ شامل security requirements
- ✅ شامل response schemas
- ✅ به‌روزرسانی خودکار با تغییر ViewSets

### نحوه استفاده:

```bash
# استفاده پیش‌فرض
python schema_tool_generator.py

# تعیین فایل خروجی
python schema_tool_generator.py --output my_tools.py

# تعیین مسیر schema
python schema_tool_generator.py --schema /path/to/schema.json
```

### خروجی:
- فایل Python شامل تمام Tools
- آمار استخراج شده (تعداد endpoints، پارامترها، tags)
- گروه‌بندی بر اساس tags

---

## 🔶 Model Tool Generator

### فایل: `model_tool_generator.py`

این generator از **ViewSets, Serializers و Models** استفاده می‌کند.

### مزایا:
- ✅ تحلیل مستقیم ViewSets
- ✅ استفاده از Serializers برای استخراج فیلدها
- ✅ استفاده از Models برای تولید body
- ✅ پشتیبانی از custom actions
- ✅ تولید کد body کامل برای CRUD operations

### نحوه استفاده:

```bash
# استفاده پیش‌فرض
python model_tool_generator.py

# تعیین فایل خروجی
python model_tool_generator.py --output my_tools.py
```

### خروجی:
- فایل Python شامل تمام Tools
- کد body کامل برای list, retrieve, create, update, delete
- استفاده مستقیم از Models

---

## 🔄 مقایسه دو روش

| ویژگی | Schema Generator | Model Generator |
|-------|-----------------|-----------------|
| منبع داده | OpenAPI Schema | ViewSets, Serializers, Models |
| کامل بودن | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| سرعت | سریع | متوسط |
| به‌روزرسانی | خودکار | نیاز به اجرای مجدد |
| Custom Actions | ✅ کامل | ✅ کامل |
| Request Body | ✅ کامل | ⚠️ نیاز به Serializer |
| Response Info | ✅ دارد | ❌ ندارد |
| Security Info | ✅ دارد | ⚠️ محدود |
| Body Implementation | ❌ TODO | ✅ کامل |

---

## 💡 توصیه

### استفاده از Schema Generator زمانی که:
- ✅ می‌خواهید کامل‌ترین اطلاعات را داشته باشید
- ✅ نیاز به اطلاعات security و responses دارید
- ✅ می‌خواهید از OpenAPI schema استفاده کنید
- ✅ نیاز به به‌روزرسانی خودکار دارید

### استفاده از Model Generator زمانی که:
- ✅ می‌خواهید کد body کامل داشته باشید
- ✅ نیاز به استفاده مستقیم از Models دارید
- ✅ Schema در دسترس نیست
- ✅ می‌خواهید کنترل بیشتری روی تولید کد داشته باشید

---

## 🌍 استفاده در پروژه‌های دیگر Django

### پیش‌نیازها:
1. Django REST Framework نصب شده باشد
2. `drf-spectacular` برای Schema Generator (اختیاری)
3. `langchain` برای استفاده از Tools

### نحوه استفاده در پروژه جدید:

#### 1. کپی کردن فایل‌ها:
```bash
# کپی schema_tool_generator.py
cp schema_tool_generator.py /path/to/your/project/

# کپی model_tool_generator.py
cp model_tool_generator.py /path/to/your/project/
```

#### 2. استفاده از Schema Generator:
```bash
# تولید schema (اگر وجود ندارد)
python manage.py spectacular --file schema.json --format openapi-json

# تولید Tools
python schema_tool_generator.py --schema schema.json --output my_tools.py
```

#### 3. استفاده از Model Generator:
```bash
# Auto-discovery (پیدا کردن خودکار ViewSets)
python model_tool_generator.py --output my_tools.py

# با ViewSets مشخص
python model_tool_generator.py \
  --viewsets myapp.api.UserViewSet,myapp.api.ProductViewSet \
  --output my_tools.py

# با ProjectManager (اگر پروژه شما از project filtering استفاده می‌کند)
python model_tool_generator.py \
  --project-manager myapp.project_manager.ProjectManager \
  --output my_tools.py
```

### تنظیمات خودکار:
- ✅ پیدا کردن خودکار `settings.py`
- ✅ پیدا کردن خودکار ViewSets در `*.api` modules
- ✅ پیدا کردن خودکار Models در `*.models` modules
- ✅ تولید خودکار schema در صورت نبود

### نکات مهم:
- اگر پروژه شما از ساختار متفاوتی استفاده می‌کند، می‌توانید ViewSets را به صورت دستی مشخص کنید
- ProjectManager اختیاری است - فقط اگر پروژه شما از project filtering استفاده می‌کند
- Schema Generator می‌تواند schema را خودش تولید کند (نیاز به drf-spectacular)

---

## 📝 مثال استفاده

### Schema Generator:
```bash
cd construction/assistant
python schema_tool_generator.py --output generated_tools_from_schema.py
```

### Model Generator:
```bash
cd construction/assistant
python model_tool_generator.py --output generated_tools_from_models.py
```

---

## ⚠️ نکات مهم

1. **هر دو generator** نیاز به Django setup دارند
2. **Schema Generator** نیاز به فایل `schema.json` دارد (در صورت نبود، خودش تولید می‌کند)
3. **Model Generator** نیاز به دسترسی به ViewSets و Models دارد
4. خروجی هر دو generator نیاز به **بررسی و تکمیل** دارد
5. Tools تولید شده باید در فایل `tools.py` import شوند

---

## 🔧 تنظیمات

### Schema Generator:
- مسیر پیش‌فرض schema: `schema.json` در root پروژه
- مسیر پیش‌فرض خروجی: `construction/assistant/generated_tools_from_schema.py`

### Model Generator:
- ViewSets مورد استفاده: لیست در `generate_all_tools()`
- مسیر پیش‌فرض خروجی: `construction/assistant/generated_tools_from_models.py`

---

## 📚 منابع

- [OpenAPI Specification](https://swagger.io/specification/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)

