# 📊 مستندات فایل Excel Dynamic - پروژه ساختمانی

## 📑 فهرست مطالب
1. [معرفی و هدف](#معرفی-و-هدف)
2. [ساختار کلی](#ساختار-کلی)
3. [شیت‌های موجود](#شیتهای-موجود)
4. [Named Ranges](#named-ranges)
5. [فرمول‌های کلیدی](#فرمولهای-کلیدی)
6. [نحوه استفاده](#نحوه-استفاده)
7. [توسعه و نگهداری](#توسعه-و-نگهداری)
8. [مشکلات رایج و راه‌حل](#مشکلات-رایج-و-راهحل)

---

## 🎯 معرفی و هدف

### هدف اصلی
تولید یک فایل Excel کاملاً داینامیک که:
- ✅ همه محاسبات با فرمول‌های Excel انجام شود
- ✅ کاربر بتواند داده‌های پایه را ویرایش کند
- ✅ تمام محاسبات به صورت خودکار به‌روز شوند
- ✅ مسیر محاسبات کاملاً شفاف و قابل ردیابی باشد
- ✅ از Named Ranges برای خوانایی بهتر استفاده شود

### تفاوت با Excel Static
| ویژگی | Static | Dynamic |
|--------|--------|---------|
| محاسبات | در سرور (Python) | در Excel (فرمول) |
| قابلیت ویرایش | خیر | بله |
| شفافیت | کم | بالا |
| به‌روزرسانی | نیاز به تولید مجدد | خودکار |
| حجم فایل | کمتر | بیشتر |

---

## 🏗️ ساختار کلی

### فایل اصلی
```
construction/excel_export_dynamic.py
```

### کلاس‌های اصلی
```python
ExcelDynamicExportService         # سرویس اصلی تولید Excel
NamedRangeHelper                  # کمک‌کننده برای Named Ranges
FormulaGuideSheet                 # شیت راهنمای فرمول‌ها
PeriodExpenseSummarySheet         # شیت کمکی محاسبه دوره متوسط
ComprehensiveMetricsSheet         # شیت جامع محاسبات
TransactionProfitCalculationsSheet # شیت محاسبه سود تراکنش‌ها
```

### API Endpoint
```
GET /api/v1/Project/export_excel_dynamic/
```

### Django Management Command
```bash
python manage.py export_excel --dynamic
```

---

## 📋 شیت‌های موجود

### 1️⃣ شیت‌های راهنما و فهرست

#### `📋 فهرست`
- **هدف**: فهرست تمام شیت‌ها با لینک مستقیم
- **محتوا**: نام شیت، توضیح، لینک
- **ویژگی**: قابلیت کلیک و رفتن به شیت

#### `📖 راهنمای فرمول‌ها`
- **هدف**: مستندات کامل Named Ranges و فرمول‌ها
- **بخش‌ها**:
  - Named Ranges شیت‌های پایه (8 مورد)
  - Named Ranges شیت Comprehensive_Metrics (21 مورد)
  - فرمول‌های رایج
  - نکات مهم

---

### 2️⃣ شیت‌های داده پایه

#### `Project`
- **محتوا**: اطلاعات پروژه
- **ستون‌های کلیدی**: نام، تاریخ شروع/پایان، زیربنای کل، ضریب اصلاحی
- **ویژگی**: Freeze header, Auto-filter

#### `Units`
- **محتوا**: واحدهای ساختمانی
- **ستون‌های کلیدی**: نام، متراژ، قیمت هر متر، قیمت نهایی
- **Named Range**: `UnitAreas`, `UnitPrices`

#### `Investors`
- **محتوا**: سرمایه‌گذاران
- **ستون‌های کلیدی**: نام، نام خانوادگی، نوع مشارکت، واحدها، تاریخ قرارداد

#### `Periods`
- **محتوا**: دوره‌های زمانی
- **ستون‌های کلیدی**: عنوان، سال، ماه، **وزن دوره** ⭐
- **نکته مهم**: وزن دوره برای محاسبه دوره متوسط ساخت استفاده می‌شود

#### `InterestRates`
- **محتوا**: نرخ‌های سود
- **ستون‌های کلیدی**: نرخ سود روزانه، تاریخ اعمال، فعال

#### `Transactions`
- **محتوا**: تراکنش‌های مالی
- **ستون‌های کلیدی**: 
  - سرمایه‌گذار، دوره، تاریخ
  - مبلغ (ستون I)
  - نوع تراکنش (ستون J): آورده، خروج از سرمایه، سود
  - **روز مانده (ستون L)** ⭐ - برای محاسبه سود
- **Named Range**: `TransactionAmounts`, `TransactionTypes`, `TransactionInvestors`, `TransactionPeriods`

#### `Expenses`
- **محتوا**: هزینه‌ها
- **ستون‌های کلیدی**: دوره، نوع هزینه، مبلغ (ستون F)
- **Named Range**: `ExpenseAmounts`

#### `Sales`
- **محتوا**: فروش/مرجوعی
- **ستون‌های کلیدی**: دوره، مبلغ (ستون E)
- **Named Range**: `SaleAmounts`

#### `UserProfiles`
- **محتوا**: کاربران سیستم
- **ستون‌های کلیدی**: نام کاربری، نقش، بخش

---

### 3️⃣ شیت‌های کمکی محاسباتی

#### `PeriodExpenseSummary`
- **هدف**: محاسبه دوره متوسط ساخت
- **ساختار**:
  | شناسه دوره | عنوان دوره | جمع هزینه دوره | وزن دوره |
  |-----------|------------|----------------|----------|
  | 1 | مرداد 1402 | `=SUMIF(...)` | `=VLOOKUP(...)` |

- **فرمول‌ها**:
  ```excel
  جمع هزینه دوره = SUMIF(Expenses!$C:$C, A3, Expenses!$F:$F)
  وزن دوره = VLOOKUP(A3, Periods!$A:$G, 7, FALSE)
  ```

- **استفاده**: در محاسبه `AverageConstructionPeriod`

---

### 4️⃣ شیت جامع محاسبات

#### `Comprehensive_Metrics` ⭐⭐⭐
**مهم‌ترین شیت - قلب سیستم محاسباتی**

##### بخش 1: واحدها
```excel
تعداد واحدها = COUNTA(Units!A:A)-1
متراژ کل = SUM(UnitAreas)
ارزش کل = SUM(UnitPrices)
```

##### بخش 2: اطلاعات مالی
```excel
آورده کل = SUMIF(TransactionTypes, "آورده", TransactionAmounts)
برداشت کل = SUMIF(TransactionTypes, "خروج از سرمایه", TransactionAmounts)
سرمایه موجود = TotalDeposits + TotalWithdrawals
سود تراکنش‌ها = SUMIF(TransactionTypes, "سود", TransactionAmounts)
موجودی کل = TotalCapital + TransactionProfit
```

##### بخش 3: هزینه‌ها
```excel
هزینه کل = SUM(ExpenseAmounts)
فروش کل = SUM(SaleAmounts)
هزینه خالص = TotalExpenses - TotalSales
سود نهایی ساختمان = TotalValue - NetCost
```

##### بخش 4: محاسبات درصدی
```excel
درصد سود تراکنش‌ها = (TransactionProfit / TotalCapital) * 100
درصد سود نهایی ساختمان = (BuildingProfit / TotalValue) * 100
درصد سود کل هزینه = (BuildingProfit / NetCost) * 100
```

##### بخش 5: محاسبات زمانی ⭐
```excel
دوره متوسط ساخت (ماه) = SUMPRODUCT(PeriodExpenseSummary!C:C, PeriodExpenseSummary!D:D) / SUM(PeriodExpenseSummary!C:C)

درصد سود سالانه = (TotalProfitPercentage / AverageConstructionPeriod) * 12
درصد سود ماهانه = AnnualProfitPercentage / 12
درصد سود روزانه = MonthlyProfitPercentage / 30
```

**نکته مهم**: محاسبات زمانی به صورت زنجیره‌ای انجام می‌شوند

##### بخش 6: سرمایه‌گذاران
```excel
تعداد کل سرمایه‌گذاران = COUNTA(Investors!A:A)-1
```

---

### 5️⃣ شیت محاسبه سود تراکنش‌ها

#### `Transaction_Profit_Calculations` ⭐⭐
**شیت جدید - محاسبه سود با فرمول**

##### هدف
محاسبه سود هر تراکنش آورده/برداشت با فرمول:
```
سود = مبلغ × (نرخ سود روزانه / 100) × روز مانده
```

##### ساختار
| ستون | عنوان | فرمول |
|------|--------|--------|
| A | ID تراکنش | مقدار ثابت |
| B | سرمایه‌گذار | `=VLOOKUP(A3,Transactions!$A:$D,4,FALSE)` |
| C | تاریخ | `=VLOOKUP(A3,Transactions!$A:$G,7,FALSE)` |
| D | نوع | `=VLOOKUP(A3,Transactions!$A:$J,10,FALSE)` |
| E | مبلغ تراکنش | `=VLOOKUP(A3,Transactions!$A:$I,9,FALSE)` |
| F | نرخ سود روزانه | `=DailyProfitPercentage` |
| G | روز مانده | `=VLOOKUP(A3,Transactions!$A:$L,12,FALSE)` |
| H | **سود محاسبه شده** | `=E3*(F3/100)*G3` |

##### ویژگی‌ها
- ✅ فقط تراکنش‌های آورده و برداشت (بدون سود)
- ✅ استفاده از VLOOKUP برای خواندن از Transactions
- ✅ نرخ سود داینامیک از Comprehensive_Metrics
- ✅ جمع کل با Named Range: `CalculatedTotalProfit`

##### مقایسه سود
```excel
اختلاف = CalculatedTotalProfit - TotalProfit
```

---

### 6️⃣ شیت‌های تحلیلی

#### `Investor_Analysis_Dynamic`
- **هدف**: تحلیل هر سرمایه‌گذار
- **محتوا**: آورده، برداشت، سرمایه خالص، سود، نسبت‌ها

#### `Period_Summary_Dynamic`
- **هدف**: خلاصه هر دوره
- **محتوا**: آورده، برداشت، سود، هزینه‌ها، فروش

#### `Transaction_Summary_Dynamic`
- **هدف**: خلاصه تراکنش‌ها
- **محتوا**: تعداد و مبلغ تراکنش‌ها به تفکیک نوع

---

## 🏷️ Named Ranges

### دسته‌بندی Named Ranges

#### 1. شیت‌های پایه (8 مورد)
```
TransactionAmounts     → Transactions!$I:$I
TransactionTypes       → Transactions!$J:$J
TransactionInvestors   → Transactions!$C:$C
TransactionPeriods     → Transactions!$E:$E
ExpenseAmounts         → Expenses!$F:$F
SaleAmounts            → Sales!$E:$E
UnitAreas              → Units!$E:$E
UnitPrices             → Units!$G:$G
```

#### 2. واحدها و ارزش (3 مورد)
```
TotalUnits             → Comprehensive_Metrics!$B$4
TotalArea              → Comprehensive_Metrics!$B$5
TotalValue             → Comprehensive_Metrics!$B$6
```

#### 3. اطلاعات مالی (5 مورد)
```
TotalDeposits          → Comprehensive_Metrics!$B$9
TotalWithdrawals       → Comprehensive_Metrics!$B$10
TotalCapital           → Comprehensive_Metrics!$B$11
TransactionProfit      → Comprehensive_Metrics!$B$12
TotalProfit            → Comprehensive_Metrics!$B$12  (alias)
TotalBalance           → Comprehensive_Metrics!$B$13
```

#### 4. هزینه‌ها (4 مورد)
```
TotalExpenses          → Comprehensive_Metrics!$B$16
TotalSales             → Comprehensive_Metrics!$B$17
NetCost                → Comprehensive_Metrics!$B$18
BuildingProfit         → Comprehensive_Metrics!$B$19
```

#### 5. درصدها (3 مورد)
```
TransactionProfitPercentage  → Comprehensive_Metrics!$B$22
BuildingProfitPercentage     → Comprehensive_Metrics!$B$23
TotalProfitPercentage        → Comprehensive_Metrics!$B$24
```

#### 6. محاسبات زمانی (4 مورد) ⭐
```
AverageConstructionPeriod    → Comprehensive_Metrics!$B$27
AnnualProfitPercentage       → Comprehensive_Metrics!$B$28
MonthlyProfitPercentage      → Comprehensive_Metrics!$B$29
DailyProfitPercentage        → Comprehensive_Metrics!$B$30
```

#### 7. سایر (2 مورد)
```
TotalInvestors         → Comprehensive_Metrics!$B$33
CalculatedTotalProfit  → Transaction_Profit_Calculations!$H$569
```

**جمع کل: 29 Named Range**

---

## 🧮 فرمول‌های کلیدی

### 1. دوره متوسط ساخت
```excel
=SUMPRODUCT(PeriodExpenseSummary!C:C, PeriodExpenseSummary!D:D) / SUM(PeriodExpenseSummary!C:C)
```
**توضیح**: میانگین وزنی دوره‌ها بر اساس هزینه هر دوره

**مراحل محاسبه**:
1. برای هر دوره: `جمع هزینه × وزن دوره`
2. جمع همه حاصل‌ضرب‌ها
3. تقسیم بر مجموع کل هزینه‌ها

### 2. درصد سود سالانه
```excel
=IF(AverageConstructionPeriod=0, 0, (TotalProfitPercentage/AverageConstructionPeriod)*12)
```
**توضیح**: تبدیل درصد سود کل به سالانه بر اساس دوره متوسط

### 3. سود تراکنش
```excel
=مبلغ × (نرخ سود روزانه / 100) × روز مانده
```
**مثال**:
```excel
=E3*(F3/100)*G3
```

### 4. VLOOKUP برای خواندن از Transactions
```excel
=VLOOKUP(A3, Transactions!$A:$L, 12, FALSE)
```
**پارامترها**:
- `A3`: ID تراکنش
- `Transactions!$A:$L`: محدوده جستجو
- `12`: شماره ستون (روز مانده)
- `FALSE`: تطابق دقیق

---

## 📘 نحوه استفاده

### برای کاربران

#### 1. دانلود فایل
```bash
# از API
GET /api/v1/Project/export_excel_dynamic/

# یا از Management Command
python manage.py export_excel --dynamic
```

#### 2. باز کردن فایل
- فایل با Excel 2016 یا بالاتر باز شود
- از LibreOffice Calc هم پشتیبانی می‌شود

#### 3. مشاهده راهنما
- شیت `📋 فهرست` را باز کنید
- شیت `📖 راهنمای فرمول‌ها` را مطالعه کنید

#### 4. ویرایش داده‌ها
- فقط شیت‌های پایه را ویرایش کنید
- شیت‌های محاسباتی خودکار به‌روز می‌شوند

#### 5. بررسی محاسبات
- روی هر سلول کلیک کنید
- فرمول را در نوار فرمول ببینید
- F2 را بزنید تا سلول‌های مرتبط هایلایت شوند

---

### برای توسعه‌دهندگان

#### ساختار کد

```python
# construction/excel_export_dynamic.py

class ExcelDynamicExportService:
    def __init__(self, project):
        self.project = project
        self.workbook = Workbook()
    
    def generate_excel(self):
        # 1. حذف شیت پیش‌فرض
        # 2. ایجاد فهرست
        # 3. ایجاد راهنما
        # 4. ایجاد شیت‌های پایه
        # 5. ایجاد شیت‌های کمکی
        # 6. ایجاد شیت جامع
        # 7. ایجاد شیت‌های تحلیلی
        # 8. تعریف Named Ranges
        return self.workbook
```

#### افزودن شیت جدید

```python
class NewCalculationSheet:
    @staticmethod
    def create(workbook, project):
        ws = workbook.create_sheet("New_Sheet")
        
        # هدرها
        headers = ['ستون 1', 'ستون 2']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # داده‌ها
        row = 2
        for item in data:
            ws.cell(row=row, column=1, value=item.field1)
            ws.cell(row=row, column=2, value='=FORMULA')
            row += 1
        
        # Named Range
        NamedRangeHelper.create_named_range(
            workbook, 'NewRange', 'New_Sheet', '$B$2'
        )
        
        return ws
```

#### افزودن به فرآیند تولید

```python
def generate_excel(self):
    # ...
    NewCalculationSheet.create(self.workbook, self.project)
    # ...
```

---

## 🔧 توسعه و نگهداری

### نکات مهم برای توسعه

#### 1. ترتیب ایجاد شیت‌ها مهم است!
```python
# ❌ اشتباه - شیت محاسباتی قبل از پایه
ComprehensiveMetricsSheet.create(...)
ProjectSheet.create(...)

# ✅ درست - شیت پایه قبل از محاسباتی
ProjectSheet.create(...)
ComprehensiveMetricsSheet.create(...)
```

#### 2. Named Ranges باید قبل از استفاده تعریف شوند
```python
# ابتدا Named Range تعریف شود
NamedRangeHelper.create_named_range(workbook, 'TotalCapital', ...)

# سپس در فرمول استفاده شود
ws['B5'] = '=TotalCapital * 0.1'
```

#### 3. استفاده از Absolute References
```python
# ❌ اشتباه
NamedRangeHelper.create_named_range(workbook, 'Total', 'Sheet', 'B5')

# ✅ درست
NamedRangeHelper.create_named_range(workbook, 'Total', 'Sheet', '$B$5')
```

#### 4. فرمول‌ها باید به صورت رشته باشند
```python
# ❌ اشتباه
ws['B5'] = =A5 * 2

# ✅ درست
ws['B5'] = '=A5 * 2'
```

#### 5. استفاده از f-string برای فرمول‌های داینامیک
```python
row = 5
ws[f'B{row}'] = f'=A{row} * 2'
```

---

### الگوهای رایج

#### الگو 1: جمع ستون با شرط
```python
ws['B10'] = '=SUMIF(TransactionTypes, "آورده", TransactionAmounts)'
```

#### الگو 2: VLOOKUP
```python
ws['B5'] = f'=VLOOKUP(A{row}, Transactions!$A:$L, 12, FALSE)'
```

#### الگو 3: محاسبه درصد
```python
ws['B5'] = '=IF(TotalCapital=0, 0, (TotalProfit/TotalCapital)*100)'
```

#### الگو 4: SUMPRODUCT برای میانگین وزنی
```python
ws['B5'] = '=SUMPRODUCT(Values!A:A, Weights!B:B) / SUM(Values!A:A)'
```

#### الگو 5: زنجیره محاسبات
```python
# محاسبه اول
ws['B5'] = '=A5 * 2'
NamedRangeHelper.create_named_range(workbook, 'FirstCalc', 'Sheet', '$B$5')

# محاسبه دوم بر اساس اول
ws['B6'] = '=FirstCalc / 12'
NamedRangeHelper.create_named_range(workbook, 'SecondCalc', 'Sheet', '$B$6')

# محاسبه سوم بر اساس دوم
ws['B7'] = '=SecondCalc / 30'
```

---

### بهینه‌سازی عملکرد

#### 1. استفاده از select_related
```python
# ❌ کند - N+1 Query
transactions = Transaction.objects.filter(project=project)
for trans in transactions:
    investor_name = trans.investor.first_name  # Query جداگانه

# ✅ سریع - یک Query
transactions = Transaction.objects.filter(
    project=project
).select_related('investor', 'period')
```

#### 2. محدود کردن داده‌ها
```python
# فقط فیلدهای مورد نیاز
transactions = Transaction.objects.filter(
    project=project
).only('id', 'amount', 'transaction_type')
```

#### 3. استفاده از bulk operations
```python
# برای تعداد زیاد سلول‌ها
cells = []
for row in range(1, 1000):
    cells.append(ws.cell(row=row, column=1, value=row))
```

---

## ⚠️ مشکلات رایج و راه‌حل

### مشکل 1: #NAME? Error
**علت**: Named Range تعریف نشده یا اشتباه نوشته شده

**راه‌حل**:
```python
# بررسی Named Ranges
for name in workbook.defined_names:
    print(name, workbook.defined_names[name].attr_text)
```

### مشکل 2: #REF! Error
**علت**: ارجاع به سلول یا شیت نامعتبر

**راه‌حل**:
- نام شیت را بررسی کنید
- آدرس سلول را بررسی کنید
- از absolute references استفاده کنید

### مشکل 3: #VALUE! Error
**علت**: نوع داده اشتباه در فرمول

**راه‌حل**:
```excel
# استفاده از IF برای جلوگیری از تقسیم بر صفر
=IF(A1=0, 0, B1/A1)
```

### مشکل 4: فرمول‌ها محاسبه نمی‌شوند
**علت**: Excel در حالت Manual Calculation است

**راه‌حل**:
- Formulas → Calculation Options → Automatic
- یا F9 برای محاسبه دستی

### مشکل 5: VLOOKUP کار نمی‌کند
**علت**: 
- ستون اشتباه
- محدوده اشتباه
- مقدار جستجو یافت نشده

**راه‌حل**:
```excel
# استفاده از IFERROR
=IFERROR(VLOOKUP(A1, Data!$A:$Z, 5, FALSE), "یافت نشد")
```

### مشکل 6: تاریخ‌های فارسی
**علت**: Excel تاریخ فارسی را نمی‌شناسد

**راه‌حل**:
- تاریخ را به صورت متن ذخیره کنید
- یا از تاریخ میلادی استفاده کنید

### مشکل 7: حجم فایل زیاد
**علت**: تعداد زیاد فرمول‌ها و Named Ranges

**راه‌حل**:
- از محدوده‌های کوچک‌تر استفاده کنید
- فرمول‌های تکراری را بهینه کنید
- از Defined Names به جای فرمول‌های طولانی

### مشکل 8: ردیف‌های نامطابق
**علت**: شیت‌ها ردیف‌های متفاوت دارند

**راه‌حل**:
- از VLOOKUP با ID استفاده کنید
- از INDEX-MATCH به جای ارجاع مستقیم

---

## 📊 آمار و اطلاعات فنی

### نسخه فعلی
- **تاریخ ایجاد**: دی ماه 1403
- **نسخه**: 1.0.0
- **تعداد شیت‌ها**: 18 شیت
- **تعداد Named Ranges**: 29 مورد
- **حجم فایل**: ~120 KB
- **تعداد تراکنش‌ها**: ~570 تراکنش

### سازگاری
- ✅ Microsoft Excel 2016+
- ✅ Microsoft Excel 365
- ✅ LibreOffice Calc 6.0+
- ⚠️ Google Sheets (محدودیت Named Ranges)
- ❌ Excel 2010 و قدیمی‌تر

### محدودیت‌ها
- حداکثر 3000 تراکنش (محدودیت عملکرد)
- حداکثر 100 دوره
- حداکثر 200 سرمایه‌گذار

---

## 🚀 توسعه‌های آینده

### فاز 1 (تکمیل شده) ✅
- [x] شیت‌های پایه
- [x] شیت جامع محاسبات
- [x] Named Ranges
- [x] محاسبه دوره متوسط ساخت
- [x] محاسبه سود تراکنش‌ها
- [x] راهنمای فرمول‌ها

### فاز 2 (پیشنهادی)
- [ ] نمودارهای داینامیک
- [ ] Pivot Tables
- [ ] Conditional Formatting پیشرفته
- [ ] Data Validation
- [ ] محافظت از شیت‌ها
- [ ] ماکروها (VBA)

### فاز 3 (پیشنهادی)
- [ ] مقایسه با بودجه
- [ ] پیش‌بینی جریان نقدی
- [ ] تحلیل حساسیت
- [ ] گزارش‌های خودکار
- [ ] صادرات به PDF

### فاز 4 (پیشنهادی)
- [ ] اتصال به Power BI
- [ ] اتصال به Tableau
- [ ] API برای به‌روزرسانی
- [ ] نسخه وب (Excel Online)

---

## 📞 پشتیبانی و مستندات

### فایل‌های مرتبط
```
construction/excel_export_dynamic.py      # کد اصلی
construction/excel_export.py              # نسخه Static
construction/api.py                       # API Endpoints
docs/API_REFERENCE.md                     # مستندات API
DYNAMIC_EXCEL_DOCUMENTATION.md            # این فایل
```

### لینک‌های مفید
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [Excel Functions Reference](https://support.microsoft.com/en-us/excel)
- [Named Ranges Guide](https://support.microsoft.com/en-us/office/define-and-use-names-in-formulas)

### تماس با توسعه‌دهنده
- **پروژه**: سیستم مدیریت پروژه‌های ساختمانی
- **تاریخ**: دی ماه 1403
- **نسخه Django**: 4.2+
- **نسخه Python**: 3.9+

---

## 📝 یادداشت‌های مهم

### نکته 1: دو نوع سود
```
1. سود تراکنش‌ها (TransactionProfit/TotalProfit):
   - سودی که به سرمایه‌گذاران پرداخت شده
   - در جدول Transactions ذخیره شده
   - Named Range: TotalProfit

2. سود نهایی ساختمان (BuildingProfit):
   - ارزش کل - هزینه خالص
   - محاسبه شده، نه ذخیره شده
   - Named Range: BuildingProfit
```

### نکته 2: محاسبه دوره متوسط
```
دوره متوسط ساخت = Σ(هزینه دوره × وزن دوره) / Σ(کل هزینه‌ها)

مثال:
دوره 1: هزینه = 1000, وزن = 5  →  1000 × 5 = 5000
دوره 2: هزینه = 2000, وزن = 3  →  2000 × 3 = 6000
دوره 3: هزینه = 1500, وزن = 2  →  1500 × 2 = 3000

جمع = (5000 + 6000 + 3000) / (1000 + 2000 + 1500)
    = 14000 / 4500
    = 3.11 ماه
```

### نکته 3: محاسبات زنجیره‌ای
```
TotalProfitPercentage (درصد سود کل هزینه)
    ↓
AnnualProfitPercentage (تقسیم بر دوره و ضرب در 12)
    ↓
MonthlyProfitPercentage (تقسیم بر 12)
    ↓
DailyProfitPercentage (تقسیم بر 30)
```

### نکته 4: VLOOKUP vs Direct Reference
```excel
# ❌ مشکل - ردیف‌ها مطابقت ندارند
=Transactions!I5

# ✅ درست - استفاده از VLOOKUP
=VLOOKUP(A5, Transactions!$A:$I, 9, FALSE)
```

---

## 🎓 آموزش گام به گام

### سناریو 1: اضافه کردن محاسبه جدید

**هدف**: محاسبه میانگین سود هر سرمایه‌گذار

**گام 1**: تعریف Named Range
```python
# در ComprehensiveMetricsSheet
ws['A35'] = 'میانگین سود سرمایه‌گذار'
ws['B35'] = '=TotalProfit / TotalInvestors'
ws['B35'].number_format = '#,##0.00'
NamedRangeHelper.create_named_range(
    workbook, 'AverageProfitPerInvestor', 
    'Comprehensive_Metrics', '$B$35'
)
```

**گام 2**: استفاده در شیت دیگر
```python
# در InvestorAnalysisSheet
ws['F5'] = '=AverageProfitPerInvestor'
```

**گام 3**: اضافه به راهنما
```python
# در FormulaGuideSheet
named_ranges_calc.append((
    'AverageProfitPerInvestor', 
    'Comprehensive_Metrics!$B$35',
    'میانگین سود هر سرمایه‌گذار',
    '=AverageProfitPerInvestor'
))
```

---

### سناریو 2: اضافه کردن شیت تحلیلی جدید

**هدف**: شیت تحلیل واحدها

```python
class UnitAnalysisSheet:
    @staticmethod
    def create(workbook, project):
        ws = workbook.create_sheet("Unit_Analysis")
        
        # هدرها
        headers = ['نام واحد', 'متراژ', 'قیمت', 'درصد از کل']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # داده‌ها
        units = models.Unit.objects.filter(project=project)
        row = 2
        for unit in units:
            ws.cell(row=row, column=1, value=unit.name)
            ws.cell(row=row, column=2, value=f'=VLOOKUP(A{row}, Units!$D:$E, 2, FALSE)')
            ws.cell(row=row, column=3, value=f'=VLOOKUP(A{row}, Units!$D:$G, 4, FALSE)')
            ws.cell(row=row, column=4, value=f'=C{row}/TotalValue*100')
            ws.cell(row=row, column=4).number_format = '0.00'
            row += 1
        
        return ws
```

---

## 🔍 دیباگ و عیب‌یابی

### روش 1: بررسی Named Ranges
```python
import openpyxl

wb = openpyxl.load_workbook('file.xlsx')
for name in wb.defined_names:
    print(f'{name}: {wb.defined_names[name].attr_text}')
```

### روش 2: بررسی فرمول‌ها
```python
ws = wb['Comprehensive_Metrics']
for row in range(1, 50):
    cell = ws[f'B{row}']
    if cell.value and str(cell.value).startswith('='):
        print(f'B{row}: {cell.value}')
```

### روش 3: تست محاسبات
```python
# در Excel
1. Tools → Formula Auditing → Evaluate Formula
2. F9 برای محاسبه مجدد
3. Ctrl + ` برای نمایش فرمول‌ها
```

---

## 📚 منابع و مراجع

### کتابخانه‌های استفاده شده
```python
openpyxl>=3.1.0          # کار با Excel
django>=4.2              # فریمورک اصلی
```

### فرمول‌های Excel
- `SUMIF`: جمع با شرط
- `VLOOKUP`: جستجو عمودی
- `SUMPRODUCT`: حاصل‌ضرب و جمع
- `IF`: شرط
- `COUNTA`: شمارش غیر خالی

### الگوهای طراحی
- **Service Pattern**: `ExcelDynamicExportService`
- **Helper Pattern**: `NamedRangeHelper`, `ExcelStyleHelper`
- **Static Factory**: `Sheet.create()`

---

## ✅ چک‌لیست توسعه

قبل از اضافه کردن ویژگی جدید:

- [ ] آیا Named Range لازم است؟
- [ ] آیا شیت کمکی نیاز است؟
- [ ] آیا ترتیب ایجاد شیت‌ها درست است؟
- [ ] آیا فرمول‌ها تست شده‌اند؟
- [ ] آیا راهنما به‌روز شده؟
- [ ] آیا مستندات نوشته شده؟
- [ ] آیا عملکرد بررسی شده؟
- [ ] آیا با Excel و LibreOffice تست شده؟

---

**تاریخ آخرین به‌روزرسانی**: دی ماه 1403  
**نسخه مستند**: 1.0.0  
**وضعیت**: فعال و در حال توسعه

---

**نکته پایانی**: این مستند یک سند زنده است و باید با هر تغییر در کد، به‌روز شود. 📝

