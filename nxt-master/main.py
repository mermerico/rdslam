#!/usr/bin/python

from control import *
from teleop import *

control = Control()

#control.motor_left.turn(100, 180);
#control.motor_right.turn(-100, 180);
teleop = TeleOp(control)

# light
# 0 0
# -458 414
# -893 832
# -1333 1247
# -1786 1649

# left
# -1786 1649
# -1421 1127
# -1047 641
# -677 156
# -347 -353

