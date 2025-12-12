"""
Django Management Command برای تولید Tools و مستندات RAG
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import sys
import os


class Command(BaseCommand):
    help = 'تولید Tools و مستندات RAG از OpenAPI Schema یا Models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['schema', 'models', 'both'],
            default='schema',
            help='منبع تولید Tools: schema (از OpenAPI Schema), models (از Models/ViewSets), both (هر دو)'
        )
        parser.add_argument(
            '--target',
            type=str,
            choices=['django', 'standalone'],
            default='standalone',
            help='نوع خروجی: django (برای استفاده در Django), standalone (برای سرویس مستقل) - پیش‌فرض: standalone'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='مسیر فایل خروجی Tools (اختیاری)'
        )
        # پیش‌فرض: True
        # وقتی --rag استفاده می‌شود: True
        # وقتی --no-rag استفاده می‌شود: False  
        # وقتی هیچ کدام استفاده نمی‌شود: True (پیش‌فرض)
        parser.add_argument(
            '--rag',
            action='store_const',
            const=True,
            default=True,
            dest='rag',
            help='تولید مستندات RAG (پیش‌فرض: فعال)'
        )
        parser.add_argument(
            '--no-rag',
            action='store_const',
            const=False,
            dest='rag',
            help='غیرفعال کردن تولید مستندات RAG'
        )
        parser.add_argument(
            '--rag-output',
            type=str,
            help='مسیر فایل خروجی مستندات RAG (اختیاری)'
        )
        parser.add_argument(
            '--standalone-output',
            type=str,
            help='مسیر فایل خروجی برای نسخه standalone (فقط برای target=standalone)'
        )
        parser.add_argument(
            '--schema-path',
            type=str,
            help='مسیر فایل OpenAPI Schema (اختیاری)'
        )

    def handle(self, *args, **options):
        source = options['source']
        target = options['target']
        output = options.get('output')
        # پیش‌فرض: True (اگر --no-rag استفاده نشده باشد)
        # اگر 'rag' در options وجود نداشت یا True بود، پیش‌فرض True است
        # فقط وقتی --no-rag استفاده شده باشد، False می‌شود
        rag = options.get('rag', True)
        rag_output = options.get('rag_output')
        standalone_output = options.get('standalone_output')
        schema_path = options.get('schema_path')

        # محاسبه project_root: از assistant/management/commands/ به construction_project/
        # __file__ = assistant/management/commands/generate_tools.py
        # .parent = assistant/management/commands/
        # .parent.parent = assistant/management/
        # .parent.parent.parent = assistant/
        # .parent.parent.parent.parent = construction_project/ ✅
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        generators_path = project_root / 'assistant' / 'generators'
        generated_path = project_root / 'assistant' / 'generated'

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('🔧 تولید Tools و مستندات RAG'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # تولید از Schema
        if source in ['schema', 'both']:
            self.stdout.write(self.style.WARNING('📋 تولید Tools از OpenAPI Schema...'))
            self._generate_from_schema(
                generators_path,
                generated_path,
                target,
                output,
                rag,
                rag_output,
                standalone_output,
                schema_path
            )
            self.stdout.write('')

        # تولید از Models
        if source in ['models', 'both']:
            self.stdout.write(self.style.WARNING('📋 تولید Tools از Models/ViewSets...'))
            self._generate_from_models(
                generators_path,
                generated_path,
                output
            )
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('✅ تولید با موفقیت انجام شد!'))

    def _generate_from_schema(self, generators_path, generated_path, target, output, rag, rag_output, standalone_output, schema_path):
        """تولید Tools از OpenAPI Schema"""
        schema_gen_path = generators_path / 'schema_tool_generator.py'
        
        if not schema_gen_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ فایل {schema_gen_path} یافت نشد!'))
            return

        # تنظیم مسیرهای پیش‌فرض - همیشه در generated
        if not output:
            if target == 'standalone' and standalone_output:
                output = standalone_output
            else:
                # همیشه در generated، حتی برای standalone
                output = str(generated_path / 'generated_tools_from_schema.py')
        
        if rag and not rag_output:
            # همیشه در generated
            rag_output = str(generated_path / 'tool_documents_for_rag.json')

        # ساخت دستور
        cmd_parts = [
            sys.executable,
            str(schema_gen_path),
            '--target', target
        ]

        if output:
            cmd_parts.extend(['--output', output])

        if rag:
            cmd_parts.append('--rag')
            if rag_output:
                cmd_parts.extend(['--rag-output', rag_output])

        if schema_path:
            cmd_parts.extend(['--schema', schema_path])

        # اجرای دستور
        import subprocess
        try:
            result = subprocess.run(
                cmd_parts,
                cwd=str(generators_path.parent.parent),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f'   ✅ Tools از Schema تولید شد: {output}'))
                if rag:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ مستندات RAG تولید شد: {rag_output}'))
                    # schema_tool_generator خودش فایل readable را هم تولید می‌کند
                    readable_output = str(Path(rag_output).parent / 'tool_documents_for_rag_readable.json')
                    if Path(readable_output).exists():
                        self.stdout.write(self.style.SUCCESS(f'   ✅ مستندات RAG (خوانا) تولید شد: {readable_output}'))
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ خطا در تولید: {result.stderr}'))
                if result.stdout:
                    self.stdout.write(self.style.WARNING(f'   خروجی: {result.stdout}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ خطا: {str(e)}'))

    def _generate_from_models(self, generators_path, generated_path, output):
        """تولید Tools از Models/ViewSets"""
        model_gen_path = generators_path / 'model_tool_generator.py'
        
        if not model_gen_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ فایل {model_gen_path} یافت نشد!'))
            return

        # تنظیم مسیر پیش‌فرض
        if not output:
            output = str(generated_path / 'generated_tools_from_models.py')

        # ساخت دستور
        cmd_parts = [
            sys.executable,
            str(model_gen_path),
            '--output', output
        ]

        # اجرای دستور
        import subprocess
        try:
            result = subprocess.run(
                cmd_parts,
                cwd=str(generators_path.parent.parent),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f'   ✅ Tools از Models تولید شد: {output}'))
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ خطا در تولید: {result.stderr}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ خطا: {str(e)}'))

