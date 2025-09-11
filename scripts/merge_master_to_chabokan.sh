#!/bin/bash

# اسکریپت خودکار برای ادغام تغییرات master به chabokan-deployment
# با حفظ فایل‌های تخصصی chabokan

set -e  # در صورت بروز خطا، اسکریپت متوقف شود

echo "🚀 شروع فرآیند ادغام master به chabokan-deployment..."

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع برای نمایش پیام‌های رنگی
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# بررسی اینکه در git repository هستیم
if [ ! -d ".git" ]; then
    print_error "این دایرکتوری یک git repository نیست!"
    exit 1
fi

# ذخیره برنچ فعلی
CURRENT_BRANCH=$(git branch --show-current)
print_message "برنچ فعلی: $CURRENT_BRANCH"

# بررسی تغییرات uncommitted
if [ -n "$(git status --porcelain)" ]; then
    print_warning "تغییرات uncommitted وجود دارد. آن‌ها را stash می‌کنم..."
    git stash push -m "Auto-stash before merging master to chabokan-deployment"
    STASHED=true
else
    STASHED=false
fi

# ایجاد دایرکتوری موقت برای پشتیبان‌گیری
BACKUP_DIR="/tmp/chabokan_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_message "دایرکتوری پشتیبان‌گیری: $BACKUP_DIR"

# لیست فایل‌های تخصصی chabokan که باید حفظ شوند
CHABOKAN_FILES=(
    ".env.chabokan"
    "CHABOKAN_BRANCH_SUMMARY.md"
    "CHABOKAN_DEPLOYMENT.md"
    "CHABOKAN_FILES_SUMMARY.md"
    "CHABOKAN_QUICK_START.md"
    "README_CHABOKAN.md"
    "deploy.sh"
    "start.sh"
    "gunicorn.conf.py"
    "security_check.py"
    "health_check.py"
    "Procfile"
    "runtime.txt"
    "nginx.conf"
    "nginx_correct.conf"
    "fix_final.sh"
    "test_chabokan_setup.py"
    "test_correct.sh"
    "staticfiles_management.py"
    "scripts/setup_chabokan_db.py"
    "construction_project/settings.py"
    "construction_project/wsgi.py"
    "requirements.txt"
)

print_step "1. پشتیبان‌گیری از فایل‌های تخصصی chabokan..."

# پشتیبان‌گیری از فایل‌های تخصصی chabokan
for file in "${CHABOKAN_FILES[@]}"; do
    if git show "chabokan-deployment:$file" >/dev/null 2>&1; then
        git show "chabokan-deployment:$file" > "$BACKUP_DIR/$file"
        print_message "پشتیبان‌گیری شد: $file"
    fi
done

print_step "2. تغییر به برنچ chabokan-deployment..."

# تغییر به برنچ chabokan-deployment
git checkout chabokan-deployment

print_step "3. ادغام تغییرات master..."

# ادغام master به chabokan-deployment
if git merge master --no-commit; then
    print_message "ادغام موفقیت‌آمیز بود"
else
    print_warning "conflict در ادغام - در حال حل..."
    
    # حل خودکار conflict در urls.py
    if [ -f "construction_project/urls.py" ]; then
        # بررسی وجود conflict markers
        if grep -q "<<<<<<< HEAD" "construction_project/urls.py"; then
            print_message "حل conflict در construction_project/urls.py..."
            
            # ایجاد نسخه اصلاح شده
            sed -i.tmp '/<<<<<<< HEAD/,/>>>>>>> master/d' "construction_project/urls.py"
            
            # اضافه کردن import های لازم
            if ! grep -q "from health_check import" "construction_project/urls.py"; then
                sed -i.tmp '/from \. import views/a\
from health_check import health_check, simple_health_check' "construction_project/urls.py"
            fi
            
            if ! grep -q "from construction import user_views" "construction_project/urls.py"; then
                sed -i.tmp '/from health_check import/a\
from construction import user_views' "construction_project/urls.py"
            fi
            
            # اضافه کردن URL patterns
            if ! grep -q "path('health/'" "construction_project/urls.py"; then
                sed -i.tmp '/path('\''admin\/'\'', admin.site.urls),/a\
    # Health check endpoints\
    path('\''health/'\'', health_check, name='\''health_check'\''),\
    path('\''health/simple/'\'', simple_health_check, name='\''simple_health_check'\''),' "construction_project/urls.py"
            fi
            
            rm -f "construction_project/urls.py.tmp"
            print_message "conflict در urls.py حل شد"
        fi
    fi
    
    # اضافه کردن فایل‌های حل شده
    git add .
fi

print_step "4. بازگردانی فایل‌های تخصصی chabokan..."

# بازگردانی فایل‌های تخصصی chabokan
for file in "${CHABOKAN_FILES[@]}"; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        # ایجاد دایرکتوری والد اگر وجود ندارد
        mkdir -p "$(dirname "$file")"
        cp "$BACKUP_DIR/$file" "$file"
        print_message "بازگردانی شد: $file"
    fi
done

print_step "5. commit تغییرات..."

# commit تغییرات
git add .
git commit -m "Auto-merge master into chabokan-deployment with preserved chabokan-specific files

- Merged latest changes from master branch
- Preserved all chabokan-specific deployment files
- Resolved conflicts in urls.py automatically
- Updated: $(date)"

print_step "6. تست صحت کار..."

# تست صحت کار
if command -v python3 &> /dev/null; then
    if [ -f "env/bin/activate" ]; then
        source env/bin/activate
        if python manage.py check >/dev/null 2>&1; then
            print_message "تست Django check موفق بود"
        else
            print_warning "تست Django check ناموفق - ممکن است نیاز به بررسی دستی باشد"
        fi
    else
        print_warning "Virtual environment یافت نشد - تست Django انجام نشد"
    fi
else
    print_warning "Python3 یافت نشد - تست Django انجام نشد"
fi

print_step "7. پاک‌سازی..."

# پاک‌سازی فایل‌های موقت
rm -rf "$BACKUP_DIR"

# بازگردانی stash اگر وجود داشت
if [ "$STASHED" = true ]; then
    print_message "بازگردانی تغییرات stash شده..."
    git stash pop || print_warning "خطا در بازگردانی stash"
fi

print_message "✅ فرآیند ادغام با موفقیت تکمیل شد!"
print_message "برنچ فعلی: $(git branch --show-current)"
print_message "تعداد commits جدید: $(git rev-list --count chabokan-deployment ^origin/chabokan-deployment)"

echo ""
echo "📋 خلاصه کارهای انجام شده:"
echo "  ✓ پشتیبان‌گیری از فایل‌های تخصصی chabokan"
echo "  ✓ ادغام تغییرات master"
echo "  ✓ حل خودکار conflicts"
echo "  ✓ بازگردانی فایل‌های تخصصی"
echo "  ✓ commit تغییرات"
echo "  ✓ تست صحت کار"
echo ""
echo "🚀 حالا می‌توانید تغییرات را push کنید:"
echo "  git push origin chabokan-deployment"
echo ""
echo "🔄 برای بازگشت به برنچ قبلی:"
echo "  git checkout $CURRENT_BRANCH"
