# 📊 مستندات فایل Excel Static - پروژه ساختمانی

## 📑 فهرست مطالب
1. [معرفی و هدف](#معرفی-و-هدف)
2. [ساختار کلی](#ساختار-کلی)
3. [شیت‌های موجود](#شیتهای-موجود)
4. [محاسبات سرور](#محاسبات-سرور)
5. [استایل و فرمت‌بندی](#استایل-و-فرمتبندی)
6. [نحوه استفاده](#نحوه-استفاده)
7. [توسعه و نگهداری](#توسعه-و-نگهداری)
8. [مشکلات رایج و راه‌حل](#مشکلات-رایج-و-راهحل)

---

## 🎯 معرفی و هدف

### هدف اصلی
تولید یک فایل Excel کامل که:
- ✅ همه محاسبات در سرور (Python) انجام شود
- ✅ نتایج نهایی در Excel ذخیره شود
- ✅ استایل و فرمت‌بندی حرفه‌ای داشته باشد
- ✅ رنگ‌بندی استاندارد پروژه را رعایت کند
- ✅ قابلیت چاپ و ارائه داشته باشد

### تفاوت با Excel Dynamic
| ویژگی | Static | Dynamic |
|--------|--------|---------|
| محاسبات | در سرور (Python) ✅ | در Excel (فرمول) |
| قابلیت ویرایش | خیر | بله |
| شفافیت | متوسط | بالا |
| به‌روزرسانی | نیاز به تولید مجدد | خودکار |
| حجم فایل | کمتر ✅ | بیشتر |
| سرعت تولید | سریع‌تر ✅ | کندتر |
| استفاده | گزارش‌گیری، چاپ ✅ | تحلیل، ویرایش |

### کاربردها
- 📄 گزارش‌های رسمی
- 🖨️ چاپ و ارائه
- 📧 ارسال ایمیل
- 💾 آرشیو و نگهداری
- 📊 اسناپ‌شات از وضعیت پروژه

---

## 🏗️ ساختار کلی

### فایل اصلی
```
construction/excel_export.py
```

### کلاس‌های اصلی
```python
ExcelExportService              # سرویس اصلی تولید Excel
ExcelStyleHelper                # کمک‌کننده برای استایل‌ها
ProjectColors                   # رنگ‌های استاندارد پروژه

# کلاس‌های شیت‌های پایه
ProjectSheet                    # شیت پروژه
UnitsSheet                      # شیت واحدها
InvestorSheet                   # شیت سرمایه‌گذاران
PeriodSheet                     # شیت دوره‌ها
InterestRateSheet               # شیت نرخ سود
TransactionSheet                # شیت تراکنش‌ها
ExpenseSheet                    # شیت هزینه‌ها
SaleSheet                       # شیت فروش
UserProfileSheet                # شیت کاربران

# کلاس‌های شیت‌های محاسباتی
TableOfContentsSheet            # فهرست
DashboardSheet                  # داشبورد
ProfitMetricsSheet              # محاسبات سود
CostMetricsSheet                # محاسبات هزینه
InvestorAnalysisSheet           # تحلیل سرمایه‌گذاران
PeriodSummarySheet              # خلاصه دوره‌ای
TransactionSummarySheet         # خلاصه تراکنش‌ها
```

### API Endpoint
```
GET /construction/api/v1/Project/export_excel_static/
```

### Django Management Command
```bash
python manage.py export_excel
# یا
python manage.py export_excel --output myfile.xlsx
```

---

## 📋 شیت‌های موجود

### 1️⃣ شیت فهرست

#### `📋 فهرست`
- **هدف**: فهرست تمام شیت‌ها با لینک مستقیم
- **محتوا**: 
  - نام شیت
  - توضیح مختصر
  - لینک هایپرلینک به شیت
- **ویژگی**: 
  - استایل حرفه‌ای
  - رنگ‌بندی دسته‌بندی شده
  - قابلیت کلیک

**کد نمونه**:
```python
class TableOfContentsSheet:
    @staticmethod
    def create(workbook, project):
        ws = workbook.create_sheet("📋 فهرست", 0)
        
        # عنوان
        ws['A1'] = f'فهرست - {project.name}'
        ws['A1'].font = Font(size=16, bold=True)
        
        # لیست شیت‌ها
        sheets = [
            ('Project', 'اطلاعات پروژه', 'info'),
            ('Units', 'واحدهای ساختمانی', 'data'),
            # ...
        ]
        
        row = 3
        for sheet_name, description, category in sheets:
            # ایجاد هایپرلینک
            ws.cell(row=row, column=1).hyperlink = f"#{sheet_name}!A1"
            ws.cell(row=row, column=1).value = sheet_name
            ws.cell(row=row, column=2).value = description
            row += 1
```

---

### 2️⃣ شیت‌های داده پایه

#### `Project`
**محتوا**: اطلاعات کلی پروژه

**ستون‌ها**:
- ID
- نام پروژه
- تاریخ شروع (شمسی/میلادی)
- تاریخ پایان (شمسی/میلادی)
- فعال
- زیربنای کل
- ضریب اصلاحی
- تاریخ ایجاد/به‌روزرسانی

**ویژگی‌ها**:
- Freeze header row
- Auto-filter
- Column width adjustment

**کد نمونه**:
```python
class ProjectSheet:
    @staticmethod
    def create(workbook, project):
        ws = workbook.create_sheet(title="Project")
        
        # هدرها
        headers = [
            'ID', 'نام پروژه', 'تاریخ شروع (شمسی)', 
            'تاریخ شروع (میلادی)', 'تاریخ پایان (شمسی)', 
            'تاریخ پایان (میلادی)', 'فعال', 
            'زیربنای کل', 'ضریب اصلاحی', 
            'تاریخ ایجاد', 'تاریخ به‌روزرسانی'
        ]
        
        # نوشتن هدرها
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # نوشتن داده
        data = [
            project.id,
            project.name,
            project.start_date_shamsi,
            project.start_date,
            project.end_date_shamsi,
            project.end_date,
            'بله' if project.is_active else 'خیر',
            float(project.total_infrastructure) if project.total_infrastructure else 0,
            float(project.correction_factor) if project.correction_factor else 0,
            project.created_at,
            project.updated_at
        ]
        
        for col_num, value in enumerate(data, 1):
            cell = ws.cell(row=2, column=col_num, value=value)
            ExcelStyleHelper.apply_cell_style(cell)
        
        # تنظیمات
        ExcelStyleHelper.freeze_header_row(ws)
        ExcelStyleHelper.add_auto_filter(ws)
        ExcelStyleHelper.auto_adjust_column_width(ws)
```

---

#### `Units`
**محتوا**: واحدهای ساختمانی

**ستون‌ها**:
- ID
- شناسه پروژه
- نام پروژه
- نام واحد
- متراژ
- قیمت هر متر
- قیمت نهایی
- تاریخ ایجاد

**محاسبات**:
```python
# قیمت نهایی = متراژ × قیمت هر متر
final_price = unit.area * unit.price_per_meter
```

---

#### `Investors`
**محتوا**: سرمایه‌گذاران

**ستون‌ها**:
- ID
- نام
- نام خانوادگی
- شماره تماس
- ایمیل
- نوع مشارکت
- واحدها (لیست)
- تاریخ قرارداد (شمسی)
- تاریخ ایجاد

**ویژگی خاص**:
```python
# واحدها به صورت لیست نمایش داده می‌شود
units_list = ', '.join([unit.name for unit in investor.units.all()])
```

---

#### `Periods`
**محتوا**: دوره‌های زمانی

**ستون‌ها**:
- ID
- شناسه پروژه
- عنوان دوره
- سال شمسی
- شماره ماه
- نام ماه
- **وزن دوره** ⭐
- تاریخ شروع (شمسی/میلادی)
- تاریخ پایان (شمسی/میلادی)

**نکته مهم**: وزن دوره برای محاسبه دوره متوسط ساخت استفاده می‌شود

---

#### `InterestRates`
**محتوا**: نرخ‌های سود

**ستون‌ها**:
- ID
- نرخ سود روزانه
- تاریخ اعمال (شمسی/میلادی)
- توضیحات
- فعال
- تاریخ ایجاد

---

#### `Transactions`
**محتوا**: تراکنش‌های مالی

**ستون‌ها**:
- ID
- شناسه پروژه
- شناسه سرمایه‌گذار
- نام سرمایه‌گذار
- شناسه دوره
- عنوان دوره
- تاریخ (شمسی/میلادی)
- **مبلغ** ⭐
- **نوع تراکنش** ⭐ (آورده، خروج از سرمایه، سود)
- توضیحات
- روز مانده
- روز از شروع
- شناسه نرخ سود
- تولید سیستمی
- شناسه تراکنش اصلی
- تاریخ ایجاد

**انواع تراکنش**:
```python
TRANSACTION_TYPES = [
    ('principal_deposit', 'آورده'),
    ('principal_withdrawal', 'خروج از سرمایه'),
    ('profit', 'سود'),
]
```

---

#### `Expenses`
**محتوا**: هزینه‌ها

**ستون‌ها**:
- ID
- شناسه پروژه
- شناسه دوره
- عنوان دوره
- نوع هزینه
- **مبلغ** ⭐
- توضیحات
- تاریخ ایجاد

**نکته**: نوع هزینه شامل دسته‌بندی‌های مختلف (مدیر پروژه، سرپرست، کارپرداز، انباردار، پیمانکار)

---

#### `Sales`
**محتوا**: فروش/مرجوعی

**ستون‌ها**:
- ID
- شناسه پروژه
- شناسه دوره
- عنوان دوره
- **مبلغ** ⭐
- توضیحات
- تاریخ ایجاد

**نکته**: مبالغ فروش برای کاهش هزینه خالص استفاده می‌شوند

---

#### `UserProfiles`
**محتوا**: کاربران سیستم

**ستون‌ها**:
- ID
- شناسه کاربر
- نام کاربری
- نقش
- شماره تلفن
- بخش
- تاریخ ایجاد

---

### 3️⃣ شیت داشبورد

#### `Dashboard` ⭐⭐⭐
**مهم‌ترین شیت - نمای کلی پروژه**

**بخش 1: اطلاعات واحدها**
```python
# محاسبات
units_data = ProjectCalculations.calculate_project_statistics(project)

تعداد واحدها = units_data['units']['count']
متراژ کل = units_data['units']['total_area']
ارزش کل = units_data['units']['total_value']
```

**بخش 2: اطلاعات مالی**
```python
# محاسبات
financial_data = ProjectCalculations.calculate_project_statistics(project)

آورده کل = financial_data['financial']['total_deposits']
برداشت کل = financial_data['financial']['total_withdrawals']
سرمایه موجود = financial_data['financial']['net_principal']
سود کل = financial_data['financial']['total_profit']
موجودی کل = financial_data['financial']['grand_total']
```

**بخش 3: محاسبات زمانی**
```python
# محاسبات
time_data = ProjectCalculations.calculate_project_statistics(project)

تاریخ شروع = project.start_date
تاریخ پایان = project.end_date
مدت پروژه (روز) = time_data['time']['project_duration']
روزهای فعال = time_data['time']['active_days']
```

**استایل**:
- کارت‌های رنگی با گرادیانت
- آیکون‌های Font Awesome
- Shadow و Border Radius
- رنگ‌بندی استاندارد پروژه

---

### 4️⃣ شیت‌های محاسباتی

#### `Profit_Metrics`
**محتوا**: محاسبات سود

**محاسبات**:
```python
profit_data = ProfitCalculations.calculate_profit_percentages(project)

# محاسبات اصلی
سرمایه کل = profit_data['total_capital']
سود کل = profit_data['total_profit']
درصد سود کل = profit_data['total_profit_percentage']

# محاسبات زمانی
دوره متوسط ساخت = profit_data['average_construction_period']
درصد سود سالانه = profit_data['annual_profit_percentage']
درصد سود ماهانه = profit_data['monthly_profit_percentage']
درصد سود روزانه = profit_data['daily_profit_percentage']
```

**فرمول‌ها**:
```python
# درصد سود کل
total_profit_percentage = (total_profit / total_capital) * 100

# دوره متوسط ساخت (ماه)
average_period = Σ(هزینه_دوره × وزن_دوره) / Σ(کل_هزینه‌ها)

# درصد سود سالانه
annual_percentage = (total_profit_percentage / average_period) * 12

# درصد سود ماهانه
monthly_percentage = annual_percentage / 12

# درصد سود روزانه
daily_percentage = monthly_percentage / 30
```

---

#### `Cost_Metrics`
**محتوا**: محاسبات هزینه

**محاسبات**:
```python
cost_data = ProjectCalculations.calculate_cost_metrics(project)

# هزینه‌ها
هزینه کل = cost_data['total_expenses']
فروش کل = cost_data['total_sales']
هزینه خالص = cost_data['net_cost']

# هزینه متری
هزینه هر متر خالص = cost_data['net_cost_per_meter']
هزینه هر متر ناخالص = cost_data['gross_cost_per_meter']

# ارزش و سود
ارزش کل = cost_data['total_value']
ارزش هر متر = cost_data['value_per_meter']
سود نهایی = cost_data['final_profit']
درصد سود کل = cost_data['total_profit_percentage']
```

**فرمول‌ها**:
```python
# هزینه خالص
net_cost = total_expenses - total_sales

# هزینه هر متر خالص
net_cost_per_meter = net_cost / total_area

# هزینه هر متر ناخالص
gross_cost_per_meter = net_cost / total_infrastructure

# سود نهایی
final_profit = total_value - net_cost

# درصد سود کل
total_profit_percentage = (final_profit / net_cost) * 100
```

---

#### `Investor_Analysis`
**محتوا**: تحلیل هر سرمایه‌گذار

**ستون‌ها**:
- نام سرمایه‌گذار
- آورده کل
- برداشت کل
- سرمایه خالص
- سود کل
- موجودی کل
- نسبت سرمایه (%)
- نسبت سود (%)
- نسبت موجودی کل (%)
- **شاخص نفع** ⭐

**محاسبات**:
```python
for investor in investors:
    # تراکنش‌ها
    deposits = Transaction.objects.filter(
        investor=investor,
        transaction_type='principal_deposit'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    withdrawals = Transaction.objects.filter(
        investor=investor,
        transaction_type='principal_withdrawal'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    profits = Transaction.objects.filter(
        investor=investor,
        transaction_type='profit'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # محاسبات
    net_principal = deposits + withdrawals  # withdrawals منفی است
    total_balance = net_principal + profits
    
    # نسبت‌ها
    capital_ratio = (net_principal / total_capital) * 100
    profit_ratio = (profits / total_profit) * 100
    balance_ratio = (total_balance / grand_total) * 100
    
    # شاخص نفع
    profit_index = profit_ratio / capital_ratio if capital_ratio > 0 else 0
```

**شاخص نفع**:
```
شاخص نفع = نسبت سود / نسبت سرمایه

مثال:
- سرمایه‌گذار A: سرمایه 30%، سود 40% → شاخص = 1.33 (عملکرد بالاتر)
- سرمایه‌گذار B: سرمایه 20%، سود 15% → شاخص = 0.75 (عملکرد پایین‌تر)
```

**رنگ‌بندی**:
- شاخص > 1: سبز (عملکرد بالاتر از متوسط)
- شاخص = 1: زرد (عملکرد متوسط)
- شاخص < 1: قرمز (عملکرد پایین‌تر از متوسط)

---

#### `Period_Summary`
**محتوا**: خلاصه هر دوره

**ستون‌ها**:
- عنوان دوره
- آورده
- برداشت
- سرمایه خالص
- سود
- هزینه‌ها
- فروش
- مانده صندوق
- آورده تجمعی
- برداشت تجمعی
- سرمایه تجمعی
- سود تجمعی
- هزینه تجمعی
- فروش تجمعی

**محاسبات**:
```python
cumulative_deposits = 0
cumulative_withdrawals = 0
cumulative_expenses = 0
cumulative_sales = 0

for period in periods:
    # تراکنش‌های دوره
    period_deposits = Transaction.objects.filter(
        period=period,
        transaction_type='principal_deposit'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # هزینه‌های دوره
    period_expenses = Expense.objects.filter(
        period=period
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # فروش دوره
    period_sales = Sale.objects.filter(
        period=period
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # مانده صندوق
    fund_balance = cumulative_capital - (cumulative_expenses - cumulative_sales)
    
    # تجمعی
    cumulative_deposits += period_deposits
    cumulative_expenses += period_expenses
    cumulative_sales += period_sales
```

---

#### `Transaction_Summary`
**محتوا**: خلاصه تراکنش‌ها

**بخش 1: آمار کلی**
- تعداد کل تراکنش‌ها
- تعداد آورده
- تعداد برداشت
- تعداد سود

**بخش 2: مبالغ**
- مجموع آورده
- مجموع برداشت
- مجموع سود
- سرمایه خالص

**بخش 3: تحلیل**
- میانگین مبلغ تراکنش
- بیشترین تراکنش
- کمترین تراکنش

---

## 🎨 استایل و فرمت‌بندی

### رنگ‌های استاندارد پروژه

```python
class ProjectColors:
    """رنگ‌های استاندارد پروژه"""
    # رنگ‌های اصلی
    DEPOSIT = '2185d0'           # آبی - آورده و واریزی
    WITHDRAWAL = 'db2828'        # قرمز - برداشت و خروجی
    PROFIT = '21ba45'            # سبز - سود مشارکت و درآمد
    CAPITAL = 'aa26ff'           # بنفش - سرمایه موجود و موجودی
    EXPENSE = 'dc3545'           # قرمز تیره - هزینه‌ها و خرجی
    SALE = 'ffc107'              # زرد - فروش/مرجوعی
    BALANCE = '6c757d'           # خاکستری - مانده صندوق و مجموع
    GOLD = 'ffd700'              # طلایی - شاخص نفع و عملکرد برتر
    
    # رنگ‌های کمکی
    HEADER_BG = '4472C4'         # آبی تیره - هدر اصلی
    SUBHEADER_BG = 'B4C7E7'      # آبی روشن - هدر فرعی
    SECTION_BG = 'E7E6E6'        # خاکستری روشن - بخش‌ها
    WHITE = 'FFFFFF'             # سفید
```

### کاربرد رنگ‌ها

```python
# کارت آورده
fill = PatternFill(
    start_color=ProjectColors.DEPOSIT,
    end_color=ProjectColors.DEPOSIT,
    fill_type='solid'
)

# کارت سود
fill = PatternFill(
    start_color=ProjectColors.PROFIT,
    end_color=ProjectColors.PROFIT,
    fill_type='solid'
)

# کارت شاخص نفع
fill = PatternFill(
    start_color=ProjectColors.GOLD,
    end_color=ProjectColors.GOLD,
    fill_type='solid'
)
```

---

### استایل‌های پیش‌فرض

#### هدر جدول
```python
def get_header_font():
    return Font(
        name='Tahoma',
        size=11,
        bold=True,
        color='FFFFFF'
    )

def get_header_fill():
    return PatternFill(
        start_color=ProjectColors.HEADER_BG,
        end_color=ProjectColors.HEADER_BG,
        fill_type='solid'
    )

def get_header_alignment():
    return Alignment(
        horizontal='center',
        vertical='center',
        wrap_text=True
    )
```

#### سلول عادی
```python
def apply_cell_style(cell):
    cell.font = Font(name='Tahoma', size=10)
    cell.alignment = Alignment(
        horizontal='right',
        vertical='center'
    )
    cell.border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
```

---

### فرمت‌های عددی

```python
# مبالغ مالی
cell.number_format = '#,##0.00'

# درصد
cell.number_format = '0.00%'

# تعداد
cell.number_format = '#,##0'

# تاریخ
cell.number_format = 'yyyy-mm-dd'
```

---

### ویژگی‌های اضافی

#### Freeze Header Row
```python
def freeze_header_row(ws):
    """فریز کردن ردیف هدر"""
    ws.freeze_panes = 'A2'
```

#### Auto Filter
```python
def add_auto_filter(ws):
    """اضافه کردن فیلتر خودکار"""
    ws.auto_filter.ref = ws.dimensions
```

#### Auto Adjust Column Width
```python
def auto_adjust_column_width(ws):
    """تنظیم خودکار عرض ستون‌ها"""
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
```

---

## 🧮 محاسبات سرور

### سرویس محاسبات

```python
# construction/calculations.py

class ProjectCalculations:
    """محاسبات کلی پروژه"""
    
    @staticmethod
    def calculate_project_statistics(project):
        """محاسبه آمار کلی پروژه"""
        # محاسبات واحدها
        units = Unit.objects.filter(project=project)
        units_data = {
            'count': units.count(),
            'total_area': units.aggregate(Sum('area'))['area__sum'] or 0,
            'total_value': units.aggregate(
                total=Sum(F('area') * F('price_per_meter'))
            )['total'] or 0
        }
        
        # محاسبات مالی
        transactions = Transaction.objects.filter(project=project)
        deposits = transactions.filter(
            transaction_type='principal_deposit'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        withdrawals = transactions.filter(
            transaction_type='principal_withdrawal'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        profits = transactions.filter(
            transaction_type='profit'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        financial_data = {
            'total_deposits': deposits,
            'total_withdrawals': withdrawals,
            'net_principal': deposits + withdrawals,
            'total_profit': profits,
            'grand_total': deposits + withdrawals + profits
        }
        
        # محاسبات زمانی
        time_data = {
            'start_date': project.start_date,
            'end_date': project.end_date,
            'project_duration': (project.end_date - project.start_date).days,
            'active_days': (timezone.now().date() - project.start_date).days
        }
        
        return {
            'units': units_data,
            'financial': financial_data,
            'time': time_data
        }
    
    @staticmethod
    def calculate_cost_metrics(project):
        """محاسبه معیارهای هزینه"""
        # هزینه‌ها
        expenses = Expense.objects.filter(project=project)
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # فروش
        sales = Sale.objects.filter(project=project)
        total_sales = sales.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # هزینه خالص
        net_cost = total_expenses - total_sales
        
        # متراژ
        units = Unit.objects.filter(project=project)
        total_area = units.aggregate(Sum('area'))['area__sum'] or 0
        
        # هزینه متری
        net_cost_per_meter = net_cost / total_area if total_area > 0 else 0
        gross_cost_per_meter = net_cost / project.total_infrastructure if project.total_infrastructure > 0 else 0
        
        # ارزش
        total_value = units.aggregate(
            total=Sum(F('area') * F('price_per_meter'))
        )['total'] or 0
        value_per_meter = total_value / total_area if total_area > 0 else 0
        
        # سود
        final_profit = total_value - net_cost
        total_profit_percentage = (final_profit / net_cost * 100) if net_cost > 0 else 0
        
        return {
            'total_expenses': total_expenses,
            'total_sales': total_sales,
            'net_cost': net_cost,
            'net_cost_per_meter': net_cost_per_meter,
            'gross_cost_per_meter': gross_cost_per_meter,
            'total_value': total_value,
            'value_per_meter': value_per_meter,
            'final_profit': final_profit,
            'total_profit_percentage': total_profit_percentage
        }


class ProfitCalculations:
    """محاسبات سود"""
    
    @staticmethod
    def calculate_profit_percentages(project):
        """محاسبه درصدهای سود"""
        # سرمایه و سود
        transactions = Transaction.objects.filter(project=project)
        
        deposits = transactions.filter(
            transaction_type='principal_deposit'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        withdrawals = transactions.filter(
            transaction_type='principal_withdrawal'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_capital = deposits + withdrawals
        
        total_profit = transactions.filter(
            transaction_type='profit'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # درصد سود کل
        total_profit_percentage = (total_profit / total_capital * 100) if total_capital > 0 else 0
        
        # دوره متوسط ساخت
        average_period = ProfitCalculations.calculate_average_construction_period(project)
        
        # درصدهای زمانی
        annual_profit_percentage = (total_profit_percentage / average_period * 12) if average_period > 0 else 0
        monthly_profit_percentage = annual_profit_percentage / 12
        daily_profit_percentage = monthly_profit_percentage / 30
        
        return {
            'total_capital': total_capital,
            'total_profit': total_profit,
            'total_profit_percentage': total_profit_percentage,
            'average_construction_period': average_period,
            'annual_profit_percentage': annual_profit_percentage,
            'monthly_profit_percentage': monthly_profit_percentage,
            'daily_profit_percentage': daily_profit_percentage
        }
    
    @staticmethod
    def calculate_average_construction_period(project):
        """محاسبه دوره متوسط ساخت (ماه)"""
        periods = Period.objects.filter(project=project)
        
        total_weighted = 0
        total_expenses = 0
        
        for period in periods:
            # هزینه دوره
            period_expenses = Expense.objects.filter(
                period=period
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            # وزن دوره
            weight = period.period_weight if hasattr(period, 'period_weight') else 1
            
            total_weighted += period_expenses * weight
            total_expenses += period_expenses
        
        return total_weighted / total_expenses if total_expenses > 0 else 0
```

---

## 📘 نحوه استفاده

### برای کاربران

#### 1. تولید فایل از API
```bash
curl -X GET "http://localhost:8000/construction/api/v1/Project/export_excel_static/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output report.xlsx
```

#### 2. تولید فایل از Management Command
```bash
# تولید با نام پیش‌فرض
python manage.py export_excel

# تولید با نام دلخواه
python manage.py export_excel --output my_report.xlsx

# تولید برای پروژه خاص
python manage.py export_excel --project-id 1

# باز کردن خودکار
python manage.py export_excel --open
```

#### 3. مشاهده فایل
- فایل با Excel 2016+ باز شود
- از LibreOffice Calc هم پشتیبانی می‌شود
- شیت `📋 فهرست` را ابتدا ببینید

---

### برای توسعه‌دهندگان

#### ساختار کد

```python
class ExcelExportService:
    def __init__(self, project):
        self.project = project
        self.workbook = Workbook()
    
    def generate_excel(self):
        """تولید فایل Excel"""
        # 1. حذف شیت پیش‌فرض
        if 'Sheet' in self.workbook.sheetnames:
            self.workbook.remove(self.workbook['Sheet'])
        
        # 2. ایجاد فهرست
        TableOfContentsSheet.create(self.workbook, self.project)
        
        # 3. ایجاد شیت‌های پایه
        ProjectSheet.create(self.workbook, self.project)
        UnitsSheet.create(self.workbook, self.project)
        InvestorSheet.create(self.workbook, self.project)
        # ...
        
        # 4. ایجاد شیت‌های محاسباتی
        DashboardSheet.create(self.workbook, self.project)
        ProfitMetricsSheet.create(self.workbook, self.project)
        CostMetricsSheet.create(self.workbook, self.project)
        # ...
        
        return self.workbook
```

#### افزودن شیت جدید

```python
class NewSheet:
    @staticmethod
    def create(workbook, project):
        ws = workbook.create_sheet("New_Sheet")
        
        # هدرها
        headers = ['ستون 1', 'ستون 2', 'ستون 3']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # داده‌ها
        data = get_data_from_database(project)
        row = 2
        for item in data:
            ws.cell(row=row, column=1, value=item.field1)
            ws.cell(row=row, column=2, value=item.field2)
            ws.cell(row=row, column=3, value=calculate_field3(item))
            
            # استایل
            for col in range(1, 4):
                ExcelStyleHelper.apply_cell_style(ws.cell(row=row, column=col))
            
            row += 1
        
        # تنظیمات
        ExcelStyleHelper.freeze_header_row(ws)
        ExcelStyleHelper.add_auto_filter(ws)
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws
```

---

## 🔧 توسعه و نگهداری

### نکات مهم برای توسعه

#### 1. استفاده از select_related و prefetch_related
```python
# ❌ کند - N+1 Query
transactions = Transaction.objects.filter(project=project)
for trans in transactions:
    investor_name = trans.investor.first_name  # Query جداگانه

# ✅ سریع - یک Query
transactions = Transaction.objects.filter(
    project=project
).select_related('investor', 'period', 'interest_rate')
```

#### 2. استفاده از aggregate برای محاسبات
```python
# ❌ کند - محاسبه در Python
total = 0
for trans in transactions:
    total += trans.amount

# ✅ سریع - محاسبه در دیتابیس
total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
```

#### 3. نرمال‌سازی datetime
```python
def normalize_datetime(dt):
    """حذف timezone برای Excel"""
    if dt and hasattr(dt, 'tzinfo') and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt
```

#### 4. فرمت‌بندی اعداد
```python
# تبدیل Decimal به float
value = float(decimal_value) if decimal_value else 0

# فرمت با جداکننده هزارگان
cell.number_format = '#,##0.00'
```

---

### الگوهای رایج

#### الگو 1: ایجاد کارت آماری
```python
def create_stat_card(ws, row, col, title, value, color):
    """ایجاد کارت آماری"""
    # عنوان
    title_cell = ws.cell(row=row, column=col, value=title)
    title_cell.font = Font(name='Tahoma', size=10, bold=True)
    title_cell.fill = PatternFill(
        start_color=color,
        end_color=color,
        fill_type='solid'
    )
    
    # مقدار
    value_cell = ws.cell(row=row+1, column=col, value=value)
    value_cell.font = Font(name='Tahoma', size=14, bold=True)
    value_cell.number_format = '#,##0.00'
    
    # مرج سلول‌ها
    ws.merge_cells(
        start_row=row, start_column=col,
        end_row=row, end_column=col+1
    )
```

#### الگو 2: ایجاد جدول با استایل
```python
def create_styled_table(ws, headers, data, start_row=1):
    """ایجاد جدول با استایل"""
    # هدرها
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col, value=header)
        ExcelStyleHelper.apply_header_style(cell)
    
    # داده‌ها
    for row_idx, row_data in enumerate(data, start_row+1):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            ExcelStyleHelper.apply_cell_style(cell)
    
    # تنظیمات
    ExcelStyleHelper.freeze_header_row(ws)
    ExcelStyleHelper.add_auto_filter(ws)
    ExcelStyleHelper.auto_adjust_column_width(ws)
```

#### الگو 3: محاسبه و نمایش نسبت
```python
def calculate_and_display_ratio(ws, row, label, numerator, denominator):
    """محاسبه و نمایش نسبت"""
    ws.cell(row=row, column=1, value=label)
    
    ratio = (numerator / denominator * 100) if denominator > 0 else 0
    
    cell = ws.cell(row=row, column=2, value=ratio)
    cell.number_format = '0.00%'
    
    # رنگ‌بندی بر اساس مقدار
    if ratio > 100:
        cell.font = Font(color=ProjectColors.PROFIT)
    elif ratio < 100:
        cell.font = Font(color=ProjectColors.EXPENSE)
```

---

### بهینه‌سازی عملکرد

#### 1. Cache کردن محاسبات
```python
from django.core.cache import cache

def get_project_statistics(project):
    cache_key = f'project_stats_{project.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = ProjectCalculations.calculate_project_statistics(project)
        cache.set(cache_key, stats, 3600)  # 1 ساعت
    
    return stats
```

#### 2. استفاده از bulk operations
```python
# برای تعداد زیاد سلول‌ها
cells = []
for row in range(1, 1000):
    for col in range(1, 10):
        cell = ws.cell(row=row, column=col, value=f'R{row}C{col}')
        cells.append(cell)

# اعمال استایل به صورت bulk
for cell in cells:
    ExcelStyleHelper.apply_cell_style(cell)
```

#### 3. محدود کردن داده‌ها
```python
# فقط فیلدهای مورد نیاز
transactions = Transaction.objects.filter(
    project=project
).only('id', 'amount', 'transaction_type', 'date_gregorian')
```

---

## ⚠️ مشکلات رایج و راه‌حل

### مشکل 1: خطای Timezone
**علت**: Excel از timezone پشتیبانی نمی‌کند

**راه‌حل**:
```python
def normalize_datetime(dt):
    if dt and hasattr(dt, 'tzinfo') and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt

# استفاده
cell.value = normalize_datetime(transaction.created_at)
```

### مشکل 2: فونت فارسی
**علت**: فونت پیش‌فرض از فارسی پشتیبانی نمی‌کند

**راه‌حل**:
```python
# استفاده از Tahoma یا Vazir
font = Font(name='Tahoma', size=10)
```

### مشکل 3: عرض ستون‌ها
**علت**: عرض خیلی کوچک یا بزرگ

**راه‌حل**:
```python
def auto_adjust_column_width(ws):
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        
        # محدود کردن عرض
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
```

### مشکل 4: حجم فایل زیاد
**علت**: تعداد زیاد داده یا استایل

**راه‌حل**:
```python
# محدود کردن داده‌ها
transactions = Transaction.objects.filter(
    project=project,
    date_gregorian__gte=start_date
)[:1000]

# استفاده از استایل‌های مشترک
shared_font = Font(name='Tahoma', size=10)
for cell in cells:
    cell.font = shared_font
```

### مشکل 5: خطای Memory
**علت**: تعداد زیاد سلول‌ها

**راه‌حل**:
```python
# استفاده از write_only mode
from openpyxl import Workbook

wb = Workbook(write_only=True)
ws = wb.create_sheet('Data')

for row in data:
    ws.append(row)

wb.save('large_file.xlsx')
```

### مشکل 6: مرتب‌سازی تاریخ فارسی
**علت**: Excel تاریخ فارسی را نمی‌شناسد

**راه‌حل**:
```python
# استفاده از تاریخ میلادی برای مرتب‌سازی
# و نمایش تاریخ فارسی در ستون جداگانه
ws.cell(row=row, column=1, value=transaction.date_gregorian)  # برای sort
ws.cell(row=row, column=2, value=transaction.date_shamsi)     # برای نمایش
```

---

## 📊 آمار و اطلاعات فنی

### نسخه فعلی
- **تاریخ ایجاد**: شهریور ماه 1403
- **نسخه**: 1.0.0
- **تعداد شیت‌ها**: 15 شیت
- **حجم فایل**: ~80-100 KB
- **زمان تولید**: 2-5 ثانیه

### سازگاری
- ✅ Microsoft Excel 2010+
- ✅ Microsoft Excel 365
- ✅ LibreOffice Calc 5.0+
- ✅ Google Sheets
- ✅ WPS Office

### محدودیت‌ها
- حداکثر 10,000 تراکنش
- حداکثر 200 دوره
- حداکثر 500 سرمایه‌گذار
- حداکثر 1,000 واحد

---

## 🚀 توسعه‌های انجام شده

### فاز 1 (تکمیل شده) ✅
- [x] شیت‌های پایه
- [x] شیت داشبورد
- [x] محاسبات مالی
- [x] محاسبات سود
- [x] محاسبات هزینه
- [x] تحلیل سرمایه‌گذاران
- [x] خلاصه دوره‌ای
- [x] خلاصه تراکنش‌ها

### فاز 2 (تکمیل شده) ✅
- [x] رنگ‌بندی استاندارد
- [x] Freeze header rows
- [x] Auto-filter
- [x] فهرست با هایپرلینک
- [x] Auto-adjust column width
- [x] فرمت‌بندی اعداد

### بهبودهای آینده (پیشنهادی)
- [ ] نمودارها
- [ ] Conditional Formatting
- [ ] Data Validation
- [ ] محافظت از شیت‌ها
- [ ] قالب‌های از پیش تعریف شده
- [ ] صادرات به PDF

---

## 📞 پشتیبانی و مستندات

### فایل‌های مرتبط
```
construction/excel_export.py              # کد اصلی
construction/calculations.py              # محاسبات
construction/api.py                       # API Endpoints
docs/API_REFERENCE.md                     # مستندات API
STATIC_EXCEL_DOCUMENTATION.md             # این فایل
```

### لینک‌های مفید
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [Excel File Format](https://docs.microsoft.com/en-us/office/open-xml/working-with-spreadsheets)
- [Django ORM Optimization](https://docs.djangoproject.com/en/4.2/topics/db/optimization/)

---

## 📝 یادداشت‌های مهم

### نکته 1: دو نوع Excel
```
Static Excel:
- محاسبات در سرور
- نتایج ثابت
- مناسب گزارش‌گیری

Dynamic Excel:
- محاسبات در Excel
- فرمول‌های زنده
- مناسب تحلیل
```

### نکته 2: محاسبه دوره متوسط
```python
# دوره متوسط ساخت (ماه)
average_period = Σ(هزینه_دوره × وزن_دوره) / Σ(کل_هزینه‌ها)

# مثال:
# دوره 1: هزینه=1000, وزن=5 → 1000×5=5000
# دوره 2: هزینه=2000, وزن=3 → 2000×3=6000
# دوره 3: هزینه=1500, وزن=2 → 1500×2=3000
# 
# میانگین = (5000+6000+3000) / (1000+2000+1500)
#          = 14000 / 4500
#          = 3.11 ماه
```

### نکته 3: شاخص نفع
```
شاخص نفع = نسبت سود / نسبت سرمایه

تفسیر:
- شاخص > 1: عملکرد بالاتر از متوسط (سبز)
- شاخص = 1: عملکرد متوسط (زرد)
- شاخص < 1: عملکرد پایین‌تر از متوسط (قرمز)
```

### نکته 4: رنگ‌بندی استاندارد
```
آبی (#2185d0):    آورده و واریزی
قرمز (#db2828):   برداشت و خروجی
سبز (#21ba45):    سود و درآمد
بنفش (#aa26ff):   سرمایه موجود
قرمز تیره (#dc3545): هزینه‌ها
زرد (#ffc107):    فروش/مرجوعی
خاکستری (#6c757d): مانده صندوق
طلایی (#ffd700):  شاخص نفع
```

---

## 🎓 آموزش گام به گام

### سناریو 1: اضافه کردن ستون جدید

**هدف**: اضافه کردن ستون "وضعیت" به شیت Transactions

**گام 1**: تغییر هدرها
```python
headers = [
    'ID', 'شناسه پروژه', 'شناسه سرمایه‌گذار',
    'نام سرمایه‌گذار', 'شناسه دوره', 'عنوان دوره',
    'تاریخ (شمسی)', 'تاریخ (میلادی)', 'مبلغ',
    'نوع تراکنش', 'توضیحات', 'روز مانده',
    'روز از شروع', 'شناسه نرخ سود', 'تولید سیستمی',
    'شناسه تراکنش اصلی', 'وضعیت',  # جدید
    'تاریخ ایجاد'
]
```

**گام 2**: اضافه کردن داده
```python
data = [
    trans.id,
    trans.project.id,
    # ...
    'تایید شده' if trans.is_approved else 'در انتظار',  # جدید
    trans.created_at
]
```

**گام 3**: تست
```bash
python manage.py export_excel --output test.xlsx
```

---

### سناریو 2: اضافه کردن شیت تحلیلی جدید

**هدف**: شیت تحلیل واحدها بر اساس متراژ

```python
class UnitAnalysisSheet:
    @staticmethod
    def create(workbook, project):
        ws = workbook.create_sheet("Unit_Analysis")
        
        # هدرها
        headers = [
            'نام واحد', 'متراژ', 'قیمت هر متر',
            'قیمت نهایی', 'درصد از کل متراژ',
            'درصد از کل ارزش'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            ExcelStyleHelper.apply_header_style(cell)
        
        # محاسبات کلی
        units = models.Unit.objects.filter(project=project)
        total_area = units.aggregate(Sum('area'))['area__sum'] or 0
        total_value = units.aggregate(
            total=Sum(F('area') * F('price_per_meter'))
        )['total'] or 0
        
        # داده‌ها
        row = 2
        for unit in units:
            final_price = unit.area * unit.price_per_meter
            area_percentage = (unit.area / total_area * 100) if total_area > 0 else 0
            value_percentage = (final_price / total_value * 100) if total_value > 0 else 0
            
            data = [
                unit.name,
                float(unit.area),
                float(unit.price_per_meter),
                float(final_price),
                area_percentage,
                value_percentage
            ]
            
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col, value=value)
                ExcelStyleHelper.apply_cell_style(cell)
                
                # فرمت عددی
                if col in [2, 3, 4]:
                    cell.number_format = '#,##0.00'
                elif col in [5, 6]:
                    cell.number_format = '0.00%'
            
            row += 1
        
        # تنظیمات
        ExcelStyleHelper.freeze_header_row(ws)
        ExcelStyleHelper.add_auto_filter(ws)
        ExcelStyleHelper.auto_adjust_column_width(ws)
        
        return ws
```

**اضافه به سرویس**:
```python
def generate_excel(self):
    # ...
    UnitAnalysisSheet.create(self.workbook, self.project)
    # ...
```

---

## 🔍 دیباگ و عیب‌یابی

### روش 1: لاگ‌گذاری
```python
import logging

logger = logging.getLogger(__name__)

def create_sheet(workbook, project):
    logger.info(f'Creating sheet for project {project.id}')
    
    try:
        # کد شیت
        pass
    except Exception as e:
        logger.error(f'Error creating sheet: {str(e)}')
        raise
```

### روش 2: بررسی داده‌ها
```python
# قبل از نوشتن در Excel
print(f'Total transactions: {transactions.count()}')
print(f'Total deposits: {deposits}')
print(f'Total withdrawals: {withdrawals}')
```

### روش 3: تست واحد
```python
from django.test import TestCase

class ExcelExportTest(TestCase):
    def test_dashboard_sheet(self):
        project = Project.objects.create(name='Test')
        service = ExcelExportService(project)
        wb = service.generate_excel()
        
        self.assertIn('Dashboard', wb.sheetnames)
        ws = wb['Dashboard']
        self.assertIsNotNone(ws['A1'].value)
```

---

## ✅ چک‌لیست توسعه

قبل از اضافه کردن ویژگی جدید:

- [ ] آیا محاسبات در سرور انجام می‌شود؟
- [ ] آیا از select_related استفاده شده؟
- [ ] آیا استایل‌های استاندارد اعمال شده؟
- [ ] آیا رنگ‌بندی پروژه رعایت شده؟
- [ ] آیا Freeze و Auto-filter اضافه شده؟
- [ ] آیا عرض ستون‌ها تنظیم شده؟
- [ ] آیا فرمت اعداد صحیح است؟
- [ ] آیا تاریخ‌ها normalize شده‌اند؟
- [ ] آیا با Excel و LibreOffice تست شده؟
- [ ] آیا مستندات به‌روز شده؟

---

**تاریخ آخرین به‌روزرسانی**: دی ماه 1403  
**نسخه مستند**: 1.0.0  
**وضعیت**: فعال و پایدار

---

**نکته پایانی**: این مستند باید با هر تغییر در کد، به‌روز شود. 📝

