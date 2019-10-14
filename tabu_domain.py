class TabuListClass:
    def __init__(self, op, move, valid_for):
        self.op = op
        self.move = move
        self.valid_for = valid_for

    def checked(self):
        self.valid_for -= 1

    def found_match(self,move):
        if self.move == move and self.valid_for > 0:
            self.valid_for -= 1
            return True
        return False



