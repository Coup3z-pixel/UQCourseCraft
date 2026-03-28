import heapq

from ComparableSchedule import ComparableSchedule


class ScheduleHeap:
    def __init__(self, capacity: int) -> None:
        """
        Initialize a min-heap with a given capacity.
        """
        self.capacity = capacity
        self.heap = []

    def newEntry(self, score: int, schedule: dict) -> None:
        """
        Add a new entry to the heap with a given score and schedule. If the heap is not full or the
        new entry has a higher score than the smallest entry, it is added to the heap.
        """
        if len(self.heap) < self.capacity or score > self.heap[0].score:
            heapq.heappush(self.heap, ComparableSchedule(score, schedule))

            if len(self.heap) > self.capacity:
                heapq.heappop(self.heap)

    def getBestSchedules(self) -> list[dict]:
        """
        Get the best schedules from the heap, sorted by score in descending order.
        """
        output = self.heap.copy()
        output.sort(
            reverse=True, key=lambda x: x.score
        )  # Sort by score in descending order
        return [
            comparable_schedule.schedule for comparable_schedule in output
        ]  # Return in descending order of score

    def getBestSchedule(self) -> dict:
        """
        Get the best schedule from the heap.
        """
        print(self.heap)
        return self.heap[0].schedule if self.heap else None
