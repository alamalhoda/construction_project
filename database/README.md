# دیتابیس پروژه

## 📁 **ساختار فایل‌ها:**

- `local.sqlite3` - دیتابیس محلی (در .gitignore)
- `online.sqlite3` - دیتابیس آنلاین (در Git)

## 🔒 **نحوه کار:**

### **Local Development:**
- دیتابیس در `database/local.sqlite3` ذخیره می‌شود
- فایل در .gitignore است و push نمی‌شود
- هر developer دیتابیس جداگانه دارد

### **GitHub Codespaces:**
- دیتابیس در `database/online.sqlite3` استفاده می‌شود
- دیتابیس در volume mount شده ذخیره می‌شود
- داده‌ها persistent هستند
- مستقل از local database

## 🚀 **راه‌اندازی:**

### **برای Local:**
```bash
# کپی کردن دیتابیس آنلاین
cp database/online.sqlite3 database/local.sqlite3

# یا ایجاد دیتابیس جدید
python manage.py migrate
```

### **برای Codespaces:**
- دیتابیس خودکار از `online.sqlite3` کپی می‌شود
- یا دستی کپی کنید:
```bash
cp database/online.sqlite3 database/online.sqlite3
```

## ⚠️ **نکات مهم:**

1. **local.sqlite3 در Git نیست** - هر محیط جداگانه
2. **online.sqlite3 در Git است** - برای Codespaces
3. **Volume mount** در Codespaces - داده‌ها persistent
4. **Backup** قبل از تغییرات مهم
