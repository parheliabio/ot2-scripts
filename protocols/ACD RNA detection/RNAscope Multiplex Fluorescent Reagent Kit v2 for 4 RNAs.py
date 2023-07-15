
metadata = {
    'protocolName': 'ACD multiplexed v2',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'ACD multiplexed v2',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps_with_thermosheath']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['black_96', 'parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

# The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='FFPE' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='double application of key solutions' TYPE=BOOLEAN
double_add = True

# The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='Avidin and Biotin block' TYPE=BOOLEAN
avidin_and_biotin_block = False
### VERAO VAR NAME='preblock_incubation' TYPE=BOOLEAN
preblock_incubation = False

### VERAO VAR NAME='protease treatment' TYPE=BOOLEAN
protease_treatment = False

### VERAO VAR NAME='Temp lag for adjusting the temp' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALS
templag = 30
"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the PAR2 device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the 96-well plate
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""

### VERAO VAR NAME='labwarePositions.heatmodule_position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
heatmodule_position = 7

### VERAO VAR NAME='labwarePositions.wash_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
wash_buffers_plate_position = 4

### VERAO VAR NAME='labwarePositions.additional_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
additional_buffers_plate_position = 5

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_1 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_1_position = 1

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_2 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_2_position = 2

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_3 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_3_position = 3

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 9

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 2

### VERAO VAR NAME='Number of RNAs for codetection' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_RNAs = 1

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='RNA_hybridization time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
hybridization_time_minutes = 600

### VERAO VAR NAME='RNA protocol protease incubation time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=900 DECIMAL=FALSE
protease_incubation_time = 30

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 100

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 55

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

labwarePositions = Object()
labwarePositions.wash_buffers_plate = wash_buffers_plate_position
labwarePositions.additional_buffers_plate = additional_buffers_plate_position
labwarePositions.rna_reagents_plate_1 = rna_reagents_plate_1_position
labwarePositions.rna_reagents_plate_2 = rna_reagents_plate_2_position
labwarePositions.rna_reagents_plate_3 = rna_reagents_plate_3_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position

labwarePositions.heatmodule = heatmodule_position

####################GENERAL SETUP#########s#######################


####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5


#####################CUSTOM LABWARE_DEFINITION###################

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1,
                                          'tiprack 300ul 1')
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_2,
                                          'tiprack 300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_300_1, tiprack_300_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos - 1]

    temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)

    omnistainer = temp_mod.load_labware(omnistainer_type)

    rna_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.wash_buffers_plate,
                                         '12-trough buffers reservoir')

    buffer_wells = rna_trough12.wells_by_name()

    #    additional_buffer_wells = rna_trough12_addon.wells_by_name()

    RNA_reagents_96plate_1 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_1,
                                                   '96-well-plate')
    RNA_reagents_96plate_2 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_2,
                                                   '96-well-plate')
    RNA_reagents_96plate_3 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_3,
                                                   '96-well-plate')

    buffers = Object()

    probes_and_amps_wells = list(range(4))

    HRP_wells = list(range(4))
    Tyramide_wells = list(range(4))
    Substrate_wells = list(range(4))
    HRPblocker_wells = list(range(4))

    #    buffers.parhelia_rnawash_buffer = buffer_wells['A8']
    #    buffers.water = additional_buffer_wells['A10']
    #    buffers.storage = additional_buffer_wells['A12']
    buffers.water = buffer_wells['A10']
    buffers.storage = buffer_wells['A12']

    H2O2wash1_wells = RNA_reagents_96plate_1.rows()[0]  # could be used for the protease
    preblock_wells = RNA_reagents_96plate_1.rows()[1]
    avidinblock_wells = RNA_reagents_96plate_1.rows()[2]
    biotinblock_wells = RNA_reagents_96plate_1.rows()[3]
    probe_wells = RNA_reagents_96plate_1.rows()[4]
    amp1_wells = RNA_reagents_96plate_1.rows()[5]
    amp2_wells = RNA_reagents_96plate_1.rows()[6]
    amp3_wells = RNA_reagents_96plate_1.rows()[7]

    probes_and_amps_wells[0] = probe_wells
    probes_and_amps_wells[1] = amp1_wells
    probes_and_amps_wells[2] = amp2_wells
    probes_and_amps_wells[3] = amp3_wells

    probes_and_amps_incubation_times = [hybridization_time_minutes, 30, 15, 30]

    keeping_the_tips = [False, True, True, True]

    comments = ["probes hyb", "amp1", "amp2", "amp3"]

    HRP_wells[0] = RNA_reagents_96plate_2.rows()[0]
    Substrate_wells[0] = RNA_reagents_96plate_2.rows()[1]
    Tyramide_wells[0] = RNA_reagents_96plate_2.rows()[2]

    HRPblocker_wells[0] = RNA_reagents_96plate_2.rows()[3]

    HRP_wells[1] = RNA_reagents_96plate_2.rows()[4]
    Substrate_wells[1] = RNA_reagents_96plate_2.rows()[5]
    Tyramide_wells[1] = RNA_reagents_96plate_2.rows()[6]

    HRPblocker_wells[1] = RNA_reagents_96plate_2.rows()[7]

    HRP_wells[2] = RNA_reagents_96plate_3.rows()[0]
    Substrate_wells[2] = RNA_reagents_96plate_3.rows()[1]
    Tyramide_wells[2] = RNA_reagents_96plate_3.rows()[2]

    HRPblocker_wells[2] = RNA_reagents_96plate_3.rows()[3]

    HRP_wells[3] = RNA_reagents_96plate_3.rows()[4]
    Substrate_wells[3] = RNA_reagents_96plate_3.rows()[5]
    Tyramide_wells[3] = RNA_reagents_96plate_3.rows()[6]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################

    protocol.comment("Starting the RNA staining protocol for samples:" + str(sample_chambers))
    protocol.home()

    # PRE-HYB WASHING SAMPLES WITH water at room temperature
    protocol.comment("puncturing the water well")
    # puncturing the foil
    puncture_wells(pipette_300, buffers.water, height_offset=30, keep_tip=True)

    protocol.comment("washing with water")
    openShutter(protocol, pipette_300, omnistainer)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)
    closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    temp_mod.set_temperature(42)
    protocol.delay(minutes=templag)

    protocol.comment("puncturing protease wells")
    for i in range(len(sample_chambers)):
        puncture_wells(pipette_300, H2O2wash1_wells[i], height_offset=13,
                       keep_tip=True)  # cycle is needed to puncture only the columns in use

    # PROTEASE TREATMENT
    if protease_treatment:
        protocol.comment("applying the protease")
        openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, H2O2wash1_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        protocol.comment("protease incubation: 30 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=protease_incubation_time)

        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 4, keep_tip=True)
        closeShutter(protocol, pipette_300, omnistainer)

    # BLOCKING THE BIOTIN
    if avidin_and_biotin_block:

        temp_mod.set_temperature(25)
        protocol.delay(minutes=templag)

        # AVIDIN block
        protocol.comment("puncturing avi-block wells")
        puncture_wells(pipette_300, avidinblock_wells, height_offset=13)

        protocol.comment("applying the preblock")
        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, avidinblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("avidin block incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)

        # BIOTIN block
        protocol.comment("puncturing biotin-block wells")
        puncture_wells(pipette_300, biotinblock_wells, height_offset=13)

        protocol.comment("applying the biotin")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, biotinblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("biotin block incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        protocol.delay(minutes=15)

        openShutter(protocol, pipette_300, omnistainer)
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        temp_mod.set_temperature(42)
        protocol.delay(minutes=templag)

    # WASHING SAMPLES WITH PROBE DILUENT
    if preblock_incubation:
        protocol.comment("puncturing the preblock")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, preblock_wells, height_offset=13, keep_tip=True)

        openShutter(protocol, pipette_300, omnistainer)

        protocol.comment("applying the probe diluent")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, preblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        #    pipette_300.drop_tip()
        protocol.comment("preblockblock incubation: 1 h")
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        protocol.delay(minutes=60)

    # Puncture Parhelia RNA WASH BUFFER
    protocol.comment("puncturing the ACD wash buffer")
    for i in range(len(sample_chambers)):
        puncture_wells(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], height_offset=30, keep_tip=True)
    pipette_300.drop_tip()

    # applying probes and amps

    for z in range(4):

        protocol.home()

        protocol.comment(comments[z])
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, probes_and_amps_wells[z][i], height_offset=13, keep_tip=keeping_the_tips[z])

        openShutter(protocol, pipette_300, omnistainer)

        if double_add:
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, probes_and_amps_wells[z][i], sample_chambers[i], ab_volume, 1,
                            keep_tip=keeping_the_tips[z])
            protocol.delay(minutes=1)
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, probes_and_amps_wells[z][i], sample_chambers[i], ab_volume, 1,
                        keep_tip=keeping_the_tips[z])

        protocol.comment("incubation: " + str(probes_and_amps_incubation_times[z]) + "min")
        closeShutter(protocol, pipette_300, omnistainer)

        protocol.delay(minutes=probes_and_amps_incubation_times[z])

        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

    # HERE the final iterative branch detection starts

    protocol.comment("puncturing the storage well")
    puncture_wells(pipette_300, buffers.storage, height_offset=30, keep_tip=True)

    for z in range(num_RNAs):
        # Filling the flow cell with storage buffer before ramping down to room temperature

        channel = z + 1

        if z > 0:  # only done in cycles 2,3 and 4

            protocol.home()
            protocol.comment("filling with storage buffer")
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume, 2, keep_tip=True)
            closeShutter(protocol, pipette_300, omnistainer)

            temp_mod.set_temperature(42)
            protocol.delay(minutes=templag)

            # Blocking the channel 1 HRP
            # First HRP block
            protocol.comment("puncturing HRP_block " + str(z))
            puncture_wells(pipette_300, HRPblocker_wells[z - 1], height_offset=13, keep_tip=True)

            openShutter(protocol, pipette_300, omnistainer)
            protocol.comment("applying the HRP_block " + str(z))
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, HRPblocker_wells[z - 1][i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            #    pipette_300.drop_tip()
            protocol.comment("HRP_block " + str(z) + ": 5 min")
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=5)

            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.comment("applying the HRP_block " + str(z))
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, HRPblocker_wells[z - 1][i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            #    pipette_300.drop_tip()
            protocol.comment("HRP_block " + str(z) + ": 10 min")
            closeShutter(protocol, pipette_300, omnistainer)
            protocol.delay(minutes=10)

            # WASHING WITH PARHELIA RNA WASHING REAGENT
            protocol.comment("washing in ACD wash buffer")
            for wash_counter in range(3):
                openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
                for i in range(len(sample_chambers)):
                    washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i],
                                wash_volume, 2, keep_tip=True)
                #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
                closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
                protocol.delay(minutes=1, msg="incubation in ACD wash buffer")
            pipette_300.drop_tip()

        protocol.comment("puncturing HRP channel " + str(channel) + " wells")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, HRP_wells[z][i], height_offset=13, keep_tip=True)

        protocol.comment("applying the HRP channel " + str(channel))
        openShutter(protocol, pipette_300, omnistainer)
        if double_add:
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, HRP_wells[z][i], sample_chambers[i], ab_volume, 1)
            protocol.delay(minutes=1)
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, HRP_wells[z][i], sample_chambers[i], ab_volume, 1)
        #    pipette_300.drop_tip()
        protocol.comment("HRP channel " + str(channel) + " incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        # WASHING WITH 0.5 WASH BUFFER
        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i],
                            wash_volume, 2, keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        temp_mod.set_temperature(25)
        protocol.delay(minutes=templag)

        # DILUTING AND APPLYING THE Ch1 tyramide
        protocol.comment("puncturing the Ch" + str(channel) + " tyramide")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, Tyramide_wells[z][i], height_offset=13, keep_tip=True)

        protocol.comment("puncturing the substrate buffer wells")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, Substrate_wells[z][i], height_offset=13, keep_tip=True)

        protocol.comment("applying the Ch" + str(channel) + " tyramide")
        openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            dilute_and_apply_fixative(pipette_300, Tyramide_wells[z][i], Substrate_wells[z][i], Tyramide_wells[z][i],
                                      2 * ab_volume)
        if double_add:
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, Tyramide_wells[z][i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            protocol.delay(minutes=1)
        for i in range(len(sample_chambers)):
            washSamples(pipette_300, Tyramide_wells[z][i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        protocol.comment("developing Ch" + str(z) + " tyramide")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(3):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i],
                            wash_volume, 2, keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=1, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

    temp_mod.set_temperature(25)





