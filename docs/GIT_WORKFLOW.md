# 🔄 راهنمای Workflow استاندارد Git

## ⚠️ **مشکل رایج: Diverged Branches**

وقتی از چند جا (مثلاً Local و Codespaces) کار می‌کنید، ممکن است local و remote diverged شوند. این راهنما به شما کمک می‌کند از این مشکل جلوگیری کنید.

---

## ✅ **Workflow استاندارد (پیشنهادی)**

### **قبل از شروع کار:**

```bash
# 1. همیشه ابتدا pull کنید
git pull origin master

# 2. بررسی کنید که همه چیز OK است
git status
```

### **در حین کار:**

```bash
# 1. تغییرات را commit کنید
git add .
git commit -m "توضیح تغییرات"

# 2. قبل از push، دوباره pull کنید
git pull origin master

# 3. اگر conflict بود، حل کنید
# (conflict ها را حل کنید)
git add .
git commit -m "Merge remote changes"

# 4. حالا push کنید
git push origin master
```

---

## 🛡️ **روش‌های پیشگیری**

### **1. استفاده از Git Hook (خودکار)**

یک hook نصب شده که قبل از هر push، بررسی می‌کند:
- ✅ آیا local با remote sync است؟
- ✅ آیا diverged شده‌اند؟
- ✅ اگر diverged بودند، push را متوقف می‌کند

**این hook خودکار است و نیازی به فعال‌سازی ندارد!**

### **2. استفاده از اسکریپت امن**

```bash
# به جای git push، از این استفاده کنید:
./git-safe-push.sh
```

این اسکریپت:
- ✅ بررسی می‌کند که local با remote sync باشد
- ✅ اگر diverged بود، push را متوقف می‌کند
- ✅ راهنمایی می‌دهد که چه کار کنید

### **3. بررسی دستی قبل از push**

```bash
# بررسی وضعیت
git fetch origin
git status

# اگر diverged بود، pull کنید
git pull origin master
```

---

## 🔧 **حل مشکل Diverged**

### **اگر local و remote diverged شدند:**

```bash
# 1. دریافت آخرین تغییرات
git fetch origin

# 2. Pull با merge
git pull origin master

# 3. اگر conflict بود:
#    - فایل‌های conflict را باز کنید
#    - conflict ها را حل کنید
#    - git add .
#    - git commit

# 4. Push
git push origin master
```

### **اگر می‌خواهید تغییرات local را حفظ کنید:**

```bash
# استفاده از strategy که local را اولویت دهد
git pull origin master -X ours
git commit -m "Merge - حفظ تغییرات local"
git push origin master
```

---

## 📋 **چک‌لیست قبل از Push**

- [ ] `git status` - بررسی تغییرات uncommitted
- [ ] `git fetch origin` - دریافت آخرین تغییرات
- [ ] `git status` - بررسی diverged بودن
- [ ] اگر diverged بود: `git pull origin master`
- [ ] حل conflict ها (اگر وجود داشت)
- [ ] `git push origin master`

---

## 🚨 **هشدارها**

### **❌ هرگز این کارها را نکنید:**

1. **Force push بدون بررسی:**
   ```bash
   # ❌ خطرناک!
   git push --force origin master
   ```

2. **Push بدون pull:**
   ```bash
   # ❌ ممکن است diverged شود
   git push origin master  # بدون pull
   ```

3. **Ignore کردن conflict ها:**
   ```bash
   # ❌ ممکن است تغییرات از دست برود
   git pull origin master
   # conflict ها را ignore کنید
   ```

---

## 💡 **نکات مهم**

### **1. همیشه از یک branch کار کنید:**
- اگر روی `master` کار می‌کنید، همیشه از `master` push کنید
- اگر branch جدید ساختید، قبل از merge به master، pull کنید

### **2. قبل از push، همیشه pull کنید:**
```bash
git pull origin master && git push origin master
```

### **3. از اسکریپت امن استفاده کنید:**
```bash
./git-safe-push.sh  # به جای git push
```

---

## 🔍 **بررسی وضعیت**

### **بررسی diverged بودن:**

```bash
# تعداد commit های local که در remote نیست
git rev-list --count @ ^@{u}

# تعداد commit های remote که در local نیست
git rev-list --count @{u} ^@
```

### **مشاهده commit های diverged:**

```bash
# commit های local
git log @ ^@{u} --oneline

# commit های remote
git log @{u} ^@ --oneline
```

---

## 📚 **مراجع**

- [Git Workflow Best Practices](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [Git Merge Strategies](https://git-scm.com/docs/merge-strategies)

---

**تاریخ ایجاد**: 2025-01-28  
**نسخه**: 1.0

