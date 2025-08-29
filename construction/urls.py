from django.urls import path, include
from rest_framework import routers

from . import api
from . import views
from . import htmx


router = routers.DefaultRouter()
router.register("Expense", api.ExpenseViewSet)
router.register("Investor", api.InvestorViewSet)
router.register("Period", api.PeriodViewSet)
router.register("Project", api.ProjectViewSet)
router.register("Transaction", api.TransactionViewSet)
router.register("Unit", api.UnitViewSet)

urlpatterns = (
    path("api/v1/", include(router.urls)),
    path("construction/Expense/", views.ExpenseListView.as_view(), name="construction_Expense_list"),
    path("construction/Expense/create/", views.ExpenseCreateView.as_view(), name="construction_Expense_create"),
    path("construction/Expense/detail/<int:pk>/", views.ExpenseDetailView.as_view(), name="construction_Expense_detail"),
    path("construction/Expense/update/<int:pk>/", views.ExpenseUpdateView.as_view(), name="construction_Expense_update"),
    path("construction/Expense/delete/<int:pk>/", views.ExpenseDeleteView.as_view(), name="construction_Expense_delete"),
    path("construction/Investor/", views.InvestorListView.as_view(), name="construction_Investor_list"),
    path("construction/Investor/create/", views.InvestorCreateView.as_view(), name="construction_Investor_create"),
    path("construction/Investor/detail/<int:pk>/", views.InvestorDetailView.as_view(), name="construction_Investor_detail"),
    path("construction/Investor/update/<int:pk>/", views.InvestorUpdateView.as_view(), name="construction_Investor_update"),
    path("construction/Investor/delete/<int:pk>/", views.InvestorDeleteView.as_view(), name="construction_Investor_delete"),
    path("construction/Period/", views.PeriodListView.as_view(), name="construction_Period_list"),
    path("construction/Period/create/", views.PeriodCreateView.as_view(), name="construction_Period_create"),
    path("construction/Period/detail/<int:pk>/", views.PeriodDetailView.as_view(), name="construction_Period_detail"),
    path("construction/Period/update/<int:pk>/", views.PeriodUpdateView.as_view(), name="construction_Period_update"),
    path("construction/Period/delete/<int:pk>/", views.PeriodDeleteView.as_view(), name="construction_Period_delete"),
    path("construction/Project/", views.ProjectListView.as_view(), name="construction_Project_list"),
    path("construction/Project/create/", views.ProjectCreateView.as_view(), name="construction_Project_create"),
    path("construction/Project/detail/<int:pk>/", views.ProjectDetailView.as_view(), name="construction_Project_detail"),
    path("construction/Project/update/<int:pk>/", views.ProjectUpdateView.as_view(), name="construction_Project_update"),
    path("construction/Project/delete/<int:pk>/", views.ProjectDeleteView.as_view(), name="construction_Project_delete"),
    path("construction/Transaction/", views.TransactionListView.as_view(), name="construction_Transaction_list"),
    path("construction/Transaction/create/", views.TransactionCreateView.as_view(), name="construction_Transaction_create"),
    path("construction/Transaction/detail/<int:pk>/", views.TransactionDetailView.as_view(), name="construction_Transaction_detail"),
    path("construction/Transaction/update/<int:pk>/", views.TransactionUpdateView.as_view(), name="construction_Transaction_update"),
    path("construction/Transaction/delete/<int:pk>/", views.TransactionDeleteView.as_view(), name="construction_Transaction_delete"),
    path("construction/Unit/", views.UnitListView.as_view(), name="construction_Unit_list"),
    path("construction/Unit/create/", views.UnitCreateView.as_view(), name="construction_Unit_create"),
    path("construction/Unit/detail/<int:pk>/", views.UnitDetailView.as_view(), name="construction_Unit_detail"),
    path("construction/Unit/update/<int:pk>/", views.UnitUpdateView.as_view(), name="construction_Unit_update"),
    path("construction/Unit/delete/<int:pk>/", views.UnitDeleteView.as_view(), name="construction_Unit_delete"),

    path("construction/htmx/Expense/", htmx.HTMXExpenseListView.as_view(), name="construction_Expense_htmx_list"),
    path("construction/htmx/Expense/create/", htmx.HTMXExpenseCreateView.as_view(), name="construction_Expense_htmx_create"),
    path("construction/htmx/Expense/delete/<int:pk>/", htmx.HTMXExpenseDeleteView.as_view(), name="construction_Expense_htmx_delete"),
    path("construction/htmx/Investor/", htmx.HTMXInvestorListView.as_view(), name="construction_Investor_htmx_list"),
    path("construction/htmx/Investor/create/", htmx.HTMXInvestorCreateView.as_view(), name="construction_Investor_htmx_create"),
    path("construction/htmx/Investor/delete/<int:pk>/", htmx.HTMXInvestorDeleteView.as_view(), name="construction_Investor_htmx_delete"),
    path("construction/htmx/Period/", htmx.HTMXPeriodListView.as_view(), name="construction_Period_htmx_list"),
    path("construction/htmx/Period/create/", htmx.HTMXPeriodCreateView.as_view(), name="construction_Period_htmx_create"),
    path("construction/htmx/Period/delete/<int:pk>/", htmx.HTMXPeriodDeleteView.as_view(), name="construction_Period_htmx_delete"),
    path("construction/htmx/Project/", htmx.HTMXProjectListView.as_view(), name="construction_Project_htmx_list"),
    path("construction/htmx/Project/create/", htmx.HTMXProjectCreateView.as_view(), name="construction_Project_htmx_create"),
    path("construction/htmx/Project/delete/<int:pk>/", htmx.HTMXProjectDeleteView.as_view(), name="construction_Project_htmx_delete"),
    path("construction/htmx/Transaction/", htmx.HTMXTransactionListView.as_view(), name="construction_Transaction_htmx_list"),
    path("construction/htmx/Transaction/create/", htmx.HTMXTransactionCreateView.as_view(), name="construction_Transaction_htmx_create"),
    path("construction/htmx/Transaction/delete/<int:pk>/", htmx.HTMXTransactionDeleteView.as_view(), name="construction_Transaction_htmx_delete"),
    path("construction/htmx/Unit/", htmx.HTMXUnitListView.as_view(), name="construction_Unit_htmx_list"),
    path("construction/htmx/Unit/create/", htmx.HTMXUnitCreateView.as_view(), name="construction_Unit_htmx_create"),
    path("construction/htmx/Unit/delete/<int:pk>/", htmx.HTMXUnitDeleteView.as_view(), name="construction_Unit_htmx_delete"),
)
