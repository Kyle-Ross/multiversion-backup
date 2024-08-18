import os


def create_directory(directory, directory_name) -> str:
    """Function to check a directory and create it if it doesn't exist, logging the outcome & returning the directory"""
    full_path = os.path.join(directory, directory_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path
