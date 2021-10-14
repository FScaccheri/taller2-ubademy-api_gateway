FROM python

WORKDIR .
COPY . .

ENV USERS_BACKEND_URL='http://localhost:8001'
ENV PORT=8000

EXPOSE $PORT

RUN pip install -r requirements.txt
RUN pip install newrelic

ENV NEW_RELIC_CONFIG_FILE='newrelic.ini'

CMD newrelic-admin run-program python main.py
