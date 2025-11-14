"""
ProjectManager: کلاس helper برای مدیریت پروژه جاری کاربر
"""

from .models import Project


class ProjectManager:
    """کلاس helper برای مدیریت پروژه کاربر"""
    
    @staticmethod
    def get_current_project(request):
        """
        دریافت پروژه جاری از session یا پروژه فعال
        
        Args:
            request: درخواست HTTP
            
        Returns:
            Project: پروژه جاری یا None
        """
        project_id = request.session.get('current_project_id')
        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if project:
                return project
        
        # اگر در session نبود، از پروژه فعال استفاده کن
        return Project.get_active_project()
    
    @staticmethod
    def set_current_project(request, project_id):
        """
        تنظیم پروژه جاری در session
        
        Args:
            request: درخواست HTTP
            project_id: شناسه پروژه
        """
        request.session['current_project_id'] = project_id
    
    @staticmethod
    def get_all_projects():
        """
        دریافت تمام پروژه‌ها
        
        Returns:
            QuerySet: لیست تمام پروژه‌ها به ترتیب نام
        """
        return Project.objects.all().order_by('name')

