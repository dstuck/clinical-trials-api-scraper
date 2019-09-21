from abc import ABC, abstractmethod


class TrialsStoreInterfaceBase(ABC):
    @abstractmethod
    def store_trials_batch(self, trials_batch):
        raise NotImplementedError
