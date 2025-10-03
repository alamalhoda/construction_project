from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from . import models
from . import forms

def api_login_view(request):
    """صفحه لاگین API"""
    return render(request, 'construction/api_login.html')


@method_decorator(login_required, name='dispatch')
class ExpenseListView(generic.ListView):
    model = models.Expense
    form_class = forms.ExpenseForm
    ordering = ['period__id', 'created_at']


@method_decorator(login_required, name='dispatch')
class ExpenseCreateView(generic.CreateView):
    model = models.Expense
    form_class = forms.ExpenseForm


@method_decorator(login_required, name='dispatch')
class ExpenseDetailView(generic.DetailView):
    model = models.Expense
    form_class = forms.ExpenseForm


@method_decorator(login_required, name='dispatch')
class ExpenseUpdateView(generic.UpdateView):
    model = models.Expense
    form_class = forms.ExpenseForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class ExpenseDeleteView(generic.DeleteView):
    model = models.Expense
    success_url = reverse_lazy("construction_Expense_list")


# Sale Views
@method_decorator(login_required, name='dispatch')
class SaleListView(generic.ListView):
    model = models.Sale
    form_class = forms.SaleForm
    ordering = ['period__id', 'created_at']


@method_decorator(login_required, name='dispatch')
class SaleCreateView(generic.CreateView):
    model = models.Sale
    form_class = forms.SaleForm


@method_decorator(login_required, name='dispatch')
class SaleDetailView(generic.DetailView):
    model = models.Sale
    form_class = forms.SaleForm


@method_decorator(login_required, name='dispatch')
class SaleUpdateView(generic.UpdateView):
    model = models.Sale
    form_class = forms.SaleForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class SaleDeleteView(generic.DeleteView):
    model = models.Sale
    success_url = reverse_lazy("construction_Sale_list")


@method_decorator(login_required, name='dispatch')
class InvestorListView(generic.ListView):
    model = models.Investor
    form_class = forms.InvestorForm


@method_decorator(login_required, name='dispatch')
class InvestorCreateView(generic.CreateView):
    model = models.Investor
    form_class = forms.InvestorForm


@method_decorator(login_required, name='dispatch')
class InvestorDetailView(generic.DetailView):
    model = models.Investor
    form_class = forms.InvestorForm


@method_decorator(login_required, name='dispatch')
class InvestorUpdateView(generic.UpdateView):
    model = models.Investor
    form_class = forms.InvestorForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class InvestorDeleteView(generic.DeleteView):
    model = models.Investor
    success_url = reverse_lazy("construction_Investor_list")


@method_decorator(login_required, name='dispatch')
class PeriodListView(generic.ListView):
    model = models.Period
    form_class = forms.PeriodForm


@method_decorator(login_required, name='dispatch')
class PeriodCreateView(generic.CreateView):
    model = models.Period
    form_class = forms.PeriodForm


@method_decorator(login_required, name='dispatch')
class PeriodDetailView(generic.DetailView):
    model = models.Period
    form_class = forms.PeriodForm


@method_decorator(login_required, name='dispatch')
class PeriodUpdateView(generic.UpdateView):
    model = models.Period
    form_class = forms.PeriodForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class PeriodDeleteView(generic.DeleteView):
    model = models.Period
    success_url = reverse_lazy("construction_Period_list")


@method_decorator(login_required, name='dispatch')
class ProjectListView(generic.ListView):
    model = models.Project
    form_class = forms.ProjectForm


@method_decorator(login_required, name='dispatch')
class ProjectCreateView(generic.CreateView):
    model = models.Project
    form_class = forms.ProjectForm


@method_decorator(login_required, name='dispatch')
class ProjectDetailView(generic.DetailView):
    model = models.Project
    form_class = forms.ProjectForm


@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(generic.UpdateView):
    model = models.Project
    form_class = forms.ProjectForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class ProjectDeleteView(generic.DeleteView):
    model = models.Project
    success_url = reverse_lazy("construction_Project_list")


@method_decorator(login_required, name='dispatch')
class TransactionListView(generic.ListView):
    model = models.Transaction
    form_class = forms.TransactionForm


@method_decorator(login_required, name='dispatch')
class TransactionCreateView(generic.CreateView):
    model = models.Transaction
    form_class = forms.TransactionForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن اطلاعات پروژه فعال به context
        active_project = models.Project.get_active_project()
        context['active_project'] = active_project
        if not active_project:
            context['error_message'] = "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."
        return context


@method_decorator(login_required, name='dispatch')
class TransactionDetailView(generic.DetailView):
    model = models.Transaction
    form_class = forms.TransactionForm


@method_decorator(login_required, name='dispatch')
class TransactionUpdateView(generic.UpdateView):
    model = models.Transaction
    form_class = forms.TransactionForm
    pk_url_kwarg = "pk"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن اطلاعات پروژه فعال به context
        active_project = models.Project.get_active_project()
        context['active_project'] = active_project
        if not active_project:
            context['error_message'] = "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."
        return context


@method_decorator(login_required, name='dispatch')
class TransactionDeleteView(generic.DeleteView):
    model = models.Transaction
    success_url = reverse_lazy("construction_Transaction_list")


@method_decorator(login_required, name='dispatch')
class UnitListView(generic.ListView):
    model = models.Unit
    form_class = forms.UnitForm


@method_decorator(login_required, name='dispatch')
class UnitCreateView(generic.CreateView):
    model = models.Unit
    form_class = forms.UnitForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن اطلاعات پروژه فعال به context
        active_project = models.Project.get_active_project()
        context['active_project'] = active_project
        if not active_project:
            context['error_message'] = "هیچ پروژه فعالی یافت نشد. لطفاً ابتدا یک پروژه را فعال کنید."
        return context


@method_decorator(login_required, name='dispatch')
class UnitDetailView(generic.DetailView):
    model = models.Unit
    form_class = forms.UnitForm


@method_decorator(login_required, name='dispatch')
class UnitUpdateView(generic.UpdateView):
    model = models.Unit
    form_class = forms.UnitForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class UnitDeleteView(generic.DeleteView):
    model = models.Unit
    success_url = reverse_lazy("construction_Unit_list")


# View های مربوط به پروژه فعال
@login_required
def active_project_view(request):
    """نمایش پروژه فعال"""
    active_project = models.Project.get_active_project()
    all_projects = models.Project.objects.all().order_by('-created_at')
    context = {
        'active_project': active_project,
        'all_projects': all_projects,
        'title': 'پروژه فعال'
    }
    return render(request, 'construction/active_project.html', context)


@login_required
@require_http_methods(["POST"])
def set_active_project_view(request):
    """تنظیم پروژه فعال"""
    project_id = request.POST.get('project_id')
    
    if not project_id:
        messages.error(request, 'شناسه پروژه الزامی است')
        return redirect('construction_active_project')
    
    try:
        project = models.Project.set_active_project(project_id)
        if project:
            messages.success(request, f'پروژه "{project.name}" به عنوان پروژه فعال تنظیم شد')
        else:
            messages.error(request, 'پروژه یافت نشد')
    except Exception as e:
        messages.error(request, f'خطا در تنظیم پروژه فعال: {str(e)}')
    
    return redirect('construction_active_project')


@login_required
def active_project_api(request):
    """API برای دریافت پروژه فعال"""
    active_project = models.Project.get_active_project()
    if active_project:
        data = {
            'id': active_project.id,
            'name': active_project.name,
            'is_active': active_project.is_active,
            'start_date_shamsi': active_project.start_date_shamsi,
            'end_date_shamsi': active_project.end_date_shamsi,
            'start_date_gregorian': active_project.start_date_gregorian,
            'end_date_gregorian': active_project.end_date_gregorian,
            'created_at': active_project.created_at,
            'updated_at': active_project.updated_at,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'هیچ پروژه فعالی یافت نشد'}, status=404)


@login_required
@require_http_methods(["POST"])
def set_active_project_api(request):
    """API برای تنظیم پروژه فعال"""
    import json
    
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        
        if not project_id:
            return JsonResponse({'error': 'شناسه پروژه الزامی است'}, status=400)
        
        project = models.Project.set_active_project(project_id)
        if project:
            return JsonResponse({
                'success': True,
                'message': f'پروژه "{project.name}" به عنوان پروژه فعال تنظیم شد',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'is_active': project.is_active,
                }
            })
        else:
            return JsonResponse({'error': 'پروژه یافت نشد'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'داده‌های JSON نامعتبر است'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'خطا در تنظیم پروژه فعال: {str(e)}'}, status=500)


# InterestRate Views
@method_decorator(login_required, name='dispatch')
class InterestRateListView(generic.ListView):
    model = models.InterestRate
    form_class = forms.InterestRateForm
    ordering = ['-effective_date']


@method_decorator(login_required, name='dispatch')
class InterestRateCreateView(generic.CreateView):
    model = models.InterestRate
    form_class = forms.InterestRateForm


@method_decorator(login_required, name='dispatch')
class InterestRateDetailView(generic.DetailView):
    model = models.InterestRate
    form_class = forms.InterestRateForm


@method_decorator(login_required, name='dispatch')
class InterestRateUpdateView(generic.UpdateView):
    model = models.InterestRate
    form_class = forms.InterestRateForm
    pk_url_kwarg = "pk"


@method_decorator(login_required, name='dispatch')
class InterestRateDeleteView(generic.DeleteView):
    model = models.InterestRate
    success_url = reverse_lazy("construction_InterestRate_list")
