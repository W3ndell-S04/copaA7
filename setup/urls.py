"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from torneio import views  # Importamos o módulo views inteiro para acessar todas as funções

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ROTA PRINCIPAL: Agora chama a view 'index' que carrega Times + Artilheiros
    path('', views.index, name='index'), 
    
    # ROTA SECUNDÁRIA: Caso queira acessar apenas a tabela isolada
    path('tabela/', views.tabela_classificacao, name='tabela_simples'),

    # ROTA PARA O CALENDÁRIO DE JOGOS
    path('jogos/', views.lista_jogos, name='lista_jogos'),

    # ROTA PARA A ARTILHARIA COMPLETA
    path('artilharia/', views.artilharia_completa, name='artilharia_completa'),
]