from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 IHC',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IHC staining protocol for EA PAR2 instrument',
    'apiLevel': '2.7'

}
####################MODIFIABLE RUN PARAMETERS#########################

retreaval = True

wellslist = ['A2', 'A3']

type_of_96well_plate = 'parhelia_red_96'

tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

# Antibody incubation time in minutes
primary_ab_incubation_time_minutes = 480
secondary_ab_incubation_time_minutes = 30

# debug mode skips all incubations, prints out additional info
debug = False

####################FIXED RUN PARAMETERS#########################

API_VERSION = '2.7'
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.4
wash_volume = 200
USE_TROUGH = True
extra_bottom_gap = 0


class Object:
    pass


####################LABWARE LAYOUT ON DECK#########################
labwarePositions = Object()
labwarePositions.buffers_reservoir = 1
labwarePositions.par2 = 2
labwarePositions.antibodies_plate = 3
labwarePositions.tiprack_300 = 6
labwarePositions.heatmodule = 8

####################GENERAL SETUP################################


stats = Object()
stats.volume = 0


####################! FUNCTIONS - DO NOT MODIFY !#########################
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, dispense_bottom_gap=0, keep_tip=False):
    try:
        iter(samples)
        # print('samples are iterable')
    except TypeError:
        # print('samples arent iterable')
        samples = [samples]

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

    pipette_300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.well(tiprack_starting_pos['tiprack_300'])

    if debug: print(pipette_300)

    black_96 = protocol.load_labware(type_of_96well_plate, labwarePositions.antibodies_plate, type_of_96well_plate)

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_reservoir,
                                     '12-trough buffers reservoir')
    if (not retreaval):
        par2 = protocol.load_labware('par2s_9slides_blue_v2', labwarePositions.par2,
                                     'par2s_9slides_blue_v2')
    if retreaval:
        temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)

        par2 = temp_mod.load_labware('par2s_9slides_blue_v2')

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
    antibody_wells = black_96.rows()[1]
    enzymeblock_wells = black_96.rows()[2]
    hrpsecondaryab_wells = black_96.rows()[3]
    substrate_wells = black_96.rows()[4]
    DAB_wells = black_96.rows()[5]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    if debug: print(sample_chambers)

    #################PROTOCOL####################
    protocol.home()
    if retreaval:
        washSamples(pipette_300, buffers.retreaval, buffers.retreaval, 0, 1, extra_bottom_gap)
        washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, 2, extra_bottom_gap)
        temp_mod.set_temperature(95)
        print("retreaval")
        protocol.delay(minutes=15)
        washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=15)
        washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=15)
        print("cooling down to RT")
        temp_mod.set_temperature(25)
        protocol.delay(minutes=20)

    # WASHING SAMPLES WITH TBS
    print("washing in TBS")
    washSamples(pipette_300, buffers.TBS_wash, buffers.TBS_wash, 0, 1, extra_bottom_gap)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 2, extra_bottom_gap)

    # Preblocking
    print("preblocking")
    print(len(wellslist))
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], wash_volume, 1, extra_bottom_gap)
    print("preblocking incubation: 15 min")
    protocol.delay(minutes=15)

    # APPLYING ANTIBODY COCKTAILS TO SAMPLES
    print("applying antibodies")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], wash_volume, 1, extra_bottom_gap)

    # INCUBATE FOR DESIRED TIME
    print("staining incubation: " + str(primary_ab_incubation_time_minutes) + "min")
    protocol.delay(minutes=primary_ab_incubation_time_minutes)

    # WASHING SAMPLES WITH TBS
    # three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    for i in range(5):
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=3)

    # APPLYING enzyme blocking
    print("applying enzyme blocking")
    for i in range(len(wellslist)):
        washSamples(pipette_300, enzymeblock_wells[i], sample_chambers[i], wash_volume, 1, extra_bottom_gap)
    # INCUBATE 10 MIN
    print("hrp blocking incubation: 10min")
    protocol.delay(minutes=10)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 3, extra_bottom_gap)

    # APPLYING HRP SECONDARY ANTIBODY COCKTAILS TO SAMPLES
    print("applying hrpsecondaryab")
    for i in range(len(wellslist)):
        washSamples(pipette_300, hrpsecondaryab_wells[i], sample_chambers[i], wash_volume, 1, extra_bottom_gap)

    # INCUBATE FOR DESIRED TIME
    print("staining incubation: " + str(secondary_ab_incubation_time_minutes) + "min")
    protocol.delay(minutes=secondary_ab_incubation_time_minutes)

    # three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    for i in range(3):
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, 1, extra_bottom_gap)
        protocol.delay(minutes=3)

    # DILUTING AND APPLYING THE DAB
    for i in range(len(wellslist)):
        dilute_and_apply_fixative(pipette_300, DAB_wells[i], substrate_wells[i], sample_chambers[i], 200)

    print("developing substrate")

    protocol.delay(minutes=10)

    washSamples(pipette_300, buffers.water, buffers.water, 0, 1, extra_bottom_gap)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 5, extra_bottom_gap)

    # STORAGE, washing samples every hour
    washSamples(pipette_300, buffers.storage, buffers.storage, 0, 1, extra_bottom_gap)
    for i in range(48):
        washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume / 2, 1, extra_bottom_gap, keep_tip=True)
        protocol.delay(minutes=60)
        print("total dispensed volume: ", str(stats.volume))
