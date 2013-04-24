#!/usr/bin/python

import control
import curses
import math
import time

class TeleOp:
    stdscr = None
    control = None

    def __init__(self, control):
        self.control = control
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.clear()
        self.loop()

    def __del__(self):
        curses.endwin()

    def clear(self):
        self.stdscr.erase()
        self.stdscr.addstr(0,10,"Hit 'q' to quit")

    def readTacho(self):
        left, right = self.control.getTacho()
        self.stdscr.addstr(2, 4, "Left Degrees:  %f        " % left)
        self.stdscr.addstr(3, 4, "Right Degrees: %f        " % right)

    def loop(self):
        self.stdscr.timeout(250)
        k = ''
        wheeldiameter = 0.055
        wheeldistance = 0.242
        oldleft, oldright = self.control.getTacho()
        oldleft = -oldleft #wheels are mounted backwards
        oldright = -oldright 
        oldtime = time.time()
        xpos = 0
        ypos = 0
        theta = 0
        
        while k != ord('q'):
            self.readTacho()
            k = self.stdscr.getch()
            #self.stdscr.addstr(5, 4, "k = %d" % k)
            newleft, newright = self.control.getTacho()
            newleft = -newleft #wheels are backwards
            newright = -newright
            newtime = time.time()
            elapsed = newtime - oldtime
            oldtime = newtime
            rightchange = math.pi*wheeldiameter*(newright-oldright)/360
            leftchange = math.pi*wheeldiameter*(newleft-oldleft)/360
            oldright = newright
            oldleft = newleft
            vr = rightchange/elapsed
            vl = leftchange/elapsed
            oldxpos = xpos
            oldypos = ypos
            if (abs(vr-vl) > 0.001):
                xpos = oldxpos + (wheeldistance*(vr+vl))/(2*(vr-vl))*(math.sin((vr-vl)*elapsed/wheeldistance + theta)-math.sin(theta))
                ypos = oldypos - (wheeldistance*(vr+vl))/(2*(vr-vl))*(math.cos((vr-vl)*elapsed/wheeldistance + theta)-math.cos(theta))
            else:
                xpos = oldxpos + 0.5*(vr+vl)*elapsed*math.sin(theta)
                ypos = oldypos - 0.5*(vr+vl)*elapsed*math.cos(theta)
            theta = (rightchange-leftchange)/wheeldistance + theta
            self.stdscr.addstr(4, 4, "X Position:  %f        " % xpos)
            self.stdscr.addstr(5, 4, "Y Position:  %f        " % ypos)
            self.stdscr.addstr(6, 4, "Degree of Rotation (Rads):  %f        " % theta)
            self.stdscr.addstr(7, 4, "rightchange:  %f       " % rightchange)
            self.stdscr.addstr(8, 4, "Elapsed:     %f        " % elapsed)
            self.stdscr.addstr(9, 4, "vr:     %f             " % vr)
            if k == 65: #curses.KEY_UP: 
                self.stdscr.addstr(15, 1, "FORWARD ");
                self.control.setSpeed(-80, -80);
            elif k == 66: #curses.KEY_DOWN: 
                self.stdscr.addstr(15, 1, "BACKWARD");
                self.control.setSpeed(80, 80);
            elif k == 67: #curses.KEY_RIGHT: 
                self.stdscr.addstr(15, 1, "RIGHT   ");
                self.control.setSpeed(-80, 80);
            elif k == 68: #curses.KEY_LEFT: 
                self.stdscr.addstr(15, 1, "LEFT    ");
                self.control.setSpeed(80, -80);
            elif k == ord(' '):
                self.stdscr.addstr(15, 1, "STOP    ");
                self.control.idle()
#            newleft, newright = self.control.getTacho()
#            newtime = time.time()
#            elapsed = newtime - oldtime
#            oldtime = newtime
#            rightchange = math.pi*wheeldiameter*(newright-oldright)/360
#            leftchange = math.pi*wheeldiameter*(newleft-oldleft)/360
#            oldright = newright
#            oldleft = newleft
#            vr = rightchange/elapsed
#            vl = leftchange/elapsed
#            oldxpos = xpos
#            oldypos = ypos
#            oldtheta = theta
#            if math.abs(vr-vl) > 0.001:
#                xpos = oldxpos + (wheeldistance*(vr+vl))/(2*(vr-vl))*(math.sin((vr-vl)*elapsed/wheeldiameter + theta)-math.sin(theta));
#                ypos = oldypos - (wheeldistance*(vr+vl))/(2*(vr-vl))*(math.cos((vr-vl)*elapsed/wheeldiameter + theta)-math.cos(theta));
#            else:
#                xpos = oldxpos + 0.5*(vr+vl)*math.sin(theta);
#                ypos = oldypos - 0.5*(vr+vl)*math.cos(theta);
#            theta = (rightchange-leftchange)/wheeldiameter + oldtheta
