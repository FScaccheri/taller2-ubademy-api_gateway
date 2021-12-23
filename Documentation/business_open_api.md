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
exam_creator_email está para corroborar que el que modifica el examen es el creador.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }

## __POST /courses/publish_exam__

Request Body:  
    { 
    course_id: String,  
    questions: Array.of(String),  
    exam_name: String,  
    exam_creator_email: String }

Description:
Crea un examen de nombre exam_name para el curso de course_id recibido utilizando questions para guardar el enunciado. El parámetro
exam_creator_email está para corroborar que el que modifica el examen es el creador.

Responses:

* success => {"status":"ok", "message": ... }

* error => {"status":"error", "message": ... }
