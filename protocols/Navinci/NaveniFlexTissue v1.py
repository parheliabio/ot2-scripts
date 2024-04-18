### VERAO GLOBAL
from global_functions import *
### END VERAO GLOBAL

metadata = {
    'protocolName': 'Navinci NaveniFlexTissue v1',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Navinci NaveniFlexTissue protocol',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='D5'
num_samples = 4

### VERAO VAR NAME='Double add?' TYPE=BOOLEAN EXCEL_POSITION='D4'
double_add = True

### VERAO VAR NAME='Number of washes post Navenibodies' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
num_washes_post_NAB = 5

### VERAO VAR NAME='Wash incubation time' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
wash_incubation_time = 2

### VERAO VAR NAME='Room temp' TYPE=NUMBER LBOUND=15 UBOUND=25 DECIMAL=FALSE
room_temp = 20

### VERAO VAR NAME='Amplification temp' TYPE=NUMBER LBOUND=20 UBOUND=40 DECIMAL=FALSE
amp_temp = 30

### VERAO VAR NAME='Incubation temp' TYPE=NUMBER LBOUND=20 UBOUND=40 DECIMAL=FALSE
incubation_temp = 37

### VERAO VAR NAME='Storage temp' TYPE=NUMBER LBOUND=0 UBOUND=20 DECIMAL=FALSE
storage_temp = 4

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Staining volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
stain_volume = 110

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.4

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 1

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12 module' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
omnistainer_position = 3

### VERAO VAR NAME='Deck position: Buffer W/ Antibodies plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_plate_position = 4

### VERAO VAR NAME='Deck position: 300ul tip rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 9

### VERAO VAR NAME='TEST MODE (ALL INCUBATION DELAYS WILL BE SKIPPED)' TYPE=BOOLEAN
testmode = False

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.ab_plate = ab_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
tiprack_300_starting_pos = 1

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1, 'tiprack 300ul 1')

    pipette_type = 'p300_single_gen2'

    pipette = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks = [tiprack_300_1])

    pipette.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos-1]

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    if 'thermosheath' in omnistainer_type and labwarePositions.omnistainer > 9:
        raise Exception("Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_plate, '96-well-plate')

    wash_buffer = trough12.wells_by_name()['A11']
    nuclear_stain = trough12.wells_by_name()['A12']

    wells = Object()
    wells.block =           reagents_96plate.rows()[0][:num_samples]
    wells.primary_ab =      reagents_96plate.rows()[1][:num_samples]
    wells.secondary_ab =    reagents_96plate.rows()[2][:num_samples]
    wells.ligation =        reagents_96plate.rows()[3][:num_samples]
    wells.amp =             reagents_96plate.rows()[4][:num_samples]
    wells.post_block =      reagents_96plate.rows()[5][:num_samples]
    wells.detection =       reagents_96plate.rows()[6][:num_samples]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    num_reps = 2 if double_add else 1

    #################PROTOCOL####################
    protocol.comment("Starting the "+ metadata["protocolName"] +" for samples:" + str(sample_chambers))

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette, omnistainer)

    temp_mod.quick_temp(incubation_temp)
    apply_and_incubate(protocol, pipette, wells.block,      "Block",        sample_chambers, stain_volume, 1,                   60)
    apply_and_incubate(protocol, pipette, wells.primary_ab, "Primary abs",  sample_chambers, stain_volume, 1,                   60, new_tip='always')
    apply_and_incubate(protocol, pipette, wash_buffer,      "Wash",         sample_chambers, wash_volume,  3,                   wash_incubation_time)
    apply_and_incubate(protocol, pipette, wells.primary_ab, "Navenibodies", sample_chambers, stain_volume, num_reps,            60)
    apply_and_incubate(protocol, pipette, wash_buffer,      "Wash",         sample_chambers, wash_volume,  num_washes_post_NAB, wash_incubation_time, puncture=False)
    apply_and_incubate(protocol, pipette, wells.ligation,   "Ligation",     sample_chambers, stain_volume, 1,                   30)
    apply_and_incubate(protocol, pipette, wash_buffer,      "Wash",         sample_chambers, wash_volume,  2,                   wash_incubation_time, puncture=False)
    temp_mod.quick_temp(amp_temp)
    apply_and_incubate(protocol, pipette, wells.amp,        "Amplifiсation",sample_chambers, stain_volume, num_reps,            45)
    apply_and_incubate(protocol, pipette, wash_buffer,      "Wash",         sample_chambers, wash_volume,  2,                   wash_incubation_time, puncture=False)
    temp_mod.quick_temp(incubation_temp)
    apply_and_incubate(protocol, pipette, wells.post_block, "Post-block",   sample_chambers, stain_volume, num_reps,            15)
    apply_and_incubate(protocol, pipette, wells.detection,  "Detection",    sample_chambers, stain_volume, 1,                   30)
    temp_mod.quick_temp(room_temp)
    apply_and_incubate(protocol, pipette, wash_buffer,      "Wash",         sample_chambers, wash_volume,  3,                   wash_incubation_time, puncture=False)
    apply_and_incubate(protocol, pipette, nuclear_stain,    "Nuclear stain",sample_chambers, wash_volume,  2,                   2.5)
    apply_and_incubate(protocol, pipette, wash_buffer,      "Wash",         sample_chambers, wash_volume,  3,                   wash_incubation_time, puncture=False)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette, omnistainer)
    temp_mod.quick_temp(storage_temp)

    protocol.pause("Protocol paused for 4C storage. Hit resume to end")

