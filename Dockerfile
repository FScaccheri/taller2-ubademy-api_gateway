FROM python

WORKDIR /app
COPY . .

ENV USERS_BACKEND_URL='http://backend_users:8001'
ENV PORT=8000

ENV BUSINESS_BACKEND_URL='http://backend_business:8002'

ENV PAYMENTS_BACKEND_URL='http://backend_payments:8003'

ENV USERS_API_KEY='db927b6105712695971a38fa593db084d95f86f68a1f85030ff5326d7a30c673'
ENV BUSINESS_API_KEY='faf5b8b0651b9baf0919f77f5b50f9b872b3521f922c14c0ad12f696b50c1b73'
ENV PAYMENTS_API_KEY='03aaeb781af46e2f06a9784c2a8e4b26a3fd89f96ad08e2988917ba76f7d9933'

EXPOSE $PORT

RUN pip install -r requirements.txt
RUN pip install newrelic

ENV NEW_RELIC_CONFIG_FILE='newrelic.ini'

CMD newrelic-admin run-program python main.py
