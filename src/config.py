import os

PETITION_API_ROOT = 'https://petitions.whitehouse.gov/api/v1'
PETITION_SLEEP    = .125
PETITION_DATA_DIR = '../data/petitions'

NPR_SLEEP         = .333

ROOT_DATA_DIR = '/home/data/justin_files/whitehouse_hackathon'
NPR_DATA_DIR = os.path.join(ROOT_DATA_DIR, 'articles')

PETITION_DATA_DUMP = 'https://api.whitehouse.gov/v1/downloads/data.sql.zip'

try:
    import extra_config
    NPR_API_KEY = extra_config.NPR_API_KEY
    PETITION_API_KEY = extra_config.PETITION_API_KEY
except:
    assert False, 'Read the README.txt file for setting up API keys.'
