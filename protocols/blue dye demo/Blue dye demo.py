## VERAO GLOBAL
from global_functions import *
### END VERAO GLOBAL

metadata = {
    'protocolName': 'Parhelia Blue Dye Demo v5',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'A protocol for testing liquid exchange in Parhelia Omni-Stainer™',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_c12_cslps', 'par2s_9slides_blue_v3', 'par2c_12coverslips']
omnistainer_type = 'omni_stainer_s12_slides'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 1

### VERAO VAR NAME='Number of Exchange Cycles' TYPE=NUMBER LBOUND=1 UBOUND=10 DECIMAL=FALSE
num_reps = 1

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Stain buffer volume (uL)' TYPE=NUMBER LBOUND=25 UBOUND=300 DECIMAL=FALSE
stain_volume = 110

### VERAO VAR NAME='Wash buffer volume (uL)' TYPE=NUMBER LBOUND=25 UBOUND=300 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=2.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.4

####################LABWARE LAYOUT ON DECK#########################

### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

labwarePositions = Object()
labwarePositions.buffers_plate = 3
labwarePositions.omnistainer = 2
labwarePositions.tiprack_300 = 6


def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single',
                                           pipette_300_location, tip_racks=[tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos - 1]

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    buffer_wells = trough12.wells_by_name()
    buffers = Object()
    buffers.clear = buffer_wells['A1']
    buffers.blue = buffer_wells['A2']

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################
    protocol.comment("Starting the DEMO BLUE DYE protocol for samples:" + str(sample_chambers))

    for iterator in range(0, num_reps):
        protocol.comment("Applying blue staining reagent to the sample")
        washSamples(pipette_300, buffers.blue, sample_chambers, stain_volume, num_repeats=1)

        protocol.comment("Washing with clear buffer")
        washSamples(pipette_300, buffers.clear, sample_chambers, wash_volume, num_repeats=2)
# protocol exported from Parhelia StainWorks Aug 2 2023 4pm PST