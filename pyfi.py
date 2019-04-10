

# Purpose: get all files ending with a given extension in a drive or folder

import os
from hashlib import md5
import datetime
import json
import codecs
from filetypes import FileProperySet
from pprint import pprint
import logging
from s3_integration import pyfish_util as pfu

JSON_FILE_PATH='logs/json_data.json'
JSON_STATS_PATH='logs/json_stats.json'

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig( filename='./logs/app_log.txt', level=logging.DEBUG,
        format=LOG_FORMAT)
logger = logging.getLogger()




def select_volume_from_list(previous_volumes:list):
    """present a list of volumes to choose from and over to enter a new one
    
    Arguments:
        previous_volumes {list} -- a list of volume names found in the saved 
        data
    
    Returns:
        str -- either a new volume name, or one from the list
    """

    select_list = [ (key, previous_volumes[key-1]) for key in range(1,len(previous_volumes)+1) ]
    result = ''
    confirm = 'n'
    new_volume_prompt = "HINT: Names should be unique, and help you know where the volume is.\n"
    new_volume_prompt += "i.e: 'Macbook Lucy/ HD01'\n"
    new_volume_prompt += "Please enter a new name, but it should not match an existing name: "
    # we'll loop the prompt until the user is sure of their selection
    while confirm[0].lower() != 'y':
        if previous_volumes:
            print("You can choose a volume/location found in the saved data\n")
            for key,volume in select_list:
                print(f"press '{key}' for '{volume}'")
            print(f"Enter '0' to type in a new name for a new volume\n")

        entry = input("Type the name of the computer volume and press 'Enter': ")
        try:
            entry = int(entry)
        except:
            if not entry:
                entry = 0
        entry = str(input(new_volume_prompt)) if str(entry) == '0' else entry
        prompt_entry = entry if type(entry) is str else previous_volumes[entry-1]
        confirm = input(f"\nYou entered '{prompt_entry}'. Is that correct? (yes,no,cancel): ") if entry else 'n'
        confirm = 'y' if confirm == '' else confirm
        if confirm[0].lower() == 'c':
            print("You have canceled. Existing")
            exit()
        # get the text name if a previous volume slected.
        if type(entry) == int:
            result = previous_volumes[entry-1]
        else:
            result = entry
            if result in previous_volumes:
                print("SORRY, you can't use a name that's been used already\n")
                confirm = 'n'
                result = ''
        # reset confirm if blank
        if not confirm:
            confirm = 'n'

    # return the volume name to use
    return str(result)
    

# Functions to move to another module or class
def get_file_types_from_user():
    """prompt user for file types and return a list
    """
    # fileTypeList = ['png', 'jpeg', 'mp4', 'bmp', 'wav', 'jpg', ]
    filePropList = FileProperySet()
    file_type_input = ""
    while True:
        if file_type_input == 'new':
            # fileTypeList = []
            filePropList.clear()
        # fileTypeList.append(file_type_input)
        prompt_text = "Please input file types to search for, but don't " + \
            "add the period.\n  Or just press enter or type 'done' if satisfied with...\n" + \
            ', '.join([ prop.extension for prop in filePropList.ft_list]) + "\n: "
        prompt_text += "Or type 'new' to clear the list and start over\n"
        file_type_input = input(prompt_text)
        if file_type_input in ['done', '']:
            break
        if file_type_input != 'new':
            print("Please enter a mininimum size in bytes."
                    "(smaller files will be ignored.)")
            min_size = input("mininmum size: ")
            filePropList.add(filePropList.file_properties(file_type_input, min_size))

    # return fileTypeList
    return filePropList


#
def modification_date(filename):
    time_of_mod = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(time_of_mod)


# for getting the hex version of md5
def get_md5(fileObjectToHash, block_size=(2048*20)):
    file_hash = md5()
    while True:
        data = fileObjectToHash.read(block_size)
        if not data:
            break
        file_hash.update(data)
    # hex digest is better than digest, for standart use.
    return file_hash.hexdigest()

def load_saved_file_list(json_file_path):
    """
    loads the json file that has previously found files
    """
    external_file_list = {}
    try:
        with open(json_file_path, 'r') as json_data:
            external_file_list = json.load(json_data)
            logger.info(f"found the json file and loaded saved data from {json_file_path}")
    except FileNotFoundError as e:
        print(f"Warning: {e.strerror}")
        print(f"warning: Missing {json_file_path}")
        print("Info: This is normal, if this is a first run of the program.")
        logger.info(f"{json_file_path} was not found. A new file will be created")
    return external_file_list

def promt_user_for_run_mode():
    """sub routine to report on previous data
    """

    prompt = "Would you like to see finding on previous data. Choose 0 for 'no' to just run the scanner?"
    print(
        """
        1) see unique file size totals. This roughly show the amount of disk space required to store all the files in the data
        2) see the volumes currentinly captured in the data
        3) Scan and find files, as well as sync to AWS S3 bucket.
            (Note: you must already have your cli and bucket configured for this to work)
        0) Scan and find files for data, but do not sync to another location
        """)
    try:
        choice = int(input(prompt))
    except Exception as e:
        print(f"'not a valid choice': {e}")
        choice = 0

    if choice:
        if choice == 1:
            print(pfu.get_unique_files_totalsize())
        elif choice == 2:
            print(pfu.get_current_volumes())
        elif choice > 3:
            choice = 0
        return choice
    else:
        return choice
    



    



# MAIN FUNCTION
def main():

    sync_to_s3 = False
    sync_to_another_drive = False
    run_mode = promt_user_for_run_mode()
    
    if run_mode == 3:
        sync_to_s3 == True
    elif run_mode >= 1:
        exit()

    # Set properties
    previous_volumes = [ vol for vol in pfu.get_current_volumes() ]
    volume = select_volume_from_list(previous_volumes)
    volume_name = input(
        "Name the volume you're searching" +
        "(something distinct from other volumes): ") if not volume else volume
    data_dir = "logs"
    outfile_suffix = "_filefish_out.log"
    load_external=True
    json_file_path='logs/json_data.json'
    json_stats_path='logs/json_stats.json'
    json_multi_summary_file = 'logs/json_multi.json'

    # ignore directories
    ignore = ['Volumes', '.Trash', '.MobileBackups', 'atest', 'Applications',
              '.git',
              '.gitignore',
              '.docker',
              '.local',
              '.config',
              '.dropbox',
              #   'Dropbox',
              'Downloads',
              'Windows',
              'drivers',
              'Program Files',
              'Program Files(x86)',
              'lib',
              'bin',
              'snap',
              'lost+found',
              'root',
              'sbin',
              'run',
              'sys',
              'tmp',
              'lib64',
              'proc',
              'dev',
              'local_dev',
              'dotfiles',
              ]

    if os.name == 'nt':
        folder = input("Enter the drive letter you'd like to search: ")

        if folder == '':
            folder = "C:\\"
        else:
            folder = folder + ":\\"

    elif os.name == 'posix':
        print('OS is Mac/Linux')
        folder = input("Enter the file path (Default is './test/': ")
        if folder == '':
            folder = "./test/"

    else:  # quit if not NT OR POSIX
        exit()

    print (f"All files ending with .txt in folder {folder}:")
    file_list = {} if not load_external else load_saved_file_list(json_file_path)
    file_types = get_file_types_from_user()
    print(f"Start Time: {str(datetime.datetime.now().time())}")
    for (paths, dirs, files) in os.walk(folder, topdown=True):
        for ignore_dir in ignore:
            if ignore_dir in dirs:
                dirs.remove(ignore_dir)

        dirs[:] = [d for d in dirs if d not in ignore]
        # Testing section end...
        for file_to_check in files:
            # TODO: change this to check first if the file is the right size,
            #       do the checks.  Also use a "fancy" tuple with named values
            #       to store the min size per type instead of a global type
            for file_type in file_types.ft_list:
                temp_outfile = file_type.extension + outfile_suffix
                temp_outfile = os.path.join(data_dir, temp_outfile)
                if not os.path.exists(temp_outfile):
                    startFile = open(temp_outfile, 'w+')
                    startFile.write(
                            "Filename\t"
                            "Hash\t"
                            "FileSize\t"
                            "Date\t"
                            "FileType\t"
                            "VolumeName\n")
                    startFile.close()
                if (file_to_check.lower()).endswith(file_type.extension):
                    filename = os.path.join(paths, file_to_check)
                    with open(filename, 'rb') as file_to_hash:
                        file_hash = get_md5(file_to_hash)
                        file_stat = os.stat(filename)
                        timestamp = str(modification_date(filename))
                        file_size = str(file_stat.st_size/(1024*1024.0))
                        full_path = os.path.realpath(file_to_hash.name)
                        path_tags = [tag for tag in filter(None,full_path.split("/"))]
                        if float(file_type.min_size/(1024*1024.0)) < int(float(file_size)):
                            if file_hash not in file_list.keys():
                                file_list[file_hash] = []
                            file_ref = file_list[file_hash]
                            # filter if the same tags are found on same volume.
                            # indicating same file
                            existing =  [  (i['tags'],i['volume']) for i in file_ref ]
                            matches = [ tags for tags, volume in existing if path_tags == tags and volume_name == volume ]
                            if not matches:
                            # if file_list[file_hash]['tags'] != path_tags and file_list[file_hash]['volume'] == volume_name:
                                file_ref.append({
                                        'tags': path_tags,
                                        'filename': str(path_tags[-1]),
                                        'md5hash': file_hash,
                                        'full_path': full_path,
                                        'volume': volume_name,
                                        'file_size': file_size,
                                        'timestamp': timestamp,
                                        })
                            if sync_to_s3:
                                # sync to s3 if option was selected.
                                # use the file just added, since it's likely accessible
                                pfu.sync_file_to_s3(file_ref[-1]) 
                            if sync_to_another_drive:
                                # TODO
                                # 
                                # 
                                # Add a sync to another drive here
                                #
                                pass
                            # if file_stat.st_size > min_file_size:
                            with open(temp_outfile, 'a+') as out_put_file:
                                out_put_file.writelines(
                                    "{}\t{}\t{}\t{}\t{}\t{}\t{}\t\n".format(
                                        str(path_tags[-1]),
                                        filename,
                                        file_hash,
                                        file_size,
                                        timestamp,
                                        file_type,
                                        volume_name,

                                            )
                            )

    # debug
    # print([
    #     """\nhash: {}
    #     count: {}
    #     fileslist:
    #     __________
    #     {}""".format(i, len(file_list[i]), file_list[i]) for i in file_list])
    print(f"End Time: {str(datetime.datetime.now().time())}")
    print(f"All done.... See {data_dir} folder for output files")
    print(f"All done.... See {json_file_path} folder"
            "accumlated json from all sources")
    
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
