"""Manages loading, parsing and validation of configuration from file"""
import configparser
from configparser import NoSectionError, NoOptionError
import os
from distutils.util import strtobool


class Config:
    """Configuration file management class"""

    # pylint: disable=too-many-instance-attributes
    # This is a reasonable use of attributes
    def __init__(self, config_file):
        self.source_path = ""
        self.source_skip_files = ""
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
        self.config_file = config_file

    def load(self):
        """Load and validate the configuration from file"""

        try:
            # Parse the config file
            config = configparser.RawConfigParser()
            config.read(self.config_file)

            # Source and Target
            self.source_path = config.get("Source", "source_path")
            self.source_skip_files = config.get("Source", "skip_files").lower().split(",")
            self.photo_files = config.get("Source", "photo_files").lower().split(",")
            self.video_files = config.get("Source", "video_files").lower().split(",")
            self.target_photo_path = config.get("Target", "photo_path")
            self.target_video_path = config.get("Target", "video_path")

            # Options
            self.use_year = strtobool(val=config.get("Options", "use_year"))
            self.use_month = strtobool(val=config.get("Options", "use_month"))
            self.use_day = strtobool(val=config.get("Options", "use_day"))
            self.use_month_name = strtobool(val=config.get("Options", "use_month_name"))
            self.proceed_on_error = strtobool(val=config.get("Options", "proceed_on_error"))
            self.execute = strtobool(val=config.get("Options", "execute"))
            self.move_or_copy = config.get("Options", "move_or_copy").lower()

            # Validate config
            result, error_text = self.validate_config()

            return result, error_text
        except NoSectionError as no_section_exception:
            error_text = f"Could not open the config file\n" \
                         f"Error Description: {no_section_exception.message}."
            return False, error_text
        except NoOptionError as no_option_error:
            error_text = f"Configuration file is incorrect.\n" \
                         f"Error Description: {no_option_error.message}."
            return False, error_text

    def validate_config(self):
        """Validate the configuration content"""
        result = True
        error_text = ""

        # Check for source exists
        if not os.path.exists(self.source_path):
            error_text = f"Folder path does not exist. {self.source_path}"
            result = False
        return result, error_text
