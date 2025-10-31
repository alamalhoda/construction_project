#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تحلیل گزارش مصرف Cursor
"""

import csv
from datetime import datetime
from collections import defaultdict

total_cost = 0
total_tokens = 0
daily_stats = defaultdict(lambda: {'cost': 0, 'tokens': 0, 'requests': 0})
monthly_stats = defaultdict(lambda: {'cost': 0, 'tokens': 0, 'requests': 0})
model_stats = defaultdict(lambda: {'cost': 0, 'tokens': 0, 'requests': 0})
kind_stats = defaultdict(lambda: {'cost': 0, 'tokens': 0, 'requests': 0})

with open('usage-events-2025-10-31.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            cost = float(row['Cost'])
            tokens_str = row['Total Tokens'].replace(',', '') if row['Total Tokens'] else '0'
            tokens = int(tokens_str) if tokens_str else 0
            model = row['Model']
            kind = row['Kind']
            date_str = row['Date'][:10]  # فقط تاریخ
            
            total_cost += cost
            total_tokens += tokens
            
            # استخراج ماه (YYYY-MM)
            month_str = date_str[:7]  # فقط سال-ماه
            
            daily_stats[date_str]['cost'] += cost
            daily_stats[date_str]['tokens'] += tokens
            daily_stats[date_str]['requests'] += 1
            
            monthly_stats[month_str]['cost'] += cost
            monthly_stats[month_str]['tokens'] += tokens
            monthly_stats[month_str]['requests'] += 1
            
            model_stats[model]['cost'] += cost
            model_stats[model]['tokens'] += tokens
            model_stats[model]['requests'] += 1
            
            kind_stats[kind]['cost'] += cost
            kind_stats[kind]['tokens'] += tokens
            kind_stats[kind]['requests'] += 1
        except Exception as e:
            continue

print('=' * 60)
print('📊 آمار کلی مصرف')
print('=' * 60)
print(f'💰 کل هزینه: ${total_cost:.2f}')
print(f'🔢 کل Token: {total_tokens:,}')
print(f'📝 تعداد کل درخواست‌ها: {sum(daily_stats[d]["requests"] for d in daily_stats):,}')
print(f'📅 بازه زمانی: {min(daily_stats.keys())} تا {max(daily_stats.keys())}')
print()

print('=' * 60)
print('🤖 آمار بر اساس مدل')
print('=' * 60)
for model, stats in sorted(model_stats.items(), key=lambda x: x[1]['cost'], reverse=True):
    percentage = (stats['cost'] / total_cost * 100) if total_cost > 0 else 0
    print(f'{model:15} | ${stats["cost"]:8.2f} ({percentage:5.1f}%) | {stats["tokens"]:12,} token | {stats["requests"]:5} درخواست')
print()

print('=' * 60)
print('📋 آمار بر اساس نوع (Kind)')
print('=' * 60)
for kind, stats in sorted(kind_stats.items(), key=lambda x: x[1]['cost'], reverse=True):
    percentage = (stats['cost'] / total_cost * 100) if total_cost > 0 else 0
    print(f'{kind:15} | ${stats["cost"]:8.2f} ({percentage:5.1f}%) | {stats["tokens"]:12,} token | {stats["requests"]:5} درخواست')
print()

print('=' * 60)
print('📅 15 روز پرمصرف (بر اساس هزینه)')
print('=' * 60)
sorted_days = sorted(daily_stats.items(), key=lambda x: x[1]['cost'], reverse=True)[:15]
for date, stats in sorted_days:
    percentage = (stats['cost'] / total_cost * 100) if total_cost > 0 else 0
    print(f'{date} | ${stats["cost"]:7.2f} ({percentage:5.1f}%) | {stats["tokens"]:12,} token | {stats["requests"]:4} درخواست')
print()

print('=' * 60)
print('📅 آمار ماهانه (همه ماه‌ها)')
print('=' * 60)
sorted_months = sorted(monthly_stats.items(), key=lambda x: x[0])
for month, stats in sorted_months:
    percentage = (stats['cost'] / total_cost * 100) if total_cost > 0 else 0
    # محاسبه تعداد روزهای فعال در هر ماه
    days_in_month = len([d for d in daily_stats.keys() if d.startswith(month) and daily_stats[d]['cost'] > 0])
    avg_daily = stats['cost'] / days_in_month if days_in_month > 0 else 0
    avg_per_request = stats['cost'] / stats['requests'] if stats['requests'] > 0 else 0
    print(f'{month} | ${stats["cost"]:8.2f} ({percentage:5.1f}%) | {stats["tokens"]:15,} token | {stats["requests"]:5} درخواست | ${avg_daily:.2f}/روز | ${avg_per_request:.3f}/درخواست')
print()

print('=' * 60)
print('📈 آمار روزانه (30 روز آخر)')
print('=' * 60)
sorted_all_days = sorted(daily_stats.items(), key=lambda x: x[0], reverse=True)[:30]
for date, stats in sorted_all_days:
    print(f'{date} | ${stats["cost"]:7.2f} | {stats["tokens"]:12,} token | {stats["requests"]:4} درخواست')

