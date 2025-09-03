from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse

from . import models
from . import forms

def api_login_view(request):
    """صفحه لاگین API"""
    return render(request, 'construction/api_login.html')


class ExpenseListView(generic.ListView):
    model = models.Expense
    form_class = forms.ExpenseForm


class ExpenseCreateView(generic.CreateView):
    model = models.Expense
    form_class = forms.ExpenseForm


class ExpenseDetailView(generic.DetailView):
    model = models.Expense
    form_class = forms.ExpenseForm


class ExpenseUpdateView(generic.UpdateView):
    model = models.Expense
    form_class = forms.ExpenseForm
    pk_url_kwarg = "pk"


class ExpenseDeleteView(generic.DeleteView):
    model = models.Expense
    success_url = reverse_lazy("construction_Expense_list")


class InvestorListView(generic.ListView):
    model = models.Investor
    form_class = forms.InvestorForm


class InvestorCreateView(generic.CreateView):
    model = models.Investor
    form_class = forms.InvestorForm


class InvestorDetailView(generic.DetailView):
    model = models.Investor
    form_class = forms.InvestorForm


class InvestorUpdateView(generic.UpdateView):
    model = models.Investor
    form_class = forms.InvestorForm
    pk_url_kwarg = "pk"


class InvestorDeleteView(generic.DeleteView):
    model = models.Investor
    success_url = reverse_lazy("construction_Investor_list")


class PeriodListView(generic.ListView):
    model = models.Period
    form_class = forms.PeriodForm


class PeriodCreateView(generic.CreateView):
    model = models.Period
    form_class = forms.PeriodForm


class PeriodDetailView(generic.DetailView):
    model = models.Period
    form_class = forms.PeriodForm


class PeriodUpdateView(generic.UpdateView):
    model = models.Period
    form_class = forms.PeriodForm
    pk_url_kwarg = "pk"


class PeriodDeleteView(generic.DeleteView):
    model = models.Period
    success_url = reverse_lazy("construction_Period_list")


class ProjectListView(generic.ListView):
    model = models.Project
    form_class = forms.ProjectForm


class ProjectCreateView(generic.CreateView):
    model = models.Project
    form_class = forms.ProjectForm


class ProjectDetailView(generic.DetailView):
    model = models.Project
    form_class = forms.ProjectForm


class ProjectUpdateView(generic.UpdateView):
    model = models.Project
    form_class = forms.ProjectForm
    pk_url_kwarg = "pk"


class ProjectDeleteView(generic.DeleteView):
    model = models.Project
    success_url = reverse_lazy("construction_Project_list")


class TransactionListView(generic.ListView):
    model = models.Transaction
    form_class = forms.TransactionForm


class TransactionCreateView(generic.CreateView):
    model = models.Transaction
    form_class = forms.TransactionForm


class TransactionDetailView(generic.DetailView):
    model = models.Transaction
    form_class = forms.TransactionForm


class TransactionUpdateView(generic.UpdateView):
    model = models.Transaction
    form_class = forms.TransactionForm
    pk_url_kwarg = "pk"


class TransactionDeleteView(generic.DeleteView):
    model = models.Transaction
    success_url = reverse_lazy("construction_Transaction_list")


class UnitListView(generic.ListView):
    model = models.Unit
    form_class = forms.UnitForm


class UnitCreateView(generic.CreateView):
    model = models.Unit
    form_class = forms.UnitForm


class UnitDetailView(generic.DetailView):
    model = models.Unit
    form_class = forms.UnitForm


class UnitUpdateView(generic.UpdateView):
    model = models.Unit
    form_class = forms.UnitForm
    pk_url_kwarg = "pk"


class UnitDeleteView(generic.DeleteView):
    model = models.Unit
    success_url = reverse_lazy("construction_Unit_list")
