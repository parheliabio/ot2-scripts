
## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
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
aspiration_gap=0
dispensing_gap=0

def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, height_offset=0, aspiration_offset=0, dispensing_offset=0, keep_tip=False):
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

    for i in range(0, num_repeats):
        for s in samples:
            print(s)
            print("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell.bottom(height_offset+aspiration_offset), rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(height_offset+dispensing_offset), rate=sample_flow_rate)
            stats.volume += volume

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

def puncture_wells(pipette, wells, height_offset=-5, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    if not pipette.has_tip: pipette.pick_up_tip()
    for well in wells:
        pipette.aspirate(1, well.top(height_offset), rate=well_flow_rate)
        pipette.dispense(1, well.top(height_offset), rate=well_flow_rate)
    if not keep_tip: pipette.drop_tip()

### END VERAO GLOBAL


metadata = {
    'protocolName': 'Parhelia IHC',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IHC staining protocol for Parhelia Omni-stainer',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################
### VERAO VAR NAME='Baking' TYPE=BOOLEAN
baking = True

### VERAO VAR NAME='Rehydration' TYPE=BOOLEAN
rehydration = True

### VERAO VAR NAME='ANTIGEN RETRIEVAL' TYPE=BOOLEAN
retrieval = False

### VERAO VAR NAME='shall the protocol PAUSE at the primary ab incubation step' TYPE=BOOLEAN
protocol_pause = False

### VERAO VAR NAME='Type of protocol' TYPE=CHOICE OPTIONS=['IHC only','IHC with Hematoxylin','Hematoxylin only']
type_of_protocol = 'Hematoxylin only'

### VERAO VAR NAME='Hematoxylin source' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
hematoxylin_source = 'from pcr strip'

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'par2s_9slides_blue_v3', 'PAR2c_12coverslips']
omnistainer_type = 'omni_stainer_s12_slides'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 1

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

### VERAO VAR NAME='Hematoxylin incubation time (seconds)' TYPE=NUMBER LBOUND=30 UBOUND=1440 DECIMAL=FALSE
hematoxylin_incubation_time_seconds = 60

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

USE_TROUGH = True

### VERAO VAR NAME='Sample wash volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 100

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
buffers_plate_position = 1

### VERAO VAR NAME='labwarePositions.omnistainer' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 7

### VERAO VAR NAME='labwarePositions.ihc_reagents_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ihc_reagents_plate_position = 3

### VERAO VAR NAME='labwarePositions.tiprack_300' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 6

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.ihc_reagents_plate = ihc_reagents_plate_position
labwarePositions.tiprack_300 = tiprack_300_position


###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos - 1]

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    IHC_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ihc_reagents_plate,
                                                 type_of_96well_plate)

    if (not (retrieval or baking)):
        omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    if (retrieval or baking):
        temp_mod = protocol.load_module('temperature module', labwarePositions.omnistainer)
        omnistainer = temp_mod.load_labware(omnistainer_type)

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.retrieval = buffer_wells['A1']
    buffers.TBS_wash = buffer_wells['A2']
    buffers.water = buffer_wells['A3']
    buffers.storage = buffer_wells['A4']
    buffers.eth_70perc = buffer_wells['A5']
    buffers.eth_80perc = buffer_wells['A6']
    buffers.eth_95perc = buffer_wells['A7']
    buffers.eth_100perc = buffer_wells['A8']
    buffers.clear_view = buffer_wells['A9']
    buffers.hematoxylin = buffer_wells['A12']

    preblock_wells = IHC_reagents_96plate.rows()[0]
    antibody_wells = IHC_reagents_96plate.rows()[5]
    enzymeblock_wells = IHC_reagents_96plate.rows()[1]
    hrpsecondaryab_wells = IHC_reagents_96plate.rows()[2]
    substrate_wells = IHC_reagents_96plate.rows()[3]
    DAB_wells = IHC_reagents_96plate.rows()[4]
    hematoxylin_wells = IHC_reagents_96plate.rows()[7]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    if debug: protocol.comment(sample_chambers)

    #################PROTOCOL####################
    protocol.home()
    if baking:
        protocol.comment("baking")
        temp_mod.set_temperature(65)
        protocol.delay(minutes=120)
        temp_mod.set_temperature(25)
        protocol.delay(minutes=20)

    if rehydration:
        #        puncture_wells(pipette_300, buffers.eth_100perc, height_offset=-5, keep_tip=True)
        #        puncture_wells(pipette_300, buffers.eth_95perc, height_offset=-5, keep_tip=True)
        #        puncture_wells(pipette_300, buffers.eth_80perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_70perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_70perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_70perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_70perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_70perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.water, height_offset=-5)

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        #        washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 2, keep_tip=True)
        #        protocol.delay(minutes=1)
        #        washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 2, keep_tip=True)
        #        protocol.delay(minutes=1)
        #        washSamples(pipette_300, buffers.eth_80perc, sample_chambers, wash_volume, 2, keep_tip=True)
        #        protocol.delay(minutes=1)
        washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 1, keep_tip=True)
        washSamples(pipette_300, buffers.clear_view, sample_chambers, wash_volume, 1, keep_tip=True)
        protocol.delay(minutes=1)
        washSamples(pipette_300, buffers.clear_view, sample_chambers, wash_volume, 1, keep_tip=True)
        protocol.delay(minutes=1)
        washSamples(pipette_300, buffers.clear_view, sample_chambers, wash_volume, 1, keep_tip=True)
        protocol.delay(minutes=1)
        washSamples(pipette_300, buffers.clear_view, sample_chambers, wash_volume, 1, keep_tip=True)
        protocol.delay(minutes=1)
        washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 3, keep_tip=True)
        washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 1, keep_tip=True)
        washSamples(pipette_300, buffers.eth_70perc, sample_chambers, wash_volume, 2, keep_tip=True)
        pipette_300.drop_tip()
        #        protocol.delay(minutes=1)
        for i in range(3):
            washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)
            protocol.delay(minutes=1)
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    if retrieval:
        puncture_wells(pipette_300, buffers.retrieval, height_offset=-5)
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        washSamples(pipette_300, buffers.retrieval, sample_chambers, wash_volume, 2, keep_tip=True)
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer)

        for i in range(1, 36):
            protocol.comment(i)
            temp_mod.set_temperature(25 + 2 * i)
            protocol.delay(40)
        temp_mod.set_temperature(96)
        protocol.comment("there we are")
        protocol.delay(1200)
        print("coming back")
        for i in range(36):
            protocol.comment(i)
            temp_mod.set_temperature(95 - 2 * i)
            protocol.delay(40)
        protocol.comment("we are back to normal")

        protocol.delay(1200)

    if type_of_protocol in ['IHC only', 'IHC with Hematoxylin']:
        # WASHING SAMPLES WITH TBS
        protocol.comment("washing in TBS")
        puncture_wells(pipette_300, buffers.TBS_wash, height_offset=-5)
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 2, keep_tip=True)

        # APPLYING enzyme blocking
        protocol.comment("puncturing enzyme blocking wells")
        for i in range(num_samples):
            puncture_wells(pipette_300, enzymeblock_wells[i], height_offset=-5, keep_tip=True)
        pipette_300.drop_tip()

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
        for i in range(num_samples):
            puncture_wells(pipette_300, preblock_wells[i], height_offset=-5, keep_tip=True)
        pipette_300.drop_tip()

        protocol.comment("applying the preblock")
        for i in range(num_samples):
            protocol.comment(i)
            washSamples(pipette_300, preblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("preblocking incubation: 15 min")
        protocol.delay(minutes=15)

        # APPLYING ANTIBODY COCKTAILS TO SAMPLES

        protocol.comment("puncturing and applying abs")
        for i in range(num_samples):
            protocol.comment(i)
            puncture_wells(pipette_300, antibody_wells[i], height_offset=-5)
            washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume, 1)

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        # INCUBATE FOR DESIRED TIME
        protocol.comment("staining incubation: " + str(primary_ab_incubation_time_minutes) + "min")

        if protocol_pause:
            protocol.pause(msg="The protocol is paused for primary antibody incubation")
        if not protocol_pause:
            protocol.delay(minutes=primary_ab_incubation_time_minutes, msg="staining incubation")

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
        for i in range(num_samples):
            puncture_wells(pipette_300, hrpsecondaryab_wells[i], height_offset=-5, keep_tip=True)
        pipette_300.drop_tip()

        protocol.comment("applying hrpsecondaryab")
        for i in range(num_samples):
            washSamples(pipette_300, hrpsecondaryab_wells[i], sample_chambers[i], ab_volume, 1)

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        # INCUBATE FOR DESIRED TIME
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
        for i in range(num_samples):
            puncture_wells(pipette_300, DAB_wells[i], height_offset=-5, keep_tip=True)
            puncture_wells(pipette_300, substrate_wells[i], height_offset=-5, keep_tip=True)
        pipette_300.drop_tip()

        protocol.comment("applying DAB")
        for i in range(num_samples):
            dilute_and_apply_fixative(pipette_300, DAB_wells[i], substrate_wells[i], sample_chambers[i], ab_volume,
                                      keep_tip=True)
        pipette_300.drop_tip()

        protocol.comment("developing substrate")
        protocol.delay(minutes=10)

        protocol.comment("final washw with water")
        puncture_wells(pipette_300, buffers.water, height_offset=-5)
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 5, keep_tip=True)

    # HEMATOXYLIN STAINING
    if type_of_protocol in ['IHC with Hematoxylin', 'Hematoxylin only']:
        protocol.pause(msg="The protocol is paused for adding a slide")
        sample_chambers = getOmnistainerWellsList(omnistainer, num_samples+1)

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        if hematoxylin_source == 'from reagent trough':
            puncture_wells(pipette_300, buffers.hematoxylin, height_offset=-5)
            washSamples(pipette_300, buffers.hematoxylin, sample_chambers, wash_volume, 1)
            protocol.delay(minutes=hematoxylin_incubation_time_seconds)
        if hematoxylin_source == 'from pcr strip':
            protocol.comment("puncturing the hematoxylin wells")
            for i in range(num_samples):
                puncture_wells(pipette_300, hematoxylin_wells[i], height_offset=-5, keep_tip=True)
            pipette_300.drop_tip()
            protocol.comment("applying hematoxylin")
            for i in range(num_samples):
                washSamples(pipette_300, hematoxylin_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            pipette_300.drop_tip()
        protocol.delay(seconds=hematoxylin_incubation_time_seconds)

        # WASHING SAMPLES WITH WATER
        # three individual repeats below is because they need particular incubation time between them
        protocol.comment("washing with water")
        washSamples(pipette_300, buffers.storage, buffers.storage, 2, 1)
        for i in range(3):
            washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume, 2)
            protocol.delay(minutes=3)

        puncture_wells(pipette_300, buffers.eth_100perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_95perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_80perc, height_offset=-5, keep_tip=True)
        puncture_wells(pipette_300, buffers.eth_70perc, height_offset=-5)

        washSamples(pipette_300, buffers.eth_70perc, sample_chambers, wash_volume, 1, keep_tip=True)
        washSamples(pipette_300, buffers.eth_80perc, sample_chambers, wash_volume, 1, keep_tip=True)
        washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 2, keep_tip=True)
        washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 2)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)