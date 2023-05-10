

metadata = {
    'protocolName': 'Parhelia Hematoxylin and Eosin staining',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia Hematoxylin and Eosin staining',
    'apiLevel': '2.7'

}
####################MODIFIABLE RUN PARAMETERS#########################
### VERAO VAR NAME='ANTIGEN RETRIEVAL' TYPE=BOOLEAN
retrieval = False

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'par2s_9slides_blue_v3', 'PAR2c_12coverslips']
omnistainer_type = 'omni_stainer_s12_slides'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 4


### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

### VERAO VAR NAME='How to apply HEMATOXYLIN' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
hematoxylin_source = 'from pcr strip'

### VERAO VAR NAME='How to apply EOSIN' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
eosin_source = 'from pcr strip'

### VERAO VAR NAME='How to apply Clearing reagent' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
clearing_source = 'from pcr strip'

### VERAO VAR NAME='How to apply Blueing reagent' TYPE=CHOICE OPTIONS=['from reagent trough', 'from pcr strip']
blueing_source = 'from pcr strip'

### VERAO VAR NAME='Clearing incubation time (seconds)' TYPE=NUMBER LBOUND=1 UBOUND=1000 DECIMAL=FALSE
clearing_incubation_time_seconds = 60

### VERAO VAR NAME='Blueing incubation time (seconds)' TYPE=NUMBER LBOUND=1 UBOUND=1000 DECIMAL=FALSE
blueing_incubation_time_seconds = 60

### VERAO VAR NAME='Hematoxilin incubation time (seconds)' TYPE=NUMBER LBOUND=1 UBOUND=1000 DECIMAL=FALSE
hematoxylin_incubation_time_seconds = 60

### VERAO VAR NAME='Eosin incubation time (seconds)' TYPE=NUMBER LBOUND=1 UBOUND=1000 DECIMAL=FALSE
eosin_incubation_time_seconds = 60

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

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

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'


### VERAO VAR NAME='labwarePositions.buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 1

### VERAO VAR NAME='labwarePositions.omnistainer' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 2

### VERAO VAR NAME='labwarePositions.ihc_reagents_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
hande_reagents_plate_position = 3

### VERAO VAR NAME='labwarePositions.tiprack_300' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 6


labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.hande_reagents_plate = hande_reagents_plate_position
labwarePositions.tiprack_300 = tiprack_300_position


###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):

    ###########################LABWARE SETUP#################################

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos-1]

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    hande_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.hande_reagents_plate, type_of_96well_plate)

    if (not retrieval):
        omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    if retrieval:
        temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)
        omnistainer = temp_mod.load_labware(omnistainer_type)

    buffer_wells = trough12.wells_by_name()

    buffers = Object()

    buffers.water =  buffer_wells['A1']
    buffers.clearing = buffer_wells['A2']
    buffers.blueing = buffer_wells['A3']
    buffers.eth_70perc =  buffer_wells['A4']
    buffers.eth_80perc =  buffer_wells['A5']
    buffers.eth_95perc =  buffer_wells['A6']
    buffers.eth_100perc = buffer_wells['A7']

    buffers.hematoxylin = buffer_wells['A9']

    buffers.eosin = buffer_wells['A11']
    buffers.clear_rite= buffer_wells['A12']

    clearing_wells = hande_reagents_96plate.rows()[0]
    blueing_wells = hande_reagents_96plate.rows()[1]
    hematoxylin_wells = hande_reagents_96plate.rows()[2]
    eosin_wells = hande_reagents_96plate.rows()[3]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)


    if debug: protocol.comment(sample_chambers)


#################PROTOCOL####################

#WASHING SAMPLES WITH WATER

    puncture_wells(pipette_300, buffers.water, height_offset=30)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2)

#Staining the samples with hematoxylin
    if hematoxylin_source == 'from reagent trough':
        puncture_wells(pipette_300, buffers.hematoxylin, height_offset=30)
        washSamples(pipette_300, buffers.hematoxylin, sample_chambers, wash_volume, 1)
        protocol.delay(seconds=hematoxylin_incubation_time_seconds)
    if hematoxylin_source == 'from pcr strip':
        protocol.comment("puncturing the hematoxylin wells")
        puncture_wells(pipette_300, hematoxylin_wells, height_offset=18)
        protocol.comment("applying hematoxylin")
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, hematoxylin_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
    protocol.delay(seconds=hematoxylin_incubation_time_seconds)


#WASHING SAMPLES WITH WATER
    for i in range (2):
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2)
        protocol.delay(minutes=1)

#Clearing the samples
    if clearing_source == 'from reagent trough':
        puncture_wells(pipette_300, buffers.clearing, height_offset=30)
        pipette_300.drop_tip()
        washSamples(pipette_300, buffers.clearing, sample_chambers, wash_volume, 1)
        protocol.delay(seconds=clearing_incubation_time_seconds)
    if clearing_source == 'from pcr strip':
        protocol.comment("puncturing the clearing wells")
        puncture_wells(pipette_300, clearing_wells, height_offset=18)
        protocol.comment("applying clearing")
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, clearing_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
    protocol.delay(seconds=clearing_incubation_time_seconds)

#WASHING SAMPLES WITH WATER
    for i in range (2):
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2)

#Blueing the samples
    if blueing_source == 'from reagent trough':
        puncture_wells(pipette_300, buffers.blueing, height_offset=30)
        washSamples(pipette_300, buffers.blueing, sample_chambers, wash_volume, 1)
        protocol.delay(seconds=blueing_incubation_time_seconds)
    if blueing_source == 'from pcr strip':
        protocol.comment("puncturing the blueing wells")
        puncture_wells(pipette_300, blueing_wells, height_offset=18)
        protocol.comment("applying blueing")
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, blueing_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
    protocol.delay(seconds=blueing_incubation_time_seconds)

#WASHING SAMPLES WITH WATER
    for i in range (2):
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2)

    puncture_wells(pipette_300, buffers.clear_rite, height_offset=30)

    puncture_wells(pipette_300, buffers.eth_100perc, height_offset=30, keep_tip=True)
    puncture_wells(pipette_300, buffers.eth_95perc, height_offset=30, keep_tip=True)
    puncture_wells(pipette_300, buffers.eth_80perc, height_offset=30, keep_tip=True)
    puncture_wells(pipette_300, buffers.eth_70perc, height_offset=30)


    washSamples(pipette_300, buffers.eth_70perc, sample_chambers, wash_volume, 3,extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_80perc, sample_chambers, wash_volume, 3,extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 3,extra_bottom_gap)

#Staining with eosin
    if eosin_source == 'from reagent trough':
        puncture_wells(pipette_300, buffers.eosin, height_offset=30)
        washSamples(pipette_300, buffers.eosin, sample_chambers, wash_volume, 1)
        protocol.delay(seconds=eosin_incubation_time_seconds)
    if eosin_source == 'from pcr strip':
        protocol.comment("puncturing the eosin wells")
        puncture_wells(pipette_300, eosin_wells, height_offset=18)
        protocol.comment("applying eosin")
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, eosin_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
    protocol.delay(seconds=eosin_incubation_time_seconds)

    washSamples(pipette_300, buffers.eth_95perc, sample_chambers, wash_volume, 2,extra_bottom_gap)
    washSamples(pipette_300, buffers.eth_100perc, sample_chambers, wash_volume, 2,extra_bottom_gap)

    washSamples(pipette_300, buffers.clear_rite, sample_chambers, wash_volume, 2,extra_bottom_gap)


