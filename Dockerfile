FROM python:3.5-alpine

WORKDIR /app
ADD clinical_trials_api_scraper /app/clinical-trials-api-scraper/clinical_trials_api_scraper
ADD setup.py /app/clinical-trials-api-scraper

RUN pip install /app/clinical-trials-api-scraper

CMD update_trials_store.py --max-id 100 --in-memory
