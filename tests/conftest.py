import s3_integration
from s3_integration import pyfish_util as pfu
import pytest


@pytest.fixture()
def file_list():
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()
    result = pfu._load_saved_file_list('tests/test_json_data.json')
    return result
