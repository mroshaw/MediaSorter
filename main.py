import os
import shutil
import datetime
import calendar
from os import path
from config import Config
import logging
import argparse


def sort_photos(config_file, log_level_arg):
    # Start logging
    log_level = getattr(logging, log_level_arg.upper())
    log_file_name = datetime.datetime.now().strftime('media_sorter_%d_%m_%Y_%H_%M_%S.log')
    print(f"Logging to {log_file_name}")
    # noinspection PyArgumentList
    logging.basicConfig(filename=log_file_name, encoding='utf-8', level=log_level, format='%(asctime)s %('
                                                                                             'message)s')
    logging.info(f"..............................................")
    logging.info(f"Welcome to Media Sorter!")
    logging.info(f"..............................................")
    logging.info(f"Log level {log_level_arg}...")
    logging.info(f"Loading config {config_file}...")

    # Init config
    config = Config(config_file)
    result, log_text = config.load()
    if not result:
        end_fail(log_text)
        return
    logging.info(f"Config loaded.")
    logging.info(f"Sorting media...")
    # Copy all from source to target, based on criteria
    result, log_text, photo_file_count, video_file_count, folder_count = move_files(config.source_path, config, 0, 0, 0)
    if result:
        logging.info(f"Success!")
        logging.info(f"Processed {photo_file_count} photo files and {video_file_count} video files "
                     f"across {folder_count} folders")
    else:
        logging.info(f"Sorry, something went wrong!")
        logging.info(log_text)


def move_files(source_path, config, photo_file_count, video_file_count, folder_count):
    result = True
    log_text = ""

    photo_files = config.photo_files
    video_files = config.video_files
    skip_files = config.source_skip_files

    for folder_item in os.scandir(source_path):
        # Process files
        # print(folder_item)
        if folder_item.is_file():
            source_file_name = folder_item.name
            source_file_path = folder_item.path
            filename, source_file_extension = os.path.splitext(source_file_path)
            logging.debug(f"Found file: {source_file_path}")

            # Get file size
            source_file_size = folder_item.stat().st_size
            file_type = ""
            # Work out what to do with the files
            if source_file_size <= 0:
                target_path = None
            elif skip_file(filename, skip_files):
                target_path = None
            elif source_file_extension in photo_files:
                target_path = config.target_photo_path
                file_type = "photo"
            elif source_file_extension in video_files:
                target_path = config.target_video_path
                file_type = "video"
            else:
                target_path = None

            if target_path is not None:

                created_date = datetime.datetime.fromtimestamp(folder_item.stat().st_ctime)
                logging.debug(f"Created date of file is: {created_date}")

                # day_text = str(created_date.day)
                month = created_date.month
                year_text = str(created_date.year)

                logging.debug(f"Creating / checking base year folder: {year_text}")
                base_folder = f"{target_path}\\{year_text}"
                result, log_text = create_folder(base_folder, config.execute)

                if config.use_month:
                    if config.use_month_name:
                        month_text = calendar.month_name[month]
                    else:
                        month_text = str(month)

                    # Create or check folder
                    logging.debug(f"Creating / checking base month folder: {month_text}")
                    base_folder = f"{target_path}\\{year_text}\\{month_text}"
                    result, log_text = create_folder(base_folder, config.execute)

                # Move file
                target_file_name_path = f"{base_folder}\\{source_file_name}"
                # Check if target file exists
                if os.path.exists(target_file_name_path):
                    logging.debug(f"Skipping {source_file_path}: File already exists")
                else:
                    if source_file_path != target_file_name_path:
                        if file_type == "photo":
                            photo_file_count = photo_file_count + 1
                        elif file_type == "video":
                            video_file_count = video_file_count + 1
                        if config.execute:
                            logging.info(f"Moving: {source_file_path} to {target_file_name_path}")
                            if config.move_or_copy == "move":
                                os.rename(source_file_path, target_file_name_path)
                            else:
                                shutil.copy2(source_file_path, target_file_name_path)
            else:
                logging.debug(f"Skipping {source_file_path}: Not a valid file")

        # If folder, then iterate
        if folder_item.is_dir():
            logging.debug(f"Found dir: {folder_item.name}")
            folder_count = folder_count + 1
            result, log_text, photo_file_count, video_file_count, folder_count = move_files(folder_item.path, config,
                                                                                            photo_file_count,
                                                                                            video_file_count,
                                                                                            folder_count)

        result = True
        log_text = "Success"

    return result, log_text, photo_file_count, video_file_count, folder_count


def create_folder(folder_path, execute):
    try:
        if not path.exists(folder_path):
            if execute:
                os.mkdir(folder_path)
            log_text = f"Created: {folder_path}"
        else:
            log_text = f"Exists. Skipping: {folder_path}"
        return True, log_text
    except OSError as exception:
        log_text = "Sorry, there was a problem creating the target folder"
        return False, log_text


def end_fail(error_description):
    logging.info(f"Sorry, a problem has occurred: {error_description}")


def skip_file(file_name, files_to_skip):
    if any(skip_text in file_name for skip_text in files_to_skip):
        return True
    else:
        return False


def get_args():
    parser = argparse.ArgumentParser(description='Sunrose Media Sorter')
    parser.add_argument('--config', dest='config_file', type=str,
                        help='path to the configuration file')
    parser.add_argument('--loglevel', dest='log_level', type=str,
                        help='level of logging required')

    return parser.parse_args()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = get_args()
    sort_photos(config_file=args.config_file, log_level_arg=args.log_level)
