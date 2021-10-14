FROM python

WORKDIR .
COPY . .

ENV USERS_BACKEND_URL='http://0.0.0.0:8001'
ENV PORT=8000

EXPOSE $PORT

RUN pip install -r requirements.txt

CMD python main.py
