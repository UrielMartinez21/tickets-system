"""Pruebas de la app accounts: roles, autenticación y gestión de usuarios."""
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from accounts import roles


class RolesMigracionTests(TestCase):
    """Verifica que la migración de datos creó los grupos con permisos."""

    def test_grupos_existen(self):
        for rol in roles.ROLES:
            self.assertTrue(
                Group.objects.filter(name=rol).exists(),
                f"Falta el grupo '{rol}'",
            )

    def test_admin_tiene_permisos_tickets(self):
        grupo = Group.objects.get(name=roles.ROL_ADMIN)
        codenames = set(grupo.permissions.values_list("codename", flat=True))
        self.assertIn("add_ticket", codenames)
        self.assertIn("change_ticket", codenames)
        self.assertIn("delete_ticket", codenames)
        self.assertIn("view_ticket", codenames)

    def test_solicitante_permisos_limitados(self):
        grupo = Group.objects.get(name=roles.ROL_SOLICITANTE)
        codenames = set(grupo.permissions.values_list("codename", flat=True))
        self.assertIn("add_ticket", codenames)
        self.assertIn("view_ticket", codenames)
        self.assertNotIn("delete_ticket", codenames)


class HelpersRolesTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin_t", password="x")
        self.admin.groups.add(Group.objects.get(name=roles.ROL_ADMIN))
        self.agente = User.objects.create_user("agente_t", password="x")
        self.agente.groups.add(Group.objects.get(name=roles.ROL_AGENTE))
        self.solic = User.objects.create_user("solic_t", password="x")
        self.solic.groups.add(Group.objects.get(name=roles.ROL_SOLICITANTE))

    def test_es_admin(self):
        self.assertTrue(roles.es_admin(self.admin))
        self.assertFalse(roles.es_admin(self.agente))

    def test_es_staff_tickets(self):
        self.assertTrue(roles.es_staff_tickets(self.admin))
        self.assertTrue(roles.es_staff_tickets(self.agente))
        self.assertFalse(roles.es_staff_tickets(self.solic))


class AutenticacionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("juan", password="clave_segura_1")

    def test_login_exitoso(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "juan", "password": "clave_segura_1"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_login_fallido(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "juan", "password": "incorrecta"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_acceso_denegado_sin_sesion(self):
        resp = self.client.get(reverse("tickets:lista"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/cuentas/login/", resp.url)


class GestionUsuariosTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin_g", password="x")
        self.admin.groups.add(Group.objects.get(name=roles.ROL_ADMIN))
        self.solic = User.objects.create_user("solic_g", password="x")
        self.solic.groups.add(Group.objects.get(name=roles.ROL_SOLICITANTE))

    def test_admin_crea_usuario_con_rol(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("accounts:crear_usuario"),
            {
                "username": "nuevo_agente",
                "password1": "ContraseñaFuerte123",
                "password2": "ContraseñaFuerte123",
                "rol": roles.ROL_AGENTE,
            },
        )
        self.assertEqual(resp.status_code, 302)
        nuevo = User.objects.get(username="nuevo_agente")
        self.assertTrue(nuevo.groups.filter(name=roles.ROL_AGENTE).exists())

    def test_no_admin_recibe_403(self):
        self.client.force_login(self.solic)
        resp = self.client.get(reverse("accounts:crear_usuario"))
        self.assertEqual(resp.status_code, 403)
