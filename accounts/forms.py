"""Formularios de la app accounts."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from . import roles


class CrearUsuarioForm(UserCreationForm):
    """Formulario para que el Admin cree usuarios y les asigne un rol."""

    email = forms.EmailField(
        label="Correo electrónico", required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        label="Nombre", required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label="Apellidos", required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    rol = forms.ChoiceField(
        label="Rol",
        choices=[(r, r) for r in roles.ROLES],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in ("username", "password1", "password2"):
            self.fields[campo].widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            self._asignar_rol(user)
        return user

    def _asignar_rol(self, user):
        rol = self.cleaned_data["rol"]
        grupo = Group.objects.get(name=rol)
        user.groups.set([grupo])
        # El rol Admin obtiene acceso al admin de Django.
        if rol == roles.ROL_ADMIN:
            user.is_staff = True
            user.save(update_fields=["is_staff"])


class EditarRolForm(forms.Form):
    """Formulario para cambiar el rol de un usuario existente."""

    rol = forms.ChoiceField(
        label="Rol",
        choices=[(r, r) for r in roles.ROLES],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
