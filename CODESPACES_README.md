# راهنمای GitHub Codespaces

## 🚀 **مزایای Codespaces:**

- ✅ **Persistent Storage** - داده‌ها حفظ می‌شوند
- ✅ **SQLite Support** - بدون مشکل کار می‌کند
- ✅ **120 ساعت رایگان** در ماه
- ✅ **2 Core CPU** + **4GB RAM**
- ✅ **32GB Storage**
- ✅ **HTTPS** خودکار
- ✅ **Port Forwarding** خودکار

## 📋 **مراحل راه‌اندازی:**

### 1. **فعال‌سازی Codespaces**
1. به repository بروید
2. روی **"Code"** کلیک کنید
3. **"Codespaces"** tab را انتخاب کنید
4. **"Create codespace"** را کلیک کنید

### 2. **انتظار Build**
- Codespace خودکار build می‌شود
- Docker container ایجاد می‌شود
- Dependencies نصب می‌شوند
- Database migrate می‌شود

### 3. **دسترسی به اپلیکیشن**
- Port 8000 خودکار forward می‌شود
- URL در notification نمایش داده می‌شود
- یا از **"Ports"** tab استفاده کنید

## 🔧 **دستورات مفید:**

### **اجرای سرور:**
```bash
python manage.py runserver 0.0.0.0:8000
```

### **ایجاد Superuser:**
```bash
python manage.py createsuperuser
```

### **اجرای Tests:**
```bash
python manage.py test
```

### **Collect Static Files:**
```bash
python manage.py collectstatic --noinput
```

## 📁 **ساختار فایل‌ها:**

```
/workspaces/construction_project/
├── .devcontainer/
│   ├── devcontainer.json  # Volume mounts تعریف شده
│   └── Dockerfile
├── database/              # 🔒 VOLUME - Persistent
│   └── online.sqlite3
├── logs/                  # 🔒 VOLUME - Persistent
├── media/                 # 🔒 VOLUME - Persistent
├── backups/               # 🔒 VOLUME - Persistent
└── staticfiles/           # Temporary
```

## 🔒 **Volume Mounts:**

در `devcontainer.json` تعریف شده:
```json
"mounts": [
  "source=construction-db,target=/workspaces/construction_project/database,type=volume",
  "source=construction-logs,target=/workspaces/construction_project/logs,type=volume", 
  "source=construction-media,target=/workspaces/construction_project/media,type=volume",
  "source=construction-backups,target=/workspaces/construction_project/backups,type=volume"
]
```

### **مزایای Volume Mounts:**
- ✅ **داده‌ها persistent** هستند
- ✅ **حتی بعد از rebuild** حفظ می‌شوند
- ✅ **Performance بهتر** از bind mount
- ✅ **Backup خودکار** GitHub

## 🔒 **تنظیمات امنیتی:**

- **DEBUG**: False (production mode)
- **ALLOWED_HOSTS**: ['*'] (برای Codespaces)
- **SSL**: غیرفعال (Codespaces خودکار HTTPS)
- **Database**: SQLite (persistent volume)

## ⚙️ **فایل‌های Environment:**

### `.env.codespaces` (مخصوص Codespaces)
```bash
# خودکار کپی می‌شود به .env
DJANGO_SETTINGS_MODULE=construction_project.production_settings
USE_SQLITE=true
DB_NAME=database/online.sqlite3
SECRET_KEY=codespaces-secret-key
```

### `.env.example` (نمونه)
- تنظیمات کامل برای local development
- شامل PostgreSQL و SQLite options
- شامل Email configuration

### `.env` (محلی)
- تنظیمات local development
- از .env.codespaces کپی می‌شود در Codespaces

## 💡 **نکات مهم:**

1. **داده‌ها persistent هستند** - SQLite فایل حفظ می‌شود
2. **Port 8000** خودکار forward می‌شود
3. **HTTPS** خودکار فعال است
4. **Git integration** کامل
5. **VS Code** در browser

## 🆘 **Troubleshooting:**

### **اگر سرور شروع نشد:**
```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### **اگر static files نمایش داده نمی‌شوند:**
```bash
python manage.py collectstatic --noinput
```

### **اگر database error:**
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📊 **محدودیت‌ها:**

- **120 ساعت رایگان** در ماه
- **2 Core CPU** + **4GB RAM**
- **32GB Storage**
- **Codespace** بعد از 30 دقیقه غیرفعال می‌شود

## 🎯 **توصیه:**

Codespaces برای **تست و development** عالی است و داده‌ها persistent هستند!
