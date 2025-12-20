class IncidentState:
    def __init__(self):
        self.active = False
        self.start_time = None
        self.root_cause = None
        self.root_cause = None
        self.severity = None
        self.recovery_windows = 1

    def open(self, timestamp, diagnosis):
        self.active = True
        self.start_time = timestamp
        self.root_cause = diagnosis["root_cause"]
        self.severity = diagnosis["severity"]

    def update(self, diagnosis):
        # keep the highest severity
        if diagnosis["severity"] == "high":
            self.severity = "high"

    def close(self):
        self.active = False
        self.start_time = None
        self.root_cause = None
        self.severity = None
