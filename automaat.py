#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gpiozero import LED

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import sys
import threading
import traceback
import random
import datetime
import MySQLdb

leds={
    "led_right_red":13,     #33
    "led_right_green":19,   #35
    "led_left_red":26,    #37
    "led_left_green":12,  #32
    "led_up_red":5,        #29
    "led_up_green":6       #31
    }  

butt={
    "button_green":16,     #36
    "button_red":20,       #38
    "button_blue":21      #40
    }

switch={
    "switch_red":27,       #13
    "switch_blue":22      #15
}

servo_red=23        #16
servo_blue=24       #18

servo_red_lock=4        #7
servo_blue_lock=3       #5

rfid_sda=8          #24  SPIO_CE0_N
rfid_sck=11         #23 SPIO_SCLK
rfid_mosi=10        #19 SPIO_MOSI
rfid_miso=9         #21 SPIO_MISO
rfid_rst=25         #22

allowed_orders=[]

blue_available=False
red_available=False


last_luck=datetime.datetime.now()
#How often green luck button can be pressed.
luck_interval=15
#What is the chance of winning.
luck_chance=100
 
last_order=datetime.datetime.now()
#Set timeout to forget an order if no choice is made
order_timeout=1

while True:
    try:
        db = MySQLdb.connect(host="127.0.0.1",  # your host 
                        user="identity",       # username
                        port=3306,
                        passwd="ChangeMe",     # password
                        db="identity")   # name of the database
        break
    except Exception, e:
        print e
        traceback.print_exc()
        sys.stdout.flush()
        time.sleep(5)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Initialize LED-s
class LEDplus():
    def __init__(self,pinnumber):
        self.led = LED(pinnumber)
        self.__loop = True
        self.operation = 'off'
        self.__threading = threading.Thread(target=self.__blink)
    def on(self,):
        self.operation = 'on'
        self.__loop = False
        self.maybejoin()
        self.led.on()
    def off(self, ):
        self.operation = 'off'
        self.__loop = False
        self.maybejoin()
        self.led.off()
    def close(self, ):
        self.operation = 'off'
        self.__loop = False
        self.maybejoin()
        self.led.off()
        self.led.close()
    def close(self,):
        self.operation = 'off'
        self.__loop = False
        self.maybejoin()
        self.led.off()
        self.led.close()
    def maybejoin(self,):
        if self.__threading.isAlive():
            self.__threading.join()
    def blink(self, pitch):
        if self.operation != 'blink-%s'%pitch:
            self.__loop = False
            if self.operation != 'on' and self.operation != 'off':
                last_pitch=self.operation.split('-')[1]
                time.sleep(float(last_pitch)+0.1)
            self.operation = 'blink-%s'%pitch
            self.__loop = False
            self.maybejoin()
            self.__threading = threading.Thread(target=self.__blink, args=(pitch, ))
            self.__threading.start()
    def __blink(self, pitch=2):
        self.__loop = True
        while self.__loop:
            self.led.toggle()
            time.sleep(pitch)
        self.led.off()

l={}
for n in sorted(leds.keys()):
    l[n]=LEDplus(leds[n])
    l[n].on()

#Initialize Servos
def servo(gpio, pos):
    p = GPIO.PWM(gpio, 50)
    p.start(pos)
    time.sleep(0.4)
    p.stop()

def setup_servo(name, gpio):
    print "Servo setup %s GPIO %s"%(name,gpio)
    GPIO.setup(gpio, GPIO.OUT)

setup_servo('blue', servo_blue)
setup_servo('red', servo_red)
setup_servo('blue_lock', servo_blue_lock)
setup_servo('red_lock', servo_red_lock)
servo(servo_blue, 11)
servo(servo_blue_lock, 2)
servo(servo_red, 11)
servo(servo_red_lock, 12)

l['led_right_red'].off()

#Initialize Can Switches

def setup_switch(name, gpio):
    GPIO.setup(gpio,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print "Configured Can Switch %s GPIO %s"%(name,gpio)
    GPIO.add_event_detect(gpio, GPIO.RISING)

for n in sorted(switch.keys()):
    setup_switch(n,switch[n])


l['led_left_red'].off()


#BUTTON tests
def setup_button(name, gpio):
    GPIO.setup(gpio,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print "Configured Button %s GPIO %s"%(name,gpio)
    GPIO.add_event_detect(gpio, GPIO.RISING, bouncetime=50)

for n in sorted(butt.keys()):
    setup_button(n,butt[n])



reader = SimpleMFRC522()
cur = db.cursor()

intervals=0

while True:
  if intervals > 36000:
    intervals=0
    try:
        db.ping(True)
    except Exception, e:
        pass
  else:
    intervals+=1
  try:
    #Check if order has timed out.
    if len(allowed_orders) > 0:
        if last_order + datetime.timedelta(minutes = order_timeout) < datetime.datetime.now():
            order=allowed_orders.pop()
            print "Order time out. %s"%order
    
    #Red detection
    if GPIO.input(switch['switch_red']):
            red_available=False            #Turn RED led on when we have no cans
            l['led_right_green'].off()
            l['led_right_red'].on()
    else:
            red_available=True
            l['led_right_red'].off()
            if len(allowed_orders) == 0:
                l['led_right_green'].on()        #Turn on GREEN when we have cans in the the machine
            else:
                l['led_right_green'].blink(0.1)   #Blink GREEN when we have orders waiting
    #Blue detection
    time.sleep(0.1)
    if GPIO.input(switch['switch_blue']):
            blue_available=False
            l['led_left_green'].off()
            l['led_left_red'].on()
    else:
            blue_available=True
            l['led_left_red'].off()
            if len(allowed_orders) == 0:
                l['led_left_green'].on()
            else:
                l['led_left_green'].blink(0.1)
    #Can we accept orders 
    if blue_available or red_available:
        if len(allowed_orders) > 0:
            l['led_up_red'].off()
            l['led_up_green'].off()
        else:
            l['led_up_red'].off()
            if last_luck + datetime.timedelta(minutes = luck_interval) > datetime.datetime.now():
                l['led_up_green'].blink(1)
            else:
                l['led_up_green'].blink(0.1)
    else:
        l['led_up_red'].on()
        l['led_up_green'].off()
        print "Out of cans"
        time.sleep(30)
    #if GPIO.event_detected(switch['switch_red']):
    #    print('Red can released')
    #if GPIO.event_detected(switch['switch_blue']):
    #    print('Blue can released')
    if GPIO.event_detected(butt["button_red"]):
      if not GPIO.input(butt["button_red"]):
        print "Red is the chosen one"
        if red_available:
            if len(allowed_orders) > 0:
                order=allowed_orders.pop()
                print "Completing order %s"%order
                sys.stdout.flush()
                if order != 'JACKPOT':
                    cur.execute("UPDATE users SET credit=credit-1,lastscan=NOW() WHERE rfid='%s'"%order)
                cur.execute("INSERT INTO orders SET aeg=NOW(),rfid='%s',slot='red'"%order)
                db.commit()
                GPIO.event_detected(switch['switch_red'])
                sys.stdout.flush()
                servo(servo_red_lock, 7)
                servo(servo_red, 3)
                time.sleep(0.1)
                servo(servo_red, 11)
                servo(servo_red_lock, 12)
                if GPIO.event_detected(switch['switch_red']):
                  print "Red can release detected!"
        else:
            print "No cans available in red!"
        GPIO.event_detected(butt["button_red"])
    if GPIO.event_detected(butt["button_blue"]):
      if not GPIO.input(butt["button_blue"]):
        print "Blue is the chosen one"
        if blue_available:
            if len(allowed_orders) > 0:
                order=allowed_orders.pop()
                print "Completing order %s"%order
                sys.stdout.flush()
                if order != 'JACKPOT':
                    cur.execute("UPDATE users SET credit=credit-1,lastscan=NOW() WHERE rfid='%s'"%order)
                cur.execute("INSERT INTO orders SET aeg=NOW(),rfid='%s',slot='blue'"%order)
                db.commit()
                GPIO.event_detected(switch['switch_blue'])
                sys.stdout.flush()
                servo(servo_blue_lock, 5.5)
                servo(servo_blue, 3)
                time.sleep(0.1)
                servo(servo_blue, 11)
                servo(servo_blue_lock, 2)
                if GPIO.event_detected(switch['switch_blue']):
                  print "Blue can release detected!"
        else:
            print "No cans available in blue!"
        GPIO.event_detected(butt["button_blue"])
    if GPIO.event_detected(butt["button_green"]):
      if not GPIO.input(butt["button_green"]):
        print "I am green"
        if blue_available or red_available:
            if len(allowed_orders) == 0:
                if last_luck + datetime.timedelta(minutes = luck_interval) < datetime.datetime.now():
                    last_luck=datetime.datetime.now()
                    luck=random.randint(1,luck_chance)
                    print "Your lucky number is %s!"%luck
                    if luck == 1:
                        print "Adding order!"
                        l['led_up_green'].blink(0.1)
                        time.sleep(0.1)
                        l['led_up_red'].blink(0.1)
                        time.sleep(0.1)
                        l['led_left_green'].blink(0.1)
                        l['led_left_red'].blink(0.1)
                        time.sleep(0.1)
                        l['led_right_green'].blink(0.1)
                        l['led_right_red'].blink(0.1)
                        allowed_orders.append('JACKPOT')
                        last_order=datetime.datetime.now()
                        time.sleep(1)
                    else:
                        print "Shit luck!"
                        l['led_up_green'].off()
                        l['led_up_red'].blink(0.1)
                        time.sleep(0.5)
                else:
                    print "You can't get lucky too often!"
        else:
          print "Not possible to give out order"
        GPIO.event_detected(butt["button_green"])
    id, test = reader.read_no_block()
    if id != None:
        print "RFID %s"%id
        if blue_available or red_available:
            if len(allowed_orders) == 0:
                cur.execute("SELECT rfid,credit FROM users WHERE rfid=%s"%id)
                if cur.rowcount > 0:
                    row=cur.fetchone()
                    if row[1] > 0:
                        print "Adding order!"
                        cur.execute("UPDATE users SET lastscan=NOW() WHERE rfid='%s'"%id)
                        db.commit()
                        allowed_orders.append(id)
                        last_order=datetime.datetime.now()
                        l['led_up_green'].blink(0.1)
                        time.sleep(0.5)
                    else:
                        print "Not enough credit!"
                        cur.execute("UPDATE users SET lastscan=NOW() WHERE rfid='%s'"%id)
                        db.commit()
                        l['led_up_green'].off()
                        l['led_up_red'].blink(0.1)
                        time.sleep(1)
                elif cur.rowcount == 0:
                        cur.execute("INSERT INTO users SET rfid='%s', lastscan=NOW()"%id)
                        db.commit()
                        print "Registered new RFID!"
                        l['led_up_green'].off()
                        l['led_up_red'].blink(0.1)
                        time.sleep(1)
            else:
                time.sleep(1)
        else:
          print "Not possible to give out order"
    sys.stdout.flush()
  except (KeyboardInterrupt, SystemExit):
    print 'Caught exit signal, killing children ;-)'
    sys.stdout.flush()
    for name,led in l.iteritems():
      led.close()
    sys.stdout.flush()
    break;
  except (AttributeError, MySQLdb.OperationalError):
      try:
          db.ping(True)
      except Exception, e:
          print e
          traceback.print_exc()
          sys.stdout.flush()
          pass
      print "MySQL connection error."
      sys.stdout.flush()
      l['led_up_green'].off()
      l['led_left_green'].off()
      l['led_right_green'].off()
      l['led_up_red'].blink(0.3)
      time.sleep(3)
  except Exception, e:
      print e
      traceback.print_exc()
      sys.stdout.flush()
      time.sleep(0.2)
      pass

for n in sorted(butt.keys()):
    GPIO.cleanup(butt[n])
for n in sorted(switch.keys()):
    GPIO.cleanup(switch[n])

GPIO.cleanup(servo_red)
GPIO.cleanup(servo_blue)
GPIO.cleanup(servo_red_lock)
GPIO.cleanup(servo_blue_lock)
GPIO.cleanup(rfid_rst)
print "GPIO cleanup complete"
