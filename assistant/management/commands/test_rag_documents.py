"""
Django management command برای تست مستندات RAG

استفاده:
    python manage.py test_rag_documents
    python manage.py test_rag_documents --output test_output.json
"""

from django.core.management.base import BaseCommand
from assistant.generators.schema_tool_generator import SchemaToolGenerator
from django.conf import settings
import json
from pathlib import Path


class Command(BaseCommand):
    help = 'تست تولید مستندات RAG از Tools و بررسی ساختار Documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='مسیر فایل JSON خروجی (پیش‌فرض: assistant/generated/test_tool_documents.json)',
        )
        parser.add_argument(
            '--sample',
            type=int,
            default=3,
            help='تعداد نمونه Documents برای نمایش (پیش‌فرض: 3)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='نمایش جزئیات بیشتر',
        )

    def handle(self, *args, **options):
        output_file = options.get('output')
        sample_count = options.get('sample', 3)
        verbose = options.get('verbose', False)
        
        if not output_file:
            output_file = str(Path(settings.BASE_DIR) / 'assistant' / 'generated' / 'test_tool_documents.json')
        
        self.stdout.write(self.style.SUCCESS('🧪 تست تولید مستندات RAG از Tools'))
        self.stdout.write('='*80)
        
        # ایجاد generator
        self.stdout.write('\n1️⃣  ایجاد SchemaToolGenerator...')
        try:
            generator = SchemaToolGenerator()
            self.stdout.write(self.style.SUCCESS('   ✅ Generator ایجاد شد'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ خطا در ایجاد generator: {e}'))
            return
        
        # تولید Documents
        self.stdout.write('\n2️⃣  تولید Documents از Tools...')
        try:
            documents = generator.generate_tool_documents_for_rag(output_file)
            self.stdout.write(self.style.SUCCESS(f'   ✅ {len(documents)} Document تولید شد'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ خطا در تولید Documents: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
            return
        
        # بررسی ساختار
        self.stdout.write('\n3️⃣  بررسی ساختار Documents...')
        valid_count = 0
        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            tool_name = metadata.get('tool_name', 'unknown')
            
            # بررسی page_content
            if 'page_content' not in doc or not doc['page_content']:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Document #{i+1} ({tool_name}): page_content missing'))
                continue
            
            # بررسی metadata
            if 'metadata' not in doc:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Document #{i+1} ({tool_name}): metadata missing'))
                continue
            
            required_fields = ['tool_name', 'category', 'method', 'path']
            missing_fields = [f for f in required_fields if f not in doc['metadata']]
            if missing_fields:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Document #{i+1} ({tool_name}): missing fields: {missing_fields}'))
                continue
            
            valid_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ {valid_count}/{len(documents)} Documents معتبر'))
        
        # تحلیل محتوا
        self.stdout.write('\n4️⃣  تحلیل محتوای Documents...')
        analyses = []
        for doc in documents:
            page_content = doc.get('page_content', '')
            metadata = doc.get('metadata', {})
            
            analysis = {
                'tool_name': metadata.get('tool_name', 'unknown'),
                'content_length': len(page_content),
                'has_description': 'Description:' in page_content,
                'has_capabilities': 'قابلیت' in page_content or 'Capabilities' in page_content,
                'has_use_cases': 'سناریو' in page_content or 'Use Cases' in page_content,
                'has_parameters': 'پارامتر' in page_content or 'Parameters' in page_content,
                'has_examples': 'مثال' in page_content or 'Examples' in page_content,
                'has_notes': 'نکات' in page_content or 'Notes' in page_content,
                'has_endpoint': 'API Endpoint:' in page_content,
                'parameter_count': len(metadata.get('parameters', [])),
                'category': metadata.get('category', 'unknown'),
            }
            analyses.append(analysis)
        
        # آمار کلی
        avg_length = sum(a['content_length'] for a in analyses) / len(analyses) if analyses else 0
        has_all_sections = sum(
            1 for a in analyses 
            if a['has_description'] and a['has_parameters'] and a['has_examples']
        )
        
        self.stdout.write(f'   📊 میانگین طول محتوا: {avg_length:.0f} کاراکتر')
        self.stdout.write(f'   📊 Documents با تمام بخش‌ها: {has_all_sections}/{len(analyses)}')
        
        # دسته‌بندی
        categories = {}
        for a in analyses:
            cat = a['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        self.stdout.write(f'\n   📁 دسته‌بندی Documents:')
        for cat, count in sorted(categories.items()):
            self.stdout.write(f'      - {cat}: {count} tool')
        
        # نمایش نمونه‌ها
        if sample_count > 0:
            self.stdout.write(f'\n5️⃣  نمایش {sample_count} نمونه Document...')
            
            for i in range(min(sample_count, len(documents))):
                doc = documents[i]
                metadata = doc.get('metadata', {})
                page_content = doc.get('page_content', '')
                
                self.stdout.write('\n' + '-'*80)
                self.stdout.write(f'📄 نمونه Document #{i+1}')
                self.stdout.write('-'*80)
                self.stdout.write(f'🔧 Tool: {metadata.get("tool_name", "unknown")}')
                self.stdout.write(f'📁 Category: {metadata.get("category", "unknown")}')
                self.stdout.write(f'🌐 Method: {metadata.get("method", "unknown")}')
                self.stdout.write(f'📍 Path: {metadata.get("path", "unknown")}')
                self.stdout.write(f'📊 Parameters: {len(metadata.get("parameters", []))}')
                self.stdout.write(f'📝 Content Length: {len(page_content)} characters')
                
                if verbose:
                    self.stdout.write(f'\n📄 Content Preview (first 500 chars):')
                    self.stdout.write('-'*80)
                    preview = page_content[:500] + "..." if len(page_content) > 500 else page_content
                    self.stdout.write(preview)
                    self.stdout.write('-'*80)
        
        # تست LangChain
        self.stdout.write('\n6️⃣  تست آماده بودن برای LangChain...')
        try:
            from langchain_core.documents import Document
            
            langchain_docs = [
                Document(page_content=doc['page_content'], metadata=doc['metadata'])
                for doc in documents[:5]
            ]
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ {len(langchain_docs)} Document به فرمت LangChain تبدیل شد'))
            self.stdout.write(self.style.SUCCESS('   ✅ آماده برای استفاده در RAG pipeline'))
            
        except ImportError:
            self.stdout.write(self.style.WARNING('   ⚠️  langchain-core نصب نشده است'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ خطا: {e}'))
        
        # خلاصه
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('📊 خلاصه نتایج:'))
        self.stdout.write('='*80)
        self.stdout.write(f'✅ تعداد کل Documents: {len(documents)}')
        self.stdout.write(f'✅ Documents معتبر: {valid_count}/{len(documents)}')
        self.stdout.write(f'✅ میانگین طول محتوا: {avg_length:.0f} کاراکتر')
        self.stdout.write(f'✅ فایل خروجی: {output_file}')
        
        # پیشنهادات
        self.stdout.write('\n💡 پیشنهادات:')
        if avg_length < 300:
            self.stdout.write(self.style.WARNING('   ⚠️  میانگین طول محتوا کم است. بهتر است توضیحات بیشتری در ViewSets اضافه شود.'))
        if has_all_sections < len(analyses) * 0.8:
            self.stdout.write(self.style.WARNING('   ⚠️  برخی Documents بخش‌های مهم ندارند. docstring های ViewSets را تکمیل کنید.'))
        if valid_count < len(documents):
            self.stdout.write(self.style.WARNING('   ⚠️  برخی Documents ساختار نامعتبر دارند. بررسی کنید.'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ تست با موفقیت انجام شد!'))
