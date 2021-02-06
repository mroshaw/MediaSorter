import os
import shutil
import datetime
import calendar
from os import path
from config import Config


def sort_photos():

    # Init config
    config = Config()
    result, log_text = config.load()
    if not result:
        end_fail(log_text)
        return

    # Copy all from source to target, based on criteria
    result, log_text, photo_file_count, video_file_count, folder_count = move_files(config.source_path, config, 0, 0, 0)
    if result:
        print(f"Success!")
        print(f"Processed {photo_file_count} photo files and {video_file_count} video files "
              f"across {folder_count} folders")
    else:
        print(f"Sorry, something went wrong!")
        print(log_text)


def move_files(source_path, config, photo_file_count, video_file_count, folder_count):

    result = True
    log_text = ""

    photo_files = config.photo_files
    video_files = config.video_files

    for folder_item in os.scandir(source_path):
        # Process files
        # print(folder_item)
        if folder_item.is_file():
            source_file_name = folder_item.name
            source_file_path = folder_item.path
            filename, source_file_extension = os.path.splitext(source_file_path)
            print(f"Found file: {source_file_path}")

            # Get file size
            source_file_size = folder_item.stat().st_size

            # Work out what to do with the files
            if source_file_size <= 0:
                target_path = None
            elif source_file_extension in photo_files:
                target_path = config.target_photo_path
                photo_file_count = photo_file_count + 1
            elif source_file_extension in video_files:
                target_path = config.target_video_path
                video_file_count = video_file_count + 1
            else:
                target_path = None

            if target_path is not None:

                created_date = datetime.datetime.fromtimestamp(folder_item.stat().st_ctime)
                print(f"Created: {created_date}")

                # day_text = str(created_date.day)
                month = created_date.month
                year_text = str(created_date.year)

                print(f"Creating / checking base year folder: {year_text}")
                base_folder = f"{target_path}\\{year_text}"
                result, log_text = create_folder(base_folder, config.execute)

                if config.use_month:
                    if config.use_month_name:
                        month_text = calendar.month_name[month]
                    else:
                        month_text = str(month)

                    # Create or check folder
                    print(f"Creating / checking base month folder: {month_text}")
                    base_folder = f"{target_path}\\{year_text}\\{month_text}"
                    result, log_text = create_folder(base_folder, config.execute)

                # Move file
                target_file_name_path = f"{base_folder}\\{source_file_name}"
                print(f"Moving: {source_file_path} to {target_file_name_path}")
                if source_file_path != target_file_name_path:
                    if config.execute:
                        if config.move_or_copy == "move":
                            os.rename(source_file_path, target_file_name_path)
                        else:
                            shutil.copy2(source_file_path, target_file_name_path)
            else:
                print(f"Skipping {source_file_path}: Not a valid file")

        # If folder, then iterate
        if folder_item.is_dir():
            print(f"Found dir: {folder_item.name}")
            folder_count = folder_count + 1
            result, log_text, photo_file_count, video_file_count, folder_count = move_files(folder_item.path, config, photo_file_count, video_file_count, folder_count)

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
    print(f"Sorry, a problem has occurred.\n{error_description}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sort_photos()

