from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 IHC',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IHC staining protocol for EA PAR2 instrument',
    'apiLevel': '2.7'

}
####################MODIFIABLE RUN PARAMETERS#########################
### VERAO VAR NAME='ANTIGEN RETRIEVAL' TYPE=BOOLEAN
retreaval = False

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['PAR2c_12coverslips', 'PAR2s_9slides', 'par2s_9slides_whilid_v1']
type_of_par2 = 'par2s_9slides_whilid_v1'

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['parhelia_black_96', 'parhelia_red_96', 'parhelia_red_96_with_strip']
type_of_96well_plate = 'parhelia_red_96_with_strip'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 3
wellslist = ['A2', 'A3', 'C2', 'C3']
wellslist = wellslist[0:num_samples]

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
secondary_ab_incubation_time_minutes = 30

# debug mode skips all incubations, prints out additional info
debug = False

####################FIXED RUN PARAMETERS#########################

API_VERSION = '2.7'
default_flow_rate = 50
well_flow_rate = 5

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=1 UBOUND=1 DECIMAL=True
sample_flow_rate = 0.2

USE_TROUGH = True

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 200

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 150

### VERAO VAR NAME='Extra bottom gap (for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0


class Object:
    pass


####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'

labwarePositions = Object()
labwarePositions.buffers_reservoir = 1
labwarePositions.par2 = 9
labwarePositions.antibodies_plate = 3
labwarePositions.tiprack_300 = 6
labwarePositions.heatmodule = 8

####################GENERAL SETUP################################


stats = Object()
stats.volume = 0


####################! FUNCTIONS - DO NOT MODIFY !#########################

def openPar2(protocol, pipette, covered_lbwr):
    pipette.pick_up_tip()
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].bottom(0), force_direct=True)
    protocol.delay(seconds=1)
    pipette.drop_tip()


def closePar2(protocol, pipette, covered_lbwr):
    pipette.pick_up_tip()
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].bottom(0), force_direct=True)
    protocol.delay(seconds=1)
    pipette.drop_tip()


def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, dispense_bottom_gap=0, keep_tip=False):
    try:
        iter(samples)
        # print('samples are iterable')
    except TypeError:
        # print('samples arent iterable')
        samples = [samples]

    if not pipette.has_tip:
        pipette.pick_up_tip()

    #    if(len(samples)==0):
    #       samples = [samples]
    #    print("Replacing solution on samples:" +str(samples) + " len=" + str(len(samples)))
    for i in range(0, num_repeats):
        print("Iteration:" + str(i))
        for s in samples:
            print(s)
            print("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(dispense_bottom_gap), rate=sample_flow_rate).blow_out()
            stats.volume += volume

    if not keep_tip: pipette.drop_tip()
    if keep_tip: pipette.move_to(samples[len(samples) - 1].bottom(60))


def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume):
    try:
        iter(samples)
        # print('samples are iterable')
    except TypeError:
        # print('samples arent iterable')
        samples = [samples]
    if not pipette.has_tip:
        pipette.pick_up_tip()

    #    if(len(samples)==0):
    #        samples = [samples]
    #    print("Applying fixative to samples:" +str(samples) + " len=" + str(len(samples)))

    for s in samples:
        print("Diluting fixative: " + str(s))
        pipette.aspirate(volume + 50, dilutant_buffer_well, rate=well_flow_rate)
        pipette.dispense(volume + 50, sourceSolutionWell, rate=well_flow_rate)
        for iterator in range(0, 3):
            print("Mixing: " + str(iterator + 1))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
        print("Applying fixative to sample: " + str(s))
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, s, rate=sample_flow_rate).blow_out()
        stats.volume += volume

    pipette.drop_tip()


def mix(pipette, sourceSolutionWell, volume, num_repeats):
    pipette.pick_up_tip()

    print("Mixing solution in samples:" + str(sourceSolutionWell))
    for i in range(0, num_repeats):
        print("Iteration:" + str(i))
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()


###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):
    if debug: print(protocol)

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, "tiprack 300ul")

    if debug: print(tiprack_300)
    pipette_300 = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single',
                                           pipette_300_location, tip_racks=[tiprack_300])
    #    pipette_300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos - 1]
    # pipette_300.starting_tip = tiprack_300.well(tiprack_starting_pos['tiprack_300'])

    if debug: print(pipette_300)

    black_96 = protocol.load_labware(type_of_96well_plate, labwarePositions.antibodies_plate, type_of_96well_plate)

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_reservoir,
                                     '12-trough buffers reservoir')
    if (not retreaval):
        par2 = protocol.load_labware(type_of_par2, labwarePositions.par2,
                                     type_of_par2)
    if retreaval:
        temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)

        par2 = temp_mod.load_labware(type_of_par2)

    if debug: print(par2)

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.retreaval = buffer_wells['A1']
    buffers.TBS_wash = buffer_wells['A2']
    buffers.water = buffer_wells['A3']
    buffers.storage = buffer_wells['A4']
    buffers.eth_70perc_ = buffer_wells['A5']
    buffers.eth_80perc = buffer_wells['A6']
    buffers.eth_95perc = buffer_wells['A7']
    buffers.eth_100perc = buffer_wells['A8']
    buffers.hematoxylin = buffer_wells['A12']

    preblock_wells = black_96.rows()[0]
    antibody_wells = black_96.rows()[5]
    enzymeblock_wells = black_96.rows()[1]
    hrpsecondaryab_wells = black_96.rows()[2]
    substrate_wells = black_96.rows()[3]
    DAB_wells = black_96.rows()[4]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    if debug: print(sample_chambers)

    #################PROTOCOL####################
    protocol.home()

    openPar2(protocol, pipette_300, par2)

    if retreaval:
        washSamples(pipette_300, buffers.retreaval, buffers.retreaval, 2, 1, extra_bottom_gap + 18)
        washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, 2, extra_bottom_gap)

        closePar2(protocol, pipette_300, par2)

        temp_mod.set_temperature(95)
        print("retreaval")
        protocol.delay(minutes=15)
        #        washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=15)
        #        washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=15)
        print("cooling down to RT")
        temp_mod.set_temperature(25)
        protocol.delay(minutes=20)
        openPar2(protocol, pipette_300, par2)

    # WASHING SAMPLES WITH TBS
    print("washing in TBS")
    washSamples(pipette_300, buffers.TBS_wash, buffers.TBS_wash, 2, 1, extra_bottom_gap + 18)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 2, extra_bottom_gap)

    # Preblocking
    print("preblocking")
    print(len(wellslist))

    print("puncturing preblock wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, preblock_wells[i], preblock_wells[i], 2, 1, extra_bottom_gap + 18, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)
    print("preblocking incubation: 15 min")
    protocol.delay(minutes=15)

    # APPLYING ANTIBODY COCKTAILS TO SAMPLES

    print("puncturing and applying abs")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, antibody_wells[i], antibody_wells[i], 2, 1, extra_bottom_gap + 18, keep_tip=True)
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)

    closePar2(protocol, pipette_300, par2)
    # INCUBATE FOR DESIRED TIME
    print("staining incubation: " + str(primary_ab_incubation_time_minutes) + "min")
    protocol.delay(minutes=primary_ab_incubation_time_minutes)
    openPar2(protocol, pipette_300, par2)

    # WASHING SAMPLES WITH TBS
    # three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    for i in range(5):
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=3)

    # APPLYING enzyme blocking
    print("puncturing enzyme blocking wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, enzymeblock_wells[i], enzymeblock_wells[i], 2, 1, extra_bottom_gap + 18, keep_tip=True)
    pipette_300.drop_tip()

    print("applying enzyme blocking")
    for i in range(len(wellslist)):
        washSamples(pipette_300, enzymeblock_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)
    # INCUBATE 10 MIN
    print("hrp blocking incubation: 10min")
    protocol.delay(minutes=10)

    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 3, extra_bottom_gap)

    # APPLYING HRP SECONDARY ANTIBODY COCKTAILS TO SAMPLES
    print("puncturing hrpsecondaryab wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, hrpsecondaryab_wells[i], hrpsecondaryab_wells[i], 2, 1, extra_bottom_gap + 18,
                    keep_tip=True)
    pipette_300.drop_tip()

    print("applying hrpsecondaryab")
    for i in range(len(wellslist)):
        washSamples(pipette_300, hrpsecondaryab_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)
    closePar2(protocol, pipette_300, par2)
    # INCUBATE FOR DESIRED TIME
    print("staining incubation: " + str(secondary_ab_incubation_time_minutes) + "min")
    protocol.delay(minutes=secondary_ab_incubation_time_minutes)
    openPar2(protocol, pipette_300, par2)

    # three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    for i in range(3):
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=3)

    # DILUTING AND APPLYING THE DAB
    print("puncturing the DAB wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, DAB_wells[i], DAB_wells[i], 2, 1, extra_bottom_gap + 18)
    print("puncturing the substrate wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, substrate_wells[i], substrate_wells[i], 2, 1, extra_bottom_gap + 18, keep_tip=True)
    pipette_300.drop_tip()

    print("applying DAB")
    for i in range(len(wellslist)):
        dilute_and_apply_fixative(pipette_300, DAB_wells[i], substrate_wells[i], sample_chambers[i], wash_volume)

    print("developing substrate")

    protocol.delay(minutes=10)

    washSamples(pipette_300, buffers.water, buffers.water, 2, 1, extra_bottom_gap + 18)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 5, extra_bottom_gap)

    closePar2(protocol, pipette_300, par2)
