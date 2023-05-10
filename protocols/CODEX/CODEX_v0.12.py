metadata = {
    'protocolName': 'Parhelia CODEX v11',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX slide and coverslip staining protocol for Omni-Stainer instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath', 'par2s_9slides_blue_v3', 'PAR2c_12coverslips']
omnistainer_type = 'omni_stainer_s12_slides'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips', 'parhelia_black_96']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='FFPE mode (skip initial 1.6% PFA fixation)' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='Overnight incubation: enable manual pausing at the antibody incubation step?' TYPE=BOOLEAN
protocol_pause = False

"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the omnistainer device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the 96-well plate
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""

### VERAO VAR NAME='Antibody screening mode' TYPE=BOOLEAN
Antibody_Screening = False

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 12



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

### VERAO VAR NAME='Deck position: 300ul Tip rack #1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.tiprack_300_1 = 6

### VERAO VAR NAME='Deck position: 300ul Tip rack#2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
labwarePositions.tiprack_300_2 = 9

### VERAO VAR NAME='Tip rack #1 starting tip position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1


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
    CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate, '96-well-plate')

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

    preblock_wells = CODEX_reagents_96plate.rows()[0]
    antibody_wells = CODEX_reagents_96plate.rows()[1]
    reagent_F_wells = CODEX_reagents_96plate.rows()[2]
    rendering_wells = CODEX_reagents_96plate.rows()[3]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer)
    if not FFPE:
        #WASHING SAMPLES WITH PFA
        protocol.comment("puncturing first fix")
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
    protocol.comment("puncturing the preblock")
    puncture_wells(pipette_300, preblock_wells, height_offset=18)
    pipette_300.drop_tip()

    #WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    for i in range (num_samples):
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], wash_volume, 1, keep_tip=True)
    pipette_300.drop_tip()
    #INCUBATE

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    protocol.delay(minutes=15, msg = "preblocking incubation")

    #APPLYING ANTIBODY COCKTAILS TO SAMPLES

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer)

    protocol.comment("applying antibodies")
    for i in range (num_samples):
        protocol.comment("puncturing antibodies")
        puncture_wells(pipette_300, antibody_wells, height_offset=18)
        protocol.comment("applying antibodies")
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume,1)
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
    protocol.comment("puncturing the second fix")
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
    protocol.comment("puncturing the Methanol")
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
    protocol.comment("puncturing the fixative")
    puncture_wells(pipette_300, reagent_F_wells, height_offset=18)
    pipette_300.drop_tip()

    #DILUTING AND APPLYING THE FIXATIVE
    protocol.comment("applying the fixative")
    for i in range (num_samples):
        dilute_and_apply_fixative(pipette_300, reagent_F_wells[i], buffers.PBS, sample_chambers[i], ab_volume)

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
        for i in range (num_samples):
            protocol.comment("puncturing the rendering solution")
            puncture_wells(pipette_300, rendering_wells[i], height_offset=18)
            protocol.comment("Applying the rendering solution to the wells")
            washSamples(pipette_300, rendering_wells[i], sample_chambers[i], wash_volume,1)
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