import logging
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.ext.automap import automap_base


from clinical_trials_api_scraper.clients.trials_store_interface_base import \
    TrialsStoreInterfaceBase
import clinical_trials_api_scraper.utils.trial_model_utils as tmu


DB_SCHEMA = "trials_status_schema"

logger = logging.getLogger(__name__)

# Base = declarative_base(cls=DeferredReflection,
#                         metadata=MetaData(schema=DB_SCHEMA))
Base = automap_base(metadata=MetaData(schema=DB_SCHEMA))


class Institution(Base):
    __tablename__ = 'institutions'


class Trial(Base):
    __tablename__ = 'trials'


class SqlTrialsStoreClient(TrialsStoreInterfaceBase):
    db_name = "clinical_trials_status"

    def __init__(self):
        self.engine = create_engine(
            'postgres://postgres:1234@db:5432/{}'.format(self.db_name), echo=False)
        Base.prepare(self.engine, reflect=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(Trial.__table__.columns)
        logger.info(Institution.__table__.columns)

    def store_trials_batch(self, trials_batch):
        logger.info('storing {} values'.format(len(trials_batch)))
        trials = [tmu.trial_from_response_data(t) for t in trials_batch]
        #institution_dict = {}
        for full_trial in trials:
            institution, trial = tmu.split_institution_trial(full_trial)
            inst_obj = Institution(
                **tmu.dict_to_snake_case(institution))
            #institution_key = (inst_obj.org_name, inst_obj.org_type)

            # deduplicate institutions
            #inst_obj = institution_dict.setdefault(institution_key, inst_obj)

            trial['institution'] = inst_obj
            trial_obj = Trial(**tmu.dict_to_snake_case(trial))
            self.session.merge(trial_obj)
            logger.info(
                f'storing trial {trial_obj.id} from {inst_obj.org_name}')
        self.session.commit()

    def is_ready(self):
        return True
