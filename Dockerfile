FROM ubuntu

WORKDIR /app
RUN apt-get update
RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get install -y --reinstall libpq-dev
RUN pip3 install -r requirements.txt
#RUN pip3 install fastapi
#RUN pip3 install pydantic
#RUN pip3 install passlib
#RUN pip3 install typing
#RUN pip3 install uvicorn
RUN pip3 install requests
RUN pip3 install python-jose
RUN pip3 install python-multipart
#RUN pip3 install python-dotenv
#RUN pip3 install Crypto

ENV PORT=8000

#TODO: HAY QUE CONFIGURARLO CON DOCKER COMPOSE
ENV USERS_BACKEND_LINK = "https://localhost:8003/"
EXPOSE $PORT
COPY main.py /app/
COPY models /app/models

CMD python3 main.py
