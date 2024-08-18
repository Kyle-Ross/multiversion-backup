from multiversion_backup import BackUp

# Create BackUp objects
important_backup = BackUp(
    r"C:\Program Files\Important Folder",  # Source
    r"C:\Users\johnc\OneDrive\Backup Storage Folder",  # Storage
    "my_backup",  # Prefix
    5,  # Max versions
)

# Run backup operations
important_backup.copy()
