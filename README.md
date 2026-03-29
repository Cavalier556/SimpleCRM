# SimpleCRM

**SimpleCRM** es una herramienta CRM personal que te permite organizar tus interacciones con socios y proveedores, revisar tus interacciones en gmail, y agendar tareas para el futuro.

![Imagen del sistema](https://github.com/Cavalier556/SimpleCRM/blob/f486523fa03fbce06ab661e82301e9077059e46f/inicio.png)

## Características principaless
* **Gestión de Empresas:** Registra las empresas con las que trabajas
* **Gestión de Contactos:** Registra los contactos con los que interactúas
* **Gestión de Tareas:** Registra tareas pendientes para planear tu tiempo
* **Búsqueda RUC:** Incorpora la base de datos de RUCs para importar datos 
* **Calendario de Tareas:** Visualiza tus tareas y sigue su estado, recibe notificaciones en el dashboard
* **Visualización de Correos:** Accede a tu historial de correos ordenados cronológicamente

## Configuración
* Para poder acceder a los correos, en Google Cloud:
<ul>
  <li>Crea un nuevo proyecto</li>
  <li>Activa el Gmail API</li>
  <li>Selecciona tipo externo para el OAuth</li>
  <li>Agrega tu correo a la lista de usuarios de prueba</li>
  <li>Crea una credencial y guarda el json como credentials.json</li>
</ul> 

* El proyecto utiliza celery y redis para importar los datos de la sunat a la base de datos, activa el servidor usando el siguiente comando:
```
celery -A simplecrm worker -l info -P gevent
```

## Tecnologías utilizadas
* **Django**
* **SQLite**
* **TailwindCSS**
* **HTMX**
* **Celery**
* **Redis**
