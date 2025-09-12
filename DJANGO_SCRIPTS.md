# اسکریپت‌های Django

این پروژه شامل اسکریپت‌هایی برای اجرای آسان دستورات Django است.

## اسکریپت‌های موجود

### 1. `run_django.sh` (Bash)
اسکریپت Bash برای اجرای دستورات Django با فعال‌سازی خودکار محیط مجازی.

```bash
# استفاده
./run_django.sh [دستورات Django]

# مثال‌ها
./run_django.sh migrate construction
./run_django.sh runserver
./run_django.sh shell
./run_django.sh makemigrations
```

### 2. `run_django.py` (Python)
اسکریپت Python برای اجرای دستورات Django با فعال‌سازی خودکار محیط مجازی.

```bash
# استفاده
python3 run_django.py [دستورات Django]

# مثال‌ها
python3 run_django.py migrate construction
python3 run_django.py runserver
python3 run_django.py shell
python3 run_django.py makemigrations
```

## ویژگی‌ها

- ✅ **فعال‌سازی خودکار محیط مجازی**: نیازی به `source env/bin/activate` نیست
- ✅ **بررسی وجود محیط مجازی**: اگر `env` وجود نداشته باشد، خطا می‌دهد
- ✅ **پیام‌های واضح**: وضعیت محیط مجازی و اجرای دستورات را نشان می‌دهد
- ✅ **پشتیبانی از همه دستورات Django**: `migrate`, `runserver`, `shell`, `makemigrations` و...

## استفاده پیشنهادی

برای راحتی بیشتر، می‌توانید alias ایجاد کنید:

```bash
# در ~/.bashrc یا ~/.zshrc
alias dj='./run_django.sh'
alias djp='python3 run_django.py'

# سپس استفاده کنید
dj migrate construction
djp runserver
```

## نکات مهم

1. همیشه از پوشه اصلی پروژه Django اجرا کنید
2. مطمئن شوید که فایل `manage.py` در همان پوشه وجود دارد
3. محیط مجازی باید در پوشه `env` باشد
