#!/usr/bin/env python
import random
import json

class Baseball:
    MAX_NUMBER_LENGTH = 32
    DEFAULT_NUMBER_LENGTH = 3
    DEFAULT_GAME_COUNT = 10

    def __init__(self, number, length=DEFAULT_NUMBER_LENGTH, count=DEFAULT_GAME_COUNT):
        self.number = number
        self.length = length
        self.count = count

    @staticmethod
    def loads(_json):
        try:
            j = json.loads(_json)
            return Baseball(**j)
        except:
            return None

    def __str__(self):
        try:
            return json.dumps(self.__dict__, indent=4)
        except:
            return ""

    @staticmethod
    def make_game(num_length=DEFAULT_NUMBER_LENGTH):
        if num_length >= Baseball.MAX_NUMBER_LENGTH:
            return None

        game = ""
        while len(game) != num_length:
            var = random.randrange(1, 10)
            svar = ("%d" % var)
            if game.find(svar) >= 0:
                continue
            game += svar
        print game
        return game

    def run(self, value):
        return self._judge_strike(value) | self._judge_ball(value)

    def validate(self, value):
        if self.count <= 0:
            return "Sorry. Please restart again."

        if (not value.isdigit()) | (not len(value) == self.length):
            return "Please input %d length digit number." % self.length 

        hasZero = False
        charValue = {}
        for i in range(0, len(value)):
            if (value[i] == '0'):
                hasZero = True
            key = value[i]
            charValue[key] = key

        if hasZero == True:
            return "Please input 1 ~ 9 number."

        if not len(charValue) == self.length:
            return "Please input different number."
        return None

    def decrease(self):
        self.count -= 1
        return self.count

    def left_count(self):
        return self.count

    def length(self):
        return self.length

    def number(self):
        return self.number

    def get_strike(self, result):
        c = 0
        for index in range(0, self.length):
            if result & (1 << index):
                c += 1
        return c

    def get_ball(self, result):
        c = 0
        for index in range(0, self.length):
            if result & (1 << (index + self.length)):
                c += 1
        return c
    
    def is_out(self, result):
        c = self.get_strike(result)
        return c == self.length

    def _contain(self, strValue, charValue, index):
        i = strValue.find(charValue)
        return (i >= 0) & (i != index)

    def _judge_strike(self, value):
        result = 0
        for index in range(0, len(self.number)):
            if self.number[index] == value[index]:
                result += (1 << (index))
        return result

    def _judge_ball(self, value):
        result = 0
        for index in range(0, len(self.number)):
            if self._contain(self.number, value[index], index):
                result += (1 << (index + self.length))
        return result
    
def Main():
    print "Baseball Game!"

    value = Baseball.make_game()
    bb = Baseball(value)

    while True:
        left = bb.left_count()
        if left <= 0:
            print "Game Over!"
            exit()

        print "Left count = ", left
        val = input("Guess ? ")
        err = bb.validate(str(val))
        if not err is None:
            print err
            continue

        result = bb.run(str(val));
        bb.decrease()

        s = bb.get_strike(result)
        b = bb.get_ball(result)

        if bb.is_out(result):
            print "You did it! Good Boy! Bye!!"
            exit()

        print "%dStrike(s), %dBall(s)" % (s, b)

if __name__ == '__main__':
    Main()
