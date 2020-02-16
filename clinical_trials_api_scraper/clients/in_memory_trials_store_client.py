import logging

from clinical_trials_api_scraper.clients.trials_store_interface_base import \
    TrialsStoreInterfaceBase
import clinical_trials_api_scraper.utils.trial_model_utils as tmu

logger = logging.getLogger(__name__)


class InMemoryTrialsStoreClient(TrialsStoreInterfaceBase):
    def __init__(self):
        self.store = []

    def store_trials_batch(self, trials_batch):
        logger.info("storing {} values".format(len(trials_batch)))
        trials = [tmu.trial_from_response_data(t) for t in trials_batch]
        trials = [tmu.add_computed_fields(t) for t in trials]
        for full_trial in trials:
            organization, trial = tmu.split_organization_trial(full_trial)

            trial["organization"] = organization
            self.store.append(trial)
        logger.info("Batch stored.")

    def is_ready(self):
        return True
