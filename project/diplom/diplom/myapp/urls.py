from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('history/', views.history, name='history'),
    path('save_criteria/', views.save_criteria, name='save_criteria'),
    path('get_criteria/', views.get_criteria, name='get_criteria')
]