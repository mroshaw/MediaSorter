import configparser
from configparser import NoSectionError, NoOptionError
import os


class Config:
    def __init__(self):
        self.source_path = ""
        self.target_photo_path = ""
        self.target_video_path = ""
        self.photo_files = ""
        self.video_files = ""
        self.use_year = False
        self.use_month = False
        self.use_day = False
        self.use_month_name = False
        self.proceed_on_error = False
        self.execute = False
        self.move_or_copy = ""

    def load(self):
        # Load and validate config

        result = True
        error_text = ""

        try:
            # Parse the config file
            config = configparser.RawConfigParser()
            config.read('config.ini')

            # Source and Target
            self.source_path = config.get("Source", "source_path")
            self.target_photo_path = config.get("Target", "photo_path")
            self.target_video_path = config.get("Target", "video_path")

            # Options
            if config.get("Options", "use_year").upper() == "Y":
                self.use_year = True
            else:
                self.use_year = False

            if config.get("Options", "use_month").upper() == "Y":
                self.use_month = True
            else:
                self.use_month = False

            if config.get("Options", "use_day").upper() == "Y":
                self.use_day = True
            else:
                self.use_day = False

            if config.get("Options", "use_month_name").upper() == "Y":
                self.use_month_name = True
            else:
                self.use_month_name = False

            if config.get("Options", "proceed_on_error").upper() == "Y":
                self.proceed_on_error = True
            else:
                self.proceed_on_error = False

            if config.get("Options", "execute").upper() == "Y":
                self.execute = True
            else:
                self.execute = False

            photo_files_text = config.get("Source", "photo_files").lower()
            self.photo_files = photo_files_text.split(",")

            video_files_text = config.get("Source", "video_files").lower()
            self.video_files = video_files_text.split(",")

            self.move_or_copy = config.get("Options", "move_or_copy").lower()

            # Validate config
            result, error_text = self.validate_config()

            return result, error_text
        except NoSectionError as no_section_exception:
            error_text = f"Could not open the config file\nError Description: {no_section_exception.message}."
            return False, error_text
        except NoOptionError as no_option_error:
            error_text = f"Configuration file is incorrect.\nError Description: {no_option_error.message}."
            return False, error_text

    def validate_config(self):
        result = True
        error_text = ""

        # Check for source exists
        if not os.path.exists(self.source_path):
            error_text = f"Folder path does not exist. {self.source_path}"

        return result, error_text
