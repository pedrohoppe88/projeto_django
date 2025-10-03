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
    path("validar_sessao/<int:sessao_id>/", views.validar_sessao, name="validar_sessao"),
    path("sessoes/<int:sessao_id>/itens/", views.listar_itens, name="listar_itens"),
    path('sessao/<int:sessao_id>/itens/relatorio/pdf/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
    path("item/<int:item_id>/excluir/", views.excluir_item, name="excluir_item"),
]