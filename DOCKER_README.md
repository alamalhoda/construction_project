# 🐳 راهنمای Docker - پروژه ساخت‌وساز (ساده‌شده)

## 📋 پیش‌نیازها

- Docker
- Docker Compose

## 🚀 اجرای سریع

### Development Mode
```bash
# اجرای در حالت development
docker-compose -f docker-compose.dev.yml up --build

# دسترسی به اپلیکیشن
http://localhost:8000
```

### Production Mode
```bash
# اجرای در حالت production
docker-compose up --build

# دسترسی به اپلیکیشن
http://localhost:8000 (مستقیماً)
http://localhost:80 (از طریق Nginx)
```

## 🔧 دستورات مفید

### مدیریت Container ها
```bash
# اجرای container ها
docker-compose up -d

# توقف container ها
docker-compose down

# مشاهده لاگ‌ها
docker-compose logs -f web

# اجرای دستور در container
docker-compose exec web python manage.py shell
```

### مدیریت دیتابیس
```bash
# اجرای migration
docker-compose exec web python manage.py migrate

# ایجاد superuser
docker-compose exec web python manage.py createsuperuser

# جمع‌آوری static files
docker-compose exec web python manage.py collectstatic
```

### Backup و Restore
```bash
# Backup دیتابیس
docker-compose exec db pg_dump -U construction_user construction_db > backup.sql

# Restore دیتابیس
docker-compose exec -T db psql -U construction_user construction_db < backup.sql
```

## 🌐 سرویس‌ها

### Web Application (Port 8000)
- Django application
- Gunicorn server
- 3 workers
- SQLite database (در پوشه database/)

### Nginx (Port 80) - اختیاری
- Reverse proxy
- Static files serving

### Volume ها
- `database_volume`: فایل دیتابیس SQLite
- `backups_volume`: فایل‌های backup
- `static_volume`: فایل‌های static
- `media_volume`: فایل‌های media
- `logs_volume`: فایل‌های log

## 🔒 تنظیمات امنیتی

### Production
- SSL/TLS encryption
- Security headers
- Rate limiting
- Non-root user

### Environment Variables
```bash
# Database
DB_NAME=construction_db
DB_USER=construction_user
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1

# Django
DJANGO_ENVIRONMENT=production
SECRET_KEY=your-secret-key
```

## 📁 Volume ها

- `postgres_data`: دیتابیس PostgreSQL
- `redis_data`: داده‌های Redis
- `static_volume`: فایل‌های static
- `media_volume`: فایل‌های media
- `logs_volume`: فایل‌های log

## 🐛 Troubleshooting

### مشکل در اتصال به دیتابیس
```bash
# بررسی وضعیت container ها
docker-compose ps

# بررسی لاگ‌های دیتابیس
docker-compose logs db
```

### مشکل در static files
```bash
# جمع‌آوری مجدد static files
docker-compose exec web python manage.py collectstatic --noinput
```

### مشکل در migration
```bash
# اجرای migration به صورت دستی
docker-compose exec web python manage.py migrate --run-syncdb
```

## 📊 Monitoring

### Health Checks
- Database: `pg_isready`
- Redis: `redis-cli ping`
- Web: HTTP health check

### Logs
```bash
# مشاهده تمام لاگ‌ها
docker-compose logs

# مشاهده لاگ‌های خاص
docker-compose logs web
docker-compose logs db
docker-compose logs nginx
```

## 🔄 Update و Deploy

### Update کد
```bash
# Pull آخرین تغییرات
git pull

# Rebuild و restart
docker-compose up --build -d
```

### Backup قبل از update
```bash
# Backup دیتابیس
docker-compose exec db pg_dump -U construction_user construction_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 📞 پشتیبانی

در صورت بروز مشکل، لاگ‌ها را بررسی کنید:
```bash
docker-compose logs -f
```
