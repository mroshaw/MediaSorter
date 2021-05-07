"""Main Media Sorter module"""
import datetime
import logging
import argparse
from media_sorter import MediaSorter
from config import Config


def sort_photos(config_file, log_level_arg):
    """Main function to sort media"""
    # Start logging
    log_level = getattr(logging, log_level_arg.upper())
    log_file_name = datetime.datetime.now().strftime('media_sorter_%d_%m_%Y_%H_%M_%S.log')
    print(f"Logging to {log_file_name}")
    # noinspection PyArgumentList
    logging.basicConfig(filename=log_file_name, encoding='utf-8',
                        level=log_level, format='%(asctime)s %(''message)s')
    logger = logging.getLogger("media_sorter_log")
    logger.info("..............................................")
    logger.info("Welcome to Media Sorter!")
    logger.info("..............................................")
    logger.info(f"Log level {log_level_arg}...")
    logger.info(f"Loading config {config_file}...")

    # Init config
    config = Config(config_file)
    result, log_text = config.load()
    if not result:
        end_fail(log_text)
        return
    logger.info("Config loaded.")
    logging.debug(f"{config}")
    logger.info("..............................................")
    logger.info("Sorting media...")
    # Copy all from source to target, based on criteria
    media_sorter = MediaSorter(config)
    result, photo_file_count, video_file_count, folder_count = media_sorter.sort_media()
    if result:
        logger.info("Success!")
        logger.info(f"Processed {photo_file_count} photo files and {video_file_count} video files "
                    f"across {folder_count} folders")
    else:
        logger.info("Sorry, something went wrong!")
        logger.info(log_text)


def end_fail(error_description):
    """Handle failure"""
    logging.info(f"Sorry, a problem has occurred: {error_description}")


def get_args():
    """Parse command line arguments"""
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
