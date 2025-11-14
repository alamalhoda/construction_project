"""
Context processors برای در دسترس قرار دادن متغیرهای سراسری در templates
"""
from django.conf import settings


def project_settings(request):
    """
    Context processor برای در دسترس قرار دادن تنظیمات پروژه در تمام templates
    """
    return {
        'PROJECT_TITLE': settings.PROJECT_TITLE,
        'PROJECT_DESCRIPTION': settings.PROJECT_DESCRIPTION,
        'PROJECT_LOGO': settings.PROJECT_LOGO,
        'PROJECT_LOGO_ALT': settings.PROJECT_LOGO_ALT,
    }


def project_context(request):
    """
    Context processor برای در دسترس قرار دادن اطلاعات پروژه جاری در تمام templates
    """
    from construction.project_manager import ProjectManager
    
    return {
        'current_project': ProjectManager.get_current_project(request),
        'all_projects': ProjectManager.get_all_projects(),
    }
