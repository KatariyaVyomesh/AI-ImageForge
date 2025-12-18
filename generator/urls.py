# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('generate/', views.index, name='index'),
    path('generate/direct/', views.direct_generate, name='direct_generate'),
    path('generate/result/<int:task_id>/', views.result, name='result'),
    path('dashboard/', views.user_dashboard, name='dashboard'),  # Add this
]