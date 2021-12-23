# Business service endpoints

## __POST /courses/create

Parameters: None

Request Body:  
    { 
        email: String,  
        title: String,  
        description: String,  
        total_exams: Number.min(1).max(10),  
        country: config.get_available_countries(),  
        course_type: String,  
        subscription_type: config.get_subscription_names(),  
        hashtags: Array.of(String),  
        images: Array.of(String),  
        videos: Array -> Video: {name: string, url: string}}

Description:  
Crea un nuevo curso con el mail del creador, usando el body recibido.

Responses:

* success => {"status":"ok", "message":"course succesfully created", "id": course_id}

* error => {"status":"error", "message": ... }


## __GET /courses/data/:id/:email/:privilege__

Parameters: id, email, privilege

Request Body: None

Description:
Retorna información del curso recibido en id, chequeando con email y privilege los datos que debería poder ver el usuario.
Si el usuario es dueño del curso o administrador recibirá toda la información disponible, si es un estudiante del curso entonces
no recibirá información sobre los colaboradores y los estudiantes, y si no se encuentra relacionado con el curso solo recibirá cosas
básicas como la foto de preview del curso, el nombre, el creador, el id y una descripción.

Responses:

* success => {"status":ok, "message": ..., "course": course_data, "info_level": info_level}

* error => {"status":"error", "message": ...}

## __GET /courses/organized/:course_filter/:subscription_filter/:is_admin__

Parameters: course_filter, subscription_filter, is_admin

Request Body: None

Description: 
Retorna una lista de cursos con su id, foto re preview, nombre de curso y creador, y una descripción. Se 
le puede aplicar filtros para obtener ciertos cursos específicos, pudiendo filtrar según el género de curso y el tipo
de suscripción.

Responses:

* success => {"status":"ok", "message": ..., "courses": courses_list }

* error => {"status":"error", "message": ... }



## __PUT /courses/update__

Request Body: 
    { 
        id: String,  
        email: String,  
        title: String,  
        description: String,  
        total_exams: Number.min(1).max(10),  
        country: config.get_available_countries(),  
        course_type: String,  
        subscription_type: config.get_subscription_names(),  
        hashtags: Array.of(String),  
        images: Array.of(String),  
        videos: Array -> Video: {name: string, url: string}}

Description:
Actualiza los datos de un curso utilizando el id para encontrarlo, y el resto de los datos para modificarlo.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }


## __POST /courses/create_exam__

Request Body:  
    { 
    course_id: String,  
    questions: Array.of(String),  
    exam_name: String,  
    exam_creator_email: String }

Description:
Crea un examen de nombre exam_name para el curso de course_id recibido utilizando questions para guardar el enunciado. El parámetro
exam_creator_email está para corroborar que el que crea el examen es el creador del curso.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }



## __POST /courses/edit_exam__

Request Body:  
    { 
    course_id: String,  
    questions: Array.of(String),  
    exam_name: String,  
    exam_creator_email: String }

Description:
Crea un examen de nombre exam_name para el curso de course_id recibido utilizando questions para modificar el enunciado. El parámetro
exam_creator_email está para corroborar que el que edita el examen es el creador del curso.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }



## __POST /courses/publish_exam__

Request Body:  
    { 
    course_id: String,  
    exam_name: String,  
    exam_creator_email: String }

Description:
Publica el examen de nombre exam_name para el curso de course_id recibido, haciendo sea visible para los alumnos y que no pueda ser 
editado a partir de este momento. El parámetro exam_creator_email está para corroborar que el que modifica el examen es el creador.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }


## __POST /courses/complete_exam__

Request Body:  
    { 
    course_id: String,  
    answers: Array.of(String),  
    exam_name: String,  
    student_email: String }

Description:
Introduce en el sistema las respuestas de un estudiante del curso para un examen publicado. El parámetro answers debe tener la misma cantidad
de elementos que cantidad de preguntas tenga el examen.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /courses/grade_exam__

Request Body:  
    { 
    course_id: String,
    corrections: Array.of(String),
    exam_name: String,
    student_email: String,
    professor_email: String,
    mark: Number.min(0).max(10) }

Description:
Introduce en el sistema las correcciones de un docente para un examen de un estudiante del curso, junto con la nota que le asigna. 
El parámetro corrections debe tener la misma cantidad de elementos que cantidad de preguntas tenga el examen. Una nota de 4 a 10 se considera
como aprobado, el resto se considera reprobado. En caso de que el examen haya sido aprobado, se corroborará si el alumno aprobó todos los exámenes
publicados del curso, agregando el curso a su lista de cursos aprobados si se da el caso.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __GET /courses/exams/:id/:filter/:user_email__

Parameters: id, filter, user_email

Request Body: None

Description: 
Retorna una lista con los nombres de los exámenes de los cursos y su estado de publicación, filtrados según el tipo de filtro que haya recibido.
Si filter es none retornará todos los exámenes, si es published retornará solo los publicados, y si es not_published 
retornará solo los no publicados. Si el usuario es un estudiante del curso y pide los exámenes con algún filtro, se
ignorará y se retornarán los exámenes publicados. Si el usuario no pertenece al curso (no es estudiante ni docente)
se rechazará el pedido.

Responses:

* success => {"status":"ok", "message": ..., "courses": exams_list }

* error => {"status":"error", "message": ... }


## __GET /courses/:id/students_exams/:email/:filter__

Parameters: id, filter, user_email

Request Body: None

Description: 
Retorna una lista con los exámenes rendidos por los alumnos del curso, indicando el mail del alumno que lo rindió, el nombre del examen rendido y
si el examen fue corregido o no ("Graded" o "Not graded"). Si el usuario que pide esta información no es un docente del curso entonces se rechaza el pedido

Responses:

* success => {"status":"ok", "message": ..., "exams": students_exams_list }

* error => {"status":"error", "message": ... }


## __GET /courses/:id/exam/:email/:exam_name/:projection/:student_email__

Parameters: id, email, exam_name, projection, student_email

Request Body: None

Description: 
Retorna la información de un examen particular, dependiendo de quién sea el que lo está pidiendo. Si email pertenece a un alumno del curso, entonces
solo podrá pedir exámenes suyos, sino se rechazará el pedido (si email != student_email). Si el email es de un docente del curso, entonces puede acceder 
a la información de cualquier examen de este. El parámetro projection indica qué información se quiere ver del examen, si es "quiestions" entonces retornará
el enunciado del examen (en ese caso se ignora el parámetro student_email), si es completed_exam entonces se retornará el examen completado (preguntas, respuestas
del alumno, y correcciones del docente junto con la nota si es que fue corregido).

Responses:

* success => {"status":"ok", "message": ..., "exams": students_exams_list }

* error => {"status":"error", "message": ... }

## __POST /courses/add_collaborator__

Request Body:  
    { 
    course_id: String,  
    user_email: String,  
    collaborator_email: String }

Description:
Agrega a un curso el usuario como colaborador. Esto puede hacerse solo si el colaborador a agegar no es un estudiante del curso o el creador. 
Si user_email no es del creador del curso entonces se rechaza el pedido.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __GET /courses/:id/studends/:user_email/:exam_name__

Parameters: id, user_email, exam_name

Request Body: None

Description: 
Retorna una lista con los estudiantes inscriptos en el curso, con la posibilidad de aplicar un filtro. Si exam_name es "none", entonces se devuelve
una lista con todos los alumnos que están inscriptos, si se especifica un examen del curso, entonces se devuelve una lista con los alumnos que rindieron
ese examen, independientemente de su estado de correción o su nota.

Responses:

* success => {"status":"ok", "message": ..., "names": students_names }

* error => {"status":"error", "message": ... }

## __GET /courses/passing_courses/:user_email__

Parameters: user_email

Request Body: None

Description: 
Retorna una lista con el nombre y el creador del curso para cada curso que haya aprobado completamente el usuario de mail user_email. Retorna
error si el perfil del usuario no existe.

Responses:

* success => {"status":"ok", "message": ..., "names": students_names }

* error => {"status":"error", "message": ... }

## __POST /courses/grade_course__

Request Body:  
    { 
    course_id: String,  
    user_email: String,  
    comment: String,  
    grade: Number.min(0).max(5) }

Description:
Agrega la opinion del usuario user_email a la lista de opiniones del curso. Retorna error si el usuario ya había realizado una review anterior
o si no es un alumno inscripto en el curso. Recibe un comentario sobre el curso y una nota numérica para puntuarlo.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __GET /courses/students_gradings/:id__

Parameters: id

Request Body: None

Description: 
Retorna una lista con las opiniones del curso recibido, guardando en cada elemento el mail del estudiante que la realizó, su comentario, y la nota
que le asignó al curso, retorna también un número que es el promedio de todas las notas que los estudiantes le asignaron al curso (si tiene al menos
una opinión).

Responses:

* success => {"status":"ok", "message": ..., "gradings": students_gradings, "average": course_average }
* success => {"status":"ok", "message": ..., "gradings": [] }

* error => {"status":"error", "message": ... }

## __POST /profiles/crete__

Request Body:  
    { 
    name: string  
    profile_picture_link: string  
    email: string  
    country: string  
    subscription_type: string | undefined  
    interesting_genres: string[] }

Description:
Crea un perfil para el usuario, inicializándolo con los datos recibidos en el schema. Retorna error en caso de que el perfil ya existiera 
previamente (se repite el email).

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /profiles/update__

Request Body:  
    { 
    name: string  
    profile_picture_link: string  
    email: string  
    country: string  
    interesting_genres: string[] }

Description:
Actualiza el perfil del usuario con el mail recibido, actualizando el resto de los datos guardados en el body.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /profiles/upgrade_subscription__

IVI

Request Body:  
    { 
    name: string  
    profile_picture_link: string  
    email: string  
    country: string  
    interesting_genres: string[] }

Description:
Actualiza el perfil del usuario con el mail recibido, actualizando el resto de los datos guardados en el body.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /profiles/modify_subscription__

IVI

Request Body:  
    { 
    name: string  
    profile_picture_link: string  
    email: string  
    country: string  
    interesting_genres: string[] }

Description:
Actualiza el perfil del usuario con el mail recibido, actualizando el resto de los datos guardados en el body.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /profiles/pay_subscription__

IVI

Request Body:  
    { 
    name: string  
    profile_picture_link: string  
    email: string  
    country: string  
    interesting_genres: string[] }

Description:
Actualiza el perfil del usuario con el mail recibido, actualizando el resto de los datos guardados en el body.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /profiles/validate_subscription__

IVI

Request Body:  
    { 
    name: string  
    profile_picture_link: string  
    email: string  
    country: string  
    interesting_genres: string[] }

Description:
Actualiza el perfil del usuario con el mail recibido, actualizando el resto de los datos guardados en el body.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __GET /profiles/countries

Request Body: None

Description: 
Retorna una lista con los nombres de los paises que acepta la aplicación.

Responses:

* success => {"status":"ok", "message": ..., "locations": locations_list }

* error => {"status":"error", "message": ... }

## __GET /profiles/course_genres

Request Body: None

Description: 
Retorna una lista con los tipos de cursos que acepta la aplicación.

Responses:

* success => {"status":"ok", "message": ..., "course_genres": locations_list }

* error => {"status":"error", "message": ... }

## __GET /profiles/subscription_types

Request Body: None

Description: 
Retorna una lista con los nombres y precios de los tipos de suscripción que ofrece la aplicación.

Responses:

* success => {"status":"ok", "message": ..., "course_genres": locations_list }

* error => {"status":"error", "message": ... }

## __GET /profiles/subscription_types_names

Request Body: None

Description: 
Retorna una lista con los nombres de los tipos de suscripción que ofrece la aplicación.

Responses:

* success => {"status":"ok", "message": ..., "course_genres": locations_list }

* error => {"status":"error", "message": ... }

## __GET /profiles/:user_email/:account_type/:profile_email

Request Body: None

Description: 
Retorna los datos de un perfil del usuario de mail profile_email. Utiliza user_email y account_type para verificar
a qué tipo de información puede acceder el usuario que esta pidiendo el perfil. Un administrador puede acceder a 
toda la información de cualquier perfil. Un usuario puede acceder a toda la información de su propio perfil, y 
únicamente a la información pública de los perfiles de otros usuarios.

Responses:

* success => {"status":"ok", "message": ..., "profile": profile_to_send }

* error => {"status":"error", "message": ... }

## __POST /profiles/subscribe_to_course__

Request Body:  
    { 
    course_id: String,  
    user_email: String }

Description:
Suscribe al usuario de mail user_email al curso de id course_id si el tipo de suscripción al que está inscripto es de nivel
igual o mayor al del curso al que se está suscribiendo, sino retorna un mensaje de error. Envía un mensaje de error también en
caso de que el usuario o el curso no existan.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /profiles/unsubscribe_from_course__

Request Body:  
    { 
    course_id: String,  
    user_email: String }

Description:
Desususcribe al usuario de mail user_email al curso de id course_id. Envía un mensaje de error también en
caso de que el usuario o el curso no existan.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }