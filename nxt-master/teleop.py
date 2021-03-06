#!/usr/bin/python

import control
import curses
import math
import time
import threading
import socket
import select

class server2(threading.Thread):
    def __init__(self,teleop):
        threading.Thread.__init__(self)
        self.myteleop = teleop
    def run(self):
        s = socket.socket()
        host = socket.gethostname()
        port = 12345
        s.bind(('',port))
        
        s.listen(5)
        while not self.myteleop.stopthread:
            (ready_to_read, ready_to_write, in_error) = select.select([s],[s],[],1)
            for x in ready_to_read:
                c, addr = s.accept()    
                self.myteleop.threadLock.acquire()
                xpos = self.myteleop.xpos
                ypos = self.myteleop.ypos
                theta = self.myteleop.theta
                vx = self.myteleop.vx
                vy = self.myteleop.vy
                w = self.myteleop.w
                self.myteleop.threadLock.release()
                outstring = '{:f} {:f} {:f} {:f} {:f} {:f}'.format(xpos,ypos,theta,vx,vy,w)
                c.send(outstring)
                c.close()
        
class TeleOp:
    stdscr = None
    control = None
    threadLock = threading.Lock()
    stopthread = 0
    xpos = 0
    ypos = 0
    theta = 0
    vx = 0
    vy = 0
    w = 0
    

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
        
        self.stopthread = 0
        serverThread = server2(self)
        serverThread.start()
        

        while k != ord('q'):
            self.threadLock.acquire()
            self.readTacho()
            k = self.stdscr.getch()
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
            oldxpos = self.xpos
            oldypos = self.ypos
            if (abs(vr-vl) > 0.001):
                self.xpos = oldxpos + (wheeldistance*(vr+vl))/(2*(vr-vl))*(math.sin((vr-vl)*elapsed/wheeldistance + self.theta)-math.sin(self.theta))
                self.ypos = oldypos - (wheeldistance*(vr+vl))/(2*(vr-vl))*(math.cos((vr-vl)*elapsed/wheeldistance + self.theta)-math.cos(self.theta))
            else:
                self.xpos = oldxpos + 0.5*(vr+vl)*elapsed*math.sin(self.theta)
                self.ypos = oldypos - 0.5*(vr+vl)*elapsed*math.cos(self.theta)
            self.vx = (self.xpos-oldxpos)/elapsed
            self.vy = (self.ypos-oldypos)/elapsed
            oldtheta = self.theta
            self.theta = (rightchange-leftchange)/wheeldistance + self.theta
            self.w = (self.theta-oldtheta)/elapsed
            self.threadLock.release()
            self.stdscr.addstr(4, 4, "X Position:  %f        " % self.xpos)
            self.stdscr.addstr(5, 4, "Y Position:  %f        " % self.ypos)
            self.stdscr.addstr(6, 4, "Degree of Rotation (Rads):  %f        " % self.theta)
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
        self.control.idle()
        self.stopthread = 1
        serverThread.join()
