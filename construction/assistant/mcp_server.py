"""
MCP Server برای ارتباط با سایر AI ها
Model Context Protocol Server
"""

import json
from typing import Dict, List, Any, Optional
from mcp.server import Server
from mcp.server.models import Tool, Resource, Prompt
from mcp.types import Tool as MCPTool, Resource as MCPResource, Prompt as MCPPrompt
from construction.models import Expense, Period, Investor, Project, Transaction
from construction.project_manager import ProjectManager


class ConstructionMCPServer:
    """MCP Server برای پروژه ساخت‌وساز"""
    
    def __init__(self, project_id: Optional[int] = None):
        """
        Args:
            project_id: شناسه پروژه (اختیاری)
        """
        self.project_id = project_id
        self.server = Server("construction-project")
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    def _register_tools(self):
        """ثبت Tools برای MCP"""
        
        @self.server.tool()
        async def get_project_info(project_id: int) -> Dict[str, Any]:
            """دریافت اطلاعات یک پروژه"""
            try:
                project = Project.objects.get(id=project_id)
                return {
                    "id": project.id,
                    "name": project.name,
                    "start_date_shamsi": str(project.start_date_shamsi),
                    "end_date_shamsi": str(project.end_date_shamsi),
                    "total_infrastructure": float(project.total_infrastructure),
                    "description": project.description or ""
                }
            except Project.DoesNotExist:
                return {"error": f"پروژه با شناسه {project_id} یافت نشد"}
        
        @self.server.tool()
        async def list_projects() -> List[Dict[str, Any]]:
            """لیست تمام پروژه‌ها"""
            projects = Project.objects.all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "start_date_shamsi": str(p.start_date_shamsi),
                    "end_date_shamsi": str(p.end_date_shamsi)
                }
                for p in projects
            ]
        
        @self.server.tool()
        async def get_expense(expense_id: int) -> Dict[str, Any]:
            """دریافت اطلاعات یک هزینه"""
            try:
                expense = Expense.objects.select_related('project', 'period').get(id=expense_id)
                return {
                    "id": expense.id,
                    "project_id": expense.project.id,
                    "project_name": expense.project.name,
                    "period_id": expense.period.id,
                    "period_label": expense.period.label,
                    "expense_type": expense.expense_type,
                    "expense_type_display": expense.get_expense_type_display(),
                    "amount": float(expense.amount),
                    "description": expense.description or "",
                    "created_at": expense.created_at.isoformat()
                }
            except Expense.DoesNotExist:
                return {"error": f"هزینه با شناسه {expense_id} یافت نشد"}
        
        @self.server.tool()
        async def create_expense(
            project_id: int,
            period_id: int,
            expense_type: str,
            amount: float,
            description: str = ""
        ) -> Dict[str, Any]:
            """ایجاد یک هزینه جدید"""
            try:
                project = Project.objects.get(id=project_id)
                period = Period.objects.get(id=period_id)
                
                # بررسی معتبر بودن expense_type
                valid_types = [choice[0] for choice in Expense.EXPENSE_TYPES]
                if expense_type not in valid_types:
                    return {
                        "error": f"نوع هزینه نامعتبر است. انواع معتبر: {', '.join(valid_types)}"
                    }
                
                expense = Expense.objects.create(
                    project=project,
                    period=period,
                    expense_type=expense_type,
                    amount=amount,
                    description=description
                )
                
                return {
                    "success": True,
                    "id": expense.id,
                    "message": "هزینه با موفقیت ایجاد شد"
                }
            except Project.DoesNotExist:
                return {"error": f"پروژه با شناسه {project_id} یافت نشد"}
            except Period.DoesNotExist:
                return {"error": f"دوره با شناسه {period_id} یافت نشد"}
            except Exception as e:
                return {"error": f"خطا در ایجاد هزینه: {str(e)}"}
        
        @self.server.tool()
        async def get_investor_info(investor_id: int) -> Dict[str, Any]:
            """دریافت اطلاعات یک سرمایه‌گذار"""
            try:
                investor = Investor.objects.select_related('project').prefetch_related('units').get(id=investor_id)
                return {
                    "id": investor.id,
                    "first_name": investor.first_name,
                    "last_name": investor.last_name,
                    "full_name": f"{investor.first_name} {investor.last_name}",
                    "phone": investor.phone,
                    "email": investor.email or "",
                    "project_id": investor.project.id,
                    "project_name": investor.project.name,
                    "participation_type": investor.participation_type,
                    "units": [{"id": u.id, "name": u.name} for u in investor.units.all()],
                    "description": investor.description or ""
                }
            except Investor.DoesNotExist:
                return {"error": f"سرمایه‌گذار با شناسه {investor_id} یافت نشد"}
        
        @self.server.tool()
        async def get_transaction_info(transaction_id: int) -> Dict[str, Any]:
            """دریافت اطلاعات یک تراکنش"""
            try:
                transaction = Transaction.objects.select_related('project', 'investor').get(id=transaction_id)
                return {
                    "id": transaction.id,
                    "project_id": transaction.project.id,
                    "project_name": transaction.project.name,
                    "investor_id": transaction.investor.id,
                    "investor_name": f"{transaction.investor.first_name} {transaction.investor.last_name}",
                    "transaction_type": transaction.transaction_type,
                    "amount": float(transaction.amount),
                    "date_shamsi": str(transaction.date_shamsi),
                    "description": transaction.description or ""
                }
            except Transaction.DoesNotExist:
                return {"error": f"تراکنش با شناسه {transaction_id} یافت نشد"}
        
        @self.server.tool()
        async def get_project_statistics(project_id: int) -> Dict[str, Any]:
            """دریافت آمار پروژه"""
            try:
                from django.db.models import Sum, Count
                
                project = Project.objects.get(id=project_id)
                
                # آمار هزینه‌ها
                expenses_stats = Expense.objects.filter(project=project).aggregate(
                    total=Sum('amount'),
                    count=Count('id')
                )
                
                # آمار سرمایه‌گذاران
                investor_count = Investor.objects.filter(project=project).count()
                
                # آمار واحدها
                unit_count = project.unit_set.count()
                
                # آمار دوره‌ها
                period_count = Period.objects.filter(project=project).count()
                
                return {
                    "project_id": project.id,
                    "project_name": project.name,
                    "total_expenses": float(expenses_stats['total'] or 0),
                    "expense_count": expenses_stats['count'] or 0,
                    "investor_count": investor_count,
                    "unit_count": unit_count,
                    "period_count": period_count
                }
            except Project.DoesNotExist:
                return {"error": f"پروژه با شناسه {project_id} یافت نشد"}
    
    def _register_resources(self):
        """ثبت Resources برای MCP"""
        
        @self.server.resource("project://{project_id}")
        async def get_project_resource(project_id: str) -> str:
            """Resource برای اطلاعات پروژه"""
            try:
                project = Project.objects.get(id=int(project_id))
                return json.dumps({
                    "id": project.id,
                    "name": project.name,
                    "start_date_shamsi": str(project.start_date_shamsi),
                    "end_date_shamsi": str(project.end_date_shamsi),
                    "total_infrastructure": float(project.total_infrastructure),
                    "description": project.description or ""
                }, ensure_ascii=False)
            except Project.DoesNotExist:
                return json.dumps({"error": f"پروژه با شناسه {project_id} یافت نشد"})
        
        @self.server.resource("expense://{expense_id}")
        async def get_expense_resource(expense_id: str) -> str:
            """Resource برای اطلاعات هزینه"""
            try:
                expense = Expense.objects.select_related('project', 'period').get(id=int(expense_id))
                return json.dumps({
                    "id": expense.id,
                    "project_id": expense.project.id,
                    "project_name": expense.project.name,
                    "period_id": expense.period.id,
                    "period_label": expense.period.label,
                    "expense_type": expense.expense_type,
                    "expense_type_display": expense.get_expense_type_display(),
                    "amount": float(expense.amount),
                    "description": expense.description or ""
                }, ensure_ascii=False)
            except Expense.DoesNotExist:
                return json.dumps({"error": f"هزینه با شناسه {expense_id} یافت نشد"})
        
        @self.server.resource("investor://{investor_id}")
        async def get_investor_resource(investor_id: str) -> str:
            """Resource برای اطلاعات سرمایه‌گذار"""
            try:
                investor = Investor.objects.select_related('project').get(id=int(investor_id))
                return json.dumps({
                    "id": investor.id,
                    "first_name": investor.first_name,
                    "last_name": investor.last_name,
                    "phone": investor.phone,
                    "email": investor.email or "",
                    "project_id": investor.project.id,
                    "project_name": investor.project.name
                }, ensure_ascii=False)
            except Investor.DoesNotExist:
                return json.dumps({"error": f"سرمایه‌گذار با شناسه {investor_id} یافت نشد"})
    
    def _register_prompts(self):
        """ثبت Prompts برای MCP"""
        
        @self.server.prompt("project_summary")
        async def project_summary_prompt(project_id: str) -> str:
            """Prompt برای خلاصه پروژه"""
            try:
                project = Project.objects.get(id=int(project_id))
                from django.db.models import Sum, Count
                
                expenses_stats = Expense.objects.filter(project=project).aggregate(
                    total=Sum('amount'),
                    count=Count('id')
                )
                
                return f"""خلاصه پروژه {project.name}:

- تاریخ شروع: {project.start_date_shamsi}
- تاریخ پایان: {project.end_date_shamsi}
- مجموع هزینه‌ها: {expenses_stats['total'] or 0:,.0f} تومان
- تعداد هزینه‌ها: {expenses_stats['count'] or 0}
- تعداد سرمایه‌گذاران: {Investor.objects.filter(project=project).count()}
- تعداد واحدها: {project.unit_set.count()}
"""
            except Project.DoesNotExist:
                return f"پروژه با شناسه {project_id} یافت نشد"
        
        @self.server.prompt("expense_analysis")
        async def expense_analysis_prompt(project_id: str) -> str:
            """Prompt برای تحلیل هزینه‌ها"""
            try:
                project = Project.objects.get(id=int(project_id))
                from django.db.models import Sum
                
                expenses_by_type = {}
                for expense_type, display_name in Expense.EXPENSE_TYPES:
                    total = Expense.objects.filter(
                        project=project,
                        expense_type=expense_type
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    expenses_by_type[display_name] = float(total)
                
                result = f"تحلیل هزینه‌های پروژه {project.name}:\n\n"
                for expense_type, total in expenses_by_type.items():
                    if total > 0:
                        result += f"- {expense_type}: {total:,.0f} تومان\n"
                
                return result
            except Project.DoesNotExist:
                return f"پروژه با شناسه {project_id} یافت نشد"
    
    async def run(self):
        """اجرای MCP Server"""
        await self.server.run()


def create_mcp_server(project_id: Optional[int] = None) -> ConstructionMCPServer:
    """
    Factory function برای ایجاد MCP Server
    
    Args:
        project_id: شناسه پروژه (اختیاری)
    
    Returns:
        ConstructionMCPServer instance
    """
    return ConstructionMCPServer(project_id=project_id)

