# دیتابیس پروژه

## 📁 **ساختار فایل‌ها:**

- `db.sqlite3` - دیتابیس اصلی (در .gitignore)
- `db.sqlite3.example` - نمونه دیتابیس با داده‌های تست

## 🔒 **نحوه کار:**

### **Local Development:**
- دیتابیس در `database/db.sqlite3` ذخیره می‌شود
- فایل در .gitignore است و push نمی‌شود
- هر developer دیتابیس جداگانه دارد

### **GitHub Codespaces:**
- دیتابیس در volume mount شده ذخیره می‌شود
- داده‌ها persistent هستند
- مستقل از local database

## 🚀 **راه‌اندازی:**

### **برای Local:**
```bash
# کپی کردن نمونه دیتابیس
cp database/db.sqlite3.example database/db.sqlite3

# یا ایجاد دیتابیس جدید
python manage.py migrate
```

### **برای Codespaces:**
- دیتابیس خودکار ایجاد می‌شود
- یا از نمونه کپی کنید:
```bash
cp database/db.sqlite3.example database/db.sqlite3
```

## ⚠️ **نکات مهم:**

1. **دیتابیس در Git نیست** - هر محیط جداگانه
2. **Volume mount** در Codespaces - داده‌ها persistent
3. **Backup** قبل از تغییرات مهم
4. **مثال** در `db.sqlite3.example` موجود است
