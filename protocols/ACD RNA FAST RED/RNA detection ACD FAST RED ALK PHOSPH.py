from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 RNA',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX coverslip staining protocol for EA PAR2 instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['PAR2c_12coverslips', 'PAR2s_9slides','PAR2c_12coverslips_gray']
omniStainer_type = 'PAR2c_12coverslips_gray'

""" !!! IMPORTANT !!! Specify the PAR2 positions where your specimens are located,
starting with A1 (A0 is reserved for calibration and should not be used for staining)
PAR2 'A' row positions 1-4 correspond to wells A1-A4, whereas 'B' and 'C' row positions 1-4
correspond to wells B1-4 and C1-4, respectively """



#The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='FFPE' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='Temp lag for adjusting the temp' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALS
templag=15
"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the PAR2 device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the 96-well plate
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""
### VERAO VAR NAME='Antibody Screening Mode' TYPE=BOOLEAN
Antibody_Screening = False

### VERAO VAR NAME='Lid on the box' TYPE=CHOICE OPTIONS=['yes', 'no']
lid = 'no'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_black_96', 'parhelia_red_96', 'parhelia_red_96_with_strip']
type_of_96well_plate = 'parhelia_red_96_with_strip'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 1

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1


### VERAO VAR NAME='RNA_hybridization time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
hybridization_time_minutes = 600

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 200

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 150

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

#Creating a dummy class
class Object:
    pass

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'


### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'

labwarePositions = Object()
labwarePositions.buffers_plate = 1
labwarePositions.par2 = 2
labwarePositions.antibodies_plate = 3
labwarePositions.tiprack_300 = 6
labwarePositions.heatmodule = 7

####################GENERAL SETUP################################

stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5

####################! FUNCTIONS - DO NOT MODIFY !#########################
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, dispense_bottom_gap=0, keep_tip = False):

    try:
        iter(samples)
        print('samples are iterable')
    except TypeError:
        print('samples arent iterable')
        samples = [samples]

    print ('Samples are:')
    print (samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

#    if(len(samples)==0):
#       samples = [samples]
#    print("Replacing solution on samples:" +str(samples) + " len=" + str(len(samples)))
    for i in range(0, num_repeats):
        print ("Iteration:"+ str(i))
        for s in samples:
            print(s)
            print ("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(dispense_bottom_gap), rate=sample_flow_rate).blow_out()
            stats.volume += volume

    if not keep_tip: pipette.drop_tip()
    if keep_tip: pipette.move_to(samples[len(samples)-1].bottom(60))

def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    if not pipette.has_tip: pipette.pick_up_tip()

    if(len(samples)==0):
        samples = [samples]

    for s in samples:
    #Diluting fixative:
        pipette.aspirate(volume+50, dilutant_buffer_well, rate=well_flow_rate)
        pipette.dispense(volume+50, sourceSolutionWell, rate=well_flow_rate)
        for iterator in range(0, 3):
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    #Applying fixative to sample:
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, s, rate=sample_flow_rate).blow_out()
        stats.volume += volume

    pipette.drop_tip()

def mix(pipette, sourceSolutionWell, volume, num_repeats):

    if not pipette.has_tip: pipette.pick_up_tip()

    #print ("Mixing solution in samples:" +str(sourceSolutionWell))
    for i in range(0, num_repeats):
    #    print ("Iteration:"+ str(i))
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()


#####################CUSTOM LABWARE_DEFINITION###################

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single', pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos-1]

    temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)

    par2 = temp_mod.load_labware(omniStainer_type)
    wellslist=list(par2.wells_by_name().keys())
    wellslist = wellslist[1:num_samples+1]
    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    black_96 = protocol.load_labware(type_of_96well_plate, labwarePositions.antibodies_plate, '96-well-plate')

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.retrieval = buffer_wells['A1']
    buffers.TBS_wash = buffer_wells['A2']
    buffers.water = buffer_wells['A3']
    buffers.storage = buffer_wells['A4']
    buffers.eth_70perc_ = buffer_wells['A5']
    buffers.eth_80perc = buffer_wells['A6']
    buffers.eth_95perc = buffer_wells['A7']
    buffers.eth_100perc = buffer_wells['A8']
    buffers.washbuffer05 = buffer_wells['A10']
    buffers.hematoxylin = buffer_wells['A12']
    buffers.Hydration_PFA_1pt6pct = buffer_wells['A9']


    probe_wells = black_96.columns()[0]
    amp1_wells = black_96.columns()[1]
    amp2_wells = black_96.columns()[2]
    amp3_wells = black_96.columns()[3]
    amp4_wells = black_96.columns()[4]
    amp5_wells = black_96.columns()[5]
    amp6_wells = black_96.columns()[6]
    substrate_wells = black_96.columns()[7]
    FR_wells = black_96.columns()[8]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    print("wellslist is:")
    print(wellslist)
    print("par2.wells_by_name are:")
    print(par2.wells_by_name())
    print ("sample_chambers are:")
    print (sample_chambers)

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if not FFPE:
        #WASHING SAMPLES WITH PFA
        protocol.comment("first fix")
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, buffers.Hydration_PFA_1pt6pct, 0,1,extra_bottom_gap)
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume,1,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=10, msg = "first fix incubation")

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")
    #puncturing the foil
    washSamples(pipette_300, buffers.washbuffer05, buffers.washbuffer05, 0, 1,extra_bottom_gap)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)


    #readjusting the heat module temp
    temp_mod.set_temperature(40)
    protocol.delay(minutes=templag)


    # APPLYING probe COCKTAILS TO SAMPLES

    print("puncturing and applying abs")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, probe_wells[i], probe_wells[i], 2, 1, extra_bottom_gap + 21)
        washSamples(pipette_300, probe_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)

    print("staining incubation: " + str(hybridization_time_minutes) + "min")
    protocol.delay(minutes=hybridization_time_minutes)

    
    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")



    #AMP 1
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp1_wells[i], amp1_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp1_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=30)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")


    #AMP 2
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp2_wells[i], amp2_wells[i], 2, 1, extra_bottom_gap + 23, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp2_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=15)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")

    #AMP 3
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp3_wells[i], amp3_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp3_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=30)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")

    #AMP 4
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp4_wells[i], amp4_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp4_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=15)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")



    temp_mod.set_temperature(25)
    protocol.delay(minutes=templag)

    #AMP 5
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp5_wells[i], amp5_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp5_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=30)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")

    #AMP 6
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp6_wells[i], amp6_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp6_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=15)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")


    # DILUTING AND APPLYING THE DAB
    print("puncturing the DAB wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, FR_wells[i], FR_wells[i], 2, 1, extra_bottom_gap + 21)
    print("puncturing the substrate wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, substrate_wells[i], substrate_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying DAB")
    for i in range(len(wellslist)):
        dilute_and_apply_fixative(pipette_300, FR_wells[i], substrate_wells[i], sample_chambers[i], ab_volume)

    print("developing substrate")

    protocol.delay(minutes=10)

    washSamples(pipette_300, buffers.water, buffers.water, 2, 1, extra_bottom_gap + 21)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 5, extra_bottom_gap)






