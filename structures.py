class Stack(list):
    def __init__(self):
        super().__init__()

    def push(self, element):
        self.append(element)


class Queue:
    def __init__(self):
        self.s1 = Stack()
        self.s2 = Stack()

    def push(self, elem):
        self.s1.push(elem)

    def pop(self):
        if not self.s2:
            while self.s1:
                self.s2.push(self.s1.pop())
        return self.s2.pop()

    def size(self):
        return len(self.s1) + len(self.s2)
