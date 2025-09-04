# استفاده از Python 3.11 به عنوان base image
FROM python:3.11-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ENVIRONMENT=production

# تنظیم دایرکتوری کاری
WORKDIR /app

# نصب system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
    && rm -rf /var/lib/apt/lists/*

# کپی requirements و نصب dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد پروژه
COPY . /app/

# ایجاد دایرکتوری‌های مورد نیاز
RUN mkdir -p /app/logs /app/staticfiles /app/media

# جمع‌آوری static files
RUN python manage.py collectstatic --noinput --settings=construction_project.production_settings

# ایجاد کاربر غیر root
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# پورت
EXPOSE 8000

# دستور اجرا
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "construction_project.wsgi:application"]
