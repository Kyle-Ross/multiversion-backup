# multiversion-backup

## About
A 'BackUp' class which copies a target file or folder to set output folders. Detects and keeps a set amount of backup versions and deletes old backups outside that range. 

I made this since I was frustrated with syncing behaviours of services like OneDrive, which when used to sync files that were actively in use, would cause lag and other issues.

This method side steps the issue by letting you schedule when you copy to OneDrive, providing incremental multi-version backup and synchronisation without OneDrive disruptively trying to synchronise files that are always changing like game saves and settings.

## How-To Use

### Import the BackUp class
```python
from multiversion_backup import BackUp
```
### Create the BackUp object

#### Per File backup

```python
backup_object = BackUp(r"F:\image.jpg",  # Source file as a string
                     r"F:\File Backup",  # String or list of output folders
                     "important_file",  # Prefix for the output file name and log messages
                     3)  # Maximum amount of backups to keep
```

#### Per Folder backup

```python
backup_object = BackUp(r"F:\Folder",  # Source folder as a string
                       [r"F:\Folder Backup 1", r"F:\Folder Backup 2"],  # String or list of output folders
                       "important_folder",  # Prefix for the output folder name and log messages
                       5)  # Maximum amount of backups to keep
```

### Call the `.copy()` method

```python
backup_object.copy()
```

## What it does

- A version of the output is saved to the output folder or folders
- A log file is generated and added when the copy method is used detailing the backup activity (see example)
- Older backups outside of the specified limit are deleted
- Backups won't occur if the backup has no changes

## Troubleshooting

- File or folder names in the output folders will be ignored if they do not start with the defined prefix
- Changes to the datetime string formatting of the output files will raise exceptions