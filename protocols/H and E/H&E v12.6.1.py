## VERAO GLOBAL
from global_functions import *
from opentrons import protocol_api

### END VERAO GLOBAL

metadata = {
    'protocolName': 'Parhelia H&E v12.6.1.1',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'H&E protocol (no dewax) for slides (incl. 10x Visium) and coverslips',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='D2'
num_samples = 4

do_dewax = False
dewax_temp = 72
alc_temp = 50

### VERAO VAR NAME='Room temp (C)' TYPE=NUMBER LBOUND=10 UBOUND=45 DECIMAL=TRUE
room_temp = 25.0

### VERAO VAR NAME='Do rehydration' TYPE=BOOLEAN EXCEL_POSITION='D4'
do_rehydration = True

### VERAO VAR NAME='Do clairfying' TYPE=BOOLEAN EXCEL_POSITION='D5'
do_clarifying = False

### VERAO VAR NAME='Wash buffer volume (uL)' TYPE=NUMBER LBOUND=25 UBOUND=300 DECIMAL=FALSE EXCEL_POSITION='D6'
wash_volume = 150

### VERAO VAR NAME='Sample flow rate: set to 0.2 for slides, 0.07 for cslps' TYPE=NUMBER LBOUND=0.01 UBOUND=1 DECIMAL=TRUE INCREMENT=0.01
sample_flow_rate = 0.4

### VERAO VAR NAME='Hematoxylin incubation time' TYPE=NUMBER LBOUND=1 UBOUND=5 DECIMAL=TRUE
hematox_delay = 2.5

### VERAO VAR NAME='post-Hematoxylin differentiation in water time (min)' TYPE=NUMBER LBOUND=0 UBOUND=5 DECIMAL=TRUE
hx_diff_time = 1

### VERAO VAR NAME='Eosin incubation time' TYPE=NUMBER LBOUND=1 UBOUND=5 DECIMAL=FALSE
eosin_delay = 1.75

### VERAO VAR NAME='Dehydrate (end in 100% EtOH)' TYPE=BOOLEAN
dehydrate = False

### VERAO VAR NAME='post-Eosin differentiation in 99.9% EtOH time (min, 0=skip)' TYPE=NUMBER LBOUND=0 UBOUND=30 DECIMAL=TRUE
eos_diff_time = 0

### VERAO VAR NAME='ttyUSB_ temp_mod number (usually is 0)' TYPE=NUMBER LBOUND=0 UBOUND=10 DECIMAL=FALSE
temp_mod_number = 1

####################LABWARE LAYOUT ON DECK#########################

### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

### VERAO VAR NAME='Tip type' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul','opentrons_96_filtertiprack_200ul']
tip_type = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='DECK POSITION: Reagent/Buffers plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
HE_buffers_plate_position = 3

### VERAO VAR NAME='DECK POSITION: Staining Module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='DECK POSITION: Tip rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_position = 6

labwarePositions = Object()
labwarePositions.buffers_plate = HE_buffers_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300 = tiprack_position


def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    tiprack_300 = protocol.load_labware(tip_type, labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single', pipette_300_location, tip_racks = [tiprack_300])
    pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate
    pipette.flow_rate.aspirate = default_flow_rate * well_flow_rate

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    temp_mod = None
    plate = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, 'Buffers plate')

    wells = plate.wells_by_name()

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol, temp_mode_number=temp_mod_number)

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception("The temperature module cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        openShutter(protocol, pipette, omnistainer, keep_tip=True)

    if do_dewax and temp_mod is None:
        raise Exception("Dewaxing cannot be performed without a temperature module.")


    reagent_map = {
        'Dewax': wells['A1'],
        '100% EtOH': wells['A2'],
        '95% EtOH': wells['A3'],
        '70% EtOH' : wells['A4'],
        'Water': wells['A5'],
        'Hematoxylin': wells['A6'],
        'Blueing reagent': wells['A7'],
        'Clarifying agent': wells['A8'],
        'Diff (99.9% EtOH)': wells['A9'],
        'Eosin': wells['A11']
    }

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    reagent_sequence =  ['Dewax',   '100% EtOH',    '95% EtOH', '70% EtOH',     'Water',    'Hematoxylin',      'Water',            'Clarifying agent', 'Water',    'Blueing reagent',      'Water',        'Eosin',            'Diff (99.9% EtOH)', '100% EtOH',  'Water']
    delay_mins =        [10,        3,              3,          3,              0,          hematox_delay,      hx_diff_time,           1,                  0,              2,                  0,          eosin_delay,        eos_diff_time,       0,                1]
    reps =              [2,         2,              2,          2,              2,          2,                  2,                      1,                  2,              1,                  2,          2,                  1,                   3,                3]
    speeds =            [0.3,       0.7,            0.7,        0.7,            1,          1,                  1,                      1,                  1,              1,                  1,          0.7,                0.7,                 0.7,              1]
    temps =            [dewax_temp, alc_temp,       alc_temp,   alc_temp,       room_temp,  room_temp,         room_temp,               room_temp,         room_temp,      room_temp,           room_temp, room_temp,           room_temp,           room_temp,         room_temp]


    if dehydrate:
        reagent_sequence.pop(14)
    else:
        for k in [12, 13]:
            reagent_sequence.pop(k)
            delay_mins.pop(k)
            reps.pop(k)
            speeds.pop(k)

    starting_step = 0

    #################PROTOCOL####################
    protocol.comment("Starting the " + metadata['protocolName'] + " for samples:" + str(sample_chambers))

    if not(do_dewax):
        del reagent_map['Dewax']

    if not(do_rehydration):
        del reagent_map['70% EtOH']
        del reagent_map['95% EtOH']

    if not(do_clarifying):
        del reagent_map['Clarifying agent']

    puncture_wells(pipette, list(reagent_map.values()))

    for i in range(len(reagent_sequence)):
        reag_name = reagent_sequence[i]

        if i < starting_step:
            continue

        if not(do_dewax) and 'Dewax' in reag_name:
            continue

        if not (do_rehydration) and i < 4:
            continue

        if not (do_clarifying) and 'Clarifying' in reag_name:
            #skipping the addl water wash as well
            i+=1
            continue

        if (eos_diff_time==0) and ('95% EtOH' in reag_name) and i > 4:
            continue

        if do_dewax and not (temp_mod is None) and (i==0 or temps[i-1]!=temps[i]):
            temp_mod.quick_temp(temps[i])

        if not pipette.has_tip: pipette.pick_up_tip()
        reagent = reagent_sequence[i]
        well = reagent_map[reagent]
        pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate * speeds[i]

        start = time.time()

        for j in range(reps[i]):
            protocol.comment("Applying reagent "  +  reagent + " from well " + str(well) + " to the sample, repeat "+ str(j+1) + " out of " + str(reps[i]))
            pipette.distribute(wash_volume, well, sample_chambers, new_tip = 'never', disposal_volume=0, blowout=False)

        if pipette.has_tip:
            pipette.drop_tip()

        elapsed = min(1, int(time.time() - start))

        delay_seconds = max(1, (delay_mins[i] * 60) - elapsed)
        protocol.comment("Dispensing took " + str(elapsed) + " sec, incubating for remaining: " + str(delay_seconds) + " out of total " + str(delay_mins[i] * 60) + " sec")
        if delay_seconds > 1:
            protocol.delay(seconds=delay_seconds)

        protocol.home()