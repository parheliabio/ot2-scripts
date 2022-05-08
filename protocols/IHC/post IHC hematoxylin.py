from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 IHC',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IHC staining protocol for EA PAR2 instrument',
    'apiLevel': '2.7'

}
####################MODIFIABLE RUN PARAMETERS#########################
####################MODIFIABLE RUN PARAMETERS#########################
### VERAO VAR NAME='ANTIGEN RETRIEVAL' TYPE=BOOLEAN
retreaval = False

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['PAR2c_12coverslips', 'PAR2c_12coverslips_gray', 'PAR2s_9slides', 'par2s_9slides_whilid_v1']
omniStainer_type = 'par2s_9slides_whilid_v1'

### VERAO VAR NAME='Lid on the box' TYPE=CHOICE OPTIONS=['yes', 'no']
lid = 'yes',

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_black_96', 'parhelia_red_96', 'parhelia_red_96_with_strip']
type_of_96well_plate = 'parhelia_red_96_with_strip'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 4

num_samples = int(num_samples)

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=0 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 2

tiprack_300_starting_pos = int(tiprack_300_starting_pos)

### VERAO VAR NAME='How to apply HEMATOXYLIN' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
hematoxylin_source = 'from pcr strip'

### VERAO VAR NAME='Hematoxilin incubation time (seconds)' TYPE=NUMBER LBOUND=1 UBOUND=120 DECIMAL=FALSE
hematoxylin_incubation_time_seconds = 60

# debug mode skips all incubations, prints out additional info
debug = False

####################FIXED RUN PARAMETERS#########################

API_VERSION = '2.7'
default_flow_rate = 50
well_flow_rate = 5

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.4

USE_TROUGH = True

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 200

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 150

### VERAO VAR NAME='Extra bottom gap (for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'


class Object:
    pass


####################LABWARE LAYOUT ON DECK#########################
labwarePositions = Object()
labwarePositions.buffers_reservoir = 1
labwarePositions.par2 = 9
labwarePositions.antibodies_plate = 3
labwarePositions.tiprack_300 = 6
labwarePositions.heatmodule = 7

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
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos - 1]

    if debug: print(pipette_300)

    black_96 = protocol.load_labware(type_of_96well_plate, labwarePositions.antibodies_plate, type_of_96well_plate)

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_reservoir,
                                     '12-trough buffers reservoir')
    if (not retreaval):
        par2 = protocol.load_labware(omniStainer_type, labwarePositions.par2, omniStainer_type)
    if retreaval:
        temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)

        par2 = temp_mod.load_labware(omniStainer_type)
    wellslist = list(par2.wells_by_name().keys())
    wellslist = wellslist[1:num_samples + 1]
    if debug: print(par2)

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.retreaval = buffer_wells['A1']
    buffers.TBS_wash = buffer_wells['A2']
    buffers.water = buffer_wells['A3']
    buffers.storage = buffer_wells['A4']
    buffers.eth_70perc = buffer_wells['A5']
    buffers.eth_80perc = buffer_wells['A6']
    buffers.eth_95perc = buffer_wells['A7']
    buffers.eth_100perc = buffer_wells['A8']
    buffers.hematoxylin = buffer_wells['A12']

    hematoxylin_wells = black_96.rows()[7]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    if debug: print(sample_chambers)

    #################PROTOCOL####################
    #################applying HEMATOXYLIN####################
    if lid == 'yes':
        openPar2(protocol, pipette_300, par2)
    if hematoxylin_source == 'from reagent trough':
        washSamples(pipette_300, buffers.hematoxylin, buffers.hematoxylin, 2, 1, extra_bottom_gap)
        washSamples(pipette_300, buffers.hematoxylin, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=hematoxylin_incubation_time_seconds)
    if hematoxylin_source == 'from pcr strip':
        print("puncturing the hematoxylin wells")
        for i in range(len(wellslist)):
            washSamples(pipette_300, hematoxylin_wells[i], hematoxylin_wells[i], 2, 1, extra_bottom_gap + 23,
                        keep_tip=True)
        pipette_300.drop_tip()
        print("applying hematoxylin")
        for i in range(len(wellslist)):
            washSamples(pipette_300, hematoxylin_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)
    protocol.delay(seconds=hematoxylin_incubation_time_seconds)

    # WASHING SAMPLES WITH WATER
    # three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    washSamples(pipette_300, buffers.storage, buffers.storage, 2, 1, extra_bottom_gap)
    for i in range(3):
        washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume, 2, extra_bottom_gap)
        protocol.delay(minutes=3)

    washSamples(pipette_300, buffers.eth_70perc, buffers.eth_70perc, 2, 1, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_70perc, sample_chambers, wash_volume, 3, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_80perc, buffers.eth_80perc, 2, 1, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_80perc, sample_chambers, wash_volume, 3, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_95perc, buffers.eth_95perc, 2, 1, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 3, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_100perc, buffers.eth_100perc, 2, 1, extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 3, extra_bottom_gap)

    if lid == 'yes':
        closePar2(protocol, pipette_300, par2)
# STORAGE, washing samples every hour
#    for i in range (3):
#        washSamples(pipette_300, buffers.eth_100perc,sample_chambers, 100,extra_bottom_gap, keep_tip=True)
#        protocol.delay(minutes=15)
#        print("total dispensed volume: ", str(stats.volume))
