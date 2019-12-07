#!/usr/local/bin/python
import logging
import sys

from clinical_trials_api_scraper.clients.in_memory_trials_store_client import \
    InMemoryTrialsStoreClient
from clinical_trials_api_scraper.clients.gql_trials_store_client import GqlTrialsStoreClient
from clinical_trials_api_scraper.scrapers.clinical_trials_scraper import ClinicalTrialsScraper


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def main(min_id=None, max_id=None, in_memory=False, host="localhost", port=5000):
    if in_memory:
        store = InMemoryTrialsStoreClient()
    else:
        store = GqlTrialsStoreClient(host, port)
    if not store.is_ready():
        raise ValueError("Store not ready for data")
    scraper = ClinicalTrialsScraper(
        data_store_client=store, min_id=min_id, max_id=max_id)
    scraper.scrape_all_trials()
    logger.info("Completed scraping trials")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--min-id", type=int, required=False)
    parser.add_argument("--max-id", type=int, required=False)
    parser.add_argument("--in-memory", action='store_true')
    parser.add_argument("--host")
    parser.add_argument("--port")
    args = parser.parse_args()

    logger.info(args)

    main(
        min_id=args.min_id,
        max_id=args.max_id,
        in_memory=args.in_memory,
        host=args.host,
        port=args.port
    )
