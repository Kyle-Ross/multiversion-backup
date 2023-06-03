from datetime import datetime
import logging
import shutil
import os
import re


# Defining class and functions representing a single source / output pair
class BackUp:
    def __init__(self, source, output_targets, prefix_string, limit_number):
        self.prefix = prefix_string.replace("-", "")
        self.limit = limit_number
        self.source = source
        if type(output_targets) == str:
            self.output = [output_targets]
        elif type(output_targets) == list:
            self.output = output_targets
        else:
            output_exception_message = f"{self.prefix} | execution halted - 'output_folders' var must be list or str"
            logging.error(output_exception_message)
            raise Exception(output_exception_message)

    # Defining logging settings
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="logs.txt"
    )

    # Get current datetime as a string
    def get_dt_str(self):
        return datetime.today().strftime("%Y-%m-%d %H-%M %p")

    # Get datetime object from that string
    def get_dt_obj(self, date_string):
        return datetime.strptime(date_string, "%Y-%m-%d %H-%M %p")

    # Get a list of folders in a folder and sort them by the datetime string
    def get_folders(self, path):
        folders = []
        for entry in os.scandir(path):
            folder_path = entry.path
            folder_name = entry.name
            if re.match(f"^{self.prefix}", folder_name):
                try:
                    folder_datetime = self.get_dt_obj(folder_name.split(" - ", 1)[1])
                    folders.append((folder_path, folder_name, folder_datetime))
                except ValueError:
                    logging.warning(f"{self.prefix} | folder '{folder_name}' in '{path}'"
                                    f" did not match date time format and was skipped")
            else:
                logging.info(f"{self.prefix} | folder '{folder_name}' in '{path}'"
                             f" did not start with prefix and was skipped")
        sorted_folders = sorted(folders, key=lambda x: x[2])
        return sorted_folders

    # Copy the source folder to the output folders
    # Delete the oldest folders outside of the limit property
    def copy_folder(self):
        for output_path in self.output:
            file_name = self.prefix + " - " + self.get_dt_str()
            output_folder_details = self.get_folders(output_path)
            output_subdir = os.path.join(output_path, file_name)
            if file_name not in [x[1] for x in output_folder_details]:
                shutil.copytree(self.source, output_subdir)
                logging.info(f"{self.prefix} | Folder | Saved '{output_subdir}'")
            else:
                logging.info(f"{self.prefix} | Folder | Did not save '{output_subdir}' - file already exists")
            output_folder_details_after = self.get_folders(output_path)
            if len(output_folder_details_after) > self.limit:
                folders_to_keep = output_folder_details_after[-abs(self.limit):]
                for folder in output_folder_details_after:
                    if folder not in folders_to_keep:
                        shutil.rmtree(folder[0])
                        logging.info(f"{self.prefix} | Folder | Deleted '{folder[0]}'"
                                     f" - old folder outside limit ({self.limit})")

    # Get a list of files in the source folder
    def get_files(self, directory):
        file_details = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.relpath(file_path, directory)
                file_name_without_extension = os.path.splitext(file_name)[0]
                if re.match(f"^{self.prefix}", file_name):
                    try:
                        file_datetime = self.get_dt_obj(file_name_without_extension.split(" - ", 1)[1])
                        file_details.append((file_path, file_name, file_datetime))
                    except ValueError:
                        logging.warning(f"{self.prefix} | file '{file_name}' in '{directory}'"
                                        f" did not match date time format and was skipped")
                else:
                    logging.info(f"{self.prefix} | folder '{file_name}' in '{directory}'"
                                 f" did not start with prefix and was skipped")
        sorted_files = sorted(file_details, key=lambda x: x[2])
        return file_details

    # Copy the source file to the output folders
    # Delete the oldest files outside of the limit property
    def copy_file(self, ext):
        for output_path in self.output:
            file_name = self.prefix + " - " + self.get_dt_str()
            output_folder_details = self.get_files(output_path)
            output_file = os.path.join(output_path, file_name) + f".{ext}"
            if file_name not in [x[1] for x in output_folder_details]:
                shutil.copy(self.source, output_file)
                logging.info(f"{self.prefix} | File | Saved '{output_file}'")
            else:
                logging.info(
                    f"{self.prefix} | File | Did not save '{output_file}' - file already exists")
            output_folder_details_after = self.get_files(output_path)
            if len(output_folder_details_after) > self.limit:
                files_to_keep = output_folder_details_after[-abs(self.limit):]
                for file in output_folder_details_after:
                    if file not in files_to_keep:
                        os.remove(file[0])
                        logging.info(
                            f"{self.prefix} | File | Deleted '{file[0]}' - old file outside limit ({self.limit})")

    # Run the 'copy_file' or 'copy_folder' functions based on path type detection of the source
    # If file, pass the file extention to the 'copy_file' argument
    def copy(self):
        if os.path.isdir(self.source):
            self.copy_folder()
        elif os.path.isfile(self.source):
            file_ext = self.source.split(".")[-1]
            self.copy_file(file_ext)
        else:
            source_exception_message = f"{self.prefix} | execution halted - 'source' var must be file or directory"
            logging.error(source_exception_message)
            raise Exception(source_exception_message)
