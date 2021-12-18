# Introducción
&nbsp;&nbsp;&nbsp;&nbsp;A lo largo del cuatrimestre se estuvo implementando un programa llamado "Ubademy", un clon de sitios de clases online. Para lograrlo se utilizó una arquitectura de microservicios, utilizando el patrón de Api Gateway. A continuación se explicarán tecnicismos de la aplicación tanto en forma macroscópica como microscópica.


# Api gateway
&nbsp;&nbsp;&nbsp;&nbsp;El servicio de Api Gateway fue implementado utilizando el lenguaje de programación Python, junto con una cantidad de bibliotecas excternas que facilitaron la contrsucción del backend. Su razón de ser es delegar los distintos procesos a realizar en los backends correspondientes. las bibliotecas utilizadas son:  
- Uvicorn: es la biblioteca utilizada para levantar un server que escucha requests, es utilizado por FastApi para poder procesarlas correctamente.
- FastApi: es la bilbioteca que fue usada principalmente, en conjunto con otras bibliotecas. Se encarga de procesar los requests HTTP que llegan al servidor levantado con uvicorn, facilitando enormemente la creación de endpoints y dejando así mayor tiempo de desarrollo para las funcionalidades con las que dichos endpoints están asociados. Esta biblioteca no fue utilizada únicamente para el parseo de requests recibidas, sino que también para la creación de schemas para los cuerpos de los requests HTTP, lo cual también facilita el trabajo manual de chequeos (se verá luego que en el caso de los servidores que corren node, a pesar de usar bibliotecas externas, se debió realizar un trabajo más manual para asegurar cierta composición de los cuerpos de los pedidos HTTP). 
- Requests: fue utilizado para enviar los requests necesarios a los otros servicios del backend (como se indicó en el archivo de descripción de la arquitectura, api gateway se encarga de delegar las distintas tareas del servidor a los correspondientes backends).
- jose: es la biblioteca utilizada para validar los requests que le llegan de un usuario al servidor, es decir, es la biblioteca que genera y valida JWTs, permitiendo asegurar que los pedidos HTTP pertenecen a usuarios loggeados al sistema y, de esa forma, identificarlos, previniendo la posibilidad de cambios imprevistos en cuentas de usuarios por falta de chequeo de validez de la información recibida. Al generarse un JWT con una clave secreta conocida únicamente por Api Gateway, únicamente este puede desencriptar el mensaje enviado en cada request y, por lo tanto, verificar que la información no solo sea válida, sino que además haya sido enviada por alguien que previamente validó el servidor.

# Users

## Introducción
&nbsp;&nbsp;&nbsp;&nbsp;El servicio de users fue implementado utilizando el lenguaje de programación Python, al igual que Api Gateway. Este servicio se encarga de validar la existencia de un usuario que intenta loggearse, además de permitir el registro de nuevos usuarios. Permite el login tanto de usuarios registrados con la implementación propia de registro como con el uso de una identidad federada, que en este caso se trata de; además de manejar si cada usuario puede o no entrar a su cuenta (que puede estar bloqueada). Maneja también el login y registro de administradores, que son usuarios con permisos que un usuario normal no posee.  

## Base de datos
&nbsp;&nbsp;&nbsp;&nbsp;Para el registro de usuarios, se utilizó una base de datos Postgres hosteada por Heroku, y para interactuar con ella se utiliza la biblioteca SqlAlchemy, aprovechando sus funcionalidades de Object Relational Mapping (ORM). Por esto se crearon distintos objetos que representan entradas de las distintas tablas que fueron creadas. Los distintos modelos creados son los siguientes:

### User
```
class User(Base):
    __tablename__ = "users"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    hashed_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    firebase_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    is_blocked = Column(Boolean(), nullable = False)
    registration_date = Column(DateTime(), nullable = False)
    last_login_date = Column(DateTime(), nullable = False

    TODO: UPDATEAR CON LA DATA DEL EXPO TOKEN

```

&nbsp;&nbsp;&nbsp;&nbsp;Puede verse que un usuario normal almacena el email (que es lo utilizado para identificarlo en la plataforma, puede verse que es la primary key de la tabla, por lo que no puede repetirse), una contraseña hasheada y con sal (para proteger la cuenta del usuario en caso de que se filtren las contraseñas), una contraseña de firebase para que el usuario pueda utilizar correctamente la funcionalidad de chat, y una columna llamada is_blocked, que indica si el usuario se encuentra o no bloqueado de su cuenta y, por lo tanto, si puede acceder a ella o no. Por otro lado, pueden verse las columnas registration_date y last_login_date, que se utilizan para poder calcular métricas de registro y loggeo de usuarios en cierta ventana de tiempo (para que sea simple testear, se decidió tener una ventana de 1 día de registro y 1 hora de login, es decir, serán tomados en cuenta para 
las métricas de registro aquellos que se hayan registrado en la cuenta hace menos de 1 día, y para login los que se hayan loggeado hace menos de 1 hora).


### Google
```
class Google(Base):
    __tablename__ = "Google"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    firebase_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    is_blocked = Column(Boolean(), nullable = False)
    registration_date = Column(DateTime(), nullable = False)
    last_login_date = Column(DateTime(), nullable = False)

    TODO: UPDATEAR CON LA DATA DEL EXPO TOKEN

```

&nbsp;&nbsp;&nbsp;&nbsp;Es evidente que la tabla de usuarios que se loggean con Google es muy similar a la de los usuarios que utilizan nuestro sistema de registro propio, con la diferencia de que estos no tienen contraseña. Esto se debe claramente al hecho de que, al utilizar el loggeo con Google, el usuario está utilizando su contraseña de Google para generar el certificado que a nosotros nos indica que es un usuario válido.


### Admin
```
class Admin(Base):
    __tablename__ = "admins"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    hashed_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    name = Column(String(database_shared_constants.CONST_NAME_LENGTH), nullable = False)
```

&nbsp;&nbsp;&nbsp;&nbsp;Fue implementado también el usuario de tipo admin, que es un tipo de usuario distinto con permisos que un usuario normal no posee. Puede verse que solo tiene un mail, un nombre y una contraseña (hasheada al igual que en el caso de un usuario normal). Es un usuario de distinta categoría, a pesar de que los mails de los admins no pueden repetirse entre sí, no hay problema si un mail es utilziado para una cuenta normal y de admin. Un admin no tiene las funcionalidades del usuario normal (suscripción, creación de curso, etc.).

## Bibliotecas

Como se dijo previamente, las bibliotecas utilizadas por este servicio son:
- Uvicorn: por las mismas razones que en Api Gateway, levanta el servidor que escuchará los requests que vienen de Api Gateway.
- Fastapi: por las mismas razones que en Api Gateway, permite abstraerse del parseo de mensajes recibidos, redirigiendo los distintos requests HTTP a la función que la maneja de la forma apropiada.
- Psychopg2: para manejar las distintas causas de errores al momento de actualizar las tablas de usuarios y así responder con un mensaje de error apropiado.
- SqlAlchemy: como se dijo previamente, para manejar el mapeo de objetos de Python a entradas de tablas, utilizando sus funcionalidades de Object Relational Mapping (ORM).
- Passlib: utilizada para el hasheo de la contraseña de usuario y para la generación de una contraseña aleatoria para firebase.

## Funcionalidades

### Registro y log in

&nbsp;&nbsp;&nbsp;&nbsp;Como se dijo previamente, este backend se encarga del registro y login de usuarios, para esto se utiliza una serie de endpoints, unos para el registro y login de un usuario normal, y otro para el registro o login de un usuario que utiliza Google para entrar a la aplicación.  
&nbsp;&nbsp;&nbsp;&nbsp;Si el usuario quiere tener una cuenta con contraseña manejada por Ubademy, entonces primero deberá registrarse, proporcionando el usuario y contraseña que querrá usar para loguearse las siguientes veces. Si por otro lado quiere registrarse y loguearse utilizando una cuenta de Google, entonces deberá hacer log in en la cuenta de Google para obtener un token, que será validado por Api Gateway, si este es aprobado entonces se le indicará a Users que se quiere loguear un usuario con identidad federada. Si el usuario ya existía entonces simplemente se retorna que este ya existía, sino se guarda en la tabla de usuarios con login federado y se retorna en el mensaje de respuesta que el usuario fue registrado.  
&nbsp;&nbsp;&nbsp;&nbsp;Es necesario aclarar que un usuario no puede loggearse de las dos formas, sino que debe escoger una. En caso de que tenga una cuenta normal se le negará el acceso con login federado, y en caso de que su cuenta se haya creado por utilizar un login federado no se le permitirá crear una cuenta normal. Esto se realiza haciendo una query en cada tabla según lo necesite el contexto sabiendo así en qué tabla realmente está guardado el usuario.

### Obtención de métricas
&nbsp;&nbsp;&nbsp;&nbsp;Esta funcionalidad retorna la cantidad total de usuarios de la plataforma, la cantidad de usuarios que se registraron el último día, la cantidad de usuarios bloqueados, y la cantidad de usaurios que se loguearon en la última hora, siempre diviendo seǵun el tipo de login del usuario (excepto en la cantidad de usuarios de la plataforma y la cantidad de usuarios bloqueados). Esta funcionalidad solo debe ser accedida por un administrador, sin embargo, el chequeo necesario es realizado por Api Gateway, quien rebota al usuario si no cumple con los requisitos necesarios.

TODO: AGREGAR INFORMACIÓN SOBRE EL ENVIADO DE MENSAJES

# Business

## Introducción
&nbsp;&nbsp;&nbsp;&nbsp;El servicio de users fue implementado en Javascript, utilizando Node js. Este servicio se encarga de realizar las operaciones necesarias para que el usuario pueda interactuar con la aplicación de la forma apropiada, es decir, todas las funcionalidades que permiten que un usuario interactúe con cursos y otros usuarios. A continuación se explicará más en detalle las distintas secciones del backend.

## Base de datos
A diferencia del servicio Users, Business interactúa con una base de datos no relacional de Mongo, hosteada en Atlas. Allí almacena todos los datos necesarios para la funcionalidad general de la app, los cursos creados, los perfiles, los examenes y los pagos realizados.

### Profile

```
class UserProfile
    name: string;
    profile_picture_link: string;
    email: string;
    country: string;
    subscription_type: string;
    interesting_genres: string[];
    collaborator_courses: string[];
    subscribed_courses: string[];
    passed_courses: string[];
```

Puede verse que el perfil guarda el nombre del usuario, un link que lleva a su foto de perfil (hosteada en firebase), su email de registro (que es único para cada perfil, no puede repetirse), el país al que pertenece el usuario, los géneros de cursos que le interesan, el tipo de suscripción, los ids de los cursos en los que colabora, los id de los cursos a los que está suscripto, y los ids de los cursos que aprobó. Toda esta información es utilizada para las operaciones normales de los usuarios, como se verá en las siguientes secciones del documento.

### Course

```
class Course 
    creator_email: string;
    title: string;
    description: string;
    total_exams: Number;
    hashtags: string[];
    images: string[];
    videos: Array<Video>;
    country: string;
    course_type: string;
    subscription_type: string;
    collaborators: string[];
    students: string[];
    students_grading: CourseGrading[];


interface Video 
    name: string;
    url: string;

class CourseGrading 
    student_email: string;
    comment: string;
    grade: Number;

```

Puede verse que el documento de cursos guarda una mayor cantidad de elementos en cada entrada que el perfil, esto se debe a que es utilizada para muchas mas funcionalidades. Estas se analizarán luego, explicando qué entradas de los documentos utilizan para funcionar correctamente.


### Exam

```
class Exam
    exam_name: string;
    questions: string[];
    students_exams: CompletedExam[];
    is_published: boolean;


class CompletedExam
    student_email: string;
    answers: string[];
    professors_notes: string[];
    mark: Number;
```

Al igual que en el caso de los cursos, al utilizarse para una gran cantidad de funcionalidades, se explicarán en detalle los campos mostrados cuando se indique los usos que se les dan.

## Bibliotecas

Las bibliotecas que se utilizaron para la implementación del backend Business son las siguientes:
- Mongodb: es una de las bibliotecas de mayor importancia del programa, es utilizada para todas las interacciones realizadas con la base de datos, permite la implementación de todas las funcionalidades que requieren persistencia de datos en disco, por lo que permitió la implementación de la mayoría de los servicios que requiere el usuario de la app.
- Express: es utilizado para cumplir las funcionalidades de Fastapi y levantar el servidor, es decir, se encarga de generar un servidor que acepta conexiones para hacer pedidos HTTP, y además parsea los mensajes recibidos para mapear los requests HTTP a los endpoints (y por lo tanto funciones e implementaciones) correspondientes.

# Payments


