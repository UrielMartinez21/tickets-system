"""Pruebas de la app tickets: flujo de estados y control por rol."""
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from accounts import roles

from .models import Estado, Prioridad, Ticket, TransicionInvalidaError


class MaquinaEstadosTests(TestCase):
    def setUp(self):
        self.solic = User.objects.create_user("s1", password="x")
        self.ticket = Ticket.objects.create(
            titulo="Prueba",
            descripcion="desc",
            solicitante=self.solic,
            prioridad=Prioridad.MEDIA,
        )

    def test_estado_inicial(self):
        self.assertEqual(self.ticket.estado, Estado.NO_INICIADO)

    def test_transicion_valida(self):
        self.ticket.cambiar_estado(Estado.EN_PROCESO)
        self.assertEqual(self.ticket.estado, Estado.EN_PROCESO)

    def test_flujo_completo_hasta_resuelto(self):
        self.ticket.cambiar_estado(Estado.EN_PROCESO)
        self.ticket.cambiar_estado(Estado.RESUELTO)
        self.assertEqual(self.ticket.estado, Estado.RESUELTO)
        self.assertIsNotNone(self.ticket.resuelto_en)

    def test_transicion_invalida_directa_a_resuelto(self):
        # No iniciado -> Resuelto no es válido (debe pasar por En proceso).
        with self.assertRaises(TransicionInvalidaError):
            self.ticket.cambiar_estado(Estado.RESUELTO)

    def test_no_se_puede_salir_de_estado_cerrado(self):
        self.ticket.cambiar_estado(Estado.CANCELADO)
        with self.assertRaises(TransicionInvalidaError):
            self.ticket.cambiar_estado(Estado.EN_PROCESO)

    def test_salida_a_rechazado(self):
        self.ticket.cambiar_estado(Estado.RECHAZADO)
        self.assertEqual(self.ticket.estado, Estado.RECHAZADO)
        self.assertTrue(self.ticket.esta_cerrado)


class ControlPorRolTests(TestCase):
    def setUp(self):
        self.agente = User.objects.create_user("ag", password="x")
        self.agente.groups.add(Group.objects.get(name=roles.ROL_AGENTE))
        self.solic = User.objects.create_user("so", password="x")
        self.solic.groups.add(Group.objects.get(name=roles.ROL_SOLICITANTE))
        self.otro = User.objects.create_user("otro", password="x")
        self.otro.groups.add(Group.objects.get(name=roles.ROL_SOLICITANTE))

        self.ticket = Ticket.objects.create(
            titulo="T", descripcion="d", solicitante=self.solic
        )

    def test_solicitante_solo_ve_sus_tickets(self):
        self.client.force_login(self.otro)
        resp = self.client.get(reverse("tickets:detalle", args=[self.ticket.id]))
        self.assertEqual(resp.status_code, 404)

    def test_agente_puede_cambiar_estado(self):
        self.client.force_login(self.agente)
        resp = self.client.post(
            reverse("tickets:cambiar_estado", args=[self.ticket.id]),
            {"nuevo_estado": Estado.EN_PROCESO},
        )
        self.assertEqual(resp.status_code, 302)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Estado.EN_PROCESO)

    def test_solicitante_no_puede_cambiar_estado(self):
        self.client.force_login(self.solic)
        resp = self.client.post(
            reverse("tickets:cambiar_estado", args=[self.ticket.id]),
            {"nuevo_estado": Estado.EN_PROCESO},
        )
        self.assertEqual(resp.status_code, 403)

    def test_solicitante_crea_ticket(self):
        self.client.force_login(self.solic)
        resp = self.client.post(
            reverse("tickets:crear"),
            {
                "titulo": "Nuevo",
                "descripcion": "algo",
                "prioridad": Prioridad.ALTA,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            Ticket.objects.filter(titulo="Nuevo", solicitante=self.solic).exists()
        )
