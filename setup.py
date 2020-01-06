from setuptools import find_packages, setup

setup(
    name="clinical_trials_api_scraper",
    version="0.1.0",
    author="David Stuck",
    packages=find_packages(),
    scripts=["clinical_trials_api_scraper/scripts/update_trials_store.py"],
    url="https://github.com/dstuck/clinical-trials-api-scraper",
    description="Scraper to pull trial reporting data from clinicaltrials.gov.",
    # long_description=open('README.md').read(),
    # Not using install_requires: it can't be cached effectively
    # install_requires=[
    #     "requests",
    #     "python-dateutil",
    #     "sqlalchemy",
    #     "psycopg2-binary"
    # ],
)
