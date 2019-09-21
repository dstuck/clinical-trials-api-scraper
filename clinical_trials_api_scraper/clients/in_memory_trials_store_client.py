import logging

from clinical_trials_api_scraper.clients.trials_store_interface_base import \
    TrialsStoreInterfaceBase

logger = logging.getLogger(__name__)


class InMemoryTrialsStoreClient(TrialsStoreInterfaceBase):
    def __init__(self):
        self.store = []

    def store_trials_batch(self, trials_batch):
        logger.debug('storing {} values'.format(len(trials_batch)))
        self.store.extend(trials_batch)
