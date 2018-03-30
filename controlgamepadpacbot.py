import socket
import io
from urllib2 import urlopen
import threading
import json
import time
import gamepad  # make sure gamepad.py is in the same folder as this

random.seed()

host = "robot.sr"  # 127.0.0.1
port = 4096
s = socket.socket()

while True:
    try:
        s.connect((host, port))
        break
    except socket.error, msg:
        print "Socket Error: " + msg[1]
        host = raw_input("Enter address of control server (probably robot.sr): ")


def update():
    send_gamepad_input()
    print "Sending data... {}".format(gamepad.LTHUMBSTICK_Y)
    time.sleep(0.1)


def send_gamepad_input():
    input_vals = gamepad.get()
    s.send(json.dumps({
        "LThumbstick_Y": input_vals[gamepad.LTHUMBSTICK_Y],
        "LThumbstick_X": input_vals[gamepad.LTHUMBSTICK_X],
        "Button_A": input_vals[gamepad.BUTTON_A],
        "LBumper": input_vals[gamepad.LBUMPER],
        "RBumper": input_vals[gamepad.RBUMPER],
    }))


while True:
    update()
