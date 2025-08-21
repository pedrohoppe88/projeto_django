from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from usuarios import views  # Importa views para usar login_usuario

def home(request):
    return HttpResponse("Bem-vindo à página inicial!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('accounts/login/', views.login_usuario, name='accounts_login'),  # Adicione esta linha aqui
    path('', home, name='home'),
]