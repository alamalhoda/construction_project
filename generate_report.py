#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تولید گزارش فنی پروژه Construction Project
این اسکریپت آمار کامل پروژه را جمع‌آوری و گزارش جامع تولید می‌کند.
"""

import subprocess
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import re
import sys

# تنظیمات پروژه
PROJECT_NAME = "Construction Project"
PROJECT_REPO = "https://github.com/alamalhoda/construction_project"
GITHUB_REPO = "alamalhoda/construction_project"

class ProjectReportGenerator:
    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir).resolve()
        self.report_data = {}
        self.git_data = {}
        
    def run_command(self, command, shell=False, cwd=None):
        """اجرای دستور و دریافت خروجی"""
        try:
            if isinstance(command, str) and shell:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    cwd=cwd or self.project_dir
                )
            else:
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True,
                    cwd=cwd or self.project_dir
                )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            print(f"⚠️ خطا در اجرای دستور: {command}\n{str(e)}")
            return ""
    
    def get_git_branches(self):
        """دریافت لیست تمام برنچ‌ها"""
        branches = self.run_command("git branch -a", shell=True)
        branch_list = [b.strip().replace('* ', '').replace('remotes/origin/', '') 
                      for b in branches.split('\n') if b.strip()]
        return list(set(branch_list))
    
    def get_branch_commits(self, branch="master"):
        """دریافت تعداد کامیت‌های یک برنچ"""
        count = self.run_command(f"git rev-list --count {branch}", shell=True)
        return int(count) if count.isdigit() else 0
    
    def get_first_commit_date(self):
        """دریافت تاریخ اولین کامیت"""
        date_str = self.run_command(
            "git log --reverse --format='%ai' --date=iso | head -1", 
            shell=True
        )
        if date_str:
            try:
                return datetime.fromisoformat(date_str.split()[0] + ' ' + date_str.split()[1])
            except:
                return None
        return None
    
    def get_last_commit_date(self):
        """دریافت تاریخ آخرین کامیت"""
        date_str = self.run_command(
            "git log -1 --format='%ai' --date=iso", 
            shell=True
        )
        if date_str:
            try:
                return datetime.fromisoformat(date_str.split()[0] + ' ' + date_str.split()[1])
            except:
                return None
        return None
    
    def get_merge_commits_count(self):
        """تعداد کامیت‌های merge"""
        count = self.run_command("git log --merges --oneline | wc -l", shell=True)
        return int(count.strip()) if count.strip().isdigit() else 0
    
    def get_chabokan_deployment_merge_count(self):
        """تعداد merge های برنچ chabokan-deployment"""
        # شمارش کامیت‌های merge که chabokan-deployment را در پیغام دارند
        count = self.run_command(
            "git log --oneline --all --merges | grep -i 'chabokan-deployment' | wc -l",
            shell=True
        )
        return int(count.strip()) if count.strip().isdigit() else 0
    
    def get_git_push_count(self):
        """تعداد git push ها (بر اساس reflog و commits در remote)"""
        # روش 1: استفاده از reflog برای push events
        reflog_count = self.run_command(
            "git reflog show origin/master 2>/dev/null | grep -iE 'update|push' | wc -l",
            shell=True
        )
        
        # روش 2: شمارش commits در remote branches
        # اگر origin/master وجود دارد، commits آن را می‌شماریم
        remote_commits = self.run_command(
            "git rev-list --count origin/master 2>/dev/null || echo '0'",
            shell=True
        )
        
        # روش 3: شمارش unique commits در remote branches
        all_remote_commits = self.run_command(
            "git log --all --remotes --oneline 2>/dev/null | wc -l",
            shell=True
        )
        
        # انتخاب بهترین تخمین: اگر reflog موجود باشد استفاده می‌کنیم، وگرنه از remote commits
        if reflog_count.strip().isdigit() and int(reflog_count.strip()) > 0:
            return int(reflog_count.strip())
        elif remote_commits.strip().isdigit():
            # اگر تعداد commits در remote برابر با local است، احتمالاً همه push شده‌اند
            local_commits = self.get_branch_commits("master")
            if int(remote_commits.strip()) == local_commits:
                # تخمین: تعداد commits / میانگین commits در هر push (فرض: 2-3 commits)
                estimated_pushes = max(1, local_commits // 2)
                return estimated_pushes
        
        # اگر هیچکدام کار نکرد، از reflog default استفاده کنیم
        default_reflog = self.run_command(
            "git reflog | grep -iE 'origin|push' | wc -l",
            shell=True
        )
        return int(default_reflog.strip()) if default_reflog.strip().isdigit() else 0
    
    def get_daily_commits(self, branch="master"):
        """گزارش روزانه کامیت‌ها با محاسبه زمان صرف شده"""
        log_output = self.run_command(
            f"git log --format='%ai' --date=iso {branch}",
            shell=True
        )
        
        # ساختار: {date: {'count': X, 'first_time': datetime, 'last_time': datetime}}
        daily_data = {}
        
        for line in log_output.split('\n'):
            if not line.strip():
                continue
            
            try:
                # پارس کردن تاریخ و زمان (فرمت: 2025-10-31 19:11:18 +0300)
                # حذف timezone برای ساده‌سازی
                line_clean = line.strip()
                if ' ' in line_clean:
                    date_time_part = line_clean.split()[0] + ' ' + line_clean.split()[1]
                    commit_datetime = datetime.strptime(date_time_part, '%Y-%m-%d %H:%M:%S')
                    date_part = commit_datetime.strftime('%Y-%m-%d')
                else:
                    continue
                
                if date_part not in daily_data:
                    daily_data[date_part] = {
                        'count': 0,
                        'first_time': commit_datetime,
                        'last_time': commit_datetime
                    }
                
                daily_data[date_part]['count'] += 1
                
                # به‌روزرسانی اولین و آخرین زمان
                if commit_datetime < daily_data[date_part]['first_time']:
                    daily_data[date_part]['first_time'] = commit_datetime
                if commit_datetime > daily_data[date_part]['last_time']:
                    daily_data[date_part]['last_time'] = commit_datetime
                    
            except Exception as e:
                # در صورت خطا در پارس، فقط تعداد را بشمار
                try:
                    date_part = line.split()[0]
                    if date_part not in daily_data:
                        daily_data[date_part] = {
                            'count': 0,
                            'first_time': None,
                            'last_time': None
                        }
                    daily_data[date_part]['count'] += 1
                except:
                    pass
        
        # محاسبه زمان صرف شده برای هر روز
        result = {}
        for date, data in daily_data.items():
            time_spent = None
            if data['first_time'] and data['last_time']:
                time_diff = data['last_time'] - data['first_time']
                total_seconds = time_diff.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                time_spent = {'hours': hours, 'minutes': minutes, 'total_seconds': total_seconds}
            
            result[date] = {
                'count': data['count'],
                'time_spent': time_spent,
                'first_time': data['first_time'],
                'last_time': data['last_time']
            }
        
        return result
    
    def get_commit_stats(self, branch="master", limit=None):
        """آمار کامیت‌های برنچ اصلی"""
        commits = []
        
        # دریافت لیست کامیت‌ها با جزئیات (با پیغام کامل شامل body)
        if limit:
            commit_list = self.run_command(
                f"git log --format='%H' -n {limit} {branch}",
                shell=True
            )
        else:
            commit_list = self.run_command(
                f"git log --format='%H' {branch}",
                shell=True
            )
        
        for commit_hash in commit_list.split('\n'):
            if not commit_hash.strip():
                continue
            
            commit_hash = commit_hash.strip()
            
            # دریافت اطلاعات کامیت (با body)
            commit_info = self.run_command(
                f"git log -1 --format='%H|%ai|%an|%ae' {commit_hash}",
                shell=True
            )
            
            if not commit_info:
                continue
            
            parts = commit_info.split('|')
            if len(parts) >= 4:
                date_str = parts[1]
                author = parts[2]
                email = parts[3]
                
                # دریافت پیغام کامل (subject + body)
                full_message = self.run_command(
                    f"git log -1 --format='%B' {commit_hash}",
                    shell=True
                )
                message = full_message.strip() if full_message else ""
                
                # دریافت تعداد فایل‌های تغییر کرده
                changed_files = self.run_command(
                    f"git show --stat --format='' {commit_hash} | grep -E '\\|' | wc -l",
                    shell=True
                )
                num_files = int(changed_files.strip()) if changed_files.strip().isdigit() else 0
                
                # دریافت فایل‌های تغییر کرده (همه فایل‌ها)
                files_output = self.run_command(
                    f"git show --stat --format='' {commit_hash} | grep -E '\\|'",
                    shell=True
                )
                files_changed = []
                for file_line in files_output.split('\n'):
                    if '|' in file_line:
                        file_name = file_line.split('|')[0].strip()
                        if file_name:
                            files_changed.append(file_name)
                
                commits.append({
                    'hash': commit_hash[:8],
                    'date': date_str,
                    'message': message,  # پیغام کامل
                    'author': author,
                    'files_count': num_files,
                    'files': files_changed  # تمام فایل‌ها
                })
        
        return commits
    
    def get_top_changed_files(self, branch="master", limit=20):
        """فایل‌های با بیشترین تغییرات"""
        # استفاده از git log برای یافتن فایل‌های با بیشترین تغییرات
        output = self.run_command(
            f"git log --name-only --pretty=format: {branch} | sort | uniq -c | sort -rn | head -{limit}",
            shell=True
        )
        
        files = []
        for line in output.split('\n'):
            if line.strip() and not line.strip().startswith('commit'):
                parts = line.strip().split(None, 1)
                if len(parts) == 2 and os.path.exists(parts[1]):
                    files.append({
                        'count': int(parts[0]),
                        'file': parts[1]
                    })
        return files
    
    def get_code_stats_cloc(self):
        """استخراج آمار کد با cloc"""
        output = self.run_command(
            "cloc . --exclude-dir=env,staticfiles,__pycache__,node_modules,.git,backups,logs,temp_data --json",
            shell=True
        )
        if output:
            try:
                return json.loads(output)
            except:
                return None
        return None
    
    def count_project_files(self):
        """شمارش فایل‌های پروژه بر اساس نوع"""
        file_counts = defaultdict(int)
        file_types = {
            '.py': 'Python',
            '.html': 'HTML',
            '.js': 'JavaScript',
            '.css': 'CSS',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.txt': 'Text',
            '.yml': 'YAML',
            '.yaml': 'YAML',
        }
        
        excluded_dirs = {'env', 'staticfiles', '__pycache__', '.git', 'node_modules', 
                        'backups', 'logs', 'temp_data', '.pytest_cache', 'venv'}
        
        for root, dirs, files in os.walk(self.project_dir):
            # حذف دایرکتوری‌های حذف شده
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in file_types:
                    file_counts[file_types[ext]] += 1
                else:
                    file_counts['Other'] += 1
        
        return dict(file_counts)
    
    def get_django_apps(self):
        """استخراج اپلیکیشن‌های Django"""
        settings_file = self.project_dir / "construction_project" / "settings.py"
        if settings_file.exists():
            content = settings_file.read_text(encoding='utf-8')
            # جستجوی INSTALLED_APPS
            match = re.search(r"INSTALLED_APPS\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if match:
                apps_text = match.group(1)
                apps = []
                for line in apps_text.split('\n'):
                    app = line.strip().strip('",\'').strip()
                    if app and not app.startswith('#') and not app.startswith('django'):
                        apps.append(app)
                return apps
        return []
    
    def get_django_models_count(self):
        """شمارش مدل‌های Django"""
        models_count = 0
        model_files = list(self.project_dir.glob("**/models.py"))
        for model_file in model_files:
            content = model_file.read_text(encoding='utf-8', errors='ignore')
            # شمارش کلاس‌های Model
            models_count += len(re.findall(r'class\s+\w+\(models\.Model\)', content))
        return models_count
    
    def count_documentation_files(self):
        """شمارش فایل‌های مستندات"""
        md_files = list(self.project_dir.glob("**/*.md"))
        md_count = len([f for f in md_files if 'docs' in str(f) or 'README' in f.name])
        total_size = sum(f.stat().st_size for f in md_files)
        return {
            'count': md_count,
            'total_size_kb': round(total_size / 1024, 2)
        }
    
    def get_python_dependencies(self):
        """خواندن requirements.txt"""
        req_file = self.project_dir / "requirements.txt"
        if req_file.exists():
            deps = []
            for line in req_file.read_text(encoding='utf-8').split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    deps.append(line.split('>=')[0].split('==')[0].split('~')[0])
            return deps
        return []
    
    def calculate_project_duration(self, first_date, last_date):
        """محاسبه مدت زمان پروژه"""
        if first_date and last_date:
            duration = last_date - first_date
            return {
                'days': duration.days,
                'months': round(duration.days / 30, 1),
                'hours_estimate': duration.days * 4  # تخمین 4 ساعت در روز
            }
        return None
    
    def get_ai_usage_stats(self, project_start_date, project_end_date):
        """استخراج آمار استفاده از AI"""
        import csv
        
        stats = {
            'chat_count': 0,
            'total_tokens': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'total_cost': 0.0,
            'estimated': True,
            'note': 'آمار بر اساس فیلتر تاریخ پروژه (تقریبی)'
        }
        
        # شمارش چت‌ها از .specstory/history (دقیق)
        history_dir = self.project_dir / ".specstory" / "history"
        if history_dir.exists():
            md_files = list(history_dir.glob("*.md"))
            stats['chat_count'] = len(md_files)
            stats['chat_count_estimated'] = False
        else:
            stats['chat_count'] = 0
            stats['chat_count_estimated'] = True
        
        # خواندن آمار توکن و هزینه از CSV (فیلتر شده)
        csv_file = self.project_dir / "docs" / "usage-events-2025-10-31.csv"
        if csv_file.exists():
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    events_processed = 0
                    events_filtered = 0
                    
                    for row in reader:
                        events_processed += 1
                        # پارس کردن تاریخ
                        date_str = row.get('Date', '').strip('"')
                        if not date_str:
                            continue
                        
                        try:
                            # تبدیل تاریخ ISO به datetime
                            # فرمت: "2025-10-29T14:46:13.662Z"
                            if 'T' in date_str:
                                date_part = date_str.split('T')[0]
                                time_part = date_str.split('T')[1].split('.')[0] if '.' in date_str.split('T')[1] else date_str.split('T')[1].split('Z')[0]
                                date_time_str = f"{date_part} {time_part}"
                                event_date_naive = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                            else:
                                event_date_naive = datetime.fromisoformat(date_str)
                            
                            # فیلتر بر اساس تاریخ پروژه
                            should_include = True
                            if project_start_date and project_end_date:
                                # فقط تاریخ را مقایسه می‌کنیم (بدون ساعت)
                                event_date_only = event_date_naive.date()
                                start_date_only = project_start_date.date()
                                end_date_only = project_end_date.date()
                                should_include = start_date_only <= event_date_only <= end_date_only
                            
                            if should_include:
                                events_filtered += 1
                                # اضافه کردن به آمار - حذف کاما و تبدیل به عدد
                                total_tokens_str = row.get('Total Tokens', '0').strip('"').replace(',', '') or '0'
                                input_tokens_str = row.get('Input (w/ Cache Write)', '0').strip('"').replace(',', '') or '0'
                                output_tokens_str = row.get('Output Tokens', '0').strip('"').replace(',', '') or '0'
                                cost_str = row.get('Cost', '0').strip('"') or '0'
                                
                                total_tokens = int(total_tokens_str) if total_tokens_str.isdigit() else 0
                                input_tokens = int(input_tokens_str) if input_tokens_str.isdigit() else 0
                                output_tokens = int(output_tokens_str) if output_tokens_str.isdigit() else 0
                                cost = float(cost_str) if cost_str.replace('.', '').replace('-', '').isdigit() else 0.0
                                
                                stats['total_tokens'] += total_tokens
                                stats['input_tokens'] += input_tokens
                                stats['output_tokens'] += output_tokens
                                stats['total_cost'] += cost
                        except (ValueError, KeyError) as e:
                            continue
                    
                    stats['csv_events_processed'] = events_processed
                    stats['csv_events_filtered'] = events_filtered
            except Exception as e:
                stats['error'] = str(e)
        
        return stats
    
    def generate_report(self):
        """تولید گزارش کامل"""
        print("🔄 در حال جمع‌آوری اطلاعات Git...")
        
        # اطلاعات Git
        branches = self.get_git_branches()
        master_commits = self.get_branch_commits("master")
        first_commit = self.get_first_commit_date()
        last_commit = self.get_last_commit_date()
        merge_count = self.get_merge_commits_count()
        chabokan_merge_count = self.get_chabokan_deployment_merge_count()
        print("🔄 در حال محاسبه تعداد git push ها...")
        push_count = self.get_git_push_count()
        daily_commits = self.get_daily_commits("master")
        commit_stats = self.get_commit_stats("master", limit=None)  # تمام کامیت‌ها
        top_files = self.get_top_changed_files("master", limit=30)
        
        print("🔄 در حال محاسبه خطوط کد با cloc...")
        cloc_data = self.get_code_stats_cloc()
        
        print("🔄 در حال شمارش فایل‌ها...")
        file_counts = self.count_project_files()
        
        print("🔄 در حال استخراج اطلاعات Django...")
        django_apps = self.get_django_apps()
        models_count = self.get_django_models_count()
        
        print("🔄 در حال بررسی مستندات...")
        docs_info = self.count_documentation_files()
        
        print("🔄 در حال خواندن وابستگی‌ها...")
        dependencies = self.get_python_dependencies()
        
        print("🔄 در حال محاسبه مدت زمان پروژه...")
        duration = self.calculate_project_duration(first_commit, last_commit)
        
        print("🔄 در حال استخراج آمار استفاده از AI...")
        ai_stats = self.get_ai_usage_stats(first_commit, last_commit)
        
        # جمع‌آوری تمام داده‌ها
        self.report_data = {
            'project': {
                'name': PROJECT_NAME,
                'repo': PROJECT_REPO,
                'first_commit': first_commit.strftime('%Y-%m-%d %H:%M:%S') if first_commit else None,
                'last_commit': last_commit.strftime('%Y-%m-%d %H:%M:%S') if last_commit else None,
                'duration': duration
            },
            'git': {
                'branches': branches,
                'branches_count': len(branches),
                'master_commits': master_commits,
                'merge_commits': merge_count,
                'chabokan_merge_count': chabokan_merge_count,
                'push_count': push_count,
                'daily_commits': daily_commits,
                'commit_stats': commit_stats,
                'top_changed_files': top_files
            },
            'code': {
                'cloc': cloc_data,
                'file_counts': file_counts
            },
            'django': {
                'apps': django_apps,
                'apps_count': len(django_apps),
                'models_count': models_count
            },
            'docs': docs_info,
            'dependencies': {
                'python': dependencies,
                'python_count': len(dependencies)
            },
            'ai_usage': ai_stats
        }
        
        return self.report_data
    
    def format_report_markdown(self):
        """فرمت‌بندی گزارش به Markdown"""
        data = self.report_data
        
        report = f"""# 📊 گزارش فنی پروژه {PROJECT_NAME}

> **تولید شده در:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> **Repository:** [{PROJECT_REPO}]({PROJECT_REPO})

---

## 1️⃣ خلاصه اجرایی

| مورد | مقدار |
|------|-------|
| **نام پروژه** | {data['project']['name']} |
| **تاریخ اولین کامیت** | {data['project']['first_commit'] or 'نامشخص'} |
| **تاریخ آخرین کامیت** | {data['project']['last_commit'] or 'نامشخص'} |
| **مدت زمان توسعه** | {data['project']['duration']['days']} روز ({data['project']['duration']['months']} ماه) |

---

## 2️⃣ معماری و فناوری‌ها

### معماری کلی
- **نوع:** Client/Server
- **API:** REST API
- **Framework:** Django 4.2
- **Frontend:** HTML, JavaScript, CSS
- **Backend:** Python 3.8+

### زبان‌های برنامه‌نویسی

"""
        
        if data['code']['cloc']:
            cloc = data['code']['cloc']
            report += "| زبان | فایل | خطوط خالی | خطوط کامنت | خطوط کد |\n"
            report += "|------|------|-----------|------------|----------|\n"
            
            if 'SUM' in cloc:
                sum_data = cloc['SUM']
                report += f"| **کل** | {sum_data.get('nFiles', 0)} | {sum_data.get('blank', 0):,} | {sum_data.get('comment', 0):,} | **{sum_data.get('code', 0):,}** |\n"
            
            # زبان‌های اصلی
            for lang, stats in sorted(cloc.items(), key=lambda x: x[1].get('code', 0), reverse=True):
                if lang not in ['header', 'SUM'] and stats.get('code', 0) > 0:
                    report += f"| {lang} | {stats.get('nFiles', 0)} | {stats.get('blank', 0):,} | {stats.get('comment', 0):,} | {stats.get('code', 0):,} |\n"
        
        report += f"""

---

## 3️⃣ آمار کد

### توزیع فایل‌ها بر اساس نوع

| نوع فایل | تعداد |
|----------|-------|
"""
        for file_type, count in sorted(data['code']['file_counts'].items(), key=lambda x: x[1], reverse=True):
            report += f"| {file_type} | {count:,} |\n"
        
        report += f"""

---

## 4️⃣ ساختار پروژه

### اپلیکیشن‌های Django

**تعداد اپلیکیشن‌ها:** {data['django']['apps_count']}

- {chr(10).join(f"- `{app}`" for app in data['django']['apps'])}

### مدل‌های پایگاه داده

**تعداد مدل‌ها:** {data['django']['models_count']}

---

## 5️⃣ تاریخچه Git

### آمار کلی

| مورد | مقدار |
|------|-------|
| **تعداد برنچ‌ها** | {data['git']['branches_count']} |
| **تعداد کامیت‌ها در master** | {data['git']['master_commits']:,} |
| **تعداد کامیت‌های merge** | {data['git']['merge_commits']:,} |
| **تعداد merge های chabokan-deployment** | {data['git']['chabokan_merge_count']:,} |
| **تعداد git push ها** | {data['git']['push_count']:,} |
| **اولین کامیت** | {data['project']['first_commit']} |
| **آخرین کامیت** | {data['project']['last_commit']} |

### برنچ‌ها

"""
        for branch in data['git']['branches']:
            commits = self.get_branch_commits(branch)
            report += f"- `{branch}` - {commits:,} کامیت\n"
        
        report += f"""

### گزارش کامیت‌های Master (تمام کامیت‌ها)

**تعداد کل کامیت‌ها:** {len(data['git']['commit_stats']):,}

| تاریخ | پیغام کامیت | تعداد فایل |
|-------|-------------|-----------|
"""
        
        for commit in data['git']['commit_stats']:
            # پیغام کامیت کامل (با حفظ خطوط جدید)
            commit_message = commit['message']
            # جایگزینی کاراکترهای خاص برای Markdown
            commit_message = commit_message.replace('|', '\\|')
            # تبدیل خطوط جدید به <br> برای نمایش در جدول Markdown
            commit_message = commit_message.replace('\n', '<br>')
            # حذف فضای اضافی
            commit_message = commit_message.strip()
            
            # تاریخ
            date_part = commit['date'].split()[0] if commit['date'] else ''
            time_part = commit['date'].split()[1][:5] if len(commit['date'].split()) > 1 else ''
            
            # سطر اول: تاریخ، پیغام، تعداد فایل
            report += f"| {date_part} {time_part} | {commit_message} | {commit['files_count']} |\n"
            
            # سطر دوم: لیست فایل‌ها به صورت tag
            if commit['files']:
                # تبدیل فایل‌ها به tag های markdown (inline code با فاصله)
                files_tags = ' '.join(f"`{f}`" for f in commit['files'])
                report += f"| ⬇️ *فایل‌ها:* | {files_tags} | |\n"
            else:
                report += f"| ⬇️ *فایل‌ها:* | *هیچ فایلی تغییر نکرده* | |\n"
        
        report += f"""

### فایل‌های با بیشترین تغییرات

| رتبه | فایل | تعداد تغییرات |
|------|------|---------------|
"""
        for i, file_info in enumerate(data['git']['top_changed_files'][:20], 1):
            report += f"| {i} | `{file_info['file']}` | {file_info['count']:,} |\n"
        
        report += f"""

### گزارش روزانه کامیت‌ها

| تاریخ | تعداد کامیت‌ها | اولین کامیت | آخرین کامیت | زمان صرف شده |
|-------|----------------|------------|------------|-------------|
"""
        sorted_daily = sorted(data['git']['daily_commits'].items(), key=lambda x: x[0], reverse=True)
        
        # محاسبه مجموع زمان صرف شده (از تمام روزها)
        total_seconds = 0
        days_with_time = 0
        
        # نمایش همه روزهای دارای کامیت در جدول
        for date, daily_info in sorted_daily:
            count = daily_info['count']
            
            # نمایش زمان اولین و آخرین کامیت
            first_time_str = "-"
            last_time_str = "-"
            time_spent_str = "-"
            day_seconds = 0
            
            if daily_info.get('first_time') and daily_info.get('last_time'):
                first_time_str = daily_info['first_time'].strftime('%H:%M:%S')
                last_time_str = daily_info['last_time'].strftime('%H:%M:%S')
                
                # محاسبه زمان صرف شده
                if daily_info.get('time_spent'):
                    ts = daily_info['time_spent']
                    day_seconds = ts.get('total_seconds', 0)
                    if ts['hours'] > 0 or ts['minutes'] > 0:
                        time_spent_str = f"{ts['hours']}h {ts['minutes']}m"
                    else:
                        time_spent_str = "< 1 دقیقه"
                else:
                    # محاسبه مجدد اگر موجود نباشد
                    time_diff = daily_info['last_time'] - daily_info['first_time']
                    day_seconds = time_diff.total_seconds()
                    hours = int(day_seconds // 3600)
                    minutes = int((day_seconds % 3600) // 60)
                    if hours > 0 or minutes > 0:
                        time_spent_str = f"{hours}h {minutes}m"
                    else:
                        time_spent_str = "< 1 دقیقه"
            
            # اضافه کردن به مجموع
            if day_seconds > 0:
                total_seconds += day_seconds
                days_with_time += 1
            
            # نمایش در جدول (همه روزها)
            report += f"| {date} | {count} | {first_time_str} | {last_time_str} | {time_spent_str} |\n"
        
        # محاسبه و نمایش مجموع
        total_hours = int(total_seconds // 3600)
        total_minutes = int((total_seconds % 3600) // 60)
        total_days = int(total_hours // 24)
        remaining_hours = total_hours % 24
        
        # محاسبه میانگین
        avg_hours = total_hours / max(days_with_time, 1)
        avg_minutes = int((avg_hours % 1) * 60)
        avg_hours_int = int(avg_hours)
        
        report += f"""
**📊 آمار کلی گزارش روزانه:**

- **تعداد روزهای دارای کامیت:** {days_with_time}
- **مجموع زمان صرف شده:** {total_days} روز، {remaining_hours} ساعت و {total_minutes} دقیقه ({total_hours} ساعت و {total_minutes} دقیقه)
- **میانگین زمان در روز:** {avg_hours_int} ساعت و {avg_minutes} دقیقه

---

## 6️⃣ وابستگی‌ها

### Python Packages

**تعداد Package ها:** {data['dependencies']['python_count']}

**لیست 10 Package اول:**

"""
        for dep in data['dependencies']['python'][:10]:
            report += f"- `{dep}`\n"
        
        report += f"""

---

## 7️⃣ استفاده از هوش مصنوعی

### آمار استفاده از AI

| مورد | مقدار | دقت |
|------|-------|-----|
| **تعداد چت‌ها** | {data['ai_usage']['chat_count']:,} | {'✅ دقیق' if not data['ai_usage'].get('chat_count_estimated', True) else '⚠️ تقریبی'} |
| **مجموع توکن‌ها** | {data['ai_usage']['total_tokens']:,} | ⚠️ تقریبی (فیلتر بر اساس تاریخ) |
| **توکن‌های ورودی** | {data['ai_usage']['input_tokens']:,} | ⚠️ تقریبی |
| **توکن‌های خروجی** | {data['ai_usage']['output_tokens']:,} | ⚠️ تقریبی |
| **هزینه کل (USD)** | ${data['ai_usage']['total_cost']:.2f} | ⚠️ تقریبی (فیلتر بر اساس تاریخ) |

**نکته مهم:**
- ✅ تعداد چت‌ها از `.specstory/history` استخراج شده و **دقیق** است
- ⚠️ آمار توکن و هزینه از فایل CSV با فیلتر تاریخ پروژه استخراج شده و **تقریبی** است (ممکن است شامل پروژه‌های دیگر هم باشد)

**منابع داده:**
- تعداد چت‌ها: `.specstory/history/` ({data['ai_usage']['chat_count']} فایل)
- توکن و هزینه: `docs/usage-events-2025-10-31.csv` (فیلتر شده بر اساس تاریخ پروژه)
  - رویدادهای پردازش شده در CSV: {data['ai_usage'].get('csv_events_processed', 0):,}
  - رویدادهای فیلتر شده (مربوط به پروژه): {data['ai_usage'].get('csv_events_filtered', 0):,}

---

## 8️⃣ مستندات

- **تعداد فایل‌های مستندات:** {data['docs']['count']}
- **حجم کل مستندات:** {data['docs']['total_size_kb']:,} KB

---

## 9️⃣ نتیجه‌گیری

### خلاصه آمار

- ✅ **{data['git']['master_commits']:,} کامیت** در برنچ اصلی
- ✅ **{data['git']['branches_count']} برنچ** در پروژه
- ✅ **{data['git']['merge_commits']:,} کامیت merge** در کل پروژه
- ✅ **{data['git']['chabokan_merge_count']:,} merge** از برنچ chabokan-deployment
- ✅ **{data['git']['push_count']:,} git push** به GitHub
- ✅ **{data['django']['apps_count']} اپلیکیشن Django**
- ✅ **{data['django']['models_count']} مدل پایگاه داده**
- ✅ **{data['dependencies']['python_count']} وابستگی Python**
- ✅ **{data['docs']['count']} فایل مستندات**

### نکات مهم

- پروژه در مدت **{data['project']['duration']['days']} روز** توسعه یافته است
- میانگین **{round(data['git']['master_commits'] / max(data['project']['duration']['days'], 1), 2)} کامیت در روز**

---

**📝 گزارش تولید شده با اسکریپت Project Report Generator**  
**🔄 آخرین بروزرسانی:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report
    
    def format_report_html(self):
        """فرمت‌بندی گزارش به HTML با Bootstrap"""
        import markdown
        import re
        
        # تبدیل Markdown به HTML
        md_content = self.format_report_markdown()
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # پردازش جدول کامیت‌ها برای اضافه کردن کلاس‌های رنگ‌بندی
        # پیدا کردن جدول کامیت‌ها با استفاده از شناسه منحصر به فرد
        # الگوی دقیق‌تر: پیدا کردن جدول بعد از "گزارش کامیت‌های Master"
        
        def process_commits_table(html):
            # پیدا کردن موقعیت جدول کامیت‌ها
            # جستجوی هدر "گزارش کامیت‌های Master"
            header_pattern = r'<h3>گزارش کامیت‌های Master.*?</h3>'
            header_match = re.search(header_pattern, html, re.DOTALL)
            
            if not header_match:
                return html
            
            # پیدا کردن جدول بعد از هدر
            start_pos = header_match.end()
            # جستجوی <table> بعد از هدر
            table_start = html.find('<table>', start_pos)
            if table_start == -1:
                return html
            
            # پیدا کردن پایان جدول (قبل از <h3> بعدی یا <h2>)
            table_end_pattern = r'</table>\s*(?:<h[23]>|</body>|$)'
            table_end_match = re.search(table_end_pattern, html[table_start:], re.DOTALL)
            
            if not table_end_match:
                return html
            
            table_end = table_start + table_end_match.end()
            table_html = html[table_start:table_end]
            
            # اضافه کردن کلاس commits-table
            table_html = re.sub(r'<table>', '<table class="commits-table">', table_html)
            
            # پردازش سطرهای tbody
            # پیدا کردن تمام <tr> در tbody
            tbody_pattern = r'(<tbody>)(.*?)(</tbody>)'
            
            def process_tbody(match):
                tbody_open = match.group(1)
                tbody_content = match.group(2)
                tbody_close = match.group(3)
                
                # پیدا کردن تمام سطرها
                tr_pattern = r'(<tr>.*?</tr>)'
                rows = re.findall(tr_pattern, tbody_content, re.DOTALL)
                
                if not rows:
                    return match.group(0)
                
                # هر 2 سطر یک کامیت است
                processed_rows = []
                commit_index = 0
                
                for i in range(0, len(rows), 2):
                    commit_class = 'commit-even' if commit_index % 2 == 0 else 'commit-odd'
                    
                    # سطر اول کامیت
                    row1 = rows[i]
                    row1 = re.sub(r'<tr>', f'<tr class="{commit_class}">', row1)
                    processed_rows.append(row1)
                    
                    # سطر دوم کامیت (فایل‌ها) - اگر وجود دارد
                    if i + 1 < len(rows):
                        row2 = rows[i + 1]
                        row2 = re.sub(r'<tr>', f'<tr class="{commit_class}">', row2)
                        processed_rows.append(row2)
                    
                    commit_index += 1
                
                return tbody_open + ''.join(processed_rows) + tbody_close
            
            # اعمال پردازش روی tbody
            table_html = re.sub(tbody_pattern, process_tbody, table_html, flags=re.DOTALL)
            
            # جایگزینی جدول در HTML اصلی
            return html[:table_start] + table_html + html[table_end:]
        
        # اعمال پردازش روی HTML
        html_content = process_commits_table(html_content)
        
        # ساخت HTML کامل با Bootstrap
        html_template = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گزارش فنی پروژه {PROJECT_NAME}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            padding: 20px 0;
        }}
        .report-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            padding: 30px;
            margin: 20px auto;
            max-width: 1400px;
        }}
        .report-header {{
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .report-header h1 {{
            color: #007bff;
            font-weight: bold;
        }}
        .stats-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stats-card h3 {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stats-card p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        table {{
            font-size: 0.95rem;
        }}
        table th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}
        /* رنگ‌بندی یکی درمیان برای کامیت‌ها (هر 2 سطر یک کامیت) */
        .commits-table tbody tr.commit-odd {{
            background-color: #f8f9fa;
        }}
        .commits-table tbody tr.commit-even {{
            background-color: #ffffff;
        }}
        .commits-table tbody tr.commit-odd:hover,
        .commits-table tbody tr.commit-even:hover {{
            background-color: #edf6ff;
        }}
        .badge {{
            font-size: 0.85rem;
            padding: 5px 10px;
        }}
        .commit-message {{
            white-space: pre-wrap;
            word-wrap: break-word;
            max-width: 600px;
        }}
        .files-list {{
            font-size: 0.9rem;
            color: #6c757d;
        }}
        .files-list code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            margin: 2px;
            display: inline-block;
        }}
        h2 {{
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        h3 {{
            color: #6c757d;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .code-block {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            direction: ltr;
            text-align: left;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
            text-align: center;
            color: #6c757d;
        }}
        @media print {{
            .report-container {{
                box-shadow: none;
                padding: 0;
            }}
        }}
        code{{
            border-radius: 9px;
            border-color: #198754;
            border-style: ridge;
            padding: 2px;
            background-color: #198754;
            font-size: .875em;
            color: #deeede;
            word-wrap: break-word; 
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="report-container">
            <div class="report-header">
                <h1><i class="bi bi-file-earmark-text"></i> گزارش فنی پروژه {PROJECT_NAME}</h1>
                <p class="text-muted">
                    <i class="bi bi-calendar"></i> تولید شده در: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    <i class="bi bi-github"></i> Repository: <a href="{PROJECT_REPO}" target="_blank">{PROJECT_REPO}</a>
                </p>
            </div>
            
            {html_content}
            
            <div class="footer">
                <p><i class="bi bi-info-circle"></i> گزارش تولید شده با اسکریپت Project Report Generator</p>
                <p class="text-muted">آخرین بروزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
        
        return html_template
    
    def save_report(self, output_file="TECHNICAL_REPORT.md"):
        """ذخیره گزارش در فایل"""
        report_content = self.format_report_markdown()
        output_path = self.project_dir / output_file
        output_path.write_text(report_content, encoding='utf-8')
        print(f"✅ گزارش در فایل {output_path} ذخیره شد!")
        return output_path
    
    def save_html_report(self, output_file="TECHNICAL_REPORT.html"):
        """ذخیره گزارش HTML در فایل"""
        try:
            html_content = self.format_report_html()
            output_path = self.project_dir / output_file
            output_path.write_text(html_content, encoding='utf-8')
            print(f"✅ گزارش HTML در فایل {output_path} ذخیره شد!")
            return output_path
        except ImportError:
            print("⚠️ برای تولید گزارش HTML نیاز به کتابخانه markdown است.")
            print("💡 نصب: pip install markdown")
            return None


def main():
    """تابع اصلی"""
    print("🚀 شروع تولید گزارش فنی پروژه...")
    print("=" * 60)
    
    generator = ProjectReportGenerator()
    generator.generate_report()
    output_file = generator.save_report()
    html_file = generator.save_html_report()
    
    print("=" * 60)
    print(f"✅ گزارش Markdown با موفقیت تولید شد: {output_file}")
    print(f"📄 حجم فایل: {os.path.getsize(output_file) / 1024:.2f} KB")
    if html_file:
        print(f"✅ گزارش HTML با موفقیت تولید شد: {html_file}")
        print(f"📄 حجم فایل: {os.path.getsize(html_file) / 1024:.2f} KB")


if __name__ == "__main__":
    main()