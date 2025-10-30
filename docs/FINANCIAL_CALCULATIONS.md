```

```

# 📊 مستند کامل محاسبات مالی پروژه

🎯 هدف

این مستند شامل تمام محاسبات مالی موجود در سیستم است که باید از JavaScript به سمت سرور منتقل شوند.

---

## 📋 فهرست محاسبات

### 🏗️ **1. محاسبات اصلی پروژه**

#### 1.1 سرمایه موجود (Current Capital)

- **نام**: `currentCapital`
- **فرمول**: `totalDeposits - totalWithdrawals`
- **توضیح**: محاسبه سرمایه موجود پس از کسر برداشت‌ها از آورده‌ها
- **مکان استفاده**:
  - `project_dashboard.html` (خط 1263)
  - `transaction_manager.html` (خط 1720)
  - `investor_profile.html` (خط 1681)
- **نوع داده**: عدد اعشاری (تومان)

#### 1.2 سود کل (Total Profit)

- **نام**: `totalProfit`
- **فرمول**: `profitData.reduce((sum, row) => sum + parseFloat(row.amount || 0), 0)`
- **توضیح**: مجموع تمام سودهای تعلق گرفته
- **مکان استفاده**:
  - `project_dashboard.html` (خط 1267)
  - `investor_profile.html` (خط 1679)
  - `transaction_manager.html` (خط 1716)
- **نوع داده**: عدد اعشاری (تومان)

#### 1.3 موجودی کل (Grand Total)

- **نام**: `grandTotal`
- **فرمول**: `netPrincipal + totalProfit`
- **توضیح**: مجموع سرمایه موجود و سود کل
- **مکان استفاده**:
  - `project_dashboard.html` (خط 1273)
  - `investor_profile.html` (خط 1682)
- **نوع داده**: عدد اعشاری (تومان)

---

### 💰 **2. محاسبات هزینه و فروش**

#### 2.1 هزینه نهایی (Final Cost)

- **نام**: `finalCost`
- **فرمول**: `totalExpenses - totalSales`
- **توضیح**: هزینه خالص پروژه پس از کسر فروش‌ها
- **مکان استفاده**: `interestrate_manager.html` (خط 1616)
- **نوع داده**: عدد اعشاری (تومان)

#### 2.2 هزینه هر متر خالص (Net Cost Per Meter)

- **نام**: `netCostPerMeter`
- **فرمول**: `finalCost / totalArea`
- **توضیح**: هزینه ساخت هر متر مربع از فضای مفید
- **مکان استفاده**: `interestrate_manager.html` (خط 1722)
- **نوع داده**: عدد اعشاری (تومان/متر مربع)

#### 2.3 هزینه هر متر ناخالص (Gross Cost Per Meter)

- **نام**: `grossCostPerMeter`
- **فرمول**: `finalCost / totalInfrastructure`
- **توضیح**: هزینه ساخت هر متر مربع از زیربنا
- **مکان استفاده**: `interestrate_manager.html` (خط 1728)
- **نوع داده**: عدد اعشاری (تومان/متر مربع)

#### 2.4 ارزش هر متر (Value Per Meter)

- **نام**: `valuePerMeter`
- **فرمول**: `totalValue / totalArea`
- **توضیح**: ارزش هر متر مربع بر اساس قیمت‌گذاری واحدها
- **مکان استفاده**: `interestrate_manager.html` (خط 1734)
- **نوع داده**: عدد اعشاری (تومان/متر مربع)

#### 2.5 سود نهایی (Final Profit Amount)

- **نام**: `finalProfitAmount`
- **فرمول**: `totalValue - finalCost`
- **توضیح**: مبلغ سود نهایی پروژه
- **مکان استفاده**: `interestrate_manager.html` (خط 1741)
- **نوع داده**: عدد اعشاری (تومان)

#### 2.6 درصد سود کل (Total Profit Percentage)

- **نام**: `totalProfitPercentage`
- **فرمول**: `(finalProfitAmount / finalCost) * 100`
- **توضیح**: درصد سود کل پروژه
- **مکان استفاده**: `interestrate_manager.html` (خط 1745)
- **نوع داده**: عدد اعشاری (درصد)

#### 2.7 مانده صندوق ساختمان (Building Fund Balance)

- **نام**: `buildingFundBalance`
- **فرمول**: `مجموع کل سرمایه - مجموع هزینه خالص`
- **توضیح**: مانده صندوق ساختمان پس از کسر هزینه‌ها از سرمایه
- **مکان استفاده**: `project_dashboard.html` (کارت جدید)
- **نوع داده**: عدد اعشاری (تومان)

---

### 📈 **3. محاسبات سود زمانی**

#### 3.1 دوره متوسط ساخت (Average Construction Period)

- **نام**: `averageConstructionPeriod`
- **فرمول**: `مجموع (هزینه هر دوره × وزن آن دوره) ÷ مجموع کل هزینه‌ها`
- **توضیح**: محاسبه دوره متوسط ساخت بر اساس وزن دوره‌ها
- **مکان استفاده**: `interestrate_manager.html` (خط 1238)
- **نوع داده**: عدد اعشاری (روز)

#### 3.2 درصد سود سالانه (Annual Profit Percentage)

- **نام**: `annualProfitPercentage`
- **فرمول**: `(Total Profit Percentage / Average Construction Period) * 12`
- **توضیح**: درصد سود سالانه بر اساس دوره متوسط ساخت
- **مکان استفاده**: `interestrate_manager.html` (خط 1812)
- **نوع داده**: عدد اعشاری (درصد)

#### 3.3 درصد سود ماهانه (Monthly Profit Percentage)

- **نام**: `monthlyProfitPercentage`
- **فرمول**: `Annual Profit Percentage / 12`
- **توضیح**: درصد سود ماهانه
- **مکان استفاده**: `interestrate_manager.html` (خط 1846)
- **نوع داده**: عدد اعشاری (درصد)

#### 3.4 درصد سود روزانه (Daily Profit Percentage)

- **نام**: `dailyProfitPercentage`
- **فرمول**: `(Annual Profit Percentage / 365) * correction_factor`
- **توضیح**: درصد سود روزانه با ضریب اصلاحی
- **مکان استفاده**: `interestrate_manager.html` (خط 1861)
- **نوع داده**: عدد اعشاری (درصد)

---

### 👥 **4. محاسبات سرمایه‌گذاران**

#### 4.1 آورده کل (Total Principal)

- **نام**: `totalPrincipal`
- **فرمول**: `principalData.reduce((sum, row) => sum + parseFloat(row.amount || 0), 0)`
- **توضیح**: مجموع تمام آورده‌های سرمایه‌گذار
- **مکان استفاده**: `investor_profile.html` (خط 1677)
- **نوع داده**: عدد اعشاری (تومان)

#### 4.2 برداشت کل (Total Withdrawal)

- **نام**: `totalWithdrawal`
- **فرمول**: `withdrawalData.reduce((sum, row) => sum + parseFloat(row.amount || 0), 0)`
- **توضیح**: مجموع تمام برداشت‌های سرمایه‌گذار
- **مکان استفاده**: `investor_profile.html` (خط 1678)
- **نوع داده**: عدد اعشاری (تومان)

#### 4.3 سرمایه خالص (Net Principal)

- **نام**: `netPrincipal`
- **فرمول**: `totalPrincipal + totalWithdrawal`
- **توضیح**: سرمایه موجود پس از کسر برداشت‌ها
- **مکان استفاده**: `investor_profile.html` (خط 1681)
- **نوع داده**: عدد اعشاری (تومان)

#### 4.4 موجودی کل سرمایه‌گذار (Total Balance)

- **نام**: `totalBalance`
- **فرمول**: `netPrincipal + totalProfit`
- **توضیح**: مجموع سرمایه و سود سرمایه‌گذار
- **مکان استفاده**: `investor_profile.html` (خط 1682)
- **نوع داده**: عدد اعشاری (تومان)

#### 4.5 نسبت سرمایه فرد به کل (Capital Ratio)

- **نام**: `capitalRatio`
- **فرمول**: `(netPrincipal / globalStatistics.net_principal) * 100`
- **توضیح**: نسبت سرمایه فرد به سرمایه کل پروژه
- **مکان استفاده**:
  - `investor_profile.html` (خط 1579)
  - `project_dashboard.html` (خط 1557)
- **نوع داده**: عدد اعشاری (درصد)

#### 4.6 نسبت سود فرد به کل (Profit Ratio to Total)

- **نام**: `profitRatioToTotal`
- **فرمول**: `(totalProfit / globalStatistics.total_profits) * 100`
- **توضیح**: نسبت سود فرد به سود کل پروژه
- **مکان استفاده**:
  - `investor_profile.html` (خط 1586)
  - `project_dashboard.html` (خط 1549)
- **نوع داده**: عدد اعشاری (درصد)

#### 4.7 نسبت کل فرد به کل (Total Ratio to Grand Total)

- **نام**: `totalRatioToGrandTotal`
- **فرمول**: `(totalBalance / globalStatistics.grand_total) * 100`
- **توضیح**: نسبت موجودی کل فرد به موجودی کل پروژه
- **مکان استفاده**: `investor_profile.html` (خط 1593)
- **نوع داده**: عدد اعشاری (درصد)

#### 4.8 شاخص نفع (Profit Index)

- **نام**: `profitIndex`
- **فرمول**: `(نسبت سود به سود کل) ÷ (نسبت سرمایه به سرمایه کل)`
- **توضیح**: شاخص نشان‌دهنده کارایی سرمایه‌گذاری
- **مکان استفاده**:
  - `investor_profile.html` (خط 1605)
  - `project_dashboard.html` (خط 1563)
- **نوع داده**: عدد اعشاری

---

### 📊 **5. محاسبات تراکنش‌ها**

#### 5.1 مجموع واریزها (Total Deposits)

- **نام**: `totalDeposits`
- **فرمول**: `filteredData.filter(row => row.transaction_type === 'principal_deposit').reduce(...)`
- **توضیح**: مجموع تمام واریزهای فیلتر شده
- **مکان استفاده**: `transaction_manager.html` (خط 1706)
- **نوع داده**: عدد اعشاری (تومان)

#### 5.2 مجموع برداشت‌ها (Total Withdrawals)

- **نام**: `totalWithdrawals`
- **فرمول**: `filteredData.filter(row => row.transaction_type === 'principal_withdrawal').reduce(...)`
- **توضیح**: مجموع تمام برداشت‌های فیلتر شده
- **مکان استفاده**: `transaction_manager.html` (خط 1710)
- **نوع داده**: عدد اعشاری (تومان)

#### 5.3 مجموع سودها (Total Profits)

- **نام**: `totalProfits`
- **فرمول**: `filteredData.filter(row => row.transaction_type === 'profit_accrual').reduce(...)`
- **توضیح**: مجموع تمام سودهای فیلتر شده
- **مکان استفاده**: `transaction_manager.html` (خط 1714)
- **نوع داده**: عدد اعشاری (تومان)

#### 5.4 سرمایه موجود (Net Capital)

- **نام**: `netCapital`
- **فرمول**: `deposits + withdrawals`
- **توضیح**: سرمایه موجود (برداشت‌ها منفی هستند)
- **مکان استفاده**: `transaction_manager.html` (خط 1720)
- **نوع داده**: عدد اعشاری (تومان)

---

### 🏗️ **6. محاسبات ساخت و ساز**

#### 6.1 تعداد واحدها (Total Units)

- **نام**: `totalUnits`
- **فرمول**: `allInvestors.length` یا `Count('id')`
- **توضیح**: تعداد کل واحدهای پروژه
- **مکان استفاده**: `project_dashboard.html` (خط 1255)
- **نوع داده**: عدد صحیح

#### 6.2 متراژ کل (Total Area)

- **نام**: `totalArea`
- **فرمول**: `Sum('area')`
- **توضیح**: مجموع متراژ مفید همه واحدها
- **مکان استفاده**: `interestrate_manager.html` (خط 1132)
- **نوع داده**: عدد اعشاری (متر مربع)

#### 6.3 قیمت کل (Total Value)

- **نام**: `totalValue`
- **فرمول**: `Sum('total_price')`
- **توضیح**: مجموع قیمت همه واحدها
- **مکان استفاده**: `interestrate_manager.html` (خط 1146)
- **نوع داده**: عدد اعشاری (تومان)

#### 6.4 زیربنای کل (Total Infrastructure)

- **نام**: `totalInfrastructure`
- **فرمول**: `project.total_infrastructure`
- **توضیح**: زیربنای کل پروژه
- **مکان استفاده**: `interestrate_manager.html` (خط 1160)
- **نوع داده**: عدد اعشاری (متر مربع)

#### 6.5 ضریب اصلاحی (Correction Factor)

- **نام**: `correctionFactor`
- **فرمول**: `project.correction_factor`
- **توضیح**: ضریب اصلاحی پروژه
- **مکان استفاده**: `interestrate_manager.html` (خط 1854)
- **نوع داده**: عدد اعشاری

---

### 📅 **7. محاسبات زمانی**

#### 7.1 مدت پروژه (Project Duration)

- **نام**: `projectDuration`
- **فرمول**: `calculateDaysBetweenDates(startDate, endDate)`
- **توضیح**: تعداد روزهای پروژه
- **مکان استفاده**: `project_dashboard.html` (خط 1373)
- **نوع داده**: عدد صحیح (روز)

#### 7.2 روزهای فعال (Active Days)

- **نام**: `activeDays`
- **فرمول**: `uniqueDates.size`
- **توضیح**: تعداد روزهایی که تراکنش انجام شده
- **مکان استفاده**: `project_dashboard.html` (خط 1376)
- **نوع داده**: عدد صحیح (روز)

---

### 💱 **8. محاسبات تبدیل واحد**

#### 8.1 تبدیل به تومان (Convert to Toman)

- **نام**: `convertToToman`
- **فرمول**: `amount / 10`
- **توضیح**: تبدیل از واحد اصلی به تومان
- **مکان استفاده**:
  - `investor_profile.html` (خط 1611-1615)
  - `investor_profile.html` (خط 1687-1691)
- **نوع داده**: عدد اعشاری (تومان)

#### 8.2 تبدیل به کلمات فارسی (Convert to Persian Words)

- **نام**: `amountToPersianWords`
- **فرمول**: تابع تبدیل عدد به کلمات فارسی
- **توضیح**: تبدیل مبلغ به کلمات فارسی
- **مکان استفاده**: `transaction_manager.html` (خط 1726)
- **نوع داده**: رشته (کلمات فارسی)

#### 8.3 فرمت اعداد (Format Numbers)

- **نام**: `formatNumber`
- **فرمول**: `new Intl.NumberFormat('en-US').format(num)`
- **توضیح**: فرمت اعداد با جداکننده هزارگان
- **مکان استفاده**: تمام صفحات
- **نوع داده**: رشته (فرمت شده)

#### 8.4 فرمت درصد (Format Percentage)

- **نام**: `formatPercentage`
- **فرمول**: `num.toFixed(2) + '%'`
- **توضیح**: فرمت درصد با دو رقم اعشار
- **مکان استفاده**: تمام صفحات
- **نوع داده**: رشته (درصد)

---

### 📈 **9. محاسبات آماری**

#### 9.1 میانگین (Average)

- **نام**: `average`
- **فرمول**: `sum / count`
- **توضیح**: محاسبه میانگین
- **مکان استفاده**: محاسبات مختلف
- **نوع داده**: عدد اعشاری

#### 9.2 مجموع تجمعی (Cumulative Sum)

- **نام**: `cumulativeSum`
- **فرمول**: `cumulative_total += amount`
- **توضیح**: محاسبه مجموع تجمعی
- **مکان استفاده**: `api.py` (خط 642)
- **نوع داده**: عدد اعشاری

#### 9.3 تعداد منحصر به فرد (Unique Count)

- **نام**: `uniqueCount`
- **فرمول**: `distinct().count()`
- **توضیح**: تعداد رکوردهای منحصر به فرد
- **مکان استفاده**: `api.py` (خط 698)
- **نوع داده**: عدد صحیح

---

### 🎯 **10. محاسبات خاص**

#### 10.1 نرخ سود فعلی (Current Interest Rate)

- **نام**: `currentInterestRate`
- **فرمول**: `parseFloat(currentInterestRate.rate) * 100`
- **توضیح**: نرخ سود فعلی به درصد
- **مکان استفاده**: `project_dashboard.html` (خط 1372)
- **نوع داده**: عدد اعشاری (درصد)

#### 10.2 تعداد مالکان (Owner Count)

- **نام**: `ownerCount`
- **فرمول**: `filter(inv => inv.participation_type === 'owner').length`
- **توضیح**: تعداد سرمایه‌گذاران با نوع مالک
- **مکان استفاده**: `project_dashboard.html` (خط 1365)
- **نوع داده**: عدد صحیح

#### 10.3 تعداد سرمایه‌گذاران (Investor Count)

- **نام**: `investorCount`
- **فرمول**: `filter(inv => inv.participation_type === 'investor').length`
- **توضیح**: تعداد سرمایه‌گذاران با نوع سرمایه‌گذار
- **مکان استفاده**: `project_dashboard.html` (خط 1366)
- **نوع داده**: عدد صحیح

---

## 🔄 **محاسبات تکراری**

### محاسباتی که در چندین صفحه تکرار شده‌اند:

1. **سرمایه موجود** - در 3 صفحه
2. **نسبت‌های سرمایه‌گذاری** - در 2 صفحه
3. **شاخص نفع** - در 2 صفحه
4. **درصد سود** - در 2 صفحه
5. **موجودی کل** - در 3 صفحه
6. **فرمت اعداد** - در تمام صفحات
7. **تبدیل به تومان** - در 2 صفحه

---

## 🎯 **اهداف انتقال به سمت سرور**

### مزایای فنی:

- کاهش 80% کد JavaScript
- یکپارچگی کامل محاسبات
- دقت بالاتر و اعتبارسنجی بهتر
- نگهداری آسان‌تر
- امنیت بیشتر

### مزایای کسب‌وکار:

- تطبیق‌پذیری: تغییر فرمول‌ها بدون تغییر فرانت‌اند
- گزارش‌گیری: امکان ذخیره تاریخچه محاسبات
- اعتبارسنجی: کنترل بهتر روی صحت محاسبات

---

## 📝 **نکات مهم**

1. **مرجع واحد تراکنش‌ها (Single Source of Truth)**: تمام محاسبات مربوط به آورده/برداشت/سرمایه خالص باید از طریق Manager سفارشی مدل تراکنش انجام شود: `Transaction.objects` با توابع `project_totals(project=None)`, `period_totals(project, period)`, `cumulative_until(project, upto_period)`
   - قاعده استاندارد: `deposits = principal_deposit + loan_deposit`، `withdrawals = principal_withdrawal (منفی)`، `net_capital = deposits + withdrawals`
2. **دقت محاسبات**: تمام محاسبات باید با دقت بالا انجام شوند
3. **اعتبارسنجی**: ورودی‌ها باید اعتبارسنجی شوند
4. **مدیریت خطا**: خطاهای محاسباتی باید مدیریت شوند
5. **مستندسازی**: تمام فرمول‌ها باید مستند شوند
6. **تست**: تمام محاسبات باید تست شوند

---

## 🚀 **مراحل پیاده‌سازی**

1. ✅ ایجاد مستند کامل محاسبات
2. 🔄 ایجاد سرویس محاسبات مالی در Django
3. ⏳ ایجاد API endpoints جدید
4. ⏳ به‌روزرسانی فرانت‌اند
5. ⏳ تست یکپارچگی

---

**تاریخ ایجاد**: 2025-01-04
**نسخه**: 1.0
**وضعیت**: در حال توسعه
