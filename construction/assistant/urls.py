"""
URL patterns برای AI Assistant
"""

from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('api/', views.chat_api, name='chat_api'),
    path('history/', views.chat_history, name='chat_history'),
]

