

```python
## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
### GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###
from opentrons import protocol_api
import json
from collections import defaultdict
import serial
import platform

metadata = {
    'protocolName': 'ColdPlate Test',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'ColdPlate Test Fri21',
    'apiLevel': '2.13'
}

class ColdPlateSlimDriver():

    def __init__(self, protocol_context, my_device_name="/dev/ttyUSB0", max_temp_lag=15, heating_rate_deg_per_min=10,
                 cooling_rate_deg_per_min=2):
        # Default ColdPlate device name is /dev/ttyUSB0
        # If multiple ColdPlates are connected, you will need to find which
        # device uses which device file (ttyUSB0, ttyUSB1...)
        # (See "serial-device/ttyusb_devices.py")
        DEVICE_NAME = my_device_name

        # Specified in the QInstruments documentation
        BAUDRATE = 9600
        BYTESIZE = serial.EIGHTBITS
        PARITY = serial.PARITY_NONE
        STOPBITS = serial.STOPBITS_ONE

        # Optional timeouts in seconds
        READ_TIMEOUT = 2
        WRITE_TIMEOUT = 2

        self.temp = 0
        self.max_temp_lag = max_temp_lag
        self.heating_rate_deg_per_min = heating_rate_deg_per_min
        self.cooling_rate_deg_per_min = cooling_rate_deg_per_min
        self.protocol = protocol_context

        # check OS type, skip the init if != Linux
        if platform.system() != "Linux":
            print("Non-linux system detected: " + platform.system())
            print("Initializing in the dummy mode")
            self.serial_object = None
            self.max_temp_lag = 0
            self.heating_rate_deg_per_min = 1000
            self.cooling_rate_deg_per_min = 1000
        else:
            print("Linux system detected: " + platform.system())
            print("Initializing in the real deal mode")
            self.serial_object = serial.Serial(
                port=DEVICE_NAME,
                baudrate=BAUDRATE,
                bytesize=BYTESIZE,
                parity=PARITY,
                stopbits=STOPBITS,
                timeout=READ_TIMEOUT,
                write_timeout=WRITE_TIMEOUT)

    def _reset_buffers(self):
        """
        Worker function
        """
        if self.serial_object is None:
            return

        self.serial_object.reset_input_buffer()
        self.serial_object.reset_output_buffer()

    def _read_response(self):
        """
        Worker function
        """
        if self.serial_object is None:
            return ("dummy response")

        output_lines = self.serial_object.readlines()
        output_string = ""

        for l in output_lines:
            output_string += l.decode("utf-8")
        return output_string

    def _send_command(self, my_command):
        """
        Worker function
        """
        SERIAL_ACK = "\r\n"

        command = my_command
        command += SERIAL_ACK

        if self.serial_object is None:
            print("sending dummy command: " + my_command)
            return

        self.serial_object.write(command.encode())
        self.serial_object.flush()
        return (self._read_response())

    def get_info(self):
        if self.serial_object is None:
            return "dummy info"
        return self._send_command("info")

    def get_temp(self):
        if self.serial_object is None:
            return self.temp
        t = self._send_command("getTempActual")
        return float(t)

    def set_temp(self, my_temp):
        if self.serial_object is None:
            self.temp = my_temp
            return

        temp = float(my_temp) * 10
        temp = int(temp)
        self._send_command(f'setTempTarget{temp:03}')
        self._send_command("tempOn")
        return

    def set_temp_andWait(self, target_temp, timeout_min=30, tolerance=0.5):
        interval_sec = float(10)
        
        SEC_IN_MIN = 60

        curr_temp = self.get_temp()

        print("current temp: " + str(curr_temp))
        print("target temp:" + str(target_temp))

        temp_diff = target_temp - curr_temp

        temp_lag = self.max_temp_lag * (abs(temp_diff) / 100.0)

        if temp_diff > 0:
            temp_step = self.heating_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            print("heating rate: " + str(temp_step))
        else:
            temp_step = -self.cooling_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            print("cooling rate: " + str(temp_step))

        curr_temp = self.get_temp()

        i = curr_temp

        while (abs(target_temp - i) > abs(temp_step)):
            i += temp_step
            self.set_temp(i)
            print("ramping the temp to: " + str(i))
            self.protocol.delay(seconds=interval_sec)
            print("actual temp: " + str(self.get_temp()))

        response = self.set_temp(target_temp)

        time_elapsed = 0

        while (abs(self.get_temp() - target_temp) > tolerance):
            print("waiting for temp to reach target: " + str(target_temp) + ", actual temp: " + str(self.get_temp()))
            self.protocol.delay(seconds=interval_sec)
            time_elapsed += interval_sec
            if (time_elapsed > timeout_min * 60):
                raise Exception("temperature timeout")

        print("target reached, equilibrating minutes:" + str(temp_lag))
        self.protocol.delay(seconds=temp_lag * SEC_IN_MIN)
        return response

    def temp_off(self):
        if self.serial_object is None:
            self.temp = 25
            return
        self._send_command("tempOff")


def run(protocol: protocol_api.ProtocolContext):

#    protocol.home()
    
    print("init coldplate driver")
    

    temp_mod = ColdPlateSlimDriver(protocol)
    # End of move post test

    temp_mod.set_temp_andWait(99)

    print("actual temperature:" + str(temp_mod.get_temp()))

    temp_mod.set_temp_andWait(4)

    print("actual temperature:" + str(temp_mod.get_temp()))

    temp_mod.temp_off()

```


```python
import sys

sys.path.append('/var/lib/jupyter/notebooks')

from opentrons import protocol_api

import opentrons.execute
import opentrons.simulate

# import opentrons.simulate if you want to simulate the protocol first

# This is where you establish the API version for executing a protocol
protocol = opentrons.simulate.get_protocol_api('2.13')

run(protocol)
```

    WARNING:opentrons.config.robot_configs:/data/deck_calibration.json not found. Loading defaults


    init coldplate driver
    Non-linux system detected: Linux
    Initializing in the dummy mode
    current temp: 0
    target temp:99
    heating rate: 166.66666666666666
    target reached, equilibrating minutes:0.0
    actual temperature:99
    current temp: 99
    target temp:4
    cooling rate: -166.66666666666666
    target reached, equilibrating minutes:0.0
    actual temperature:4



```python
print(temp_mod.get_temp())
```

    3.978



```python

```
