## VERAO GLOBAL
## (С) Parhelia Biosciences Corporation 2024-2025
## Last updated by nwedin May 23rd 2024
## apply_and_incubate has 2 named parameters added: step_repeats and new_tip
## fixed a bug in quick_temp where the temp was calculated in minutes, but time.delay was in seconds
## fixed a bug where closeShutter was giving comment "opening the shutter"
### GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###

from opentrons import protocol_api
import json
from collections import defaultdict
import serial
import opentrons.protocol_api
import time
from itertools import chain

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

class Table:
    def __init__(self, rows, columns, values):
        self.rows = rows
        self.columns = columns
        self.values = values
        self.populate_wells_dict()

    def __init__(self, text):
        lines = text.splitlines()
        #deleting the first line if it's empty
        if not lines[0]:
            lines.pop(0)
        #print ('lines:')
        #print(lines)
        columns = lines[0].split()
        #print ('columns:')
        #print(columns)
        lines.pop(0)
        #print ('lines after pop(0):')
        #print(lines)
        lines = [x.split() for x in lines]
        #print ('lines after splitting:')
        #print(lines)
        rows = [x.pop(0) for x in lines]
        #print ('rows:')
        #print(rows)

        values  = [[(None if y == "." else y.split("|")) for y in x] for x in lines]
        #print ('values:')
        #print(values)
        self.rows       = rows
        self.columns    = columns
        self.values     = values
        self.populate_wells_dict()

    def populate_wells_dict(self):
        self.xy_index = defaultdict()
        for i in range (len(self.rows)):
            for j in range (len(self.columns)):
                key_val = self.values[i][j]
                if key_val is None: continue
                key = key_val[0]
                if key in self.xy_index: raise Exception("Duplicate key: " + key)
                self.xy_index[key]=(i, j)

class ColdPlateSlimDriver:
    def __init__(
            self,
            protocol_context,
            temp_mode_number=0,
            max_temp_lag=0,
            heating_rate_deg_per_min=100,
            cooling_rate_deg_per_min=100,
    ):
        self.serial_number = "29517"
        self.device_name = "/dev/ttyUSB" + str(temp_mode_number)
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.read_timeout = 2
        self.write_timeout = 2
        self.height = 45

        self.temp = 20
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

    def time_to_reach_sample_temp(self, delta_temp):
        x = delta_temp
        if(x>0):
            time = 0.364 + 0.559*x -0.0315*x**2 + 1.29E-03*x**3 -2.46E-05*x**4 + 2.21E-07*x**5 -7.09E-10*x**6
        else:
            time = -0.1 -0.329*x -0.00413*x**2 -0.0000569*x**3 + 0.0000000223*x**4
        return time

    def quick_temp(self, temp_target, overshot = 10, undershot=3):
        start_temp = self.get_temp()
        delta_temp = temp_target - start_temp

        if delta_temp > 0:
            overshot_temp = min(temp_target + overshot, 99.9)
            undershot_temp = delta_temp - undershot
        else:
            overshot_temp = max(temp_target - overshot, -10)
            undershot_temp = delta_temp + undershot

        delay_min = self.time_to_reach_sample_temp(undershot_temp)

        self.set_temp(overshot_temp)
        if testmode:
            delay_min = 0.1
        self.protocol.delay(minutes=delay_min, msg="quick_temp from " + str(start_temp) + " to " + str(temp_target))
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
            for k in range(2):
                pipette.move_to(sourceWell.bottom(k+1))
                time.sleep(0.33)
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

def moveShutter(protocol, pipette, covered_lbwr, keep_tip, use_tip, rate, repeats, top_offset, move_open):
    if move_open:
        protocol.comment("opening the shutter")
    else:
        protocol.comment("closing the shutter")

    well1 = covered_lbwr.wells()[len(covered_lbwr.wells()) - 2]
    well2 = covered_lbwr.wells()[len(covered_lbwr.wells()) - (1 if move_open else 3)]

    if use_tip:
        if not pipette.has_tip:
            pipette.pick_up_tip()
        loc1 = well1.bottom(0)
        loc2 = well2.bottom(0)
    else:
        if pipette.has_tip:
            pipette.drop_tip()
        loc1 = well1.top(top_offset)
        loc2 = well2.top(top_offset)

    pipette.move_to(loc1)

    speed = pipette.default_speed

    pipette.default_speed = speed*rate

    for i in range(repeats):
        for l in [loc1, loc2]:
            pipette.move_to(l, force_direct=True)

    pipette.default_speed = speed

    if use_tip and not keep_tip:
        pipette.drop_tip()

def openShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False, rate=1, repeats=2, top_offset=-12):
    moveShutter(protocol, pipette, covered_lbwr, keep_tip, use_tip, rate, repeats, top_offset, move_open=True)

def closeShutter(protocol, pipette, covered_lbwr, keep_tip=False, use_tip=False, rate=1, repeats=2, top_offset=-12):
    moveShutter(protocol, pipette, covered_lbwr, keep_tip, use_tip, rate, repeats, top_offset, move_open=False)
    pipette.move_to(protocol.fixed_trash)

def apply_and_incubate(
        protocol,
        pipette,
        source,
        reagent_name,
        target_wells,
        volume,
        step_repeats,
        incubation_time,
        dispense_repeats=1,
        puncture=True,
        new_tip='once'
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
                pipette.distribute(
                    volume,
                    source,
                    target_wells,
                    new_tip=new_tip,
                    disposal_volume=0,
                    blowout=False
                )
        else:
            for i in range(dispense_repeats):
                pipette.transfer(
                    volume,
                    source,
                    target_wells,
                    new_tip=new_tip,
                    disposal_volume=0,
                    blowout=False
                )
        protocol.home()
        if testmode:
            protocol.comment("TEST MODE!!! Incubation skipped")
        else:
            protocol.delay(minutes=incubation_time, msg=reagent_name + " incubation")

def safe_delay(protocol, *args, **kwargs):
    if testmode:
        protocol.delay(seconds=5, msg="TEST MODE delay: " + kwargs.get('msg',""))
    else:
        protocol.delay(*args, **kwargs)

def distribute_between_samples(
        pipette,
        sourceSolutionWell,
        samples,
        volume,
        num_repeats=1,
        keep_tip=False
):

    if not pipette.has_tip:
        pipette.pick_up_tip()

    for i in range(num_repeats):
        pipette.distribute(volume, sourceSolutionWell, samples, new_tip='Never', disposal_volume=0)

    if not keep_tip:
        pipette.drop_tip()


def lift_coverpads(pipette, sample_chambers, z_offset = -2.85, rate = 0.01, reps = 3):
    for s in sample_chambers:
        pipette.move(s.bottom(0))
        for i in range(reps):
            pipette.move(s.bottom(z_offset) , rate = rate)
            pipette.move(s.bottom(0)        , rate = rate)

def set_gantry_speeds(protocol, XYrate, Zrate):
    protocol.max_speeds.update({
        'X': (600 * XYrate),
        'Y': (400 * XYrate),
        'Z': (125 * Zrate),
        'A': (125 * Zrate),
    })

    speed_max = max(protocol.max_speeds.values())

    for instr in protocol.loaded_instruments.values():
        instr.default_speed = speed_max


### END VERAO GLOBAL
