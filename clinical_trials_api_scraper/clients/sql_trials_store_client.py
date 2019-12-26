import logging
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection


from clinical_trials_api_scraper.clients.trials_store_interface_base import \
    TrialsStoreInterfaceBase
from clinical_trials_api_scraper.utils.trial_model_utils import trial_from_response_data, dict_to_snake_case, extract_institution_from_trial


DB_SCHEMA = "trials_status_schema"

logger = logging.getLogger(__name__)

Base = declarative_base(cls=DeferredReflection,
                        metadata=MetaData(schema=DB_SCHEMA))


class Institution(Base):
    __tablename__ = 'institutions'


class Trial(Base):
    __tablename__ = 'trials'


class SqlTrialsStoreClient(TrialsStoreInterfaceBase):
    db_name = "clinical_trials_status"

    def __init__(self):
        self.engine = create_engine(
            'postgres://postgres:1234@db:5432/{}'.format(self.db_name), echo=False)
        Base.prepare(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(Trial.__table__.columns)
        logger.info(Institution.__table__.columns)

    def store_trials_batch(self, trials_batch):
        logger.info('storing {} values'.format(len(trials_batch)))
        trials = [trial_from_response_data(t) for t in trials_batch]
        institutions = [dict_to_snake_case(
            extract_institution_from_trial(t)) for t in trials]
        for institution in institutions[:5]:
            logger.info(institution)
            self.session.add(Institution(**institution))
        for trial in trials[:5]:
            logger.info(trial)
            self.session.add(Trial(**dict_to_snake_case(trial)))
        self.session.commit()

    def is_ready(self):
        return True
