import s3_integration
from pyfi_util import pyfish_util as pfu
import pytest
from pyfi_ui import pyfi_cli as pui
from dotenv import load_dotenv
from os import getenv
from collections import namedtuple


ACTIVE_BUCKET_NAME='backups.beaukinstler.com' ## TODO: create a test bucket and change this
PYFI_S3_SALT='test'
PYFI_S3_ENCRYPTION_KEY='T3stK3yF04Fun'


@pytest.fixture()
def file_list():
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()
    result = pfu._load_saved_file_list('tests/test_json_data.json')
    return result

@pytest.fixture()
def file_list_only_one_volume():
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()
    result = pfu._load_saved_file_list('tests/test_json_data_one_vol.json')
    return result

@pytest.fixture()
def test_env():
    EnvBuilder = namedtuple("env", ['ACTIVE_BUCKET_NAME','PYFI_S3_SALT','PYFI_S3_ENCRYPTION_KEY' ])
    env = EnvBuilder._make([ACTIVE_BUCKET_NAME,PYFI_S3_SALT,PYFI_S3_ENCRYPTION_KEY])

    return env
    
