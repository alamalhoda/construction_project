"""
تولید خودکار Tools از OpenAPI Schema
این ماژول فقط از OpenAPI schema تولید شده توسط drf-spectacular استفاده می‌کند

این generator برای استفاده در هر پروژه Django قابل استفاده است.
"""

import os
import sys
import json
import re
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

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


# ============================================================================
# کلاس‌های پایه برای Parameter و Endpoint
# ============================================================================

class ParameterLocation(Enum):
    """موقعیت پارامتر در درخواست HTTP"""
    PATH = "path"  # /api/v1/Expense/{id}/
    QUERY = "query"  # ?page=1&page_size=10
    BODY = "body"  # JSON body
    HEADER = "header"  # HTTP headers


@dataclass
class Parameter:
    """تعریف پارامتر با اطلاعات کامل"""
    name: str  # نام انگلیسی
    name_fa: str  # نام فارسی
    location: ParameterLocation  # موقعیت
    type: str  # نوع داده (string, integer, boolean, etc)
    required: bool  # الزامی؟
    description: str  # توضیح فارسی
    example: Any = None  # مثال
    enum_values: Optional[List[str]] = None  # مقادیر ممکن
    pattern: Optional[str] = None  # regex pattern
    min_length: Optional[int] = None  # حداقل طول
    max_length: Optional[int] = None  # حداکثر طول
    min_value: Optional[float] = None  # حداقل مقدار (برای عدد)
    max_value: Optional[float] = None  # حداکثر مقدار (برای عدد)
    format: Optional[str] = None  # format (date, email, etc)
    nullable: bool = False  # آیا می‌تواند null باشد
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        data = asdict(self)
        data['location'] = self.location.value
        return data
    
    def get_python_type_hint(self) -> str:
        """بدست آوردن Python type hint"""
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict',
        }
        python_type = type_mapping.get(self.type, 'str')
        
        # اگر optional است
        if not self.required or self.nullable:
            python_type = f"Optional[{python_type}]"
        
        return python_type
    
    def get_validation_code(self) -> str:
        """تولید کد validation برای این پارامتر"""
        validations = []
        
        # بررسی required (فقط اگر required است و nullable نیست)
        if self.required and not self.nullable:
            validations.append(f"if {self.name} is None: raise ValueError('{self.name_fa} الزامی است')")
        
        # بررسی length (فقط برای string)
        if self.type == 'string':
            if self.min_length:
                validations.append(f"if {self.name} is not None and len({self.name}) < {self.min_length}: raise ValueError('{self.name_fa} حداقل {self.min_length} کاراکتر باید باشد')")
            
            if self.max_length:
                validations.append(f"if {self.name} is not None and len({self.name}) > {self.max_length}: raise ValueError('{self.name_fa} حداکثر {self.max_length} کاراکتر می‌تواند باشد')")
        
        # بررسی مقدار (برای integer و number)
        if self.type in ['integer', 'number']:
            if self.min_value is not None:
                validations.append(f"if {self.name} is not None and {self.name} < {self.min_value}: raise ValueError('{self.name_fa} حداقل {self.min_value} باید باشد')")
            
            if self.max_value is not None:
                validations.append(f"if {self.name} is not None and {self.name} > {self.max_value}: raise ValueError('{self.name_fa} حداکثر {self.max_value} می‌تواند باشد')")
        
        # بررسی enum
        if self.enum_values:
            enum_str = "', '".join(map(str, self.enum_values))
            validations.append(f"if {self.name} is not None and {self.name} not in ['{enum_str}']: raise ValueError('{self.name_fa} باید یکی از این باشد: {enum_str}')")
        
        # بررسی pattern
        if self.pattern:
            validations.append(f"if {self.name} is not None and not re.match(r'{self.pattern}', str({self.name})): raise ValueError('{self.name_fa} فرمت نامعتبر است')")
        
        # برگرداندن کد validation بدون indentation (indentation در generate_tool_code اضافه می‌شود)
        return '\n'.join(validations)


@dataclass
class Endpoint:
    """تعریف endpoint کامل"""
    path: str  # /api/v1/Expense/
    method: str  # GET, POST, PUT, DELETE, PATCH
    operation_id: str  # Expense_list
    name_en: str  # expense_list
    name_fa: str  # لیست هزینه‌ها
    description: str  # توضیح کامل
    tags: List[str]  # دسته‌بندی‌ها
    parameters: List[Parameter]  # پارامترها
    required_params: List[Parameter]  # پارامترهای الزامی
    optional_params: List[Parameter]  # پارامترهای اختیاری
    security: List[str]  # نیاز به احراز هویت
    request_body: Optional[Dict[str, Any]] = None  # JSON body schema
    responses: Optional[Dict[str, Any]] = None  # پاسخ‌های احتمالی
    examples: Optional[List[Dict[str, Any]]] = None  # مثال‌های عملی
    
    def get_path_params(self) -> List[Parameter]:
        """بدست آوردن path parameters"""
        return [p for p in self.parameters if p.location == ParameterLocation.PATH]
    
    def get_query_params(self) -> List[Parameter]:
        """بدست آوردن query parameters"""
        return [p for p in self.parameters if p.location == ParameterLocation.QUERY]
    
    def get_body_params(self) -> List[Parameter]:
        """بدست آوردن body parameters"""
        return [p for p in self.parameters if p.location == ParameterLocation.BODY]
    
    def get_path_with_params(self) -> str:
        """بدست آوردن path با جایگزاری parameters"""
        path = self.path
        for param in self.get_path_params():
            path = path.replace(f"{{{param.name}}}", f"{{{{self.{param.name}}}}}")
        return path


# ============================================================================
# SmartParameterExtractor - استخراج هوشمند پارامترها
# ============================================================================

class SmartParameterExtractor:
    """
    استخراج هوشمند پارامترها از OpenAPI schema
    
    وظایف:
    - تفکیک کامل path, query, body parameters
    - بدست آوردن توضیحات دقیق هر پارامتر
    - تعیین required/optional
    - استخراج examples و validation rules
    """
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.components = schema.get('components', {}).get('schemas', {})
    
    def resolve_schema_ref(self, ref: str) -> dict:
        """حل کردن $ref به schema واقعی"""
        if ref.startswith('#/components/schemas/'):
            schema_name = ref.split('/')[-1]
            return self.components.get(schema_name, {})
        return {}
    
    def extract_path_parameters(self, path: str, endpoint_data: Dict[str, Any]) -> List[Parameter]:
        """استخراج path parameters از {id}، {pk}، etc"""
        path_params = []
        
        # یافتن تمام {xxx} در path
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, path)
        
        for match in matches:
            param_name = match
            
            # یافتن توصیف در parameters list
            param_info = None
            if 'parameters' in endpoint_data:
                for param in endpoint_data['parameters']:
                    if param.get('name') == param_name and param.get('in') == 'path':
                        param_info = param
                        break
            
            # استخراج schema
            schema_info = {}
            if param_info:
                schema_info = param_info.get('schema', {})
                # حل کردن $ref
                if '$ref' in schema_info:
                    schema_info = self.resolve_schema_ref(schema_info['$ref'])
            
            # تولید Parameter object
            param = Parameter(
                name=param_name,
                name_fa=self._get_persian_name(param_name),
                location=ParameterLocation.PATH,
                type=schema_info.get('type', 'string') if schema_info else 'string',
                required=True,  # path parameters همیشه required هستند
                description=param_info.get('description', f'شناسه {param_name}') if param_info else f'شناسه {param_name}',
                example=param_info.get('example') if param_info and 'example' in param_info else (schema_info.get('example', 1) if schema_info else 1),
                format=schema_info.get('format') if schema_info else None,
            )
            path_params.append(param)
        
        return path_params
    
    def extract_query_parameters(self, endpoint_data: Dict[str, Any]) -> List[Parameter]:
        """استخراج query parameters"""
        query_params = []
        
        if 'parameters' not in endpoint_data:
            return query_params
        
        for param_info in endpoint_data['parameters']:
            if param_info.get('in') != 'query':
                continue
            
            param_name = param_info.get('name', '')
            schema_info = param_info.get('schema', {})
            
            # حل کردن $ref
            if '$ref' in schema_info:
                schema_info = self.resolve_schema_ref(schema_info['$ref'])
            
            param = Parameter(
                name=param_name,
                name_fa=self._get_persian_name(param_name),
                location=ParameterLocation.QUERY,
                type=schema_info.get('type', 'string'),
                required=param_info.get('required', False),
                description=param_info.get('description', ''),
                example=schema_info.get('example') if 'example' in schema_info else param_info.get('example'),
                enum_values=schema_info.get('enum', None),
                format=schema_info.get('format', None),
                min_value=schema_info.get('minimum'),
                max_value=schema_info.get('maximum'),
                min_length=schema_info.get('minLength'),
                max_length=schema_info.get('maxLength'),
                pattern=schema_info.get('pattern'),
                nullable=schema_info.get('nullable', False),
            )
            query_params.append(param)
        
        return query_params
    
    def extract_body_parameters(self, endpoint_data: Dict[str, Any]) -> List[Parameter]:
        """استخراج body parameters از requestBody"""
        body_params = []
        
        if 'requestBody' not in endpoint_data:
            return body_params
        
        request_body = endpoint_data['requestBody']
        
        # یافتن schema
        schema_obj = None
        if 'content' in request_body:
            for content_type, content_data in request_body['content'].items():
                if 'schema' in content_data:
                    schema_obj = content_data['schema']
                    break
        
        if not schema_obj:
            return body_params
        
        # حل کردن $ref
        if '$ref' in schema_obj:
            schema_obj = self.resolve_schema_ref(schema_obj['$ref'])
        
        # استخراج properties
        properties = schema_obj.get('properties', {})
        required_fields = schema_obj.get('required', [])
        
        for prop_name, prop_schema in properties.items():
            # حل کردن $ref در property
            if '$ref' in prop_schema:
                prop_schema = self.resolve_schema_ref(prop_schema['$ref'])
            
            # بررسی readOnly
            if prop_schema.get('readOnly', False):
                continue  # فیلدهای readOnly را در requestBody نادیده بگیر
            
            param = Parameter(
                name=prop_name,
                name_fa=self._get_persian_name(prop_name),
                location=ParameterLocation.BODY,
                type=prop_schema.get('type', 'string'),
                required=prop_name in required_fields,
                description=prop_schema.get('description', ''),
                example=prop_schema.get('example', None),
                enum_values=prop_schema.get('enum', None),
                format=prop_schema.get('format', None),
                min_value=prop_schema.get('minimum'),
                max_value=prop_schema.get('maximum'),
                min_length=prop_schema.get('minLength'),
                max_length=prop_schema.get('maxLength'),
                pattern=prop_schema.get('pattern'),
                nullable=prop_schema.get('nullable', False),
            )
            body_params.append(param)
        
        return body_params
    
    def _get_persian_name(self, english_name: str) -> str:
        """تبدیل نام انگلیسی به فارسی"""
        # یک dictionary ساده برای تبدیل‌های معمول
        translations = {
            'id': 'شناسه',
            'pk': 'شناسه',
            'page': 'صفحه',
            'page_size': 'اندازه صفحه',
            'ordering': 'مرتب‌سازی',
            'period': 'دوره',
            'expense_type': 'نوع هزینه',
            'amount': 'مبلغ',
            'description': 'توضیحات',
            'created_at': 'تاریخ ایجاد',
            'updated_at': 'تاریخ آخرین به‌روزرسانی',
            'name': 'نام',
            'email': 'ایمیل',
            'phone': 'تلفن',
            'investor': 'سرمایه‌گذار',
            'project': 'پروژه',
            'date': 'تاریخ',
            'status': 'وضعیت',
            'type': 'نوع',
        }
        return translations.get(english_name.lower(), english_name)


# ============================================================================
# ToolTemplateGenerator - تولید docstring بهتر
# ============================================================================

class ToolTemplateGenerator:
    """
    تولید templates بهتر برای tools
    
    وظایف:
    - تولید docstring غنی‌تر
    - تولید validation code
    - تولید request handling
    - تولید error handling
    """
    
    def generate_tool_docstring(self, endpoint: Endpoint) -> str:
        """تولید docstring کامل برای tool"""
        lines = [
            f'    {endpoint.name_fa}',
            "",
        ]
        
        # اضافه کردن description
        if endpoint.description:
            desc_lines = endpoint.description.split('\n')
            for line in desc_lines:
                lines.append(f"    {line}")
            lines.append("")
        
        # پارامترهای درخواست
        has_params = bool(endpoint.get_path_params() or endpoint.get_query_params() or endpoint.get_body_params())
        if has_params:
            lines.append("    پارامترهای درخواست:")
            lines.append("")
            
            # Path parameters
            path_params = endpoint.get_path_params()
            if path_params:
                lines.append("        * مسیر (URL Path):")
                for param in path_params:
                    lines.append(f"            - {param.name} ({param.name_fa}): {param.type}")
                    if param.description:
                        lines.append(f"              {param.description}")
                    lines.append(f"              الزامی: {'بله' if param.required else 'خیر'}")
                    if param.example is not None:
                        lines.append(f"              مثال: {param.example}")
                lines.append("")
            
            # Query parameters
            query_params = endpoint.get_query_params()
            if query_params:
                lines.append("        * کوئری (Query String):")
                for param in query_params:
                    lines.append(f"            - {param.name} ({param.name_fa}): {param.type}")
                    if param.description:
                        lines.append(f"              {param.description}")
                    lines.append(f"              الزامی: {'بله' if param.required else 'خیر'}")
                    if param.example is not None:
                        lines.append(f"              مثال: {param.example}")
                    if param.enum_values:
                        lines.append(f"              مقادیر معتبر: {', '.join(map(str, param.enum_values))}")
                    if param.min_value is not None or param.max_value is not None:
                        range_str = []
                        if param.min_value is not None:
                            range_str.append(f"حداقل: {param.min_value}")
                        if param.max_value is not None:
                            range_str.append(f"حداکثر: {param.max_value}")
                        if range_str:
                            lines.append(f"              محدوده: {', '.join(range_str)}")
                lines.append("")
            
            # Body parameters
            body_params = endpoint.get_body_params()
            if body_params:
                lines.append("        * بدنه (Request Body):")
                for param in body_params:
                    lines.append(f"            - {param.name} ({param.name_fa}): {param.type}")
                    if param.description:
                        lines.append(f"              {param.description}")
                    lines.append(f"              الزامی: {'بله' if param.required else 'خیر'}")
                    if param.example is not None:
                        lines.append(f"              مثال: {param.example}")
                    if param.enum_values:
                        lines.append(f"              مقادیر معتبر: {', '.join(map(str, param.enum_values))}")
                    if param.min_value is not None or param.max_value is not None:
                        range_str = []
                        if param.min_value is not None:
                            range_str.append(f"حداقل: {param.min_value}")
                        if param.max_value is not None:
                            range_str.append(f"حداکثر: {param.max_value}")
                        if range_str:
                            lines.append(f"              محدوده: {', '.join(range_str)}")
                lines.append("")
        
        # Returns
        lines.append("    Returns:")
        lines.append("        str: نتیجه عملیات به صورت رشته متنی")
        lines.append("")
        
        # مثال‌های کاربردی
        if endpoint.examples:
            lines.append("    مثال‌های کاربردی:")
            for i, example in enumerate(endpoint.examples, 1):
                lines.append(f"        {i}. {example.get('description', '')}")
                lines.append(f"           {example.get('request', '')}")
            lines.append("")
        
        # نکات مهم
        lines.append("    نکات مهم:")
        lines.append(f"        - روش HTTP: {endpoint.method}")
        lines.append(f"        - مسیر: {endpoint.path}")
        if endpoint.security:
            lines.append(f"        - نیاز به احراز هویت: {', '.join(endpoint.security)}")
        else:
            lines.append("        - نیاز به احراز هویت: خیر")
        
        return "\n".join(lines)


# ============================================================================
# SchemaToolGenerator - کلاس اصلی
# ============================================================================

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
    
    def analyze_openapi_schema(self) -> List[Endpoint]:
        """
        تحلیل OpenAPI schema و تولید Endpoint objects
        
        این متد از OpenAPI schema کامل استفاده می‌کند که شامل:
        - تمام endpoints (standard و custom actions)
        - پارامترهای path و query
        - requestBody با schema کامل
        - components/schemas با تمام جزئیات
        
        Returns:
            لیست Endpoint objects
        """
        if not self.schema:
            self.load_schema()
        
        # ایجاد SmartParameterExtractor
        extractor = SmartParameterExtractor(self.schema)
        
        endpoints = []
        
        # تحلیل paths
        if 'paths' in self.schema:
            for path, methods in self.schema['paths'].items():
                for method, details in methods.items():
                    if method.lower() in ['get', 'post', 'put', 'patch', 'delete']:
                        operation_id = details.get('operationId', '')
                        description = details.get('description', details.get('summary', '')) or f"{method.upper()} {path}"
                        tags = details.get('tags', [])
                        
                        # استخراج پارامترها با SmartParameterExtractor
                        path_params = extractor.extract_path_parameters(path, details)
                        query_params = extractor.extract_query_parameters(details)
                        body_params = extractor.extract_body_parameters(details)
                        
                        # ترکیب تمام پارامترها
                        all_params = path_params + query_params + body_params
                        
                        # تفکیک required و optional
                        required_params = [p for p in all_params if p.required and not p.nullable]
                        optional_params = [p for p in all_params if not p.required or p.nullable]
                        
                        # تولید نام Tool با نرمال‌سازی
                        tool_name = self.normalize_tool_name(operation_id, max_length=64)
                        if not tool_name:
                            # ساخت نام از path و method
                            path_parts = path.strip('/').split('/')
                            resource = path_parts[-1] if path_parts else 'resource'
                            fallback_name = f"{method.lower()}_{resource}".replace('-', '_').replace('{', '').replace('}', '')
                            tool_name = self.normalize_tool_name(fallback_name, max_length=64)
                        
                        # استخراج نام فارسی از description یا tags
                        name_fa = description.split('\n')[0].strip() if description else tool_name
                        if len(name_fa) > 50:  # اگر خیلی طولانی است، کوتاه کن
                            name_fa = name_fa[:50] + "..."
                        
                        # استخراج اطلاعات security
                        security = details.get('security', [])
                        security_info = []
                        for sec in security:
                            if isinstance(sec, dict):
                                security_info.extend(list(sec.keys()))
                        
                        # استخراج requestBody schema
                        request_body = None
                        if 'requestBody' in details:
                            request_body = details['requestBody']
                        
                        # استخراج responses
                        responses = details.get('responses', {})
                        
                        # استخراج examples (اگر وجود دارد)
                        examples = None
                        if 'x-examples' in details:
                            examples = details['x-examples']
                        elif isinstance(examples, list):
                            pass  # قبلاً list است
                        else:
                            examples = []
                        
                        # ساخت Endpoint object
                        endpoint = Endpoint(
                            path=path,
                            method=method.upper(),
                            operation_id=operation_id,
                            name_en=tool_name,
                            name_fa=name_fa,
                            description=description,
                            tags=tags,
                            parameters=all_params,
                            required_params=required_params,
                            optional_params=optional_params,
                            security=security_info,
                            request_body=request_body,
                            responses=responses,
                            examples=examples
                        )
                        
                        endpoints.append(endpoint)
        
        return endpoints
    
    def generate_tool_code(self, endpoint: Endpoint, target_service: str = 'django') -> str:
        """
        تولید کد Tool از Endpoint object
        
        Args:
            endpoint: Endpoint object با اطلاعات کامل
            target_service: 'django' یا 'standalone' (برای سرویس مستقل)
        
        Returns:
            کد Python برای Tool
        """
        if target_service == 'standalone':
            return self._generate_standalone_tool_code(endpoint)
        else:
            return self._generate_django_tool_code(endpoint)
    
    def _generate_django_tool_code(self, endpoint: Endpoint) -> str:
        """
        تولید کد Tool برای Django (نسخه فعلی)
        """
        tool_name = endpoint.name_en
        method = endpoint.method
        path = endpoint.path
        
        # ایجاد ToolTemplateGenerator برای docstring
        template_generator = ToolTemplateGenerator()
        docstring = template_generator.generate_tool_docstring(endpoint)
        
        # ساخت signature - جدا کردن required و optional از Parameter objects
        required_params = []
        optional_params = []
        path_params = endpoint.get_path_params()
        query_params = endpoint.get_query_params()
        body_params = endpoint.get_body_params()
        
        # ساخت signature برای path parameters (همیشه required)
        for param in path_params:
            python_type = param.get_python_type_hint()
            required_params.append(f"{param.name}: {python_type}")
        
        # ساخت signature برای required query/body parameters
        for param in query_params + body_params:
            if param.required and not param.nullable:
                python_type = param.get_python_type_hint()
                required_params.append(f"{param.name}: {python_type}")
        
        # ساخت signature برای optional parameters
        for param in query_params + body_params:
            if not param.required or param.nullable:
                python_type = param.get_python_type_hint()
                optional_params.append(f"{param.name}: {python_type} = None")
        
        # اضافه کردن request در آخر
        param_signatures = required_params + optional_params + ["request=None"]
        signature = ", ".join(param_signatures)
        
        # ساخت URL کامل با جایگزینی path parameters
        url_builder_parts = []
        url_builder_parts.append("        # ساخت URL کامل")
        url_builder_parts.append(f"        url = '{path}'")
        
        # جایگزینی path parameters در URL
        for param in path_params:
            url_builder_parts.append(f"        if {param.name} is not None:")
            url_builder_parts.append(f"            url = url.replace('{{{param.name}}}', str({param.name}))")
        
        url_builder_str = '\n'.join(url_builder_parts)
        
        # ساخت کد validation برای تمام پارامترها
        validation_code_parts = []
        for param in endpoint.parameters:
            validation = param.get_validation_code()
            if validation:
                validation_code_parts.append(validation)
        
        # join کردن validation codes (بدون indentation اضافی)
        validation_code_str = '\n'.join(validation_code_parts) if validation_code_parts else ""
        
        # ساخت کد برای query parameters (برای GET)
        query_params_code = []
        for param in query_params:
            query_params_code.append(f"        if {param.name} is not None:\n            kwargs['{param.name}'] = {param.name}")
        
        query_params_str = '\n'.join(query_params_code) if query_params_code else ""
        
        # ساخت کد برای body parameters (برای POST, PUT, PATCH)
        body_params_code = []
        for param in body_params:
            body_params_code.append(f"        if {param.name} is not None:\n            data['{param.name}'] = {param.name}")
        
        body_params_str = '\n'.join(body_params_code) if body_params_code else ""
        
        # ساخت body بر اساس method (با validation)
        if validation_code_str:
            validation_import = "        import re\n"
            # اضافه کردن indentation 8 space به هر خط validation
            validation_lines = validation_code_str.split('\n')
            indented_validation = '\n'.join(f"        {line}" if line.strip() else "" for line in validation_lines if line.strip())
            # validation_block باید در خط جدید و با indentation درست باشد
            validation_block = f"\n        # Validation\n{indented_validation}\n" if indented_validation else ""
        else:
            validation_import = ""
            validation_block = ""
        
        if method == 'GET':
            body = f'''    try:
{validation_import}        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        ){validation_block}{url_builder_str}
        
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
{validation_import}        from assistant.viewset_helper import (
            call_api_via_http,
            response_to_string
        ){validation_block}{url_builder_str}
        
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
    
    def _generate_standalone_tool_code(self, endpoint: Endpoint) -> str:
        """
        تولید کد Tool برای سرویس مستقل (standalone)
        
        این نسخه:
        - از HTTPToolsExecutor استفاده می‌کند
        - async است
        - api_token را به عنوان parameter دریافت می‌کند
        """
        tool_name = endpoint.name_en
        method = endpoint.method
        path = endpoint.path
        
        # ایجاد ToolTemplateGenerator برای docstring
        template_generator = ToolTemplateGenerator()
        docstring = template_generator.generate_tool_docstring(endpoint)
        
        # ساخت signature - جدا کردن required و optional از Parameter objects
        required_params = []
        optional_params = []
        path_params = endpoint.get_path_params()
        query_params = endpoint.get_query_params()
        body_params = endpoint.get_body_params()
        
        # اضافه کردن api_token به عنوان اولین parameter (required)
        required_params.append("api_token: str")
        
        # ساخت signature برای path parameters (همیشه required)
        for param in path_params:
            python_type = param.get_python_type_hint()
            required_params.append(f"{param.name}: {python_type}")
        
        # ساخت signature برای required query/body parameters
        for param in query_params + body_params:
            if param.required and not param.nullable:
                python_type = param.get_python_type_hint()
                required_params.append(f"{param.name}: {python_type}")
        
        # ساخت signature برای optional parameters
        for param in query_params + body_params:
            if not param.required or param.nullable:
                python_type = param.get_python_type_hint()
                optional_params.append(f"{param.name}: {python_type} = None")
        
        param_signatures = required_params + optional_params
        signature = ", ".join(param_signatures)
        
        # ساخت path با جایگزینی path parameters
        path_replacements = []
        for param in path_params:
            path_replacements.append(f"        if {param.name} is not None:\n            path = path.replace('{{{param.name}}}', str({param.name}))")
        
        path_builder_str = '\n'.join(path_replacements) if path_replacements else ""
        if path_builder_str:
            path_builder_str = f"        path = '{path}'\n{path_builder_str}"
        else:
            path_builder_str = f"        path = '{path}'"
        
        # ساخت کد validation برای تمام پارامترها (به جز api_token)
        validation_code_parts = []
        for param in endpoint.parameters:
            if param.name != 'api_token':  # api_token نیازی به validation ندارد
                validation = param.get_validation_code()
                if validation:
                    validation_code_parts.append(validation)
        
        # join کردن validation codes
        validation_code_str = '\n'.join(validation_code_parts) if validation_code_parts else ""
        
        # ساخت کد برای query parameters (برای GET)
        query_params_code = []
        for param in query_params:
            query_params_code.append(f"        if {param.name} is not None:\n            params['{param.name}'] = {param.name}")
        
        query_params_str = '\n'.join(query_params_code) if query_params_code else ""
        
        # ساخت کد برای body parameters (برای POST, PUT, PATCH)
        body_params_code = []
        for param in body_params:
            body_params_code.append(f"        if {param.name} is not None:\n            data['{param.name}'] = {param.name}")
        
        body_params_str = '\n'.join(body_params_code) if body_params_code else ""
        
        # ساخت body بر اساس method (با validation)
        if validation_code_str:
            validation_import = "        import re\n"
            validation_lines = validation_code_str.split('\n')
            indented_validation = '\n'.join(f"        {line}" if line.strip() else "" for line in validation_lines if line.strip())
            validation_block = f"\n        # Validation\n{indented_validation}\n" if indented_validation else ""
        else:
            validation_import = ""
            validation_block = ""
        
        if method == 'GET':
            body = f'''    try:
{validation_import}        from assistant_service.tools.executor import HTTPToolsExecutor
        from assistant_service.tools.response_formatter import format_response
        from django.conf import settings
        
        # ایجاد executor
        executor = HTTPToolsExecutor(
            base_url=getattr(settings, 'MAIN_APP_URL', 'http://localhost:8000'),
            api_token=api_token
        )
        
{validation_block}        # ساخت path با جایگزینی path parameters
{path_builder_str}
        
        # ساخت params برای query parameters
        params = {{}}
{query_params_str}
        
        # فراخوانی API endpoint از طریق HTTP
        result = await executor.execute(
            method='{method}',
            path=path,
            params=params if params else None
        )
        
        # بستن executor
        await executor.close()
        
        # تبدیل response به string
        return format_response(result)
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        else:
            body = f'''    try:
{validation_import}        from assistant_service.tools.executor import HTTPToolsExecutor
        from assistant_service.tools.response_formatter import format_response
        from django.conf import settings
        
        # ایجاد executor
        executor = HTTPToolsExecutor(
            base_url=getattr(settings, 'MAIN_APP_URL', 'http://localhost:8000'),
            api_token=api_token
        )
        
{validation_block}        # ساخت path با جایگزینی path parameters
{path_builder_str}
        
        # ساخت data برای request body
        data = {{}}
{body_params_str}
        
        # فراخوانی API endpoint از طریق HTTP
        result = await executor.execute(
            method='{method}',
            path=path,
            data=data if data else None
        )
        
        # بستن executor
        await executor.close()
        
        # تبدیل response به string
        return format_response(result)
    except Exception as e:
        return f"❌ خطا: {{str(e)}}"'''
        
        code = f'''@tool
async def {tool_name}({signature}) -> str:
    """
{docstring}
    """
{body}
'''
        
        return code
    
    def generate_all_tools(self, output_file: Optional[str] = None, target_service: str = 'django') -> str:
        """
        تولید Tools از OpenAPI schema
        
        Args:
            output_file: مسیر فایل خروجی
            target_service: 'django' یا 'standalone' (برای سرویس مستقل)
        
        Returns:
            کد کامل Tools
        """
        endpoints = self.analyze_openapi_schema()
        
        # شمارش اطلاعات استخراج شده
        total_endpoints = len(endpoints)
        total_params = sum(len(e.parameters) for e in endpoints)
        tags_count = len(set(tag for endpoint in endpoints for tag in endpoint.tags))
        
        # تعیین imports و توضیحات بر اساس target_service
        if target_service == 'standalone':
            imports = '''from langchain.tools import tool
from typing import Optional, Dict, Any
import re
from django.conf import settings

'''
            service_note = "نسخه مستقل - برای استفاده در سرویس دستیار هوش مصنوعی مستقل"
        else:
            imports = '''from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
import re
from django.conf import settings

'''
            service_note = "نسخه Django - برای استفاده در برنامه اصلی"
        
        all_code = f'''"""
Tools تولید شده خودکار از OpenAPI Schema
این فایل به صورت خودکار از schema.json تولید شده است.

{service_note}

📊 آمار استخراج شده:
   - تعداد کل Endpoints: {total_endpoints}
   - تعداد کل پارامترها: {total_params}
   - تعداد دسته‌بندی‌ها (Tags): {tags_count}

✅ اطلاعات شامل شده در هر Tool:
   - توضیحات کامل endpoint (description)
   - مسیر API (path)
   - متد HTTP (GET, POST, PUT, DELETE, PATCH)
   - تمام پارامترها (path, query, body) با نام فارسی
   - توضیحات کامل هر فیلد (description, type, format)
   - فیلدهای الزامی و اختیاری (required)
   - مقادیر enum (اگر وجود داشته باشد)
   - Validation rules (min/max, pattern, etc)
   - نیاز به احراز هویت (security)
   - کدهای وضعیت پاسخ (responses)
   - Operation ID
   - دسته‌بندی (tags)

⚠️  توجه: این Tools نیاز به پیاده‌سازی کامل دارند.
"""

{imports}'''
        
        # گروه‌بندی بر اساس tags
        tools_by_tag = {}
        for endpoint in endpoints:
            tags = endpoint.tags or ['other']
            tag = tags[0] if tags else 'other'
            if tag not in tools_by_tag:
                tools_by_tag[tag] = []
            tools_by_tag[tag].append(endpoint)
        
        # تولید کد برای هر گروه
        for tag, endpoint_list in tools_by_tag.items():
            all_code += f"\n# ===== Tools for {tag} ({len(endpoint_list)} endpoint) =====\n\n"
            
            for endpoint in endpoint_list:
                tool_code = self.generate_tool_code(endpoint, target_service=target_service)
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
            print(f"   - نوع سرویس: {target_service}")
            print(f"\n✅ هر Tool شامل:")
            print(f"   ✓ توضیحات کامل endpoint")
            print(f"   ✓ مسیر API و متد HTTP")
            print(f"   ✓ تمام پارامترها با توضیحات")
            print(f"   ✓ فیلدهای الزامی/اختیاری")
            print(f"   ✓ مقادیر enum و format ها")
            print(f"   ✓ نیاز به احراز هویت")
            print(f"   ✓ کدهای وضعیت پاسخ")
        
        return all_code
    
    def build_tool_document_content(self, endpoint: Endpoint) -> str:
        """
        ساخت محتوای بهینه برای RAG از Endpoint object
        
        Args:
            endpoint: Endpoint object با اطلاعات کامل
        
        Returns:
            محتوای متنی بهینه برای semantic search
        """
        tool_name = endpoint.name_en
        description = endpoint.description
        method = endpoint.method
        path = endpoint.path
        tags = endpoint.tags
        operation_id = endpoint.operation_id
        security = endpoint.security
        params = endpoint.parameters
        
        content_parts = []
        
        # 1. عنوان و توضیحات اصلی
        content_parts.append(f"Tool: {tool_name}")
        if description:
            # استخراج عنوان کوتاه و توضیحات کامل
            desc_lines = description.split('\n')
            short_title = desc_lines[0].strip() if desc_lines else ""
            detailed_desc = '\n'.join(desc_lines[1:]).strip() if len(desc_lines) > 1 else ""
            
            content_parts.append(f"Description: {short_title}")
            if detailed_desc:
                content_parts.append(f"\n{detailed_desc}")
        
        # 2. استخراج قابلیت‌ها از description
        if description:
            # جستجوی بخش "قابلیت‌ها" یا "Capabilities"
            desc_lower = description.lower()
            if 'قابلیت' in desc_lower or 'capabilit' in desc_lower:
                lines = description.split('\n')
                in_capabilities = False
                capabilities = []
                for line in lines:
                    line_lower = line.lower()
                    if 'قابلیت' in line_lower or 'capabilit' in line_lower:
                        in_capabilities = True
                        continue
                    if in_capabilities:
                        if line.strip().startswith('-') or line.strip().startswith('*'):
                            capabilities.append(line.strip())
                        elif line.strip() and not line.strip().startswith('سناریو') and not line.strip().startswith('مثال'):
                            if not any(keyword in line_lower for keyword in ['سناریو', 'مثال', 'نکات', 'scenario', 'example', 'note']):
                                capabilities.append(line.strip())
                        else:
                            if line.strip() and any(keyword in line_lower for keyword in ['سناریو', 'مثال', 'نکات', 'scenario', 'example', 'note']):
                                break
                
                if capabilities:
                    content_parts.append("\nقابلیت‌ها:")
                    for cap in capabilities[:10]:  # محدود کردن به 10 مورد
                        content_parts.append(f"- {cap}")
        
        # 3. استخراج سناریوهای استفاده
        if description:
            lines = description.split('\n')
            in_use_cases = False
            use_cases = []
            for line in lines:
                line_lower = line.lower()
                if 'سناریو' in line_lower or 'use case' in line_lower or 'scenario' in line_lower:
                    in_use_cases = True
                    continue
                if in_use_cases:
                    if line.strip().startswith('-') or line.strip().startswith('*'):
                        use_cases.append(line.strip())
                    elif line.strip() and not line.strip().startswith('مثال') and not line.strip().startswith('نکات'):
                        if not any(keyword in line_lower for keyword in ['مثال', 'نکات', 'example', 'note']):
                            use_cases.append(line.strip())
                    else:
                        if line.strip() and any(keyword in line_lower for keyword in ['مثال', 'نکات', 'example', 'note']):
                            break
            
            if use_cases:
                content_parts.append("\nسناریوهای استفاده:")
                for use_case in use_cases[:10]:  # محدود کردن به 10 مورد
                    content_parts.append(f"- {use_case}")
        
        # 4. پارامترها با توضیحات کامل
        if params:
            content_parts.append("\nپارامترها:")
            for param in params:
                python_type = param.get_python_type_hint()
                
                # ساخت توضیحات پارامتر
                param_line = f"- {param.name} ({param.name_fa}) ({python_type}"
                if not param.required or param.nullable:
                    param_line += ", optional"
                param_line += ")"
                
                if param.description:
                    param_line += f": {param.description}"
                
                if param.format:
                    if param.format == 'date':
                        param_line += " (فرمت: YYYY-MM-DD)"
                    elif param.format == 'date-time':
                        param_line += " (فرمت: ISO 8601)"
                    elif param.format == 'email':
                        param_line += " (ایمیل)"
                
                if param.enum_values:
                    param_line += f" [مقادیر معتبر: {', '.join(map(str, param.enum_values))}]"
                
                if param.min_value is not None or param.max_value is not None:
                    range_parts = []
                    if param.min_value is not None:
                        range_parts.append(f"حداقل: {param.min_value}")
                    if param.max_value is not None:
                        range_parts.append(f"حداکثر: {param.max_value}")
                    if range_parts:
                        param_line += f" [{', '.join(range_parts)}]"
                
                if param.required and not param.nullable:
                    param_line += " [required]"
                
                content_parts.append(param_line)
        
        # 5. مثال‌های استفاده - بررسی اینکه آیا در description وجود دارد یا نه
        has_examples_in_desc = False
        if description:
            desc_lower = description.lower()
            # بررسی اینکه آیا در description "مثال:" یا "مثال‌های استفاده:" وجود دارد
            if ('مثال:' in desc_lower or 'example:' in desc_lower or 
                'مثال‌های استفاده:' in desc_lower or 'examples:' in desc_lower):
                has_examples_in_desc = True
        
        # اگر مثال در description نبود، از endpoint.examples یا ساخت ساده استفاده کن
        examples_to_add = []
        if not has_examples_in_desc:
            if endpoint.examples:
                for example in endpoint.examples[:5]:
                    if isinstance(example, dict):
                        desc = example.get('description', '')
                        req = example.get('request', '')
                        if desc and req:
                            examples_to_add.append(f"{desc}: {req}")
                        elif req:
                            examples_to_add.append(req)
                    else:
                        examples_to_add.append(str(example))
            
            # اگر هنوز مثال نداریم، یک مثال ساده بساز
            if not examples_to_add:
                example_parts = [tool_name + "("]
                param_examples = []
                for param in params[:5]:  # فقط 5 پارامتر اول
                    if param.name != 'request':
                        if param.type == 'string':
                            param_examples.append(f"{param.name}='value'")
                        elif param.type == 'integer':
                            param_examples.append(f"{param.name}=1")
                        elif param.type == 'boolean':
                            param_examples.append(f"{param.name}=True")
                        else:
                            param_examples.append(f"{param.name}=value")
                example_parts.append(", ".join(param_examples))
                example_parts.append(")")
                examples_to_add.append("".join(example_parts))
        
        # اضافه کردن مثال‌ها (فقط اگر در description نبودند)
        if examples_to_add and not has_examples_in_desc:
            content_parts.append("\nمثال‌های استفاده:")
            for example in examples_to_add[:5]:  # محدود کردن به 5 مثال
                content_parts.append(f"- {example}")
        
        # 6. نکات مهم - بررسی اینکه آیا در description وجود دارد یا نه
        has_notes_in_desc = False
        if description:
            desc_lower = description.lower()
            # بررسی اینکه آیا در description "نکات:" یا "نکات مهم:" وجود دارد
            if ('نکات:' in desc_lower or 'note:' in desc_lower or 'important:' in desc_lower or
                'نکات مهم:' in desc_lower or 'notes:' in desc_lower):
                has_notes_in_desc = True
        
        # اگر نکات در description نبود، از security استفاده کن
        notes_to_add = []
        if not has_notes_in_desc:
            if security:
                notes_to_add.append("نیاز به احراز هویت دارد")
        
        # اضافه کردن نکات (فقط اگر در description نبودند)
        if notes_to_add and not has_notes_in_desc:
            content_parts.append("\nنکات مهم:")
            for note in notes_to_add[:10]:  # محدود کردن به 10 نکته
                content_parts.append(f"- {note}")
        
        # 7. API endpoint
        if path:
            content_parts.append(f"\nAPI Endpoint: {method} {path}")
        
        if operation_id:
            content_parts.append(f"Operation ID: {operation_id}")
        
        if tags:
            content_parts.append(f"دسته‌بندی: {', '.join(tags)}")
        
        return "\n".join(content_parts)
    
    def _save_json_with_multiline_strings(self, output_file: str, documents: List[Dict[str, Any]]):
        """
        ذخیره JSON با فرمت چند خطی برای page_content
        
        این متد JSON را به صورت چند خطی ذخیره می‌کند تا خواندن آن راحت‌تر باشد.
        برای page_content از array از خطوط استفاده می‌کند که خوانایی بهتری دارد.
        
        توجه: برای استفاده در RAG، باید page_content را از array به string تبدیل کنید:
        page_content = '\\n'.join(doc['page_content']) if isinstance(doc['page_content'], list) else doc['page_content']
        
        Args:
            output_file: مسیر فایل خروجی
            documents: لیست Documents
        """
        # تبدیل page_content از string به array از خطوط برای خوانایی بهتر
        formatted_documents = []
        for doc in documents:
            formatted_doc = doc.copy()
            if 'page_content' in formatted_doc and isinstance(formatted_doc['page_content'], str):
                # تبدیل string به array از خطوط
                formatted_doc['page_content'] = formatted_doc['page_content'].split('\n')
            formatted_documents.append(formatted_doc)
        
        # ذخیره با indent
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_documents, f, ensure_ascii=False, indent=2)
    
    def _save_json_for_rag(self, output_file: str, documents: List[Dict[str, Any]]):
        """
        ذخیره JSON به صورت فشرده و مناسب برای استفاده در RAG
        
        این متد JSON را به صورت compact ذخیره می‌کند و page_content را
        به صورت string نگه می‌دارد (نه array) که مناسب برای استفاده مستقیم
        در سیستم‌های RAG و Vector Database است.
        
        Args:
            output_file: مسیر فایل خروجی
            documents: لیست Documents
        """
        # اطمینان از اینکه page_content به صورت string است
        formatted_documents = []
        for doc in documents:
            formatted_doc = doc.copy()
            if 'page_content' in formatted_doc:
                # اگر array است، به string تبدیل کن
                if isinstance(formatted_doc['page_content'], list):
                    formatted_doc['page_content'] = '\n'.join(formatted_doc['page_content'])
                # اطمینان از اینکه string است
                elif not isinstance(formatted_doc['page_content'], str):
                    formatted_doc['page_content'] = str(formatted_doc['page_content'])
            formatted_documents.append(formatted_doc)
        
        # ذخیره به صورت compact (بدون indent)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_documents, f, ensure_ascii=False, separators=(',', ':'))
    
    def generate_tool_documents_for_rag(self, output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        تولید مستندات Tools برای استفاده در RAG/Vector Database
        
        این متد اطلاعات کامل tools را استخراج کرده و به فرمت LangChain Document
        تبدیل می‌کند که مناسب برای استفاده در RAG pipeline است.
        
        هر Document شامل:
        - page_content: محتوای متنی بهینه برای semantic search
          شامل: نام tool، توضیحات، قابلیت‌ها، سناریوها، پارامترها، مثال‌ها، نکات
        - metadata: اطلاعات ساختاریافته برای فیلتر و دسته‌بندی
          شامل: tool_name, category, method, path, operation_id, tags, parameters
        
        Args:
            output_file: مسیر فایل JSON خروجی (اختیاری)
                       اگر مشخص شود، دو فایل ایجاد می‌شود:
                       - {output_file}_readable.json: فرمت چند خطی برای خواندن انسان
                       - {output_file}: فرمت فشرده با page_content به صورت string برای RAG
        
        Returns:
            لیست Documents برای RAG (هر Document شامل page_content و metadata)
        
        مثال استفاده:
            >>> generator = SchemaToolGenerator()
            >>> documents = generator.generate_tool_documents_for_rag('tool_docs.json')
            >>> # استفاده در RAG pipeline
            >>> from langchain_core.documents import Document
            >>> from langchain_community.vectorstores import Chroma
            >>> 
            >>> # تبدیل به Document objects
            >>> langchain_docs = [
            ...     Document(page_content=doc['page_content'], metadata=doc['metadata'])
            ...     for doc in documents
            ... ]
            >>> 
            >>> # ایجاد vector store
            >>> vector_store = Chroma.from_documents(
            ...     documents=langchain_docs,
            ...     embedding=embeddings,
            ...     persist_directory='tool_rag_db'
            ... )
        """
        endpoints = self.analyze_openapi_schema()
        
        documents = []
        
        for endpoint in endpoints:
            # ساخت محتوای قابل جستجو
            page_content = self.build_tool_document_content(endpoint)
            
            # استخراج پارامترها برای metadata
            params_metadata = []
            for param in endpoint.parameters:
                if param.name != 'request':  # حذف request از metadata
                    params_metadata.append({
                        'name': param.name,
                        'name_fa': param.name_fa,
                        'type': param.type,
                        'required': param.required and not param.nullable,
                        'description': param.description,
                        'location': param.location.value,
                        'enum_values': param.enum_values,
                        'min_value': param.min_value,
                        'max_value': param.max_value,
                    })
            
            # ساخت metadata
            tags = endpoint.tags or []
            category = tags[0] if tags else 'other'
            
            metadata = {
                'tool_name': endpoint.name_en,
                'category': category,
                'method': endpoint.method,
                'path': endpoint.path,
                'operation_id': endpoint.operation_id,
                'tags': tags,
                'has_auth': len(endpoint.security) > 0,
                'parameters': params_metadata,
                'response_codes': list(endpoint.responses.keys()) if endpoint.responses else []
            }
            
            documents.append({
                'page_content': page_content,
                'metadata': metadata
            })
        
        # ذخیره در دو فایل: یکی خوانا برای انسان، یکی فشرده برای RAG
        if output_file:
            # تعیین نام فایل خوانا
            if output_file.endswith('.json'):
                readable_file = output_file.replace('.json', '_readable.json')
            else:
                readable_file = f"{output_file}_readable.json"
            
            # ذخیره فایل خوانا (چند خطی با array)
            self._save_json_with_multiline_strings(readable_file, documents)
            
            # ذخیره فایل RAG (فشرده با string)
            self._save_json_for_rag(output_file, documents)
            
            print(f"✅ مستندات RAG در دو فایل ذخیره شد:")
            print(f"   📖 خوانا (برای انسان): {readable_file}")
            print(f"   🤖 فشرده (برای RAG): {output_file}")
            print(f"📊 تعداد کل Documents: {len(documents)}")
            
            # نمایش خلاصه
            categories = {}
            for doc in documents:
                cat = doc['metadata'].get('category', 'other')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\n📁 دسته‌بندی Documents:")
            for cat, count in sorted(categories.items()):
                print(f"   - {cat}: {count} tool")
        
        return documents


def main():
    """تابع اصلی برای اجرای schema-based generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='تولید خودکار Tools از OpenAPI Schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌ها:
  # تولید tools برای Django (پیش‌فرض)
  python schema_tool_generator.py --output generated_tools_from_schema.py
  
  # تولید tools برای سرویس مستقل
  python schema_tool_generator.py --output generated_tools_from_schema.py --target standalone
  
  # تولید مستندات RAG
  python schema_tool_generator.py --rag --rag-output tool_documents.json
  
  # تولید هر دو برای سرویس مستقل
  python schema_tool_generator.py --output tools.py --rag --rag-output rag_docs.json --target standalone
        """
    )
    parser.add_argument('--schema', type=str, default=None,
                       help='مسیر فایل schema.json (پیش‌فرض: schema.json در root پروژه)')
    parser.add_argument('--output', type=str, default=None,
                       help='مسیر فایل خروجی برای tools (پیش‌فرض: generated_tools_from_schema.py)')
    parser.add_argument('--target', type=str, default='django', choices=['django', 'standalone'],
                       help='نوع سرویس هدف: django (پیش‌فرض) یا standalone (برای سرویس مستقل)')
    parser.add_argument('--rag', action='store_true',
                       help='تولید مستندات RAG از tools')
    parser.add_argument('--rag-output', type=str, default=None,
                       help='مسیر فایل JSON خروجی برای مستندات RAG (پیش‌فرض: tool_documents_for_rag.json)')
    
    args = parser.parse_args()
    
    generator = SchemaToolGenerator(schema_path=args.schema)
    
    # تولید tools (اگر output مشخص شده یا rag مشخص نشده)
    if args.output or not args.rag:
        if not args.output:
            # تعیین مسیر خروجی بر اساس target
            if args.target == 'standalone':
                # برای standalone، در پوشه سرویس مستقل ذخیره می‌شود
                args.output = str(project_root.parent / 'django_ai_assistant_service' / 'assistant_service' / 'tools' / 'generated' / 'generated_tools_from_schema.py')
            else:
                args.output = str(project_root / 'assistant' / 'generated' / 'generated_tools_from_schema.py')
        
        print("🔧 در حال تولید Tools از OpenAPI Schema...")
        print("   ✅ استفاده از schema کامل drf-spectacular")
        print("   ✅ شامل تمام endpoints، parameters، requestBody و schemas")
        print(f"   ✅ نوع سرویس: {args.target}\n")
        
        code = generator.generate_all_tools(output_file=args.output, target_service=args.target)
        
        print(f"\n📁 فایل خروجی Tools: {args.output}")
        if args.target == 'standalone':
            print("   ✅ نسخه مستقل - برای استفاده در سرویس دستیار هوش مصنوعی")
            print("   ✅ از HTTPToolsExecutor استفاده می‌کند")
            print("   ✅ async functions")
        else:
            print("   ✅ نسخه Django - برای استفاده در برنامه اصلی")
        print("\n⚠️  توجه: این Tools به صورت خودکار تولید شده‌اند و نیاز به بررسی و تکمیل دارند.")
    
    # تولید مستندات RAG
    if args.rag:
        if not args.rag_output:
            # تعیین مسیر خروجی RAG بر اساس target
            if args.target == 'standalone':
                args.rag_output = str(project_root.parent / 'django_ai_assistant_service' / 'assistant_service' / 'tools' / 'generated' / 'tool_documents_for_rag.json')
            else:
                args.rag_output = str(project_root / 'assistant' / 'generated' / 'tool_documents_for_rag.json')
        
        print("\n" + "="*80)
        print("📚 در حال تولید مستندات RAG از Tools...")
        print("   ✅ فرمت: LangChain Document")
        print("   ✅ شامل: page_content (semantic search) + metadata (filtering)")
        print(f"   ✅ نوع سرویس: {args.target}\n")
        
        documents = generator.generate_tool_documents_for_rag(output_file=args.rag_output)
        
        print(f"\n📁 فایل خروجی RAG: {args.rag_output}")
        print(f"✅ {len(documents)} Document برای استفاده در RAG pipeline آماده است")
        if args.target == 'standalone':
            print("   ✅ مناسب برای استفاده در سرویس دستیار هوش مصنوعی مستقل")
        print("\n💡 نحوه استفاده:")
        if args.target == 'standalone':
            print("   from assistant_service.rag.pipeline import RAGPipeline")
            print("   rag = RAGPipeline()")
            print("   # بارگذاری documents از JSON و استفاده در vector store")
        else:
            print("   from assistant.generators.schema_tool_generator import SchemaToolGenerator")
            print("   generator = SchemaToolGenerator()")
            print("   documents = generator.generate_tool_documents_for_rag()")
            print("   # سپس از documents در RAG pipeline استفاده کنید")


if __name__ == "__main__":
    main()

