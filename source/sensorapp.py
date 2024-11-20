from flask import Flask
import smbus
import subprocess
from datetime import datetime

app = Flask(__name__)

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

TEMP_REG = 0x01
LIGHT_REG_L = 0x02
LIGHT_REG_H = 0x03
STATUS_REG = 0x04
ON_BOARD_TEMP_REG = 0x05
ON_BOARD_HUMIDITY_REG = 0x06
ON_BOARD_SENSOR_ERROR = 0x07
BMP280_TEMP_REG = 0x08
BMP280_PRESSURE_REG_L = 0x09
BMP280_PRESSURE_REG_M = 0x0A
BMP280_PRESSURE_REG_H = 0x0B
BMP280_STATUS = 0x0C
HUMAN_DETECT = 0x0D




@app.route('/')
def hello_world():
    return 'OK'

def read_sensor():
    results = {}
    bus = smbus.SMBus(DEVICE_BUS)
    aReceiveBuf = []
    aReceiveBuf.append(0x00)

    # if aReceiveBuf[ON_BOARD_SENSOR_ERROR] != 0 :
    #     print("Onboard temperature and humidity sensor data may not be up to date!")

    for i in range(TEMP_REG,HUMAN_DETECT + 1):
        aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

    if aReceiveBuf[HUMAN_DETECT] == 1 :
        results['human'] = "Within 5 seconds!"
    else:
        results['human'] = "No humans detected!"

    if aReceiveBuf[STATUS_REG] & 0x01 :
        results['offboardtemp'] = "Off-chip temperature sensor overrange!"
    elif aReceiveBuf[STATUS_REG] & 0x02 :
        results['offboardtemp'] = "No external temperature sensor!"
    else :
        results['offboardtemp'] = "{} Celsius".format({aReceiveBuf[TEMP_REG]}) 

    results['onboardtemp'] = "{} Celsius".format(aReceiveBuf[ON_BOARD_TEMP_REG])
    results['humidity'] = "{} %".format(aReceiveBuf[ON_BOARD_HUMIDITY_REG])

    if aReceiveBuf[BMP280_STATUS] == 0 :
        # results['barometer'] = "Current barometer temperature = {aReceiveBuf[BMP280_TEMP_REG]} Celsius" 
        results['barometer'] = "pressure:{} Pascal | temperature = {} Celsius".format((aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16), aReceiveBuf[BMP280_TEMP_REG])
    else :
        results['barometer'] =  "Error!"

    if aReceiveBuf[STATUS_REG] & 0x04 :
        results['brightness'] = "Onboard brightness sensor overrange!"
    elif aReceiveBuf[STATUS_REG] & 0x08 :
        results['brightness'] = "Dark"
    else :
        results['brightness'] = "{} Lux".format(aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L])

    return results

@app.route('/human/')
def human_sensor():
    data = read_sensor()
    return data['human']

@app.route('/barometer/')
def barometer_sensor():
    data = read_sensor()
    return data['barometer']

@app.route('/brightness/')
def brightness_sensor():
    data = read_sensor()
    return data['brightness']

@app.route('/humidity/')
def humidity_sensor():
    data = read_sensor()
    return data['humidity']

@app.route('/temperature/')
def temperature_sensor():
    data = read_sensor()
    return data['offboardtemp']

@app.route('/onboard-temp/')
def onboard_temp():
    data = read_sensor()
    return data['offboardtemp']

@app.route('/all/')
def all_data():
    data = read_sensor()
    return data 

@app.route('/speedtest/')
def speedtest():
    data = subprocess.check_output(['/usr/bin/speedtest', '--json'])
    return data

@app.route('/time-stamp/')
def time_stamp():
    return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
