# Introducción

Para probar el trabajo localmente se utilizaron los programas docker y docker-compose. Para instalarlos se debe utilizar los siguientes comandos en la consola: 

`sudo apt-get update`
`sudo apt install docker.io`
`sudo apt install docker-compose`


# Payments y Business

Los servicios de Payments y Business deben ser levantados en simultáneo ya que se comunican entre sí. Para ejecutar instancias de ellos deben llevarse a cabo los siguientes pasos:
- git clone https://github.com/sorianoivan/taller2-ubademy-business.git
- git clone https://github.com/nravesz/taller2-ubademy-payments.git
- Si se quiere ejecutar Payments: se debe entrar a la carpeta `taller2-ubademy-payments` y ejecutar el comando `sudo docker-compose up`, para interactuar con él se deben enviar http requests al puerto 8003.
- Si se quiere ejecutar Business: se debe entrar a la carpeta `taller2-ubademy-business` y ejecutar el comando `sudo docker-compose up`, para interactuar con él se deben enviar http requests al puerto 8002.

# Users

El servicio Users puede ser levantado sin necesidad de ejecutar otro servicio en simultáneo. Para ejecutarlo deben llevarse a cabo los siguientes pasos:
- git clone https://github.com/Drasungor/taller2-ubademy-users.git
- Si se quiere ejecutar Payments: se debe entrar a la carpeta `taller2-ubademy-users` y ejecutar el comando `sudo docker-compose up`, para interactuar con él se deben enviar http requests al puerto 8001.


# Api Gateway
El servicio Api Gateway necesita de todos los servicios previamente mencionados, por lo que si no se tienen clonados sus repositorios se debe hacer lo siguiente:
- git clone https://github.com/Drasungor/taller2-ubademy-users.git
- git clone https://github.com/nravesz/taller2-ubademy-payments.git
- git clone https://github.com/sorianoivan/taller2-ubademy-business.git
- git clone https://github.com/FScaccheri/taller2-ubademy-api_gateway.git
- Si se quiere ejecutar Payments: se debe entrar a la carpeta `taller2-ubademy-api_gateway` y ejecutar el comando `sudo docker-compose up`, para interactuar con él se deben enviar http requests al puerto 8516.