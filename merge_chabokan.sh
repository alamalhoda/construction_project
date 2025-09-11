#!/bin/bash

# اسکریپت ساده برای ادغام master به chabokan-deployment
# استفاده: ./merge_chabokan.sh

echo "🔄 ادغام تغییرات master به chabokan-deployment..."

# اجرای اسکریپت اصلی
./scripts/merge_master_to_chabokan.sh

echo "✅ کار تمام شد!"
