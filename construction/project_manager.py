"""
ProjectManager: کلاس helper برای مدیریت پروژه جاری کاربر
"""

from .models import Project


class ProjectManager:
    """کلاس helper برای مدیریت پروژه کاربر"""
    
    @staticmethod
    def get_current_project(request):
        """
        دریافت پروژه جاری از session
        
        Args:
            request: درخواست HTTP
            
        Returns:
            Project: پروژه جاری یا None
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # بررسی وجود session
        if not hasattr(request, 'session'):
            logger.warning("⚠️ ProjectManager.get_current_project - request.session وجود ندارد")
            return None
        
        project_id = request.session.get('current_project_id')
        logger.info(f"🔍 ProjectManager.get_current_project - project_id از session: {project_id}")
        
        # لاگ کردن تمام کلیدهای session برای دیباگ
        if hasattr(request.session, 'keys'):
            all_keys = list(request.session.keys())
            logger.info(f"🔍 تمام کلیدهای session: {all_keys}")
        
        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if project:
                logger.info(f"✅ پروژه جاری یافت شد: {project.id} - {project.name}")
                return project
            else:
                logger.warning(f"⚠️ پروژه با id={project_id} در پایگاه داده یافت نشد")
        else:
            all_keys = list(request.session.keys()) if hasattr(request.session, 'keys') else 'N/A'
            logger.warning(f"⚠️ هیچ project_id در session یافت نشد - تمام کلیدها: {all_keys}")
        
        # اگر در session نبود، None برگردان
        # کاربر باید ابتدا یک پروژه را انتخاب کند
        return None
    
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

