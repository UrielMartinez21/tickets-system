"""Migración inicial de la app tickets."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titulo", models.CharField(max_length=200, verbose_name="Título")),
                ("descripcion", models.TextField(verbose_name="Descripción")),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("no_iniciado", "No iniciado"),
                            ("en_proceso", "En proceso"),
                            ("resuelto", "Resuelto"),
                            ("cancelado", "Cancelado"),
                            ("rechazado", "Rechazado"),
                        ],
                        default="no_iniciado",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "prioridad",
                    models.CharField(
                        choices=[
                            ("baja", "Baja"),
                            ("media", "Media"),
                            ("alta", "Alta"),
                        ],
                        default="media",
                        max_length=10,
                        verbose_name="Prioridad",
                    ),
                ),
                (
                    "creado",
                    models.DateTimeField(auto_now_add=True, verbose_name="Creado"),
                ),
                (
                    "actualizado",
                    models.DateTimeField(auto_now=True, verbose_name="Actualizado"),
                ),
                (
                    "resuelto_en",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Resuelto en"
                    ),
                ),
                (
                    "agente",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tickets_asignados",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Agente asignado",
                    ),
                ),
                (
                    "solicitante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets_solicitados",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Solicitante",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ticket",
                "verbose_name_plural": "Tickets",
                "ordering": ["-creado"],
            },
        ),
        migrations.CreateModel(
            name="Comentario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("texto", models.TextField(verbose_name="Comentario")),
                (
                    "creado",
                    models.DateTimeField(auto_now_add=True, verbose_name="Creado"),
                ),
                (
                    "autor",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="comentarios",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Autor",
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comentarios",
                        to="tickets.ticket",
                        verbose_name="Ticket",
                    ),
                ),
            ],
            options={
                "verbose_name": "Comentario",
                "verbose_name_plural": "Comentarios",
                "ordering": ["creado"],
            },
        ),
    ]
