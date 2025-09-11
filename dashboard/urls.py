from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('project/', views.project_dashboard, name='project_dashboard'),
    path('investor-profile/', views.investor_profile, name='investor_profile'),
    path('transaction-manager/', views.transaction_manager, name='transaction_manager'),
    path('expense-dashboard/', views.expense_dashboard, name='expense_dashboard'),
    path('interest-rate-manager/', views.interest_rate_manager, name='interest_rate_manager'),
    path('data/<str:filename>', views.serve_csv_file, name='serve_csv_file'),
    
    # Test pages
    path('test-home/', views.test_home_page, name='test_home_page'),
    path('test-transaction-manager/', views.test_transaction_manager, name='test_transaction_manager'),
    path('test-transaction-api/', views.test_transaction_api, name='test_transaction_api'),
    path('test-filters/', views.test_filters, name='test_filters'),
]
