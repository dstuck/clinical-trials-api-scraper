from clinical_trials_api_scraper.clients.clinical_trials_rest_client import ClinicalTrialsRestClient

class ClinicalTrialsScraper(object):
    def __init__(self, data_store_client, min_id=1, max_id=None):
        """

        :param data_store_client: TrialsStoreInterfaceBase
        :param min_id: Min id if you don't want to pull all studies
        :param max_id: Max id (inclusive) if you don't want to pull all studies
        """
        self.data_store_client = data_store_client
        self.min_id = min_id
        self.max_id = max_id or ClinicalTrialsRestClient.get_max_study_id()

    def scrape_all_trials(self):
        max_requestable_records = ClinicalTrialsRestClient.MAX_REQUESTABLE_RECORDS
        batch_endpoints = list(range(1, self.max_id, max_requestable_records))
        batch_endpoints.append(self.max_id + 1)
        # We could always distribute this if it becomes the bottleneck
        for start_id, end_id_exclusive in zip(batch_endpoints[:-1], batch_endpoints[1:]):
            end_id = end_id_exclusive-1
            self._request_and_store_batch(start_id, end_id)

    def _request_and_store_batch(self, start_id, end_id):
        trials_batch = ClinicalTrialsRestClient.request_trials(
            start_id=start_id,
            end_id=end_id,
        )
        self._store_batch_data(trials_batch)

    def _store_batch_data(self, batch_data):
        self.data_store_client.store_trials_batch(batch_data)
