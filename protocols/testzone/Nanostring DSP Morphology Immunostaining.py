metadata = {
    'protocolName': 'Nanostring GeoMx DSP Morphology immunostaining',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Morphology immunostaining protocol post-HIER for Nanostring GeoMx DSP platform',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath']
omnistainer_type = 'omni_stainer_s12_slides'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 2

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Buffer W blocking time' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
buffer_w_incubation = 30

### VERAO VAR NAME='Primary Ab incubation time' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
primary_ab_incubation = 60

### VERAO VAR NAME='Secondary Ab incubation time' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
secondary_ab_incubation = 30

### VERAO VAR NAME='Secondary Ab incubation time' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
conj_syto_incubation = 30

### VERAO VAR NAME='SSC wash incubation time' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
wash_incubation = 5

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody staining volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 3

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12 module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 2

### VERAO VAR NAME='Deck position: Buffer W/ Antibodies plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_plate_position = 1

### VERAO VAR NAME='Deck position: 300ul tip rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='Deck position: 300ul tip rack#2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 9

### VERAO VAR NAME='TEST MODE (ALL INCUBATION DELAYS WILL BE SKIPPED)' TYPE=BOOLEAN
testmode = False

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.ab_plate = ab_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1, 'tiprack 300ul 1')
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_2, 'tiprack 300ul 2')

    pipette_type = 'p300_single_gen2'
    
    pipette = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks = [tiprack_300_1,tiprack_300_2])
    
    pipette.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos-1]

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, 'codex_12-trough buffers reservoir')
    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_plate, '96-well-plate')

    wash_buffer = trough12.wells_by_name()['A11']

    buffer_W_wells = reagents_96plate.rows()[0][:num_samples]
    primary_ab_wells = reagents_96plate.rows()[1][:num_samples]
    secondary_ab_wells = reagents_96plate.rows()[2][:num_samples]
    conj_syto_wells = reagents_96plate.rows()[3][:num_samples]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################
    protocol.comment("Starting the "+ metadata["protocolName"] +" for samples:" + str(sample_chambers))

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette, omnistainer)

    apply_and_incubate(protocol, pipette, buffer_W_wells,       "buffer W"      ,sample_chambers,   ab_volume,     1, buffer_w_incubation                                      )
    apply_and_incubate(protocol, pipette, primary_ab_wells,     "primary Ab"    ,sample_chambers,   ab_volume,     1, primary_ab_incubation                                    )
    apply_and_incubate(protocol, pipette, wash_buffer,          "2x SSC Wash"   ,sample_chambers,   wash_volume,   2, wash_incubation,         step_repeats = 2                )
    apply_and_incubate(protocol, pipette, secondary_ab_wells,   "secondary Ab"  ,sample_chambers,   ab_volume,     1, secondary_ab_incubation                                  )
    apply_and_incubate(protocol, pipette, wash_buffer,          "2x SSC Wash"   ,sample_chambers,   wash_volume,   2, wash_incubation,         step_repeats = 2, puncture=False)
    apply_and_incubate(protocol, pipette, conj_syto_wells,      "conj + syto"   ,sample_chambers,   ab_volume,     1, conj_syto_incubation                                     )
    apply_and_incubate(protocol, pipette, wash_buffer,          "2x SSC Wash"   ,sample_chambers,   wash_volume,   2, wash_incubation,         step_repeats = 2, puncture=False)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette, omnistainer)
