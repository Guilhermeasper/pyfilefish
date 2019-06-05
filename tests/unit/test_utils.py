import pytest
from pyfi_util import pyfish_util as pfu
from pyfi_filestore.pyfish_file import PyfishFile

@pytest.mark.utils
def test_build_relative_destination_path(pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    first_item = pyfish_file_set.list[first_key][0]
    path, ft, md5hash = pfu.build_relative_destination_path(first_item)
    testpath = f"{first_item.filetype}/{first_item.md5hash}/"
    assert (path, ft, md5hash) == (testpath, first_item.filetype, first_item.md5hash)


@pytest.mark.utils
def test_build_relative_destination_path_remote(pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    first_item = pyfish_file_set.list[first_key][0]
    path, ft, remote_name_hash = pfu.build_relative_destination_path_remote(first_item)
    testpath = f"{first_item.filetype}/{first_item.remote_name_hash}/"
    assert (path, ft, remote_name_hash) == (testpath, first_item.filetype, first_item.remote_name_hash)


@pytest.mark.utils_dev
def test_sync_s3_new(pyfishfile:PyfishFile):
    pyfishfile.open_and_get_info()
    pyfishfile.encrypt_remote = True
    pfu.sync_file_to_s3_new(pyfishfile)

@pytest.mark.utils_dev
def test_sync_s3_new_no_encrypt(pyfishfile:PyfishFile):
    pyfishfile.open_and_get_info()
    pyfishfile.encrypt_remote = False
    pfu.sync_file_to_s3_new(pyfishfile)


@pytest.mark.gzip
def test_gzip(pyfishfile:PyfishFile):
    pyfishfile.open_and_get_info()
    fl = pyfishfile.full_path
    before:bytes = None
    after:bytes = None
    with open(fl, 'rb') as data:
        before = data.read()
    
    with open(fl, 'rb') as data:
        import gzip
        after = gzip.compress(data.read())

    assert before.__sizeof__()/1024/1024.0 > after.__sizeof__()/1024/1024.0

@pytest.mark.utils
def test_add_files_to_manifest():
    test_manifest_encrypted = 'test.manifest.json.encrypted'
    test_manifest_decrypted = 'test.manifest.json'
    pfu.add_location_to_file_manifest(test_manifest_decrypted,'test',["made/up/path"])