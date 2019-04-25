

# Purpose: get all files ending with a given extension in a drive or folder

import os
# from hashlib import md5
# import datetime
import json
import codecs
# from filetypes import FileProperySet
from pprint import pprint
import logging
from s3_integration import pyfish_util as pfu
from settings import *
import pyfi_ui as pui


# MAIN FUNCTION
def main():
    # det defaults and properties
    sync_to_s3 = SYNC_TO_S3
    sync_to_another_drive = SYNC_TO_LOCAL
    load_external = LOAD_EXTERNAL
    json_file_path = JSON_FILE_PATH
    json_stats_path = JSON_STATS_PATH
    json_multi_summary_file = JSON_MULTI_SUMMARY_FILE
    flat_file_data_dir = FLAT_FILE_DATA_DIR
    # flat_file_suffix = "_filefish_out.log"
    target = None
    # get cli user input
    run_mode = pui.promt_user_for_run_mode()

    if run_mode == 3:
        sync_to_s3 = True
    if run_mode == 4:
        sync_to_another_drive = True
        target = pui.prompt_for_local_dest()
        # shouldn't scan the destination
        IGNORE_DIRS.append(target)
    elif run_mode == 5:
        volume_name = pui.prompt_for_volume()
        file_types = pui.get_file_types_from_user()
        target = pui.prompt_for_local_dest()
        pfu.only_sync_file(local_target=target, volume_name=volume_name, file_types=file_types)
        exit(0)
        



    elif run_mode >= 1:
        exit(0)

    volume_name = pui.prompt_for_volume()
    folder = pui.prompt_folder_to_scan()
    file_types = pui.get_file_types_from_user()
    file_list = {} if not load_external else pfu.load_pyfish_data()
    pfu.scan_for_files(file_list, folder=folder, file_types=file_types,
            volume_name=volume_name, sync_to_s3=sync_to_s3,
            sync_to_local_drive=sync_to_another_drive,
            load_external=LOAD_EXTERNAL, local_target=target)




    print(f"End Time: {str(pfu.datetime.datetime.now().time())}")
    print(f"All done.... See {flat_file_data_dir} folder for output files")
    print(f"All done.... See {json_file_path} folder\n"
            " for accumlated json data from all sources")

    stats = {}
    for key in file_list:
        stats[key] = stats.pop(key, None)
        if stats[key] is None:
            stats[key] = {}
        stats[key]['files'] = file_list[key]
        stats[key]['copies'] = len(file_list[key])
        stats[key]['md5'] = key


    # pprint(stats)

    """re-save the data to a file
    """

    with codecs.open(
            json_file_path, 'w+', encoding='utf-8'
            ) as json_out:
        json_out.write(
                json.dumps(file_list, sort_keys=True, ensure_ascii=False))

    """dump out the stats to a file
    """

    with codecs.open(
            json_stats_path, 'w+', encoding='utf-8'
            ) as json_out:
        json_out.write(
                json.dumps(stats, sort_keys=True, ensure_ascii=False))

    mulitple_files_collection = [
            stats[dups] for dups in stats if stats[dups]['copies'] > 1
        ]
    if mulitple_files_collection:
        with codecs.open(
                json_multi_summary_file, 'w+', encoding='utf-8'
                ) as json_out:
            json_out.write(
                    json.dumps(mulitple_files_collection, sort_keys=True, ensure_ascii=False))

if __name__ == '__main__':
    logger.info(f"{__name__} has started. Logging to {logger.name}")
    main()
