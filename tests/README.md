# تست‌های پروژه Construction

این پوشه شامل تمام تست‌های پروژه Construction است که شامل تست‌های Backend (Django) و Frontend (JavaScript) می‌باشد.

## 📁 ساختار فایل‌ها

```
tests/
├── README.md                           # این فایل
├── setup.js                           # تنظیمات Jest
├── construction/                       # تست‌های Django
│   ├── test_models.py                 # تست‌های مدل‌ها
│   ├── test_serializers.py            # تست‌های Serializer ها
│   ├── test_transaction_api.py        # تست‌های API Transaction
│   └── test_views.py                  # تست‌های View ها
└── frontend/                          # تست‌های JavaScript
    └── test_transaction_form.js       # تست‌های فرم تراکنش
```

## 🚀 اجرای تست‌ها

### نصب وابستگی‌ها

```bash
# نصب وابستگی‌های Python
pip install -r requirements-test.txt

# نصب وابستگی‌های JavaScript
npm install
```

### اجرای تمام تست‌ها

```bash
# اجرای تمام تست‌ها
make test

# یا به صورت جداگانه
make test-backend    # تست‌های Django
make test-frontend   # تست‌های JavaScript
```

### اجرای تست‌های خاص

```bash
# تست‌های مدل‌ها
make test-models

# تست‌های Serializer ها
make test-serializers

# تست‌های API
make test-api

# تست‌های فرم تراکنش
npm run test:transaction
```

### اجرای تست‌ها با Coverage

```bash
# تست‌های Python با Coverage
make test-coverage

# تست‌های JavaScript با Coverage
npm run test:coverage

# تمام تست‌ها با Coverage
make test-all
```

## 📊 انواع تست‌ها

### 1️⃣ تست‌های Backend (Django)

#### تست‌های مدل (test_models.py)
- ✅ ایجاد و ذخیره مدل‌ها
- ✅ اعتبارسنجی فیلدها
- ✅ روابط Foreign Key
- ✅ متدهای مدل (save, __str__)
- ✅ محاسبات خودکار (تاریخ، روزها)

#### تست‌های Serializer (test_serializers.py)
- ✅ اعتبارسنجی داده‌ها
- ✅ تبدیل اعداد فارسی
- ✅ تبدیل تاریخ شمسی به میلادی
- ✅ فیلدهای read-only
- ✅ فیلدهای write-only

#### تست‌های API (test_transaction_api.py)
- ✅ Endpoint های REST API
- ✅ ایجاد، خواندن، آپدیت، حذف (CRUD)
- ✅ اعتبارسنجی درخواست‌ها
- ✅ مدیریت خطاها
- ✅ آمار و گزارش‌ها

### 2️⃣ تست‌های Frontend (JavaScript)

#### تست‌های فرم تراکنش (test_transaction_form.js)
- ✅ فرمت‌بندی اعداد فارسی
- ✅ اعتبارسنجی فرم
- ✅ ارسال درخواست API
- ✅ مدیریت خطاها
- ✅ نمایش پیام‌ها

## 🎯 سناریوهای تست

### سناریو 1: ایجاد تراکنش جدید
```python
# تست کامل workflow ایجاد تراکنش
def test_full_transaction_workflow():
    # 1. ایجاد داده‌های اولیه
    # 2. ارسال درخواست API
    # 3. بررسی موفقیت
    # 4. بررسی داده‌های ذخیره شده
    # 5. تست دریافت تراکنش
    # 6. تست آپدیت
    # 7. تست حذف
```

### سناریو 2: تبدیل اعداد فارسی
```python
# تست تبدیل اعداد فارسی به انگلیسی
def test_persian_digits_conversion():
    data = {
        'amount': '۱۰۰۰۰',  # اعداد فارسی
        'date_shamsi': '۱۴۰۴-۰۶-۰۱'  # اعداد فارسی
    }
    # بررسی تبدیل صحیح
```

### سناریو 3: محاسبه تاریخ و روزها
```python
# تست محاسبه خودکار تاریخ میلادی و روزها
def test_date_and_day_calculations():
    # بررسی تبدیل تاریخ شمسی به میلادی
    # بررسی محاسبه روز مانده
    # بررسی محاسبه روز از شروع
```

## 🔧 تنظیمات تست

### Django Settings
```python
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
```

### Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  // ...
};
```

## 📈 Coverage Reports

### Python Coverage
```bash
# تولید گزارش Coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # گزارش HTML در htmlcov/
```

### JavaScript Coverage
```bash
# تولید گزارش Coverage
npm run test:coverage
# گزارش در coverage/frontend/
```

## 🐛 Debugging Tests

### Django Tests
```bash
# اجرای تست با debug
python manage.py test tests.construction.test_models --verbosity=2 --debug-mode

# اجرای تست خاص
python manage.py test tests.construction.test_models.TransactionModelTestCase.test_transaction_creation
```

### JavaScript Tests
```bash
# اجرای تست با watch mode
npm run test:watch

# اجرای تست خاص
npm test -- --testNamePattern="formatAmount"
```

## 📝 نوشتن تست‌های جدید

### Django Test
```python
class NewFeatureTestCase(TestCase):
    def setUp(self):
        # تنظیمات اولیه
        
    def test_new_feature(self):
        # تست جدید
        self.assertEqual(result, expected)
```

### JavaScript Test
```javascript
describe('New Feature', () => {
    test('should work correctly', () => {
        // تست جدید
        expect(result).toBe(expected);
    });
});
```

## 🚨 Best Practices

### 1️⃣ نام‌گذاری
- نام فایل‌ها: `test_*.py` یا `*.test.js`
- نام کلاس‌ها: `*TestCase`
- نام متدها: `test_*`

### 2️⃣ ساختار تست
- **Arrange**: آماده‌سازی داده‌ها
- **Act**: اجرای عملیات
- **Assert**: بررسی نتیجه

### 3️⃣ Mock و Stub
- استفاده از Mock برای API calls
- استفاده از Factory برای ایجاد داده‌های تست
- پاک کردن Mock ها بین تست‌ها

### 4️⃣ Coverage
- هدف: حداقل 80% coverage
- تست تمام مسیرهای کد
- تست edge cases

## 🔍 Troubleshooting

### مشکلات رایج

#### 1️⃣ خطای Database
```bash
# پاک کردن دیتابیس تست
rm db.sqlite3
python manage.py migrate
```

#### 2️⃣ خطای Import
```python
# بررسی مسیر import
from construction.models import Transaction
```

#### 3️⃣ خطای JavaScript
```javascript
// بررسی Mock ها
global.fetch = jest.fn();
```

## 📚 منابع بیشتر

- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://realpython.com/python-testing/)

## 🤝 مشارکت

برای اضافه کردن تست‌های جدید:

1. فایل تست مناسب را انتخاب کنید
2. تست جدید را بنویسید
3. تست را اجرا کنید
4. Pull Request ارسال کنید

---

**نکته**: همیشه قبل از commit کردن کد، تمام تست‌ها را اجرا کنید تا از صحت عملکرد اطمینان حاصل کنید.
