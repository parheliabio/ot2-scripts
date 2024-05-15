### VERAO GLOBAL
from global_functions import *
### END VERAO GLOBAL

metadata = {
    'protocolName': 'Akoya PCF-CODEX v13 with Temperature Control',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': '20m Fixative incubation, RT MeOH, 3x PBS wash after MeOH',
    'apiLevel': '2.14'
}

########################MODIFIABLE RUN PARAMETERS#######################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='Delayed start' TYPE=BOOLEAN
delayed_start = False

### VERAO VAR NAME='Do 1.6% PFA fixation? (standard for FF)' TYPE=BOOLEAN
pre_fix = False

### VERAO VAR NAME='Protocol start delay time (minutes)' TYPE=NUMBER LBOUND=15 UBOUND=8000 DECIMAL=FALSE
protocol_delay_minutes = 30

### VERAO VAR NAME='Overnight incubation: enable manual pausing at the antibody incubation step?' TYPE=BOOLEAN
protocol_pause = False

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='D3'
num_samples = 5

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=2000 DECIMAL=FALSE
ab_incubation_time_minutes = 600

### VERAO VAR NAME='Do preblock?' TYPE=BOOLEAN
preblock = False

### VERAO VAR NAME='Preblock incubation time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=60 DECIMAL=FALSE
preblock_incubation_time_minutes = 15

### VERAO VAR NAME='Antibody incubation temperature' TYPE=NUMBER LBOUND=0 UBOUND=40
antibody_staining_temp = 8

### VERAO VAR NAME='Room temperature' TYPE=NUMBER LBOUND=15 UBOUND=25
room_temp = 22

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=2 UBOUND=25
storage_temp = 4

"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the omnistainer device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the 96-well plate
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""

### VERAO VAR NAME='Antibody screening mode (involves additional fluorescent detection probes)' TYPE=BOOLEAN EXCEL_POSITION='D5'
Antibody_Screening = True

### VERAO VAR NAME='Perform ONLY Antibody screening mode? Only used if working with previouslly stained samples' TYPE=BOOLEAN 
Ab_Screening_Only = False

### VERAO VAR NAME='Reporter incubation time (minutes) (for screening mode only)' TYPE=NUMBER LBOUND=1 UBOUND=300 DECIMAL=FALSE
probe_incubation_time_minutes = 15

### VERAO VAR NAME='Sample wash volume (150ul for slides/100ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE EXCEL_POSITION='D7'
wash_volume = 150

### VERAO VAR NAME='Antibody mix volume (120ul for slides/60ul for coverslips)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE EXCEL_POSITION='D6'
ab_volume = 110

### VERAO VAR NAME='Aspiration height offset(mm, for calibration debugging)'  TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=TRUE INCREMENT=0.1
aspiration_gap = 0

### VERAO VAR NAME='Dispensing height offset (mm, for calibration debugging)'  TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=TRUE INCREMENT=0.1
dispensing_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.4

### not exposing this one due to the lack of validation and potential problems with the fixation consistency
cold_MeOH = False

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_buffers_plate_position = 8

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12/C12 module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='Deck position: Preblock/Antibody/F reagents plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
codex_reagents_plate_position = 3

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='Tip type for tiprack 1' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type_tiprack1 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 9

### VERAO VAR NAME='Tip type for tiprack 2' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type_tiprack2 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='Test mode (all delays reduced to 30s)' TYPE=BOOLEAN
testmode = False

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

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

    # Tip racks and pipette
    tiprack_1 = protocol.load_labware(tip_type_tiprack1, labwarePositions.tiprack_300_1, 'tiprack 200/300ul 1')
    tiprack_2 = protocol.load_labware(tip_type_tiprack2, labwarePositions.tiprack_300_2, 'tiprack 200/300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_1, tiprack_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos - 1]

    # Staining Module
    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    # Reagents
    codex_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.codex_buffers_plate, 'codex_12-trough buffers reservoir')
    CODEX_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.codex_reagents_plate, '96-well-plate')

    codex_buffer_wells = codex_trough12.wells_by_name()

    codex_buffers = Object()
    codex_buffers.Hydration_PFA_1pt6pct = codex_buffer_wells['A1']
    codex_buffers.Staining = codex_buffer_wells['A2']
    codex_buffers.Storage_PFA_1pt6pct = codex_buffer_wells['A3']
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
    protocol.comment("Starting the Akoya PCF staining protocol for samples:" + str(sample_chambers))
    protocol.home()

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "The temperature module cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        openShutter(protocol, pipette_300, omnistainer, keep_tip=True)

    temp_mod = None

    if delayed_start:
        closeShutter(protocol, pipette_300, omnistainer)
        safe_delay(protocol, minutes=protocol_delay_minutes, msg = "Delaying the start by " + str(protocol_delay_minutes) + " minutes" )

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)
        temp_mod.quick_temp(room_temp)

    if pre_fix:
        protocol.comment("puncturing first fix")
        puncture_wells(pipette_300, codex_buffers.Hydration_PFA_1pt6pct)
        protocol.comment("initial 1.6% PFA fix")
        washSamples(pipette_300, codex_buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume, 1)
    
    # INCUBATE
    safe_delay(protocol, minutes=10, msg="first fix incubation")

    if not Ab_Screening_Only:
        # WASHING SAMPLES WITH Staining Buffer
        protocol.comment("puncture Staining Buffer")
        puncture_wells(pipette_300, codex_buffers.Staining)
        protocol.comment("wash in Staining Buffer")
        washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)

        if preblock:
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

            safe_delay(protocol, minutes=preblock_incubation_time_minutes, msg="preblocking incubation")

        # APPLYING ANTIBODY COCKTAILS TO SAMPLES

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer)

        protocol.comment("applying antibody cocktail(s)")
        
        for i in range(num_samples):
            protocol.comment("puncturing antibodies")
            puncture_wells(pipette_300, codex_antibody_wells[i])
            protocol.comment("applying antibodies")
            washSamples(pipette_300, codex_antibody_wells[i], sample_chambers[i], ab_volume, 1)
            
        # INCUBATE
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer)

        if not (temp_mod is None):
            temp_mod.quick_temp(antibody_staining_temp)
            
        if protocol_pause:
            protocol.pause(msg="The protocol is paused for primary ab incubation")
        else:
            safe_delay(protocol, minutes=ab_incubation_time_minutes, msg=f"staining incubation for {ab_incubation_time_minutes} minutes ")

        if not (temp_mod is None):
            temp_mod.quick_temp(room_temp)
        

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer)

            
        for i in range(2):
            # WASHING SAMPLES WITH Staining buffer
            protocol.comment("washing with Staining buffer #" + str(i))
            washSamples(pipette_300, codex_buffers.Staining, sample_chambers, wash_volume, 2, keep_tip=True)
            # INCUBATE
            safe_delay(protocol, minutes=5, msg="incubation in Staining Buffer" + str(i))

            
        # POST STAINING FIXING SAMPLES WITH PFA
        protocol.comment("puncturing the second fix")
        puncture_wells(pipette_300, codex_buffers.Storage_PFA_1pt6pct)
        protocol.comment("second fix")
        washSamples(pipette_300, codex_buffers.Storage_PFA_1pt6pct, sample_chambers, wash_volume, 2)
        # INCUBATE
        safe_delay(protocol, minutes=10, msg="10 min incubation with Post-Staining Fixation Solution")
        

        # WASHING SAMPLES WITH PBS
        protocol.comment("puncture the PBS wash")
        puncture_wells(pipette_300, codex_buffers.PBS)
        protocol.comment("3x PBS wash")
        for i in range(3):
            washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 1)
            safe_delay(protocol, minutes=1, msg = "PBS wash #" + str(i+1))

        # FIXING SAMPLES WITH Methanol

        protocol.comment("puncturing the Methanol")
        puncture_wells(pipette_300, codex_buffers.MeOH)

        for i in range(2):
            protocol.comment("applying MeOH")
            washSamples(pipette_300, codex_buffers.MeOH, sample_chambers, wash_volume, 1)
            # INCUBATE
            safe_delay(protocol, minutes=2.5, msg="MeOH incubation")

        # WASHING SAMPLES WITH PBS
        for i in range(3):
            washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 1, keep_tip=True)
            safe_delay(protocol, minutes=1, msg = "PBS wash #" + str(i+1))

        # PUNCTURING THE FIXATIVE
        protocol.comment("puncturing the fixative")
        for i in range(num_samples):
            puncture_wells(pipette_300, codex_reagent_F_wells[i], keep_tip=True)
        if pipette_300.has_tip: pipette_300.drop_tip()

        # DILUTING AND APPLYING THE FIXATIVE
        protocol.comment("applying the fixative")
        for i in range(num_samples):
            dilute_and_apply_fixative(pipette_300, codex_reagent_F_wells[i], codex_buffers.PBS, sample_chambers[i], wash_volume, keep_tip=True)

        protocol.comment("Post-Staining Fixing Solution incubation")

        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette_300, omnistainer, keep_tip=True)

        safe_delay(protocol, minutes=20, msg="Post-Staining Fixing Solution incubation")

        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette_300, omnistainer)

        # WASHING SAMPLES WITH PBS
        protocol.comment("PBS wash")
        washSamples(pipette_300, codex_buffers.PBS, sample_chambers, wash_volume, 2)

    if Antibody_Screening:
        protocol.comment("puncture the PCF Buffer")
        puncture_wells(pipette_300, codex_buffers.CODEX_buffer_1x, keep_tip=True)
        protocol.comment("puncture the Screening Buffer")
        puncture_wells(pipette_300, codex_buffers.Screening_Buffer, keep_tip=True)
        protocol.comment("puncture the Stripping Buffer")
        puncture_wells(pipette_300, codex_buffers.Stripping_buffer)
        # PRE-CLEARING THE TISSUE
        
        for i in range(3):
            protocol.comment("tissue clearing round" + str(i + 1))
            washSamples(pipette_300, codex_buffers.Stripping_buffer, sample_chambers, wash_volume, 2)
            safe_delay(protocol, seconds=30)
            washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 1)
            washSamples(pipette_300, codex_buffers.CODEX_buffer_1x, sample_chambers, wash_volume, 1)

        # Equilibration in Screening buffer
        protocol.comment("Equilibration in Screening buffer")
        washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 1)

        # Detector/Probe Application, AKA RENDERING
        protocol.comment("Applying Screening solution to wells")
        for i in range(num_samples):
            protocol.comment("puncturing the Screening solution")
            puncture_wells(pipette_300, codex_rendering_wells[i])
            protocol.comment("Applying the Screening solution to the wells")
            washSamples(pipette_300, codex_rendering_wells[i], sample_chambers[i], wash_volume, 1)
        # INCUBATE
        safe_delay(protocol, minutes=probe_incubation_time_minutes,
                       msg=f"Detector Mix (Probe) hybridization {probe_incubation_time_minutes} minutes ")

        # WASH SAMPLES IN 1x CODEX buffer
        protocol.comment("Washing with screening buffer")
        washSamples(pipette_300, codex_buffers.Screening_Buffer, sample_chambers, wash_volume, 2)

    # STORAGE wash
    protocol.comment("puncturing the storage buffer")
    puncture_wells(pipette_300, codex_buffers.storage)
    protocol.comment("applying the storage buffer")
    washSamples(pipette_300, codex_buffers.storage, sample_chambers, wash_volume, 2)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette_300, omnistainer)

    if not (temp_mod is None):
        protocol.comment(f"cooling down to {storage_temp} deg for storage. The protocol will pause next")
        temp_mod.set_temp(storage_temp)
        protocol.pause(
            msg=f"Protocol is paused for {storage_temp} C storage. "
                f"Hit Resume to end the protocol and turn off the thermal module")
        temp_mod.temp_off()



