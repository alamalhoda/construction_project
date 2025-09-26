"""
سیستم احراز هویت API
API Authentication System for Construction Project
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.middleware.csrf import get_token
import logging

logger = logging.getLogger('django.security')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_csrf_token(request):
    """
    دریافت CSRF Token
    """
    try:
        csrf_token = get_token(request)
        return Response({
            'success': True,
            'csrf_token': csrf_token
        })
    except Exception as e:
        logger.error(f'خطا در دریافت CSRF token: {str(e)}')
        return Response({
            'success': False,
            'error': 'خطا در دریافت CSRF token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    ورود به API
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'نام کاربری و رمز عبور الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # احراز هویت کاربر
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            logger.warning(f"Failed API login attempt for username: {username} from IP: {get_client_ip(request)}")
            return Response({
                'error': 'نام کاربری یا رمز عبور اشتباه است'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted API login: {username}")
            return Response({
                'error': 'حساب کاربری غیرفعال است'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # ورود موفق
        login(request, user)
        
        # ایجاد یا دریافت token
        token, created = Token.objects.get_or_create(user=user)
        
        # ثبت ورود موفق
        logger.info(f"Successful API login: {username} from IP: {get_client_ip(request)}")
        
        return Response({
            'success': True,
            'message': 'ورود موفقیت‌آمیز',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in API login: {e}")
        return Response({
            'error': 'خطا در ورود به سیستم'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_logout(request):
    """
    خروج از API
    """
    try:
        # ثبت خروج
        logger.info(f"API logout: {request.user.username} from IP: {get_client_ip(request)}")
        
        # حذف token
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass
        
        # خروج از سیستم
        logout(request)
        
        return Response({
            'success': True,
            'message': 'خروج موفقیت‌آمیز'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in API logout: {e}")
        return Response({
            'error': 'خطا در خروج از سیستم'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def api_user_info(request):
    """
    دریافت اطلاعات کاربر فعلی
    """
    try:
        if not request.user.is_authenticated:
            return Response({
                'error': 'کاربر احراز هویت نشده است'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
                'last_login': request.user.last_login,
                'date_joined': request.user.date_joined,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in API user info: {e}")
        return Response({
            'error': 'خطا در دریافت اطلاعات کاربر'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_change_password(request):
    """
    تغییر رمز عبور
    """
    try:
        if not request.user.is_authenticated:
            return Response({
                'error': 'کاربر احراز هویت نشده است'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'error': 'رمز عبور قدیمی و جدید الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی رمز عبور قدیمی
        if not request.user.check_password(old_password):
            return Response({
                'error': 'رمز عبور قدیمی اشتباه است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی قدرت رمز عبور جدید
        from construction.authentication import PasswordSecurity
        errors = PasswordSecurity.validate_password_strength(new_password)
        if errors:
            return Response({
                'error': 'رمز عبور جدید ضعیف است',
                'details': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # تغییر رمز عبور
        request.user.set_password(new_password)
        request.user.save()
        
        # ثبت تغییر رمز عبور
        logger.info(f"Password changed for user: {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'رمز عبور با موفقیت تغییر کرد'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in API change password: {e}")
        return Response({
            'error': 'خطا در تغییر رمز عبور'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """
    ثبت‌نام کاربر جدید (فقط برای ادمین‌ها)
    """
    try:
        # بررسی دسترسی
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({
                'error': 'فقط ادمین‌ها می‌توانند کاربر جدید ثبت کنند'
            }, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not username or not password:
            return Response({
                'error': 'نام کاربری و رمز عبور الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی وجود کاربر
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'نام کاربری قبلاً استفاده شده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی قدرت رمز عبور
        from construction.authentication import PasswordSecurity
        errors = PasswordSecurity.validate_password_strength(password)
        if errors:
            return Response({
                'error': 'رمز عبور ضعیف است',
                'details': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ایجاد کاربر
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # ایجاد token
            token = Token.objects.create(user=user)
        
        # ثبت ایجاد کاربر
        logger.info(f"New user created by {request.user.username}: {username}")
        
        return Response({
            'success': True,
            'message': 'کاربر با موفقیت ایجاد شد',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in API register: {e}")
        return Response({
            'error': 'خطا در ایجاد کاربر'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def api_status(request):
    """
    بررسی وضعیت API
    """
    try:
        return Response({
            'status': 'active',
            'message': 'API فعال است',
            'timestamp': timezone.now().isoformat(),
            'user': {
                'authenticated': request.user.is_authenticated,
                'username': request.user.username if request.user.is_authenticated else None,
                'is_staff': request.user.is_staff if request.user.is_authenticated else False,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in API status: {e}")
        return Response({
            'error': 'خطا در بررسی وضعیت API'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_client_ip(request):
    """دریافت IP واقعی کاربر"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
