class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None

    def is_empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)
    
test_list = Stack()
test_list.push({'table': 'noaa_ace'})
test_list.push({'data_id': 'noaa_ace_mag'})
for i in test_list.stack:
    print(i)