"""Comando de datos de prueba (seed).

Crea usuarios de cada rol y tickets de ejemplo en distintos estados y
prioridades. Es idempotente: si se ejecuta de nuevo, no duplica datos.

Uso:
    python manage.py seed
"""
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts import roles
from tickets.models import Comentario, Estado, Prioridad, Ticket

# Usuarios de ejemplo: (username, rol, password)
USUARIOS = [
    ("admin", roles.ROL_ADMIN, "admin12345"),
    ("agente1", roles.ROL_AGENTE, "agente12345"),
    ("agente2", roles.ROL_AGENTE, "agente12345"),
    ("solicitante1", roles.ROL_SOLICITANTE, "usuario12345"),
    ("solicitante2", roles.ROL_SOLICITANTE, "usuario12345"),
]

# Tickets de ejemplo: (titulo, descripcion, estado, prioridad, solicitante, agente)
TICKETS = [
    ("No enciende la laptop", "La laptop no responde al botón de encendido.",
     Estado.NO_INICIADO, Prioridad.ALTA, "solicitante1", None),
    ("Correo no sincroniza", "Outlook muestra error al sincronizar.",
     Estado.EN_PROCESO, Prioridad.MEDIA, "solicitante1", "agente1"),
    ("Instalar software de diseño", "Solicito instalación de herramienta de diseño.",
     Estado.RESUELTO, Prioridad.BAJA, "solicitante2", "agente1"),
    ("Acceso a carpeta compartida", "Necesito permisos a la carpeta del equipo.",
     Estado.EN_PROCESO, Prioridad.MEDIA, "solicitante2", "agente2"),
    ("Impresora sin tóner", "La impresora del piso 3 pide reemplazo de tóner.",
     Estado.CANCELADO, Prioridad.BAJA, "solicitante1", "agente2"),
    ("VPN se desconecta", "La VPN se cae cada 10 minutos.",
     Estado.RECHAZADO, Prioridad.ALTA, "solicitante2", "agente1"),
    ("Monitor parpadea", "El monitor secundario parpadea de forma intermitente.",
     Estado.RESUELTO, Prioridad.MEDIA, "solicitante1", "agente2"),
]


class Command(BaseCommand):
    help = "Carga usuarios de prueba y tickets de ejemplo (idempotente)."

    def handle(self, *args, **options):
        self.stdout.write("Creando datos de prueba...")

        usuarios = self._crear_usuarios()
        self._crear_tickets(usuarios)

        self.stdout.write(self.style.SUCCESS("¡Datos de prueba cargados!"))
        self.stdout.write("")
        self.stdout.write("Credenciales de acceso:")
        for username, rol, password in USUARIOS:
            self.stdout.write(f"  {rol:<12} usuario='{username}' contraseña='{password}'")

    def _crear_usuarios(self):
        creados = {}
        for username, rol, password in USUARIOS:
            user, nuevo = User.objects.get_or_create(username=username)
            if nuevo:
                user.set_password(password)
            user.is_staff = rol == roles.ROL_ADMIN
            user.is_superuser = username == "admin"
            user.save()

            grupo = Group.objects.get(name=rol)
            user.groups.set([grupo])
            creados[username] = user

            estado = "creado" if nuevo else "ya existía"
            self.stdout.write(f"  Usuario '{username}' ({rol}) {estado}.")
        return creados

    def _crear_tickets(self, usuarios):
        for titulo, desc, estado, prioridad, solicitante, agente in TICKETS:
            # Idempotencia: no duplicar por título + solicitante.
            existe = Ticket.objects.filter(
                titulo=titulo, solicitante=usuarios[solicitante]
            ).exists()
            if existe:
                self.stdout.write(f"  Ticket '{titulo}' ya existía.")
                continue

            ticket = Ticket.objects.create(
                titulo=titulo,
                descripcion=desc,
                estado=estado,
                prioridad=prioridad,
                solicitante=usuarios[solicitante],
                agente=usuarios[agente] if agente else None,
            )
            # Registrar fecha de resolución para métricas de tiempo promedio.
            if estado == Estado.RESUELTO:
                ticket.resuelto_en = ticket.creado + timedelta(hours=6)
                ticket.save(update_fields=["resuelto_en"])

            Comentario.objects.create(
                ticket=ticket,
                autor=usuarios[solicitante],
                texto="Ticket creado por el solicitante.",
            )
            self.stdout.write(f"  Ticket '{titulo}' creado.")
