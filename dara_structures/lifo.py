class Stack:
    def __init__(self):
        self.stack = []

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None

    def push(self, value):
        return self.stack.append(value)

    def peak(self):
        if not self.is_empty():
            return self.stack[-1]
        return None

    def size(self):
        return len(self.stack)

    def is_empty(self):
        return len(self.stack) == 0
