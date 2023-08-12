from datetime import datetime


class Log:
    """Provides access to log file data for the BackUp class and its methods"""
    def __init__(self, log_path):
        self.original_log_data = None
        self.log_path = log_path
        self.log_data = []  # Storage for unpacked log log_data dicts
        self.get_logs()  # Get the log log_data
        self.last_log_dt = None
        self.last_log_line = None
        self.last_log_type = None
        self.last_backup_name = None
        self.last_log_filetype = None
        self.last_log_action = None
        self.set_properties()  # Setting 'None' properties using function below

    def get_logs(self):
        # Open the file in read mode
        with open(self.log_path, 'r') as file:
            lines = file.readlines()  # Read all lines and store them in a list

        # Get the datetimes from the log and add them to the list
        for line in lines:
            # Storage of the per line dict
            line_dict = {}

            # Split log by sep
            list_items = [x.strip() for x in line.split(sep='|')]

            # Get datetime
            try:
                dt_str = list_items[0]
                line_dict["datetime"] = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print(f"Could not convert '{line}' to a datetime.")

            # Get log type
            line_dict["logtype"] = list_items[1]

            # Get identifier aka prefix
            line_dict["backup_name"] = list_items[2]

            # Get file type
            line_dict["filetype"] = list_items[3]

            # Get action that was taken per line
            line_dict["action"] = list_items[4].split("'")[0].strip()
            accepted_actions = ('Saved', 'Deleted')
            if line_dict["action"] not in accepted_actions:
                raise Exception(f"Log file features unknown action status not in {accepted_actions}, please review")

            # Append the log dict object property
            self.log_data.append(line_dict)

        # Storing copy of full, unfiltered log_data
        self.original_log_data = self.log_data

    # Function to update max line values using self.log_data
    def set_properties(self):
        self.last_log_dt = max([x["datetime"] for x in self.log_data])
        self.last_log_line = [x for x in self.log_data if x["datetime"] == self.last_log_dt][-1]
        self.last_log_type = self.last_log_line["logtype"]
        self.last_backup_name = self.last_log_line["backup_name"]
        self.last_log_filetype = self.last_log_line["filetype"]
        self.last_log_action = self.last_log_line["action"]

    def filter_logs(self, backup_name, action):

        # Checking action input
        allowed = ('all', 'saves', 'deletes')  # Check args
        if action not in allowed:
            raise Exception(f"Argument for self.action() must be in f{allowed}")
        # Checking backup_name input
        if backup_name not in [x["backup_name"] for x in self.log_data]:
            raise Exception(f"Argument for self.backup_names() does not exist in log file")

        # Filter log_data property per backup_name
        self.log_data = [x for x in self.original_log_data if x["backup_name"] == backup_name]

        # Filter log_data property per action
        if action == 'all':
            self.log_data = self.log_data
        if action == 'saves':
            self.log_data = [x for x in self.log_data if x["action"] == 'Saved']
        if action == 'deletes':
            self.log_data = [x for x in self.log_data if x["action"] == 'Deleted']

        # Update values for max properties based on the now filtered self.log_data
        self.set_properties()

        # Return self for argument chaining
        return self
