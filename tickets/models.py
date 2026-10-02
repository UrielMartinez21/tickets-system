"""Modelos de la app tickets: Ticket, Comentario y la máquina de estados."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Estado(models.TextChoices):
    """Estados posibles de un ticket."""

    NO_INICIADO = "no_iniciado", "No iniciado"
    EN_PROCESO = "en_proceso", "En proceso"
    RESUELTO = "resuelto", "Resuelto"
    CANCELADO = "cancelado", "Cancelado"
    RECHAZADO = "rechazado", "Rechazado"


# Estados que se consideran "cerrados" (ya no admiten más transiciones).
ESTADOS_CERRADOS = {Estado.RESUELTO, Estado.CANCELADO, Estado.RECHAZADO}
ESTADOS_ABIERTOS = {Estado.NO_INICIADO, Estado.EN_PROCESO}

# Máquina de estados: define las transiciones válidas.
# Flujo principal: No iniciado -> En proceso -> Resuelto
# Salidas posibles desde estados abiertos: Cancelado y Rechazado.
TRANSICIONES_VALIDAS = {
    Estado.NO_INICIADO: {Estado.EN_PROCESO, Estado.CANCELADO, Estado.RECHAZADO},
    Estado.EN_PROCESO: {Estado.RESUELTO, Estado.CANCELADO, Estado.RECHAZADO},
    Estado.RESUELTO: set(),
    Estado.CANCELADO: set(),
    Estado.RECHAZADO: set(),
}


class Prioridad(models.TextChoices):
    """Niveles de prioridad de un ticket."""

    BAJA = "baja", "Baja"
    MEDIA = "media", "Media"
    ALTA = "alta", "Alta"


class TransicionInvalidaError(ValidationError):
    """Se lanza cuando se intenta una transición de estado no permitida."""


class Ticket(models.Model):
    """Un ticket de trabajo de TI."""

    titulo = models.CharField("Título", max_length=200)
    descripcion = models.TextField("Descripción")
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.NO_INICIADO,
    )
    prioridad = models.CharField(
        "Prioridad",
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets_solicitados",
        verbose_name="Solicitante",
    )
    agente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="tickets_asignados",
        verbose_name="Agente asignado",
        null=True,
        blank=True,
    )
    creado = models.DateTimeField("Creado", auto_now_add=True)
    actualizado = models.DateTimeField("Actualizado", auto_now=True)
    resuelto_en = models.DateTimeField("Resuelto en", null=True, blank=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-creado"]

    def __str__(self):
        return f"#{self.pk} - {self.titulo}"

    @property
    def esta_cerrado(self):
        return self.estado in ESTADOS_CERRADOS

    @property
    def esta_abierto(self):
        return self.estado in ESTADOS_ABIERTOS

    def transiciones_posibles(self):
        """Lista de estados a los que este ticket puede transicionar."""
        return sorted(TRANSICIONES_VALIDAS.get(self.estado, set()))

    def puede_transicionar_a(self, nuevo_estado):
        """Indica si la transición al nuevo estado es válida."""
        return nuevo_estado in TRANSICIONES_VALIDAS.get(self.estado, set())

    def cambiar_estado(self, nuevo_estado):
        """Cambia el estado validando la transición.

        Lanza TransicionInvalidaError si la transición no está permitida.
        Actualiza resuelto_en al pasar a Resuelto.
        """
        nuevo_estado = str(nuevo_estado)
        if nuevo_estado == self.estado:
            raise TransicionInvalidaError(
                f"El ticket ya está en estado "
                f"'{self.get_estado_display()}'."
            )
        if not self.puede_transicionar_a(nuevo_estado):
            raise TransicionInvalidaError(
                f"No se puede pasar de '{self.get_estado_display()}' al "
                f"estado solicitado."
            )
        self.estado = nuevo_estado
        if nuevo_estado == Estado.RESUELTO:
            self.resuelto_en = timezone.now()
        self.save()


class Comentario(models.Model):
    """Comentario o entrada de historial asociada a un ticket."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Ticket",
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comentarios",
        verbose_name="Autor",
        null=True,
    )
    texto = models.TextField("Comentario")
    creado = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["creado"]

    def __str__(self):
        return f"Comentario de {self.autor} en {self.ticket}"
