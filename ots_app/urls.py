from django.urls import path
from . import views

urlpatterns = [
    # Template URLs
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tests/', views.tests_page, name='tests'),
    path('results/', views.results_page, name='results'),
    
    # API URLs
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/user/', views.api_current_user, name='api_current_user'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    path('api/subjects/', views.api_subjects, name='api_subjects'),
]
