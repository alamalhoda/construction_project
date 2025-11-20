from django.urls import path, include
from rest_framework import routers

from . import api
from . import views

from . import api_auth
from . import user_views


router = routers.DefaultRouter()
router.register("Expense", api.ExpenseViewSet)
router.register("Investor", api.InvestorViewSet)
router.register("InterestRate", api.InterestRateViewSet)
router.register("Period", api.PeriodViewSet)
router.register("Project", api.ProjectViewSet)
router.register("Sale", api.SaleViewSet)
router.register("Transaction", api.TransactionViewSet)
router.register("Unit", api.UnitViewSet)
router.register("UnitSpecificExpense", api.UnitSpecificExpenseViewSet)
router.register("PettyCashTransaction", api.PettyCashTransactionViewSet)
router.register("comprehensive", api.ComprehensiveAnalysisViewSet, basename="comprehensive")



urlpatterns = (
    # API Login Page
    path("api/login/", views.api_login_view, name="api_login_page"),
    
    # API Authentication URLs
    path("api/v1/auth/csrf/", api_auth.api_csrf_token, name="api_csrf_token"),
    path("api/v1/auth/login/", api_auth.api_login, name="api_login"),
    path("api/v1/auth/logout/", api_auth.api_logout, name="api_logout"),
    path("api/v1/auth/user/", api_auth.api_user_info, name="api_user_info"),
    path("api/v1/auth/change-password/", api_auth.api_change_password, name="api_change_password"),
    path("api/v1/auth/register/", api_auth.api_register, name="api_register"),
    path("api/v1/status/", api_auth.api_status, name="api_status"),
    
    # API URLs
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
    path("construction/InterestRate/", views.InterestRateListView.as_view(), name="construction_InterestRate_list"),
    path("construction/InterestRate/create/", views.InterestRateCreateView.as_view(), name="construction_InterestRate_create"),
    path("construction/InterestRate/detail/<int:pk>/", views.InterestRateDetailView.as_view(), name="construction_InterestRate_detail"),
    path("construction/InterestRate/update/<int:pk>/", views.InterestRateUpdateView.as_view(), name="construction_InterestRate_update"),
    path("construction/InterestRate/delete/<int:pk>/", views.InterestRateDeleteView.as_view(), name="construction_InterestRate_delete"),
    path("construction/Sale/", views.SaleListView.as_view(), name="construction_Sale_list"),
    path("construction/Sale/create/", views.SaleCreateView.as_view(), name="construction_Sale_create"),
    path("construction/Sale/detail/<int:pk>/", views.SaleDetailView.as_view(), name="construction_Sale_detail"),
    path("construction/Sale/update/<int:pk>/", views.SaleUpdateView.as_view(), name="construction_Sale_update"),
    path("construction/Sale/delete/<int:pk>/", views.SaleDeleteView.as_view(), name="construction_Sale_delete"),
    path("construction/UnitSpecificExpense/", views.UnitSpecificExpenseListView.as_view(), name="construction_UnitSpecificExpense_list"),
    path("construction/UnitSpecificExpense/create/", views.UnitSpecificExpenseCreateView.as_view(), name="construction_UnitSpecificExpense_create"),
    path("construction/UnitSpecificExpense/detail/<int:pk>/", views.UnitSpecificExpenseDetailView.as_view(), name="construction_UnitSpecificExpense_detail"),
    path("construction/UnitSpecificExpense/update/<int:pk>/", views.UnitSpecificExpenseUpdateView.as_view(), name="construction_UnitSpecificExpense_update"),
    path("construction/UnitSpecificExpense/delete/<int:pk>/", views.UnitSpecificExpenseDeleteView.as_view(), name="construction_UnitSpecificExpense_delete"),
    path("construction/PettyCashTransaction/", views.PettyCashTransactionListView.as_view(), name="construction_PettyCashTransaction_list"),
    path("construction/PettyCashTransaction/create/", views.PettyCashTransactionCreateView.as_view(), name="construction_PettyCashTransaction_create"),
    path("construction/PettyCashTransaction/detail/<int:pk>/", views.PettyCashTransactionDetailView.as_view(), name="construction_PettyCashTransaction_detail"),
    path("construction/PettyCashTransaction/update/<int:pk>/", views.PettyCashTransactionUpdateView.as_view(), name="construction_PettyCashTransaction_update"),
    path("construction/PettyCashTransaction/delete/<int:pk>/", views.PettyCashTransactionDeleteView.as_view(), name="construction_PettyCashTransaction_delete"),

    # User Authentication URLs - moved to root level in main urls.py
    # path("login/", user_views.user_login_view, name="user_login"),
    # path("register/", user_views.user_register_view, name="user_register"),
    # path("logout/", user_views.user_logout_view, name="user_logout"),
    # path("dashboard/", user_views.user_dashboard_view, name="user_dashboard"),
    # path("profile/", user_views.user_profile_view, name="user_profile"),
    # path("change-password/", user_views.change_password_view, name="change_password"),
    
    # Protected Pages
    path("protected/", user_views.ProtectedIndexView.as_view(), name="protected_index"),
    
    # User API endpoints
    path("api/user/info/", user_views.user_info_api, name="user_info_api"),
    path("api/user/logout/", user_views.user_logout_api, name="user_logout_api"),
    
    # Active Project URLs
    path("construction/active-project/", views.active_project_view, name="construction_active_project"),
    path("construction/active-project/set/", views.set_active_project_view, name="construction_set_active_project"),
    path("api/active-project/", views.active_project_api, name="construction_active_project_api"),
    path("api/active-project/set/", views.set_active_project_api, name="construction_set_active_project_api"),
    
    # AI Assistant URLs
    path("assistant/", include('assistant.urls')),


)
