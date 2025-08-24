from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from usuarios import views
from django.contrib import messages
from django.shortcuts import render

def home(request):
    return render(request, 'usuarios/home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('accounts/login/', views.login_usuario, name='accounts_login'),
    path('', home, name='home'),
]