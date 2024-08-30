from datetime import datetime
import logging
import shutil
import os
import re

from multiversion_backup.log import Log
from multiversion_backup.path_constants import ROOT_DIR
from multiversion_backup.directory_creator import create_directory


# Defining class and functions representing a single source / output pair
class BackUp(Log):
    def __init__(self, source, output_targets, backup_name, limit_number):
        self.backup_name = backup_name.replace("-", "")
        self.limit = limit_number
        self.source = source
        self.file_modified_dt = None
        self.folder_modified_dt = None
        self.file_last_modified_dt(self.source)
        if type(output_targets) is str:
            self.output = [output_targets]
        elif type(output_targets) is list:
            self.output = output_targets
        else:
            output_exception_message = f"{self.backup_name} | execution halted - 'output_folders' var must be list or str"
            logging.error(output_exception_message)
            raise Exception(output_exception_message)

        # Create the log directory and define the full path of the log file
        logs_folder_path = create_directory(ROOT_DIR, "logs")
        log_path = os.path.join(logs_folder_path, "logs.txt")

        # Defining logging settings, creating log file if it does not already exist
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filename=log_path
        )

        # Inheriting everything from the Log superclass (see Log in the class definition BackUp(Log))
        # The __init__ method of Log() takes the log_path argument
        super().__init__(log_path)

    # Get current datetime as a string
    @staticmethod
    def get_dt_str():
        return datetime.today().strftime("%Y-%m-%d %H-%M %p")

    # Get datetime object from that string
    @staticmethod
    def get_dt_obj(date_string):
        return datetime.strptime(date_string, "%Y-%m-%d %H-%M %p")

    # Get a list of folders in a folder and sort them by the datetime string
    def get_folders(self, path):
        folders = []
        for entry in os.scandir(path):
            folder_path = entry.path
            folder_name = entry.name
            if re.match(f"^{self.backup_name}", folder_name):
                try:
                    folder_datetime = self.get_dt_obj(folder_name.split(" - ", 1)[1])
                    folders.append((folder_path, folder_name, folder_datetime))
                except ValueError:
                    logging.warning(f"{self.backup_name} | folder '{folder_name}' in '{path}'"
                                    f" did not match date time format and was skipped")
            else:
                logging.info(f"{self.backup_name} | folder '{folder_name}' in '{path}'"
                             f" did not start with prefix and was skipped")
        sorted_folders = sorted(folders, key=lambda x: x[2])
        return sorted_folders

    # Copy the source folder to the output folders
    # Delete the oldest folders outside of the limit property
    def copy_folder(self):
        for output_path in self.output:
            file_name = self.backup_name + " - " + self.get_dt_str()
            output_folder_details = self.get_folders(output_path)
            output_subdir = os.path.join(output_path, file_name)
            if file_name not in [x[1] for x in output_folder_details]:
                shutil.copytree(self.source, output_subdir)
                logging.info(f"{self.backup_name} | Folder | Saved '{output_subdir}'")
            else:
                logging.info(f"{self.backup_name} | Folder | DidNothing '{output_subdir}' - file already exists")
            output_folder_details_after = self.get_folders(output_path)
            if len(output_folder_details_after) > self.limit:
                folders_to_keep = output_folder_details_after[-abs(self.limit):]
                for folder in output_folder_details_after:
                    if folder not in folders_to_keep:
                        shutil.rmtree(folder[0])
                        logging.info(f"{self.backup_name} | Folder | Deleted '{folder[0]}'"
                                     f" - old folder outside limit ({self.limit})")

    # Get a list of files in the source folder
    def get_files(self, directory):
        file_details = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.relpath(file_path, directory)
                file_name_without_extension = os.path.splitext(file_name)[0]
                if re.match(f"^{self.backup_name}", file_name):
                    try:
                        file_datetime = self.get_dt_obj(file_name_without_extension.split(" - ", 1)[1])
                        file_details.append((file_path, file_name, file_datetime))
                    except ValueError:
                        logging.warning(f"{self.backup_name} | file '{file_name}' in '{directory}'"
                                        f" did not match date time format and was skipped")
                else:
                    logging.info(f"{self.backup_name} | folder '{file_name}' in '{directory}'"
                                 f" did not start with prefix and was skipped")
        sorted_files = sorted(file_details, key=lambda x: x[2])
        return sorted_files

    # Copy the source file to the output folders
    # Delete the oldest files outside of the limit property
    def copy_file(self, ext):
        for output_path in self.output:
            file_name = self.backup_name + " - " + self.get_dt_str()
            output_folder_details = self.get_files(output_path)
            output_file = os.path.join(output_path, file_name) + f".{ext}"
            if file_name not in [x[1] for x in output_folder_details]:
                shutil.copy(self.source, output_file)
                logging.info(f"{self.backup_name} | File | Saved '{output_file}'")
            else:
                logging.info(
                    f"{self.backup_name} | File | DidNothing '{output_file}' - file already exists")
            output_folder_details_after = self.get_files(output_path)
            if len(output_folder_details_after) > self.limit:
                files_to_keep = output_folder_details_after[-abs(self.limit):]
                for file in output_folder_details_after:
                    if file not in files_to_keep:
                        os.remove(file[0])
                        logging.info(
                            f"{self.backup_name} | File | Deleted '{file[0]}' - old file outside limit ({self.limit})")

    # Gets the last modified date of a file
    def file_last_modified_dt(self, file_path):
        try:
            modification_time = os.path.getmtime(file_path)
            last_modified_date = datetime.fromtimestamp(modification_time)
            self.file_modified_dt = last_modified_date
        except OSError:
            return f"Source file '{file_path}' was not found"

    # Run the 'copy_file' or 'copy_folder' functions based on log_path type detection of the source
    # If file, pass the file extention to the 'copy_file' argument
    # Only undertakes the copy method if the source has changed since the last logged backup
    def copy(self):
        is_dir = os.path.isdir(self.source)
        is_file = os.path.isfile(self.source)
        is_either = any([is_dir, is_file])
        last_log_dt = self.filter_logs(self.backup_name, 'saves').last_log_dt
        # For files, check if it is newer than the last logged modify-date, store in is_newer
        if is_file:
            is_newer = True  # True by default, avoiding NoneType errors for new backups
            if last_log_dt is not None:
                is_newer = self.file_modified_dt > last_log_dt
        # If the source is a directory
        if is_dir:
            self.copy_folder()
        # If the source is a file
        elif is_file and is_newer:
            file_ext = self.source.split(".")[-1]
            self.copy_file(file_ext)
        # if it was either a file or directory but failed the conditions above due to lack of changes
        elif is_either:
            no_changes_message = f"{self.backup_name} | File | DidNothing '{self.source}' no changes since last log"
            logging.info(no_changes_message)
        # Source variable had issues
        else:
            source_exception_message = f"{self.backup_name} | File | execution halted - 'source' var must be file or directory"
            logging.error(source_exception_message)
            raise Exception(source_exception_message)
