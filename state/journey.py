
class Journey:
    #
    def __init__(self, journey_id, title, destination, deadline, users=None):
        self.journey_id = journey_id
        self.title = title
        self.destination = destination
        self.deadline = deadline
        if users is None:
            users = {}
        self.users = users



