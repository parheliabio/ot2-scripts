## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
### GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###
from opentrons import protocol_api
import sys
import json
from collections import defaultdict
import serial
import opentrons.protocol_api

####################GENERAL SETUP################################
volume_counter = defaultdict(int)
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.2
aspiration_gap = 0
dispensing_gap = 0

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
        self.deck_position = 7  # Replace this with labwarePosition_heat_module or w.e
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

    def set_temp_andWait(self, target_temp, timeout_min=30, tolerance=0.5, msg=None):
        if msg is not None:
            print(msg)

        interval_sec = 10
        SEC_IN_MIN = 60

        curr_temp = self.get_temp()
        self.protocol.comment(f"Current temp: {curr_temp}\nTarget temp: {target_temp}")

        temp_diff = target_temp - curr_temp
        temp_lag = self.max_temp_lag * (abs(temp_diff) / 100.0)

        if temp_diff > 0:
            temp_step = self.heating_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            print(f"Heating rate: {temp_step}")
        else:
            temp_step = -self.cooling_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            print(f"Cooling rate: {temp_step}")

        while (abs(target_temp - curr_temp) > abs(temp_step)):
            curr_temp += temp_step
            self.set_temp(curr_temp)
            print(f"Ramping the temp to: {curr_temp}")
            self.protocol.delay(seconds=interval_sec)
            curr_temp = self.get_temp()
            print(f"Actual temp: {curr_temp}")

        self.set_temp(target_temp)

        time_elapsed = 0

        while (abs(self.get_temp() - target_temp) > tolerance):
            print(f"Waiting for temp to reach target: {target_temp}, actual temp: {self.get_temp()}, {msg}")
            if not self.protocol.is_simulating():  # Skip delay during simulation
                self.protocol.delay(seconds=interval_sec)
            time_elapsed += interval_sec
            if (time_elapsed > timeout_min * 60):
                raise Exception("Temperature timeout")

        print(f"Target reached, equilibrating for {ab_incubation_time_minutes} minutes, {msg}")
        if not self.protocol.is_simulating():  # Skip delay during simulation
            self.protocol.delay(seconds=temp_lag * SEC_IN_MIN)
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

#This is just for jupyter lab runs
labware_defs = {
    "omni_stainer_s12_slides_with_thermosheath_offset": """{"ordering": [["A1", "A2", "A3", "A4", "A5"], ["B1", "B2", "B3", "B4"], ["C1", "C2", "C3", "C4"], ["D1", "D2", "D3"]], "brand": { "brand": "Parhelia", "brandId": ["Omni-Stainer S12 with Thermal Sheath_offset"] }, "metadata": { "displayName": "Omni-Stainer S12 (for slides) with Thermal Sheath", "displayCategory": "wellPlate", "displayVolumeUnits": "µL", "tags": [] }, "dimensions": { "xDimension": 127.71, "yDimension": 85.43, "zDimension": 102 }, "wells": { "A1": { "depth": 0, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 9.8, "y": 77.7, "z": 96 }, "A2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 70.7, "z": 61.5 }, "B1": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 44.6, "z": 61.5 }, "C1": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 41.7, "y": 18.6, "z": 61.5 }, "A3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 70.7, "z": 61.5 }, "B2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 44.6, "z": 61.5 }, "C2": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 62.7, "y": 18.6, "z": 61.5 }, "A4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 70.7, "z": 61.5 }, "B3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 44.6, "z": 61.5 }, "C3": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 83.7, "y": 18.6, "z": 61.5 }, "A5": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 70.7, "z": 61.5 }, "B4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 44.6, "z": 61.5 }, "C4": { "depth": 34.5, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 104.7, "y": 18.6, "z": 61.5 }, "D1": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 97.7, "z": 58 }, "D2": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 104.7, "z": 58 }, "D3": { "depth": 38, "totalLiquidVolume": 300, "shape": "circular", "diameter": 10, "x": 64.8, "y": 111.7, "z": 58 } }, "groups": [{ "metadata": { "displayName": "Omni-Stainer S12 (for slides) with Thermal Sheath_Offset", "displayCategory": "wellPlate", "wellBottomShape": "flat" }, "brand": { "brand": "Parhelia", "brandId": ["Omni-Stainer S12 with Thermal Sheath_Offset"] }, "wells": ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "D1", "D2", "D3"] }], "parameters": { "format": "irregular", "quirks": [], "isTiprack": false, "isMagneticModuleCompatible": false, "loadName": "omni_stainer_s12_slides_with_thermosheath_offset" }, "namespace": "custom_beta", "version": 1, "schemaVersion": 2, "cornerOffsetFromSlot": { "x": 0, "y": 0, "z": 0 } }""",
    "parhelia_12trough": """{"ordering":[["A1"], ["A2"],["A3"],["A4"],["A5"],["A6"],["A7"],["A8"],["A9"],["A10"],["A11"],["A12"]],"brand":{"brand":"Parhelia","brandId":["12trough"]},"metadata":{"displayName":"Parhelia12-troughreservoir","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.8,"zDimension":44.45},"wells":{"A1":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":13.94,"y":42.9,"z":8},"A2":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":23.03,"y":42.9,"z":8},"A3":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":32.12,"y":42.9,"z":8},"A4":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":41.21,"y":42.9,"z":8},"A5":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":50.3,"y":42.9,"z":8},"A6":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":59.39,"y":42.9,"z":8},"A7":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":68.48,"y":42.9,"z":8},"A8":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":77.57,"y":42.9,"z":8},"A9":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":86.66,"y":42.9,"z":8},"A10":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":95.75,"y":42.9,"z":8},"A11":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":104.84,"y":42.9,"z":8},"A12":{"shape":"rectangular","depth":38,"xDimension":8.33,"yDimension":71.88,"totalLiquidVolume":22000,"x":113.93,"y":42.9,"z":8}},"groups":[{"metadata":{"displayName":"Parhelia12-troughreservoir","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["12trough"]},"wells":["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_12trough"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":1,"y":-1,"z":-0.6}}""",
    "parhelia_skirted_96_with_strips": """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"],"links":["https://www.parheliabio.com"]},"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.48,"zDimension":25},"wells":{"H1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":10,"z":6},"G1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":19,"z":6},"F1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":28,"z":6},"E1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":37,"z":6},"D1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":46,"z":6},"C1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":55,"z":6},"B1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":64,"z":6},"A1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":73,"z":6},"H2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":10,"z":6},"G2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":19,"z":6},"F2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":28,"z":6},"E2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":37,"z":6},"D2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":46,"z":6},"C2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":55,"z":6},"B2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":64,"z":6},"A2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":73,"z":6},"H3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":10,"z":6},"G3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":19,"z":6},"F3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":28,"z":6},"E3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":37,"z":6},"D3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":46,"z":6},"C3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":55,"z":6},"B3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":64,"z":6},"A3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":73,"z":6},"H4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":10,"z":6},"G4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":19,"z":6},"F4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":28,"z":6},"E4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":37,"z":6},"D4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":46,"z":6},"C4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":55,"z":6},"B4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":64,"z":6},"A4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":73,"z":6},"H5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":10,"z":6},"G5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":19,"z":6},"F5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":28,"z":6},"E5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":37,"z":6},"D5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":46,"z":6},"C5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":55,"z":6},"B5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":64,"z":6},"A5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":73,"z":6},"H6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":10,"z":6},"G6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":19,"z":6},"F6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":28,"z":6},"E6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":37,"z":6},"D6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":46,"z":6},"C6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":55,"z":6},"B6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":64,"z":6},"A6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":73,"z":6},"H7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":10,"z":6},"G7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":19,"z":6},"F7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":28,"z":6},"E7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":37,"z":6},"D7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":46,"z":6},"C7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":55,"z":6},"B7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":64,"z":6},"A7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":73,"z":6},"H8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":10,"z":6},"G8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":19,"z":6},"F8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":28,"z":6},"E8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":37,"z":6},"D8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":46,"z":6},"C8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":55,"z":6},"B8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":64,"z":6},"A8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":73,"z":6},"H9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":10,"z":6},"G9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":19,"z":6},"F9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":28,"z":6},"E9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":37,"z":6},"D9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":46,"z":6},"C9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":55,"z":6},"B9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":64,"z":6},"A9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":73,"z":6},"H10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":10,"z":6},"G10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":19,"z":6},"F10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":28,"z":6},"E10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":37,"z":6},"D10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":46,"z":6},"C10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":55,"z":6},"B10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":64,"z":6},"A10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":73,"z":6},"H11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":10,"z":6},"G11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":19,"z":6},"F11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":28,"z":6},"E11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":37,"z":6},"D11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":46,"z":6},"C11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":55,"z":6},"B11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":64,"z":6},"A11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":73,"z":6},"H12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":10,"z":6},"G12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":19,"z":6},"F12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":28,"z":6},"E12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":37,"z":6},"D12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":46,"z":6},"C12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":55,"z":6},"B12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":64,"z":6},"A12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":73,"z":6}},"groups":[{"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_skirted_96_with_strips"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}""",
}

def dict2obj(dict1):
    # using json.loads method and passing json.dumps
    # method and custom object hook as arguments
    return json.loads(json.dumps(dict1), object_hook=Object)


def loadLabwareFromDict(labwareName, protocol_or_tempmodule, position=-1, z_offset=0):
    LABWARE_DEF = json.loads(labware_defs[labwareName])
    LABWARE_DEF['dimensions']['zDimension'] += z_offset

    WELLS = LABWARE_DEF['wells']

    for k in WELLS.keys():
        WELLS[k]['z'] += z_offset

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

#End of jupyter notebook labware stuff
def washSamples(pipette, sourceLiquid, samples, volume, num_repeats=1, height_offset=0, aspiration_offset=0,
                dispensing_offset=0, keep_tip=False):
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


def puncture_wells(pipette, wells, top_offset=-5, height_offset=0, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    if not pipette.has_tip: pipette.pick_up_tip()

    for well in wells:
        if isinstance(well, ParLiquid):
            well = well.wells[well.current_well]  # access the current well in use by the ParLiquid
        else:
            print(
                "warning: please don't pass the well directly, instead pass ParLiquid as an argument. \n this way we can track the liquid types and the volumes used")
        pipette.aspirate(1, well.top(top_offset), rate=well_flow_rate)
        pipette.dispense(1, well.top(top_offset), rate=well_flow_rate)
    if not keep_tip: pipette.drop_tip()


def dilute_and_apply_fixative(pipette, sourceSolution, dilutant_buffer, samples, volume, height_offset=0,
                              keep_tip=False):
    if not pipette.has_tip: pipette.pick_up_tip()
    # Diluting fixative:
    sourceSolutionWell = sourceSolution.wells[
        sourceSolution.current_well]  # access the current well in use by the ParLiquid
    dilutant_buffer_well = dilutant_buffer.wells[
        dilutant_buffer.current_well]  # access the current well in use by the ParLiquid

    if sourceSolution.volume - sourceSolution.volume_used < volume:
        sourceSolution.next_well()  # update to the next well
        sourceSolutionWell = sourceSolution.wells[sourceSolution.current_well]  # update the current well
        if sourceSolution.volume - sourceSolution.volume_used < volume:
            raise Exception(f"Liquid depleted: {sourceSolution}")
    sourceSolution.volume_used += volume

    pipette.aspirate(volume, dilutant_buffer_well, rate=well_flow_rate)
    pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)

    for iterator in range(0, 3):
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)

    washSamples(pipette, sourceSolutionWell, [samples.wells[samples.current_well]], volume, 1, height_offset,
                keep_tip=keep_tip)


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
    if not pipette.has_tip: pipette.pick_up_tip()

    for i in range(0, num_repeats):
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()


def openShutter(protocol, pipette, covered_lbwr, use_tip=False):
    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].bottom(0), force_direct=True)
        protocol.delay(seconds=1)
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].top(-5))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].top(-5), force_direct=True)
        protocol.delay(seconds=1)

def closeShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False):
    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].bottom(0), force_direct=True)
        protocol.delay(seconds=1)
        if not keep_tip:
            pipette.drop_tip()
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].top(-10))
        pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].top(-10), force_direct=True)
        protocol.delay(seconds=1)

labwarePositions = dict2obj({
    "heatmodule": 7,
    "tiprack_300_1": 6
})

#######################
metadata = {
    'protocolName': 'TestQIplateS12thermoloadlabware',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'TestQIplateS12thermoloadlabware',
    'apiLevel': '2.13'
}
###############
def run(protocol: protocol_api.ProtocolContext):
    protocol.home()

    # Create a new ColdPlateSlimDriver instance, 50 here is 50mm tall coldplate
    temp_mod = ColdPlateSlimDriver( protocol, "/dev/ttyUSB0")

    if labwarePositions.heatmodule >= 10:
        raise Exception("heat module cannot be in positions 10 or 11")

    omnistainer_type = "omni_stainer_s12_slides_with_thermosheath_on_coldplate"
    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.heatmodule, 'omni-stainer')

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1,
                                          'tiprack 300ul 1')

    pipette_300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_300_1])

    # Set temperature and wait for it to reach the target
    temp_mod.set_temp_andWait(45)  # let's say we want to set the temperature to 25 degrees Celsius

    if not pipette_300.has_tip:
        pipette_300.pick_up_tip()

    for well in omnistainer.wells():
        pipette_300.move_to(well.top(0))
        protocol.pause("confirm placement")
        pipette_300.move_to(well.bottom(0))
        protocol.pause("confirm placement")

    openShutter(protocol, pipette_300, omnistainer, use_tip=True)
    closeShutter(protocol, pipette_300, omnistainer, use_tip=True)

    openShutter(protocol, pipette_300, omnistainer, use_tip=False)
    closeShutter(protocol, pipette_300, omnistainer, use_tip=False)

    # Print current temperature
    print("Current temperature is: " + str(temp_mod.get_temp()))

    temp_mod.temp_off()