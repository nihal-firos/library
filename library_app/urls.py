from django.urls import path
from django.contrib.auth import logout
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views

def custom_logout(request):
    logout(request)
    return redirect("login")

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='library_app/login.html'), name='login'),
    path("logout/", custom_logout, name="logout"),

    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow_book'),
    path('book/<int:pk>/return/', views.return_book, name='return_book'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-book/', views.add_book_view, name='add_book'),
]
