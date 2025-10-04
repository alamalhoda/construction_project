# 🎨 قانون رنگ‌بندی استاندارد پروژه

## 🎯 هدف
این قانون رنگ‌بندی استاندارد پروژه را تعریف می‌کند که در تمام صفحات و کامپوننت‌های مالی باید رعایت شود.

---

## 🚫 **قوانین ممنوع**

### ❌ **استفاده از رنگ‌های hard-coded ممنوع است**
```css
/* ❌ اشتباه - رنگ hard-coded */
color: #21ba45;
background-color: green;

/* ✅ درست - استفاده از CSS Variables */
color: var(--profit-color);
background-color: var(--profit-color-light);
```

### ❌ **رنگ‌های غیراستاندارد ممنوع است**
- از رنگ‌هایی غیر از رنگ‌های تعریف شده استفاده نکنید
- هر رنگ فقط برای مفهوم مالی مشخص خود استفاده شود

---

## ✅ **رنگ‌های استاندارد پروژه**

### 🎨 **دسته‌بندی مالی:**
- **🔵 آبی (#2185d0)** - آورده و واریزی
- **🔴 قرمز (#db2828)** - برداشت و خروجی  
- **🟢 سبز (#21ba45)** - سود مشارکت و درآمد
- **🟣 بنفش (#667eea)** - سرمایه موجود و موجودی
- **🔴 قرمز تیره (#dc3545)** - هزینه‌ها و خرجی
- **⚫ خاکستری (#6c757d)** - مجموع و کل

---

## 🎨 **CSS Variables**

### **رنگ‌های اصلی:**
```css
:root {
    --deposit-color: #2185d0;           /* آبی - آورده */
    --withdrawal-color: #db2828;        /* قرمز - برداشت */
    --profit-color: #21ba45;            /* سبز - سود مشارکت */
    --capital-color: #667eea;           /* بنفش - سرمایه موجود */
    --expense-color: #dc3545;           /* قرمز تیره - هزینه‌ها */
    --total-color: #6c757d;             /* خاکستری - مجموع */
}
```

### **نسخه‌های شفاف برای پس‌زمینه:**
```css
:root {
    --deposit-color-light: rgba(33, 133, 208, 0.1);
    --withdrawal-color-light: rgba(219, 40, 40, 0.1);
    --profit-color-light: rgba(33, 186, 69, 0.1);
    --capital-color-light: rgba(102, 126, 234, 0.1);
    --expense-color-light: rgba(220, 53, 69, 0.1);
    --total-color-light: rgba(108, 117, 125, 0.1);
}
```

### **حالت تاریک:**
```css
[data-theme="dark"] {
    --deposit-color: #4fc3f7;           /* آبی روشن‌تر */
    --withdrawal-color: #f48fb1;        /* قرمز روشن‌تر */
    --profit-color: #81c784;            /* سبز روشن‌تر */
    --capital-color: #9575cd;           /* بنفش روشن‌تر */
    --expense-color: #f48fb1;           /* قرمز روشن‌تر */
    --total-color: #b0bec5;             /* خاکستری روشن‌تر */
}
```

---

## 🚀 **الگوهای استفاده**

### **1. کارت‌های آماری:**
```css
.stat-card.principal-card {
    background: linear-gradient(135deg, var(--capital-color) 0%, var(--secondary-color) 100%);
    box-shadow: 0 12px 40px var(--capital-color-light);
}

.stat-card.profit-card {
    background: linear-gradient(135deg, var(--profit-color) 0%, var(--secondary-color) 100%);
    box-shadow: 0 12px 40px var(--profit-color-light);
}
```

### **2. جداول:**
```css
.summary-table th:nth-child(2) { /* آورده */
    background-color: var(--deposit-color-light);
    border-left: 3px solid var(--deposit-color);
}

.summary-table th:nth-child(3) { /* برداشت */
    background-color: var(--withdrawal-color-light);
    border-left: 3px solid var(--withdrawal-color);
}
```

### **3. هدرها:**
```html
<th class="deposit-header"><i class="fas fa-plus-circle"></i> آورده</th>
<th class="withdrawal-header"><i class="fas fa-minus-circle"></i> برداشت</th>
<th class="profit-header"><i class="fas fa-chart-line"></i> سود</th>
```

### **4. نمودارها و چارت‌ها:**
```javascript
// استفاده در Chart.js
const chartColors = {
    deposit: 'var(--deposit-color)',
    withdrawal: 'var(--withdrawal-color)',
    profit: 'var(--profit-color)',
    capital: 'var(--capital-color)',
    expense: 'var(--expense-color)',
    total: 'var(--total-color)'
};
```

---

## 📝 **قوانین الزامی**

### 1. **یکپارچگی**
- تمام صفحات باید از همین رنگ‌ها استفاده کنند
- هر رنگ فقط برای مفهوم مالی مشخص خود استفاده شود

### 2. **معنایی**
- 🔵 آبی فقط برای آورده و واریزی
- 🔴 قرمز فقط برای برداشت و خروجی
- 🟢 سبز فقط برای سود مشارکت و درآمد
- 🟣 بنفش فقط برای سرمایه موجود و موجودی
- 🔴 قرمز تیره فقط برای هزینه‌ها و خرجی
- ⚫ خاکستری فقط برای مجموع و کل

### 3. **تم‌پذیری**
- پشتیبانی از حالت روشن و تیره الزامی است
- از CSS Variables استفاده شود، نه رنگ‌های hard-coded

### 4. **نسخه Light**
- برای پس‌زمینه‌ها از نسخه‌های شفاف استفاده شود
- `--color-light` برای پس‌زمینه‌ها
- `--color` برای متن و border ها

---

## ⚠️ **هشدارها**

### 1. **عدم رعایت قوانین**
- استفاده از رنگ‌های hard-coded رد می‌شود
- رنگ‌های غیراستاندارد ممنوع است

### 2. **تطبیق با تم**
- تمام رنگ‌ها باید با حالت تاریک و روشن سازگار باشند
- از CSS Variables استفاده کنید

### 3. **به‌روزرسانی**
- در صورت نیاز به تغییر، باید از فایل `project_dashboard.html` تغییر داده شوند
- تمام صفحات جدید باید این استاندارد را رعایت کنند

---

## 📚 **مراجع**

- فایل `project_dashboard.html` - تعریف استاندارد رنگ‌ها
- فایل `interestrate_manager.html` - نمونه استفاده
- فایل `investor_profile.html` - نمونه استفاده

---

**تاریخ ایجاد**: 2025-01-04  
**نسخه**: 1.0  
**وضعیت**: فعال
