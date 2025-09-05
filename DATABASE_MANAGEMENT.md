# مدیریت دیتابیس Local و Online

## 🎯 **هدف:**
- **دیتابیس آنلاین** محفوظ بماند
- **امکان دانلود** دیتابیس آنلاین برای local
- **جلوگیری از بازنویسی** تصادفی دیتابیس آنلاین

## 📁 **ساختار دیتابیس:**

### **Local Development:**
- `database/local.sqlite3` - دیتابیس محلی (در .gitignore)
- داده‌های تست و development

### **GitHub Codespaces:**
- `database/online.sqlite3` - دیتابیس آنلاین (در Git)
- داده‌های واقعی و production

## 🔧 **دستورات مدیریت:**

### **1. دانلود دیتابیس آنلاین از GitHub:**
```bash
# دانلود ساده
python manage.py download_online_db --confirm

# دانلود با backup از دیتابیس محلی
python manage.py download_online_db --backup-local --confirm

# دانلود از شاخه خاص
python manage.py download_online_db --branch develop --confirm
```

### **2. آپلود دیتابیس محلی به GitHub:**
```bash
# آپلود ساده
python manage.py upload_local_db --confirm

# آپلود با backup از دیتابیس آنلاین
python manage.py upload_local_db --backup-online --confirm

# آپلود با پیام commit سفارشی
python manage.py upload_local_db --backup-online --confirm --commit-message "Update database with new data"
```

### **3. Git Hook (خودکار):**
- قبل از هر `git push`، دیتابیس محلی به آنلاین کپی می‌شود
- backup خودکار از دیتابیس آنلاین ایجاد می‌شود

## ⚠️ **نکات مهم:**

### **برای Local Development:**
1. روی `local.sqlite3` کار کنید
2. تغییرات رو تست کنید
3. وقتی راضی بودید، آپلود کنید:
   ```bash
   python manage.py upload_local_db --backup-online --confirm
   git add database/online.sqlite3
   git commit -m "Update database"
   git push
   ```

### **برای Codespaces:**
1. `git pull` کنید
2. دیتابیس خودکار آپدیت می‌شود
3. روی volume mount کار کنید
4. تغییرات persistent هستند

## 🔒 **امنیت:**

- **دیتابیس آنلاین** همیشه backup می‌شود
- **تأیید دستی** برای آپلود لازم است
- **Git hook** خودکار sync می‌کند
- **Volume mount** در Codespaces محفوظ است

## 📋 **Workflow پیشنهادی:**

### **سناریو 1: کار روی Local**
1. دانلود دیتابیس آنلاین
2. کار روی local
3. تست تغییرات
4. آپلود به آنلاین
5. Push به Git

### **سناریو 2: کار روی Codespaces**
1. Git pull
2. کار روی Codespaces
3. تغییرات persistent هستند
4. نیازی به sync نیست

## 🆘 **Troubleshooting:**

### **اگر دیتابیس آنلاین خراب شد:**
```bash
# بازیابی از backup
cp database/online_backup_YYYYMMDD_HHMMSS.sqlite3 database/online.sqlite3
git add database/online.sqlite3
git commit -m "Restore database from backup"
git push
```

### **اگر دیتابیس محلی خراب شد:**
```bash
# دانلود دیتابیس آنلاین
python manage.py download_online_db --confirm
```
