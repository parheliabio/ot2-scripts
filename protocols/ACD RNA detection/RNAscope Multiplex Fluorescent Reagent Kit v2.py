## VERAO GLOBAL
## Copyright Parhelia Biosciences Corporation 2022-2023
### GLOBAL FUNCTIONS - AUTO-GENERATED - DO NOT MODIFY ###
from opentrons import protocol_api
import json


class Object:
    pass


####################GENERAL SETUP################################
stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.15
extra_bottom_gap = 0


def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, height_offset=0, keep_tip=False):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    print('Samples are:')
    print(samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

    height_offset += extra_bottom_gap

    for i in range(0, num_repeats):
        for s in samples:
            print(s)
            print("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell.bottom(height_offset), rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(height_offset), rate=sample_flow_rate)
            stats.volume += volume

    if not keep_tip: pipette.drop_tip()


def puncture_wells(pipette, wells, height_offset=0, keep_tip=False):
    try:
        iter(wells)
    except TypeError:
        wells = [wells]
    for well in wells:
        washSamples(pipette, well, well, 1, 1, height_offset, keep_tip=True)
    if not keep_tip: pipette.drop_tip()


def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume, height_offset=0,
                              keep_tip=False):
    if not pipette.has_tip: pipette.pick_up_tip()
    # Diluting fixative:
    pipette.aspirate(volume, dilutant_buffer_well, rate=well_flow_rate)
    pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    for iterator in range(0, 3):
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)

    washSamples(pipette, sourceSolutionWell, samples, volume, 1, height_offset, keep_tip=keep_tip)


def getOmnistainerWellsList(omnistainer, num_samples):
    sample_chambers = []

    if (len(omnistainer.wells_by_name()) < num_samples):
        raise Exception("number of wells in the Omni-Stainer less than num_samples")

    wellslist = list(omnistainer.wells_by_name().keys())
    wellslist = wellslist[1:num_samples + 1]

    for well in wellslist:
        sample_chambers.append(omnistainer.wells_by_name()[well])

    print("omnistainer.wells_by_name are:")
    print(omnistainer.wells_by_name())
    print("sample_chambers are:")
    print(sample_chambers)
    return sample_chambers


def mix(pipette, sourceSolutionWell, volume, num_repeats):
    if not pipette.has_tip: pipette.pick_up_tip()

    for i in range(0, num_repeats):
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()


def openShutter(protocol, pipette, covered_lbwr, keep_tip=False):
    if not pipette.has_tip:
        pipette.pick_up_tip()
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 1].bottom(0), force_direct=True)
    protocol.delay(seconds=1)
    if not keep_tip: pipette.drop_tip()


def closeShutter(protocol, pipette, covered_lbwr, keep_tip=False):
    if not pipette.has_tip:
        pipette.pick_up_tip()
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 2].bottom(0))
    pipette.move_to(covered_lbwr.wells()[len(covered_lbwr.wells()) - 3].bottom(0), force_direct=True)
    protocol.delay(seconds=1)
    if not keep_tip: pipette.drop_tip()


### END VERAO GLOBAL


metadata = {
    'protocolName': '3 probes RNA ACD v2',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': '3 probes RNA ACD v2',
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

# The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='Avidin and Biotin block' TYPE=BOOLEAN
avidin_and_biotin_block = False

### VERAO VAR NAME='Type of protocol' TYPE=CHOICE OPTIONS=['RNA only','RNA and CODEX','CODEX only']
type_of_protocol = 'RNA only'

### VERAO VAR NAME='Antibody screening mode' TYPE=BOOLEAN
Antibody_Screening = True

### VERAO VAR NAME='Overnight incubation: enable manual pausing at the antibody incubation step?' TYPE=BOOLEAN
protocol_pause = False

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

### VERAO VAR NAME='labwarePositions.buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 4

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_1 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_1_position = 1

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_2 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
rna_reagents_plate_2_position = 2

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_buffers_plate_position = 5

### VERAO VAR NAME='Deck position: Preblock/Antibody/F reagents plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_reagents_plate_position = 3

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 9

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 4

### VERAO VAR NAME='Number of RNAs for codetection' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_RNAs = 1

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='RNA_hybridization time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
hybridization_time_minutes = 120

### VERAO VAR NAME='CODEX Antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=900 DECIMAL=FALSE
ab_incubation_time_minutes = 120

### VERAO VAR NAME='RNA protocol protease incubation time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=900 DECIMAL=FALSE
protease_incubation_time = 30

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 100

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 60

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.15

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
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.rna_reagents_plate_1 = rna_reagents_plate_1_position
labwarePositions.rna_reagents_plate_2 = rna_reagents_plate_2_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position

labwarePositions.codex_buffers_plate = codex_buffers_plate_position

labwarePositions.codex_reagents_plate = codex_reagents_plate_position

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

    if type_of_protocol in ['RNA and CODEX']:
        rna_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate,
                                             '12-trough buffers reservoir')
        codex_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.codex_buffers_plate,
                                               'codex_12-trough buffers reservoir')

        CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate,
                                                       'codex_96-well-plate')
        RNA_reagents_96plate_1 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_1,
                                                       '96-well-plate')
        RNA_reagents_96plate_2 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_2,
                                                       '96-well-plate')
        codex_buffers = Object()

        buffers = Object()
        buffer_wells = rna_trough12.wells_by_name()
        buffers.parhelia_rnawash_buffer = buffer_wells['A8']
        buffers.water = buffer_wells['A10']
        buffers.storage = buffer_wells['A12']

        H2O2wash1_wells = RNA_reagents_96plate_1.rows()[0]
        preblock_wells = RNA_reagents_96plate_1.rows()[1]
        avidinblock_wells = RNA_reagents_96plate_1.rows()[2]
        biotinblock_wells = RNA_reagents_96plate_1.rows()[3]
        probe_wells = RNA_reagents_96plate_1.rows()[4]
        amp1_wells = RNA_reagents_96plate_1.rows()[5]
        amp2_wells = RNA_reagents_96plate_1.rows()[6]
        amp3_wells = RNA_reagents_96plate_1.rows()[7]

        HRPC1_wells = RNA_reagents_96plate_2.rows()[0]
        substrate_wells_1 = RNA_reagents_96plate_2.rows()[1]
        Ch1_tyramide_wells = RNA_reagents_96plate_2.rows()[2]

        HRPC1_block1_wells = RNA_reagents_96plate_2.rows()[3]
        HRPC1_block2_wells = RNA_reagents_96plate_2.rows()[4]

        HRPC2_wells = RNA_reagents_96plate_2.rows()[5]
        substrate_wells_2 = RNA_reagents_96plate_2.rows()[6]
        Ch2_tyramide_wells = RNA_reagents_96plate_2.rows()[7]

        codex_buffer_wells = codex_trough12.wells_by_name()
        codex_buffers.Hydration_PFA_1pt6pct = codex_buffer_wells['A1']
        codex_buffers.Staining = codex_buffer_wells['A2']
        codex_buffers.Storage_PFA_4pct = codex_buffer_wells['A3']
        codex_buffers.MeOH = codex_buffer_wells['A4']
        codex_buffers.PBS = codex_buffer_wells['A5']
        codex_buffers.CODEX_buffer_1x = codex_buffer_wells['A6']
        codex_buffers.Screening_Buffer = codex_buffer_wells['A7']
        codex_buffers.Stripping_buffer = codex_buffer_wells['A8']
        codex_buffers.storage = codex_buffer_wells['A9']

        codex_preblock_wells = CODEX_reagents_96plate.rows()[0]
        codex_antibody_wells = CODEX_reagents_96plate.rows()[1]
        codex_reagent_F_wells = CODEX_reagents_96plate.rows()[2]
        codex_rendering_wells = CODEX_reagents_96plate.rows()[3]

    if type_of_protocol in ['RNA only']:
        rna_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate,
                                             '12-trough buffers reservoir')
        RNA_reagents_96plate_1 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_1,
                                                       '96-well-plate')
        RNA_reagents_96plate_2 = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate_2,
                                                       '96-well-plate')

        buffers = Object()
        buffer_wells = rna_trough12.wells_by_name()
        buffers.parhelia_rnawash_buffer = buffer_wells['A8']
        buffers.water = buffer_wells['A10']
        buffers.storage = buffer_wells['A12']

        H2O2wash1_wells = RNA_reagents_96plate_1.rows()[0]  #could be used for the protease
        preblock_wells = RNA_reagents_96plate_1.rows()[1]
        avidinblock_wells = RNA_reagents_96plate_1.rows()[2]
        biotinblock_wells = RNA_reagents_96plate_1.rows()[3]
        probe_wells = RNA_reagents_96plate_1.rows()[4]
        amp1_wells = RNA_reagents_96plate_1.rows()[5]
        amp2_wells = RNA_reagents_96plate_1.rows()[6]
        amp3_wells = RNA_reagents_96plate_1.rows()[7]

        HRPC1_wells = RNA_reagents_96plate_2.rows()[0]
        substrate_wells_1 = RNA_reagents_96plate_2.rows()[1]
        Ch1_tyramide_wells = RNA_reagents_96plate_2.rows()[2]

        HRPC1_block1_wells = RNA_reagents_96plate_2.rows()[3]
        HRPC1_block2_wells = RNA_reagents_96plate_2.rows()[4]

        HRPC2_wells = RNA_reagents_96plate_2.rows()[5]
        substrate_wells_2 = RNA_reagents_96plate_2.rows()[6]
        Ch2_tyramide_wells = RNA_reagents_96plate_2.rows()[7]

    if type_of_protocol in ['CODEX only']:
        codex_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.codex_buffers_plate,
                                               'codex_12-trough buffers reservoir')

        CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate,
                                                       'codex_96-well-plate')
        codex_buffers = Object()
        codex_buffer_wells = codex_trough12.wells_by_name()
        codex_buffers.Hydration_PFA_1pt6pct = codex_buffer_wells['A1']
        codex_buffers.Staining = codex_buffer_wells['A2']
        codex_buffers.Storage_PFA_4pct = codex_buffer_wells['A3']
        codex_buffers.MeOH = codex_buffer_wells['A4']
        codex_buffers.PBS = codex_buffer_wells['A5']
        codex_buffers.CODEX_buffer_1x = codex_buffer_wells['A6']
        codex_buffers.Screening_Buffer = codex_buffer_wells['A7']
        codex_buffers.Stripping_buffer = codex_buffer_wells['A8']
        codex_buffers.storage = codex_buffer_wells['A9']

        codex_preblock_wells = CODEX_reagents_96plate.rows()[0]
        codex_antibody_wells = CODEX_reagents_96plate.rows()[1]
        codex_reagent_F_wells = CODEX_reagents_96plate.rows()[2]
        codex_rendering_wells = CODEX_reagents_96plate.rows()[3]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################

    protocol.comment("Starting the RNA staining protocol for samples:" + str(sample_chambers))
    protocol.home()
    if type_of_protocol in ['RNA and CODEX', 'RNA only']:
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
        puncture_wells(pipette_300, H2O2wash1_wells, height_offset=13)

        #PROTEASE TREATMENT
        protocol.comment("applying the protease")
        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, H2O2wash1_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        pipette_300.drop_tip()
        protocol.comment("protease incubation: 30 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=protease_incubation_time)

        openShutter(protocol, pipette_300, omnistainer)
        washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 4, keep_tip=True)
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        #BLOCKING THE BIOTIN
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

            protocol.comment("applying the preblock")
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
        protocol.comment("puncturing the preblock")
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

        # APPLYING probe COCKTAILS TO SAMPLES
        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        protocol.comment("puncturing and applying abs")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, probe_wells[i], probe_wells[i], 2, 1, height_offset=13)
            washSamples(pipette_300, probe_wells[i], sample_chambers[i], ab_volume, 1)

        protocol.comment("staining incubation: " + str(hybridization_time_minutes) + "min")
        closeShutter(protocol, pipette_300, omnistainer)

        protocol.delay(minutes=hybridization_time_minutes)

        protocol.home()

        # WASHING WITH Parhelia RNA WASH BUFFER
        protocol.comment("puncturing the ACD wash buffer")
        for i in range(len(sample_chambers)):
            puncture_wells(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], height_offset=30, keep_tip=True)
        pipette_300.drop_tip()

        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        # AMP 1
        protocol.comment("puncturing amp1 wells")
        puncture_wells(pipette_300, amp1_wells, height_offset=13, keep_tip=True)
        #    pipette_300.drop_tip()

        openShutter(protocol, pipette_300, omnistainer)
        protocol.comment("applying the AMP1")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, amp1_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        #    pipette_300.drop_tip()
        protocol.comment("AMP1 incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=30)

        # WASHING WITH Parhelia RNA WASH BUFFER

        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        # AMP 2
        protocol.comment("puncturing amp2 wells")
        puncture_wells(pipette_300, amp2_wells, height_offset=13, keep_tip=True)
        #    pipette_300.drop_tip()
        openShutter(protocol, pipette_300, omnistainer)
        protocol.comment("applying the AMP2")
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, amp2_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        #    pipette_300.drop_tip()
        protocol.comment("AMP2 incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=30)

        # WASHING WITH Parhelia RNA WASH BUFFER
        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        # AMP 3
        protocol.comment("puncturing amp3 wells")
        puncture_wells(pipette_300, amp3_wells, height_offset=13, keep_tip=True)

        protocol.comment("applying the AMP3")
        openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, amp3_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
        #    pipette_300.drop_tip()
        protocol.comment("AMP3 incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        # WASHING WITH Parhelia RNA WASH BUFFER
        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        # puncturing HRPC1 wells"
        protocol.comment("puncturing HRPC1 wells")
        puncture_wells(pipette_300, HRPC1_wells, height_offset=13, keep_tip=True)

        protocol.comment("applying the HRPC1")
        openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            protocol.comment(i)
            washSamples(pipette_300, HRPC1_wells[i], sample_chambers[i], ab_volume, 1)
        #    pipette_300.drop_tip()
        protocol.comment("HRP-C1 incubation: 15 min")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=15)

        # WASHING WITH Parhelia RNA WASH BUFFER
        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(4):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=4, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        temp_mod.set_temperature(25)
        protocol.delay(minutes=templag)

        # DILUTING AND APPLYING THE Ch1 tyramide
        protocol.comment("puncturing the Ch1 tyramide")
        puncture_wells(pipette_300, Ch1_tyramide_wells, height_offset=13, keep_tip=True)

        protocol.comment("puncturing the substrate buffer wells")
        puncture_wells(pipette_300, substrate_wells_1, height_offset=13, keep_tip=True)

        protocol.comment("applying Ch1 tyramide")
        openShutter(protocol, pipette_300, omnistainer)
        for i in range(len(sample_chambers)):
            dilute_and_apply_fixative(pipette_300, Ch1_tyramide_wells[i], substrate_wells_1[i], sample_chambers[i],
                                      ab_volume)

        protocol.comment("developing Ch1 tyramide")
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=30)


        # WASHING WITH Parhelia RNA WASH BUFFER
        protocol.comment("washing in ACD wash buffer")
        for wash_counter in range(3):
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            for i in range(len(sample_chambers)):
                washSamples(pipette_300, buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 2,
                            keep_tip=True)
            #            washSamples(pipette_300,  buffer_wells[list(buffer_wells.keys())[i]], sample_chambers[i], wash_volume, 1)
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=1, msg="incubation in ACD wash buffer")
        pipette_300.drop_tip()

        if num_RNAs == 2:
            # Filling the flow cell with storage buffer before ramping down to room temperature
            protocol.comment("puncturing the storage well")
            puncture_wells(pipette_300, buffers.storage, height_offset=30, keep_tip=True)

            protocol.home()
            protocol.comment("filling with storage buffer")
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume, 2, keep_tip=True)
            closeShutter(protocol, pipette_300, omnistainer)

            temp_mod.set_temperature(42)
            protocol.delay(minutes=templag)

            # Blocking the channel 1 HRP
            # First HRP block
            protocol.comment("puncturing HRPC1_block1 and HRPC1_block2")
            puncture_wells(pipette_300, HRPC1_block1_wells, height_offset=13, keep_tip=True)
            puncture_wells(pipette_300, HRPC1_block2_wells, height_offset=13, keep_tip=True)

            openShutter(protocol, pipette_300, omnistainer)
            protocol.comment("applying the HRP_block1")
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, HRPC1_block1_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            #    pipette_300.drop_tip()
            protocol.comment("HRP_block1: 15 min")
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.delay(minutes=5)

            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
            protocol.comment("applying the HRP_block2")
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, HRPC1_block2_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
            #    pipette_300.drop_tip()
            protocol.comment("HRP_block2: 15 min")
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

            protocol.comment("puncturing HRPC2 wells")
            puncture_wells(pipette_300, HRPC2_wells, height_offset=13, keep_tip=True)

            protocol.comment("applying the HRPC2")
            openShutter(protocol, pipette_300, omnistainer)
            for i in range(len(sample_chambers)):
                protocol.comment(i)
                washSamples(pipette_300, HRPC2_wells[i], sample_chambers[i], ab_volume, 1)
            #    pipette_300.drop_tip()
            protocol.comment("HRP-C1 incubation: 15 min")
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
            protocol.comment("puncturing the Ch1 tyramide")
            puncture_wells(pipette_300, Ch2_tyramide_wells, height_offset=13, keep_tip=True)

            protocol.comment("puncturing the substrate buffer wells")
            puncture_wells(pipette_300, substrate_wells_2, height_offset=13, keep_tip=True)

            protocol.comment("applying Ch1 tyramide")
            openShutter(protocol, pipette_300, omnistainer)
            for i in range(len(sample_chambers)):
                dilute_and_apply_fixative(pipette_300, Ch2_tyramide_wells[i], substrate_wells_2[i], sample_chambers[i],
                                          ab_volume)

            protocol.comment("developing Ch1 tyramide")
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

    if type_of_protocol in ['RNA and CODEX', 'CODEX only']:

        # CODEX protocol starts here

        protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))
        protocol.home()

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        if not FFPE:
            # WASHING SAMPLES WITH PFA
            protocol.comment("puncturing first fix")
            puncture_wells(pipette_300, codex_buffers.Hydration_PFA_1pt6pct, height_offset=30)
            protocol.comment("first fix")
            washSamples(pipette_300, codex_buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume, 1)
            # INCUBATE
            protocol.delay(minutes=10, msg="first fix incubation")

        # WASHING SAMPLES WITH S2
        protocol.comment("puncture S2")
        puncture_wells(pipette_300, codex_buffers.Staining, height_offset=30)
        protocol.comment("wash in S2")
        washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)

        # PUNCTURING THE PREBLOCK
        protocol.comment("puncturing the preblock")
        puncture_wells(pipette_300, codex_preblock_wells, height_offset=13)

        # WASHING SAMPLES WITH PREBLOCK
        protocol.comment("preblocking")
        for i in range(num_samples):
            washSamples(pipette_300, codex_preblock_wells[i], sample_chambers[i], wash_volume, 1, keep_tip=True)
        # INCUBATE

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer)

        protocol.delay(minutes=15, msg="preblocking incubation")

        # APPLYING ANTIBODY COCKTAILS TO SAMPLES

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer)

        protocol.comment("applying antibodies")
        for i in range(num_samples):
            protocol.comment("puncturing antibodies")
            puncture_wells(pipette_300, codex_antibody_wells[i], height_offset=13)
            protocol.comment("applying antibodies")
            washSamples(pipette_300, codex_antibody_wells[i], sample_chambers[i], ab_volume, 1)
        # INCUBATE
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        if protocol_pause:
            protocol.pause(msg="The protocol is paused for primary ab incubation")
        else:
            protocol.delay(minutes=ab_incubation_time_minutes, msg="staining incubation")

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
        for i in range(2):
            # WASHING SAMPLES WITH Staining buffer
            protocol.comment("first washing with Staining buffer")
            washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)
            # INCUBATE
            protocol.delay(minutes=5, msg="first incubation in Staining Buffer")

        # POST STAINING FIXING SAMPLES WITH PFA
        protocol.comment("puncturing the second fix")
        puncture_wells(pipette_300, codex_buffers.Storage_PFA_4pct, height_offset=30)
        protocol.comment("second fix")
        washSamples(pipette_300, codex_buffers.Storage_PFA_4pct, sample_chambers, wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=5, msg="incubation with fixative")

        # WASHING SAMPLES WITH PBS
        protocol.comment("puncture the PBS wash")
        puncture_wells(pipette_300, codex_buffers.PBS)
        protocol.comment("the PBS wash")
        washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)

        # FIXING SAMPLES WITH Methanol
        protocol.comment("puncturing the Methanol")
        puncture_wells(pipette_300, codex_buffers.MeOH, height_offset=30)
        for i in range(2):
            protocol.comment("applying MeOH")
            washSamples(pipette_300, codex_buffers.MeOH, sample_chambers, wash_volume, 1)
            # INCUBATE
            protocol.delay(minutes=2.5, msg="MeOH incubation")

        # WASHING SAMPLES WITH PBS
        protocol.comment("PBS wash")
        washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)

        # PUNCTURING THE FIXATIVE
        protocol.comment("puncturing the fixative")
        puncture_wells(pipette_300, codex_reagent_F_wells, height_offset=13)

        # DILUTING AND APPLYING THE FIXATIVE
        protocol.comment("applying the fixative")
        for i in range(num_samples):
            dilute_and_apply_fixative(pipette_300, codex_reagent_F_wells[i], codex_buffers.PBS, sample_chambers[i],
                                      wash_volume, keep_tip=True)

        protocol.comment("third fix incubation")

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        protocol.delay(minutes=10, msg="Reagent F incubation")

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer)

        # WASHING SAMPLES WITH PBS
        protocol.comment("PBS wash")
        washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2)

        if Antibody_Screening:
            protocol.comment("puncture the Codex Buffer")
            puncture_wells(pipette_300, codex_buffers.CODEX_buffer_1x, keep_tip=True)
            protocol.comment("puncture the Screening Buffer")
            puncture_wells(pipette_300, codex_buffers.Screening_Buffer, keep_tip=True)
            protocol.comment("puncture the Stripping Buffer")
            puncture_wells(pipette_300, codex_buffers.Stripping_buffer)
            # PRE-CLEARING THE TISSUE
            for i in range(3):
                protocol.comment("tissue clearing round" + str(i + 1))
                washSamples(pipette_300, codex_buffers.Stripping_buffer, sample_chambers, wash_volume, 2)
                protocol.delay(seconds=30)
                washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 1)
                washSamples(pipette_300, codex_buffers.CODEX_buffer_1x, sample_chambers, wash_volume, 1)

            # Equilibration in rendering buffer
            protocol.comment("Equilibration in rendering buffer")
            washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 1)

            # RENDERING
            protocol.comment("Applying rendering solution to wells")
            for i in range(num_samples):
                protocol.comment("puncturing the rendering solution")
                puncture_wells(pipette_300, codex_rendering_wells[i], height_offset=13)
                protocol.comment("Applying the rendering solution to the wells")
                washSamples(pipette_300, codex_rendering_wells[i], sample_chambers[i], wash_volume, 1)
            # INCUBATE
            protocol.delay(minutes=10, msg="rendering hybridization")

            # WASH SAMPLES IN 1x CODEX buffer
            protocol.comment("Washing with rendering buffer")
            washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 2)

        # STORAGE, washing samples every hour for 100 hours
        protocol.comment("puncturing the storage buffer")
        puncture_wells(pipette_300, codex_buffers.storage)
        protocol.comment("applying the storage buffer")
        washSamples(pipette_300, codex_buffers.storage, sample_chambers, wash_volume, 2)

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer)


