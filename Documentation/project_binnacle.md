# Introducción

&nbsp;&nbsp;&nbsp;&nbsp;Se explicará a continuación el orden en el que se fueron completando las siguientes historias de usuario, según el checkpoint en el que fueron finalizadas completamente.

# Checkpoint 0

&nbsp;&nbsp;&nbsp;&nbsp;Comienzo de familiarización con los entornos y herramientas de trabajo (docker, heroku, bibliotecas de manejo de bases de datos como Postgre y Mongo, monitoreo de backends con New Relic). Por el lado del front end, al no tener los encargados de su desarrollo experiencia previa en ello, comenzaron a aprender su funcionamiento y a practicar su uso.

# Checkpoint 1

&nbsp;&nbsp;&nbsp;&nbsp;Comienzo de configuración de continuous deployment e integration (CD, CI), familiarización con los entornos de trabajo (docker, heroku, bibliotecas de manejo de bases de datos como Postgre y Mongo, monitorización de backends con New Relic). En este checkpoint se comenzó a usar las distintas herramientas principales del trabajo, se levantaron servers de python con Uvicorn y Fastapi, se levantaron servers con Express, se establecieron conexiones con las bases de datos y se probó producción que estas funcionaran correctamente.  
&nbsp;&nbsp;&nbsp;&nbsp;Una vez terminada la investigación y configuración, se prosiguió a implementar las primeras funcionalidades básicas de la aplicación. Estas son:
- Registrar usuario: en backend se implementó la funcionalidad de registro normal de usuario (es decir, utilizando una cuenta de Ubademy, no un login federado).
- Loguearse como usuario: a pesar de que no se encontraba implementada la pantalla que pide mail y contraseña, sí se utilizaba el endpoint de login para loggear un usuario.
- Loguearse como admin: a pesar de que no se encontraba implementada la pantalla que pide mail y contraseña, sí se utilizaba el endpoint de login para entrar a la pantalla de administrador.
- Registrar admin: se implementó en back la funcionalidad de administradores de registrar otro administrador.
- Ver perfil de usuarios: se permitió obtener la información de tanto el perfil propio como de otros usuarios (tomando en cuenta qué información es pública y qué no), además de poder obtener la información del perfil de otros usuarios como administrador.
- Creación de curso: se agregó en Business la posibilidad de crear un nuevo curso en la base de datos.

Es necesario aclarar que, al no planear implementar funcionalidades relacionadas con los pagos, el backend de Payments no se desarrolló en este checkpoint, sino que se desarrollaron Api Gateway, Users y Business.

# Checkpoint 2

&nbsp;&nbsp;&nbsp;&nbsp;En esta etapa, a pesar de que también se realizaron configuraciones (establecimiento de imágenes locales de docker para las bases de datos, setupeo de pruebas de Api Gateway, etc.), la cantidad fue considerablemente menor a la del checkpoint anterior. Las funcionalidades que fueron implementadas en este período de tiempo son:
- Registro normal de usuario: se terminó de implementar la pantalla de registro de usuario en front end, permitiendo así registrar cualquier usuario con facilidad utilizando la app, sin tener que modificar código.
- Loggeo normal de usuario: se terminó de implementar la pantalla de loggeo normal de usuario, permitiendo así probar utilizando la aplicación el loggeo de cualquier usuario deseado con facilidad.
- Visualización de perfil: se permitió visualizar en la aplicación los perfiles propios y de otros usuarios para un usuario común.
- Pantalla de creación de curso: se creó en la app la pantalla que permite crear un curso.
- Loggeo de admin: se agregó la posibilidad de introducir usuario y contraseña para loggearse a una cuenta específica de administrador el la página de backoffice.
- Registro de admin: se agregó la posibilidad de introducir usuario y contraseña para registrar una nueva cuenta de administrador en la página de backoffice.
- Edición de perfil: se permitió tanto en el backend como en frontend modificar los datos del perfil de un usuario.
- Visualización de curso: se permitió tanto en el backend como en frontend obtener los datos de un curso, para poder visualizarlo en la app.
- Edición de curso: se permitió en el backend modificar los datos de una entrada de un curso.
- Listado de usuarios para administradores: se agregó en backend la posibilidad de listar todos los usuarios de la plataforma para un administrador.


# Checkpoint 3


# Checkpoint 4
