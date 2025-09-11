# راهنمای ادغام خودکار تغییرات

## 🎯 هدف

این راهنما نحوه استفاده از اسکریپت‌های خودکار برای ادغام تغییرات برنچ `master` به برنچ `chabokan-deployment` را توضیح می‌دهد.

## 🚀 استفاده ساده

### روش ۱: اسکریپت ساده (پیشنهادی)

```bash
./merge_chabokan.sh
```

### روش ۲: اسکریپت کامل

```bash
./scripts/merge_master_to_chabokan.sh
```

## 📋 آنچه اسکریپت انجام می‌دهد

### ✅ مراحل خودکار:

1. **پشتیبان‌گیری**: از تمام فایل‌های تخصصی chabokan
2. **ادغام**: تغییرات master به chabokan-deployment
3. **حل conflict**: خودکار در فایل‌های رایج
4. **بازگردانی**: فایل‌های تخصصی chabokan
5. **commit**: تغییرات با پیام مناسب
6. **تست**: بررسی صحت کار Django

### 🔒 فایل‌هایی که حفظ می‌شوند:

- **مستندات**: `CHABOKAN_*.md`
- **تنظیمات**: `.env.chabokan`, `settings.py`, `wsgi.py`
- **اسکریپت‌ها**: `deploy.sh`, `start.sh`, `security_check.py`
- **فایل‌های deployment**: `gunicorn.conf.py`, `Procfile`, `runtime.txt`

## 🛠️ تنظیمات پیش از استفاده

### ۱. اطمینان از بروزرسانی master

```bash
# برنچ master را بروزرسانی کنید
git checkout master
git pull origin master

# یا اگر تغییرات محلی دارید
git checkout master
git stash
git pull origin master
git stash pop
```

### ۲. بررسی وضعیت فعلی

```bash
# وضعیت git را بررسی کنید
git status

# برنچ فعلی را ببینید
git branch
```

## 📖 مثال کامل استفاده

```bash
# ۱. بروزرسانی master
git checkout master
git pull origin master

# ۲. اجرای اسکریپت ادغام
./merge_chabokan.sh

# ۳. push تغییرات (اختیاری)
git push origin chabokan-deployment
```

## ⚠️ نکات مهم

### ✅ موارد امن:

- اسکریپت تغییرات uncommitted را خودکار stash می‌کند
- فایل‌های تخصصی chabokan همیشه حفظ می‌شوند
- در صورت خطا، اسکریپت متوقف می‌شود

### 🔍 بررسی دستی در صورت نیاز:

اگر اسکریپت با خطا مواجه شد:

```bash
# وضعیت git را بررسی کنید
git status

# conflicts را بررسی کنید
git diff

# stash را بررسی کنید
git stash list
```

## 🐛 عیب‌یابی

### مشکل ۱: خطای permission

```bash
chmod +x merge_chabokan.sh
chmod +x scripts/merge_master_to_chabokan.sh
```

### مشکل ۲: conflict پیچیده

```bash
# حل دستی conflict
git status
# فایل‌های conflict را ویرایش کنید
git add .
git commit -m "Resolve merge conflicts"
```

### مشکل ۳: خطای Django

```bash
# فعال کردن virtual environment
source env/bin/activate

# تست Django
python manage.py check
python manage.py migrate --plan
```

## 📊 بررسی نتیجه

### ✅ نشانه‌های موفقیت:

- پیام "✅ فرآیند ادغام با موفقیت تکمیل شد!"
- برنچ فعلی: `chabokan-deployment`
- تست Django موفق

### 📈 بررسی تغییرات:

```bash
# دیدن commits جدید
git log --oneline -10

# مقایسه با origin
git log --oneline origin/chabokan-deployment..HEAD

# دیدن فایل‌های تغییر یافته
git diff --name-only HEAD~1
```

## 🔄 بازگشت به حالت قبلی

اگر مشکلی پیش آمد:

```bash
# بازگشت به commit قبلی
git reset --hard HEAD~1

# یا بازگشت به origin
git reset --hard origin/chabokan-deployment

# بازگردانی stash
git stash pop
```

## 📞 پشتیبانی

در صورت بروز مشکل:

1. **بررسی لاگ**: خروجی اسکریپت را بررسی کنید
2. **بررسی git status**: وضعیت repository را ببینید
3. **تست دستی**: مراحل را به صورت دستی انجام دهید

---

**نکته**: این اسکریپت برای استفاده منظم طراحی شده است. برای اولین بار یا در صورت تغییرات اساسی، ممکن است نیاز به بررسی دستی باشد.
