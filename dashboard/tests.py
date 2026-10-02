"""Pruebas de la app dashboard: métricas y exportación CSV."""
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from accounts import roles
from tickets.models import Estado, Prioridad, Ticket

from . import metrics


class MetricasTests(TestCase):
    def setUp(self):
        self.agente = User.objects.create_user("agm", password="x")
        self.agente.groups.add(Group.objects.get(name=roles.ROL_AGENTE))
        self.solic = User.objects.create_user("som", password="x")
        self.solic.groups.add(Group.objects.get(name=roles.ROL_SOLICITANTE))

        # 3 tickets: 1 no iniciado, 1 en proceso, 1 resuelto.
        Ticket.objects.create(
            titulo="A", descripcion="d", solicitante=self.solic,
            prioridad=Prioridad.ALTA, estado=Estado.NO_INICIADO,
        )
        Ticket.objects.create(
            titulo="B", descripcion="d", solicitante=self.solic,
            prioridad=Prioridad.MEDIA, estado=Estado.EN_PROCESO,
            agente=self.agente,
        )
        resuelto = Ticket.objects.create(
            titulo="C", descripcion="d", solicitante=self.solic,
            prioridad=Prioridad.BAJA, estado=Estado.RESUELTO,
            agente=self.agente,
        )
        resuelto.resuelto_en = resuelto.creado + timedelta(hours=4)
        resuelto.save(update_fields=["resuelto_en"])

    def test_total_por_estado(self):
        datos = dict(metrics.totales_por_estado())
        self.assertEqual(datos["No iniciado"], 1)
        self.assertEqual(datos["En proceso"], 1)
        self.assertEqual(datos["Resuelto"], 1)

    def test_abiertos_vs_cerrados(self):
        datos = metrics.abiertos_vs_cerrados()
        self.assertEqual(datos["abiertos"], 2)
        self.assertEqual(datos["cerrados"], 1)

    def test_tickets_por_agente(self):
        datos = dict(metrics.tickets_por_agente())
        self.assertEqual(datos["agm"], 2)

    def test_tiempo_promedio_resolucion(self):
        promedio = metrics.tiempo_promedio_resolucion_horas()
        self.assertAlmostEqual(promedio, 4.0, places=1)

    def test_ultimos_30_dias(self):
        self.assertEqual(metrics.tickets_ultimos_30_dias(), 3)


class ExportacionCSVTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("adm", password="x")
        self.admin.groups.add(Group.objects.get(name=roles.ROL_ADMIN))
        self.solic = User.objects.create_user("sol", password="x")
        self.solic.groups.add(Group.objects.get(name=roles.ROL_SOLICITANTE))
        Ticket.objects.create(
            titulo="Export", descripcion="d", solicitante=self.solic
        )

    def test_exportar_tickets_csv(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("dashboard:exportar_tickets"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])
        self.assertIn("attachment", resp["Content-Disposition"])
        contenido = resp.content.decode("utf-8")
        self.assertIn("Export", contenido)
        self.assertIn("Título", contenido)

    def test_exportar_metricas_csv(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("dashboard:exportar_metricas"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Total de tickets", resp.content.decode("utf-8"))

    def test_solicitante_no_accede_dashboard(self):
        self.client.force_login(self.solic)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 403)

    def test_solicitante_no_exporta(self):
        self.client.force_login(self.solic)
        resp = self.client.get(reverse("dashboard:exportar_tickets"))
        self.assertEqual(resp.status_code, 403)
