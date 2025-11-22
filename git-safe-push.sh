#!/bin/bash
# اسکریپت امن برای push کردن تغییرات
# این اسکریپت قبل از push، بررسی می‌کند که local با remote sync باشد

set -e  # در صورت خطا، متوقف شود

echo "🔍 بررسی وضعیت Git..."

# بررسی تغییرات uncommitted
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  تغییرات uncommitted وجود دارد!"
    echo "💡 لطفاً ابتدا تغییرات را commit کنید:"
    echo "   git add ."
    echo "   git commit -m 'پیام شما'"
    exit 1
fi

# دریافت آخرین تغییرات از remote
echo "📥 دریافت آخرین تغییرات از remote..."
git fetch origin

# بررسی وضعیت sync
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Local و remote همگام هستند"
    echo "🚀 در حال push..."
    git push origin master
elif [ "$LOCAL" = "$BASE" ]; then
    echo "⚠️  Remote جلوتر است!"
    echo "💡 لطفاً ابتدا pull کنید:"
    echo "   git pull origin master"
    exit 1
elif [ "$REMOTE" = "$BASE" ]; then
    echo "✅ Local جلوتر است"
    echo "🚀 در حال push..."
    git push origin master
else
    echo "⚠️  Local و remote diverged شده‌اند!"
    LOCAL_COUNT=$(git rev-list --count @ ^@{u})
    REMOTE_COUNT=$(git rev-list --count @{u} ^@)
    echo "📋 Local commits: $LOCAL_COUNT"
    echo "📋 Remote commits: $REMOTE_COUNT"
    echo ""
    echo "💡 راهکار:"
    echo "   1. git pull origin master"
    echo "   2. conflict ها را حل کنید"
    echo "   3. git commit"
    echo "   4. git push origin master"
    exit 1
fi

echo "✅ Push با موفقیت انجام شد!"

