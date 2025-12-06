#!/usr/bin/env python
"""
اسکریپت تست برای بررسی خروجی generate_tool_documents_for_rag

این اسکریپت:
1. مستندات RAG را از tools تولید می‌کند
2. ساختار و محتوای Documents را بررسی می‌کند
3. نمونه‌ای از Documents را نمایش می‌دهد
4. آماده بودن برای استفاده در RAG pipeline را تست می‌کند
"""

import os
import sys
import json
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path (همان روش schema_tool_generator.py)
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# دریافت settings module از environment یا استفاده از پیش‌فرض
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
if not settings_module:
    # تلاش برای پیدا کردن settings module
    if (project_root / 'construction_project' / 'settings.py').exists():
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
    else:
        # پیدا کردن اولین settings.py
        for settings_file in project_root.rglob('settings.py'):
            relative_path = settings_file.relative_to(project_root)
            module_path = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', module_path)
            break

try:
    import django
    django.setup()
except Exception as e:
    print(f"⚠️  Warning: Django setup failed: {e}")
    print("   Continuing without Django setup...")

from assistant.generators.schema_tool_generator import SchemaToolGenerator


def validate_document_structure(doc: dict) -> tuple[bool, list]:
    """
    بررسی ساختار Document
    
    Returns:
        (is_valid, errors)
    """
    errors = []
    
    # بررسی وجود page_content
    if 'page_content' not in doc:
        errors.append("❌ page_content missing")
    elif not doc['page_content']:
        errors.append("❌ page_content is empty")
    elif len(doc['page_content']) < 50:
        errors.append(f"⚠️  page_content too short ({len(doc['page_content'])} chars)")
    
    # بررسی وجود metadata
    if 'metadata' not in doc:
        errors.append("❌ metadata missing")
    else:
        metadata = doc['metadata']
        required_fields = ['tool_name', 'category', 'method', 'path']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"❌ metadata.{field} missing")
    
    return len(errors) == 0, errors


def analyze_document_content(doc: dict) -> dict:
    """تحلیل محتوای Document"""
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
        'method': metadata.get('method', 'unknown'),
    }
    
    return analysis


def print_document_sample(doc: dict, index: int = 0):
    """نمایش نمونه Document"""
    print("\n" + "="*80)
    print(f"📄 نمونه Document #{index + 1}")
    print("="*80)
    
    metadata = doc.get('metadata', {})
    print(f"\n🔧 Tool: {metadata.get('tool_name', 'unknown')}")
    print(f"📁 Category: {metadata.get('category', 'unknown')}")
    print(f"🌐 Method: {metadata.get('method', 'unknown')}")
    print(f"📍 Path: {metadata.get('path', 'unknown')}")
    print(f"🏷️  Tags: {', '.join(metadata.get('tags', []))}")
    print(f"🔐 Auth Required: {metadata.get('has_auth', False)}")
    print(f"📊 Parameters: {len(metadata.get('parameters', []))}")
    
    page_content = doc.get('page_content', '')
    print(f"\n📝 Content Length: {len(page_content)} characters")
    print(f"\n📄 Content Preview (first 500 chars):")
    print("-" * 80)
    print(page_content[:500] + "..." if len(page_content) > 500 else page_content)
    print("-" * 80)


def test_rag_documents_generation():
    """تست اصلی تولید Documents"""
    print("🧪 تست تولید مستندات RAG از Tools")
    print("="*80)
    
    # ایجاد generator
    print("\n1️⃣  ایجاد SchemaToolGenerator...")
    try:
        generator = SchemaToolGenerator()
        print("   ✅ Generator ایجاد شد")
    except Exception as e:
        print(f"   ❌ خطا در ایجاد generator: {e}")
        return False
    
    # تولید Documents
    print("\n2️⃣  تولید Documents از Tools...")
    try:
        output_file = project_root / 'assistant' / 'generated' / 'test_tool_documents.json'
        documents = generator.generate_tool_documents_for_rag(str(output_file))
        print(f"   ✅ {len(documents)} Document تولید شد")
    except Exception as e:
        print(f"   ❌ خطا در تولید Documents: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # بررسی ساختار
    print("\n3️⃣  بررسی ساختار Documents...")
    validation_results = []
    for i, doc in enumerate(documents):
        is_valid, errors = validate_document_structure(doc)
        validation_results.append((is_valid, errors))
        if not is_valid:
            print(f"   ⚠️  Document #{i+1} ({doc.get('metadata', {}).get('tool_name', 'unknown')}):")
            for error in errors:
                print(f"      {error}")
    
    valid_count = sum(1 for is_valid, _ in validation_results if is_valid)
    print(f"   ✅ {valid_count}/{len(documents)} Documents معتبر")
    
    # تحلیل محتوا
    print("\n4️⃣  تحلیل محتوای Documents...")
    analyses = [analyze_document_content(doc) for doc in documents]
    
    # آمار کلی
    avg_length = sum(a['content_length'] for a in analyses) / len(analyses) if analyses else 0
    has_all_sections = sum(
        1 for a in analyses 
        if a['has_description'] and a['has_parameters'] and a['has_examples']
    )
    
    print(f"   📊 میانگین طول محتوا: {avg_length:.0f} کاراکتر")
    print(f"   📊 Documents با تمام بخش‌ها: {has_all_sections}/{len(analyses)}")
    
    # دسته‌بندی
    categories = {}
    for a in analyses:
        cat = a['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n   📁 دسته‌بندی Documents:")
    for cat, count in sorted(categories.items()):
        print(f"      - {cat}: {count} tool")
    
    # نمایش نمونه‌ها
    print("\n5️⃣  نمایش نمونه Documents...")
    
    # نمونه اول: اولین tool
    if documents:
        print_document_sample(documents[0], 0)
    
    # نمونه دوم: یک tool با بیشترین محتوا
    if len(documents) > 1:
        max_content_doc = max(documents, key=lambda d: len(d.get('page_content', '')))
        max_index = documents.index(max_content_doc)
        print_document_sample(max_content_doc, max_index)
    
    # نمونه سوم: یک tool از دسته‌بندی مختلف
    if len(documents) > 2:
        first_category = analyses[0]['category']
        different_doc = next(
            (doc for doc, a in zip(documents, analyses) if a['category'] != first_category),
            None
        )
        if different_doc:
            diff_index = documents.index(different_doc)
            print_document_sample(different_doc, diff_index)
    
    # تست آماده بودن برای LangChain
    print("\n6️⃣  تست آماده بودن برای LangChain...")
    try:
        from langchain_core.documents import Document
        
        langchain_docs = [
            Document(page_content=doc['page_content'], metadata=doc['metadata'])
            for doc in documents[:5]  # فقط 5 مورد اول برای تست
        ]
        
        print(f"   ✅ {len(langchain_docs)} Document به فرمت LangChain تبدیل شد")
        print(f"   ✅ آماده برای استفاده در RAG pipeline")
        
        # نمایش نمونه LangChain Document
        if langchain_docs:
            print(f"\n   📄 نمونه LangChain Document:")
            print(f"      - page_content length: {len(langchain_docs[0].page_content)}")
            print(f"      - metadata keys: {list(langchain_docs[0].metadata.keys())}")
        
    except ImportError:
        print("   ⚠️  langchain-core نصب نشده است (برای تست کامل نیاز است)")
    except Exception as e:
        print(f"   ❌ خطا در تبدیل به LangChain Document: {e}")
    
    # خلاصه
    print("\n" + "="*80)
    print("📊 خلاصه نتایج:")
    print("="*80)
    print(f"✅ تعداد کل Documents: {len(documents)}")
    print(f"✅ Documents معتبر: {valid_count}/{len(documents)}")
    print(f"✅ میانگین طول محتوا: {avg_length:.0f} کاراکتر")
    print(f"✅ فایل خروجی: {output_file}")
    print(f"✅ آماده برای استفاده در RAG pipeline")
    
    # پیشنهادات
    print("\n💡 پیشنهادات:")
    if avg_length < 300:
        print("   ⚠️  میانگین طول محتوا کم است. بهتر است توضیحات بیشتری در ViewSets اضافه شود.")
    if has_all_sections < len(analyses) * 0.8:
        print("   ⚠️  برخی Documents بخش‌های مهم ندارند. docstring های ViewSets را تکمیل کنید.")
    if valid_count < len(documents):
        print("   ⚠️  برخی Documents ساختار نامعتبر دارند. بررسی کنید.")
    
    print("\n✅ تست با موفقیت انجام شد!")
    return True


def main():
    """تابع اصلی"""
    try:
        success = test_rag_documents_generation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تست توسط کاربر متوقف شد")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
