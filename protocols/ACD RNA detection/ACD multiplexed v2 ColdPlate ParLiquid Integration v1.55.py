##### START VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
## Last updated by nsamusik 7/26/2023
## GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###

from opentrons import protocol_api
import json
from collections import defaultdict
import serial
import opentrons.protocol_api
import time
#Expand below to see Global Functions
####################GENERAL SETUP###############################
volume_counter = defaultdict(int)
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.2
extra_bottom_gap=0
aspiration_gap = 0
dispensing_gap = 0


####################Global Functions Defs#########################
class Object:
    # constructor
    def __init__(self, dict1=None):
        if dict1 != None:
            self.__dict__.update(dict1)
        else:
            pass


class ColdPlateSlimDriver():
    def __init__(self, protocol_context,
                 my_device_name="/dev/ttyUSB0", max_temp_lag=15,
                 heating_rate_deg_per_min=10, cooling_rate_deg_per_min=2):
        self.serial_number = '29517'
        self.device_name = my_device_name
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.read_timeout = 2
        self.write_timeout = 2
        self.height = 45

        self.temp = 0
        self.max_temp_lag = max_temp_lag
        self.heating_rate_deg_per_min = heating_rate_deg_per_min
        self.cooling_rate_deg_per_min = cooling_rate_deg_per_min
        self.protocol = protocol_context

        # check context, skip if simulating Linux
        if protocol_context.is_simulating():
            print("simulation detected")
            print("Initializing in the dummy mode")
            self.serial_object = None
            self.max_temp_lag = 0
            self.heating_rate_deg_per_min = 1000
            self.cooling_rate_deg_per_min = 1000
        else:
            print("execution mode")
            print("Initializing in the real deal mode")
            self.serial_object = serial.Serial(
                port=self.device_name,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.read_timeout,
                write_timeout=self.write_timeout)

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
        output_string = "".join(l.decode("utf-8") for l in output_lines)
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
        interval_sec = 10
        SEC_IN_MIN = 60

        curr_temp = self.get_temp()
        self.protocol.comment(f"Setting temperature. Current temp: {curr_temp}\nTarget temp: {target_temp}")

        temp_diff = target_temp - curr_temp
        temp_lag = self.max_temp_lag * (abs(temp_diff) / 100.0)

        if temp_diff > 0:
            temp_step = self.heating_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            self.protocol.comment(f"Heating rate: {temp_step}")
        else:
            temp_step = -self.cooling_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            self.protocol.comment(f"Cooling rate: {temp_step}")

        while (abs(target_temp - curr_temp) > abs(temp_step)):
            curr_temp += temp_step
            self.set_temp(curr_temp)
            self.protocol.comment(f"Ramping the temp to: {curr_temp}")
            time.sleep(interval_sec)
            curr_temp = self.get_temp()
            self.protocol.comment(f"Actual temp: {curr_temp}")

        self.set_temp(target_temp)

        time_elapsed = 0

        while (abs(self.get_temp() - target_temp) > tolerance):
            self.protocol.comment(f"Waiting for temp to reach target: {target_temp}, actual temp: {self.get_temp()}")
            if not self.protocol.is_simulating():  # Skip delay during simulation
                time.sleep(interval_sec)
            time_elapsed += interval_sec
            if (time_elapsed > timeout_min * SEC_IN_MIN):
                raise Exception("Temperature timeout")

        self.protocol.comment(f"Target reached, equilibrating now for incubation time")
        if not self.protocol.is_simulating():  # Skip delay during simulation
            time.sleep(temp_lag * SEC_IN_MIN)
        return target_temp

    def temp_off(self):
        if self.serial_object is None:
            self.temp = 25
        else:
            self._send_command("tempOff")

class ParLiquid:
    def __init__(self, name, color, well_list, volume):
        self.name = name
        self.color = color
        if not isinstance(well_list, list):
            well_list = [well_list]
        self.wells = well_list
        self.current_well = 0  # start with the first well
        self.volume = volume
        self.volume_used = 0  # start with no volume used

    def next_well(self):
        if self.current_well < len(self.wells) - 1:
            self.current_well += 1
        else:
            raise Exception(f"Out of wells for {self.name}")

    def dispense(self, volume):
        if self.volume < volume:
            self.next_well()
            self.volume = self.wells[self.current_well].volume
        self.volume -= volume
        self.volume_used += volume  # Assuming you want to track the total volume used

    def __str__(self):
        return f"Liquid: {self.name}\tVolume: {self.volume}\tVolume Used: {self.volume_used}\tNumber of Wells: {len(self.wells)}"

def dict2obj(dict1):
    # using json.loads method and passing json.dumps
    # method and custom object hook as arguments
    return json.loads(json.dumps(dict1), object_hook=Object)

#This is just for jupyter lab runs
labware_defs = {
"parhelia_skirted_96_with_strips": """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"],"links":["https://www.parheliabio.com"]},"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.48,"zDimension":25},"wells":{"H1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":10,"z":6},"G1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":19,"z":6},"F1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":28,"z":6},"E1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":37,"z":6},"D1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":46,"z":6},"C1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":55,"z":6},"B1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":64,"z":6},"A1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":73,"z":6},"H2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":10,"z":6},"G2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":19,"z":6},"F2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":28,"z":6},"E2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":37,"z":6},"D2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":46,"z":6},"C2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":55,"z":6},"B2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":64,"z":6},"A2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":73,"z":6},"H3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":10,"z":6},"G3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":19,"z":6},"F3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":28,"z":6},"E3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":37,"z":6},"D3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":46,"z":6},"C3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":55,"z":6},"B3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":64,"z":6},"A3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":73,"z":6},"H4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":10,"z":6},"G4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":19,"z":6},"F4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":28,"z":6},"E4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":37,"z":6},"D4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":46,"z":6},"C4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":55,"z":6},"B4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":64,"z":6},"A4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":73,"z":6},"H5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":10,"z":6},"G5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":19,"z":6},"F5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":28,"z":6},"E5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":37,"z":6},"D5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":46,"z":6},"C5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":55,"z":6},"B5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":64,"z":6},"A5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":73,"z":6},"H6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":10,"z":6},"G6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":19,"z":6},"F6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":28,"z":6},"E6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":37,"z":6},"D6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":46,"z":6},"C6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":55,"z":6},"B6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":64,"z":6},"A6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":73,"z":6},"H7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":10,"z":6},"G7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":19,"z":6},"F7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":28,"z":6},"E7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":37,"z":6},"D7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":46,"z":6},"C7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":55,"z":6},"B7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":64,"z":6},"A7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":73,"z":6},"H8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":10,"z":6},"G8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":19,"z":6},"F8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":28,"z":6},"E8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":37,"z":6},"D8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":46,"z":6},"C8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":55,"z":6},"B8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":64,"z":6},"A8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":73,"z":6},"H9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":10,"z":6},"G9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":19,"z":6},"F9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":28,"z":6},"E9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":37,"z":6},"D9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":46,"z":6},"C9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":55,"z":6},"B9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":64,"z":6},"A9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":73,"z":6},"H10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":10,"z":6},"G10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":19,"z":6},"F10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":28,"z":6},"E10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":37,"z":6},"D10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":46,"z":6},"C10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":55,"z":6},"B10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":64,"z":6},"A10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":73,"z":6},"H11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":10,"z":6},"G11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":19,"z":6},"F11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":28,"z":6},"E11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":37,"z":6},"D11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":46,"z":6},"C11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":55,"z":6},"B11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":64,"z":6},"A11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":73,"z":6},"H12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":10,"z":6},"G12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":19,"z":6},"F12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":28,"z":6},"E12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":37,"z":6},"D12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":46,"z":6},"C12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":55,"z":6},"B12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":64,"z":6},"A12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":73,"z":6}},"groups":[{"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_skirted_96_with_strips"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}""",
"omni_stainer_s12_slides_with_thermosheath_on_coldplate": """{ "ordering": [["A1", "A2", "A3", "A4", "A5"], ["B1", "B2", "B3", "B4"], ["C1", "C2", "C3", "C4"], ["D1", "D2", "D3"]], "brand": { "brand": "Parhelia", "brandId": ["Omni-Stainer S12 with Thermal Sheath on ColdPlateSlim"] }, "metadata": { "displayName": "Omni-Stainer S12 (for slides) with Thermal Sheath on ColdPlate", "displayCategory": "wellPlate", "displayVolumeUnits": "µL", "tags": [] }, "dimensions": { "xDimension": 127.71, "yDimension": 85.43, "zDimension": 140 }, "wells": { "A1": { "depth": 0, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 9.8, "y": 77.7, "z": 140 }, "A2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 70.7, "z": 105.5 }, "B1": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 44.6, "z": 105.5 }, "C1": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 18.6, "z": 105.5 }, "A3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 70.7, "z": 105.5 }, "B2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 44.6, "z": 105.5 }, "C2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 18.6, "z": 105.5 }, "A4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 70.7, "z": 105.5 }, "B3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 44.6, "z": 105.5 }, "C3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 18.6, "z": 105.5 }, "A5": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 70.7, "z": 105.5 }, "B4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 44.6, "z": 105.5 }, "C4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 18.6, "z": 105.5 }, "D1": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 97.7, "z": 105.5 }, "D2": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 104.7, "z": 105.5 }, "D3": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 111.7, "z": 105.5 } }, "groups": [{ "metadata": { "displayName": "Omni-Stainer S12 (for slides) with Thermal Sheath", "displayCategory": "wellPlate", "wellBottomShape": "flat" }, "brand": { "brand": "Parhelia", "brandId": ["Omni-Stainer S12 with Thermal Sheath"] }, "wells": ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "D1", "D2", "D3"] }], "parameters": { "format": "irregular", "quirks": [], "isTiprack": false, "isMagneticModuleCompatible": false, "loadName": "omni_stainer_s12_slides_with_thermosheath_on_coldplate" }, "namespace": "custom_beta", "version": 1, "schemaVersion": 2, "cornerOffsetFromSlot": { "x": 0, "y": 0, "z": 0 } }""",
"parhelia_12trough": """{"ordering":[["A1"], ["A2"],["A3"],["A4"],["A5"],["A6"],["A7"],["A8"],["A9"],["A10"],["A11"],["A12"]],"brand":{"brand":"Parhelia","brandId":["12trough"]},"metadata":{"displayName":"Parhelia12-troughreservoir","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.8,"zDimension":44.45},"wells":{"A1":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":13.94,"y":42.9,"z":8},"A2":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":23.03,"y":42.9,"z":8},"A3":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":32.12,"y":42.9,"z":8},"A4":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":41.21,"y":42.9,"z":8},"A5":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":50.3,"y":42.9,"z":8},"A6":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":59.39,"y":42.9,"z":8},"A7":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":68.48,"y":42.9,"z":8},"A8":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":77.57,"y":42.9,"z":8},"A9":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":86.66,"y":42.9,"z":8},"A10":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":95.75,"y":42.9,"z":8},"A11":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":104.84,"y":42.9,"z":8},"A12":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":113.93,"y":42.9,"z":8}},"groups":[{"metadata":{"displayName":"Parhelia12-troughreservoir","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["12trough"]},"wells":["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_12trough"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":1,"y":-1,"z":-0.6}}""",
"parhelia_skirted_96": """{ "ordering": [ [ "A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1" ], [ "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2" ], [ "A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3" ], [ "A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4" ], [ "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5" ], [ "A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6" ], [ "A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7" ], [ "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8" ], [ "A9", "B9", "C9", "D9", "E9", "F9", "G9", "H9" ], [ "A10", "B10", "C10", "D10", "E10", "F10", "G10", "H10" ], [ "A11", "B11", "C11", "D11", "E11", "F11", "G11", "H11" ], [ "A12", "B12", "C12", "D12", "E12", "F12", "G12", "H12" ] ], "brand": { "brand": "Parhelia", "brandId": [ "Parhelia skirted 96-well plate" ], "links": [ "https://www.parheliabio.com" ] }, "metadata": { "displayName": "Parhelia skirted 96-well plate", "displayVolumeUnits": "mL", "displayCategory": "reservoir", "tags": [] }, "dimensions": { "xDimension": 127.76, "yDimension": 85.48, "zDimension": 16.06 }, "wells": { "H1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 10, "z": 1 }, "G1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 19, "z": 1 }, "F1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 28, "z": 1 }, "E1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 37, "z": 1 }, "D1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 46, "z": 1 }, "C1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 55, "z": 1 }, "B1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 64, "z": 1 }, "A1": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 14, "y": 73, "z": 1 }, "H2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 10, "z": 1 }, "G2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 19, "z": 1 }, "F2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 28, "z": 1 }, "E2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 37, "z": 1 }, "D2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 46, "z": 1 }, "C2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 55, "z": 1 }, "B2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 64, "z": 1 }, "A2": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 23, "y": 73, "z": 1 }, "H3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 10, "z": 1 }, "G3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 19, "z": 1 }, "F3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 28, "z": 1 }, "E3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 37, "z": 1 }, "D3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 46, "z": 1 }, "C3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 55, "z": 1 }, "B3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 64, "z": 1 }, "A3": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 32, "y": 73, "z": 1 }, "H4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 10, "z": 1 }, "G4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 19, "z": 1 }, "F4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 28, "z": 1 }, "E4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 37, "z": 1 }, "D4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 46, "z": 1 }, "C4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 55, "z": 1 }, "B4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 64, "z": 1 }, "A4": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 41, "y": 73, "z": 1 }, "H5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 10, "z": 1 }, "G5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 19, "z": 1 }, "F5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 28, "z": 1 }, "E5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 37, "z": 1 }, "D5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 46, "z": 1 }, "C5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 55, "z": 1 }, "B5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 64, "z": 1 }, "A5": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 50, "y": 73, "z": 1 }, "H6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 10, "z": 1 }, "G6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 19, "z": 1 }, "F6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 28, "z": 1 }, "E6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 37, "z": 1 }, "D6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 46, "z": 1 }, "C6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 55, "z": 1 }, "B6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 64, "z": 1 }, "A6": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 59, "y": 73, "z": 1 }, "H7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 10, "z": 1 }, "G7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 19, "z": 1 }, "F7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 28, "z": 1 }, "E7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 37, "z": 1 }, "D7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 46, "z": 1 }, "C7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 55, "z": 1 }, "B7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 64, "z": 1 }, "A7": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 68, "y": 73, "z": 1 }, "H8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 10, "z": 1 }, "G8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 19, "z": 1 }, "F8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 28, "z": 1 }, "E8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 37, "z": 1 }, "D8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 46, "z": 1 }, "C8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 55, "z": 1 }, "B8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 64, "z": 1 }, "A8": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 77, "y": 73, "z": 1 }, "H9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 10, "z": 1 }, "G9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 19, "z": 1 }, "F9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 28, "z": 1 }, "E9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 37, "z": 1 }, "D9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 46, "z": 1 }, "C9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 55, "z": 1 }, "B9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 64, "z": 1 }, "A9": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 86, "y": 73, "z": 1 }, "H10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 10, "z": 1 }, "G10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 19, "z": 1 }, "F10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 28, "z": 1 }, "E10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 37, "z": 1 }, "D10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 46, "z": 1 }, "C10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 55, "z": 1 }, "B10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 64, "z": 1 }, "A10": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 95, "y": 73, "z": 1 }, "H11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 10, "z": 1 }, "G11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 19, "z": 1 }, "F11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 28, "z": 1 }, "E11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 37, "z": 1 }, "D11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 46, "z": 1 }, "C11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 55, "z": 1 }, "B11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 64, "z": 1 }, "A11": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 104, "y": 73, "z": 1 }, "H12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 10, "z": 1 }, "G12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 19, "z": 1 }, "F12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 28, "z": 1 }, "E12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 37, "z": 1 }, "D12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 46, "z": 1 }, "C12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 55, "z": 1 }, "B12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 64, "z": 1 }, "A12": { "depth": 13.91, "shape": "circular", "diameter": 5.46, "totalLiquidVolume": 200, "x": 113, "y": 73, "z": 1 } }, "groups": [ { "metadata": { "displayName": "Parhelia skirted 96-well plate", "displayCategory": "wellPlate", "wellBottomShape": "v" }, "brand": { "brand": "Parhelia", "brandId": [ "Parhelia skirted 96-well plate" ] }, "wells": [ "A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3", "A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4", "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5", "A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6", "A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7", "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8", "A9", "B9", "C9", "D9", "E9", "F9", "G9", "H9", "A10", "B10", "C10", "D10", "E10", "F10", "G10", "H10", "A11", "B11", "C11", "D11", "E11", "F11", "G11", "H11", "A12", "B12", "C12", "D12", "E12", "F12", "G12", "H12" ] } ], "parameters": { "format": "irregular", "quirks": [], "isTiprack": false, "isMagneticModuleCompatible": false, "loadName": "parhelia_skirted_96" }, "namespace": "custom_beta", "version": 1, "schemaVersion": 2, "cornerOffsetFromSlot": { "x": 0, "y": 2, "z": 0.3 } } """,

}



def loadLabwareFromDict(labwareName, protocol_or_tempmodule, position=-1):
    LABWARE_DEF = json.loads(labware_defs[labwareName])

    WELLS = LABWARE_DEF['wells']

    # Check if the passed context is a TemperatureModuleContext or ColdPlateSlimDriver
    if isinstance(protocol_or_tempmodule, opentrons.protocol_api.TemperatureModuleContext) or isinstance(
            protocol_or_tempmodule, ColdPlateSlimDriver):
        labware = protocol_or_tempmodule.load_labware_from_definition(LABWARE_DEF, LABWARE_DEF.get('metadata', {}).get(
            'displayName'))
    else:
        labware = protocol_or_tempmodule.load_labware_from_definition(LABWARE_DEF, position,
                                                                      LABWARE_DEF.get('metadata', {}).get(
                                                                          'displayName'))
    return labware

#End of jupyter notebook -specific functions

def washSamples(pipette, sourceLiquid, samples, volume, num_repeats=1, height_offset=0, aspiration_offset=0, dispensing_offset=0, keep_tip=False):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    print('Samples are:')
    print(samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

    aspiration_offset += aspiration_gap
    dispensing_offset += dispensing_gap

    if isinstance(sourceLiquid, ParLiquid):
        sourceWell = sourceLiquid.wells[sourceLiquid.current_well]
    else:
        sourceWell = sourceLiquid

    for i in range(0, num_repeats):
        for sample in samples:  # iterate over samples
            if isinstance(sourceLiquid, ParLiquid):
                if sourceLiquid.volume - sourceLiquid.volume_used < volume:
                    sourceLiquid.next_well()  # update to the next well
                    sourceWell = sourceLiquid.wells[sourceLiquid.current_well]  # update the current well
                    if sourceLiquid.volume - sourceLiquid.volume_used < volume:
                        raise Exception(f"Liquid depleted: {sourceLiquid}")
                sourceLiquid.volume_used += volume
            pipette.aspirate(volume, sourceWell.bottom(height_offset + aspiration_offset), rate=well_flow_rate)
            pipette.dispense(volume, sample.bottom(height_offset + dispensing_offset), rate=sample_flow_rate)
            volume_counter[sourceLiquid] += volume

    if not keep_tip: pipette.drop_tip()

def puncture_wells(pipette, wells, height_offset=0, top_height_offset=-5, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    if not pipette.has_tip:
        pipette.pick_up_tip()
    for well in wells:
        if isinstance(well, ParLiquid):
            well = well.wells[well.current_well]  # access the current well in use by the ParLiquid
        pipette.move_to(well.top(top_height_offset))
    if not keep_tip: pipette.drop_tip()

def dilute_and_apply_fixative(pipette, sourceLiquid, diluentLiquid, samples, volume, height_offset=0, keep_tip=False):

    if not pipette.has_tip: pipette.pick_up_tip()
#    for sample in samples:  # iterate over samples

    if isinstance(sourceLiquid, ParLiquid):
        sourceWell = sourceLiquid.wells[sourceLiquid.current_well]
    else:
        sourceWell = sourceLiquid
    if isinstance(diluentLiquid, ParLiquid):
        diluentWell = diluentLiquid.wells[diluentLiquid.current_well]
    else:
        diluentWell = diluentLiquid
    if sourceLiquid.volume - sourceLiquid.volume_used < volume:
        sourceLiquid.next_well()  # update to the next well
        sourceWell = sourceLiquid.wells[sourceLiquid.current_well]  # update the current well
        if sourceLiquid.volume - sourceLiquid.volume_used < volume:
            raise Exception(f"Liquid depleted: {sourceLiquid}")
#    sourceLiquid.volume_used += volume

    # Diluting fixative:
    pipette.aspirate(volume, diluentWell.bottom(height_offset), rate=well_flow_rate)
    pipette.dispense(volume, sourceWell.bottom(height_offset), rate=well_flow_rate)
    for iterator in range(0, 3):
        pipette.aspirate(volume, sourceWell.bottom(height_offset), rate=well_flow_rate)
        pipette.dispense(volume, sourceWell.bottom(height_offset), rate=well_flow_rate)

    washSamples(pipette, sourceLiquid, samples, volume, 1, height_offset, keep_tip=keep_tip)

def getOmnistainerWellsList(omnistainer, num_samples):
    sample_chambers = []

    if (len(omnistainer.wells_by_name()) < num_samples):
        raise Exception("number of wells in the Omni-Stainer less than num_samples")

    wellslist = list(omnistainer.wells_by_name().keys())
    wellslist = wellslist[1:num_samples + 1]

    for well in wellslist:
        sample_chambers.append(omnistainer.wells_by_name()[well])

    print("omnistainer.wells_by_name are:")
    print(omnistainer.wells_by_name())
    print("sample_chambers are:")
    print(sample_chambers)
    return sample_chambers

def mix(pipette, sourceSolutionWell, volume, num_repeats):
    #mix is not compatible with ParLiquid class yet
    if not pipette.has_tip: pipette.pick_up_tip()

    for i in range(0, num_repeats):
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()

def openShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False):
    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].bottom(0), force_direct=True)
        if not keep_tip:
            pipette.drop_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].top(-10))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].top(-10), force_direct=True)
    protocol.delay(seconds=1)


def closeShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False):
    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].bottom(0), force_direct=True)
        if not keep_tip:
            pipette.drop_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].top(-10))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].top(-10), force_direct=True)
    protocol.home()
def washSamplesShutterSafe(pipette, sourceLiquid, samples, volume, num_repeats=1, height_offset=0, aspiration_offset=0, dispensing_offset=0, keep_tip=False, omnistainer=None, has_sheath=False):
    if has_sheath:
        openShutter(protocol, pipette, omnistainer)
    washSamples(pipette, sourceLiquid, samples, volume, num_repeats, height_offset, aspiration_offset, dispensing_offset, keep_tip)
    if has_sheath:
        closeShutter(protocol, pipette, omnistainer)

#################### END Global Functions Defs#########################

##### END VERAO GLOBAL #####
metadata = {
    'protocolName': 'ACD multiplexed v2 ColdPlate ParLiquid Integration v1.55',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'ACD multiplexed v2 ColdPlate ParLiquid Integration v1.55',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = "omni_stainer_s12_slides_with_thermosheath_on_coldplate"

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['black_96', 'parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96'

# The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='FFPE' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='double application of key solutions' TYPE=BOOLEAN
double_add = True

# The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='Avidin and Biotin block' TYPE=BOOLEAN
avidin_and_biotin_block = True
### VERAO VAR NAME='preblock_incubation' TYPE=BOOLEAN
preblock_incubation = True

### VERAO VAR NAME='protease treatment' TYPE=BOOLEAN
protease_treatment = True

### VERAO VAR NAME='Hybridization temperature' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
hyb_temp = 42

### VERAO VAR NAME='Room temperature' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
room_temp = 25

### VERAO VAR NAME='Temp lag for adjusting the temp' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
templag = 1  # this is set low for testing protocol sequence

### VERAO VAR NAME='Temperature Module Position, 7 highly recommended, ignore if not using temp mod' TYPE=NUMBER LBOUND=1 UBOUND=7 DECIMAL=FALSE
heatmodule_position = 3

"""If there is an S12 with thermosheath on a ColdPlate Slim, the pipette tip may impact the S12 module if it intersects the direct paths between the remaining labware and the trash"""
### VERAO VAR NAME='Deck position: Parhelia Omni-stainer / Thermosheath / ColdPlate' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
omnistainer_position = 3

### VERAO VAR NAME='labwarePositions.wash_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
wash_buffers_plate_position = 7

### VERAO VAR NAME='labwarePositions.additional_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
additional_buffers_plate_position = 1

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_1 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_1_position = 4

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_2 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_2_position = 8

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_3 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_3_position = 9

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 11

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 10

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 3

### VERAO VAR NAME='Number of RNAs for codetection' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_RNAs = 4

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='RNA_hybridization time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
hybridization_time_minutes = 2
# 600 default
### VERAO VAR NAME='RNA protocol protease incubation time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=900 DECIMAL=FALSE
protease_incubation_time = 1
# 30 default
### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 100

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 55

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
storage_temp = 4

### VERAO VAR NAME='Automated Storage Temperature Hold time (minutes)' TYPE=NUMBER LBOUND=0 UBOUND=900 DECIMAL=FALSE
storage_hold_set_time_minutes = 3

### VERAO VAR NAME='Manual Storage Hold: continue to hold at storage temp until manually stopped' TYPE=BOOLEAN
manual_storage_hold = False

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'



####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5


#####################Staining Protocol###################

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    volume_counter.clear()
    ###########################LABWARE SETUP#################################
    labwarePositions = dict2obj({
        "wash_buffers_plate": wash_buffers_plate_position,
        "additional_buffers_plate": additional_buffers_plate_position,
        "rna_reagents_plate_1": rna_reagents_plate_1_position,
        "rna_reagents_plate_2": rna_reagents_plate_2_position,
        "rna_reagents_plate_3": rna_reagents_plate_3_position,
        "tiprack_300_1": tiprack_300_1_position,
        "tiprack_300_2": tiprack_300_2_position,
        "heatmodule": heatmodule_position
    })
    protocol.home()

    if "_on_coldplate" in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol, max_temp_lag=15, heating_rate_deg_per_min=10, cooling_rate_deg_per_min=2)

    has_sheath = 'thermosheath' in omnistainer_type

    if labwarePositions.heatmodule >= 10:
        raise Exception("heat module cannot be in positions 10 or 11")
# For Jupyter Notebook run use loadLabwareFromDict() instead of protocol.load_labware()
#    omnistainer = loadLabwareFromDict(omnistainer_type, protocol, labwarePositions.heatmodule)
    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.heatmodule, 'omni-stainer')
    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1,
                                          'tiprack 300ul 1')
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_2,
                                          'tiprack 300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_300_1, tiprack_300_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos - 1]
    reservoirs = Object()
#protocol.load_labware option if needed:
    #    codex_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.codex_buffers_plate, 'codex_12-trough buffers reservoir')
    #CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate, '96-well-plate')
    reservoirs.rna_trough12 = loadLabwareFromDict('parhelia_12trough', protocol, labwarePositions.wash_buffers_plate)

    buffer_wells = reservoirs.rna_trough12.wells_by_name()

    reservoirs.RNA_reagents_96plate_1 = loadLabwareFromDict(type_of_96well_plate, protocol,
                                                            labwarePositions.rna_reagents_plate_1)
    reservoirs.RNA_reagents_96plate_2 = loadLabwareFromDict(type_of_96well_plate, protocol,
                                                            labwarePositions.rna_reagents_plate_2)
    reservoirs.RNA_reagents_96plate_3 = loadLabwareFromDict(type_of_96well_plate, protocol,
                                                            labwarePositions.rna_reagents_plate_3)
    buffer_wells = reservoirs.rna_trough12.wells()
    buffers = Object()
    HRP_wells = list(range(4))
    Substrate_wells = list(range(4))
    Tyramide_wells = list(range(4))
    HRPblocker_wells = list(range(4))

    liquids = Object()
    liquids.water = ParLiquid("water", "#aaf", buffer_wells[9], 20000)
    liquids.storage = ParLiquid("storage buffer", "#aa0", buffer_wells[11], 10000)
    liquids.RNAwash = []
    Rgnt_plate_wells_vol = ((2* ab_volume) + 10) * num_samples
    Rgnt_plate_wells_half_vol = (ab_volume + 10) * num_samples
    for i in range(num_samples):
        liquids.RNAwash.append(ParLiquid("RNAwash", "#aff", buffer_wells[i], 20000))

    #    liquids.water = ParLiquid("water", "#aaf", reservoirs.rna_trough12.wells_by_name()['A10'], 20000)
    #    liquids.storage = ParLiquid("storage buffer", "#aa0", reservoirs.rna_trough12.wells_by_name()['A12'], 10000)
    # Make ParLiquid for RNA wash, ideally daisy chained so that protocol moves on after using complete well
    #    liquids.Protease = ParLiquid("Protease", "#aaf", reservoirs.RNA_reagents_96plate_1.rows()[i], 250)
    liquids.Protease = ParLiquid("Protease", "#aaf", reservoirs.RNA_reagents_96plate_1.rows()[0], Rgnt_plate_wells_half_vol)
    liquids.ProbeDiluent = ParLiquid("ProbeDiluent", "#aba", reservoirs.RNA_reagents_96plate_1.rows()[1], Rgnt_plate_wells_half_vol)
    liquids.aviblock = ParLiquid("aviblock", "#aca", reservoirs.RNA_reagents_96plate_1.rows()[2], Rgnt_plate_wells_half_vol)
    liquids.biotinblock = ParLiquid("biotinblock", "#ada", reservoirs.RNA_reagents_96plate_1.rows()[3], Rgnt_plate_wells_half_vol)
    liquids.probe = ParLiquid("probe", "#aea", reservoirs.RNA_reagents_96plate_1.rows()[4], Rgnt_plate_wells_vol)
    liquids.amp1 = ParLiquid("amp1", "#afa", reservoirs.RNA_reagents_96plate_1.rows()[5], Rgnt_plate_wells_vol)
    liquids.amp2 = ParLiquid("amp2", "#baf", reservoirs.RNA_reagents_96plate_1.rows()[6], Rgnt_plate_wells_vol)
    liquids.amp3 = ParLiquid("amp3", "#bba", reservoirs.RNA_reagents_96plate_1.rows()[7], Rgnt_plate_wells_vol)

    liquids.HRP = [None] * 4
    liquids.HRP[0] = ParLiquid("HRP[0]", "#bca", reservoirs.RNA_reagents_96plate_2.rows()[0], Rgnt_plate_wells_vol)
    liquids.HRP[1] = ParLiquid("HRP[1]", "#bda", reservoirs.RNA_reagents_96plate_2.rows()[4], Rgnt_plate_wells_vol)
    liquids.HRP[2] = ParLiquid("HRP[2]", "#bea", reservoirs.RNA_reagents_96plate_3.rows()[0], Rgnt_plate_wells_vol)
    liquids.HRP[3] = ParLiquid("HRP[3]", "#bfa", reservoirs.RNA_reagents_96plate_3.rows()[4], Rgnt_plate_wells_vol)

    liquids.Substrate = [None] * 4
    liquids.Substrate[0] = ParLiquid("Substrate[0]", "#caa", reservoirs.RNA_reagents_96plate_2.rows()[1], Rgnt_plate_wells_vol)
    liquids.Substrate[1] = ParLiquid("Substrate[1]", "#cba", reservoirs.RNA_reagents_96plate_2.rows()[5], Rgnt_plate_wells_vol)
    liquids.Substrate[2] = ParLiquid("Substrate[2]", "#cca", reservoirs.RNA_reagents_96plate_3.rows()[1], Rgnt_plate_wells_vol)
    liquids.Substrate[3] = ParLiquid("Substrate[3]", "#cda", reservoirs.RNA_reagents_96plate_3.rows()[5], Rgnt_plate_wells_vol)

    liquids.Tyramide = [None] * 4
    liquids.Tyramide[0] = ParLiquid("Tyramide[0]", "#cea", reservoirs.RNA_reagents_96plate_2.rows()[2], 2500)
    liquids.Tyramide[1] = ParLiquid("Tyramide[1]", "#cfa", reservoirs.RNA_reagents_96plate_2.rows()[6], 2500)
    liquids.Tyramide[2] = ParLiquid("Tyramide[2]", "#daa", reservoirs.RNA_reagents_96plate_3.rows()[2], 2500)
    liquids.Tyramide[3] = ParLiquid("Tyramide[3]", "#dba", reservoirs.RNA_reagents_96plate_3.rows()[6], 2500)

    liquids.HRPblocker = [None] * 4
    liquids.HRPblocker[0] = ParLiquid("HRPblocker[0]", "#dca", reservoirs.RNA_reagents_96plate_2.rows()[3], Rgnt_plate_wells_vol)
    liquids.HRPblocker[1] = ParLiquid("HRPblocker[1]", "#dda", reservoirs.RNA_reagents_96plate_2.rows()[7], Rgnt_plate_wells_vol)
    liquids.HRPblocker[2] = ParLiquid("HRPblocker[2]", "#dea", reservoirs.RNA_reagents_96plate_3.rows()[3], Rgnt_plate_wells_vol)
    liquids.HRPblocker[3] = ParLiquid("HRPblocker[3]", "#dfa", reservoirs.RNA_reagents_96plate_3.rows()[7], Rgnt_plate_wells_vol)

    probes_and_amps = [liquids.probe, liquids.amp1, liquids.amp2, liquids.amp3]
    probes_and_amps_incubation_times = [hybridization_time_minutes, 30, 15, 30]

    keeping_the_tips = [False, True, True, True]

    comments = ["probes hyb", "amp1", "amp2", "amp3"]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

########################PROTOCOL#################

    protocol.comment("Starting the RNAscope Multiplex V2 staining protocol for samples:" + str(sample_chambers))
    protocol.home()

    if temp_mod is not None:
        temp_mod.set_temp_andWait(room_temp)
        protocol.comment(f"bringing samples to room temp: {room_temp} C")

    # PRE-HYB WASHING SAMPLES WITH water at room temperature
    protocol.comment("puncturing the water well")

    for i in range(len(sample_chambers)):
        puncture_wells(pipette_300, liquids.water, keep_tip=True)

    protocol.comment("washing with water")
    if has_sheath:
        openShutter(protocol, pipette_300, omnistainer)
    for i in range(len(sample_chambers)):
        protocol.comment(i)
        washSamples(pipette_300, liquids.water, [sample_chambers[i]], wash_volume, 2, keep_tip=True)
    if has_sheath:
        closeShutter(protocol, pipette_300, omnistainer)
    temp_mod.set_temp_andWait(hyb_temp)
    protocol.delay(minutes=templag)
#test for washSamplesShutterSafe
    protocol.comment("washing with water")
    if has_sheath:
        openShutter(protocol, pipette_300, omnistainer)
    for i in range(len(sample_chambers)):
        protocol.comment(i)
        washSamplesShutterSafe(pipette_300, liquids.water, [sample_chambers[i]], wash_volume, 2, keep_tip=True)

    temp_mod.set_temp_andWait(hyb_temp)
    protocol.delay(minutes=templag)

    # PROTEASE TREATMENT
    if protease_treatment:
        protocol.comment("puncturing protease wells")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, liquids.Protease, keep_tip=True)

        protocol.comment("applying the protease")
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, liquids.Protease, [sample_chambers[i]], ab_volume, 1, keep_tip=True)
        protocol.comment("protease incubation: 30 min")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=protease_incubation_time)

        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        washSamples(pipette_300, liquids.water, [sample_chambers[i]], wash_volume, 4, keep_tip=True)
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)

    # BLOCKING BIOTIN AND AVIDIN
    if avidin_and_biotin_block:

        temp_mod.set_temp_andWait(room_temp)
        protocol.delay(minutes=templag)

        # AVIDIN block
        protocol.comment("puncturing avi-block wells")
        puncture_wells(pipette_300, liquids.aviblock)

        protocol.comment("applying avi-block")
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)

        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, liquids.aviblock, [sample_chambers[i]], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("avi-block incubation: 15 min")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        washSamples(pipette_300, liquids.water, [sample_chambers[i]], wash_volume, 2, keep_tip=True)

        # BIOTIN block
        protocol.comment("puncturing avi-block wells")
        puncture_wells(pipette_300, liquids.biotinblock)

        protocol.comment("applying the biotin")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, liquids.biotinblock, [sample_chambers[i]], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("biotin block incubation: 15 min")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        washSamples(pipette_300, liquids.water, [sample_chambers[i]], wash_volume, 2, keep_tip=True)
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)

        temp_mod.set_temp_andWait(hyb_temp)
        protocol.delay(minutes=templag)

    # WASHING SAMPLES WITH PROBE DILUENT
    if preblock_incubation:
        protocol.comment("puncturing the probe diluent")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, liquids.ProbeDiluent, keep_tip=True)

        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)

        protocol.comment("applying the probe diluent")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, liquids.ProbeDiluent, [sample_chambers[i]], ab_volume, 1, keep_tip=True)
        protocol.comment("probe diluent incubation: 1 h")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=60)

    # Puncture Parhelia RNA WASH BUFFER
    protocol.comment("puncturing the ACD wash buffer")
    for i in range(len(sample_chambers)):
        puncture_wells(pipette_300, liquids.RNAwash, keep_tip=True)
    pipette_300.drop_tip()

    # applying probes and amps

    for z in range(4):

        protocol.home()

        protocol.comment(comments[z])
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, probes_and_amps[z], keep_tip=keeping_the_tips[z])

        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)

        if double_add:
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, probes_and_amps[z], [sample_chambers[i]], ab_volume, 1,
                            keep_tip=keeping_the_tips[z])
            protocol.delay(minutes=1)
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, probes_and_amps[z], [sample_chambers[i]], ab_volume, 1,
                        keep_tip=keeping_the_tips[z])

        protocol.comment("incubation: " + str(probes_and_amps_incubation_times[z]) + "min")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)

        protocol.delay(minutes=probes_and_amps_incubation_times[z])

        protocol.comment("washing in ACD wash buffer")
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        for wash_counter in range(4):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, liquids.RNAwash[i], [sample_chambers[i]], wash_volume, 2, keep_tip=True)

    if has_sheath:
        closeShutter(protocol, pipette_300, omnistainer)
    protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
    # HERE the final iterative branch detection starts

    protocol.comment("puncturing the storage well")
    puncture_wells(pipette_300, liquids.storage, keep_tip=True)

    for z in range(num_RNAs):
        # Filling the flow cell with storage buffer before ramping down to room temperature

        channel = z + 1

        if z > 0:  # only done in cycles 2,3 and 4

            protocol.home()
            protocol.comment("filling with storage buffer")
            if has_sheath:
                openShutter(protocol, pipette_300, omnistainer)
            washSamples(pipette_300, liquids.storage, [sample_chambers[i]], wash_volume, 2, keep_tip=True)
            if has_sheath:
                closeShutter(protocol, pipette_300, omnistainer)

            temp_mod.set_temp_andWait(hyb_temp)
            protocol.delay(minutes=templag)

            # Blocking the channel 1 HRP
            # First HRP block
            protocol.comment("puncturing HRP_block " + str(z))
            puncture_wells(pipette_300, liquids.HRPblocker[z - 1], keep_tip=True)

            if has_sheath:
                openShutter(protocol, pipette_300, omnistainer)
            protocol.comment("applying the HRP_block " + str(z))
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, liquids.HRPblocker[z - 1], [sample_chambers[i]], ab_volume, 1, keep_tip=True)
            protocol.comment("HRP_block " + str(z) + ": 5 min")
            if has_sheath:
                closeShutter(protocol, pipette_300, omnistainer)
            protocol.delay(minutes=5)

            if has_sheath:
                openShutter(protocol, pipette_300, omnistainer)
            protocol.comment("applying the HRP_block " + str(z))
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, liquids.HRPblocker[z - 1], [sample_chambers[i]], ab_volume, 1, keep_tip=True)
            protocol.comment("HRP_block " + str(z) + ": 10 min")
            if has_sheath:
                closeShutter(protocol, pipette_300, omnistainer)
            protocol.delay(minutes=10)

            # WASHING ACD WASH BUFFER
            protocol.comment("washing in ACD wash buffer")
            for wash_counter in range(3):
                if has_sheath:
                    openShutter(protocol, pipette_300, omnistainer)
                for i in range(len(sample_chambers)):
                    for i in range(len(sample_chambers)):
                        washSamples(pipette_300, liquids.RNAwash[i], [sample_chambers[i]], wash_volume, 2,
                                    keep_tip=True)
                if has_sheath:
                    closeShutter(protocol, pipette_300, omnistainer)
                protocol.delay(minutes=1, msg="incubation in ACD wash buffer")

        protocol.comment("puncturing HRP channel " + str(channel) + " wells")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, liquids.HRP[z], keep_tip=True)

        protocol.comment("applying the HRP channel " + str(channel))
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        if double_add:
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, liquids.HRP[z], [sample_chambers[i]], ab_volume, 1)
            protocol.delay(minutes=1)
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, liquids.HRP[z], [sample_chambers[i]], ab_volume, 1)
        protocol.comment("HRP channel " + str(channel) + " incubation: 15 min")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        # WASHING ACD WASH BUFFER
        protocol.comment("washing in ACD wash buffer")
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        for wash_counter in range(4):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, liquids.RNAwash[i], [sample_chambers[i]], wash_volume, 2, keep_tip=True)

        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=4, msg="incubation in ACD wash buffer")

        temp_mod.set_temp_andWait(room_temp)
        protocol.delay(minutes=templag)

        # DILUTING AND APPLYING THE Ch1 tyramide
        protocol.comment("puncturing the Ch" + str(channel) + " tyramide")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, liquids.Tyramide[z], keep_tip=True)

        protocol.comment("puncturing the substrate buffer wells")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, liquids.Substrate[z], keep_tip=True)

        protocol.comment("applying the Ch" + str(channel) + " tyramide")
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            dilute_and_apply_fixative(pipette_300, liquids.Tyramide[z], liquids.Substrate[z],[sample_chambers[i]], 2 * ab_volume)
        if double_add:
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, liquids.Tyramide[z], [sample_chambers[i]], ab_volume, 1, keep_tip=True)
            protocol.delay(minutes=1)
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, liquids.Tyramide[z], [sample_chambers[i]], ab_volume, 1, keep_tip=True)
        protocol.comment("developing Ch" + str(z) + " tyramide")
        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        protocol.comment("washing in ACD wash buffer")
        if has_sheath:
            openShutter(protocol, pipette_300, omnistainer)
        for wash_counter in range(3):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, liquids.RNAwash[i], [sample_chambers[i]], wash_volume, 2, keep_tip=True)

        if has_sheath:
            closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=1, msg="incubation in ACD wash buffer")

    temp_mod.set_temp_andWait(room_temp)

    protocol.comment("Printing reagent usage stats")
    for key in volume_counter.keys():
        protocol.comment(str(key) + "\t" + str(volume_counter[key]))
# Storage
    if temp_mod is not None:
        protocol.comment(f"Holding at storage temp: {storage_temp} C for {storage_hold_set_time_minutes} min")
        protocol.delay(minutes=storage_hold_set_time_minutes, msg="preset automated storage mode")
        if manual_storage_hold:
            protocol.pause(msg=f"The protocol is paused in storage mode: {storage_temp} C")

    temp_mod.temp_off()
    protocol.comment(f"temp off - protocol complete")
########Comments########