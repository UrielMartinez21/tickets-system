# 🎫 Sistema de Tickets de Trabajo de TI

Sistema web estilo Jira para gestionar tickets de soporte de TI, con
autenticación por sesiones, roles y permisos, flujo de estados, dashboard de
analítica y exportación a CSV.

> La justificación de tecnologías y la arquitectura detallada están en
> [`DOCUMENTACION.md`](DOCUMENTACION.md).

---

## Características

- 🔐 **Login con sesiones** nativas de Django.
- 👥 **Roles y permisos**: Admin, Agente y Solicitante.
- 🎫 **Tickets** con título, descripción, prioridad, solicitante y agente.
- 🔄 **Flujo de estados** controlado: No iniciado → En proceso → Resuelto, con
  salidas Cancelado y Rechazado.
- 📊 **Dashboard de analítica** con métricas de tickets y usuarios.
- ⬇️ **Exportación a CSV** de tickets, usuarios y métricas.

---

## Requisitos

- Python 3.10 o superior.

---

## Instalación y ejecución

Desde la carpeta raíz del proyecto (`tickets-system/`):

### 1. Crear y activar el entorno virtual

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones (crea la base de datos y los roles)
```bash
python manage.py migrate
```

### 4. Cargar datos de prueba (usuarios y tickets de ejemplo)
```bash
python manage.py seed
```

### 5. Levantar el servidor
```bash
python manage.py runserver
```

Abre tu navegador en: http://127.0.0.1:8000/

---

## Credenciales de prueba

Tras ejecutar `python manage.py seed`:

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Admin | `admin` | `admin12345` |
| Agente | `agente1` | `agente12345` |
| Agente | `agente2` | `agente12345` |
| Solicitante | `solicitante1` | `usuario12345` |
| Solicitante | `solicitante2` | `usuario12345` |

> ⚠️ Estas credenciales son solo para desarrollo/demostración.

---

## Cómo probar las funcionalidades

1. **Login**: entra con `solicitante1`. Crea un ticket nuevo.
2. **Flujo de roles**: cierra sesión y entra como `agente1`. Verás todos los
   tickets; abre uno, autoasígnate y cámbialo a "En proceso" y luego "Resuelto".
3. **Gestión de usuarios**: entra como `admin`, ve a **Usuarios** y crea un
   usuario nuevo asignándole un rol, o cambia el rol de uno existente.
4. **Dashboard**: como `admin` o `agente`, abre el **Dashboard** y descarga los
   CSV de tickets, usuarios y métricas.

---

## Ejecutar las pruebas

```bash
python manage.py test
```

---

## Comprobar la configuración

```bash
python manage.py check
```

---

## Estructura del proyecto

```
tickets-system/
├── config/        # Settings, URLs raíz, WSGI/ASGI
├── accounts/      # Autenticación, roles y gestión de usuarios
├── tickets/       # Tickets, flujo de estados, comentarios
├── dashboard/     # Métricas y exportación CSV
├── core/          # Comando seed (datos de prueba)
├── templates/     # Plantillas HTML
├── static/        # CSS
├── manage.py
├── requirements.txt
├── README.md
└── DOCUMENTACION.md
```
