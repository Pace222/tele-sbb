
class Journey:
    #
    def __init__(self, journey_id, title, destination, deadline_month, deadline_day, deadline_time, users=None, plan=""):
        self.journey_id = journey_id
        self.title = title
        self.destination = destination
        self.deadline_month = deadline_month
        self.deadline_day = deadline_day
        self.deadline_time = deadline_time
        if users is None:
            users = {}
        self.users = users
        self.plan = plan

    def __str__(self):
        return f"Journey {self.title} to {self.destination} with {len(self.users)} users"


