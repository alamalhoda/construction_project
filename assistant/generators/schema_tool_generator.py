"""
تولید خودکار Tools از OpenAPI Schema
این ماژول فقط از OpenAPI schema تولید شده توسط drf-spectacular استفاده می‌کند

این generator برای استفاده در هر پروژه Django قابل استفاده است.
"""

import os
import sys
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

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

try:
    import django
    django.setup()
except Exception:
    pass  # Django setup optional for schema generator


class SchemaToolGenerator:
    """کلاس برای تولید خودکار Tools از OpenAPI Schema"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Args:
            schema_path: مسیر فایل schema.json (پیش‌فرض: schema.json در root پروژه)
        """
        self.schema_path = schema_path or str(project_root / 'schema.json')
        self.components = {}
        self.schema = None
    
    def load_schema(self) -> dict:
        """
        بارگذاری OpenAPI schema
        
        در صورت نبود schema، تلاش می‌کند با استفاده از drf-spectacular تولید کند.
        """
        if not os.path.exists(self.schema_path):
            print(f"⚠️  فایل schema در {self.schema_path} یافت نشد. در حال تولید...")
            
            # تلاش برای تولید schema با drf-spectacular
            try:
                import django
                from django.core.management import call_command
                from io import StringIO
                
                django.setup()
                
                # تولید schema با drf-spectacular
                output = StringIO()
                call_command('spectacular', '--file', self.schema_path, '--format', 'openapi-json', stdout=output)
                
                if not os.path.exists(self.schema_path):
                    raise FileNotFoundError(f"Schema file not created at {self.schema_path}")
                    
            except Exception as e:
                # Fallback: تلاش برای استفاده از RAGPipeline (اگر در این پروژه موجود باشد)
                try:
                    from assistant.rag import RAGPipeline
                    rag = RAGPipeline()
                    rag.generate_schema()
                    self.schema_path = rag.schema_path
                except ImportError:
                    raise FileNotFoundError(
                        f"Schema file not found at {self.schema_path} and could not generate it. "
                        f"Please run: python manage.py spectacular --file {self.schema_path} --format openapi-json"
                    )
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        self.components = self.schema.get('components', {}).get('schemas', {})
        return self.schema
    
    def resolve_schema_ref(self, ref: str) -> dict:
        """حل کردن $ref به schema واقعی"""
        if ref.startswith('#/components/schemas/'):
            schema_name = ref.split('/')[-1]
            return self.components.get(schema_name, {})
        return {}
    
    def normalize_tool_name(self, operation_id: str, max_length: int = 64) -> str:
        """
        نرمال‌سازی نام tool برای سازگاری با LLM providers
        
        این تابع:
        1. نام‌های تکراری را حذف می‌کند (مثل investor_investor_ -> investor_)
        2. نام‌های طولانی را کوتاه می‌کند
        3. کاراکترهای غیرمجاز را حذف می‌کند
        
        Args:
            operation_id: Operation ID از OpenAPI schema
            max_length: حداکثر طول مجاز (پیش‌فرض: 64 برای Gemini)
        
        Returns:
            نام نرمال‌سازی شده
        """
        if not operation_id:
            return ''
        
        # تبدیل به lowercase و جایگزینی کاراکترهای غیرمجاز
        tool_name = operation_id.lower().replace('-', '_').replace(' ', '_')
        
        # حذف کاراکترهای غیرمجاز (فقط alphanumeric و underscore)
        tool_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in tool_name)
        
        # حذف تکرارهای متوالی در ابتدای نام
        # مثال: investor_investor_cumulative -> investor_cumulative
        parts = tool_name.split('_')
        if len(parts) >= 2:
            # بررسی اینکه آیا دو بخش اول یکسان هستند
            if parts[0] == parts[1]:
                # حذف بخش تکراری
                parts = [parts[0]] + parts[2:]
            # بررسی تکرارهای دیگر (مثل investor_investor_investor)
            filtered_parts = []
            prev_part = None
            for part in parts:
                if part != prev_part:
                    filtered_parts.append(part)
                    prev_part = part
                # اگر بخش فعلی با بخش قبلی متفاوت است اما با بخش قبل از آن یکسان است
                # (مثل: investor_cumulative_investor -> investor_cumulative)
                elif len(filtered_parts) >= 2 and part == filtered_parts[-2]:
                    # حذف بخش تکراری
                    continue
            parts = filtered_parts
        
        tool_name = '_'.join(parts)
        
        # حذف underscore های متوالی
        while '__' in tool_name:
            tool_name = tool_name.replace('__', '_')
        
        # حذف underscore از ابتدا و انتها
        tool_name = tool_name.strip('_')
        
        # اگر خیلی طولانی است، کوتاه کن
        if len(tool_name) > max_length:
            # استراتژی: حفظ بخش‌های مهم (اولین و آخرین بخش)
            parts = tool_name.split('_')
            if len(parts) > 2:
                # حفظ اولین بخش (مثل investor) و آخرین بخش (مثل retrieve)
                first_part = parts[0]
                last_part = parts[-1]
                middle_parts = parts[1:-1]
                
                # کوتاه کردن بخش‌های میانی
                available_length = max_length - len(first_part) - len(last_part) - 2  # 2 برای underscore ها
                if available_length > 0:
                    # کوتاه کردن بخش‌های میانی
                    shortened_middle = []
                    for part in middle_parts:
                        if len('_'.join(shortened_middle + [part])) <= available_length:
                            shortened_middle.append(part)
                        else:
                            break
                    
                    if shortened_middle:
                        tool_name = '_'.join([first_part] + shortened_middle + [last_part])
                    else:
                        # اگر نمی‌توانیم بخش میانی را نگه داریم، فقط اول و آخر را نگه دار
                        tool_name = f"{first_part}_{last_part}"
                else:
                    # اگر حتی اول و آخر هم نمی‌گنجد، فقط اول را نگه دار
                    tool_name = first_part[:max_length]
            else:
                # اگر فقط دو بخش دارد، کوتاه کن
                tool_name = tool_name[:max_length]
        
        # اطمینان از اینکه با حرف یا underscore شروع می‌شود
        if tool_name and not (tool_name[0].isalpha() or tool_name[0] == '_'):
            tool_name = '_' + tool_name
        
        return tool_name
    
    def extract_properties_from_schema(self, schema_obj: dict) -> List[Dict[str, Any]]:
        """استخراج properties از schema (با پشتیبانی از $ref)"""
        params = []
        
        # اگر $ref دارد، آن را حل کن
        if '$ref' in schema_obj:
            schema_obj = self.resolve_schema_ref(schema_obj['$ref'])
        
        # استخراج properties
        properties = schema_obj.get('properties', {})
        required_fields = schema_obj.get('required', [])
        
        for prop_name, prop_schema in properties.items():
            # اگر prop_schema خودش $ref دارد
            if '$ref' in prop_schema:
                prop_schema = self.resolve_schema_ref(prop_schema['$ref'])
            
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
    
    def analyze_openapi_schema(self) -> List[Dict[str, Any]]:
        """
        تحلیل OpenAPI schema و تولید Tools
        
        این متد از OpenAPI schema کامل استفاده می‌کند که شامل:
        - تمام endpoints (standard و custom actions)
        - پارامترهای path و query
        - requestBody با schema کامل
        - components/schemas با تمام جزئیات
        
        Returns:
            لیست اطلاعات Tools
        """
        if not self.schema:
            self.load_schema()
        
        tools = []
        
        # تحلیل paths
        if 'paths' in self.schema:
            for path, methods in self.schema['paths'].items():
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
                                    param_schema = self.resolve_schema_ref(param_schema['$ref'])
                                
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
                                body_params = self.extract_properties_from_schema(request_schema)
                                
                                # اضافه کردن به params (بدون تکرار) و مشخص کردن in='body'
                                existing_names = {p['name'] for p in params}
                                for body_param in body_params:
                                    if body_param['name'] not in existing_names:
                                        body_param['in'] = 'body'  # مشخص کردن که این body parameter است
                                        params.append(body_param)
                        
                        # تولید نام Tool با نرمال‌سازی
                        tool_name = self.normalize_tool_name(operation_id, max_length=64)
                        if not tool_name:
                            # ساخت نام از path و method
                            path_parts = path.strip('/').split('/')
                            resource = path_parts[-1] if path_parts else 'resource'
                            fallback_name = f"{method.lower()}_{resource}".replace('-', '_').replace('{', '').replace('}', '')
                            tool_name = self.normalize_tool_name(fallback_name, max_length=64)
                        
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
    
    def generate_tool_code(self, tool_info: Dict[str, Any]) -> str:
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
        
        # ساخت signature - جدا کردن required و optional
        required_params = []
        optional_params = []
        param_docs = []
        path_params = []  # برای جایگزینی در URL
        
        for param in params:
            param_name = param['name']
            param_type = param['type']
            param_in = param.get('in', 'query')  # path, query, body
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
            
            param_doc = f"        {param_name}: {python_type} - {param_desc or ('(اختیاری)' if not required else '(الزامی)')}"
            param_docs.append(param_doc)
            
            # path parameters همیشه required هستند
            if param_in == 'path':
                required_params.append(f"{param_name}: {python_type}")
                path_params.append(param_name)
            elif not required:
                optional_params.append(f"{param_name}: Optional[{python_type}] = None")
            else:
                required_params.append(f"{param_name}: {python_type}")
        
        # اضافه کردن request در آخر
        param_signatures = required_params + optional_params + ["request=None"]
        signature = ", ".join(param_signatures)
        
        # استخراج اطلاعات اضافی
        tags = tool_info.get('tags', [])
        security = tool_info.get('security', [])
        responses = tool_info.get('responses', [])
        operation_id = tool_info.get('operation_id', '')
        
        # ساخت docstring کامل با فرمت استاندارد
        # استخراج عنوان کوتاه از description (اولین خط)
        description_lines = description.split('\n') if description else ['']
        short_title = description_lines[0].strip() if description_lines else f"{method} {path}"
        detailed_description = '\n'.join(description_lines[1:]).strip() if len(description_lines) > 1 else ""
        
        docstring_parts = [f"    {short_title}"]
        
        # اگر توضیحات کامل‌تری وجود دارد
        if detailed_description:
            docstring_parts.append("")
            # تقسیم به خطوط و اضافه کردن با indent
            for line in detailed_description.split('\n'):
                docstring_parts.append(f"    {line}")
        
        # اضافه کردن اطلاعات تکنیکی
        docstring_parts.append("")
        docstring_parts.append(f"    این Tool از API endpoint {method} {path} استفاده می‌کند.")
        
        if operation_id:
            docstring_parts.append(f"    Operation ID: {operation_id}")
        
        if tags:
            docstring_parts.append(f"    دسته‌بندی: {', '.join(tags)}")
        
        # Args با فرمت استاندارد Python docstring - استخراج خودکار از schema
        docstring_parts.append("")
        docstring_parts.append("    Args:")
        if param_docs:
            # تبدیل فرمت param_docs به فرمت استاندارد
            for param_doc in param_docs:
                # param_doc به صورت "        param_name: type - description" است
                # تبدیل به "        param_name (type): description"
                if ' - ' in param_doc:
                    parts = param_doc.split(' - ', 1)
                    param_part = parts[0].strip()  # "        param_name: type"
                    desc_part = parts[1].strip() if len(parts) > 1 else ""  # "description"
                    # استخراج نام و نوع
                    if ':' in param_part:
                        param_name = param_part.split(':', 1)[0].strip()  # "param_name"
                        type_part = param_part.split(':', 1)[1].strip() if ':' in param_part else 'str'
                        # اگر Optional است
                        if 'Optional[' in type_part:
                            type_part = type_part.replace('Optional[', '').replace(']', '').strip()
                            if desc_part:
                                docstring_parts.append(f"        {param_name} ({type_part}, optional): {desc_part}")
                            else:
                                docstring_parts.append(f"        {param_name} ({type_part}, optional): (اختیاری)")
                        else:
                            if desc_part:
                                docstring_parts.append(f"        {param_name} ({type_part}): {desc_part}")
                            else:
                                docstring_parts.append(f"        {param_name} ({type_part}): (الزامی)")
                    else:
                        docstring_parts.append(f"    {param_doc}")
                else:
                    docstring_parts.append(f"    {param_doc}")
        else:
            docstring_parts.append("        (بدون پارامتر)")
        docstring_parts.append("        request (optional): درخواست HTTP برای احراز هویت (برای استفاده داخلی)")
        
        # Returns با فرمت استاندارد - استخراج خودکار از schema
        docstring_parts.append("")
        docstring_parts.append("    Returns:")
        if responses:
            docstring_parts.append("        str: نتیجه عملیات به صورت رشته متنی")
            if len(responses) > 1:
                docstring_parts.append("        کدهای وضعیت ممکن:")
                for resp in responses:
                    docstring_parts.append(f"        - {resp}")
            else:
                # اگر فقط یک response داریم، جزئیات بیشتری بدهیم
                resp = responses[0]
                if ':' in resp:
                    status_code, schema_name = resp.split(':', 1)
                    docstring_parts.append(f"        - {status_code}: {schema_name.strip()}")
        else:
            docstring_parts.append("        str: نتیجه عملیات به صورت رشته متنی")
        
        # Raises (اگر خطاهای احتمالی وجود دارد)
        if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            docstring_parts.append("")
            docstring_parts.append("    Raises:")
            docstring_parts.append("        ValidationError: اگر ورودی‌ها نامعتبر باشند")
            docstring_parts.append("        PermissionDenied: اگر کاربر دسترسی نداشته باشد")
        
        # مثال استفاده
        docstring_parts.append("")
        docstring_parts.append("    مثال استفاده:")
        if method == 'GET':
            example_path = path.replace('{id}', '1') if '{id}' in path else path
            docstring_parts.append(f"        {method} {example_path}")
        else:
            docstring_parts.append(f"        {method} {path}")
        
        # نکات مهم
        if security:
            docstring_parts.append("")
            docstring_parts.append("    نکات مهم:")
            security_str = ', '.join(security)
            docstring_parts.append(f"        - نیاز به احراز هویت: {security_str}")
        
        docstring = '\n'.join(docstring_parts)
        
        # ساخت URL با جایگزینی path parameters
        url_path = path
        for path_param in path_params:
            url_path = url_path.replace(f"{{{path_param}}}", f"{{{{'{path_param}'}}}}")
        
        # تعیین action name از operation_id یا method
        action_name = None
        if operation_id:
            # استخراج action از operation_id (مثل Expense_list -> list)
            parts = operation_id.split('_')
            if len(parts) >= 2:
                action_name = '_'.join(parts[1:])  # list, create, retrieve, etc.
                
                # حذف suffix های DRF از custom actions
                # مثال: active_retrieve -> active, dashboard_data_retrieve -> dashboard_data
                drf_suffixes = ['_list', '_retrieve', '_create', '_update', '_partial_update', '_destroy']
                for suffix in drf_suffixes:
                    if action_name.endswith(suffix):
                        # اگر action فقط suffix است (مثل list, retrieve)، نگه دار
                        if action_name == suffix[1:]:  # حذف _ اول
                            break
                        # اگر action custom است (مثل active_retrieve)، suffix را حذف کن
                        action_name = action_name[:-len(suffix)]
                        break
        
        # اگر action_name پیدا نشد، از method و path استخراج کن
        if not action_name:
            if method == 'GET':
                if path_params:
                    action_name = 'retrieve'
                else:
                    action_name = 'list'
            elif method == 'POST':
                action_name = 'create'
            elif method == 'PUT':
                action_name = 'update'
            elif method == 'PATCH':
                action_name = 'partial_update'
            elif method == 'DELETE':
                action_name = 'destroy'
        
        # ساخت URL کامل با جایگزینی path parameters
        url_builder_parts = []
        url_builder_parts.append("        # ساخت URL کامل")
        url_builder_parts.append(f"        url = '{path}'")
        
        # جایگزینی path parameters در URL
        for path_param in path_params:
            url_builder_parts.append(f"        if {path_param} is not None:")
            url_builder_parts.append(f"            url = url.replace('{{{path_param}}}', str({path_param}))")
        
        url_builder_str = '\n'.join(url_builder_parts)
        
        # ساخت کد برای query parameters (برای GET)
        query_params_code = []
        for p in params:
            param_in = p.get('in', 'query')
            if param_in == 'query':
                query_params_code.append(f"        if {p['name']} is not None:\n            kwargs['{p['name']}'] = {p['name']}")
        
        query_params_str = '\n'.join(query_params_code) if query_params_code else ""
        
        # ساخت کد برای body parameters (برای POST, PUT, PATCH)
        body_params_code = []
        for p in params:
            param_in = p.get('in', 'body')  # پیش‌فرض body برای requestBody
            if param_in == 'body' or param_in not in ['path', 'query']:  # body parameters
                body_params_code.append(f"        if {p['name']} is not None:\n            data['{p['name']}'] = {p['name']}")
        
        body_params_str = '\n'.join(body_params_code) if body_params_code else ""
        
        # ساخت body بر اساس method
        if method == 'GET':
            body = f'''    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        
{url_builder_str}
        
        # ساخت kwargs برای query parameters
        kwargs = {{}}
{query_params_str}
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='{method}',
            **kwargs
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        else:
            body = f'''    try:
        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        )
        
{url_builder_str}
        
        # ساخت data برای request body
        data = {{}}
{body_params_str}
        
        # فراخوانی API endpoint از طریق HTTP
        response = call_api_via_http(
            url=url,
            request=request,
            method='{method}',
            data=data
        )
        
        # تبدیل response به string
        return response_to_string(response)
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        
        code = f'''@tool
def {tool_name}({signature}) -> str:
    """
{docstring}
    """
{body}
'''
        
        return code
    
    def generate_all_tools(self, output_file: Optional[str] = None) -> str:
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
                tool_code = self.generate_tool_code(tool_info)
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
    """تابع اصلی برای اجرای schema-based generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='تولید خودکار Tools از OpenAPI Schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال:
  python schema_tool_generator.py --output generated_tools_from_schema.py
        """
    )
    parser.add_argument('--schema', type=str, default=None,
                       help='مسیر فایل schema.json (پیش‌فرض: schema.json در root پروژه)')
    parser.add_argument('--output', type=str, default=None,
                       help='مسیر فایل خروجی (پیش‌فرض: generated_tools_from_schema.py)')
    
    args = parser.parse_args()
    
    generator = SchemaToolGenerator(schema_path=args.schema)
    
    if not args.output:
        args.output = str(project_root / 'assistant' / 'generated' / 'generated_tools_from_schema.py')
    
    print("🔧 در حال تولید Tools از OpenAPI Schema...")
    print("   ✅ استفاده از schema کامل drf-spectacular")
    print("   ✅ شامل تمام endpoints، parameters، requestBody و schemas\n")
    
    code = generator.generate_all_tools(output_file=args.output)
    
    print(f"\n📁 فایل خروجی: {args.output}")
    print("\n⚠️  توجه: این Tools به صورت خودکار تولید شده‌اند و نیاز به بررسی و تکمیل دارند.")


if __name__ == "__main__":
    main()

