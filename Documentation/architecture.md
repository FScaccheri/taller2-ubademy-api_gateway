# Introducción
Para el desarrollo del producto se utilizó la arquitectura de microservicios. A continuación se detallará de qué forma se distribuyeron las distintas tareas a los distintos servicios, y cuál es la función principal de cada uno. En particular decidimos utilizar el patrón de Api Gateway, que facilita la implementación del front end de la app, haciendo que este solo le tenga que manejar una única dirección para obtener los servicios (de otra manera tendrían que manejar a qué dirección mandar una request para cada acción que quieran realizar).

# Api gateway
Este servicio es la puerta de acceso principal a todas las funcionalidades del programa. Puede ser accedido por cualquier dispositivo y permite acceso a todas las funcionalidades de la aplicación. Al permitir la abstracción del frontend de la existencia de más de un microservicio, es el mismo Api Gateway quien se encarga de delegarle las distintas requests necesarias a los distintos servicios implementados. Puede verse entonces que es el orquestrador que se encarga de que todas las acciones sean ejecutadas en el orden correcto. Un ejemplo de una acción que requiere llamados a más de un backend es el registro de un usuario, ya que en un principio se realiza un registro de la cuenta (mail y contraseña) en el backend Users, y luego (en caso de que la operación haya sido exitosa) se realiza una creación del nuevo perfil del usuario en el backend Business.


# Users



# Business



# Payments


