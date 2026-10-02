"""URLs de la app tickets."""
from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.lista_tickets, name="lista"),
    path("nuevo/", views.crear_ticket, name="crear"),
    path("<int:pk>/", views.detalle_ticket, name="detalle"),
    path("<int:pk>/comentar/", views.agregar_comentario, name="comentar"),
    path("<int:pk>/estado/", views.cambiar_estado, name="cambiar_estado"),
    path("<int:pk>/asignar/", views.asignar_agente, name="asignar_agente"),
    path("<int:pk>/autoasignarme/", views.autoasignarme, name="autoasignarme"),
]
