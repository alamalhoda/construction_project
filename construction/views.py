from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from . import models
from . import forms

def api_login_view(request):
    """صفحه لاگین API"""
    return render(request, 'construction/api_login.html')


@method_decorator(login_required, name='dispatch')
class ExpenseListView(generic.ListView):
    model = models.Expense
    form_class = forms.ExpenseForm


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


@method_decorator(login_required, name='dispatch')
class TransactionDetailView(generic.DetailView):
    model = models.Transaction
    form_class = forms.TransactionForm


@method_decorator(login_required, name='dispatch')
class TransactionUpdateView(generic.UpdateView):
    model = models.Transaction
    form_class = forms.TransactionForm
    pk_url_kwarg = "pk"


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
