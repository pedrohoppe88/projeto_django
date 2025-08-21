from django.urls import path
from . import views

urlpatterns = [
    path('all_users/', views.all_users, name='all_users'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path("criar_sessao/", views.criar_sessao, name="criar_sessao"),

]