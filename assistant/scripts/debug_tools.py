"""
اسکریپت برای مشاهده اطلاعات ابزارهایی که به AI معرفی می‌شوند
"""

import os
import sys
import django

# اضافه کردن مسیر پروژه به Python path
# از assistant/scripts/ به ریشه پروژه می‌رویم
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from assistant.agent import ConstructionAssistantAgent
from langchain.tools import tool
import json


def show_tools_info():
    """نمایش اطلاعات ابزارها"""
    
    # ایجاد یک Agent نمونه (بدون request)
    agent = ConstructionAssistantAgent(use_rag=False)
    
    print("=" * 80)
    print("🔧 ابزارهای معرفی شده به AI:")
    print("=" * 80)
    print()
    
    for i, tool_obj in enumerate(agent.tools, 1):
        print(f"{i}. {tool_obj.name}")
        print(f"   📝 توضیحات: {tool_obj.description}")
        print(f"   📋 Schema: {json.dumps(tool_obj.args_schema.schema() if hasattr(tool_obj, 'args_schema') and tool_obj.args_schema else {}, indent=2, ensure_ascii=False)}")
        print()
    
    print("=" * 80)
    print(f"📊 مجموع ابزارها: {len(agent.tools)}")
    print("=" * 80)
    
    # نمایش جزئیات یک ابزار نمونه
    if agent.tools:
        print("\n" + "=" * 80)
        print("📖 جزئیات یک ابزار نمونه (get_expense_stats_tool):")
        print("=" * 80)
        sample_tool = None
        for t in agent.tools:
            if 'expense_stats' in t.name.lower():
                sample_tool = t
                break
        
        if sample_tool:
            print(f"\nنام ابزار: {sample_tool.name}")
            print(f"\nتوضیحات: {sample_tool.description}")
            
            # نمایش schema کامل
            if hasattr(sample_tool, 'args_schema'):
                print(f"\nSchema کامل:")
                print(json.dumps(sample_tool.args_schema.schema(), indent=2, ensure_ascii=False))
            
            # نمایش JSON schema که به LLM ارسال می‌شود
            print(f"\nJSON Schema که به LLM ارسال می‌شود:")
            try:
                # LangChain tools معمولاً یک متد برای تبدیل به dict دارند
                if hasattr(sample_tool, 'dict'):
                    tool_dict = sample_tool.dict()
                    print(json.dumps(tool_dict, indent=2, ensure_ascii=False))
                elif hasattr(sample_tool, 'schema'):
                    print(json.dumps(sample_tool.schema(), indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"خطا در نمایش schema: {e}")


if __name__ == "__main__":
    show_tools_info()

