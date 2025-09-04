# استفاده از Python 3.11 برای Codespaces
FROM mcr.microsoft.com/devcontainers/python:3.11

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ENVIRONMENT=development

# تنظیم دایرکتوری کاری
WORKDIR /workspaces/construction_project

# نصب system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gettext \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# کپی requirements و نصب dependencies
COPY requirements.txt /workspaces/construction_project/
RUN pip install --no-cache-dir -r requirements.txt

# ایجاد دایرکتوری‌های مورد نیاز
RUN mkdir -p /workspaces/construction_project/logs \
             /workspaces/construction_project/staticfiles \
             /workspaces/construction_project/media \
             /workspaces/construction_project/database \
             /workspaces/construction_project/backups

# تنظیم permissions برای volume ها
RUN chown -R vscode:vscode /workspaces/construction_project
RUN chmod -R 755 /workspaces/construction_project/database \
                 /workspaces/construction_project/logs \
                 /workspaces/construction_project/media \
                 /workspaces/construction_project/backups

# پورت
EXPOSE 8000

# دستور اجرا برای development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
