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


# This is just for jupyter lab runs
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


# End of jupyter notebook labware stuff
# Below is washSamples puncture_wells and dilute_and_appply_fixation for well based methods, not ParLiquid Class
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, height_offset=0, aspiration_offset=0, dispensing_offset=0, keep_tip=False):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    print('Samples are:')
    print(samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

    for i in range(0, num_repeats):
        for s in samples:
            print(s)
            print("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell.bottom(height_offset+aspiration_offset), rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(height_offset+dispensing_offset), rate=sample_flow_rate)

    if not keep_tip: pipette.drop_tip()

def puncture_wells(pipette, wells, height_offset=0, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    for well in wells:
        washSamples(pipette, well, well, 1, 1, height_offset, keep_tip=True)
    if not keep_tip: pipette.drop_tip()

def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume, height_offset=0, keep_tip=False):

    if not pipette.has_tip: pipette.pick_up_tip()
    # Diluting fixative:
    pipette.aspirate(volume, dilutant_buffer_well, rate=well_flow_rate)
    pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    for iterator in range(0, 3):
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)

    washSamples(pipette, sourceSolutionWell, samples, volume, 1, height_offset, keep_tip=keep_tip)

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


metadata = {
    'protocolName': 'Parhelia CODEX v13',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX/PhenoCycler Sample Prep/Antibody Screening w/ ColdPlateSlimDriver',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = "omni_stainer_s12_slides_with_thermosheath_on_coldplate"

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='FFPE mode (skip initial 1.6% PFA fixation)' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='Manual Overnight incubation: enable manual pausing at the antibody incubation step?' TYPE=BOOLEAN
protocol_pause = False

### VERAO VAR NAME='Automated antibody incubation: use ColdPlate at 4C for the antibody incubation step?' TYPE=BOOLEAN
coldplate_incubation = True

"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the omnistainer device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the 96-well plate
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""

### VERAO VAR NAME='Antibody screening mode' TYPE=BOOLEAN
Antibody_Screening = True

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 3

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=900 DECIMAL=FALSE
ab_incubation_time_minutes = 480

### VERAO VAR NAME='Sample wash volume (150ul for slides/100ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody mix volume (110ul for slides/60ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Aspiration height offset(mm, for calibration debugging)'  TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=TRUE INCREMENT=0.1
aspiration_gap = 0

### VERAO VAR NAME='Dispensing height offset (mm, for calibration debugging)'  TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=TRUE INCREMENT=0.1
dispensing_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 pipette model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'
### VERAO VAR NAME='Antibody cocktail incubation temperature' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
antibody_incubation_temp = 4

### VERAO VAR NAME='Temperature Module Position' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
heatmodule_position = 7

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_buffers_plate_position = 1

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer w/ Thermosheath w/ ColdPlate' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
omnistainer_position = 7

### VERAO VAR NAME='Deck position: Preblock/Antibody/F reagents plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_reagents_plate_position = 3

### VERAO VAR NAME='Deck position: 300ul tip rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='Deck position: 300ul tip rack#2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 9

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    labwarePositions = {
        "codex_buffers_plate": codex_buffers_plate_position,
        "omnistainer": omnistainer_position,
        "codex_reagents_plate": codex_reagents_plate_position,
        "tiprack_300_1": tiprack_300_1_position,
        "tiprack_300_2": tiprack_300_2_position,
        "heatmodule": heatmodule_position,
    }
    protocol.home()


    temp_mod = ColdPlateSlimDriver(protocol, "/dev/ttyUSB0", max_temp_lag=15,
                 heating_rate_deg_per_min=10, cooling_rate_deg_per_min=2)

    if labwarePositions['heatmodule'] >= 10:
        raise Exception("heat module cannot be in positions 10 or 11")

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions['heatmodule'], 'omni-stainer')

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions['tiprack_300_1'],
                                          'tiprack 300ul 1')
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions['tiprack_300_2'],
                                          'tiprack 300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_300_1, tiprack_300_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos - 1]

    codex_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions['codex_buffers_plate'],
                                           'codex_12-trough buffers reservoir')
    CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions['codex_reagents_plate'],
                                                   '96-well-plate')

    codex_buffer_wells = codex_trough12.wells_by_name()

    codex_buffers = Object()
    codex_buffers.Hydration_PFA_1pt6pct = codex_buffer_wells['A1']
    codex_buffers.Staining = codex_buffer_wells['A2']
    codex_buffers.Storage_PFA_4pct = codex_buffer_wells['A3']
    codex_buffers.MeOH = codex_buffer_wells['A4']
    codex_buffers.PBS = codex_buffer_wells['A5']
    codex_buffers.CODEX_buffer_1x = codex_buffer_wells['A6']
    codex_buffers.Screening_Buffer = codex_buffer_wells['A7']
    codex_buffers.Stripping_buffer = codex_buffer_wells['A8']
    codex_buffers.storage = codex_buffer_wells['A9']

    codex_preblock_wells = CODEX_reagents_96plate.rows()[0]
    codex_antibody_wells = CODEX_reagents_96plate.rows()[1]
    codex_reagent_F_wells = CODEX_reagents_96plate.rows()[2]
    codex_rendering_wells = CODEX_reagents_96plate.rows()[3]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer, use_tip=False)
    if not FFPE:
        # WASHING SAMPLES WITH PFA
        protocol.comment("puncturing first fix")
        puncture_wells(pipette_300, codex_buffers.Hydration_PFA_1pt6pct, height_offset=30)
        protocol.comment("first fix")
        washSamples(pipette_300, codex_buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=10, msg="first fix incubation")

    # WASHING SAMPLES WITH S2
    protocol.comment("puncture S2")
    puncture_wells(pipette_300, codex_buffers.Staining, height_offset=30)
    protocol.comment("wash in S2")
    washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)

    # PUNCTURING THE PREBLOCK
    protocol.comment("puncturing the preblock")
    for i in range(num_samples):
        puncture_wells(pipette_300, codex_preblock_wells[i], height_offset=12, keep_tip=True)
    if pipette_300.has_tip: pipette_300.drop_tip()

    # WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    for i in range(num_samples):
        washSamples(pipette_300, codex_preblock_wells[i], sample_chambers[i], wash_volume, 1, keep_tip=True)
    # INCUBATE

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    protocol.delay(minutes=15, msg="preblocking incubation")

    # APPLYING ANTIBODY COCKTAILS TO SAMPLES

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer, use_tip=False)

    protocol.comment("applying antibodies")
    for i in range(num_samples):
        protocol.comment("puncturing antibodies")
        puncture_wells(pipette_300, codex_antibody_wells[i], height_offset=12)
        protocol.comment("applying antibodies")
        washSamples(pipette_300, codex_antibody_wells[i], sample_chambers[i], ab_volume, 1)
    # INCUBATE
    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    if protocol_pause:
        protocol.pause(msg="The protocol is paused for manual primary ab incubation")

    if coldplate_incubation and omnistainer_type == "omni_stainer_s12_slides_with_thermosheath_on_coldplate":
        # Default incubation temp is 4C
        temp_mod.set_temp_andWait(antibody_incubation_temp, timeout_min=ab_incubation_time_minutes,
                                  msg="staining incubation on coldplate")
        print(f"staining incubation on coldplate: {ab_incubation_time_minutes} temp: {antibody_incubation_temp}")

        temp_mod.temp_off()
        # If we wanted to leave at 4C this temp_off would be deleted

        print(f"cooling stopped")
        # If we wanted to do room temp between the cold steps that would go here

    else:
        protocol.delay(minutes=ab_incubation_time_minutes, msg="staining incubation")

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer, use_tip=False)
    for i in range(2):
        # WASHING SAMPLES WITH Staining buffer
        protocol.comment("first washing with Staining buffer")
        washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)
        # INCUBATE
        protocol.delay(minutes=5, msg="first incubation in Staining Buffer")

    # POST STAINING FIXING SAMPLES WITH PFA
    protocol.comment("puncturing the second fix")
    puncture_wells(pipette_300, codex_buffers.Storage_PFA_4pct, height_offset=30)
    protocol.comment("second fix")
    washSamples(pipette_300, codex_buffers.Storage_PFA_4pct, sample_chambers, wash_volume, 1)
    # INCUBATE
    protocol.delay(minutes=5, msg="incubation with fixative")

    # WASHING SAMPLES WITH PBS
    protocol.comment("puncture the PBS wash")
    puncture_wells(pipette_300, codex_buffers.PBS)
    protocol.comment("the PBS wash")
    washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)

    # FIXING SAMPLES WITH Methanol
    protocol.comment("puncturing the Methanol")
    puncture_wells(pipette_300, codex_buffers.MeOH, height_offset=30)
    for i in range(2):
        protocol.comment("applying MeOH")
        washSamples(pipette_300, codex_buffers.MeOH, sample_chambers, wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=2.5, msg="MeOH incubation")

    # FIXING SAMPLES WITH Methanol
    protocol.comment("puncturing the Methanol")
    puncture_wells(pipette_300, codex_buffers.MeOH, height_offset=30)

    # If the omnistainer_type is "omni_stainer_s12_slides_with_thermosheath_on_coldplate",
    # set the temperature of the ColdPlate to 4°C before applying the cold methanol
    if omnistainer_type == "omni_stainer_s12_slides_with_thermosheath_on_coldplate":
        methanol_fixation_temp = 4  # Temperature for methanol fixation in Celsius
        temp_mod.set_temp_andWait(methanol_fixation_temp, timeout_min=10,
                                  msg="Cooling staining chamber for cold methanol fixation")
        print(f"Setting ColdPlate to {methanol_fixation_temp}°C for cold methanol fixation")

    # Slow down the dispensing rate for the cold methanol fixation
    pipette_300.flow_rate.dispense = 0.05

    # Apply the methanol
    for i in range(2):
        protocol.comment("applying MeOH")
        washSamples(pipette_300, codex_buffers.MeOH, sample_chambers, wash_volume, 1)

    # Reset the dispensing rate back to its original value
    pipette_300.flow_rate.dispense = sample_flow_rate

    # INCUBATE
    if omnistainer_type == "omni_stainer_s12_slides_with_thermosheath_on_coldplate":
        temp_mod.set_temp_andWait(methanol_fixation_temp, timeout_min=2.5, msg="MeOH incubation at 4°C on ColdPlate")
        print(f"Methanol incubation at 4°C on ColdPlate: 2.5 minutes")

        temp_mod.temp_off()
    else:
        protocol.delay(minutes=2.5, msg="MeOH incubation at room temperature")

    # WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)

    # PUNCTURING THE FIXATIVE
    protocol.comment("puncturing the fixative")
    for i in range(num_samples):
        puncture_wells(pipette_300, codex_reagent_F_wells[i], height_offset=12, keep_tip=True)
    if pipette_300.has_tip: pipette_300.drop_tip()

    # DILUTING AND APPLYING THE FIXATIVE
    protocol.comment("applying the fixative")
    for i in range(num_samples):
        dilute_and_apply_fixative(pipette_300, codex_reagent_F_wells[i], codex_buffers.PBS, sample_chambers[i],
                                  ab_volume, keep_tip=True)

    protocol.comment("third fix incubation")

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    protocol.delay(minutes=10, msg="Reagent F incubation")

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer, use_tip=False)

    # WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2)

    if Antibody_Screening:
        protocol.comment("puncture the Codex Buffer")
        puncture_wells(pipette_300, codex_buffers.CODEX_buffer_1x, keep_tip=True)
        protocol.comment("puncture the Screening Buffer")
        puncture_wells(pipette_300, codex_buffers.Screening_Buffer, keep_tip=True)
        protocol.comment("puncture the Stripping Buffer")
        puncture_wells(pipette_300, codex_buffers.Stripping_buffer)
        # PRE-CLEARING THE TISSUE
        for i in range(3):
            protocol.comment("tissue clearing round" + str(i + 1))
            washSamples(pipette_300, codex_buffers.Stripping_buffer, sample_chambers, wash_volume, 2)
            protocol.delay(seconds=30)
            washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 1)
            washSamples(pipette_300, codex_buffers.CODEX_buffer_1x, sample_chambers, wash_volume, 1)

        # Equilibration in rendering buffer
        protocol.comment("Equilibration in rendering buffer")
        washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 1)

        # RENDERING
        protocol.comment("Applying rendering solution to wells")
        for i in range(num_samples):
            protocol.comment("puncturing the rendering solution")
            puncture_wells(pipette_300, codex_rendering_wells[i], height_offset=12)
            protocol.comment("Applying the rendering solution to the wells")
            washSamples(pipette_300, codex_rendering_wells[i], sample_chambers[i], wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=10, msg="rendering hybridization")

        # WASH SAMPLES IN 1x CODEX buffer
        protocol.comment("Washing with rendering buffer")
        washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 2)

    # STORAGE, washing samples every hour for 100 hours
    protocol.comment("puncturing the storage buffer")
    puncture_wells(pipette_300, codex_buffers.storage)
    protocol.comment("applying the storage buffer")
    washSamples(pipette_300, codex_buffers.storage, sample_chambers, wash_volume, 2)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)
