"""
ابزار برای تولید خودکار Tools از Views و APIs
این ماژول می‌تواند ViewSets و API endpoints را تحلیل کند و Tools مناسب برای AI تولید کند
"""

import os
import sys
import inspect
import ast
from typing import List, Dict, Optional, Any
from pathlib import Path
import django

# تنظیم Django
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from rest_framework import viewsets
from rest_framework.decorators import action
from django.db import models as django_models
from django.core.exceptions import FieldDoesNotExist
from construction import api, views, serializers
from construction.models import Expense, Period, Investor, Project


class ToolGenerator:
    """کلاس برای تولید خودکار Tools از Views و APIs"""
    
    def __init__(self):
        self.generated_tools = []
        self.serializer_cache = {}
        self.model_cache = {}
    
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
    
    def generate_tool_code(self, tool_info: Dict[str, Any], viewset_name: str) -> str:
        """
        تولید کد Python برای یک Tool
        
        Args:
            tool_info: اطلاعات Tool
            viewset_name: نام ViewSet
        
        Returns:
            کد Python برای Tool
        """
        tool_name = tool_info['name']
        description = tool_info['description']
        params = tool_info.get('params', [])
        
        # ساخت signature
        param_signatures = []
        param_docs = []
        
        for param in params:
            param_name = param['name']
            param_type = param['type']
            required = param.get('required', True)
            
            if param_type == 'int':
                type_hint = 'int'
            elif param_type == 'float':
                type_hint = 'float'
            elif param_type == 'bool':
                type_hint = 'bool'
            else:
                type_hint = 'str'
            
            if not required:
                param_signatures.append(f"{param_name}: Optional[{type_hint}] = None")
            else:
                param_signatures.append(f"{param_name}: {type_hint}")
            
            param_docs.append(f"        {param_name}: {param_type} - {'(اختیاری)' if not required else '(الزامی)'}")
        
        # اضافه کردن request
        param_signatures.append("request=None")
        
        signature = ", ".join(param_signatures)
        
        # ساخت docstring
        docstring = f'''    """
    {description}
    
    Args:
{chr(10).join(param_docs)}
        request: درخواست HTTP برای دریافت پروژه جاری (برای استفاده داخلی)
    
    Returns:
        نتیجه عملیات به صورت رشته متنی
    """'''
        
        # ساخت body
        if tool_info['type'] == 'standard':
            if tool_info['action'] == 'list':
                body = f'''    try:
        # دریافت پروژه جاری
        project = None
        if request:
            from construction.project_manager import ProjectManager
            project = ProjectManager.get_current_project(request)
        
        # TODO: پیاده‌سازی منطق دریافت لیست
        return f"📋 لیست {viewset_name.replace('ViewSet', '')}ها"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
            elif tool_info['action'] == 'retrieve':
                body = f'''    try:
        # TODO: پیاده‌سازی منطق دریافت یک مورد
        return f"📋 اطلاعات {viewset_name.replace('ViewSet', '')} #{{id}}"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
            else:
                body = f'''    try:
        # TODO: پیاده‌سازی منطق {tool_info['action']}
        return f"✅ عملیات با موفقیت انجام شد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        else:
            body = f'''    try:
        # TODO: پیاده‌سازی منطق custom action
        return f"✅ عملیات {tool_info['action']} با موفقیت انجام شد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        
        # ساخت کد کامل
        code = f'''@tool
def {tool_name}({signature}) -> str:
{docstring}
{body}
'''
        
        return code
    
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
            if isinstance(field, django_models.ForeignKey):
                field_info['related_model'] = field.related_model.__name__
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
        
        # ساخت signature
        param_signatures = []
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
            
            if not required:
                param_signatures.append(f"{param_name}: Optional[{type_hint}] = None")
            else:
                param_signatures.append(f"{param_name}: {type_hint}")
            
            # ساخت docstring برای param
            param_doc = f"        {param_name}: {type_hint}"
            if param_desc:
                param_doc += f" - {param_desc}"
            if not required:
                param_doc += " (اختیاری)"
            param_docs.append(param_doc)
        
        # اضافه کردن request
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
{docstring}
{body}
'''
        
        return code
    
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
        
        return f'''    try:
        # دریافت پروژه جاری
        project = None
        if request:
            from construction.project_manager import ProjectManager
            project = ProjectManager.get_current_project(request)
            if not project:
                return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        # دریافت لیست {model_name}ها
        from construction.models import {model_name}
        items = {model_name}.objects.all()
        
        if project:
            items = items.filter(project=project)
        
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
        
        return f'''    try:
        # دریافت پروژه جاری
        project = None
        if request:
            from construction.project_manager import ProjectManager
            project = ProjectManager.get_current_project(request)
            if not project:
                return "❌ خطا: پروژه جاری یافت نشد. لطفاً ابتدا یک پروژه را انتخاب کنید."
        
        # ساخت داده‌ها
{chr(10).join(data_lines)}
        
        if project:
            data['project'] = project
        
        # ایجاد {model_name} جدید
        from construction.models import {model_name}
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
        
        return f'''    try:
        # دریافت {model_name} با شناسه
        from construction.models import {model_name}
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
        
        return f'''    try:
        # دریافت و حذف {model_name}
        from construction.models import {model_name}
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
    
    def generate_all_tools(self, output_file: Optional[str] = None) -> str:
        """
        تولید Tools برای تمام ViewSets
        
        Args:
            output_file: مسیر فایل خروجی (اختیاری)
        
        Returns:
            کد کامل تمام Tools
        """
        all_code = '''"""
Tools تولید شده خودکار از ViewSets و APIs
این فایل به صورت خودکار تولید شده است. لطفاً قبل از استفاده بررسی کنید.
"""

from langchain.tools import tool
from typing import Optional
from construction.models import *
from construction.project_manager import ProjectManager

'''
        
        # تحلیل تمام ViewSets در api.py
        viewset_classes = [
            api.ExpenseViewSet,
            api.InvestorViewSet,
            api.PeriodViewSet,
            api.ProjectViewSet,
            api.SaleViewSet,
            api.TransactionViewSet,
            api.UnitViewSet,
            # اضافه کردن بقیه ViewSets
        ]
        
        for viewset_class in viewset_classes:
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
        
        # ذخیره در فایل
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(all_code)
            print(f"✅ Tools در فایل {output_file} ذخیره شد")
        
        return all_code
    
    def analyze_openapi_schema(self, schema_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        تحلیل OpenAPI schema و تولید Tools
        
        این متد از OpenAPI schema کامل استفاده می‌کند که شامل:
        - تمام endpoints (standard و custom actions)
        - پارامترهای path و query
        - requestBody با schema کامل
        - components/schemas با تمام جزئیات
        
        Args:
            schema_path: مسیر فایل schema.json
        
        Returns:
            لیست اطلاعات Tools
        """
        import json
        
        if not schema_path:
            schema_path = project_root / 'schema.json'
        
        if not os.path.exists(schema_path):
            print(f"⚠️  فایل schema در {schema_path} یافت نشد. در حال تولید...")
            from construction.assistant.rag import RAGPipeline
            rag = RAGPipeline()
            rag.generate_schema()
            schema_path = rag.schema_path
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        tools = []
        components = schema.get('components', {}).get('schemas', {})
        
        def resolve_schema_ref(ref: str) -> dict:
            """حل کردن $ref به schema واقعی"""
            if ref.startswith('#/components/schemas/'):
                schema_name = ref.split('/')[-1]
                return components.get(schema_name, {})
            return {}
        
        def extract_properties_from_schema(schema_obj: dict, components: dict) -> List[Dict[str, Any]]:
            """استخراج properties از schema (با پشتیبانی از $ref)"""
            params = []
            
            # اگر $ref دارد، آن را حل کن
            if '$ref' in schema_obj:
                schema_obj = resolve_schema_ref(schema_obj['$ref'])
            
            # استخراج properties
            properties = schema_obj.get('properties', {})
            required_fields = schema_obj.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                # اگر prop_schema خودش $ref دارد
                if '$ref' in prop_schema:
                    prop_schema = resolve_schema_ref(prop_schema['$ref'])
                
                # استخراج نوع
                prop_type = prop_schema.get('type', 'string')
                
                # تبدیل enum به string با description
                if 'enum' in prop_schema:
                    enum_values = prop_schema.get('enum', [])
                    prop_type = 'string'
                    enum_desc = f"مقادیر مجاز: {', '.join(map(str, enum_values))}"
                    description = prop_schema.get('description', '') or prop_schema.get('title', '')
                    if enum_desc:
                        description = f"{description} ({enum_desc})" if description else enum_desc
                else:
                    description = prop_schema.get('description', '') or prop_schema.get('title', '')
                
                # بررسی readOnly
                if prop_schema.get('readOnly', False):
                    continue  # فیلدهای readOnly را در requestBody نادیده بگیر
                
                params.append({
                    'name': prop_name,
                    'type': prop_type,
                    'required': prop_name in required_fields,
                    'description': description,
                    'format': prop_schema.get('format'),  # برای date, date-time و...
                    'nullable': prop_schema.get('nullable', False)
                })
            
            return params
        
        # تحلیل paths
        if 'paths' in schema:
            for path, methods in schema['paths'].items():
                for method, details in methods.items():
                    if method.lower() in ['get', 'post', 'put', 'patch', 'delete']:
                        operation_id = details.get('operationId', '')
                        description = details.get('description', details.get('summary', ''))
                        tags = details.get('tags', [])
                        
                        # استخراج پارامترهای path و query
                        params = []
                        if 'parameters' in details:
                            for param in details['parameters']:
                                param_name = param.get('name', '')
                                param_schema = param.get('schema', {})
                                
                                # حل کردن $ref در schema
                                if '$ref' in param_schema:
                                    param_schema = resolve_schema_ref(param_schema['$ref'])
                                
                                param_type = param_schema.get('type', 'string')
                                required = param.get('required', False)
                                
                                if param_name:
                                    params.append({
                                        'name': param_name,
                                        'type': param_type,
                                        'required': required,
                                        'description': param.get('description', ''),
                                        'in': param.get('in', 'query'),  # path, query, header
                                        'format': param_schema.get('format')
                                    })
                        
                        # استخراج request body (برای POST, PUT, PATCH)
                        if 'requestBody' in details:
                            content = details['requestBody'].get('content', {})
                            if 'application/json' in content:
                                request_schema = content['application/json'].get('schema', {})
                                
                                # استخراج properties از requestBody schema
                                body_params = extract_properties_from_schema(request_schema, components)
                                
                                # اضافه کردن به params (بدون تکرار)
                                existing_names = {p['name'] for p in params}
                                for body_param in body_params:
                                    if body_param['name'] not in existing_names:
                                        params.append(body_param)
                        
                        # تولید نام Tool
                        tool_name = operation_id.lower().replace('_', '_')
                        if not tool_name:
                            # ساخت نام از path و method
                            path_parts = path.strip('/').split('/')
                            resource = path_parts[-1] if path_parts else 'resource'
                            tool_name = f"{method.lower()}_{resource}".replace('-', '_').replace('{', '').replace('}', '')
                        
                        # استخراج اطلاعات security
                        security = details.get('security', [])
                        security_info = []
                        for sec in security:
                            if isinstance(sec, dict):
                                security_info.extend(list(sec.keys()))
                        
                        # استخراج اطلاعات response (برای docstring)
                        responses = details.get('responses', {})
                        response_info = []
                        for status_code, response_detail in responses.items():
                            if isinstance(response_detail, dict):
                                content = response_detail.get('content', {})
                                if 'application/json' in content:
                                    response_schema = content['application/json'].get('schema', {})
                                    if '$ref' in response_schema:
                                        schema_name = response_schema['$ref'].split('/')[-1]
                                        response_info.append(f"{status_code}: {schema_name}")
                                    else:
                                        response_info.append(f"{status_code}: {response_schema.get('type', 'object')}")
                        
                        tools.append({
                            'name': tool_name,
                            'description': description or f"{method.upper()} {path}",
                            'method': method.upper(),
                            'path': path,
                            'params': params,
                            'tags': tags,
                            'operation_id': operation_id,
                            'security': security_info,
                            'responses': response_info
                        })
        
        return tools
    
    def generate_tool_from_openapi(self, tool_info: Dict[str, Any]) -> str:
        """
        تولید کد Tool از اطلاعات OpenAPI
        
        Args:
            tool_info: اطلاعات Tool از OpenAPI schema
        
        Returns:
            کد Python برای Tool
        """
        tool_name = tool_info['name']
        description = tool_info['description']
        params = tool_info.get('params', [])
        path = tool_info.get('path', '')
        method = tool_info.get('method', 'GET')
        
        # ساخت signature
        param_signatures = []
        param_docs = []
        
        for param in params:
            param_name = param['name']
            param_type = param['type']
            required = param.get('required', False) and not param.get('nullable', False)
            param_desc = param.get('description', '')
            param_format = param.get('format', '')
            
            # تبدیل نوع OpenAPI به Python (با توجه به format)
            type_mapping = {
                'integer': 'int',
                'number': 'float',
                'boolean': 'bool',
                'string': 'str',
                'array': 'list',
                'object': 'dict'
            }
            python_type = type_mapping.get(param_type, 'str')
            
            # اگر format دارد، در description اضافه کن
            if param_format:
                if param_format == 'date':
                    param_desc = f"{param_desc} (فرمت: YYYY-MM-DD)" if param_desc else "فرمت: YYYY-MM-DD"
                elif param_format == 'date-time':
                    param_desc = f"{param_desc} (فرمت: ISO 8601)" if param_desc else "فرمت: ISO 8601"
                elif param_format == 'email':
                    param_desc = f"{param_desc} (ایمیل)" if param_desc else "ایمیل"
            
            if not required:
                param_signatures.append(f"{param_name}: Optional[{python_type}] = None")
            else:
                param_signatures.append(f"{param_name}: {python_type}")
            
            param_docs.append(f"        {param_name}: {python_type} - {param_desc or ('(اختیاری)' if not required else '(الزامی)')}")
        
        # اضافه کردن request
        param_signatures.append("request=None")
        
        signature = ", ".join(param_signatures)
        
        # استخراج اطلاعات اضافی
        tags = tool_info.get('tags', [])
        security = tool_info.get('security', [])
        responses = tool_info.get('responses', [])
        operation_id = tool_info.get('operation_id', '')
        
        # ساخت docstring کامل
        docstring_parts = [f"    {description}"]
        docstring_parts.append("")
        docstring_parts.append(f"    این Tool از API endpoint {method} {path} استفاده می‌کند.")
        
        if operation_id:
            docstring_parts.append(f"    Operation ID: {operation_id}")
        
        if tags:
            docstring_parts.append(f"    دسته‌بندی: {', '.join(tags)}")
        
        if security:
            security_str = ', '.join(security)
            docstring_parts.append(f"    نیاز به احراز هویت: {security_str}")
        
        docstring_parts.append("")
        docstring_parts.append("    Args:")
        if param_docs:
            docstring_parts.extend(param_docs)
        else:
            docstring_parts.append("        (بدون پارامتر)")
        docstring_parts.append("        request: درخواست HTTP برای احراز هویت (برای استفاده داخلی)")
        
        if responses:
            docstring_parts.append("")
            docstring_parts.append("    Returns:")
            docstring_parts.append("        نتیجه عملیات به صورت رشته متنی")
            docstring_parts.append("        کدهای وضعیت ممکن:")
            for resp in responses:
                docstring_parts.append(f"        - {resp}")
        else:
            docstring_parts.append("")
            docstring_parts.append("    Returns:")
            docstring_parts.append("        نتیجه عملیات به صورت رشته متنی")
        
        docstring = '\n'.join(docstring_parts)
        
        # ساخت body
        # برای GET requests
        if method == 'GET':
            body = f'''    try:
        # ساخت URL
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        url = f"{{base_url}}{path}"
        
        # اضافه کردن پارامترها به URL
        params = {{}}
{chr(10).join([f"        if {p['name']} is not None:\n            params['{p['name']}'] = {p['name']}" for p in params if p.get('required', False)])}
        
        # TODO: پیاده‌سازی فراخوانی API
        # می‌توانید از requests یا Django test client استفاده کنید
        return f"✅ درخواست {method} به {{url}} ارسال شد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        else:
            body = f'''    try:
        # ساخت URL
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        url = f"{{base_url}}{path}"
        
        # ساخت data
        data = {{}}
{chr(10).join([f"        if {p['name']} is not None:\n            data['{p['name']}'] = {p['name']}" for p in params])}
        
        # TODO: پیاده‌سازی فراخوانی API
        return f"✅ درخواست {method} به {{url}} ارسال شد"
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        
        code = f'''@tool
def {tool_name}({signature}) -> str:
{docstring}
{body}
'''
        
        return code
    
    def generate_tools_from_schema(self, output_file: Optional[str] = None) -> str:
        """
        تولید Tools از OpenAPI schema
        
        Args:
            output_file: مسیر فایل خروجی
        
        Returns:
            کد کامل Tools
        """
        tools_info = self.analyze_openapi_schema()
        
        # شمارش اطلاعات استخراج شده
        total_endpoints = len(tools_info)
        total_params = sum(len(t.get('params', [])) for t in tools_info)
        tags_count = len(set(tag for tool in tools_info for tag in tool.get('tags', [])))
        
        all_code = f'''"""
Tools تولید شده خودکار از OpenAPI Schema
این فایل به صورت خودکار از schema.json تولید شده است.

📊 آمار استخراج شده:
   - تعداد کل Endpoints: {total_endpoints}
   - تعداد کل پارامترها: {total_params}
   - تعداد دسته‌بندی‌ها (Tags): {tags_count}

✅ اطلاعات شامل شده در هر Tool:
   - توضیحات کامل endpoint (description)
   - مسیر API (path)
   - متد HTTP (GET, POST, PUT, DELETE, PATCH)
   - تمام پارامترها (path, query, body)
   - توضیحات کامل هر فیلد (description, type, format)
   - فیلدهای الزامی و اختیاری (required)
   - مقادیر enum (اگر وجود داشته باشد)
   - نیاز به احراز هویت (security)
   - کدهای وضعیت پاسخ (responses)
   - Operation ID
   - دسته‌بندی (tags)

⚠️  توجه: این Tools نیاز به پیاده‌سازی کامل دارند.
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
from django.conf import settings

'''
        
        # گروه‌بندی بر اساس tags
        tools_by_tag = {}
        for tool_info in tools_info:
            tags = tool_info.get('tags', ['other'])
            tag = tags[0] if tags else 'other'
            if tag not in tools_by_tag:
                tools_by_tag[tag] = []
            tools_by_tag[tag].append(tool_info)
        
        # تولید کد برای هر گروه
        for tag, tools in tools_by_tag.items():
            all_code += f"\n# ===== Tools for {tag} ({len(tools)} endpoint) =====\n\n"
            
            for tool_info in tools:
                tool_code = self.generate_tool_from_openapi(tool_info)
                all_code += tool_code + "\n"
        
        # ذخیره در فایل
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(all_code)
            print(f"✅ Tools در فایل {output_file} ذخیره شد")
            
            # نمایش خلاصه
            print(f"\n📊 خلاصه اطلاعات استخراج شده:")
            print(f"   - تعداد کل Endpoints: {total_endpoints}")
            print(f"   - تعداد کل پارامترها: {total_params}")
            print(f"   - تعداد دسته‌بندی‌ها: {tags_count}")
            print(f"\n✅ هر Tool شامل:")
            print(f"   ✓ توضیحات کامل endpoint")
            print(f"   ✓ مسیر API و متد HTTP")
            print(f"   ✓ تمام پارامترها با توضیحات")
            print(f"   ✓ فیلدهای الزامی/اختیاری")
            print(f"   ✓ مقادیر enum و format ها")
            print(f"   ✓ نیاز به احراز هویت")
            print(f"   ✓ کدهای وضعیت پاسخ")
        
        return all_code


def main():
    """
    تابع اصلی برای اجرای generator
    
    توصیه: استفاده از روش 'schema' به عنوان روش پیش‌فرض
    چرا که OpenAPI schema تولید شده توسط drf-spectacular شامل تمام اطلاعات لازم است:
    - تمام endpoints (standard و custom actions)
    - پارامترهای path و query
    - requestBody با schema کامل
    - components/schemas با تمام جزئیات (types, required, descriptions, enums)
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='تولید خودکار Tools از APIs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌ها:
  # استفاده از OpenAPI schema (توصیه می‌شود)
  python tool_generator.py --method schema
  
  # استفاده از ViewSets (برای موارد خاص)
  python tool_generator.py --method viewset
  
  # استفاده از هر دو روش
  python tool_generator.py --method both
        """
    )
    parser.add_argument('--method', choices=['viewset', 'schema', 'both'], default='schema',
                       help='روش تولید: schema (از OpenAPI - توصیه می‌شود), viewset (از ViewSets), both (هر دو)')
    parser.add_argument('--output', type=str, default=None,
                       help='مسیر فایل خروجی (پیش‌فرض: generated_tools.py)')
    
    args = parser.parse_args()
    
    generator = ToolGenerator()
    
    if not args.output:
        args.output = str(project_root / 'construction' / 'assistant' / 'generated_tools.py')
    
    if args.method in ['viewset', 'both']:
        print("🔧 در حال تولید Tools از ViewSets...")
        print("   ⚠️  توجه: این روش ممکن است تمام اطلاعات را شامل نشود.")
        print("   💡 توصیه: از روش 'schema' استفاده کنید که کامل‌تر است.\n")
        code = generator.generate_all_tools(
            output_file=args.output if args.method == 'viewset' else None
        )
        print(f"✅ تولید Tools از ViewSets با موفقیت انجام شد!")
    
    if args.method in ['schema', 'both']:
        print("\n🔧 در حال تولید Tools از OpenAPI Schema...")
        print("   ✅ استفاده از schema کامل drf-spectacular")
        print("   ✅ شامل تمام endpoints، parameters، requestBody و schemas\n")
        code = generator.generate_tools_from_schema(
            output_file=args.output if args.method == 'schema' else args.output.replace('.py', '_from_schema.py')
        )
        print(f"✅ تولید Tools از Schema با موفقیت انجام شد!")
    
    print(f"\n📁 فایل خروجی: {args.output}")
    print("\n⚠️  توجه: این Tools به صورت خودکار تولید شده‌اند و نیاز به بررسی و تکمیل دارند.")
    if args.method == 'schema':
        print("💡 مزایای استفاده از schema:")
        print("   - شامل تمام custom actions")
        print("   - شامل تمام پارامترهای requestBody")
        print("   - شامل descriptions و types کامل")
        print("   - شامل enum values و format ها")


if __name__ == "__main__":
    main()

