"""
تولید خودکار Tools از Models, Views و Serializers
این ماژول از ViewSets، Serializers و Models برای تولید Tools استفاده می‌کند

این generator برای استفاده در هر پروژه Django قابل استفاده است.
"""

import os
import sys
import inspect
import importlib
from typing import List, Dict, Optional, Any
from pathlib import Path
import django

# تنظیم Django
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

django.setup()

from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from django.db import models as django_models
from django.conf import settings


class ModelToolGenerator:
    """
    کلاس برای تولید خودکار Tools از Models, Views و Serializers
    
    این کلاس برای استفاده در هر پروژه Django طراحی شده است.
    می‌تواند ViewSets را به صورت خودکار پیدا کند یا لیست ViewSets را دریافت کند.
    """
    
    def __init__(self, viewset_classes: Optional[List] = None, project_manager_module: Optional[str] = None):
        """
        Args:
            viewset_classes: لیست ViewSet classes (اختیاری - در صورت نبود، خودکار پیدا می‌شود)
            project_manager_module: مسیر ماژول ProjectManager (اختیاری - برای فیلتر کردن بر اساس project)
        """
        self.generated_tools = []
        self.serializer_cache = {}
        self.model_cache = {}
        self.viewset_classes = viewset_classes
        self.project_manager_module = project_manager_module
        self.project_manager_class = None
        
        # بارگذاری ProjectManager در صورت وجود
        if project_manager_module:
            try:
                module_path, class_name = project_manager_module.rsplit('.', 1)
                module = importlib.import_module(module_path)
                self.project_manager_class = getattr(module, class_name, None)
            except Exception:
                self.project_manager_class = None
    
    def analyze_viewset(self, viewset_class) -> List[Dict[str, Any]]:
        """
        تحلیل یک ViewSet و تولید Tools مناسب
        
        Args:
            viewset_class: کلاس ViewSet برای تحلیل
        
        Returns:
            لیست دیکشنری‌های حاوی اطلاعات Tool
        """
        tools = []
        
        # دریافت نام ViewSet
        viewset_name = viewset_class.__name__
        model_name = viewset_name.replace('ViewSet', '')
        
        # تحلیل actions استاندارد
        standard_actions = {
            'list': {
                'name': f'list_{model_name.lower()}s',
                'description': f'دریافت لیست {model_name}ها',
                'method': 'GET',
                'params': []
            },
            'retrieve': {
                'name': f'get_{model_name.lower()}',
                'description': f'دریافت اطلاعات یک {model_name}',
                'method': 'GET',
                'params': [{'name': 'id', 'type': 'int', 'required': True}]
            },
            'create': {
                'name': f'create_{model_name.lower()}',
                'description': f'ایجاد یک {model_name} جدید',
                'method': 'POST',
                'params': []
            },
            'update': {
                'name': f'update_{model_name.lower()}',
                'description': f'به‌روزرسانی یک {model_name}',
                'method': 'PUT',
                'params': [{'name': 'id', 'type': 'int', 'required': True}]
            },
            'destroy': {
                'name': f'delete_{model_name.lower()}',
                'description': f'حذف یک {model_name}',
                'method': 'DELETE',
                'params': [{'name': 'id', 'type': 'int', 'required': True}]
            }
        }
        
        # بررسی actions موجود در ViewSet
        for action_name, action_info in standard_actions.items():
            if hasattr(viewset_class, action_name):
                tools.append({
                    'type': 'standard',
                    'action': action_name,
                    **action_info
                })
        
        # تحلیل custom actions
        for attr_name in dir(viewset_class):
            attr = getattr(viewset_class, attr_name, None)
            if attr and hasattr(attr, 'mapping'):
                # این یک custom action است
                action_mapping = attr.mapping
                methods = list(action_mapping.keys())
                
                # دریافت docstring
                docstring = inspect.getdoc(attr) or f'Custom action {attr_name}'
                
                # تحلیل پارامترها
                sig = inspect.signature(attr)
                params = []
                for param_name, param in sig.parameters.items():
                    if param_name not in ['self', 'request', 'pk']:
                        param_type = 'str'
                        if param.annotation != inspect.Parameter.empty:
                            param_type = str(param.annotation).replace('typing.', '')
                        params.append({
                            'name': param_name,
                            'type': param_type,
                            'required': param.default == inspect.Parameter.empty
                        })
                
                tools.append({
                    'type': 'custom',
                    'action': attr_name,
                    'name': f'{attr_name}_{model_name.lower()}',
                    'description': docstring,
                    'method': methods[0] if methods else 'GET',
                    'params': params
                })
        
        return tools
    
    def discover_viewsets(self) -> List:
        """
        پیدا کردن خودکار ViewSets در پروژه
        
        Returns:
            لیست ViewSet classes
        """
        viewsets_list = []
        
        # جستجو در تمام apps نصب شده
        for app_config in django.apps.apps.get_app_configs():
            app_name = app_config.name
            
            # تلاش برای import کردن api module
            try:
                api_module = importlib.import_module(f'{app_name}.api')
                
                # پیدا کردن تمام ViewSets در این module
                for attr_name in dir(api_module):
                    # رد کردن private attributes و imports
                    if attr_name.startswith('_'):
                        continue
                    
                    attr = getattr(api_module, attr_name, None)
                    if inspect.isclass(attr) and 'ViewSet' in attr_name:
                        # بررسی اینکه ViewSet است (ViewSet یا ModelViewSet)
                        is_viewset = False
                        try:
                            # استفاده از MRO برای بررسی (چون ModelViewSet مستقیماً از ViewSet ارث‌بری نمی‌کند)
                            mro = getattr(attr, '__mro__', [])
                            if (viewsets.ViewSet in mro or viewsets.ModelViewSet in mro):
                                # رد کردن کلاس‌های پایه
                                if attr not in [viewsets.ViewSet, viewsets.GenericViewSet, 
                                               viewsets.ReadOnlyModelViewSet, viewsets.ModelViewSet]:
                                    is_viewset = True
                        except (TypeError, AttributeError):
                            pass
                        
                        # بررسی اینکه این ViewSet از api_module است (نه import شده)
                        if is_viewset:
                            module_name = getattr(attr, '__module__', '')
                            if module_name == api_module.__name__:
                                viewsets_list.append(attr)
            except (ImportError, AttributeError, TypeError) as e:
                # TypeError ممکن است برای issubclass رخ دهد
                continue
        
        return viewsets_list
    
    def analyze_serializer(self, serializer_class) -> Dict[str, Any]:
        """
        تحلیل یک Serializer و استخراج اطلاعات فیلدها
        
        Args:
            serializer_class: کلاس Serializer
        
        Returns:
            دیکشنری حاوی اطلاعات فیلدها
        """
        serializer_info = {
            'fields': [],
            'read_only_fields': [],
            'required_fields': [],
            'optional_fields': [],
            'nested_serializers': {}
        }
        
        # دریافت Meta
        meta = getattr(serializer_class, 'Meta', None)
        if meta:
            fields = getattr(meta, 'fields', [])
            read_only_fields = getattr(meta, 'read_only_fields', [])
            
            serializer_info['read_only_fields'] = list(read_only_fields)
            
            # تحلیل فیلدها
            for field_name in fields:
                if field_name in serializer_class._declared_fields:
                    field = serializer_class._declared_fields[field_name]
                    
                    field_info = {
                        'name': field_name,
                        'type': type(field).__name__,
                        'required': getattr(field, 'required', False),
                        'read_only': getattr(field, 'read_only', False),
                        'allow_null': getattr(field, 'allow_null', False),
                        'help_text': getattr(field, 'help_text', ''),
                        'label': getattr(field, 'label', field_name)
                    }
                    
                    # بررسی نوع فیلد
                    if isinstance(field, serializers.SerializerMethodField):
                        field_info['type'] = 'method'
                        field_info['read_only'] = True
                    elif isinstance(field, serializers.RelatedField):
                        field_info['type'] = 'related'
                        if hasattr(field, 'queryset'):
                            field_info['related_model'] = str(field.queryset.model.__name__)
                    
                    serializer_info['fields'].append(field_info)
                    
                    if field_info['required'] and not field_info['read_only']:
                        serializer_info['required_fields'].append(field_name)
                    elif not field_info['read_only']:
                        serializer_info['optional_fields'].append(field_name)
        
        return serializer_info
    
    def analyze_model(self, model_class) -> Dict[str, Any]:
        """
        تحلیل یک Model و استخراج اطلاعات فیلدها
        
        Args:
            model_class: کلاس Model
        
        Returns:
            دیکشنری حاوی اطلاعات فیلدها
        """
        model_info = {
            'name': model_class.__name__,
            'fields': [],
            'relationships': [],
            'choices': {},
            'verbose_names': {}
        }
        
        # دریافت تمام فیلدها
        for field in model_class._meta.get_fields():
            field_info = {
                'name': field.name,
                'type': type(field).__name__,
                'verbose_name': getattr(field, 'verbose_name', field.name),
                'help_text': getattr(field, 'help_text', ''),
                'null': getattr(field, 'null', False),
                'blank': getattr(field, 'blank', False),
                'default': getattr(field, 'default', None),
                'max_length': getattr(field, 'max_length', None),
                'choices': None
            }
            
            # بررسی نوع فیلد
            try:
                if isinstance(field, django_models.ForeignKey):
                    field_info['related_model'] = field.related_model.__name__
                    if hasattr(field, 'on_delete'):
                        field_info['on_delete'] = str(field.on_delete)
                    model_info['relationships'].append({
                        'name': field.name,
                        'type': 'ForeignKey',
                        'related_model': field.related_model.__name__
                    })
                elif isinstance(field, django_models.ManyToManyField):
                    field_info['related_model'] = field.related_model.__name__
                    model_info['relationships'].append({
                        'name': field.name,
                        'type': 'ManyToMany',
                        'related_model': field.related_model.__name__
                    })
                elif isinstance(field, django_models.CharField):
                    if hasattr(field, 'choices') and field.choices:
                        field_info['choices'] = dict(field.choices)
                        model_info['choices'][field.name] = dict(field.choices)
            except Exception:
                # در صورت خطا، ادامه بده
                pass
            
            model_info['fields'].append(field_info)
            model_info['verbose_names'][field.name] = field_info['verbose_name']
        
        return model_info
    
    def get_viewset_info(self, viewset_class) -> Dict[str, Any]:
        """
        دریافت اطلاعات کامل ViewSet شامل Serializer و Model
        
        Args:
            viewset_class: کلاس ViewSet
        
        Returns:
            دیکشنری حاوی اطلاعات کامل
        """
        info = {
            'viewset': viewset_class.__name__,
            'serializer': None,
            'model': None,
            'serializer_info': None,
            'model_info': None,
            'permissions': [],
            'authentication': []
        }
        
        # دریافت Serializer
        serializer_class = getattr(viewset_class, 'serializer_class', None)
        if serializer_class:
            info['serializer'] = serializer_class.__name__
            info['serializer_info'] = self.analyze_serializer(serializer_class)
            
            # دریافت Model از Serializer
            meta = getattr(serializer_class, 'Meta', None)
            if meta:
                model_class = getattr(meta, 'model', None)
                if model_class:
                    info['model'] = model_class.__name__
                    info['model_info'] = self.analyze_model(model_class)
        
        # دریافت Permissions
        permission_classes = getattr(viewset_class, 'permission_classes', [])
        info['permissions'] = [cls.__name__ for cls in permission_classes]
        
        # دریافت Authentication
        authentication_classes = getattr(viewset_class, 'authentication_classes', [])
        info['authentication'] = [cls.__name__ for cls in authentication_classes]
        
        return info
    
    def _map_serializer_field_type(self, field_type: str) -> str:
        """تبدیل نوع فیلد Serializer به نوع Python"""
        mapping = {
            'CharField': 'str',
            'IntegerField': 'int',
            'DecimalField': 'float',
            'FloatField': 'float',
            'BooleanField': 'bool',
            'DateField': 'str',
            'DateTimeField': 'str',
            'EmailField': 'str',
            'URLField': 'str',
            'TextField': 'str',
            'related': 'int',  # ForeignKey
            'nested': 'dict'
        }
        return mapping.get(field_type, 'str')
    
    def generate_enhanced_tool_code(self, tool_info: Dict[str, Any], viewset_info: Optional[Dict[str, Any]] = None) -> str:
        """
        تولید کد Tool با استفاده از اطلاعات Serializer و Model
        
        Args:
            tool_info: اطلاعات Tool
            viewset_info: اطلاعات ViewSet (شامل Serializer و Model)
        
        Returns:
            کد Python برای Tool
        """
        tool_name = tool_info['name']
        description = tool_info['description']
        params = tool_info.get('params', [])
        
        # استفاده از اطلاعات Serializer برای بهبود params
        if viewset_info and viewset_info.get('serializer_info'):
            serializer_info = viewset_info['serializer_info']
            
            # اگر params خالی است، از serializer استفاده کن
            if not params and tool_info.get('action') == 'create':
                for field in serializer_info['fields']:
                    if not field['read_only']:
                        params.append({
                            'name': field['name'],
                            'type': self._map_serializer_field_type(field['type']),
                            'required': field['required'],
                            'description': field.get('help_text', '') or field.get('label', '')
                        })
        
        # ساخت signature - جدا کردن required و optional
        required_params = []
        optional_params = []
        param_docs = []
        
        for param in params:
            param_name = param['name']
            param_type = param['type']
            required = param.get('required', True)
            param_desc = param.get('description', '')
            
            # تبدیل نوع
            if param_type == 'int' or 'Integer' in param_type:
                type_hint = 'int'
            elif param_type == 'float' or 'Decimal' in param_type or 'Float' in param_type:
                type_hint = 'float'
            elif param_type == 'bool' or 'Boolean' in param_type:
                type_hint = 'bool'
            elif param_type == 'list' or 'Array' in param_type:
                type_hint = 'list'
            else:
                type_hint = 'str'
            
            # جدا کردن required و optional
            if not required:
                optional_params.append(f"{param_name}: Optional[{type_hint}] = None")
            else:
                required_params.append(f"{param_name}: {type_hint}")
            
            # ساخت docstring برای param
            param_doc = f"        {param_name}: {type_hint}"
            if param_desc:
                param_doc += f" - {param_desc}"
            if not required:
                param_doc += " (اختیاری)"
            param_docs.append(param_doc)
        
        # ترکیب: ابتدا required، سپس optional، سپس request
        param_signatures = required_params + optional_params
        param_signatures.append("request=None")
        
        signature = ", ".join(param_signatures)
        
        # ساخت docstring با اطلاعات بیشتر
        docstring_parts = [f"    {description}"]
        
        if viewset_info:
            if viewset_info.get('model_info'):
                model_name = viewset_info['model_info']['name']
                docstring_parts.append(f"    ")
                docstring_parts.append(f"    این Tool با مدل {model_name} کار می‌کند.")
            
            if viewset_info.get('permissions'):
                docstring_parts.append(f"    ")
                docstring_parts.append(f"    نیاز به دسترسی: {', '.join(viewset_info['permissions'])}")
        
        docstring_parts.append(f"    ")
        docstring_parts.append(f"    Args:")
        if param_docs:
            docstring_parts.extend(param_docs)
        else:
            docstring_parts.append("        (بدون پارامتر)")
        docstring_parts.append(f"        request: درخواست HTTP برای دریافت پروژه جاری (برای استفاده داخلی)")
        docstring_parts.append(f"    ")
        docstring_parts.append(f"    Returns:")
        docstring_parts.append(f"        نتیجه عملیات به صورت رشته متنی")
        
        docstring = '\n'.join(docstring_parts)
        
        # ساخت body با استفاده از اطلاعات Model
        body = self._generate_tool_body(tool_info, viewset_info)
        
        code = f'''@tool
def {tool_name}({signature}) -> str:
    """{docstring}
    """
{body}
'''
        
        return code
    
    def _generate_tool_body(self, tool_info: Dict[str, Any], viewset_info: Optional[Dict[str, Any]] = None) -> str:
        """تولید body برای Tool با استفاده از اطلاعات Model"""
        action_type = tool_info.get('type', 'standard')
        action = tool_info.get('action', '')
        params = tool_info.get('params', [])
        
        if action_type == 'standard':
            if action == 'list':
                return self._generate_list_body(viewset_info)
            elif action == 'retrieve':
                return self._generate_retrieve_body(params, viewset_info)
            elif action == 'create':
                return self._generate_create_body(params, viewset_info)
            elif action == 'update':
                return self._generate_update_body(params, viewset_info)
            elif action == 'destroy':
                return self._generate_delete_body(params, viewset_info)
        
        return self._generate_default_body(tool_info)
    
    def _generate_list_body(self, viewset_info: Optional[Dict[str, Any]]) -> str:
        """تولید body برای list action"""
        model_name = viewset_info['model_info']['name'] if viewset_info and viewset_info.get('model_info') else 'Item'
        
        # ساخت import statement برای model
        model_import = self._get_model_import(model_name)
        
        # ساخت کد برای دریافت project (در صورت وجود ProjectManager)
        project_code = ""
        project_filter = ""
        if self.project_manager_class:
            project_code = f'''        # دریافت پروژه جاری
        project = None
        if request:
            from {self.project_manager_module} import {self.project_manager_class.__name__}
            project = {self.project_manager_class.__name__}.get_current_project(request)
            if not project:
                return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        '''
            project_filter = "\n        if project:\n            items = items.filter(project=project)"
        
        return f'''    try:
{project_code}        # دریافت لیست {model_name}ها
{model_import}
        items = {model_name}.objects.all(){project_filter}
        
        if not items.exists():
            return f"📭 هیچ {model_name}ی یافت نشد."
        
        result = f"📋 لیست {model_name}ها ({{items.count()}} مورد):\\n\\n"
        for item in items[:20]:  # محدود به 20 مورد اول
            result += f"  • #{{item.id}}: {{str(item)}}\\n"
        
        return result
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
    
    def _generate_retrieve_body(self, params: List[Dict], viewset_info: Optional[Dict[str, Any]]) -> str:
        """تولید body برای retrieve action"""
        model_name = viewset_info['model_info']['name'] if viewset_info and viewset_info.get('model_info') else 'Item'
        id_param = next((p for p in params if p['name'] == 'id'), {'name': 'id'})
        
        return f'''    try:
        # دریافت {model_name} با شناسه
        from construction.models import {model_name}
        item = {model_name}.objects.get(id={id_param['name']})
        
        result = f"📋 اطلاعات {model_name} #{{item.id}}:\\n"
        result += f"{{str(item)}}\\n"
        
        return result
    except {model_name}.DoesNotExist:
        return f"❌ خطا: {model_name} با شناسه {{id}} یافت نشد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
    
    def _generate_create_body(self, params: List[Dict], viewset_info: Optional[Dict[str, Any]]) -> str:
        """تولید body برای create action"""
        model_name = viewset_info['model_info']['name'] if viewset_info and viewset_info.get('model_info') else 'Item'
        
        # ساخت data dict
        data_lines = ["        data = {}"]
        for param in params:
            if param['name'] != 'request':
                data_lines.append(f"        if {param['name']} is not None:")
                data_lines.append(f"            data['{param['name']}'] = {param['name']}")
        
        model_import = self._get_model_import(model_name)
        
        # ساخت کد برای دریافت project
        project_code = ""
        project_assign = ""
        if self.project_manager_class:
            project_code = f'''        # دریافت پروژه جاری
        project = None
        if request:
            from {self.project_manager_module} import {self.project_manager_class.__name__}
            project = {self.project_manager_class.__name__}.get_current_project(request)
            if not project:
                return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        '''
            project_assign = "\n        if project:\n            data['project'] = project"
        
        return f'''    try:
{project_code}        # ساخت داده‌ها
{chr(10).join(data_lines)}{project_assign}
        
        # ایجاد {model_name} جدید
{model_import}
        item = {model_name}.objects.create(**data)
        
        return f"✅ {model_name} با موفقیت ایجاد شد!\\n" \\
               f"📋 شناسه: #{{item.id}}\\n" \\
               f"{{str(item)}}"
    except Exception as e:
        return f"❌ خطا در ایجاد {model_name}: {{str(e)}}"'''
    
    def _generate_update_body(self, params: List[Dict], viewset_info: Optional[Dict[str, Any]]) -> str:
        """تولید body برای update action"""
        model_name = viewset_info['model_info']['name'] if viewset_info and viewset_info.get('model_info') else 'Item'
        id_param = next((p for p in params if p['name'] == 'id'), {'name': 'id'})
        
        # ساخت data dict (بدون id)
        data_lines = ["        data = {}"]
        for param in params:
            if param['name'] not in ['request', 'id']:
                data_lines.append(f"        if {param['name']} is not None:")
                data_lines.append(f"            data['{param['name']}'] = {param['name']}")
        
        model_import = self._get_model_import(model_name)
        
        return f'''    try:
        # دریافت {model_name} با شناسه
{model_import}
        item = {model_name}.objects.get(id={id_param['name']})
        
        # به‌روزرسانی داده‌ها
{chr(10).join(data_lines)}
        
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        
        return f"✅ {model_name} با موفقیت به‌روزرسانی شد!\\n" \\
               f"📋 شناسه: #{{item.id}}\\n" \\
               f"{{str(item)}}"
    except {model_name}.DoesNotExist:
        return f"❌ خطا: {model_name} با شناسه {{id}} یافت نشد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
    
    def _generate_delete_body(self, params: List[Dict], viewset_info: Optional[Dict[str, Any]]) -> str:
        """تولید body برای delete action"""
        model_name = viewset_info['model_info']['name'] if viewset_info and viewset_info.get('model_info') else 'Item'
        id_param = next((p for p in params if p['name'] == 'id'), {'name': 'id'})
        
        model_import = self._get_model_import(model_name)
        
        return f'''    try:
        # دریافت و حذف {model_name}
{model_import}
        item = {model_name}.objects.get(id={id_param['name']})
        item_id = item.id
        item_str = str(item)
        item.delete()
        
        return f"✅ {model_name} با موفقیت حذف شد!\\n" \\
               f"📋 شناسه حذف شده: #{{item_id}}\\n" \\
               f"{{item_str}}"
    except {model_name}.DoesNotExist:
        return f"❌ خطا: {model_name} با شناسه {{id}} یافت نشد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
    
    def _generate_default_body(self, tool_info: Dict[str, Any]) -> str:
        """تولید body پیش‌فرض"""
        return f'''    try:
        # TODO: پیاده‌سازی منطق {tool_info.get('action', 'custom action')}
        return f"✅ عملیات با موفقیت انجام شد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
    
    def _get_model_import(self, model_name: str) -> str:
        """
        پیدا کردن مسیر import برای یک Model
        
        Args:
            model_name: نام Model
        
        Returns:
            رشته import statement
        """
        # جستجو در تمام apps
        for app_config in django.apps.apps.get_app_configs():
            app_name = app_config.name
            
            try:
                models_module = importlib.import_module(f'{app_name}.models')
                if hasattr(models_module, model_name):
                    return f"        from {app_name}.models import {model_name}"
            except (ImportError, AttributeError):
                continue
        
        # اگر پیدا نشد، از construction.models استفاده کن (fallback)
        return f"        from construction.models import {model_name}"
    
    def generate_all_tools(self, output_file: Optional[str] = None) -> str:
        """
        تولید Tools برای تمام ViewSets
        
        Args:
            output_file: مسیر فایل خروجی (اختیاری)
        
        Returns:
            کد کامل تمام Tools
        """
        # پیدا کردن ViewSets
        if not self.viewset_classes:
            print("🔍 در حال پیدا کردن خودکار ViewSets...")
            self.viewset_classes = self.discover_viewsets()
            if not self.viewset_classes:
                print("⚠️  هیچ ViewSet یافت نشد. لطفاً ViewSets را به صورت دستی مشخص کنید.")
                return ""
        
        # ساخت imports
        imports_set = set()
        for viewset_class in self.viewset_classes:
            viewset_info = self.get_viewset_info(viewset_class)
            if viewset_info.get('model'):
                model_name = viewset_info['model']
                model_import = self._get_model_import(model_name)
                # استخراج from statement
                if 'from ' in model_import:
                    imports_set.add(model_import.strip())
        
        imports_code = '\n'.join(sorted(imports_set)) if imports_set else "# No models found"
        
        if self.project_manager_module:
            pm_import = f"from {self.project_manager_module} import {self.project_manager_class.__name__ if self.project_manager_class else 'ProjectManager'}"
        else:
            pm_import = "# ProjectManager not configured"
        
        all_code = f'''"""
Tools تولید شده خودکار از ViewSets, Serializers و Models
این فایل به صورت خودکار از ViewSets و Models تولید شده است.

✅ منابع استفاده شده:
   - ViewSets: {len(self.viewset_classes)} ViewSet پیدا شده
   - Serializers: از ViewSets استخراج شده
   - Models: از Serializers استخراج شده

⚠️  توجه: این Tools نیاز به بررسی و تکمیل دارند.
"""

from langchain.tools import tool
from typing import Optional
{imports_code}
{pm_import}

'''
        
        total_tools = 0
        total_viewsets = len(self.viewset_classes)
        
        for viewset_class in self.viewset_classes:
            tools = self.analyze_viewset(viewset_class)
            viewset_name = viewset_class.__name__
            
            # دریافت اطلاعات کامل ViewSet
            viewset_info = self.get_viewset_info(viewset_class)
            
            all_code += f"\n# ===== Tools for {viewset_name} =====\n"
            if viewset_info.get('model'):
                all_code += f"# Model: {viewset_info['model']}\n"
            if viewset_info.get('serializer'):
                all_code += f"# Serializer: {viewset_info['serializer']}\n"
            all_code += "\n"
            
            for tool_info in tools:
                # استفاده از متد بهبود یافته
                tool_code = self.generate_enhanced_tool_code(tool_info, viewset_info)
                all_code += tool_code + "\n"
                total_tools += 1
        
        # ذخیره در فایل
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(all_code)
            print(f"✅ Tools در فایل {output_file} ذخیره شد")
            print(f"\n📊 خلاصه:")
            print(f"   - تعداد ViewSets تحلیل شده: {total_viewsets}")
            print(f"   - تعداد کل Tools تولید شده: {total_tools}")
        
        return all_code


def main():
    """تابع اصلی برای اجرای model-based generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='تولید خودکار Tools از ViewSets, Serializers و Models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌ها:
  # استفاده پیش‌فرض (auto-discovery)
  python model_tool_generator.py --output generated_tools_from_models.py
  
  # با ProjectManager
  python model_tool_generator.py --project-manager construction.project_manager.ProjectManager
  
  # با ViewSets مشخص
  python model_tool_generator.py --viewsets construction.api.ExpenseViewSet,construction.api.InvestorViewSet
        """
    )
    parser.add_argument('--output', type=str, default=None,
                       help='مسیر فایل خروجی (پیش‌فرض: generated_tools_from_models.py)')
    parser.add_argument('--project-manager', type=str, default=None,
                       help='مسیر ماژول ProjectManager (مثال: construction.project_manager.ProjectManager)')
    parser.add_argument('--viewsets', type=str, default=None,
                       help='لیست ViewSets با کاما جدا شده (مثال: construction.api.ExpenseViewSet,construction.api.InvestorViewSet)')
    
    args = parser.parse_args()
    
    # پردازش ViewSets
    viewset_classes = None
    if args.viewsets:
        viewset_classes = []
        for vs_path in args.viewsets.split(','):
            vs_path = vs_path.strip()
            try:
                module_path, class_name = vs_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                viewset_class = getattr(module, class_name)
                viewset_classes.append(viewset_class)
            except Exception as e:
                print(f"⚠️  خطا در بارگذاری ViewSet {vs_path}: {e}")
    
    generator = ModelToolGenerator(
        viewset_classes=viewset_classes,
        project_manager_module=args.project_manager
    )
    
    if not args.output:
        args.output = str(project_root / 'construction' / 'assistant' / 'generated' / 'generated_tools_from_models.py')
    
    print("🔧 در حال تولید Tools از ViewSets, Serializers و Models...")
    if viewset_classes:
        print(f"   ✅ استفاده از {len(viewset_classes)} ViewSet مشخص شده")
    else:
        print("   ✅ پیدا کردن خودکار ViewSets")
    print("   ✅ استفاده از Serializers برای استخراج فیلدها")
    print("   ✅ استفاده از Models برای تولید body")
    if args.project_manager:
        print(f"   ✅ استفاده از ProjectManager: {args.project_manager}")
    print()
    
    code = generator.generate_all_tools(output_file=args.output)
    
    print(f"\n📁 فایل خروجی: {args.output}")
    print("\n⚠️  توجه: این Tools به صورت خودکار تولید شده‌اند و نیاز به بررسی و تکمیل دارند.")


if __name__ == "__main__":
    main()

