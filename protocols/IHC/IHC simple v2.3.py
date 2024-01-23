## VERAO GLOBAL
from global_functions import *
from opentrons import protocol_api

### END VERAO GLOBAL

metadata = {
    'protocolName': 'IHC v2.3 - MDD - IHC',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IHC tertiary staining added',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 3

### VERAO VAR NAME='Delayed start' TYPE=BOOLEAN
delayed_start = False

### VERAO VAR NAME='Protocol start delay time (minutes)' TYPE=NUMBER LBOUND=15 UBOUND=8000 DECIMAL=FALSE
protocol_delay_minutes = 30

### VERAO VAR NAME='Do First Wash and Preblock?' TYPE=BOOLEAN
pre_staining = True

### VERAO VAR NAME='Do Primary Antibody Stain?' TYPE=BOOLEAN
primary_staining = True

### VERAO VAR NAME='Do Secondary Antibody Stain?' TYPE=BOOLEAN
secondary_staining = True

### VERAO VAR NAME='Do Tertiary Antibody Stain?' TYPE=BOOLEAN
tertiary_staining = True

### VERAO VAR NAME='Perform Staining (i.e., DAPI, DAB)?' TYPE=BOOLEAN
counter_staining = True

### VERAO VAR NAME='Room temperature (for temp mods)' TYPE=NUMBER LBOUND=15 UBOUND=25
room_temp = 22

### VERAO VAR NAME='Wash Dispense Repeats (without wait/incubation in between)' TYPE=NUMBER LBOUND=1 UBOUND=25
wash_dispense_reps = 1

### VERAO VAR NAME='1st Wash (before preblock) Step Repeats (with wait/incubation in between)' TYPE=NUMBER LBOUND=1 UBOUND=25
wash_step_reps_1 = 3

### VERAO VAR NAME='2nd Wash (after primary ab) Step Repeats (with wait/incubation in between)' TYPE=NUMBER LBOUND=1 UBOUND=25
wash_step_reps_2 = 3

### VERAO VAR NAME='3rd Wash (after secondary ab) Step Repeats (with wait/incubation in between)' TYPE=NUMBER LBOUND=1 UBOUND=25
wash_step_reps_3 = 3

### VERAO VAR NAME='4th Wash (after tertiary) Step Repeats (with wait/incubation in between)' TYPE=NUMBER LBOUND=1 UBOUND=25
wash_step_reps_4 = 3

### VERAO VAR NAME='5th Wash (after stain) Step Repeats (with wait/incubation in between)' TYPE=NUMBER LBOUND=1 UBOUND=25
wash_step_reps_5 = 3

### VERAO VAR NAME='Storage mode?' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=2 UBOUND=25
storage_temp = 4

### VERAO VAR NAME='Preblock Incubation time (min)' TYPE=NUMBER LBOUND=5 UBOUND=4200 DECIMAL=FALSE
antibody_diluent_incubation_min = 30

### VERAO VAR NAME='Primary Antibody incubation time (min)' TYPE=NUMBER LBOUND=5 UBOUND=4200 DECIMAL=FALSE
primary_ab_incubation = 30

### VERAO VAR NAME='Secondary Antibody incubation time (min)' TYPE=NUMBER LBOUND=1 UBOUND=4200 DECIMAL=FALSE
secondary_ab_incubation = 30

### VERAO VAR NAME='Tertiary Antibody incubation time (min)' TYPE=NUMBER LBOUND=1 UBOUND=4200 DECIMAL=FALSE
tertiary_ab_incubation = 30

### VERAO VAR NAME='Stain incubation time (min)' TYPE=NUMBER LBOUND=1 UBOUND=4200 DECIMAL=TRUE
counterstain_incubation = 5

### VERAO VAR NAME='PBS wash incubation time (min)' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
wash_incubation = 5

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody/Reagent staining volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Double add of antibody/reagents (uses 2x volume, but improves uniformity)' TYPE=BOOLEAN
double_add = False

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_location = 'left'

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 7

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12 module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='Deck position: 96-well Antibody plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_plate_position = 8

### VERAO VAR NAME='Deck position: Tip Rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 10

### VERAO VAR NAME='Tip type for tiprack' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type_tiprack_1 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='TEST MODE (ALL INCUBATION DELAYS WILL BE SKIPPED)' TYPE=BOOLEAN
testmode = False

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.ab_plate = ab_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
#labwarePositions.tiprack_300_2 = tiprack_300_2_position
# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    #Tiprack
    tiprack_1 = protocol.load_labware(tip_type_tiprack_1, labwarePositions.tiprack_300_1,
                                      'tiprack 200/300ul 1')
    #tiprack_2 = protocol.load_labware(tip_type_tiprack_2, labwarePositions.tiprack_300_2,'tiprack 200/300ul 2')
    #Pipette
    pipette_type = 'p300_single_gen2'
    #pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_1, tiprack_2])
    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_1])
    pipette.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos-1]
    #Staining Module
    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')
    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)
    #Buffers plate
    PBS_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate,
                                         '12-trough PBS reservoir')
    #Reagent plate
    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_plate, '96-well-plate')

    ##########################REAGENT SETUP################################
    # Buffers plate
    #PBS_wells[list(PBS_wells.keys())[i]]
    #PBS_wells = PBS_trough12.wells_by_name()
    wash_buffer_1 = PBS_trough12.wells_by_name()['A1']
    wash_buffer_2 = PBS_trough12.wells_by_name()['A2']
    wash_buffer_3 = PBS_trough12.wells_by_name()['A3']
    wash_buffer_4 = PBS_trough12.wells_by_name()['A4']
    wash_buffer_5 = PBS_trough12.wells_by_name()['A5']
    #for i in range(num_samples):
    #    wash_buffer_wells = wash_buffer[list(wash_buffer.keys())[i]]

    # Reagent plate
    antibody_diluent_wells = reagents_96plate.rows()[0][:num_samples]
    primary_ab_wells = reagents_96plate.rows()[1][:num_samples]
    secondary_ab_wells = reagents_96plate.rows()[2][:num_samples]
    tertiary_ab_wells = reagents_96plate.rows()[3][:num_samples]
    counterstain_wells = reagents_96plate.rows()[4][:num_samples]


    if double_add:
        num_reps = 2
    else: 
        num_reps = 1

    #################PROTOCOL####################
    protocol.comment("Starting the "+ metadata["protocolName"] +" for samples:" + str(sample_chambers))

    protocol.home()

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        openShutter(protocol, pipette, omnistainer)

    temp_mod = None

    if delayed_start:
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer)
        protocol.delay(minutes=protocol_delay_minutes, msg = "Delaying the start by " + str(protocol_delay_minutes) + " minutes" )

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol,0)
        temp_mod.set_temp(room_temp)

    if pre_staining:
        apply_and_incubate(protocol, pipette, wash_buffer_1, "1x PBS Wash", sample_chambers, wash_volume, wash_dispense_reps, wash_incubation, wash_step_reps_1)
        apply_and_incubate(protocol, pipette, antibody_diluent_wells, "1x Antibody Diluent (Preblock)",       sample_chambers,   ab_volume,      num_reps, antibody_diluent_incubation_min                                      )

    if primary_staining:
        apply_and_incubate(protocol, pipette, primary_ab_wells,     "1x Primary Antibody mix",     sample_chambers,   ab_volume,     num_reps, primary_ab_incubation )
        apply_and_incubate(protocol, pipette, wash_buffer_2,          "1x PBS Wash",                  sample_chambers,   wash_volume,   wash_dispense_reps, wash_incubation, wash_step_reps_2 )

    if secondary_staining:
        apply_and_incubate(protocol, pipette, secondary_ab_wells,        "1x Secondary Antibody Mix",                  sample_chambers,   ab_volume,     num_reps, secondary_ab_incubation )
        apply_and_incubate(protocol, pipette, wash_buffer_3,          "1x PBS Wash",                  sample_chambers,   wash_volume,   wash_dispense_reps, wash_incubation,  wash_step_reps_3 )

    if tertiary_staining:
        apply_and_incubate(protocol, pipette, tertiary_ab_wells,        "1x Tertiary Antibody Mix",                  sample_chambers,   ab_volume,     num_reps, tertiary_ab_incubation )
        apply_and_incubate(protocol, pipette, wash_buffer_4,          "1x PBS Wash",                  sample_chambers,   wash_volume,   wash_dispense_reps, wash_incubation,  wash_step_reps_4 )

    if counter_staining:
        apply_and_incubate(protocol, pipette, counterstain_wells,       "1x Stain",  sample_chambers,   ab_volume,     num_reps, counterstain_incubation )
        apply_and_incubate(protocol, pipette, wash_buffer_5,          "1x PBS Wash",                  sample_chambers,   wash_volume,   wash_dispense_reps, wash_incubation,  wash_step_reps_5 )

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette, omnistainer)

    if storage_mode:
        protocol.comment(f"cooling down to {storage_temp} deg for storage. The protocol will pause next")
        temp_mod.set_temp(storage_temp)
        protocol.pause(
            msg=f"Protocol is paused for {storage_temp} C storage. "
                f"Hit Resume to end the protocol and turn off the thermal module")

    if 'coldplate' in omnistainer_type:
        temp_mod.temp_off()
        protocol.comment(f"Protocol done - temperature module has been turned off")
    else:
        protocol.comment(f"Protocol done")

    protocol.home()
#protocol exported from Parhelia StainWorks

