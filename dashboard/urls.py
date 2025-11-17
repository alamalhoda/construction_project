from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('project/', views.project_dashboard, name='project_dashboard'),
    path('investor-profile/', views.investor_profile, name='investor_profile'),
    path('investor-pdf/', views.investor_pdf, name='investor_pdf'),
    path('investors-summary-print/', views.investors_summary_print, name='investors_summary_print'),
    path('transaction-manager/', views.transaction_manager, name='transaction_manager'),
    path('expense-dashboard/', views.expense_dashboard, name='expense_dashboard'),
    path('interest-rate-manager/', views.interest_rate_manager, name='interest_rate_manager'),
    path('period-summary/', views.period_summary, name='period_summary'),
    path('period-summary-print/', views.period_summary_print, name='period_summary_print'),
    path('detailed-calculations/', views.detailed_calculations, name='detailed_calculations'),
    path('data/<str:filename>', views.serve_csv_file, name='serve_csv_file'),
    
    # Petty Cash Pages
    path('petty-cash/', views.petty_cash_dashboard, name='petty_cash_dashboard'),
    path('petty-cash/balance/', views.petty_cash_balance_report, name='petty_cash_balance_report'),
    path('petty-cash/period/', views.petty_cash_period_report, name='petty_cash_period_report'),
    path('petty-cash/detail/', views.petty_cash_detail_report, name='petty_cash_detail_report'),
    
    # Test pages
    path('test-home/', views.test_home_page, name='test_home_page'),
    path('test-transaction-manager/', views.test_transaction_manager, name='test_transaction_manager'),
    path('test-transaction-api/', views.test_transaction_api, name='test_transaction_api'),
    path('test-filters/', views.test_filters, name='test_filters'),
]
