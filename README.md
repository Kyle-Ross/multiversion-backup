# multiversion-backup

## About
A 'BackUp' class which copies a target file or folder to set output folders. Detects and keeps a set amount of backup versions and deletes old backups outside that range. 

I made this since I was frustrated with syncing behaviours of services like OneDrive, which when used to sync files that were actively in use, would cause lag and other issues.

This method side steps the issues by allowing me to schedule when I copy certain folders to OneDrive, giving me incremental multi-version backup and synchronisation through the service without distributively trying to synchronise files that are always changing like game saves and settings.

## How-To Use

1. import the class: 
```python
from BackUp import BackUp
```
4. Create the BackUp object:
``` python
backup_object = BackUp(source,  # Source folder or file path as a string
                       output_targets,  # String or list of output folder paths
                       prefix_string,  # Prefix for the file name and log messages
                       limit_number)  # Maximum amount of backups to keep
```
3. Call the `.copy()` method

```python
backup_object.copy()
```

## Behaviours

- A log file is generated and added when the copy method is used detailing backup activity (see example)
- Older backups outside of the specified limit are deleted
- File or folder names in the output folders will be ignored if they do not start with the defined prefix
- Changes to the datetime string formatting of the output files will raise exceptions

## Example usage

### Folder backup

```python
from BackUp import BackUp

folder_backup = BackUp(r"F:\Folder",  # Source folder or file path as a string
                       [r"F:\Folder Backup 1", r"F:\Folder Backup 2"],  # String or list of output folders
                       "important_folder",  # Prefix for the file name and log messages
                       5)  # Maximum amount of backups to keep

folder_backup.copy()
```

### File backups
```python
from BackUp import BackUp

file_backup = BackUp(r"F:\image.jpg",
                     r"F:\File Backup",
                     "important_file",
                     3)

file_backup.copy()
```


