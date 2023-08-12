from datetime import datetime


class Log:
    def __init__(self, log_path):
        self.original_data = None
        self.path = log_path
        self.data = []  # Storage for unpacked log data dicts
        self.get_data()  # Get the log data
        self.max_dt = None
        self.max_line = None
        self.max_logtype = None
        self.max_backup_name = None
        self.max_filetype = None
        self.max_action = None
        self.set_max()  # Setting undefined properties using function below

    def get_data(self):
        # Open the file in read mode
        with open(self.path, 'r') as file:
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
            self.data.append(line_dict)

        # Storing copy of full, unfiltered data
        self.original_data = self.data

    # Function to update max line values using self.data
    def set_max(self):
        self.max_dt = max([x["datetime"] for x in self.data])
        self.max_line = [x for x in self.data if x["datetime"] == self.max_dt][-1]
        self.max_logtype = self.max_line["logtype"]
        self.max_backup_name = self.max_line["backup_name"]
        self.max_filetype = self.max_line["filetype"]
        self.max_action = self.max_line["action"]

    def filter_data(self, backup_name, action):

        # Checking action input
        allowed = ('all', 'saves', 'deletes')  # Check args
        if action not in allowed:
            raise Exception(f"Argument for self.action() must be in f{allowed}")
        # Checking backup_name input
        if backup_name not in [x["backup_name"] for x in self.data]:
            raise Exception(f"Argument for self.backup_names() does not exist in log file")

        # Filter data property per backup_name
        self.data = [x for x in self.original_data if x["backup_name"] == backup_name]

        # Filter data property per action
        if action == 'all':
            self.data = self.data
        if action == 'saves':
            self.data = [x for x in self.data if x["action"] == 'Saved']
        if action == 'deletes':
            self.data = [x for x in self.data if x["action"] == 'Deleted']

        # Update values for max properties based on the now filtered self.data
        self.set_max()

        # Return self for argument chaining
        return self
