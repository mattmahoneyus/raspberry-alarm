#!/usr/bin/env python

import time
import math
import subprocess
import gpiozero
from twilio.rest import Client
from datetime import datetime
from argparse import ArgumentParser

sendText = None
takePicture = None
debug = None
ledOn = None
switchEnabled = None
emailPicture = None
numberOfPictures = 3
pictureDir = "/home/pi/Pictures"

currentTime = time.time()

# Pin definitions
led = gpiozero.LED(24)
sensor1 = gpiozero.MotionSensor(22)
sensor2 = gpiozero.MotionSensor(23)
switch1 = gpiozero.LED(17)
 
def exec_cmd(cmd):
    print "Cmd: {}".format(cmd)
    p = subprocess.Popen("/bin/bash", shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(cmd)
    stdout, stderr = p.communicate()
    return stdout, stderr

def sendTextMessage(sendText, msg):
    account_sid = "<your-account-sid>"
    auth_token = "<your-auth-token>"
    client = Client(account_sid, auth_token)

    if sendText:
        try:
          print "***Sending Text: {}".format(msg)
          message = client.api.account.messages.create(
                    to="<your-cell-number>",
                    from_="<your-twilio-number>",
                    body=msg)
        except Exception as ex:
          print(ex)

    else:
        print "*** Text NOT Sent: {}".format(msg)

def takeAPicture(takePicture, dir):
    if (takePicture):
        try:
          for p in range(numberOfPictures):
	    file = "{}/motion-{}.jpg".format(dir, datetime.now().isoformat())
            cmd = "raspistill -rot -hf -ex night -sh 100 -o {}".format(file)
            exec_cmd(cmd)
            print "Image file: {}".format(file)

            if (emailPicture):
                sendPicture(file)

        except Exception as ex:
          print (ex)
    else:
        print "Image NOT taken."
	
	
# Switch: On  == LED.off #         Off == LED.on
def switchOnOff(switch, enabled, on=False):
    if enabled:
	if on:
            print "Turn switch on"
            switch.off()
            return True
        else:
            print "Turn switch off"
            switch.on()
            return False

def sendPicture(imageToSend):
    import os
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.mime.image import MIMEImage

    gmailUser = '<your-email@gmail.com>'
    gmailPassword = '<your-password>'
    recipient = '<your-email-recipient>'
    message='<Your Message>'

    msg = MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = 'Your Subject'
    msg.attach(MIMEText(message))
    img_data = open(imageToSend, 'rb').read()
    image = MIMEImage(img_data, name=os.path.basename(imageToSend))
    msg.attach(image)

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    print "Sending Picture: {}".format(imageToSend)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()


## Main

parser = ArgumentParser()
parser.add_argument("-t", "--text", action="store_true", dest="sendText", default=False, help="Send text")
parser.add_argument("-p", "--picture", action="store_true", dest="takePicture", default=False, help="Take picture")
parser.add_argument("-d", "--debug", action="store_true", dest="debug", default=False, help="Debug mode - No Delays")
parser.add_argument("-l", "--led", action="store_true", dest="ledOn", default=False, help="Turn on LED")
parser.add_argument("-s", "--switch", action="store_true", dest="switchEnabled", default=False, help="Enable Switch")
parser.add_argument("-e", "--email", action="store_true", dest="emailPicture", default=False, help="Email picture")

sendText = parser.parse_args().sendText
takePicture = parser.parse_args().takePicture
debug = parser.parse_args().debug
ledOn = parser.parse_args().ledOn
switchEnabled = parser.parse_args().switchEnabled
emailPicture = parser.parse_args().emailPicture

if debug:
    print "sendText: {}".format(sendText)
    print "takePicture: {}".format(takePicture)
    print "debug: {}".format(debug)
    print "ledOn: {}".format(ledOn)
    print "switchEnabled: {}".format(switchEnabled)
    print "emailPicture: {}".format(emailPicture)

startDelay = 0 if debug else 30
textDelay = 0 if debug else (60 * 15)
switchIsOn = switchOnOff(switch1, True, on=False)

print "Start delay: {}".format(time.ctime())
time.sleep(startDelay)
print "Begin sensor: {}".format(time.ctime())

try:
    while True:
      if sensor1.motion_detected or sensor2.motion_detected:
          motion = ""
          if sensor1.motion_detected:
              motion = "Motion-1"
          if sensor2.motion_detected:
              motion = "{} Motion-2".format(motion)
  
          print "{} detected {}".format(motion, time.ctime())

          if ledOn:
            led.on()

          switchIsOn = switchOnOff(switch1, switchEnabled, on=True)

   	  elapsedTime = math.ceil(time.time() - currentTime)
          #print "tDelay: {}   eTIme: {}".format(textDelay,elapsedTime)
          if elapsedTime > textDelay:
            sendTextMessage(sendText, "{} tripped. Time: {}".format(motion, time.ctime()))
            takeAPicture(takePicture, pictureDir)
            currentTime = time.time()
          #else:
	    #print "Time before sending a text: {}".format(textDelay-elapsedTime)
      else:
        if ledOn:
	  led.off()
        if switchEnabled and switchIsOn:
          switchIsOn = switchOnOff(switch1, switchEnabled, on=False)
          
      time.sleep(3)

except KeyboardInterrupt:
    print "Keyboard interrupt"
  
finally:  
    print "In Finally"
    switchIsOn = switchOnOff(switch1, switchEnabled, on=False)

