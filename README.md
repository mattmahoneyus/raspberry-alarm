# Raspberry Pi 3 Alarm Fun Project
Fun project for learning Raspberry Pi 3 gpiozero and other interesting Python modules such as texting, taking pictures, and emailing
There a pleanty of project examples on the web to learn the gpiozero wire-ups.

Try it. Make it better!

## Environment Setup

* Dependencies
    *  `python 2.7`

```sh
# Clone this repository
$ git clone https://github.com/mattmahoneyus/raspberry-alarm.git
$ cd raspberry-alarm

# Install requirements
$ pip install -r requirements.txt

# Run
$./alarm.py --help
usage: alarm.py [-h] [-t] [-p] [-d] [-l] [-s] [-e]

optional arguments:
  -h, --help     show this help message and exit
  -t, --text     Send text
  -p, --picture  Take picture
  -d, --debug    Debug mode - No Delays
  -l, --led      Turn on LED
  -s, --switch   Enable Switch
  -e, --email    Email picture
```
