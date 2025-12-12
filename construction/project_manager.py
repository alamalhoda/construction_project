"""
ProjectManager: کلاس helper برای مدیریت پروژه جاری کاربر
"""

from .models import Project


class ProjectManager:
    """کلاس helper برای مدیریت پروژه کاربر"""
    
    @staticmethod
    def get_current_project(request):
        """
        دریافت پروژه جاری از session یا header
        
        اولویت:
        1. Header X-Project-ID (برای API calls با token authentication)
        2. Session current_project_id (برای web requests)
        
        Args:
            request: درخواست HTTP
            
        Returns:
            Project: پروژه جاری یا None
        """
        import logging
        logger = logging.getLogger(__name__)
        
        project_id = None
        
        # اولویت 1: بررسی header X-Project-ID (برای API calls با token authentication)
        if hasattr(request, 'META'):
            project_id_header = request.META.get('HTTP_X_PROJECT_ID') or request.META.get('X-Project-ID')
            if project_id_header:
                try:
                    project_id = int(project_id_header)
                    logger.info(f"🔍 ProjectManager.get_current_project - project_id از header: {project_id}")
                except (ValueError, TypeError):
                    logger.warning(f"⚠️ project_id در header نامعتبر است: {project_id_header}")
        
        # اولویت 2: بررسی session (برای web requests)
        if not project_id and hasattr(request, 'session'):
            project_id = request.session.get('current_project_id')
            if project_id:
                logger.info(f"🔍 ProjectManager.get_current_project - project_id از session: {project_id}")
        
        # لاگ کردن تمام کلیدهای session برای دیباگ (فقط اگر از session استفاده نشد)
        if not project_id and hasattr(request, 'session') and hasattr(request.session, 'keys'):
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
            if not hasattr(request, 'session'):
                logger.warning("⚠️ ProjectManager.get_current_project - request.session وجود ندارد و header هم موجود نیست")
            else:
                all_keys = list(request.session.keys()) if hasattr(request.session, 'keys') else 'N/A'
                logger.warning(f"⚠️ هیچ project_id در session یا header یافت نشد - تمام کلیدهای session: {all_keys}")
        
        # اگر در session یا header نبود، None برگردان
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

