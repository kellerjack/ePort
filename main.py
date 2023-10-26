#!/usr/bin/env python3
#Jack Keller, Team 0-sp, Section 002, ENED 1120, 3/27/23

#--------------------CONNECT TO EV3 VIA BT-------------------
#1) Click the "Click here to connect" below "EV3DEV DEVICE 
#   MANAGER" in bottom left corner of VSC
#2) Select "I don't see my device..."
#3) Enter ev3dev into the query
#4) On EV3, get IP address to show by pairing with computer
#5) Enter IP address into VSC
#------------------------------------------------------------

#--------------------HOW TO RUN FILES------------------------
#1) Right click "ev3dev" in bottom-left with the green circle
#2) Click on "Open SSH Terminal"
#3) Paste the below line WITHOUT hashtage when ready to run:
#python3 robot_hub/main.py
#4) This should run this file from the robot_hub folder
#5) Prompts should begin to appear after a short load
#------------------------------------------------------------

#one rotation ~ 15 degrees @ 50 speed

#IMPORT LIBRARIES
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.display import Display
from time import sleep

#INITIALIZE MOTORS/SENSORS
mRight = Motor(OUTPUT_A)
mLeft = Motor(OUTPUT_B)
mBoth = MoveTank(OUTPUT_B, OUTPUT_A)
mClaw = MediumMotor(OUTPUT_D)
leftLight = ColorSensor(INPUT_1)
screen = Display

#--------------------REQUIRED TEST VALUES--------------------
#enter the desired speedpercent (May be negative depending on polarity. Use the sign for forward)
sp = -25
#enter the speed in inches per second at that speedpercent
dps = 5.11
#------------------------------------------------------------

#GATHER USER INPUT 
#FORMAT: A1 is the unit, 3 is the box, 1 is the barcode type, c is the fulfillment)
shelf = input("Enter pick list (ex. input: [A1_3, 1, C])")

#INITIALIZE SOME VARIABLES (for bcLib, 1 is black, 6 is white)
L = shelf[1].lower()
shelfN = int(shelf[2])
boxN = int(shelf[4])
barT = int(shelf[7])
dest = shelf[10].lower()
bcLib = [[1,[1,6,6,6]], [2,[1,6,1,6]], [3,[1,1,6,6]], [4,[1,6,6,1]]]
wrap = bool
route = []
rFinal = []

#first letter is destination, inner letter is current location, inner most purple are the route values
#the current location is:
#   dest a/c: left most position of shelf
#   dest b/d: right most position of shelf
poss = [['a',
         ['a', [1, []], [2, []]], 
         ['b', [1, []], [2, []]], 
         ['c', [1, []], [2, []]], 
         ['d', [1, [1]], [2, []]]],
        ['b', 
         ['a', [1, []], [2, []]], 
         ['b', [1, []], [2, []]], 
         ['c', [1, []], [2, []]], 
         ['d', [1, [1]], [2, []]]],
        ['c', 
         ['a', [1, ['right', 90]], [2, ['right', 78]]], 
         ['b', [1, []], [2, []]], 
         ['c', [1, []], [2, []]], 
         ['d', [1, [1]], [2, []]]],
        ['d', 
         ['a', [1, []], [2, []]], 
         ['b', [1, []], [2, []]], 
         ['c', [1, []], [2, []]], 
         ['d', [1, [1]], [2, []]]]
]

#REUSED FUNCTIONS
def timef(d):
    return d / dps

def leftTurn():
    mBoth.on_for_seconds(SpeedPercent(25),SpeedPercent(-25), 2)
    mBoth.stop()

def rightTurn():
    mBoth.on_for_seconds(SpeedPercent(-25),SpeedPercent(25), 2)
    mBoth.stop()

#ONE TIME FUNCTIONS IN ORDER
#THIS GETS TO BOXES > 6
def further():
    rightTurn()
    mBoth.on_for_seconds(SpeedPercent(25),SpeedPercent(25), timef(48))
    leftTurn()
    mBoth.on_for_seconds(SpeedPercent(25),SpeedPercent(25), timef(12))
    leftTurn()

#THIS GOES DISTANCE TO GET TO BARCODE
def getToBox(boxN):
    dpb = 2.5
    mBoth.on_for_seconds(SpeedPercent(25),SpeedPercent(25), timef(dpb * boxN))

#THIS SCANS THE BARCODE
def barCode(barT):
    pallate = []
    mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
    mBoth.stop()
    pallate.append(leftLight.reflected_light_intensity())
    mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
    mBoth.stop()
    pallate.append(leftLight.reflected_light_intensity())
    mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
    mBoth.stop()
    pallate.append(leftLight.reflected_light_intensity())
    mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
    mBoth.stop()
    pallate.append(leftLight.reflected_light_intensity())
    for x in range(4):
        if pallate[x] > 40:
            pallate[x] = 6
        else:
            pallate[x] = 1
    if (pallate == bcLib[barT - 1][1]):
        return True
    return False

#-----------------------EVENT THAT BARCODE MATCHES-----------------------------
#GRAB BOX
def getBox():
    if wrap:
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
        mBoth.stop()
        mClaw.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
        mClaw.stop()
        mBoth.on_for_seconds(SpeedPercent(-sp), SpeedPercent(-sp), timef(0.5))
        mBoth.stop()
    else:
        rightTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
        mBoth.stop()
        mClaw.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(0.5))
        mClaw.stop()
        mBoth.on_for_seconds(SpeedPercent(-sp), SpeedPercent(-sp), timef(0.5))
        mBoth.stop()

#ROBOT FACES WHERE THE DROP OFF IS
def orient():
    if wrap:
        if dest == 'c':
            rightTurn()
            mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(6 - boxNew))
            mBoth.stop()
        elif dest == 'b' or dest == 'd':
            leftTurn()
            mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(boxNew))
            mBoth.stop()
    else: 
        if dest == 'c':
            leftTurn()
            mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(boxN))
            mBoth.stop()
        elif dest == 'b' or dest == 'd':
            rightTurn()
            mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(6 - boxN))
            mBoth.stop()
#------------------------------------------------------------------------------------
#GETS ROBOT WITH BOX TO DROP OFF
def finalRoute():
    for x in range(4):
        if poss[x][0] == dest:
            for y in range(1,5):
                if poss[x][y][0] == L:
                    for i in range(1,3):
                        if poss[x][y][i][0] == shelfN:
                            rFinal = poss[x][y][i][1]

#GETS ROBOT TO HOME ASSUMING ROBOT HAD BOX
def home():
    if dest == 'c':
        leftTurn()
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(120))
    elif dest == 'b':
        leftTurn()
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(6))
        rightTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(100))
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(100))
    elif dest == 'd':
        leftTurn()
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(6))
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(100))
        leftTurn()
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(6))

#--------------------LOGIC FOR RUN SEQUENCE----------
#DETERMINE ROUTE
#change route values accordingly. The inner yellow brackets are the actual route, the letter and number in front are just shelf unit identifiers
#note: this route just get robot to bottom left corner of the shelf
routes = [['a',
           [1,[12]],
           [2,[24]]],
          ['b',
           [1,[12,'right',42,'left']],
           [2,[12,'right',42,'left',12]]],
          ['c',
           [1,[36]],
           [2,[48]]],
          ['d',
           [1,[12,'right',42,'left',24]],
           [2,[12,'right',42,'left',36]]],]

for x in range(4):
    if routes[x][0] == L:
        for y in range (1,3):
            if routes[x][y][0] == shelfN:
                route = routes[x][y][1]

#DETERMINE IF IT SHOULD WRAP AROUND SHELF
if boxN > 6:
    wrap = True

#----------------RUN SEQUENCE-------------------------
#RUN ROUTE TO BOTTOM LEFT CORNER
for x in range(len(route) - 1):
    if route(x) == 'right':
        rightTurn()
    elif route(x) == 'left':
        leftTurn()
    else:
        mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(route(x)))
        mBoth.stop()

#WRAP FOR BOXES 7 - 12
if wrap == True:
    further()

#DISTANCE TO GET TO BOX
boxLib = [[12,1],[11,2],[10,3],[9,4],[8,5],[7,6]]
if boxN > 6:
    for x in range(6):
        if boxN == boxLib[x][0]:
            boxNew = boxLib[x][1]
            getToBox(boxNew)
        else:
            getToBox(boxN)

#SCAN BOX/DISPLAY/RETURN HOME
# EVENT BARCODE -DOES- MATCH
if barCode():
    getBox()
    orient()
    finalRoute()
    for x in range(len(rFinal) - 1):
        if rFinal(x) == 'right':
            rightTurn()
        elif rFinal(x) == 'left':
            leftTurn()
        else:
            mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(rFinal(x)))
            mBoth.stop()
    home()
# EVENT BARCODE DOES -NOT- MATCH
else: 
    screen.text_pixels("Barcode Mismatch", clear_screen = True, x = 89, y = 64)
    screen.update()
    sleep(10)
    #screen.text_pixels(screen, "Barcode Mismatch", False, 89, 64)
    dest = 'a'
    finalRoute()
    for x in range(len(rFinal) - 1):
        if rFinal(x) == 'right':
            rightTurn()
        elif rFinal(x) == 'left':
            leftTurn()
        else:
            mBoth.on_for_seconds(SpeedPercent(sp), SpeedPercent(sp), timef(rFinal(x)))
            mBoth.stop()

