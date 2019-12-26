# Using debian buster because this: https://pythonspeed.com/articles/base-image-python-docker-images/
FROM python:3.7-slim-buster

WORKDIR /app
COPY clinical_trials_api_scraper /app/clinical-trials-api-scraper/clinical_trials_api_scraper
COPY setup.py /app/clinical-trials-api-scraper

RUN pip install /app/clinical-trials-api-scraper

# Run scraper once to bootstrap db then set up cron
CMD update_trials_store.py --max-id 100 --use-sql --host ${GRAPHQL_HOST} --port ${GRAPHQL_PORT} && sleep ${SECONDS_BETWEEN_SCRAPES}
