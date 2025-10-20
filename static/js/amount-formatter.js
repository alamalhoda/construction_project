/**
 * فرمت‌بندی مبلغ مشابه صفحه مدیریت تراکنش‌ها
 * جداکننده هزارگان فقط برای قسمت صحیح
 */

function formatAmount(input) {
    // ذخیره موقعیت کرسر
    const cursorPosition = input.selectionStart;
    const oldValue = input.value;
    
    // برای اعداد صحیح - حذف تمام کاراکترهای غیرعددی شامل اعداد فارسی
    let value = input.value.replace(/[^\d۰-۹]/g, '');
    
    // تبدیل اعداد فارسی به انگلیسی
    const persianToEnglish = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    };
    
    for (let persian in persianToEnglish) {
        value = value.replace(new RegExp(persian, 'g'), persianToEnglish[persian]);
    }
    
    // محدود کردن به 12 رقم
    if (value.length > 12) {
        value = value.substring(0, 12);
    }
    
    // فرمت‌بندی با کاما
    if (value) {
        const formatted = parseInt(value).toLocaleString('en-US');
        input.value = formatted;
    }
    
    // بازگرداندن موقعیت کرسر (فقط برای فیلدهای text)
    if (input.type === 'text') {
        setTimeout(() => {
            const newValue = input.value;
            const oldLength = oldValue.length;
            const newLength = newValue.length;
            
            // محاسبه موقعیت جدید کرسر
            let newCursorPosition = cursorPosition;
            
            // اگر طول تغییر کرده، موقعیت کرسر را تنظیم کن
            if (newLength > oldLength) {
                newCursorPosition = cursorPosition + (newLength - oldLength);
            } else if (newLength < oldLength) {
                newCursorPosition = Math.max(0, cursorPosition - (oldLength - newLength));
            }
            
            // محدود کردن موقعیت کرسر
            newCursorPosition = Math.min(newCursorPosition, newValue.length);
            
            try {
                input.setSelectionRange(newCursorPosition, newCursorPosition);
            } catch (e) {
                // اگر setSelectionRange پشتیبانی نمی‌شود، خطا را نادیده بگیر
                console.log('setSelectionRange پشتیبانی نمی‌شود برای این نوع فیلد');
            }
        }, 0);
    }
}

function formatNumber(input) {
    // ذخیره موقعیت کرسر
    const cursorPosition = input.selectionStart;
    const oldValue = input.value;
    
    console.log('=== formatNumber شروع ===');
    console.log('فیلد:', input.name || input.id || 'نامشخص');
    console.log('مقدار اولیه:', oldValue);
    
    // برای اعداد اعشاری - جداکننده فقط برای قسمت صحیح
    // حذف تمام کاراکترهای غیرعددی شامل اعداد فارسی و کاماها
    let value = input.value.replace(/[^\d۰-۹.]/g, '');
    console.log('بعد از حذف کاراکترهای غیرعددی:', value);
    
    // تبدیل اعداد فارسی به انگلیسی
    const persianToEnglish = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    };
    
    for (let persian in persianToEnglish) {
        value = value.replace(new RegExp(persian, 'g'), persianToEnglish[persian]);
    }
    console.log('بعد از تبدیل اعداد فارسی:', value);
    
    // اگر خالی است، مقدار خالی برگردان
    if (!value) {
        input.value = '';
        console.log('مقدار خالی - فیلد پاک شد');
        console.log('=== formatNumber پایان ===');
        return;
    }
    
    // اگر نقطه دارد، تقسیم کن
    const parts = value.split('.');
    console.log('قسمت‌ها:', parts);
    
    if (parts.length > 2) {
        // اگر بیش از یک نقطه دارد، فقط اولی را نگه دار
        value = parts[0] + '.' + parts.slice(1).join('');
        console.log('بعد از حذف نقاط اضافی:', value);
    }
    
    // فرمت‌بندی قسمت صحیح
    if (parts[0]) {
        const integerPart = parseInt(parts[0]) || 0;
        console.log('قسمت صحیح (parseInt):', integerPart);
        
        const formattedInteger = integerPart.toLocaleString('en-US');
        console.log('قسمت صحیح فرمت‌بندی شده:', formattedInteger);
        
        if (parts.length > 1 && parts[1] !== undefined) {
            // حفظ اعشار بدون جداکننده
            let decimalPart = parts[1];
            if (decimalPart.length > 10) {
                decimalPart = decimalPart.substring(0, 10);
            }
            input.value = formattedInteger + '.' + decimalPart;
            console.log('نتیجه نهایی (با اعشار):', input.value);
        } else {
            input.value = formattedInteger;
            console.log('نتیجه نهایی (بدون اعشار):', input.value);
        }
    }
    
    // بازگرداندن موقعیت کرسر (فقط برای فیلدهای text)
    if (input.type === 'text') {
        setTimeout(() => {
            const newValue = input.value;
            const oldLength = oldValue.length;
            const newLength = newValue.length;
            
            // محاسبه موقعیت جدید کرسر
            let newCursorPosition = cursorPosition;
            
            // اگر طول تغییر کرده، موقعیت کرسر را تنظیم کن
            if (newLength > oldLength) {
                newCursorPosition = cursorPosition + (newLength - oldLength);
            } else if (newLength < oldLength) {
                newCursorPosition = Math.max(0, cursorPosition - (oldLength - newLength));
            }
            
            // محدود کردن موقعیت کرسر
            newCursorPosition = Math.min(newCursorPosition, newValue.length);
            
            try {
                input.setSelectionRange(newCursorPosition, newCursorPosition);
                console.log('کرسر تنظیم شد: موقعیت', newCursorPosition);
            } catch (e) {
                // اگر setSelectionRange پشتیبانی نمی‌شود، خطا را نادیده بگیر
                console.log('setSelectionRange پشتیبانی نمی‌شود برای این نوع فیلد');
            }
        }, 0);
    }
    
    console.log('=== formatNumber پایان ===');
}

function validateAmount(input) {
    // حذف تمام کاراکترهای غیرعددی شامل اعداد فارسی
    let value = input.value.replace(/[^\d۰-۹]/g, '');
    
    // تبدیل اعداد فارسی به انگلیسی
    const persianToEnglish = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    };
    
    for (let persian in persianToEnglish) {
        value = value.replace(new RegExp(persian, 'g'), persianToEnglish[persian]);
    }
    
    // اعتبارسنجی
    if (value && parseInt(value) > 0) {
        input.style.borderColor = '#28a745';
    } else {
        input.style.borderColor = '#dc3545';
    }
}

function validateNumber(input) {
    console.log('=== validateNumber شروع ===');
    console.log('فیلد:', input.name || input.id || 'نامشخص');
    console.log('مقدار ورودی:', input.value);
    
    // برای اعداد اعشاری
    let value = input.value.replace(/[^\d۰-۹.]/g, '');
    console.log('بعد از حذف کاراکترهای غیرعددی:', value);
    
    // تبدیل اعداد فارسی به انگلیسی
    const persianToEnglish = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    };
    
    for (let persian in persianToEnglish) {
        value = value.replace(new RegExp(persian, 'g'), persianToEnglish[persian]);
    }
    console.log('بعد از تبدیل اعداد فارسی:', value);
    
    // اعتبارسنجی
    const parsedValue = parseFloat(value);
    console.log('مقدار parseFloat:', parsedValue);
    
    if (value && parseFloat(value) > 0) {
        input.style.borderColor = '#28a745';
        console.log('✅ معتبر - border سبز');
    } else {
        input.style.borderColor = '#dc3545';
        console.log('❌ نامعتبر - border قرمز');
    }
    
    console.log('=== validateNumber پایان ===');
}

function removeFormatting(input) {
    // فقط کاماها را حذف کن، اعشار را حفظ کن
    let value = input.value.replace(/,/g, '');
    input.value = value;
}

// تابع برای حذف فرمت از تمام فیلدهای عددی قبل از ارسال فرم
function removeAllFormatting() {
    console.log('=== removeAllFormatting شروع ===');
    const numberInputs = document.querySelectorAll('input[name*="amount"], input[name*="price"], input[name*="weight"], input[name*="rate"], input[name*="infrastructure"], input[name*="percentage"]');
    
    console.log('تعداد فیلدهای پیدا شده:', numberInputs.length);
    
    numberInputs.forEach((input, index) => {
        const oldValue = input.value;
        let value = input.value.replace(/,/g, '');
        input.value = value;
        
        console.log(`فیلد ${index + 1}: ${input.name || input.id || 'نامشخص'}`);
        console.log(`  قبل: ${oldValue}`);
        console.log(`  بعد: ${value}`);
    });
    
    console.log('=== removeAllFormatting پایان ===');
}

// اضافه کردن event listener به تمام فرم‌ها برای حذف فرمت قبل از ارسال
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            removeAllFormatting();
        });
    });
    
    // فرمت‌بندی اولیه تمام فیلدهای عددی هنگام بارگذاری صفحه
    formatAllNumberInputs();
});

// تابع برای فرمت‌بندی اولیه تمام فیلدهای عددی
function formatAllNumberInputs() {
    console.log('=== formatAllNumberInputs شروع ===');
    const numberInputs = document.querySelectorAll('input[name*="amount"], input[name*="price"], input[name*="weight"], input[name*="rate"], input[name*="infrastructure"], input[name*="percentage"]');
    
    console.log('تعداد فیلدهای پیدا شده:', numberInputs.length);
    
    numberInputs.forEach((input, index) => {
        console.log(`\n--- فیلد ${index + 1} ---`);
        console.log('نام فیلد:', input.name || input.id || 'نامشخص');
        console.log('نوع فیلد:', input.type);
        console.log('مقدار اولیه:', input.value);
        
        if (input.value && input.value.trim() !== '') {
            // تشخیص نوع فیلد بر اساس نام و نوع
            if (input.type === 'number') {
                // برای فیلدهای number، فقط مقدار خام را نگه دار (بدون فرمت‌بندی)
                // چون فیلدهای number نمی‌توانند کاما داشته باشند
                let value = input.value.replace(/,/g, '');
                input.value = value;
                console.log('فیلد number - کاماها حذف شدند:', value);
            } else if (input.type === 'text') {
                // برای فیلدهای text، فرمت‌بندی اعمال کن
                if (input.name.includes('amount') || input.name.includes('price')) {
                    // برای فیلدهای مبلغ از formatNumber استفاده کن (چون ممکن است اعشار داشته باشند)
                    console.log('فیلد مبلغ - استفاده از formatNumber');
                    formatNumber(input);
                } else if (input.name.includes('weight') || input.name.includes('rate') || input.name.includes('infrastructure') || input.name.includes('percentage')) {
                    // برای فیلدهای اعشاری از formatNumber استفاده کن
                    console.log('فیلد اعشاری - استفاده از formatNumber');
                    formatNumber(input);
                } else {
                    // برای بقیه فیلدها از formatAmount استفاده کن
                    console.log('فیلد دیگر - استفاده از formatAmount');
                    formatAmount(input);
                }
            }
        } else {
            console.log('فیلد خالی - فرمت‌بندی نشد');
        }
    });
    
    console.log('=== formatAllNumberInputs پایان ===');
}

// تعریف توابع به صورت global
window.formatAmount = formatAmount;
window.formatNumber = formatNumber;
window.validateAmount = validateAmount;
window.validateNumber = validateNumber;
window.removeFormatting = removeFormatting;
window.removeAllFormatting = removeAllFormatting;
window.formatAllNumberInputs = formatAllNumberInputs;
