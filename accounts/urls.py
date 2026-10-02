"""URLs de la app accounts."""
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("usuarios/nuevo/", views.crear_usuario, name="crear_usuario"),
    path("usuarios/<int:user_id>/rol/", views.editar_rol, name="editar_rol"),
]
