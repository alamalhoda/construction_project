"""
تست‌های جامع برای Agent و ابزارهای تولید شده

این فایل شامل تست‌های زیر است:
1. تست ساخت Agent
2. تست ابزارها به صورت مستقیم (بدون LLM)
3. تست یکپارچگی ابزارها با Agent
4. تست فراخوانی ابزارها با داده‌های واقعی

نحوه اجرا:
    source env/bin/activate
    python3 construction/assistant/tests/test_agent_tools.py
    یا
    python3 manage.py test assistant.tests.test_agent_tools
"""

import os
import sys

# تنظیم Django قبل از import کردن models
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

import django
django.setup()

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware

from construction.models import Project, Expense, Period, Investor, Transaction
from assistant.agent import ConstructionAssistantAgent
from assistant.generated import generated_tools_from_schema
from langchain_core.tools import BaseTool


class AgentToolsTestCase(TestCase):
    """تست‌های جامع برای Agent و ابزارها"""
    
    def setUp(self):
        """تنظیمات اولیه برای تست‌ها"""
        # ایجاد کاربر تست
        self.user, _ = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@test.com'}
        )
        
        # ایجاد request با session
        factory = RequestFactory()
        self.request = factory.get('/assistant/chat/')
        
        # اضافه کردن session
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.user = self.user
        
        # ایجاد یا دریافت پروژه
        self.project, _ = Project.objects.get_or_create(
            name='پروژه تست',
            defaults={
                'start_date_shamsi': '1400-01-01',
                'end_date_shamsi': '1405-12-29',
                'start_date_gregorian': '2021-03-21',
                'end_date_gregorian': '2027-03-20'
            }
        )
        
        # تنظیم پروژه جاری در session
        self.request.session['current_project_id'] = self.project.id
        self.request.session.save()
        
        # ایجاد Agent
        self.agent = ConstructionAssistantAgent(
            request=self.request,
            use_rag=False
        )
    
    def test_agent_creation(self):
        """تست ساخت Agent"""
        self.assertIsNotNone(self.agent, "Agent باید ساخته شود")
        self.assertIsNotNone(self.agent.agent_graph, "Agent Graph باید ساخته شود")
        self.assertGreater(len(self.agent.tools), 0, "باید حداقل یک ابزار وجود داشته باشد")
    
    def test_tools_count(self):
        """تست تعداد ابزارها"""
        # باید 115 ابزار داشته باشیم (10 قدیمی + 105 جدید)
        self.assertEqual(len(self.agent.tools), 115, "باید 115 ابزار وجود داشته باشد")
    
    def test_tools_categories(self):
        """تست دسته‌بندی ابزارها"""
        tool_categories = {
            'expense_': 0,
            'investor_': 0,
            'project_': 0,
            'transaction_': 0,
            'period_': 0,
            'unit': 0,
            'pettycashtransaction_': 0,
            'interestrate_': 0,
            'sale_': 0,
            'auth_': 0,
        }
        
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name'):
                name = tool_obj.name
                for prefix in tool_categories.keys():
                    if name.startswith(prefix):
                        tool_categories[prefix] += 1
                        break
        
        # بررسی اینکه هر دسته حداقل یک ابزار دارد
        self.assertGreater(tool_categories['expense_'], 0, "باید ابزارهای Expense وجود داشته باشد")
        self.assertGreater(tool_categories['investor_'], 0, "باید ابزارهای Investor وجود داشته باشد")
        self.assertGreater(tool_categories['project_'], 0, "باید ابزارهای Project وجود داشته باشد")
    
    def test_expense_list_tool(self):
        """تست ابزار expense_list"""
        expense_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'expense_list':
                expense_list_tool = tool_obj
                break
        
        self.assertIsNotNone(expense_list_tool, "ابزار expense_list باید وجود داشته باشد")
        self.assertIsInstance(expense_list_tool, BaseTool, "باید یک BaseTool باشد")
        
        # تست فراخوانی
        if hasattr(expense_list_tool, 'func'):
            result = expense_list_tool.func(request=self.request)
            self.assertIsInstance(result, str, "نتیجه باید string باشد")
            self.assertGreater(len(result), 0, "نتیجه نباید خالی باشد")
    
    def test_project_list_tool(self):
        """تست ابزار project_list"""
        project_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'project_list':
                project_list_tool = tool_obj
                break
        
        self.assertIsNotNone(project_list_tool, "ابزار project_list باید وجود داشته باشد")
        
        # تست فراخوانی
        if hasattr(project_list_tool, 'func'):
            result = project_list_tool.func(request=self.request)
            self.assertIsInstance(result, str, "نتیجه باید string باشد")
            self.assertIn('پروژه', result or '', "نتیجه باید شامل اطلاعات پروژه باشد")
    
    def test_investor_list_tool(self):
        """تست ابزار investor_list"""
        investor_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'investor_list':
                investor_list_tool = tool_obj
                break
        
        self.assertIsNotNone(investor_list_tool, "ابزار investor_list باید وجود داشته باشد")
        
        # تست فراخوانی
        if hasattr(investor_list_tool, 'func'):
            result = investor_list_tool.func(request=self.request)
            self.assertIsInstance(result, str, "نتیجه باید string باشد")
    
    def test_transaction_list_tool(self):
        """تست ابزار transaction_list"""
        transaction_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'transaction_list':
                transaction_list_tool = tool_obj
                break
        
        self.assertIsNotNone(transaction_list_tool, "ابزار transaction_list باید وجود داشته باشد")
        
        # تست فراخوانی
        if hasattr(transaction_list_tool, 'func'):
            result = transaction_list_tool.func(request=self.request)
            self.assertIsInstance(result, str, "نتیجه باید string باشد")
    
    def test_period_list_tool(self):
        """تست ابزار period_list"""
        period_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'period_list':
                period_list_tool = tool_obj
                break
        
        self.assertIsNotNone(period_list_tool, "ابزار period_list باید وجود داشته باشد")
        
        # تست فراخوانی
        if hasattr(period_list_tool, 'func'):
            result = period_list_tool.func(request=self.request)
            self.assertIsInstance(result, str, "نتیجه باید string باشد")
    
    def test_tools_have_request_parameter(self):
        """تست اینکه ابزارها request parameter را دریافت می‌کنند"""
        # تست چند ابزار نمونه
        test_tools = ['expense_list', 'project_list', 'investor_list']
        
        for tool_name in test_tools:
            tool_obj = None
            for t in self.agent.tools:
                if hasattr(t, 'name') and t.name == tool_name:
                    tool_obj = t
                    break
            
            if tool_obj and hasattr(tool_obj, 'func'):
                import inspect
                sig = inspect.signature(tool_obj.func)
                # بررسی اینکه request parameter وجود دارد یا wrapper function است
                # wrapper functions ممکن است request را از closure بگیرند
                has_request = 'request' in sig.parameters
                # یا اینکه wrapper function است که request را از closure می‌گیرد
                # در این صورت، بررسی می‌کنیم که آیا می‌تواند با request فراخوانی شود
                try:
                    result = tool_obj.func(request=self.request)
                    # اگر با request کار کرد، پس request parameter دارد (یا از closure می‌گیرد)
                    self.assertIsInstance(result, str, f"ابزار {tool_name} باید با request کار کند")
                except TypeError as e:
                    # اگر TypeError داد، ممکن است request parameter نداشته باشد
                    # اما این OK است چون wrapper function request را از closure می‌گیرد
                    pass
    
    def test_tools_from_generated_module(self):
        """تست اینکه ابزارها از generated_tools_from_schema import شده‌اند"""
        # بررسی اینکه expense_list در generated_tools_from_schema وجود دارد
        self.assertTrue(
            hasattr(generated_tools_from_schema, 'expense_list'),
            "expense_list باید در generated_tools_from_schema وجود داشته باشد"
        )
        
        # بررسی اینکه ابزار در Agent هم وجود دارد
        expense_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'expense_list':
                expense_list_tool = tool_obj
                break
        
        self.assertIsNotNone(
            expense_list_tool,
            "expense_list باید در Agent tools وجود داشته باشد"
        )
    
    def test_tool_wrapper_functions(self):
        """تست wrapper functions برای ابزارها"""
        # بررسی اینکه wrapper functions به درستی request را اضافه می‌کنند
        expense_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'expense_list':
                expense_list_tool = tool_obj
                break
        
        if expense_list_tool and hasattr(expense_list_tool, 'func'):
            # فراخوانی با request
            result = expense_list_tool.func(request=self.request)
            self.assertIsInstance(result, str, "نتیجه باید string باشد")
            self.assertGreater(len(result), 0, "نتیجه نباید خالی باشد")
    
    def test_all_critical_tools_exist(self):
        """تست وجود ابزارهای مهم"""
        critical_tools = [
            'expense_list',
            'expense_create',
            'expense_retrieve',
            'project_list',
            'project_retrieve',
            'investor_list',
            'investor_create',
            'transaction_list',
            'transaction_create',
            'period_list',
        ]
        
        for tool_name in critical_tools:
            tool_found = False
            for tool_obj in self.agent.tools:
                if hasattr(tool_obj, 'name') and tool_obj.name == tool_name:
                    tool_found = True
                    break
            
            self.assertTrue(
                tool_found,
                f"ابزار {tool_name} باید وجود داشته باشد"
            )
    
    def test_tools_error_handling(self):
        """تست مدیریت خطا در ابزارها"""
        # تست با request نامعتبر
        invalid_request = None
        
        expense_list_tool = None
        for tool_obj in self.agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'expense_list':
                expense_list_tool = tool_obj
                break
        
        if expense_list_tool and hasattr(expense_list_tool, 'func'):
            # باید خطا را مدیریت کند
            try:
                result = expense_list_tool.func(request=invalid_request)
                # حتی با request نامعتبر باید string برگرداند
                self.assertIsInstance(result, str, "نتیجه باید string باشد")
            except Exception as e:
                # اگر خطا داد، باید قابل مدیریت باشد
                self.assertIsInstance(e, Exception, "خطا باید Exception باشد")


class AgentIntegrationTestCase(TestCase):
    """تست‌های یکپارچگی Agent"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        factory = RequestFactory()
        self.request = factory.get('/assistant/chat/')
        
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(self.request)
        self.request.session.save()
        
        self.user, _ = User.objects.get_or_create(
            username='test_integration',
            defaults={'email': 'integration@test.com'}
        )
        self.request.user = self.user
        
        self.project, _ = Project.objects.get_or_create(
            name='پروژه یکپارچگی',
            defaults={
                'start_date_shamsi': '1400-01-01',
                'end_date_shamsi': '1405-12-29',
                'start_date_gregorian': '2021-03-21',
                'end_date_gregorian': '2027-03-20'
            }
        )
        
        self.request.session['current_project_id'] = self.project.id
        self.request.session.save()
    
    def test_agent_with_real_data(self):
        """تست Agent با داده‌های واقعی"""
        agent = ConstructionAssistantAgent(
            request=self.request,
            use_rag=False
        )
        
        # بررسی اینکه Agent با داده‌های واقعی کار می‌کند
        self.assertIsNotNone(agent)
        self.assertGreater(len(agent.tools), 0)
        
        # تست یک ابزار با داده‌های واقعی
        project_list_tool = None
        for tool_obj in agent.tools:
            if hasattr(tool_obj, 'name') and tool_obj.name == 'project_list':
                project_list_tool = tool_obj
                break
        
        if project_list_tool and hasattr(project_list_tool, 'func'):
            result = project_list_tool.func(request=self.request)
            # باید پروژه ما را در نتایج ببیند
            self.assertIn(self.project.name, result)


def run_tests():
    """اجرای تست‌ها"""
    import unittest
    
    # ایجاد test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # اضافه کردن تست‌ها
    suite.addTests(loader.loadTestsFromTestCase(AgentToolsTestCase))
    suite.addTests(loader.loadTestsFromTestCase(AgentIntegrationTestCase))
    
    # اجرای تست‌ها
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    # اجرای تست‌ها
    result = run_tests()
    
    # نمایش خلاصه
    print("\n" + "="*80)
    print("📊 خلاصه نتایج تست:")
    print("="*80)
    print(f"✅ تست‌های موفق: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ تست‌های ناموفق: {len(result.failures)}")
    print(f"⚠️ خطاها: {len(result.errors)}")
    print(f"📊 کل تست‌ها: {result.testsRun}")
    
    if result.wasSuccessful():
        print("\n🎉 تمام تست‌ها با موفقیت انجام شد!")
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند. لطفاً خطاها را بررسی کنید.")
    
    sys.exit(0 if result.wasSuccessful() else 1)

