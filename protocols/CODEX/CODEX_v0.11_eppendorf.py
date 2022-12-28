metadata = {
    'protocolName': 'Parhelia CODEX using Eppendorf rack',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX slide and coverslip staining protocol for Omni-Stainer instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'par2s_9slides_blue_v3', 'PAR2c_12coverslips']
omnistainer_type = 'omni_stainer_s12_slides'

### _doesntwork_ VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 'opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', 'opentrons_24_tuberack_generic_2ml_screwcap', 'opentrons_24_tuberack_nest_0.5ml_screwcap', 'opentrons_24_tuberack_nest_1.5ml_screwcap', 'opentrons_24_tuberack_nest_1.5ml_snapcap', 'opentrons_24_tuberack_nest_2ml_screwcap' 'opentrons_24_tuberack_nest_2ml_snapcap']
type_of_tube_rack = 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap'

### VERAO VAR NAME='FFPE mode (skip initial 1.6% PFA fixation)' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='Overnight incubation: enable manual pausing at the antibody incubation step?' TYPE=BOOLEAN
protocol_pause = False

"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the omnistainer device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the Eppendorf rack in pos. D1
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""

### VERAO VAR NAME='Antibody screening mode' TYPE=BOOLEAN
Antibody_Screening = False

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 12

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=900 DECIMAL=FALSE
ab_incubation_time_minutes = 480

### VERAO VAR NAME='Sample wash volume (150ul for slides/100ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody mix volume (110ul for slides/60ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='P300 pipette model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

labwarePositions = Object()

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.buffers_plate = 1

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.omnistainer = 2

### VERAO VAR NAME='Deck position: Preblock/Antibody/F reagents plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.codex_reagents_plate = 3

### VERAO VAR NAME='Deck position: 300ul tip rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.tiprack_300_1 = 6

### VERAO VAR NAME='Deck position: 300ul tip rack#2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.tiprack_300_2 = 9


# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1, 'tiprack 300ul 1')
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_2, 'tiprack 300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks = [tiprack_300_1,tiprack_300_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos-1]

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')
    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')
    CODEX_reagents_rack = protocol.load_labware(type_of_tube_rack, labwarePositions.codex_reagents_plate, '96-well-plate')

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.Hydration_PFA_1pt6pct =  buffer_wells['A1']
    buffers.Staining =  buffer_wells['A2']
    buffers.Storage_PFA_4pct = buffer_wells['A3']
    buffers.MeOH =  buffer_wells['A4']
    buffers.PBS = buffer_wells['A5']
    buffers.CODEX_buffer_1x = buffer_wells['A6']
    buffers.Screening_Buffer = buffer_wells['A7']
    buffers.Stripping_buffer = buffer_wells['A8']
    buffers.storage = buffer_wells['A9']

    preblock_well = CODEX_reagents_rack.wells()[0]
    antibody_well = CODEX_reagents_rack.wells()[1]
    reagent_F_well = CODEX_reagents_rack.wells()[2]
    rendering_well = CODEX_reagents_rack.wells()[3]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer)
    if not FFPE:
        #WASHING SAMPLES WITH PFA
        protocol.comment("puncture first fix")
        puncture_wells(pipette_300, buffers.Hydration_PFA_1pt6pct)
        protocol.comment("first fix")
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume, 1)
        #INCUBATE
        protocol.delay(minutes=10, msg = "first fix incubation")

    #WASHING SAMPLES WITH S2
    protocol.comment("puncture S2")
    puncture_wells(pipette_300, buffers.Staining)
    protocol.comment("wash in S2")
    washSamples(pipette_300, buffers.Staining, sample_chambers, wash_volume, 2)

    #PUNCTURING THE PREBLOCK
    protocol.comment("puncture the preblock")
    puncture_wells(pipette_300, preblock_well, height_offset=18)
    pipette_300.drop_tip()

    #WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    washSamples(pipette_300, preblock_well, sample_chambers, wash_volume, 1, keep_tip=True)
    pipette_300.drop_tip()
    #INCUBATE

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    protocol.delay(minutes=15, msg = "preblocking incubation")

    #APPLYING ANTIBODY COCKTAILS TO SAMPLES

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer)

    protocol.comment("applying antibodies")
    puncture_wells(pipette_300, antibody_well, height_offset=18)
    washSamples(pipette_300, antibody_well, sample_chambers, ab_volume, 1)

    #INCUBATE
    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    if protocol_pause:
        protocol.pause(msg = "The protocol is paused for primary ab incubation")
    else:
        protocol.delay(minutes=ab_incubation_time_minutes, msg = "staining incubation")

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer)
    for i in range(2):
        #WASHING SAMPLES WITH Staining buffer
        protocol.comment("first washing with Staining buffer")
        washSamples(pipette_300, buffers.Staining, sample_chambers, wash_volume,2)
        #INCUBATE
        protocol.delay(minutes=5, msg = "first incubation in Staining Buffer")


    #POST STAINING FIXING SAMPLES WITH PFA
    protocol.comment("puncture second fix")
    puncture_wells(pipette_300, buffers.Storage_PFA_4pct)
    protocol.comment("second fix")
    washSamples(pipette_300, buffers.Storage_PFA_4pct, sample_chambers, wash_volume,1)
    #INCUBATE
    protocol.delay(minutes=5, msg="incubation with fixative")

    #WASHING SAMPLES WITH PBS
    protocol.comment("puncture the PBS wash")
    puncture_wells(pipette_300, buffers.PBS)
    protocol.comment("the PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2)

    # FIXING SAMPLES WITH Methanol
    protocol.comment("puncture the Methanol")
    puncture_wells(pipette_300, buffers.MeOH)
    for i in range(2):
        protocol.comment("applying MeOH")
        washSamples(pipette_300, buffers.MeOH, sample_chambers, wash_volume,1)
        # INCUBATE
        protocol.delay(minutes=2.5, msg="First MeOH incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2)

    #PUNCTURING THE FIXATIVE
    protocol.comment("puncture the fixative")
    puncture_wells(pipette_300, reagent_F_well, height_offset=18)
    pipette_300.drop_tip()

    #DILUTING AND APPLYING THE FIXATIVE
    protocol.comment("applying the fixative")
    dilute_and_apply_fixative(pipette_300, reagent_F_well, buffers.PBS, sample_chambers[i], 150)

    protocol.comment("third fix incubation")

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    protocol.delay(minutes=10, msg = "Reagent F incubation")

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer)

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume, 2)

    if Antibody_Screening:
        protocol.comment("puncture the Stripping Buffer")
        puncture_wells(pipette_300, buffers.Stripping_buffer)
        protocol.comment("puncture the Screening Buffer")
        puncture_wells(pipette_300, buffers.Screening_Buffer)
        #PRE-CLEARING THE TISSUE
        for i in range (3):
            protocol.comment("tissue clearing round" + str(i+1))
            washSamples(pipette_300, buffers.Stripping_buffer, sample_chambers, wash_volume,2)
            protocol.delay(seconds=30)
            washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,1)
            washSamples(pipette_300, buffers.CODEX_buffer_1x, sample_chambers, wash_volume,1)

        #Equilibration in rendering buffer
        protocol.comment("Equilibration in rendering buffer")
        washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,1)

        #RENDERING
        protocol.comment("Applying rendering solution to wells")
        puncture_wells(pipette_300, rendering_well, height_offset=18)
        washSamples(pipette_300, rendering_well, sample_chambers[i], wash_volume, 1)

        #INCUBATE
        protocol.delay(minutes=10, msg = "rendering hybridization")

        #WASH SAMPLES IN 1x CODEX buffer
        protocol.comment("Washing with rendering buffer")
        washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,2)

    #STORAGE, washing samples every hour for 100 hours
    protocol.comment("puncturing the storage buffer")
    puncture_wells(pipette_300, buffers.storage)
    protocol.comment("applying the storage buffer")
    washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume,2)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)


#protocol exported from Parhelia StainWorks