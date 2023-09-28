## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
## Last updated by nsamusik 9/7/2023
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
            my_device_name="/dev/ttyUSB0",
            max_temp_lag=0,
            heating_rate_deg_per_min=100,
            cooling_rate_deg_per_min=100,
    ):
        self.serial_number = "29517"
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

    def set_temp_andWait(self, target_temp, timeout_min=30, tolerance=0.5):
        interval_sec = 10
        SEC_IN_MIN = 60

        curr_temp = self.get_temp()
        self.protocol.comment(
            f"Setting temperature. Current temp: {curr_temp}\nTarget temp: {target_temp}"
        )

        temp_diff = target_temp - curr_temp
        temp_lag = self.max_temp_lag * (abs(temp_diff) / 100.0)

        if temp_diff > 0:
            temp_step = self.heating_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            self.protocol.comment(f"Heating rate: {temp_step}")
        else:
            temp_step = -self.cooling_rate_deg_per_min * (interval_sec / SEC_IN_MIN)
            self.protocol.comment(f"Cooling rate: {temp_step}")

        while abs(target_temp - curr_temp) > abs(temp_step):
            curr_temp += temp_step
            self.set_temp(curr_temp)
            self.protocol.comment(f"Ramping the temp to: {curr_temp}")
            time.sleep(interval_sec)
            curr_temp = self.get_temp()
            self.protocol.comment(f"Actual temp: {curr_temp}")

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

        self.protocol.comment(
            f"Target reached, equilibrating for {temp_lag} minutes"
        )
        if not self.protocol.is_simulating():  # Skip delay during simulation
            time.sleep(temp_lag * SEC_IN_MIN)
        return target_temp

    def temp_off(self):
        if self.serial_object is None:
            self.temp = 25
        else:
            self._send_command("tempOff")

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
    "parhelia_skirted_96_with_strips": """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"],"links":["https://www.parheliabio.com"]},"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayVolumeUnits":"mL","displayCategory":"reservoir","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.48,"zDimension":25},"wells":{"H1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":10,"z":6},"G1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":19,"z":6},"F1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":28,"z":6},"E1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":37,"z":6},"D1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":46,"z":6},"C1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":55,"z":6},"B1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":64,"z":6},"A1":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":14,"y":73,"z":6},"H2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":10,"z":6},"G2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":19,"z":6},"F2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":28,"z":6},"E2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":37,"z":6},"D2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":46,"z":6},"C2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":55,"z":6},"B2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":64,"z":6},"A2":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":23,"y":73,"z":6},"H3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":10,"z":6},"G3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":19,"z":6},"F3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":28,"z":6},"E3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":37,"z":6},"D3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":46,"z":6},"C3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":55,"z":6},"B3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":64,"z":6},"A3":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":32,"y":73,"z":6},"H4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":10,"z":6},"G4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":19,"z":6},"F4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":28,"z":6},"E4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":37,"z":6},"D4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":46,"z":6},"C4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":55,"z":6},"B4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":64,"z":6},"A4":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":41,"y":73,"z":6},"H5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":10,"z":6},"G5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":19,"z":6},"F5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":28,"z":6},"E5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":37,"z":6},"D5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":46,"z":6},"C5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":55,"z":6},"B5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":64,"z":6},"A5":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":50,"y":73,"z":6},"H6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":10,"z":6},"G6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":19,"z":6},"F6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":28,"z":6},"E6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":37,"z":6},"D6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":46,"z":6},"C6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":55,"z":6},"B6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":64,"z":6},"A6":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":59,"y":73,"z":6},"H7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":10,"z":6},"G7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":19,"z":6},"F7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":28,"z":6},"E7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":37,"z":6},"D7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":46,"z":6},"C7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":55,"z":6},"B7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":64,"z":6},"A7":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":68,"y":73,"z":6},"H8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":10,"z":6},"G8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":19,"z":6},"F8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":28,"z":6},"E8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":37,"z":6},"D8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":46,"z":6},"C8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":55,"z":6},"B8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":64,"z":6},"A8":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":77,"y":73,"z":6},"H9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":10,"z":6},"G9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":19,"z":6},"F9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":28,"z":6},"E9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":37,"z":6},"D9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":46,"z":6},"C9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":55,"z":6},"B9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":64,"z":6},"A9":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":86,"y":73,"z":6},"H10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":10,"z":6},"G10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":19,"z":6},"F10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":28,"z":6},"E10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":37,"z":6},"D10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":46,"z":6},"C10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":55,"z":6},"B10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":64,"z":6},"A10":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":95,"y":73,"z":6},"H11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":10,"z":6},"G11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":19,"z":6},"F11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":28,"z":6},"E11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":37,"z":6},"D11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":46,"z":6},"C11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":55,"z":6},"B11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":64,"z":6},"A11":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":104,"y":73,"z":6},"H12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":10,"z":6},"G12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":19,"z":6},"F12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":28,"z":6},"E12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":37,"z":6},"D12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":46,"z":6},"C12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":55,"z":6},"B12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":64,"z":6},"A12":{"depth":19,"shape":"circular","diameter":5.46,"totalLiquidVolume":200,"x":113,"y":73,"z":6}},"groups":[{"metadata":{"displayName":"Parheliaskirted96-wellplatewithstrips","displayCategory":"wellPlate","wellBottomShape":"v"},"brand":{"brand":"Parhelia","brandId":["Parheliaskirted96-wellplatewithstrips"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"parhelia_skirted_96_with_strips"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}""",
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
                rate=sample_flow_rate,
            )
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


### END VERAO GLOBAL
metadata = {
    'protocolName': 'Parhelia Phenoptics/Opal protocol for Mayo',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Multicycle fluorescent TSA protocol compatible with Akoya Phenoptics/Opal platform',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

primary_times = [90, 90, 90, 90, 90, 90]
secondary_times = [30, 30, 30, 30, 30, 30]
retrieval = ['A2', 'A2', 'A2', 'A2', 'A1', 'A1']
tyramide_times = [30, 30, 30, 30, 30, 30]

### VERAO VAR NAME='Double application of key solutions' TYPE=BOOLEAN
double_add = False

### VERAO VAR NAME='Delayed start' TYPE=BOOLEAN
delayed_start = False

### VERAO VAR NAME='DAPI: enable manual pausing before the DAPI staining?' TYPE=BOOLEAN
preDAPI_pause = True

### VERAO VAR NAME='Protocol start delay time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
protocol_delay_minutes = 30

### VERAO VAR NAME='Preblock time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=90 DECIMAL=FALSE
preblock_time_minutes = 10

### VERAO VAR NAME='Primary ab hyb time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
primary_ab_time_minutes = 60

### VERAO VAR NAME='Secondary ab hyb time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
secondary_ab_time_minutes = 10

### VERAO VAR NAME='TSA time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
tsa_time_minutes = 30

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=200 DECIMAL=FALSE
wash_volume = 130

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=200 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
num_samples = 2

### VERAO VAR NAME='Number of Antibodies' TYPE=NUMBER LBOUND=1 UBOUND=6 DECIMAL=FALSE
num_abs = 6

### VERAO VAR NAME='Temp lag for adjusting the temp' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALS
templag = 10

### VERAO VAR NAME='ER temperature' TYPE=NUMBER LBOUND=1 UBOUND=99 DECIMAL=FALSE
ar_temp = 96

### VERAO VAR NAME='Antibody stripping time' TYPE=NUMBER LBOUND=1 UBOUND=99 DECIMAL=FALSE
ar_time = 20

### VERAO VAR NAME='Room temperature' TYPE=NUMBER LBOUND=15 UBOUND=25 DECIMAL=FALSE
room_temp = 25

### VERAO VAR NAME='Storage Mode after staining' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
storage_temp = 4

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer / Thermosheath / ColdPlate' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='labwarePositions.wash_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
wash_buffers_plate_position = 3

### VERAO VAR NAME='labwarePositions.wash_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
retrieval_buffers_plate_position = 5

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_1 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_1_position = 7

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_2 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_2_position = 8

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_3 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_3_position = 9

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_4 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_4_position = 6

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 10

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 11

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Tip type' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type = 'opentrons_96_tiprack_300ul'

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

labwarePositions = Object()
labwarePositions.wash_buffers_plate = wash_buffers_plate_position
labwarePositions.retrieval_buffers_plate = retrieval_buffers_plate_position
labwarePositions.ab_reagents_plate_1 = ab_reagents_plate_1_position
labwarePositions.ab_reagents_plate_2 = ab_reagents_plate_2_position
labwarePositions.ab_reagents_plate_3 = ab_reagents_plate_3_position
labwarePositions.ab_reagents_plate_4 = ab_reagents_plate_4_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position
labwarePositions.omnistainer = omnistainer_position

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5


#####################CUSTOM LABWARE_DEFINITION###################

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_1 = protocol.load_labware(tip_type, labwarePositions.tiprack_300_1,
                                      'tiprack 200/300ul 1')
    tiprack_2 = protocol.load_labware(tip_type, labwarePositions.tiprack_300_2,
                                      'tiprack 200/300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_1, tiprack_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos - 1]

    # Setting up ColdPlate temperature module and omni-stainer module
    if "coldplate" in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)
        omnistainer = protocol.load_labware(
            omnistainer_type, labwarePositions.omnistainer, "Omni-stainer"
        )
    else:
        temp_mod = protocol.load_module("temperature module", labwarePositions.omnistainer)
        omnistainer = temp_mod.load_labware(omnistainer_type)

    TBS_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.wash_buffers_plate,
                                         '12-trough TBS reservoir')
    TBS_wells = TBS_trough12.wells_by_name()

    buffer_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.retrieval_buffers_plate,
                                            '12-trough buffers reservoir')
    buffer_wells = buffer_trough12.wells_by_name()

    buffers = Object()
    buffers.AR6 = buffer_wells['A1']
    buffers.AR9 = buffer_wells['A2']
    buffers.water = buffer_wells['A3']

    Ab_reagents_96plate_1 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_1,
                                                  '96-well-plate')
    Ab_reagents_96plate_2 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_2,
                                                  '96-well-plate')
    Ab_reagents_96plate_3 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_3,
                                                  '96-well-plate')
    Ab_reagents_96plate_4 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_4,
                                                  '96-well-plate')

    all_reag_rows = Ab_reagents_96plate_1.rows() + Ab_reagents_96plate_2.rows() + Ab_reagents_96plate_3.rows() + Ab_reagents_96plate_4.rows()

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "Omni-Stainer module with current thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        # Remove Exception for new Thermal Sheath Shutters, or if flipping lid on labware definitions
    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)
    protocol.home()

    if delayed_start:
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=protocol_delay_minutes, msg="Delaying the start by " + str(start_delay_min) + " minutes")

    puncture_wells(pipette_300, buffers.AR6, keep_tip=True)
    puncture_wells(pipette_300, buffers.AR9, keep_tip=True)
    puncture_wells(pipette_300, buffers.water, keep_tip=True)

    for i in range(num_samples):
        puncture_wells(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], keep_tip=True)
    pipette_300.drop_tip()

    for z in range(num_abs):

        preblock_wells = all_reag_rows[z * 5]
        antibody_wells = all_reag_rows[z * 5 + 1]
        opal_polymer_wells = all_reag_rows[z * 5 + 2]
        ampl_buffer_wells = all_reag_rows[z * 5 + 3]
        opal_fluorophore_wells = all_reag_rows[z * 5 + 4]


        openShutter(protocol, pipette_300, omnistainer, use_tip=True)

        # WASHING SAMPLES WITH TBS
        protocol.comment("washing in TBS")

        for i in range(len(sample_chambers)):
            washSamples(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                        keep_tip=True)

        #    protocol.delay(minutes=5)
        puncture_wells(pipette_300, preblock_wells[:num_samples], keep_tip=True)
        puncture_wells(pipette_300, antibody_wells[:num_samples])

        protocol.comment("preblocking")
        for i in range(num_samples):
            washSamples(pipette_300, preblock_wells[i], sample_chambers[i], ab_volume, keep_tip=True)
        # INCUBATE
        safe_delay(protocol, minutes=preblock_time_minutes,
                   msg="preblocking incubation: " + str(preblock_time_minutes) + " min")

        # APPLYING ANTIBODY COCKTAILS TO SAMPLES
        protocol.comment("applying primary antibodies")
        if double_add:
            for i in range(num_samples):
                washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume)
            safe_delay(protocol, minutes=1)
        for i in range(num_samples):
            washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume)

        # INCUBATE
        safe_delay(protocol, minutes=primary_times[z],
                   msg="primary antibody incubation: " + str(primary_ab_time_minutes) + " min")

        # WASHING SAMPLES WITH TBS
        # three individual repeats below is because they need particular incubation time between them
        protocol.comment("washing with TBS")
        for k in range(3):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            safe_delay(protocol, minutes=3, msg="TBS wash incubation")
        pipette_300.drop_tip()

        puncture_wells(pipette_300, opal_polymer_wells[:num_samples], keep_tip=True)
        pipette_300.drop_tip()

        # APPLYING OPAL polymer HRP
        protocol.comment("applying opal secondary")

        if double_add:
            for i in range(num_samples):
                washSamples(pipette_300, opal_polymer_wells[i], sample_chambers[i], ab_volume, keep_tip=True)
            safe_delay(protocol, minutes=1)
        for i in range(num_samples):
            washSamples(pipette_300, opal_polymer_wells[i], sample_chambers[i], ab_volume, keep_tip=True)

        pipette_300.drop_tip()

        # INCUBATE
        safe_delay(protocol, minutes=secondary_times[z],
                   msg="Opal secondary incubation for " + str(secondary_ab_time_minutes) + " min")

        # WASHING SAMPLES WITH TBS
        protocol.comment("washing with TBS")
        for k in range(3):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            safe_delay(protocol, minutes=3, msg="TBS wash incubation")

        puncture_wells(pipette_300, opal_fluorophore_wells[:num_samples], keep_tip=True)
        puncture_wells(pipette_300, ampl_buffer_wells[:num_samples], keep_tip=True)
        pipette_300.drop_tip()

        # Opal Signal generation
        protocol.comment("Applying the Opal TSA reagent")
        for i in range(num_samples):
            dilute_and_apply_fixative(pipette_300, opal_fluorophore_wells[i], ampl_buffer_wells[i], sample_chambers[i],
                                      ab_volume)

        if double_add:
            for i in range(num_samples):
                pipette_300.transfer(ab_volume, ampl_buffer_wells[i], opal_fluorophore_wells[i], new_tip='once',
                                     mix_after=(3, ab_volume))
        for i in range(num_samples):
            pipette_300.transfer(ab_volume, ampl_buffer_wells[i], opal_fluorophore_wells[i], new_tip='once',
                                 mix_after=(3, ab_volume))

        if double_add:
            for i in range(num_samples):
                washSamples(pipette_300, opal_fluorophore_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            safe_delay(protocol, minutes=1)
        for i in range(num_samples):
            washSamples(pipette_300, opal_fluorophore_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)

        # INCUBATE
        safe_delay(protocol, minutes=tyramide_times[z], msg="Opal TSA incubation for " + str(tsa_time_minutes) + " min")

        # WASHING SAMPLES WITH TBS
        # three individual repeats below is because they need particular incubation time between them
        protocol.comment("washing with TBS")
        for k in range(3):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            safe_delay(protocol, minutes=3, msg="TBS wash incubation")

        pipette_300.drop_tip()

        # ER/Stripping
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)
        protocol.delay(minutes=1, msg="Incubating in water")

        washSamples(pipette_300, buffer_wells[retrieval[z]], sample_chambers, wash_volume, 2, keep_tip=True)

        closeShutter(protocol, pipette_300, omnistainer, use_tip=True)
        if "coldplate" in omnistainer_type:
            temp_mod.set_temperature(ar_temp)

            protocol.delay(minutes=templag, msg="Equilibrating")

            protocol.delay(minutes=ar_time, msg="ER in progress")
            temp_mod.set_temp(room_temp)

            prevTemp = temp_mod.temperature
            while (temp_mod.get_temp() > room_temp + 1):
                currTemp = temp_mod.temperature
                protocol.delay(seconds=60, msg="cooling down, temp: " + str(currTemp))
                if (prevTemp - currTemp > 10):
                    openShutter(protocol, pipette_300, omnistainer)
                    distribute_between_samples(pipette_300, buffer_wells[retrieval[z]], sample_chambers,
                                               30 * num_samples, 1, keep_tip=True)
                    closeShutter(protocol, pipette_300, omnistainer)
                    prevTemp = currTemp

            protocol.delay(minutes=templag, msg="Equilibrating")

        else:
            temp_mod.set_temperature(25)
            for i in range(1, 36):
                protocol.comment(i)
                temp_mod.set_temperature(25 + 2 * i)
                protocol.delay(40)
            temp_mod.set_temperature(ar_temp)
            protocol.comment("there we are")
            protocol.delay(minutes=ar_time)
            protocol.comment("coming back")
            for i in range(36):
                protocol.comment(i)
                temp_mod.set_temperature(95 - 2 * i)
                protocol.delay(40)
                if i % 5 == 0:
                    if 'thermosheath' in omnistainer_type:
                        openShutter(protocol, pipette_300, omnistainer, keep_tip=True, use_tip=True)
                    distribute_between_samples(pipette_300, buffer_wells[retrieval[z]], sample_chambers,
                                               30 * num_samples, 1, keep_tip=True)
                    if 'thermosheath' in omnistainer_type:
                        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True, use_tip=True)
            protocol.comment("we are back to normal")

            protocol.delay(600)
            if 'thermosheath' in omnistainer_type:
                openShutter(protocol, pipette_300, omnistainer, keep_tip=True, use_tip=True)
            distribute_between_samples(pipette_300, buffer_wells[retrieval[z]], sample_chambers, 30 * num_samples, 1,
                                       keep_tip=True)
            if 'thermosheath' in omnistainer_type:
                closeShutter(protocol, pipette_300, omnistainer, keep_tip=True, use_tip=True)
            protocol.delay(600)

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer, use_tip=True)

    ### ANTI-TAG STAINING
    if num_abs == 6:
        anti_tsa_wells = all_reag_rows[-2]
        protocol.comment("puncturing anti-TSA wells")
        puncture_wells(pipette_300, anti_tsa_wells[:num_samples], keep_tip=True)
        pipette_300.drop_tip()
        for i in range(num_samples):
            washSamples(pipette_300, anti_tsa_wells[i], sample_chambers[i], ab_volume, keep_tip=True)
        pipette_300.drop_tip()
        safe_delay(protocol, minutes=60, msg="incubation in anti-TSA fluorescent antibody")

        for k in range(3):
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            safe_delay(protocol, minutes=3, msg="TBS wash incubation")
    if preDAPI_pause:
        protocol.pause(msg="The protocol is paused before the DAPI staining. Hit resume in OT2 app")
    ### DAPI STAINING
    DAPI_wells = all_reag_rows[-1]
    protocol.comment("puncturing DAPI wells")
    puncture_wells(pipette_300, DAPI_wells[:num_samples], keep_tip=True)
    pipette_300.drop_tip()
    # Washing with DAPI
    for i in range(num_samples):
        washSamples(pipette_300, DAPI_wells[i], sample_chambers[i], ab_volume, keep_tip=True)
    pipette_300.drop_tip()
    safe_delay(protocol, minutes=4, msg="incubation in DAPI")

    for i in range(len(sample_chambers)):
        washSamples(pipette_300, TBS_wells[list(TBS_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                    keep_tip=True)
    safe_delay(protocol, minutes=2, msg="TBS wash incubation")
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)

    closeShutter(protocol, pipette_300, omnistainer, use_tip=True)

    # Storage
    if storage_mode:
        temp_mod.set_temperature(storage_temp)
        protocol.pause(f"Holding at storage temp: {storage_temp} C. Press Resume to reduce")
    if "coldplate" in omnistainer_type:
        temp_mod.temp_off()
    protocol.comment(f"Protocol done - temperature module has been turned off")

