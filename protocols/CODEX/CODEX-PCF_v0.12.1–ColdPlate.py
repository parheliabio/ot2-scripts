metadata = {
    'protocolName': 'Parhelia CODEX v12_ColdPlate',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX slide and coverslip staining protocol for Omni-Stainer instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath']
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
num_samples = 3

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=900 DECIMAL=FALSE
ab_incubation_time_minutes = 480

### VERAO VAR NAME='Sample wash volume (150ul for slides/100ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody mix volume (110ul for slides/60ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 110

### VERAO VAR NAME='Aspiration height offset(mm, for calibration debugging)'  TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=TRUE INCREMENT=0.1
aspiration_gap = 0

### VERAO VAR NAME='Dispensing height offset (mm, for calibration debugging)'  TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=TRUE INCREMENT=0.1
dispensing_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

### VERAO VAR NAME='Antibody staining temperature' TYPE=NUMBER LBOUND=0 UBOUND=40
antibody_staining_temp = 4

### VERAO VAR NAME='Room temperature' TYPE=NUMBER LBOUND=15 UBOUND=25
room_temp = 25

### VERAO VAR NAME='Perform MeOH fixation at 4C?' TYPE=BOOLEAN
cold_MeOH = False

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 pipette model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_buffers_plate_position = 10

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12/C12 module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 3

### VERAO VAR NAME='Deck position: Preblock/Antibody/F reagents plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_reagents_plate_position = 7

### VERAO VAR NAME='Deck position: 300ul tip rack' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='Deck position: 300ul tip rack#2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 9

labwarePositions = Object()
labwarePositions.codex_buffers_plate = codex_buffers_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.codex_reagents_plate = codex_reagents_plate_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position


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

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')
    codex_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.codex_buffers_plate,
                                           'codex_12-trough buffers reservoir')
    CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate,
                                                   '96-well-plate')

    codex_buffer_wells = codex_trough12.wells_by_name()

    codex_buffers = Object()
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
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    temp_mod = None

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)
        temp_mod.set_temp(room_temp)

    if not FFPE:
        # WASHING SAMPLES WITH PFA
        protocol.comment("puncturing first fix")
        puncture_wells(pipette_300, codex_buffers.Hydration_PFA_1pt6pct)
        protocol.comment("first fix")
        washSamples(pipette_300, codex_buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=10, msg="first fix incubation")

    # WASHING SAMPLES WITH S2
    protocol.comment("puncture S2")
    puncture_wells(pipette_300, codex_buffers.Staining)
    protocol.comment("wash in S2")
    washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)

    # PUNCTURING THE PREBLOCK
    protocol.comment("puncturing the preblock")
    for i in range(num_samples):
        puncture_wells(pipette_300, codex_preblock_wells[i], keep_tip=True)
    if pipette_300.has_tip: pipette_300.drop_tip()

    # WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    for i in range(num_samples):
        washSamples(pipette_300, codex_preblock_wells[i], sample_chambers[i], ab_volume, 1, keep_tip=True)
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
        puncture_wells(pipette_300, codex_antibody_wells[i])
        protocol.comment("applying antibodies")
        washSamples(pipette_300, codex_antibody_wells[i], sample_chambers[i], ab_volume, 1)
    # INCUBATE
    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    if not (temp_mod is None):
        temp_mod.set_temp(antibody_staining_temp)
        protocol.delay(minutes=ab_incubation_time_minutes, msg="staining incubation")
        temp_mod.set_temp(room_temp)
    else:
        if protocol_pause:
            protocol.pause(msg="The protocol is paused for primary ab incubation")
        else:
            protocol.delay(minutes=ab_incubation_time_minutes, msg="staining incubation")

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)
    for i in range(2):
        # WASHING SAMPLES WITH Staining buffer
        protocol.comment("washing with Staining buffer #" + str(i))
        washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)
        # INCUBATE
        protocol.delay(minutes=5, msg="incubation in Staining Buffer" + str(i))

    # POST STAINING FIXING SAMPLES WITH PFA
    protocol.comment("puncturing the second fix")
    puncture_wells(pipette_300, codex_buffers.Storage_PFA_4pct)
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

    if not (temp_mod is None) and cold_MeOH:
        protocol.comment("cooling down for the MeOH step")
        temp_mod.set_temp(4)
        protocol.delay(minutes=15, msg="waiting for temperature equilibration")

    protocol.comment("puncturing the Methanol")
    puncture_wells(pipette_300, codex_buffers.MeOH)

    for i in range(2):
        protocol.comment("applying MeOH")
        washSamples(pipette_300, codex_buffers.MeOH, sample_chambers, wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=2.5, msg="MeOH incubation")

    if not (temp_mod is None) and cold_MeOH:
        protocol.comment("warming up after the MeOH step")
        temp_mod.set_temp(room_temp)

    # WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)

    if not (temp_mod is None) and cold_MeOH:
        protocol.delay(minutes=10, msg="waiting for temperature equilibration")

    # PUNCTURING THE FIXATIVE
    protocol.comment("puncturing the fixative")
    for i in range(num_samples):
        puncture_wells(pipette_300, codex_reagent_F_wells[i], keep_tip=True)
    if pipette_300.has_tip: pipette_300.drop_tip()

    # DILUTING AND APPLYING THE FIXATIVE
    protocol.comment("applying the fixative")
    for i in range(num_samples):
        dilute_and_apply_fixative(pipette_300, codex_reagent_F_wells[i], codex_buffers.PBS, sample_chambers[i],
                                  ab_volume, keep_tip=True)

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
            puncture_wells(pipette_300, codex_rendering_wells[i])
            protocol.comment("Applying the rendering solution to the wells")
            washSamples(pipette_300, codex_rendering_wells[i], sample_chambers[i], wash_volume, 1)
        # INCUBATE
        protocol.delay(minutes=10, msg="rendering hybridization")

        # WASH SAMPLES IN 1x CODEX buffer
        protocol.comment("Washing with rendering buffer")
        washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 2)

    # STORAGE wash
    protocol.comment("puncturing the storage buffer")
    puncture_wells(pipette_300, codex_buffers.storage)
    protocol.comment("applying the storage buffer")
    washSamples(pipette_300, codex_buffers.storage, sample_chambers, wash_volume, 2)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    if not (temp_mod is None):
        protocol.comment("coolind down to 4 deg for storage. The protocol will pause next")
        temp_mod.set_temp(4)
        protocol.pause(
            msg="Protocol is paused for 4C storage. Hit Resume to end the protocol and turn off the ColdPlate")
        temp_mod.temp_off()