class PairIterator:
    def __init__(self, lst):
        self.lst = lst
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.lst):
            raise StopIteration
        if self.index + 1 >= len(self.lst):
            self.index += 1
            raise StopIteration
        pair = (self.lst[self.index], self.lst[self.index + 1])
        self.index += 2
        return pair
