from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 CODEX',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX coverslip staining protocol for EA PAR2 instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='PAR2 deck position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
par2_deck_position = 2

### VERAO VAR NAME='COMMON REAGENT RESERVOIR deck position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
trough12_deck_position = 1

### VERAO VAR NAME='96 well deck position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
well96_deck_position = 3

### VERAO VAR NAME='tip rack deck position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_deck_position = 6

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['par2c_30coverslips', 'par2s_9slides_blue_v2']
omniStainer_type = 'par2c_30coverslips'

### VERAO VAR NAME='Lid on the box' TYPE=CHOICE OPTIONS=['yes', 'no']
lid = 'no'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_black_96', 'parhelia_red_96', 'parhelia_red_96_with_strip']
type_of_96well_plate = 'parhelia_red_96_with_strip'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 2

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### change these as necessary

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 100


### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

####################LABWARE LAYOUT#########################
class Object:
    pass

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'


### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'

labwarePositions = Object()
labwarePositions.buffers_plate = trough12_deck_position
labwarePositions.par2 = par2_deck_position
labwarePositions.codex_reagents_plate = well96_deck_position
labwarePositions.tiprack_300 = tiprack_deck_position

####################GENERAL SETUP################################
stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5


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


# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions


def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single', pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos-1]

    par2 = protocol.load_labware(omniStainer_type, labwarePositions.par2, 'PAR2')
    wellslist=list(par2.wells_by_name().keys())
    wellslist = wellslist[1:num_samples+1]
    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate, '96-well-plate')

    buffer_wells = trough12.wells_by_name()
    buffers = Object()
    buffers.clear=  buffer_wells['A2']
    buffers.blue =  buffer_wells['A1']


    preblock_wells = CODEX_reagents_96plate.rows()[0]
    antibody_wells = CODEX_reagents_96plate.rows()[1]


    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])



    #################PROTOCOL####################
    protocol.comment("Starting the DEMO BLUE DYE protocol for samples:" + str(sample_chambers))

    #apply BLUE reagent to the samples
    protocol.comment("Applying blue reagent to the sample")
    washSamples(pipette_300, buffers.blue, sample_chambers, wash_volume, num_repeats=1, dispense_bottom_gap=extra_bottom_gap)

    #WASH SAMPLES WITH CLEAR BUFFER
    protocol.comment("Washing with clear buffer")
    washSamples(pipette_300, buffers.clear, sample_chambers, wash_volume, num_repeats=2, dispense_bottom_gap=extra_bottom_gap)

    #application of rare reagent without tips exchange
    protocol.comment("applying rare reagent without tip exchange between the samples")
    for i in range(len(wellslist)):
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], wash_volume, 1, dispense_bottom_gap=extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()

    #WASH SAMPLES WITH CLEAR BUFFER
    protocol.comment("Washing with clear buffer")
    washSamples(pipette_300, buffers.clear, sample_chambers, wash_volume, num_repeats=2, dispense_bottom_gap=extra_bottom_gap)

    #application of rare reagent with tips exchange
    protocol.comment("applying rare reagent WITH tip exchange between the samples")
    for i in range(len(wellslist)):
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], wash_volume, 1, dispense_bottom_gap=extra_bottom_gap)

    #WASH SAMPLES WITH CLEAR BUFFER
    protocol.comment("Washing with clear buffer")
    washSamples(pipette_300, buffers.clear, sample_chambers, wash_volume, num_repeats=2, dispense_bottom_gap=extra_bottom_gap)
