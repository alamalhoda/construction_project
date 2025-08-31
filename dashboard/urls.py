from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('project/', views.project_dashboard, name='project_dashboard'),
    path('csv-viewer/', views.csv_viewer, name='csv_viewer'),
    path('csv-tabulator/', views.csv_tabulator_viewer, name='csv_tabulator_viewer'),
    path('investor-profile/', views.investor_profile, name='investor_profile'),
    path('data/<str:filename>', views.serve_csv_file, name='serve_csv_file'),
]
