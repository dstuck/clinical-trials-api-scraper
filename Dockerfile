FROM python:3.5-alpine

WORKDIR /app
COPY clinical_trials_api_scraper /app/clinical-trials-api-scraper/clinical_trials_api_scraper
COPY setup.py /app/clinical-trials-api-scraper

RUN pip install /app/clinical-trials-api-scraper

#Set up cron
COPY daily-trials-scraping /etc/cron.d/daily-trials-scraping
RUN chmod 0644 /etc/cron.d/daily-trials-scraping
RUN crontab /etc/cron.d/daily-trials-scraping

# Run scraper once to bootstrap db then set up cron
CMD update_trials_store.py --max-id 100 && crond -f -l 8
