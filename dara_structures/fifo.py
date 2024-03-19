class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.insert(0, value)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop()
        return None

    def size(self):
        return len(self.queue)

    def is_empty(self):
        return self.size() == 0
