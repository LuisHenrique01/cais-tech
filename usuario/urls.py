from django.urls import path, include
from rest_framework import routers
from .api.viewsets import HistoricoView, UsuarioViewSet
from rest_framework.authtoken import views


usuarioRouters = routers.DefaultRouter()
usuarioRouters.register('usuario', UsuarioViewSet)


urlpatterns = [
    path('historico/', HistoricoView.as_view(), name='historico'),
    path('', include(usuarioRouters.urls), name='usuario'),
    path('api-token/', views.obtain_auth_token)
]
