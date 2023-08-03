import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time
from datetime import datetime, timedelta
import pygame
import pigpio
from imutils.video import VideoStream
import requests

#initailize pygame controller stuff
pygame.init()
#setup xbox controller
joy = pygame.joystick.Joystick(0)
joy.init()
print(joy.get_name())

# pygame controls:
# Buttons: 0-A, 1-B, 2-X, 3-Y
# Axis: leftX-0, leftY-1, LT-2, rightX-3, rightY-4, RT-5


#servo positions @ 100Hz
#0deg - 5% 500micro sec
#135deg - 15% 1500micro sec
#270deg - 25% 2500micro sec
pi = pigpio.pi()

#define pins
hor_D = 22
hor_S = 23
ver_D = 17
ver_S = 27



horizontalMotor = RpiMotorLib.A4988Nema(hor_D, hor_S, (-1,-1,-1))
verticalMotor = RpiMotorLib.A4988Nema(ver_D, ver_S, (-1,-1,-1))

count = 0
auto = False
fireStatus = 'u' #'u'-uncharged   'c'-charged   'f'-firing
MOVECONST = 1.9 #constant multiplier for autonomous movement
xTarget = 0
yTarget = 0
lastDetection = datetime.now()

def autoMove(x, y):
    if x<0: #x direction
        xRot = False
    else:
        xRot = True
        
    if y<0: #y direction
        yRot = True
    else:
        yRot = False
    
    if abs(x)>abs(y):
        for i in range( int(abs(y) *MOVECONST)): #diagonal movement
            horizontalMotor.motor_go(xRot, "1/4", 1, 0.0005, False, 0.00)
            verticalMotor.motor_go(yRot, "1/4", 1, 0.0005, False, 0.00)
        for i in range( int((abs(x)-abs(y)) *MOVECONST)): #remaining straight movement x
            horizontalMotor.motor_go(xRot, "1/4", 1, 0.0005, False, 0.00)
            
    else:
        for i in range( int(abs(x) *MOVECONST)): #diagonal movement
            horizontalMotor.motor_go(xRot, "1/4", 1, 0.0005, False, 0.00)
            verticalMotor.motor_go(yRot, "1/4", 1, 0.0005, False, 0.00)
        for i in range( int((abs(y)-abs(x)) *MOVECONST)): #remaining straight movement y
            verticalMotor.motor_go(yRot, "1/4", 1, 0.0005, False, 0.00)
            

#main
while(True):
    pygame.event.get()
    x_axis = joy.get_axis(3)
    y_axis = joy.get_axis(1)
    trigger = joy.get_axis(5)
    
    #do remote control shit
    while(True):
        pygame.event.get()
        x_axis = joy.get_axis(3)
        y_axis = joy.get_axis(1)
        trigger = joy.get_axis(5)
        if (x_axis <=-0.5):
            #move left
            horizontalMotor.motor_go(False, "1/4", 1, 0.0005, False, 0.00)
            
        if (x_axis >=0.5):
            #move right
            horizontalMotor.motor_go(True, "1/4", 1, 0.0005, False, 0.00)
        
        if (y_axis <= -0.5):
            #move up
            verticalMotor.motor_go(True, "1/4", 1, 0.0005, False, 0.00)
                
        if (y_axis >= 0.5):
            #move down
            verticalMotor.motor_go(False, "1/4", 1, 0.0005, False, 0.00)
            
        if (trigger >= -0.25 and trigger <= 0.5): #charge trigger
            fireStatus='c'
            pi.set_servo_pulsewidth(24, 1250)
        elif (trigger > 0.5): #Fire
            fireStatus='f'
            pi.set_servo_pulsewidth(24, 1100)
        else: #release trigger
            fireStatus='u'
            pi.set_servo_pulsewidth(24, 1500)
            
        if (joy.get_button(0)): #on 'a' return to autonomous
            auto=True
            break
    
    #if sticks not moved do autonomous
    if (auto==True and x_axis < 0.1 and x_axis > -0.1 and y_axis < 0.1 and y_axis > -0.1):
        #do autonomous shit
        #get coords and split xTarget, yTarget
        response = requests.get('http://192.168.0.198:5000').content
        split = response.decode().split("<h1>")[1].split("</h1")
        respCoords = split[0]
        print(respCoords)
        
        if respCoords == '0':
            #firing timeout if no people detected for 1 seconds timeout firing
            if lastDetection + timedelta(seconds = 1) < datetime.now() and fireStatus!='u':
                fireStatus = 'u'
                pi.set_servo_pulsewidth(24, 1500)
            continue
        else:
            lastDetection = datetime.now()
            #split coords
            respCoords = respCoords.replace('(', '')
            respCoords = respCoords.replace(')', '')
            respCoords = respCoords.replace(' ', '')
            respCoords = respCoords = respCoords.split(',')
            xTarget = int(float(respCoords[0]))
            yTarget = int(float(respCoords[1]))
            
            #charge if not charged or firing
            if fireStatus!='c' and fireStatus!='f':
                fireStatus = 'c'
                pi.set_servo_pulsewidth(24, 1250)
            
            #move
            autoMove(xTarget, yTarget)
            
            #start firing if not firing
            if fireStatus!='f':
                fireStatus='f'
                pi.set_servo_pulsewidth(24, 1100)
                
            
        
    elif (joy.get_button(1)): #on 'b' exit
        break
    else:
        auto=False


pi.stop()
GPIO.cleanup()
#motor control
#horizontalMotor.motor_go(False, "1/8", 1600, 0.0005, False, 0.05)
#horizontalMotor.motor_go(True, "1/8", 1600, 0.0005, False, 0.05)
#verticalMotor.motor_go(False, "1/8", 1600, 0.0005, False, 0.05)
#verticalMotor.motor_go(True, "1/8", 1600, 0.0005, False, 0.05)
