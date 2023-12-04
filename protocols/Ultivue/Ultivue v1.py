## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
## Last updated by nwedin 9/21/2023
### GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###

from opentrons import protocol_api
import json
from collections import defaultdict
import serial
import opentrons.protocol_api
import time

####################GENERAL SETUP###############################
volume_counter = defaultdict(int)
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 1
sample_flow_rate = 0.2
aspiration_gap = 0
dispensing_gap = 0
extra_bottom_gap = 0

testmode = False


class Object:
    # constructor
    def __init__(self, dict1=None):
        if dict1 != None:
            self.__dict__.update(dict1)
        else:
            pass


class ColdPlateSlimDriver:
    def __init__(
            self,
            protocol_context,
            temp_mod_number=0,
            max_temp_lag=0,
            heating_rate_deg_per_min=100,
            cooling_rate_deg_per_min=100,
    ):
        self.serial_number = "29517"
        self.device_name = "/dev/ttyUSB" + str(temp_mod_number)
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.read_timeout = 2
        self.write_timeout = 2
        self.height = 45

        self.temp = 0
        self.max_temp_lag = max_temp_lag
        self.heating_rate_deg_per_amin = heating_rate_deg_per_min
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
                write_timeout=self.write_timeout,
            )

    @property
    def temperature(self):
        return self.get_temp()

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
            return "dummy response"

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
        return self._read_response()

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
        self._send_command(f"setTempTarget{temp:03}")
        self._send_command("tempOn")

    def set_temperature(self, target_temp):
        self.set_temp_andWait(target_temp)

    def quick_temp(self, temp_target, overshot=10):
        if temp_target > 60 or temp_target < 0:
            raise Exception("this function currently only works for temps btw 0C and 60C")
        start_temp = self.get_temp()

        if temp_target > start_temp:
            overshot_temp = temp_target + overshot
        else:
            overshot_temp = temp_target - overshot

        delay_seconds = abs(temp_target - start_temp) * (60 / 7)
        self.set_temp(overshot_temp)
        time.sleep(delay_seconds)
        self.set_temp(temp_target)

    def set_temp_andWait(self, target_temp, timeout_min=30, tolerance=0.5):
        interval_sec = 10
        SEC_IN_MIN = 60

        curr_temp = self.get_temp()
        self.protocol.comment(
            f"Setting temperature. Current temp: {curr_temp}\nTarget temp: {target_temp}"
        )

        self.set_temp(target_temp)

        time_elapsed = 0

        while abs(self.get_temp() - target_temp) > tolerance:
            self.protocol.comment(
                f"Waiting for temp to reach target: {target_temp}, actual temp: {self.get_temp()}"
            )
            if not self.protocol.is_simulating():  # Skip delay during simulation
                time.sleep(interval_sec)
            time_elapsed += interval_sec
            if time_elapsed > timeout_min * SEC_IN_MIN:
                raise Exception("Temperature timeout")

        return target_temp

    def temp_off(self):
        if self.serial_object is None:
            self.temp = 25
        else:
            self._send_command("tempOff")

    def deactivate(self):
        self.temp_off()

    def __del__(self):
        self.temp_off()
        self.serial_object.close()

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


# This is just for jupyter lab runs
labware_defs = {
"omni_stainer_s12_slides_with_thermosheath" : """{"ordering":[["A1","A2","A3","A4","A5"],["B1","B2","B3","B4"],["C1","C2","C3","C4"],["D1","D2","D3"]],"brand":{"brand":"Parhelia","brandId":["Omni-StainerS12withThermalSheath"]},"metadata":{"displayName":"Omni-StainerS12(forslides)withThermalSheath","displayCategory":"wellPlate","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.71,"yDimension":85.43,"zDimension":102},"wells":{"A1":{"depth":0,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":9.8,"y":77.7,"z":96},"A2":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":41.7,"y":70.7,"z":61.5},"B1":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":41.7,"y":44.6,"z":61.5},"C1":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":41.7,"y":18.6,"z":61.5},"A3":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":62.7,"y":70.7,"z":61.5},"B2":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":62.7,"y":44.6,"z":61.5},"C2":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":62.7,"y":18.6,"z":61.5},"A4":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":83.7,"y":70.7,"z":61.5},"B3":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":83.7,"y":44.6,"z":61.5},"C3":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":83.7,"y":18.6,"z":61.5},"A5":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":104.7,"y":70.7,"z":61.5},"B4":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":104.7,"y":44.6,"z":61.5},"C4":{"depth":34.5,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":104.7,"y":18.6,"z":61.5},"D1":{"depth":38,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":64.8,"y":97.7,"z":58},"D2":{"depth":38,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":64.8,"y":104.7,"z":58},"D3":{"depth":38,"totalLiquidVolume":300,"shape":"circular","diameter":10,"x":64.8,"y":111.7,"z":58}},"groups":[{"metadata":{"displayName":"Omni-StainerS12(forslides)withThermalSheath","displayCategory":"wellPlate","wellBottomShape":"flat"},"brand":{"brand":"Parhelia","brandId":["Omni-StainerS12withThermalSheath"]},"wells":["A1","A2","A3","A4","A5","B1","B2","B3","B4","C1","C2","C3","C4","D1","D2","D3"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"omni_stainer_s12_slides_with_thermosheath"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}""",
"parhelia_12trough" : """{"ordering":[["A1"], ["A2"],["A3"],["A4"],["A5"],["A6"],["A7"],["A8"],["A9"],["A10"],["A11"],["A12"]],"brand":{"brand":"Parhelia","brandId":["12trough"]},"metadata":{"displayName":"Parhelia12-troughreservoir","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.8,"zDimension":44.45},"wells":{"A1":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":13.94,"y":42.9,"z":8},"A2":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":23.03,"y":42.9,"z":8},"A3":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":32.12,"y":42.9,"z":8},"A4":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":41.21,"y":42.9,"z":8},"A5":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":50.3,"y":42.9,"z":8},"A6":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":59.39,"y":42.9,"z":8},"A7":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":68.48,"y":42.9,"z":8},"A8":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":77.57,"y":42.9,"z":8},"A9":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":86.66,"y":42.9,"z":8},"A10":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":95.75,"y":42.9,"z":8},"A11":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":104.84,"y":42.9,"z":8},"A12":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":113.93,"y":42.9,"z":8}},"groups":[{"metadata":{"displayName":"Parhelia12-troughreservoir","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["12trough"]},"wells":["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_12trough"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":1,"y":-1,"z":-0.6}}""",
"parhelia_skirted_96_with_strips" : """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"],"links":["https://www.parheliabio.com"]},"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.48,"zDimension":25},"wells":{"H1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":10,"z":6},"G1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":19,"z":6},"F1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":28,"z":6},"E1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":37,"z":6},"D1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":46,"z":6},"C1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":55,"z":6},"B1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":64,"z":6},"A1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":73,"z":6},"H2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":10,"z":6},"G2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":19,"z":6},"F2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":28,"z":6},"E2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":37,"z":6},"D2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":46,"z":6},"C2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":55,"z":6},"B2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":64,"z":6},"A2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":73,"z":6},"H3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":10,"z":6},"G3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":19,"z":6},"F3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":28,"z":6},"E3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":37,"z":6},"D3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":46,"z":6},"C3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":55,"z":6},"B3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":64,"z":6},"A3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":73,"z":6},"H4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":10,"z":6},"G4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":19,"z":6},"F4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":28,"z":6},"E4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":37,"z":6},"D4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":46,"z":6},"C4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":55,"z":6},"B4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":64,"z":6},"A4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":73,"z":6},"H5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":10,"z":6},"G5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":19,"z":6},"F5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":28,"z":6},"E5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":37,"z":6},"D5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":46,"z":6},"C5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":55,"z":6},"B5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":64,"z":6},"A5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":73,"z":6},"H6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":10,"z":6},"G6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":19,"z":6},"F6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":28,"z":6},"E6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":37,"z":6},"D6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":46,"z":6},"C6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":55,"z":6},"B6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":64,"z":6},"A6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":73,"z":6},"H7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":10,"z":6},"G7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":19,"z":6},"F7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":28,"z":6},"E7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":37,"z":6},"D7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":46,"z":6},"C7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":55,"z":6},"B7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":64,"z":6},"A7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":73,"z":6},"H8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":10,"z":6},"G8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":19,"z":6},"F8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":28,"z":6},"E8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":37,"z":6},"D8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":46,"z":6},"C8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":55,"z":6},"B8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":64,"z":6},"A8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":73,"z":6},"H9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":10,"z":6},"G9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":19,"z":6},"F9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":28,"z":6},"E9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":37,"z":6},"D9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":46,"z":6},"C9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":55,"z":6},"B9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":64,"z":6},"A9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":73,"z":6},"H10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":10,"z":6},"G10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":19,"z":6},"F10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":28,"z":6},"E10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":37,"z":6},"D10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":46,"z":6},"C10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":55,"z":6},"B10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":64,"z":6},"A10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":73,"z":6},"H11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":10,"z":6},"G11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":19,"z":6},"F11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":28,"z":6},"E11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":37,"z":6},"D11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":46,"z":6},"C11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":55,"z":6},"B11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":64,"z":6},"A11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":73,"z":6},"H12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":10,"z":6},"G12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":19,"z":6},"F12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":28,"z":6},"E12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":37,"z":6},"D12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":46,"z":6},"C12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":55,"z":6},"B12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":64,"z":6},"A12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":73,"z":6}},"groups":[{"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_skirted_96_with_strips"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}""",
"omni_stainer_s12_slides_with_thermosheath_on_coldplate" : """{ "ordering": [["A1", "A2", "A3", "A4", "A5"], ["B1", "B2", "B3", "B4"], ["C1", "C2", "C3", "C4"], ["D1", "D2", "D3"]], "brand": { "brand": "Parhelia", "brandId": ["Omni-Stainer S12 with Thermal Sheath on ColdPlateSlim"] }, "metadata": { "displayName": "Omni-Stainer S12 (for slides) with Thermal Sheath on ColdPlate", "displayCategory": "wellPlate", "displayVolumeUnits": "µL", "tags": [] }, "dimensions": { "xDimension": 127.71, "yDimension": 85.43, "zDimension": 145 }, "wells": { "A1": { "depth": 0, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 9.8, "y": 77.7, "z": 142 }, "A2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 70.7, "z": 111.1 }, "B1": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 44.6, "z": 111.1 }, "C1": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 18.6, "z": 111.1 }, "A3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 70.7, "z": 111.1 }, "B2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 44.6, "z": 111.1 }, "C2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 18.6, "z": 111.1 }, "A4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 70.7, "z": 111.1 }, "B3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 44.6, "z": 111.1 }, "C3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 18.6, "z": 111.1 }, "A5": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 70.7, "z": 111.1 }, "B4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 44.6, "z": 111.1 }, "C4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 18.6, "z": 111.1 }, "D1": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 97.7, "z": 111.1 }, "D2": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 104.7, "z": 111.1 }, "D3": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 111.7, "z": 111.1 } }, "groups": [{ "metadata": { "displayName": "Omni-Stainer S12 (for slides) with Thermal Sheath", "displayCategory": "wellPlate", "wellBottomShape": "flat" }, "brand": { "brand": "Parhelia", "brandId": ["Omni-Stainer S12 with Thermal Sheath"] }, "wells": ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "D1", "D2", "D3"] }], "parameters": { "format": "irregular", "quirks": [], "isTiprack": false, "isMagneticModuleCompatible": false, "loadName": "omni_stainer_s12_slides_with_thermosheath_on_coldplate" }, "namespace": "custom_beta", "version": 1, "schemaVersion": 2, "cornerOffsetFromSlot": { "x": 0, "y": 0, "z": 0 } }"""
}

def loadLabwareFromDict(labwareName, protocol_or_tempmodule, position=-1, z_offset=0):
    LABWARE_DEF = json.loads(labware_defs[labwareName])
    LABWARE_DEF["dimensions"]["zDimension"] += z_offset

    WELLS = LABWARE_DEF["wells"]

    for k in WELLS.keys():
        WELLS[k]["z"] += z_offset

    # Check if the passed context is a TemperatureModuleContext or ColdPlateSlimDriver
    if isinstance(
            protocol_or_tempmodule, opentrons.protocol_api.TemperatureModuleContext
    ) or isinstance(protocol_or_tempmodule, ColdPlateSlimDriver):
        labware = protocol_or_tempmodule.load_labware_from_definition(
            LABWARE_DEF, LABWARE_DEF.get("metadata", {}).get("displayName")
        )
    else:
        labware = protocol_or_tempmodule.load_labware_from_definition(
            LABWARE_DEF, position, LABWARE_DEF.get("metadata", {}).get("displayName")
        )
    return labware


# End of jupyter notebook -specific functions


def washSamples(
        pipette,
        sourceLiquid,
        samples,
        volume,
        num_repeats=1,
        height_offset=0,
        aspiration_offset=0,
        dispensing_offset=0,
        keep_tip=False,
):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    print("Samples are:")
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
                    sourceWell = sourceLiquid.wells[
                        sourceLiquid.current_well
                    ]  # update the current well
                    if sourceLiquid.volume - sourceLiquid.volume_used < volume:
                        raise Exception(f"Liquid depleted: {sourceLiquid}")
                sourceLiquid.volume_used += volume
            pipette.aspirate(
                volume,
                sourceWell.bottom(height_offset + aspiration_offset),
                rate=well_flow_rate,
            )
            pipette.dispense(
                volume,
                sample.bottom(height_offset + dispensing_offset),
                rate=sample_flow_rate,)
            volume_counter[sourceLiquid] += volume

    if not keep_tip:
        pipette.drop_tip()


def puncture_wells(pipette, wells, height_offset=0, top_height_offset=-5, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    if not pipette.has_tip:
        pipette.pick_up_tip()
    for well in wells:
        pipette.move_to(well.top(top_height_offset))
    if not keep_tip: pipette.drop_tip()


def dilute_and_apply_fixative(
        pipette,
        sourceSolutionWell,
        dilutant_buffer_well,
        samples,
        volume,
        height_offset=0,
        keep_tip=False,
):
    if not pipette.has_tip:
        pipette.pick_up_tip()
    # Diluting fixative:
    pipette.aspirate(volume, dilutant_buffer_well, rate=well_flow_rate)
    pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    for iterator in range(0, 3):
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)

    washSamples(
        pipette,
        sourceSolutionWell,
        samples,
        volume,
        1,
        height_offset,
        keep_tip=keep_tip,
    )


def getOmnistainerWellsList(omnistainer, num_samples):
    sample_chambers = []

    if len(omnistainer.wells_by_name()) < num_samples:
        raise Exception("number of wells in the Omni-Stainer less than num_samples")

    wellslist = list(omnistainer.wells_by_name().keys())
    wellslist = wellslist[1: num_samples + 1]

    for well in wellslist:
        sample_chambers.append(omnistainer.wells_by_name()[well])

    print("omnistainer.wells_by_name are:")
    print(omnistainer.wells_by_name())
    print("sample_chambers are:")
    print(sample_chambers)
    return sample_chambers


def mix(pipette, sourceSolutionWell, volume, num_repeats):
    if not pipette.has_tip:
        pipette.pick_up_tip()

    for i in range(0, num_repeats):
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()


def openShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False):
    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
        pipette.move_to(
            covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].bottom(0),
            force_direct=True,
        )
        if not keep_tip:
            pipette.drop_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].top(-10))
        pipette.move_to(
            covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].top(-10),
            force_direct=True,
        )
    protocol.delay(seconds=1)


def closeShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False):
    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
        pipette.move_to(
            covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].bottom(0),
            force_direct=True,
        )
        if not keep_tip:
            pipette.drop_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].top(-10))
        pipette.move_to(
            covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].top(-10),
            force_direct=True,
        )
    protocol.home()


def apply_and_incubate(
        protocol,
        pipette,
        source,
        reagent_name,
        target_wells,
        volume,
        dispense_repeats,
        incubation_time,
        puncture=True,
        step_repeats=1
):

    if puncture:
        puncture_wells(pipette, source)

    pipette.flow_rate.aspirate = default_flow_rate * well_flow_rate
    pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate

    one_to_many = False
    # determining if a source is a single well or a list of wells
    try:
        iter(source)
        if len(source) != len(target_wells):
            raise Exception(
                "the number of source wells ({}) doesn't match the number of target wells ({})".format(
                    len(source), len(target_wells)
                )
            )
    except TypeError:
        one_to_many = True


    for i in range(step_repeats):
        if i == 0:
            protocol.comment("applying " + reagent_name)
        else:
            protocol.comment("applying " + reagent_name + " repeat #" + str(i + 1))

        if one_to_many:
            for i in range(dispense_repeats):
                if (i > 0) and not testmode: protocol.delay(minutes=1, msg="1 min delay before repeat applications")
                pipette.distribute(
                    volume,
                    source,
                    target_wells,
                    new_tip="once",
                    disposal_volume=0,
                    blowout=False
                )
        else:
            for i in range(dispense_repeats):
                if (i > 0) and not testmode: protocol.delay(minutes=1, msg="1 min delay before repeat applications")
                pipette.transfer(
                    volume,
                    source,
                    target_wells,
                    new_tip="always",
                    disposal_volume=0,
                    blowout=False
                )

        if testmode:
            protocol.comment("TEST MODE!!! Incubation skipped")
        else:
            protocol.delay(minutes=incubation_time, msg=reagent_name + " incubation")


def safe_delay(protocol, *args, **kwargs):
    if testmode:
        protocol.delay(minutes=0.5)
        protocol.comment("TEST MODE! delay = 0.5 min")
    else:
        protocol.delay(*args, **kwargs)


def distribute_between_samples(
        pipette,
        sourceSolutionWell,
        samples,
        volume,
        num_repeats=1,
        height_offset=0,
        aspiration_offset=0,
        dispensing_offset=0,
        keep_tip=False,
):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    print("Samples are:")
    print(samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

    aspiration_offset += aspiration_gap
    dispensing_offset += dispensing_gap

    for i in range(0, num_repeats):
        pipette.aspirate(
            volume,
            sourceSolutionWell.bottom(height_offset + aspiration_offset),
            rate=well_flow_rate,
        )
        for s in samples:
            print(s)
            print("Distributing into sample:" + str(s))
            pipette.dispense(
                volume / len(samples),
                s.bottom(height_offset + dispensing_offset),
                rate=sample_flow_rate,
            )

    if not keep_tip:
        pipette.drop_tip()

# def quick_temp(temp_target, start_temp, overshot = 10):
#     if 'coldplate' in omnistainer_type:
#         temp_mod = ColdPlateSlimDriver(protocol,0)
#     overshot_temp = temp_target + overshot
#     delay_seconds = abs(temp_target - start_temp) * (60/7)
#     temp_mod.set_temp(overshot_temp)
#     safe_delay(protocol, seconds=delay_seconds, msg="adjusting temp to overshot temp" + str(overshot_temp))
#     temp_mod.set_temp(temp_target)
#     safe_delay(protocol, seconds=delay_seconds, msg="adjusting temp to temp target" + str(temp_target))
### END VERAO GLOBAL


metadata = {
    'protocolName': 'Ultivue InSituPlex v1- TEST MODE - after Dewax & Antigen Retrieval',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'UltiMapper assay automation protocol for Parhelia Omni-Stainer',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 4

### VERAO VAR NAME='Delayed start' TYPE=BOOLEAN
delayed_start = False

### VERAO VAR NAME='Protocol start delay time (minutes)' TYPE=NUMBER LBOUND=15 UBOUND=8000 DECIMAL=FALSE
protocol_delay_minutes = 30

### VERAO VAR NAME='Block and Primary Antibody Stain?' TYPE=BOOLEAN
primary_staining = True

### VERAO VAR NAME='Amplification?' TYPE=BOOLEAN
secondary_staining = True

### VERAO VAR NAME='Apply Fluorescent Probes and Nuclear Counterstain?' TYPE=BOOLEAN
probe_staining = True

### VERAO VAR NAME='Amplification temperature' TYPE=NUMBER LBOUND=0 UBOUND=40
amp_temp = 30

### VERAO VAR NAME='Room temperature' TYPE=NUMBER LBOUND=15 UBOUND=25
room_temp = 22

### VERAO VAR NAME='Storage mode?' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=2 UBOUND=25
storage_temp = 4

### VERAO VAR NAME='Blocking Incubation time (min)' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
antibody_diluent_incubation_min = 15

### VERAO VAR NAME='Primary Antibody incubation time (min)' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
primary_ab_incubation = 60

### VERAO VAR NAME='Amplification Pretreatment time (min)' TYPE=NUMBER LBOUND=5 UBOUND=120 DECIMAL=FALSE
amp_pretreatment_incubation = 30

### VERAO VAR NAME='Amplification time (min)' TYPE=NUMBER LBOUND=5 UBOUND=600 DECIMAL=FALSE
amp_incubation = 90

### VERAO VAR NAME='Nuclear Counterstain incubation time (min)' TYPE=NUMBER LBOUND=5 UBOUND=600 DECIMAL=FALSE
counterstain_incubation = 15

### VERAO VAR NAME='Fluorescent Probe incubation time (min)' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
fluor_probe_incubation = 60

### VERAO VAR NAME='PBS wash incubation time' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
wash_incubation = 5

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody/Reagent staining volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Double add (uses 2x reagents, but improves uniformity)' TYPE=BOOLEAN
double_add = False

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_location = 'left'

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 6

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12 module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='Deck position: Buffer W/ Antibodies plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_plate_position = 9

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 10

### VERAO VAR NAME='Tip type for tiprack 1' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type_tiprack1 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='TEST MODE (ALL INCUBATION DELAYS WILL BE SKIPPED)' TYPE=BOOLEAN
testmode = True

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.ab_plate = ab_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    #Tiprack
    tiprack_1 = protocol.load_labware(tip_type_tiprack1, labwarePositions.tiprack_300_1,
                                      'tiprack 200/300ul 1')
    #Pipette
    pipette_type = 'p300_single_gen2'
    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_1])
    pipette.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos-1]
    #Staining Module
    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')
    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)
    #Buffers plate
    PBS_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate,
                                         '12-trough PBS reservoir')
    #Reagent plate
    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_plate, '96-well-plate')

    ##########################REAGENT SETUP################################
    # Buffers plate
    #PBS_wells[list(PBS_wells.keys())[i]]
    #PBS_wells = PBS_trough12.wells_by_name()
    wash_buffer = PBS_trough12.wells_by_name()['A1']

    # Reagent plate
    antibody_diluent_wells = reagents_96plate.rows()[0][:num_samples]
    primary_ab_wells = reagents_96plate.rows()[1][:num_samples]
    pre_amp_wells = reagents_96plate.rows()[2][:num_samples]
    amp_wells = reagents_96plate.rows()[3][:num_samples]
    counterstain_wells = reagents_96plate.rows()[4][:num_samples]
    fluor_probe_wells = reagents_96plate.rows()[5][:num_samples]

    if double_add:
        num_reps = 2
    else: 
        num_reps = 1

    #################PROTOCOL####################
    protocol.comment("Starting the "+ metadata["protocolName"] +" for samples:" + str(sample_chambers))

    protocol.home()

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        openShutter(protocol, pipette, omnistainer)

    temp_mod = None

    if delayed_start:
        closeShutter(protocol, pipette, omnistainer)
        protocol.delay(minutes=protocol_delay_minutes, msg = "Delaying the start by " + str(protocol_delay_minutes) + " minutes" )

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol,0)
        temp_mod.set_temp(room_temp)

    apply_and_incubate(protocol, pipette, antibody_diluent_wells,   "Antibody Diluent (Block)",       sample_chambers,   ab_volume,      num_reps, antibody_diluent_incubation_min                                      )
    
    if primary_staining:
        apply_and_incubate(protocol, pipette, primary_ab_wells,     "1x (Primary) Ab solution",     sample_chambers,   ab_volume,     num_reps, primary_ab_incubation                             )
        apply_and_incubate(protocol, pipette, wash_buffer,          "1x PBS Wash",                  sample_chambers,   wash_volume,   2,         wash_incubation,         step_repeats = 2                )
    if secondary_staining:
        apply_and_incubate(protocol, pipette, pre_amp_wells,        "Pre-Amp Mix",                  sample_chambers,   ab_volume,     num_reps, amp_pretreatment_incubation                       )
        apply_and_incubate(protocol, pipette, wash_buffer,          "1x PBS Wash",                  sample_chambers,   wash_volume,   2,         wash_incubation,         step_repeats = 2, puncture=False)

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer)
        temp_mod.quick_temp(amp_temp)
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette, omnistainer)
        apply_and_incubate(protocol, pipette, amp_wells,            "1x Amp Solution",              sample_chambers,   ab_volume,    num_reps,   0)
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer)
        protocol.delay(minutes=amp_incubation, msg = "Amplification in progress")

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette, omnistainer)
        temp_mod.quick_temp(room_temp)
        apply_and_incubate(protocol, pipette, wash_buffer,          "1x PBS Wash",                  sample_chambers,   wash_volume,   2,         wash_incubation,         step_repeats = 2, puncture=False)

    if probe_staining:
        apply_and_incubate(protocol, pipette, counterstain_wells,       "1x Nuclear Counterstain",  sample_chambers,   ab_volume,     num_reps, counterstain_incubation )
        apply_and_incubate(protocol, pipette, wash_buffer,              "1x PBS Wash",              sample_chambers,   wash_volume,   2,        wash_incubation,         step_repeats = 2, puncture=False)
        apply_and_incubate(protocol, pipette, fluor_probe_wells,        "Fluorescent Probe",        sample_chambers,   ab_volume,     num_reps, counterstain_incubation )
        apply_and_incubate(protocol, pipette, wash_buffer,              "1x PBS Wash",              sample_chambers,   wash_volume,   2,        wash_incubation,         step_repeats = 2, puncture=False)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette, omnistainer)
    if storage_mode:
        protocol.comment(f"cooling down to {storage_temp} deg for storage. The protocol will pause next")
        temp_mod.set_temp(storage_temp)
        protocol.pause(
            msg=f"Protocol is paused for {storage_temp} C storage. "
                f"Hit Resume to end the protocol and turn off the thermal module")

    temp_mod.temp_off()
    protocol.comment(f"Protocol done - temperature module has been turned off")
    protocol.home()