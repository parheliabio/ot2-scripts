## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
## Last updated by nwedin 10/17/2023
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
        self.set_temp_andWait(temp_target)

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


class TempModuleGroup:
    def __init__(self, temp_modules):
        self.temp_modules = temp_modules

    @property
    def temperature(self):
        return self.get_temp()

    def get_info(self):
        return str([x.get_temp() for x in self.temp_modules])

    def get_temp(self):
        return sum([x.get_temp() for x in self.temp_modules])/len(self.temp_modules)

    def set_temp(self, my_temp):
        for mod in self.temp_modules:
            mod.set_temp(my_temp)

    ##the code below may seem confusing, but if you think about it, it's correct
    def set_temperature(self, target_temp):
        for mod in self.temp_modules:
            mod.set_temp(target_temp)
        for mod in self.temp_modules:
            mod.set_temp_andWait(target_temp)

    def quick_temp(self, temp_target, overshot=10):
        if temp_target > 60 or temp_target < 0:
            raise Exception("this function currently only works for temps btw 0C and 60C")
        for mod in self.temp_modules:
            start_temp = self.get_temp()
            if temp_target > start_temp:
                overshot_temp = temp_target + overshot
            else:
                overshot_temp = temp_target - overshot

            delay_seconds = abs(temp_target - start_temp) * (60 / 7)
            for mod in self.temp_modules:
                self.set_temp(overshot_temp)
            time.sleep(delay_seconds)

            self.set_temp_andWait(temp_target)

    def set_temp_andWait(self, target_temp, timeout_min=30, tolerance=0.5):
        interval_sec = 10
        SEC_IN_MIN = 60

        curr_temp = self.get_temp()
        self.protocol.comment(
            f"Setting temperature. Current temp: {curr_temp}\n Target temp: {target_temp}"
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
        for mod in self.temp_modules:
            mod.temp_off()

    def deactivate(self):
        self.temp_off()


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

class OmniStainerWell:
    
    def __init__(self, omni_stainer, well):
        self.well = well
        self.omni_stainer = omni_stainer
        
class OmniStainer:
    
    def __init__(self, labware, num_samples, has_shutter):
        self.labware = labware
        self.num_samples = num_samples
        self.has_shutter = has_shutter
        if has_shutter:
            self.shutter_open = False

    def get_wells(self):
        wells_list = getOmniStainerWellsList(self.labware, self.num_samples)
        os_wells  = [OmniStainerWell(self, x) for x in wells_list]
        return os_wells

def openShutter(protocol, pipette, covered_lbwr_list, keep_tip=False, use_tip=False):

    if not isinstance(covered_lbwr_list, collections.abc.Iterable):
        covered_lbwr_list = [covered_lbwr_list]

    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
                
    for covered_lbwr in covered_lbwr_list:
        if isinstance(covered_lbwr, OmniStainer):
            covered_lbwr = covered_lbwr.labware
            covered_lbwr.shutter_open = True

        src = covered_lbwr.wells()[len(covered_lbwr.wells()) - 2]
        dest = covered_lbwr.wells()[len(covered_lbwr.wells()) - 1]
        if use_tip:
            pipette.move_to(src.bottom(0))
            pipette.move_to(dest.bottom(0), force_direct=True)
        else:
            pipette.move_to(src.top(-10))
            pipette.move_to(dest.top(-10),force_direct=True)
            
    if use_tip and not keep_tip:
        pipette.drop_tip()
        
    protocol.delay(seconds=1)

def closeShutter(protocol, pipette, covered_lbwr_list, keep_tip=False, use_tip=False):

    if not isinstance(covered_lbwr_list, collections.abc.Iterable):
        covered_lbwr_list = [covered_lbwr_list]

    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
                
    for covered_lbwr in covered_lbwr_list:
        if isinstance(covered_lbwr, OmniStainer):
            covered_lbwr = covered_lbwr.labware
            covered_lbwr.shutter_open = False

        src = covered_lbwr.wells()[len(covered_lbwr.wells()) - 2]
        dest = covered_lbwr.wells()[len(covered_lbwr.wells()) - 3]
        if use_tip:
            pipette.move_to(src.bottom(0))
            pipette.move_to(dest.bottom(0), force_direct=True)
        else:
            pipette.move_to(src.top(-10))
            pipette.move_to(dest.top(-10),force_direct=True)
            
    if use_tip and not keep_tip:
        pipette.drop_tip()
        
    protocol.home()

def washSamples(
        pipette,
        sourceLiquid,
        samples,
        volume,
        num_repeats=1,
        height_offset=0,
        aspiration_offset=0,
        dispensing_offset=0,
        keep_tip=False):

    if not isinstance(samples, collections.abc.Iterable):
        samples = [samples]

    temp_samples = []
    for sample in samples:
        if isinstance(sample, OmniStainerWell):
            temp_samples.append(sample.well)
            if sample.omni_stainer.has_shutter:
                if not sample.omni_stainer.shutter_open:
                    raise Exception("Omni-Stainer shutter is closed")
        else:
            temp_samples.append(sample)

    samples = temp_samples

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
        step_repeats=1):

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
                "the number of source wells ({}) doesn't match the number of target wells ({})".format(len(source), len(target_wells))
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
                    blowout=True,
                    blowout_location="destination well"
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
        keep_tip=False):

    if not isinstance(samples, collections.abc.Iterable):
        samples = [samples]

    temp_samples = []
    for sample in samples:
        if isinstance(sample, OmniStainerWell):
            temp_samples.append(sample.well)
            if sample.omni_stainer.has_shutter:
                if not sample.omni_stainer.shutter_open:
                    raise Exception("Omni-Stainer shutter is closed")
        else:
            temp_samples.append(sample)

    samples = temp_samples

    if not pipette.has_tip:
        pipette.pick_up_tip()

    pipette.distribute(volume, sourceSolutionWell, samples, new_tip = 'never')

    if not keep_tip:
        pipette.drop_tip()

### END VERAO GLOBAL

metadata = {
    'protocolName': 'Parhelia IHC',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IHC staining protocol for Parhelia Omni-stainer',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Baking (30 min at 60C)' TYPE=BOOLEAN
baking = False

### VERAO VAR NAME='Dewaxing' TYPE=BOOLEAN
dewaxing = False

### VERAO VAR NAME='Rehydration' TYPE=BOOLEAN
rehydration = False

### VERAO VAR NAME='ANTIGEN RETRIEVAL' TYPE=BOOLEAN
retrieval = False

### VERAO VAR NAME='Retrival Temperature (C)' TYPE=NUMBER LBOUND=60 UBOUND=99 DECIMAL=FALSE
retrieval_temp = 96

### VERAO VAR NAME='Retrival Time (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
retrieval_time = 40

### VERAO VAR NAME='Retrival Temperature (C) (actual temp on sample is ~3C less)' TYPE=NUMBER LBOUND=60 UBOUND=99 DECIMAL=FALSE
room_temp = 22

### VERAO VAR NAME='manual PAUSE during the primary antibody incubation' TYPE=BOOLEAN
protocol_pause = False

### VERAO VAR NAME='Type of protocol' TYPE=CHOICE OPTIONS=['IHC only','IHC with Hematoxylin','Hematoxylin only']
type_of_protocol = 'IHC only'

### VERAO VAR NAME='Hematoxylin source' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
hematoxylin_source = 'from pcr strip'

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'par2s_9slides_blue_v3', 'PAR2c_12coverslips']
omnistainer_type = 'omni_stainer_s12_slides'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'


### VERAO VAR NAME='Number of Samples in Omni-stainer #1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples_1 = 2

### VERAO VAR NAME='Number of Samples in Omni-stainer #2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples_2 = 5

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

# Antibody incubation time in minutes
### VERAO VAR NAME='Primary antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=1440 DECIMAL=FALSE
primary_ab_incubation_time_minutes = 480

### VERAO VAR NAME='Secondary antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=1440 DECIMAL=FALSE
secondary_ab_incubation_time_minutes = 90

### VERAO VAR NAME='DAB incubation time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=1440 DECIMAL=FALSE
DAB_incubation_time = 10

### VERAO VAR NAME='Hematoxylin incubation time (seconds)' TYPE=NUMBER LBOUND=30 UBOUND=1440 DECIMAL=FALSE
hematoxylin_incubation_time_seconds = 60

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

### VERAO VAR NAME='Sample wash volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 110

### VERAO VAR NAME='Antibody mix volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 60

### VERAO VAR NAME='Extra bottom gap (for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'


### VERAO VAR NAME='labwarePositions.buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 7

### VERAO VAR NAME='labwarePositions.omnistainer_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_1_position = 1

### VERAO VAR NAME='labwarePositions.omnistainer_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_2_position = 3

### VERAO VAR NAME='labwarePositions.ihc_reagents_plate_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ihc_reagents_plate_position_1 = 8

### VERAO VAR NAME='labwarePositions.ihc_reagents_plate_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ihc_reagents_plate_position_2 = 9

### VERAO VAR NAME='labwarePositions.tiprack_300' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 6

### VERAO VAR NAME='Test mode (all delays reduced to 30s)' TYPE=BOOLEAN
testmode = True

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.omnistainer_1 = omnistainer_1_position
labwarePositions.omnistainer_2 = omnistainer_2_position
labwarePositions.ihc_reagents_plate1 = ihc_reagents_plate_position_1
labwarePositions.ihc_reagents_plate2 = ihc_reagents_plate_position_2
labwarePositions.tiprack_300 = tiprack_300_position

###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):

    ###########################LABWARE SETUP#################################

    USE_TROUGH = True
    
    if 'thermosheath' in omnistainer_type and max(labwarePositions.omnistainer_1,labwarePositions.omnistainer_2) > 9:
        raise Exception("Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")

    if 'coldplate' in omnistainer_type:
        temp_mod_1 = ColdPlateSlimDriver(protocol, temp_mod_number=0)
        temp_mod_2 = ColdPlateSlimDriver(protocol, temp_mod_number=1)

    temp_mod = TempModuleGroup([temp_mod_1, temp_mod_2])
    
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos-1]

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    IHC_reagents_96plate_1 = protocol.load_labware(type_of_96well_plate, labwarePositions.ihc_reagents_plate_1, 'IHC reagents plate 1')
    IHC_reagents_96plate_2 = protocol.load_labware(type_of_96well_plate, labwarePositions.ihc_reagents_plate_2, 'IHC reagents plate 2')


    omnistainer_labware_1 = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer_1, 'Omni-stainer 1')
    omnistainer_labware_2 = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer_2, 'Omni-stainer 2')

    omnistainer_1 = OmniStainer(omnistainer_labware_1,num_samples_1)
    #omnistainer_2 = OmniStainer(omnistainer_labware_1,num_samples_2)
    omnistainer_2 = OmniStainer(omnistainer_labware_2,num_samples_2)

    omnistainer = [omnistainer_1, omnistainer_2]

    sample_chambers = omnistainer_1.get_wells() + omnistainer_2.get_wells()

    num_samples = num_samples_1 + num_samples_2

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.dewax = buffer_wells['A1']
    buffers.eth_100perc = buffer_wells['A2']
    buffers.eth_95perc = buffer_wells['A3']
    buffers.eth_70perc = buffer_wells['A4']
    buffers.retrieval = buffer_wells['A5']
    buffers.TBS_wash = buffer_wells['A6']
    buffers.water = buffer_wells['A7']
    buffers.storage = buffer_wells['A8']
    buffers.hematoxylin = buffer_wells['A12']

    preblock_wells = IHC_reagents_96plate_1.rows()[0]+IHC_reagents_96plate_2.rows()[0]
    enzymeblock_wells = IHC_reagents_96plate_1.rows()[1]+IHC_reagents_96plate_2.rows()[1]
    hrpsecondaryab_wells = IHC_reagents_96plate_1.rows()[2]+IHC_reagents_96plate_2.rows()[2]
    substrate_wells = IHC_reagents_96plate_1.rows()[3]+IHC_reagents_96plate_2.rows()[3]
    DAB_wells = IHC_reagents_96plate_1.rows()[4]+IHC_reagents_96plate_2.rows()[4]
    antibody_wells = IHC_reagents_96plate_1.rows()[5]+IHC_reagents_96plate_2.rows()[5]
    hematoxylin_wells = IHC_reagents_96plate_1.rows()[7]+IHC_reagents_96plate_2.rows()[7]
    
    if debug: protocol.comment(sample_chambers)

    #################PROTOCOL####################
    protocol.home()

    ### this was taken from NSTG protocol

    closeShutter(protocol, pipette, omnistainer)
    puncture_wells(pipette, vars(buffers).values()[-1])

    #how much to overshoot the temp by initially in order to hasten the temp equilibration

    dewax_equilib_delay = 30
    dispense_slowdown_factor = 3

    if baking:
        protocol.comment("baking at: " + str(baking_temp))
        temp_mod.quick_temp(baking_temp)
        safe_delay(protocol, minutes=baking_time, msg="Baking")
        dewax_equilib_delay -= 20

    if dewaxing:
        protocol.comment("adjusting temp to {}C for dewaxing".format(dewax_temp))
        temp_mod.set_temp(dewax_temp)

        safe_delay(protocol, minutes=dewax_equilib_delay, msg = "equilibrating temp for to {}C for dewaxing".format(dewax_temp))

        openShutter(protocol, pipette, omnistainer)

        protocol.comment("dewaxing")

        #ultra-slow dispensing in order to fill the chamber without bubbles
        global sample_flow_rate
        sample_flow_rate /= dispense_slowdown_factor
        washSamples(pipette, buffers.dewax, sample_chambers, wash_volume, 3, keep_tip=True)
        sample_flow_rate *= dispense_slowdown_factor

        alc_wash_temp = 50
        temp_mod.quick_temp(alc_wash_temp)
        safe_delay(protocol, minutes=10, msg = "equilibrating temp for to {}C for alcohol washes".format(alc_wash_temp))

    if rehydration:
        washSamples(pipette, buffers.eth_100perc, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 100% EtOH")
        washSamples(pipette, buffers.eth_95perc, sample_chambers, wash_volume, 1, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 95% EtOH")
        washSamples(pipette, buffers.eth_70perc, sample_chambers, wash_volume, 1, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 70% EtOH")
        pipette.drop_tip()

        washSamples(pipette, buffers.water, sample_chambers, wash_volume, 2)
        safe_delay(protocol, minutes=1, msg = "Incubating in water")


    if retrieval:
        washSamples(pipette, buffers.retrieval, sample_chambers, wash_volume, 2, keep_tip=True)

        closeShutter(protocol, pipette, omnistainer)

        temp_mod.set_temp(retrieval_temp)


        if dewaxing:
            #According to the exp calibration, 20 minutes is enough to reach 99C from 50C (alc wash temp)
            reps = 4
        else:
            #Otherwise, 30 minutes is needed to reach 99C from room temp
            reps = 6
            
        for i in range (reps):
            safe_delay(protocol, minutes=5, msg = "heating up to "+str(retrieval_temp)+", topping off ER buffer as we go" + str(i+1) +"/"+ str(reps))
            openShutter(protocol, pipette, omnistainer)
            distribute_between_samples(pipette, buffers.retrieval, sample_chambers, wash_volume/2, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer)

        safe_delay(protocol, minutes=retrieval_time, msg = "HIER in progress")


        overshot = 10
        
        target_temp = room_temp-overshot
        temp_mod.set_temp(target_temp)

        cooldown_delay_min = 20
        topoff_every_min = 5

        for i in range(int(cooldown_delay_min/topoff_every_min)):
            safe_delay(protocol, minutes=topoff_every_min, msg = "adjusting temp to " + str(target_temp) + ", topping off ER buffer to prevent evap")
            openShutter(protocol, pipette, omnistainer)
            distribute_between_samples(pipette, er_buff_well, sample_chambers, wash_volume/2, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer)

    temp_mod.set_temp(room_temp)
    safe_delay(protocol, minutes=10, msg= "equilibrating to room temp")
    
    if type_of_protocol in ['IHC only', 'IHC with Hematoxylin']:
        # WASHING SAMPLES WITH TBS
        protocol.comment("washing in TBS")
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 2, keep_tip=True)

        # APPLYING enzyme blocking
        protocol.comment("puncturing enzyme blocking wells")
        puncture_wells(pipette_300, enzymeblock_wells)

        protocol.comment("applying enzyme blocking")
        for i in range(num_samples):
            washSamples(pipette_300, enzymeblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
            # INCUBATE 10 MIN
        protocol.comment("hrp blocking incubation: 10min")
        protocol.delay(minutes=10)

        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 3)

        # Preblocking
        protocol.comment("preblocking")

        protocol.comment("puncturing preblock wells")
        puncture_wells(pipette_300, preblock_wells)

        protocol.comment("applying the preblock")
        for i in range(num_samples):
            protocol.comment(i)
            washSamples(pipette_300, preblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("preblocking incubation: 15 min")
        protocol.delay(minutes=15)

        # APPLYING ANTIBODY COCKTAILS TO SAMPLES
        puncture_wells(pipette_300, antibody_wells)
        
        protocol.comment("puncturing and applying abs")
        for i in range(num_samples):
            protocol.comment(i)
            washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume, 1)

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        # PRIMARY ANTIBODY INCUBATION
        protocol.comment("staining incubation: " + str(primary_ab_incubation_time_minutes) + "min")

        if protocol_pause:
            protocol.pause(msg = "The protocol is paused for primary antibody incubation")
        if not protocol_pause:
            protocol.delay(minutes=primary_ab_incubation_time_minutes, msg = "staining incubation")

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer)

        # WASHING SAMPLES WITH TBS
        # three individual repeats below is because they need particular incubation time between them
        protocol.comment("washing with TBS")
        for i in range(5):
            washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 1, keep_tip=True)
            protocol.delay(minutes=3)
        pipette_300.drop_tip()


        # APPLYING HRP SECONDARY ANTIBODY COCKTAILS TO SAMPLES
        protocol.comment("puncturing hrpsecondaryab wells")
        puncture_wells(pipette_300, hrpsecondaryab_wells)

        protocol.comment("applying hrpsecondaryab")
        for i in range(num_samples):
            washSamples(pipette_300, hrpsecondaryab_wells[i], sample_chambers[i], ab_volume, 1)

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        # SECONDARY ANTIBODY INCUBATION
        protocol.comment("staining incubation: " + str(secondary_ab_incubation_time_minutes) + "min")
        protocol.delay(minutes=secondary_ab_incubation_time_minutes)

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        # three individual repeats below is because they need particular incubation time between them
        protocol.comment("washing with TBS")
        for i in range(3):
            washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 1, keep_tip=True)
            protocol.delay(minutes=3)
        pipette_300.drop_tip()

        # DILUTING AND APPLYING THE DAB
        protocol.comment("puncturing the DAB and substrate wells")
        puncture_wells(pipette_300, DAB_wells[i])
        puncture_wells(pipette_300, substrate_wells[i])

        protocol.comment("applying DAB")
        for i in range(num_samples):
            dilute_and_apply_fixative(pipette_300, DAB_wells[i], substrate_wells[i], sample_chambers[i], wash_volume, keep_tip=True)
        pipette_300.drop_tip()


        protocol.comment("developing substrate")
        protocol.delay(minutes=DAB_incubation_time)

        protocol.comment("final wash with water")
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 5, keep_tip=True)

    #HEMATOXYLIN STAINING
    if type_of_protocol in ['IHC with Hematoxylin','Hematoxylin only']:
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        if hematoxylin_source == 'from reagent trough':
            puncture_wells(pipette_300, buffers.hematoxylin)
            washSamples(pipette_300, buffers.hematoxylin, sample_chambers, wash_volume, 1)
            protocol.delay(minutes=hematoxylin_incubation_time_seconds)
        if hematoxylin_source == 'from pcr strip':
            protocol.comment("puncturing the hematoxylin wells")
            puncture_wells(pipette_300, hematoxylin_wells[i])
            
            protocol.comment("applying hematoxylin")
            for i in range(num_samples):
                washSamples(pipette_300, hematoxylin_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            pipette_300.drop_tip()
        protocol.delay(seconds=hematoxylin_incubation_time_seconds)

    #WASHING SAMPLES WITH WATER
    #three individual repeats below is because they need particular incubation time between them
        protocol.comment("washing with water")
        washSamples(pipette_300, buffers.storage, buffers.storage, 2, 1)
        for i in range (3):
            washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume, 2)
            protocol.delay(minutes=3)
    
        protocol.comment("Dehydration")
        
        washSamples(pipette_300, buffers.eth_70perc, sample_chambers, wash_volume, 1, keep_tip=True)
        washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 1, keep_tip=True)
        washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 2)


    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)
