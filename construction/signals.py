from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Expense


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal برای ایجاد پروفایل کاربر هنگام ایجاد کاربر جدید
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal برای ذخیره پروفایل کاربر هنگام به‌روزرسانی کاربر
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        # اگر پروفایل وجود نداشت، آن را ایجاد کن
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Expense)
def update_construction_contractor_on_expense_save(sender, instance, created, **kwargs):
    """
    Signal برای محاسبه خودکار هزینه پیمان ساختمان هنگام ایجاد یا ویرایش هزینه
    """
    # فقط اگر هزینه از نوع construction_contractor نباشد
    if instance.expense_type != 'construction_contractor':
        # محاسبه مجدد هزینه پیمان ساختمان برای این دوره
        Expense.update_construction_contractor_for_period(instance.period, instance.project)


@receiver(post_delete, sender=Expense)
def update_construction_contractor_on_expense_delete(sender, instance, **kwargs):
    """
    Signal برای محاسبه مجدد هزینه پیمان ساختمان هنگام حذف هزینه
    """
    # فقط اگر هزینه حذف شده از نوع construction_contractor نباشد
    if instance.expense_type != 'construction_contractor':
        # محاسبه مجدد هزینه پیمان ساختمان برای این دوره
        Expense.update_construction_contractor_for_period(instance.period, instance.project)
