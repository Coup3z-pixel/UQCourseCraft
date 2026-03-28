class ComparableSchedule:
    def __init__(self, score: int, schedule: dict):
        self.score = score
        self.schedule = schedule

    def __lt__(self, other):
        return self.score < other.score
