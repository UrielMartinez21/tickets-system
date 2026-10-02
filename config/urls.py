"""Configuración de URLs raíz del proyecto."""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="dashboard:index"), name="home"),
    path("cuentas/", include("accounts.urls")),
    path("tickets/", include("tickets.urls")),
    path("dashboard/", include("dashboard.urls")),
]
