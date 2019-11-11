from abc import ABC, abstractmethod


class TrialsStoreInterfaceBase(ABC):
    @abstractmethod
    def store_trials_batch(self, trials_batch):
        raise NotImplementedError

    @abstractmethod
    def is_ready(self):
        """
        :return: Boolean indicating if store is ready to accept data
        """
        raise NotImplementedError
