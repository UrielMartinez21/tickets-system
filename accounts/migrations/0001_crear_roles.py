"""Migración de datos: crea los grupos de roles y asigna permisos.

Crea los grupos Admin, Agente y Solicitante y les asigna los permisos
sobre el modelo Ticket según el rol:
  - Admin: todos los permisos sobre tickets.
  - Agente: ver, agregar y cambiar tickets.
  - Solicitante: ver y agregar tickets.
"""
from django.db import migrations

ROL_ADMIN = "Admin"
ROL_AGENTE = "Agente"
ROL_SOLICITANTE = "Solicitante"

PERMISOS_POR_ROL = {
    ROL_ADMIN: ["add_ticket", "change_ticket", "delete_ticket", "view_ticket"],
    ROL_AGENTE: ["add_ticket", "change_ticket", "view_ticket"],
    ROL_SOLICITANTE: ["add_ticket", "view_ticket"],
}


def crear_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Nombre legible por defecto de cada permiso de modelo.
    nombres_permiso = {
        "add_ticket": "Can add Ticket",
        "change_ticket": "Can change Ticket",
        "delete_ticket": "Can delete Ticket",
        "view_ticket": "Can view Ticket",
    }

    ct, _ = ContentType.objects.get_or_create(
        app_label="tickets", model="ticket"
    )

    for rol, codenames in PERMISOS_POR_ROL.items():
        grupo, _ = Group.objects.get_or_create(name=rol)
        permisos = []
        for codename in codenames:
            # Los permisos de modelo normalmente los crea un signal de auth
            # DESPUÉS de migrar. Como esta migración corre antes, los
            # creamos aquí si aún no existen (get_or_create es idempotente).
            permiso, _ = Permission.objects.get_or_create(
                content_type=ct,
                codename=codename,
                defaults={"name": nombres_permiso.get(codename, codename)},
            )
            permisos.append(permiso)
        grupo.permissions.set(permisos)


def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(
        name__in=[ROL_ADMIN, ROL_AGENTE, ROL_SOLICITANTE]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("tickets", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_grupos, eliminar_grupos),
    ]
