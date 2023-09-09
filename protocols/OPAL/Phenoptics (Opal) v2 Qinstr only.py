metadata = {
    'protocolName': 'Parhelia Phenoptics/Opal protocol',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Multicycle fluorescent TSA protocol compatible with Akoya Phenoptics/Opal platform',
    'apiLevel': '2.13'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'


### VERAO VAR NAME='Delayed start' TYPE=BOOLEAN
delayed_start = False

### VERAO VAR NAME='Protocol start delay time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
protocol_delay_minutes = 30

### VERAO VAR NAME='Preblock time (minutes)' TYPE=NUMBER LBOUND=1 UBOUND=90 DECIMAL=FALSE
preblock_time_minutes = 10

### VERAO VAR NAME='Primary ab hyb time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
primary_ab_time_minutes = 90

### VERAO VAR NAME='Secondary ab hyb time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
secondary_ab_time_minutes = 90

### VERAO VAR NAME='TSA time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
tsa_time_minutes = 30

### VERAO VAR NAME='ER destaining time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
hybridization_time_minutes = 15

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=200 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=200 DECIMAL=FALSE
ab_volume = 200

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.1

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
num_samples = 2

### VERAO VAR NAME='Number of Antibodies' TYPE=NUMBER LBOUND=1 UBOUND=6 DECIMAL=FALSE
num_abs = 6

### VERAO VAR NAME='Temp lag for adjusting the temp' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALS
templag = 10

### VERAO VAR NAME='ER temperature' TYPE=NUMBER LBOUND=1 UBOUND=99 DECIMAL=FALSE
er_temp = 99

### VERAO VAR NAME='ER/Antibody stripping time' TYPE=NUMBER LBOUND=1 UBOUND=99 DECIMAL=FALSE
er_time = 40

### VERAO VAR NAME='Antibody stripping time' TYPE=NUMBER LBOUND=1 UBOUND=99 DECIMAL=FALSE
er_time = 40

### VERAO VAR NAME='Room temperature' TYPE=NUMBER LBOUND=15 UBOUND=25 DECIMAL=FALSE
room_temp = 22

### VERAO VAR NAME='Storage Mode after staining' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
storage_temp = 4

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer / Thermosheath / ColdPlate' TYPE=NUMBER LBOUND=1 UBOUND=9 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='labwarePositions.wash_buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
wash_buffers_plate_position = 7

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_1 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_1_position = 6

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_2 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_2_position = 8

### VERAO VAR NAME='labwarePositions.rna_reagents_plate_3 ' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_reagents_plate_3_position = 9

### VERAO VAR NAME='labwarePositions.tiprack_300_1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 10

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_2_position = 11

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Tip type' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type = 'opentrons_96_tiprack_300ul'

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN2'

if pipette_300_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

labwarePositions = Object()
labwarePositions.wash_buffers_plate = wash_buffers_plate_position
labwarePositions.ab_reagents_plate_1 = ab_reagents_plate_1_position
labwarePositions.ab_reagents_plate_2 = ab_reagents_plate_2_position
labwarePositions.ab_reagents_plate_3 = ab_reagents_plate_3_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position
labwarePositions.omnistainer = omnistainer_position

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5

#####################CUSTOM LABWARE_DEFINITION###################

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_1 = protocol.load_labware(tip_type, labwarePositions.tiprack_300_1,
                                          'tiprack 200/300ul 1')
    tiprack_2 = protocol.load_labware(tip_type, labwarePositions.tiprack_300_2,
                                          'tiprack 200/300ul 2')

    pipette_300 = protocol.load_instrument(pipette_type, pipette_300_location, tip_racks=[tiprack_1, tiprack_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos - 1]

    # Setting up ColdPlate temperature module and omni-stainer module
    if "coldplate" in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)
        omnistainer = protocol.load_labware(
            omnistainer_type, labwarePositions.omnistainer, "Omni-stainer"
        )
    else:
        temp_mod = protocol.load_module("temperature module", labwarePositions.omnistainer)
        omnistainer = temp_mod.load_labware(omnistainer_type)

    buffers_trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.wash_buffers_plate, '12-trough buffers reservoir')
    buffer_wells = buffers_trough12.wells_by_name()

    buffers = Object()
    buffers.retrieval =  buffer_wells['A1']
    buffers.TBS_wash =  buffer_wells['A2']
    buffers.water =  buffer_wells['A3']
    buffers.blocking = buffer_wells['A4']
    buffers.amplification = buffer_wells['A5']

    puncture_wells(pipette_300, list(buffers.vars().values()), keep_tip=True)

    Ab_reagents_96plate_1 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_1,
                                                  '96-well-plate')
    Ab_reagents_96plate_2 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_2,
                                                  '96-well-plate')
    Ab_reagents_96plate_3 = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_reagents_plate_3,
                                                  '96-well-plate')

    all_reag_rows = Ab_reagents_96plate_1.rows() + Ab_reagents_96plate_2.rows() + Ab_reagents_96plate_3.rows()

    if 'thermosheath' in omnistainer_type:
        if labwarePositions.omnistainer > 9:
            raise Exception(
                "Omni-Stainer module with current thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")
        # Remove Exception for new Thermal Sheath Shutters

    protocol.home()

    if delayed_start:
        closeShutter(protocol, pipette_300, omnistainer)
        protocol.delay(minutes=protocol_delay_minutes, msg="Delaying the start by " + str(start_delay_min) + " minutes")

    for i in range(num_abs):

        antibody_wells = all_reag_rows[i * 4]
        opal_polymer_wells = all_reag_rows[i * 4 + 1]
        opal_fluorophore_wells = all_reag_rows[i * 4  + 2]

        puncture_wells(pipette_300, antibody_wells, keep_tip=True)
        puncture_wells(pipette_300, opal_polymer_wells, keep_tip=True)
        puncture_wells(pipette_300, opal_fluorophore_wells, keep_tip=True)

        #ER/Stripping
        washSamples(pipette, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)
        protocol.delay(minutes=1, msg="Incubating in water")

        washSamples(pipette, buffers.retrieval, sample_chambers, wash_volume, 2, keep_tip=True)

        closeShutter(protocol, pipette, omnistainer)

        temp_mod.set_temperature(retrieval_temp)

        protocol.delay(minutes=templag, msg="Equilibrating")

        protocol.delay(minutes=retrieval_time, msg="ER in progress")
        temp_mod.set_temp(room_temp)

        prevTemp = temp_mod.temperature
        while (temp_mod.get_temp() > pbs_wash_temp + 1):
            currTemp = temp_mod.temperature
            protocol.delay(seconds=60, msg="cooling down, temp: " + str(currTemp))
            if (prevTemp - currTemp > 10):
                openShutter(protocol, pipette, omnistainer)
                distribute_between_samples(pipette, buffers.retrieval, sample_chambers, 50, 1, keep_tip=True)
                closeShutter(protocol, pipette, omnistainer)
                prevTemp = currTemp

        protocol.delay(minutes=templag, msg="Equilibrating")
        openShutter(protocol, pipette, omnistainer)

        # WASHING SAMPLES WITH TBS
        protocol.comment("washing in TBS")
        washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
        #    protocol.delay(minutes=5)

        protocol.comment("preblocking")
        washSamples(pipette_300,  buffers.blocking, sample_chambers, ab_volume)
        # INCUBATE
        safe_delay(minutes=preblock_time_minutes, msg = "preblocking incubation: " + str(preblock_time_minutes)  +" min")

        # APPLYING ANTIBODY COCKTAILS TO SAMPLES
        protocol.comment("applying primary antibodies")
        for i in range(len(wellslist)):
            washSamples(pipette_300, antibody_wells[i], sample_chambers[i], wash_volume)

        # INCUBATE
        safe_delay(minutes=primary_ab_time_minutes, msg = "primary antibody incubation: " + str(primary_ab_time_minutes)  +" min")

        # WASHING SAMPLES WITH TBS
        # three individual repeats below is because they need particular incubation time between them
        print("washing with TBS")
        for i in range(3):
            washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
            safe_delay(minutes=3, msg = "TBS wash incubation")

        # APPLYING OPAL polymer HRP
        print("applying opal secondary")
        for i in range(len(wellslist)):
            washSamples(pipette_300, opal_polymer_wells[i], sample_chambers[i], ab_volume)

        # INCUBATE
        safe_delay(minutes=secondary_ab_time_minutes, msg = "Opal secondary incubation for " +  str(secondary_ab_time_minutes)+  " min")

        # WASHING SAMPLES WITH TBS
        protocol.comment("washing with TBS")
        for i in range(3):
            washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
            safe_delay(minutes=3, msg = "TBS wash incubation")

        # Opal Signal generation
        protocol.comment("Applying the Opal TSA reagent")
        for i in range(num_samples):
            dilute_and_apply_fixative(pipette_300, opal_fluorophore_wells[i], buffers.amplification, sample_chambers[i], ab_volume)

        # INCUBATE
        safe_delay(minutes=tsa_time_minutes, msg = "Opal TSA incubation for " +  str(tsa_time_minutes)+  " min")

        # WASHING SAMPLES WITH TBS
        # three individual repeats below is because they need particular incubation time between them
        print("washing with TBS")
        for i in range(3):
            washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
            protocol.delay(minutes=3)


    ### ANTI-TAG STAINING
    anti_tsa_wells = all_reag_rows[-2]
    protocol.comment("puncturing anti-TSA wells")
    puncture_wells(pipette_300, anti_tsa_wells, keep_tip=True)
    pipette_300.transfer(ab_volume, anti_tsa_wells, sample_chambers, new_tip='once', disposal_vol=0)
    safe_delay(protocol, minutes=4, msg="incubation in anti-TSA fluorescent antibody")

    ### DAPI STAINING
    DAPI_wells = all_reag_rows[-1]
    protocol.comment("puncturing DAPI wells")
    puncture_wells(pipette_300, DAPI_wells, keep_tip=True)
    #Washing with DAPI
    pipette_300.transfer(ab_volume, DAPI_wells, sample_chambers, new_tip='once', disposal_vol = 0)
    safe_delay(protocol, minutes=4, msg="incubation in DAPI")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)

    closeShutter(protocol, pipette_300, omnistainer)
    
    # Storage
    if storage_mode:
        temp_mod.set_temperature(storage_temp)
        protocol.pause(f"Holding at storage temp: {storage_temp} C. Press Resume to reduce")
    
    temp_mod.temp_off()
    protocol.comment(f"Protocol done - temperature module has been turned off")

#protocol exported from Parhelia StainWorks

#protocol exported from Parhelia StainWorks
#protocol exported from Parhelia StainWorks