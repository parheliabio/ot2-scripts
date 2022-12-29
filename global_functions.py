## VERAO GLOBAL

### GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###
from opentrons import protocol_api
import json

class Object:
    pass

####################GENERAL SETUP################################
stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.2
extra_bottom_gap=0

def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, height_offset=0, keep_tip=False):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    print('Samples are:')
    print(samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

    height_offset += extra_bottom_gap

    for i in range(0, num_repeats):
        for s in samples:
            print(s)
            print("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(height_offset), rate=sample_flow_rate)
            stats.volume += volume

    if not keep_tip: pipette.drop_tip()

def puncture_wells(pipette, wells, height_offset=0, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    for well in wells:
        washSamples(pipette, well, well, 1, 1, height_offset, keep_tip=keep_tip)

def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume, height_offset=0, keep_tip=False):

    if not pipette.has_tip: pipette.pick_up_tip()
    # Diluting fixative:
    pipette.aspirate(volume, dilutant_buffer_well, rate=well_flow_rate)
    pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    for iterator in range(0, 3):
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)

    washSamples(pipette, sourceSolutionWell, samples, volume, height_offset, keep_tip)


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

def openShutter(protocol, pipette, covered_lbwr, keep_tip=False):
    if not pipette.has_tip:
        pipette.pick_up_tip()
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].bottom(0), force_direct=True)
    protocol.delay(seconds=1)
    if not keep_tip: pipette.drop_tip()


def closeShutter(protocol, pipette, covered_lbwr, keep_tip=False):
    if not pipette.has_tip:
        pipette.pick_up_tip()
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].bottom(0), force_direct=True)
    protocol.delay(seconds=1)
    if not keep_tip: pipette.drop_tip()

### END VERAO GLOBAL