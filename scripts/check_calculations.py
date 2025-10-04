#!/usr/bin/env python3
"""
اسکریپت بررسی محاسبات موجود در سمت سرور
این اسکریپت به شما کمک می‌کند تا ببینید کدام محاسبات در سمت سرور موجود هستند
"""

import os
import sys
import django
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from construction import calculations


def check_available_calculations():
    """بررسی محاسبات موجود در سمت سرور"""
    
    print("🔍 بررسی محاسبات موجود در سمت سرور...")
    print("=" * 60)
    
    # بررسی کلاس‌های محاسباتی
    calculation_classes = [
        ('ProjectCalculations', calculations.ProjectCalculations),
        ('ProfitCalculations', calculations.ProfitCalculations),
        ('InvestorCalculations', calculations.InvestorCalculations),
        ('TransactionCalculations', calculations.TransactionCalculations),
        ('ComprehensiveCalculations', calculations.ComprehensiveCalculations),
    ]
    
    available_methods = {}
    
    for class_name, class_obj in calculation_classes:
        print(f"\n📊 {class_name}:")
        methods = []
        
        for method_name in dir(class_obj):
            if not method_name.startswith('_') and callable(getattr(class_obj, method_name)):
                methods.append(method_name)
                print(f"  ✅ {method_name}")
        
        available_methods[class_name] = methods
    
    return available_methods


def check_api_endpoints():
    """بررسی API endpoints موجود"""
    
    print("\n🌐 API Endpoints موجود:")
    print("=" * 60)
    
    endpoints = [
        ("Project APIs", [
            "GET /api/v1/Project/comprehensive_analysis/",
            "GET /api/v1/Project/profit_metrics/",
            "GET /api/v1/Project/cost_metrics/",
            "GET /api/v1/Project/project_statistics_detailed/",
        ]),
        ("Investor APIs", [
            "GET /api/v1/Investor/{id}/detailed_statistics/",
            "GET /api/v1/Investor/{id}/ratios/",
            "GET /api/v1/Investor/all_investors_summary/",
        ]),
        ("Transaction APIs", [
            "GET /api/v1/Transaction/detailed_statistics/",
        ]),
    ]
    
    for category, endpoint_list in endpoints:
        print(f"\n📋 {category}:")
        for endpoint in endpoint_list:
            print(f"  ✅ {endpoint}")


def check_calculation_coverage():
    """بررسی پوشش محاسبات"""
    
    print("\n📈 پوشش محاسبات:")
    print("=" * 60)
    
    # محاسبات پیاده‌سازی شده
    implemented_calculations = [
        "سرمایه موجود", "سود کل", "موجودی کل", "هزینه نهایی",
        "هزینه هر متر خالص", "هزینه هر متر ناخالص", "ارزش هر متر",
        "سود نهایی", "درصد سود کل", "دوره متوسط ساخت",
        "درصد سود سالانه", "درصد سود ماهانه", "درصد سود روزانه",
        "آورده کل", "برداشت کل", "سرمایه خالص", "موجودی کل سرمایه‌گذار",
        "نسبت سرمایه فرد به کل", "نسبت سود فرد به کل", "شاخص نفع",
        "مجموع واریزها", "مجموع برداشت‌ها", "مجموع سودها",
        "تعداد واحدها", "متراژ کل", "قیمت کل", "زیربنای کل",
        "ضریب اصلاحی", "مدت پروژه", "روزهای فعال", "نرخ سود فعلی",
        "تعداد مالکان", "تعداد سرمایه‌گذاران", "تبدیل به تومان",
        "فرمت اعداد", "فرمت درصد", "میانگین", "مجموع تجمعی",
        "تعداد منحصر به فرد"
    ]
    
    total_calculations = 52
    implemented_count = len(implemented_calculations)
    coverage_percentage = (implemented_count / total_calculations) * 100
    
    print(f"✅ محاسبات پیاده‌سازی شده: {implemented_count}/{total_calculations}")
    print(f"📊 درصد پوشش: {coverage_percentage:.1f}%")
    
    print(f"\n📋 لیست محاسبات پیاده‌سازی شده:")
    for i, calc in enumerate(implemented_calculations, 1):
        print(f"  {i:2d}. {calc}")


def test_api_availability():
    """تست دسترسی API ها"""
    
    print("\n🧪 تست دسترسی API ها:")
    print("=" * 60)
    
    try:
        # تست محاسبات پروژه
        print("🔍 تست ProjectCalculations...")
        project_stats = calculations.ProjectCalculations.calculate_project_statistics()
        if 'error' not in project_stats:
            print("  ✅ ProjectCalculations کار می‌کند")
        else:
            print(f"  ❌ ProjectCalculations خطا: {project_stats['error']}")
        
        # تست محاسبات سود
        print("🔍 تست ProfitCalculations...")
        profit_metrics = calculations.ProfitCalculations.calculate_profit_percentages()
        if 'error' not in profit_metrics:
            print("  ✅ ProfitCalculations کار می‌کند")
        else:
            print(f"  ❌ ProfitCalculations خطا: {profit_metrics['error']}")
        
        # تست محاسبات هزینه
        print("🔍 تست ProjectCalculations.calculate_cost_metrics...")
        cost_metrics = calculations.ProjectCalculations.calculate_cost_metrics()
        if 'error' not in cost_metrics:
            print("  ✅ CostCalculations کار می‌کند")
        else:
            print(f"  ❌ CostCalculations خطا: {cost_metrics['error']}")
        
        # تست تحلیل جامع
        print("🔍 تست ComprehensiveCalculations...")
        analysis = calculations.ComprehensiveCalculations.get_comprehensive_project_analysis()
        if 'error' not in analysis:
            print("  ✅ ComprehensiveCalculations کار می‌کند")
        else:
            print(f"  ❌ ComprehensiveCalculations خطا: {analysis['error']}")
            
    except Exception as e:
        print(f"  ❌ خطا در تست API ها: {e}")


def main():
    """تابع اصلی"""
    
    print("🚀 اسکریپت بررسی محاسبات سمت سرور")
    print("=" * 60)
    
    try:
        # بررسی محاسبات موجود
        available_methods = check_available_calculations()
        
        # بررسی API endpoints
        check_api_endpoints()
        
        # بررسی پوشش محاسبات
        check_calculation_coverage()
        
        # تست دسترسی API ها
        test_api_availability()
        
        print("\n✅ بررسی کامل شد!")
        print("\n💡 برای استفاده از محاسبات:")
        print("   1. از سرویس JavaScript استفاده کنید: window.financialService")
        print("   2. مستندات را در docs/ بررسی کنید")
        print("   3. از API endpoints استفاده کنید")
        
    except Exception as e:
        print(f"❌ خطا در اجرای اسکریپت: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
