"""Main MediaSorter class"""
import os
import shutil
import datetime
import calendar
from os import path
import logging


class MediaSorter:
    """Main MediaSorter class"""
    def __init__(self, config):
        self.config = config
        self.photo_file_count = 0
        self.video_file_count = 0
        self.folder_count = 0
        self.logger = logging.getLogger("media_sorter_log")

    def create_folder(self, folder_path):
        """Create an empty folder, if one doesn't exist"""
        try:
            if not path.exists(folder_path):
                if self.config.execute:
                    os.mkdir(folder_path)
                self.logger.debug(f"Created: {folder_path}")
            else:
                self.logger.debug(f"Exists. Skipping: {folder_path}")
            return True
        except OSError as exception:
            self.logger.debug(f"Sorry, there was a problem creating the target folder. {exception.strerror}")
            return False

    def skip_file(self, folder_item):
        """Decide whether or not to skip a file"""
        source_file_size = folder_item.stat().st_size
        filename, source_file_extension = os.path.splitext(folder_item.path)
        if source_file_size <= 0:
            skip = True
            skip_reason = "Zero file size"
        elif any(skip_text in folder_item.name for skip_text in self.config.source_skip_files):
            skip = True
            skip_reason = f"File matches pattern in skip_files: {self.config.source_skip_files}"
        elif not (source_file_extension in self.config.photo_files) and not (
                source_file_extension in self.config.video_files):
            skip = True
            skip_reason = f"File extension not in photo_files: {self.config.photo_files}" \
                          f" or video_files: {self.config.video_files}"
        else:
            skip = False
            skip_reason = None

        return skip, skip_reason

    def sort_media(self):
        """Main control function to orchestrate sorting"""
        result = self.process_folder(folder_path=self.config.source_path)
        return result, self.photo_file_count, self.video_file_count, self.folder_count

    def process_file(self, folder_item):
        """Process a specific file into destination"""
        source_file_name = folder_item.name
        source_file_path = folder_item.path
        file_name, source_file_extension = os.path.splitext(source_file_path)
        self.logger.debug(f"Found file: {source_file_path}")

        # Do we need to skip the file?
        skip, skip_reason = self.skip_file(folder_item)
        if skip:
            self.logger.debug(f"Skipping: {file_name}. Reason: {skip_reason}")
            return

        # What to do with the file?
        if source_file_extension in self.config.photo_files:
            # Photo file
            target_path = self.config.target_photo_path
            file_type = "photo"
        elif source_file_extension in self.config.video_files:
            # Video file
            target_path = self.config.target_video_path
            file_type = "video"
        else:
            # Something horrible has happened here
            self.logger.debug(f"Something has gone wrong processing: {file_name}. Reason: Can't determine file type")
            return

        created_date = datetime.datetime.fromtimestamp(folder_item.stat().st_ctime)
        self.logger.debug(f"Created date of file is: {created_date}")

        # Create or check target folders
        base_folder = self.create_base_folder(target_path=target_path, date=created_date)

        # Move or copy file
        target_file_name_path = f"{base_folder}\\{source_file_name}"
        self.move_or_copy_file(source_path=source_file_path, target_path=target_file_name_path,
                               file_type=file_type)

    def move_or_copy_file(self, source_path, target_path, file_type):
        """Move or copy the file"""
        # Check if target file exists
        if os.path.exists(target_path):
            self.logger.debug(f"Skipping {source_path}: File already exists")
            return
        if file_type == "photo":
            self.photo_file_count = self.photo_file_count + 1
        if file_type == "video":
            self.video_file_count = self.video_file_count + 1
        if self.config.execute:
            if self.config.move_or_copy == "move":
                self.logger.info(f"Moving: {source_path} to "
                                 f"{target_path}")
                os.rename(source_path, target_path)
            else:
                self.logger.info(f"Copying: {source_path} to "
                                 f"{target_path}")
                shutil.copy2(source_path, target_path)

    def create_base_folder(self, target_path, date):
        # day_text = str(created_date.day)
        month = date.month
        year_text = str(date.year)
        self.logger.debug(f"Creating / checking base year folder: {year_text}")
        year_folder = f"{target_path}\\{year_text}"
        self.create_folder(year_folder)

        if self.config.use_month:
            if self.config.use_month_name:
                month_text = calendar.month_name[month]
            else:
                month_text = str(month)

            # Create or check folder
            self.logger.debug(f"Creating / checking base month folder: {month_text}")
            month_folder = f"{target_path}\\{year_text}\\{month_text}"
            self.create_folder(folder_path=month_folder)
            return month_folder
        else:
            return year_folder

    def process_folder(self, folder_path):
        """Parse the specified folder"""
        result = True

        for folder_item in os.scandir(folder_path):
            # Process files
            # print(folder_item)
            if folder_item.is_file():
                self.process_file(folder_item)
            # If folder, then iterate
            if folder_item.is_dir():
                # Iterate
                self.logger.debug(f"Found dir: {folder_item.name}")
                self.folder_count = self.folder_count + 1
                result = self.process_folder(folder_item.path)

        return result
