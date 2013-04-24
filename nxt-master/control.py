#!/usr/bin/python

import sys
import nxt.locator
from nxt.motor import *

class Control:
    brick = None
    motor_left = None
    motor_right = None

    def __init__(self):
        self.connect()

    def connect(self):
        try:
            self.brick = nxt.locator.find_one_brick()
        except:
            print("couldn't find a brick!")
            sys.exit()
        self.motor_left = Motor(self.brick, PORT_A)
        self.motor_right = Motor(self.brick, PORT_B)

    def setSpeed(self, left_speed, right_speed):
        self.motor_left.run(left_speed)
        self.motor_right.run(right_speed)

    def idle(self):
        self.motor_left.idle()
        self.motor_right.idle()

    def getTacho(self):
        return self.motor_left.get_tacho().rotation_count, \
               self.motor_right.get_tacho().rotation_count

