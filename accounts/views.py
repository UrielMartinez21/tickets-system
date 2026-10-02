"""Vistas de la app accounts: autenticación y gestión de usuarios."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from . import roles
from .forms import CrearUsuarioForm, EditarRolForm
from .permissions import admin_requerido


def login_view(request):
    """Pantalla de inicio de sesión usando sesiones nativas de Django."""
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    siguiente = request.POST.get("next") or request.GET.get("next") or ""

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}.")
            # Validar 'next' para evitar redirecciones abiertas.
            if siguiente and url_has_allowed_host_and_scheme(
                siguiente, allowed_hosts={request.get_host()}
            ):
                return redirect(siguiente)
            return redirect("dashboard:index")
        messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm(request)

    return render(
        request, "accounts/login.html", {"form": form, "next": siguiente}
    )


@login_required
def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("accounts:login")


@login_required
@admin_requerido
def lista_usuarios(request):
    """Lista de usuarios (solo Admin)."""
    usuarios = User.objects.all().order_by("username").prefetch_related("groups")
    datos = [
        {
            "obj": u,
            "roles": ", ".join(u.groups.values_list("name", flat=True)) or "—",
        }
        for u in usuarios
    ]
    return render(request, "accounts/lista_usuarios.html", {"usuarios": datos})


@login_required
@admin_requerido
def crear_usuario(request):
    """Alta de usuario con asignación de rol (solo Admin)."""
    if request.method == "POST":
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Usuario '{user.username}' creado con rol "
                f"'{form.cleaned_data['rol']}'.",
            )
            return redirect("accounts:lista_usuarios")
    else:
        form = CrearUsuarioForm()
    return render(request, "accounts/crear_usuario.html", {"form": form})


@login_required
@admin_requerido
def editar_rol(request, user_id):
    """Cambia el rol de un usuario existente (solo Admin)."""
    usuario = get_object_or_404(User, pk=user_id)
    rol_actual = usuario.groups.values_list("name", flat=True).first()

    if request.method == "POST":
        form = EditarRolForm(request.POST)
        if form.is_valid():
            rol = form.cleaned_data["rol"]
            grupo = Group.objects.get(name=rol)
            usuario.groups.set([grupo])
            usuario.is_staff = rol == roles.ROL_ADMIN
            usuario.save(update_fields=["is_staff"])
            messages.success(
                request, f"Rol de '{usuario.username}' actualizado a '{rol}'."
            )
            return redirect("accounts:lista_usuarios")
    else:
        form = EditarRolForm(initial={"rol": rol_actual})

    return render(
        request,
        "accounts/editar_rol.html",
        {"form": form, "usuario": usuario},
    )
