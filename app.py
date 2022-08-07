from flask import Flask, render_template
import os
import glob
import time
import RPi.GPIO as GPIO
import threading
from temperature import t

RELAY_1_GPIO = 17

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


app = Flask(__name__)


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c  # , temp_f


def setup():
    GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
    GPIO.setup(RELAY_1_GPIO, GPIO.OUT) # GPIO Assign mode
    with open('temperature.txt') as f:
        f_buffer = f.read()
        t.desired_temperature = float(f_buffer)


def monitoring_loop():
    while True:
        average_temperature = 0.0
        for i in range(5):
            average_temperature += read_temp()
            time.sleep(1)
        t.temperature = average_temperature / 5.0
        if t.temperature + t.offset > t.desired_temperature:
            GPIO.output(RELAY_1_GPIO, GPIO.HIGH)  # On
            t.fridge_state = 1
            t.offset = 0.1
        else:
            GPIO.output(RELAY_1_GPIO, GPIO.LOW)  # Off
            t.fridge_state = 0
            t.offset = -0.1
        with open("temperatures_recording.csv", "a") as f:
            f.write("%s,%s,%s,%s\n" % (t.temperature, t.offset, t.desired_temperature, t.fridge_state))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_temperature')
def get_temperature():
    return "%.1f" % t.temperature


@app.route('/set_desired_temperature/<value>')
def set_desired_temperature(value):
    t.desired_temperature = float(value)
    with open('temperature.txt', 'w') as f:
        f.write("%f" % t.desired_temperature)
    return value


@app.route('/get_desired_temperature')
def get_desired_temperature():
    return "%s" % t.desired_temperature


@app.route('/get_fridge_state')
def get_fridge_state():
    return "Ανοιχτό" if t.fridge_state else "Κλειστό"


if __name__ == '__main__':
    setup()
    threading.Thread(target=monitoring_loop).start()
    app.run(debug=False, host='192.168.1.7', threaded=True)
