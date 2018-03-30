import socket
import json
import threading
import time
import RPi.GPIO as GPIO

AN2 = 13				# set pwm2 pin on MD10-Hat
AN1 = 12				# set pwm1 pin on MD10-hat
DIG2 = 24				# set dir2 pin on MD10-Hat
DIG1 = 26				# set dir1 pin on MD10-Hat)


class CytronBoard(object):
    def __init__(self):

        GPIO.setmode(GPIO.BCM)  # GPIO numbering
        GPIO.setwarnings(False)  # enable warning from GPIO
        GPIO.setup(AN2, GPIO.OUT)  # set pin as output
        GPIO.setup(AN1, GPIO.OUT)  # set pin as output
        GPIO.setup(DIG2, GPIO.OUT)  # set pin as output
        GPIO.setup(DIG1, GPIO.OUT)  # set pin as output

        time.sleep(1)  # delay for 1 seconds

        self.p1 = GPIO.PWM(AN1, 100)  # set pwm for M1
        self.p2 = GPIO.PWM(AN2, 100)  # set pwm for M2

    def m1(self, speed):
        if speed <= 0:
            GPIO.output(DIG1, GPIO.LOW)  # set DIG1 as LOW, to control direction
            speed = -speed
        else:
            GPIO.output(DIG1, GPIO.HIGH)  # set DIG1 as HIGH, to control direction
        if speed > 100:
            speed = 100  # make sure we dont over do it!
        self.p1.start(speed)

    def m2(self, speed):
        if speed <= 0:
            GPIO.output(DIG2, GPIO.LOW)  # set DIG2 as LOW, to control direction
            speed = -speed
        else:
            GPIO.output(DIG2, GPIO.HIGH)  # set DIG2 as HIGH, to control direction
        if speed > 100:
            speed = 100  # make sure we dont over do it!
        self.p2.start(speed)


CB = CytronBoard()
arm = RobotArm()

host = ""
port = 4096

s = socket.socket()
s.bind((host, port))

motor_power = [0, 0]

left_thumbstick_y = 0
left_thumbstick_x = 0
left_bumper = 0
right_bumper = 0
button_a = 0


def control_motor():
    while True:
        CB.m1(int(left_thumbstick_y * 50 + left_thumbstick_x * 35))  # left
        CB.m2(int(left_thumbstick_y * 50 - left_thumbstick_x * 35))  # right

        # -- Theoretical stuff, if you get the other bits working on PacBot --

        # if left_bumper == 1 and right_bumper == 0:
        #     arm.set(up)
        # elif right_bumper == 0 and right_bumper == 1:
        #     arm.set(down)
        # if button_a == 1:
        #     arm.suck(on)
        # elif button_a == 0:
        #     arm.suck(off)

        print "Thumb at {0}".format(int(left_thumbstick_y))
        print "Motors at {0}".format(int(-left_thumbstick_y * 100))

        time.sleep(0.1)


while True:
    try:
        motor_control_thread = threading.Thread(target=control_motor)
        motor_control_thread.start()

        while True:
            print "Listening for connection..."
            s.listen(1)  # 1 connection at a time

            conn, addr = s.accept()

            print "Connection from " + addr[0] + ":" + str(addr[1]) + "."

            while True:
                try:
                    data = conn.recv(1024)

                    if not data:  # connection closed
                        break

                    json_data = str(data)
                    print "Data is as follows: {0} :Data end".format(json_data)
                    data = json.loads(json_data)

                    left_thumbstick_y = data["LThumbstick_Y"]
                    left_thumbstick_x = data["LThumbstick_X"]
                    left_bumper = data["LBumper"]
                    right_bumper = data["RBumper"]
                    button_a = data["Button_A"]

                    print data
                except socket.error, msg:
                    print "Socket Error: " + msg[1]
                    break

    except:  # it hurts me to do this
        pass

    finally:  # kill the connection, and stop PacBot going haywire
        conn.close()
        CB.m1(0)
        CB.m2(0)
