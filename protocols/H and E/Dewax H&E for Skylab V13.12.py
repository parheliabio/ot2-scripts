
metadata = {
    'protocolName': 'Parhelia Dewax + H&E v13.12, extra opens, baking, Skylab Kit or 12 trough Full H&E',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia Dewax + H&E using Skylab H&E Kits: Dewax,100% EtOH, 70% EtOH, Water, Hematoxylin, Blueing Reagent, Eosin, Water 2',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides', 'omni_stainer_s12_slides_with_thermosheath', 'omni_stainer_s12_slides_with_thermosheath_on_coldplate', 'omni_stainer_c12_cslps', 'omni_stainer_c12_cslps_with_thermosheath']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Reagent well plate type' TYPE=CHOICE OPTIONS=['parhelia_12trough','parhelia_skirted_96_with_strips','nest_96_wellplate_2ml_deep','parhelia_skirted_96']
plate_type = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='D2'
num_samples = 2

### VERAO VAR NAME='Doing Bake on Omni-Stainer?' TYPE=BOOLEAN
baking = False

### VERAO VAR NAME='Baking time (minutes)' TYPE=NUMBER LBOUND=10 UBOUND=180 DECIMAL=FALSE
baking_time = 10

### VERAO VAR NAME='Baking temperature (C)' TYPE=NUMBER LBOUND=50 UBOUND=70 DECIMAL=FALSE
baking_temp = 65

### VERAO VAR NAME='Do dewaxing' TYPE=BOOLEAN EXCEL_POSITION='D3'
do_dewax = True

### VERAO VAR NAME='Dewaxing temp' TYPE=NUMBER LBOUND=60 UBOUND=80 DECIMAL=FALSE
dewax_temp = 72

### VERAO VAR NAME='Alcohol wash temp' TYPE=NUMBER LBOUND=20 UBOUND=60 DECIMAL=FALSE
alc_temp = 50

### VERAO VAR NAME='Room temp' TYPE=NUMBER LBOUND=15 UBOUND=25 DECIMAL=FALSE
room_temp = 22

### VERAO VAR NAME='Do rehydration' TYPE=BOOLEAN EXCEL_POSITION='D4'
do_rehydration = True

### VERAO VAR NAME='Do clairfying' TYPE=BOOLEAN EXCEL_POSITION='D5'
do_clarifying = False

### VERAO VAR NAME='Wash buffer volume (uL)' TYPE=NUMBER LBOUND=25 UBOUND=300 DECIMAL=FALSE EXCEL_POSITION='D6'
wash_volume = 150

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Sample flow rate: set to 0.2 for slides, 0.07 for cslps' TYPE=NUMBER LBOUND=0.01 UBOUND=1 DECIMAL=TRUE INCREMENT=0.01
sample_flow_rate = 0.2

### VERAO VAR NAME='Hematoxylin incubation time' TYPE=NUMBER LBOUND=1 UBOUND=5 DECIMAL=TRUE
hematox_delay = 2.5

### VERAO VAR NAME='post-Hematoxylin differentiation in water time (min)' TYPE=NUMBER LBOUND=0 UBOUND=5 DECIMAL=TRUE
hx_diff_time = 1

### VERAO VAR NAME='Eosin incubation time' TYPE=NUMBER LBOUND=1 UBOUND=5 DECIMAL=TRUE
eosin_delay = 1.75

### VERAO VAR NAME='Dehydrate (end in 100% EtOH)' TYPE=BOOLEAN
dehydrate = True

### VERAO VAR NAME='Pause before last water step' TYPE=BOOLEAN
pause_before_water = False

### VERAO VAR NAME='New tip for each sample/stain?' TYPE=BOOLEAN
new_tip = True

### VERAO VAR NAME='Water differentiation time' TYPE=NUMBER LBOUND=0 UBOUND=10 DECIMAL=TRUE
water_diff_time = 3

####################LABWARE LAYOUT ON DECK#########################

### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_GEN = 'GEN2'

### VERAO VAR NAME='Tip type' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul','opentrons_96_filtertiprack_200ul']
tip_type_tiprack_1 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='DECK POSITION: Staining Module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='DECK POSITION: H&E Reagent plate (12-trough or strip tubes in 96-holder)' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
h_e_source = 3

### VERAO VAR NAME='DECK POSITION:Tiprack 1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 6

### VERAO VAR NAME='Double add of antibody/reagents (uses 2x volume, but improves uniformity)' TYPE=BOOLEAN
double_add = False

### VERAO VAR NAME='Test mode (all delays skipped)' TYPE=BOOLEAN
testmode = False

### VERAO VAR NAME='Storage mode?' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=1 UBOUND=40 DECIMAL=TRUE INCREMENT=0.1
storage_temp = 4

labwarePositions = Object()
labwarePositions.omnistainer = omnistainer_position
labwarePositions.h_e_plate = h_e_source
labwarePositions.tiprack_300_1 = tiprack_300_1_position

def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################
    # Tiprack
    tiprack_1 = protocol.load_labware(tip_type_tiprack_1, labwarePositions.tiprack_300_1,
                                      'tiprack 200/300ul 1')
    # tiprack_2 = protocol.load_labware(tip_type_tiprack_2, labwarePositions.tiprack_300_2,'tiprack 200/300ul 2')
    # Pipette
    if pipette_GEN == 'GEN2':
        pipette_type = 'p300_single_gen2'
    else:
        pipette_type = 'p300_single'
    # pipette_type = 'p300_single_gen2'
    # pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_1, tiprack_2])
    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_1])
    pipette.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos - 1]
    # Staining Module
    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')
    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    h_e_plate = protocol.load_labware(plate_type, labwarePositions.h_e_plate, 'H&E reagent plate')

    wells = h_e_plate.wells_by_name()

    if "12trough" in plate_type:
        Dewax = wells['A1']
        EtOH_100 = wells['A2']
        EtOH_70 = wells['A4']
        Water = wells['A5']
        Water_2 = wells['A5']
        Hematoxylin = wells['A6']
        Blueing_reagent = wells['A7']
        Eosin = wells['A11']
        # 'Dewax': wells['A1'],
        # '100% EtOH': wells['A2'],
        # '95% EtOH': wells['A3'],
        # '70% EtOH': wells['A4'],
        # 'Water': wells['A5'],
        # 'Hematoxylin': wells['A6'],
        # 'Blueing reagent': wells['A7'],
        # 'Clarifying agent': wells['A8'],
        # 'Eosin': wells['A11']
    else:
        # Reagent Plate
        Dewax = h_e_plate.rows()[0][:num_samples]
        EtOH_100 = h_e_plate.rows()[1][:num_samples]
        EtOH_70 = h_e_plate.rows()[2][:num_samples]
        Water = h_e_plate.rows()[3][:num_samples]
        Hematoxylin = h_e_plate.rows()[4][:num_samples]
        Blueing_reagent = h_e_plate.rows()[5][:num_samples]
        Eosin = h_e_plate.rows()[6][:num_samples]
        Water_2 = h_e_plate.rows()[7][:num_samples]

    if double_add:
        num_reps = 2
    else:
        num_reps = 1

    single_rep = 1

    #################PROTOCOL####################
    protocol.comment("Starting the " + metadata["protocolName"] + " for samples:" + str(sample_chambers))

    protocol.home()

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        openShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)

    temp_mod = None

    # if delayed_start:
    #     if 'thermosheath' in omnistainer_type:
    #         closeShutter(protocol, pipette, omnistainer)
    #     protocol.delay(minutes=protocol_delay_minutes,
    #                    msg="Delaying the start by " + str(protocol_delay_minutes) + " minutes")

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol, 0)
        temp_mod.set_temp(room_temp)

    tip_change_policy = 'always' if new_tip else 'once'
    if baking:
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
        protocol.home()
        temp_mod.quick_temp(baking_temp)
        protocol.comment("baking at: " + str(baking_temp))
        safe_delay(protocol, minutes=baking_time, msg="Baking")

    if do_dewax:
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
        temp_mod.quick_temp(dewax_temp)
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette, omnistainer, use_tip=True)
            openShutter(protocol, pipette, omnistainer, use_tip=False)
        # dewax dispense set
        pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate * 0.3
        apply_and_incubate(protocol, pipette, Dewax, "Parhelia Dewax", sample_chambers, wash_volume,
                           1, 0, dispense_repeats=num_reps, new_tip=tip_change_policy)
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
        safe_delay(protocol, minutes=9)
        if 'thermosheath' in omnistainer_type:
            openShutter(protocol, pipette, omnistainer, use_tip=True)
            openShutter(protocol, pipette, omnistainer, use_tip=False)
        apply_and_incubate(protocol, pipette, Dewax, "Parhelia Dewax", sample_chambers, wash_volume,
                           1, 0, dispense_repeats=num_reps, new_tip=tip_change_policy, puncture=False)
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
        safe_delay(protocol, minutes=9)

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette, omnistainer, use_tip=True)
        openShutter(protocol, pipette, omnistainer, use_tip=False)
    temp_mod.quick_temp(alc_temp)
    #alc dispense set
    pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate * 0.7
    # speed is now 0.7
    apply_and_incubate(protocol, pipette, EtOH_100, "100% EtOH", sample_chambers,
                       wash_volume, single_rep, 3, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    apply_and_incubate(protocol, pipette, EtOH_70, "70% EtOH", sample_chambers,
                       wash_volume, 2, 3, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    temp_mod.quick_temp(room_temp)
    #water dispense set
    pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate * 1.0
    apply_and_incubate(protocol, pipette, Water, "Water", sample_chambers,
                       wash_volume, single_rep, 0, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    apply_and_incubate(protocol, pipette, Hematoxylin, "Hematoxylin", sample_chambers,
                       wash_volume, 2, hematox_delay, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    apply_and_incubate(protocol, pipette, Water, "Water", sample_chambers,
                       wash_volume, single_rep, hx_diff_time, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    apply_and_incubate(protocol, pipette, Blueing_reagent, "Blueing Reagent", sample_chambers,
                       wash_volume, single_rep, 2, dispense_repeats=num_reps*2,
                       new_tip=tip_change_policy)
    apply_and_incubate(protocol, pipette, Water_2, "Water 2", sample_chambers,
                       wash_volume, single_rep, 0, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    #eosin dispense set
    pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate * 0.7
    # speed is now 0.7
    apply_and_incubate(protocol, pipette, Eosin, "Eosin", sample_chambers,
                       wash_volume, 2, eosin_delay, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    apply_and_incubate(protocol, pipette, EtOH_100, "100% EtOH", sample_chambers,
                       wash_volume, single_rep, 3, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)
    # water dispense set
    pipette.flow_rate.dispense = default_flow_rate * sample_flow_rate * 1.0

    apply_and_incubate(protocol, pipette, Water_2, "Water 2", sample_chambers,
                       wash_volume, single_rep, water_diff_time, dispense_repeats=num_reps,
                       new_tip=tip_change_policy)

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette, omnistainer)

    if storage_mode:
        protocol.comment(f"cooling down to {storage_temp} deg for storage. The protocol will pause next")
        temp_mod.set_temp(storage_temp)
        protocol.pause(
            msg=f"Protocol is paused for {storage_temp} C storage. "
                f"Hit Resume to end the protocol and turn off the thermal module")

    if 'coldplate' in omnistainer_type:
        temp_mod.temp_off()
        protocol.comment(f"Protocol done - temperature module has been turned off")
    else:
        protocol.comment(f"Protocol done")

    protocol.home()

# Last modified September 16th, 2024, by Nels Wedin
# All rights reserved Parhelia Biosciences Corporation, (C) 2024-2025