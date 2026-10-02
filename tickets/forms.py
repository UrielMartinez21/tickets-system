"""Formularios de la app tickets."""
from django import forms
from django.contrib.auth.models import User

from accounts import roles

from .models import Comentario, Estado, Ticket


class TicketForm(forms.ModelForm):
    """Formulario de creación/edición de tickets por el solicitante."""

    class Meta:
        model = Ticket
        fields = ["titulo", "descripcion", "prioridad"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
            "prioridad": forms.Select(attrs={"class": "form-select"}),
        }


class AsignarAgenteForm(forms.ModelForm):
    """Formulario para asignar un agente al ticket (Admin/Agente)."""

    class Meta:
        model = Ticket
        fields = ["agente"]
        widgets = {"agente": forms.Select(attrs={"class": "form-select"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se pueden asignar usuarios con rol Agente o Admin.
        self.fields["agente"].queryset = User.objects.filter(
            groups__name__in=roles.ROLES_STAFF
        ).distinct()
        self.fields["agente"].label = "Agente asignado"


class CambiarEstadoForm(forms.Form):
    """Formulario para cambiar el estado respetando las transiciones."""

    nuevo_estado = forms.ChoiceField(
        label="Nuevo estado",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, ticket=None, **kwargs):
        super().__init__(*args, **kwargs)
        posibles = ticket.transiciones_posibles() if ticket else []
        self.fields["nuevo_estado"].choices = [
            (estado, Estado(estado).label) for estado in posibles
        ]


class ComentarioForm(forms.ModelForm):
    """Formulario para agregar comentarios al ticket."""

    class Meta:
        model = Comentario
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Escribe un comentario...",
                }
            )
        }
