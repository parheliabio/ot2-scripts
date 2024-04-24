metadata = {
    'protocolName': 'Dewax/HIER + NaveniFlexTissue for Canopy v2',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'A fully automated Parhelia protocol doing Dewax/HIER followed by NaveniFlexTissue',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate','omni_stainer_c12_cslps_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='D4'
num_samples = 2

### VERAO VAR NAME='Baking' TYPE=BOOLEAN
baking = False

### VERAO VAR NAME='Baking time (minutes)' TYPE=NUMBER LBOUND=10 UBOUND=180 DECIMAL=FALSE
baking_time = 30

### VERAO VAR NAME='Baking temperature (C)' TYPE=NUMBER LBOUND=50 UBOUND=70 DECIMAL=FALSE
baking_temp = 65

### VERAO VAR NAME='Dewax?' TYPE=BOOLEAN EXCEL_POSITION='D2'
dewax = False

### VERAO VAR NAME='Antigen retrieval?' TYPE=BOOLEAN EXCEL_POSITION='D3'
agr = False

### VERAO VAR NAME='Do Navinci protocol after HIER?' TYPE=BOOLEAN
do_navinci = True

### VERAO VAR NAME='Dewaxing temperature (C)' TYPE=NUMBER LBOUND=60 UBOUND=80 DECIMAL=FALSE
dewax_temp = 72

### VERAO VAR NAME='Dewax fill slowdown factor' TYPE=NUMBER LBOUND=1 UBOUND=20 DECIMAL=FALSE
dispense_slowdown_factor = 3

### VERAO VAR NAME='Antigen Retrieval Buffer' TYPE=CHOICE OPTIONS=['ER1','ER2'] EXCEL_POSITION='D6'
ER_buffer = 'ER2'

### VERAO VAR NAME='Retrival Temperature (C)' TYPE=NUMBER LBOUND=60 UBOUND=99 DECIMAL=FALSE
retrieval_temp = 98

### VERAO VAR NAME='Retrival Time (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
retrieval_time = 40

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

### VERAO VAR NAME='Double add?' TYPE=BOOLEAN EXCEL_POSITION='D4'
double_add = True

### VERAO VAR NAME='Number of washes post Navenibodies' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
num_washes_post_NAB = 5

### VERAO VAR NAME='Wash incubation time' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
wash_incubation_time = 2

### VERAO VAR NAME='Room temp' TYPE=NUMBER LBOUND=15 UBOUND=25 DECIMAL=FALSE
room_temp = 20

### VERAO VAR NAME='Amplification temp' TYPE=NUMBER LBOUND=20 UBOUND=40 DECIMAL=FALSE
amp_temp = 30

### VERAO VAR NAME='Incubation temp' TYPE=NUMBER LBOUND=20 UBOUND=40 DECIMAL=FALSE
incubation_temp = 37

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Staining volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
stain_volume = 110

### VERAO VAR NAME='Storage mode?' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=2 UBOUND=25
storage_temp = 4

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_GEN = 'GEN2'

if pipette_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

### VERAO VAR NAME='labwarePositions.buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_plate_position = 1
### VERAO VAR NAME='labwarePositions.omnistainer' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 3

### VERAO VAR NAME='Deck position: Buffer W/ Antibodies plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='C7'
ab_plate_position = 4

### VERAO VAR NAME='labwarePositions.tiprack_300' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 9

### VERAO VAR NAME='Test mode (all delays reduced to 5s)' TYPE=BOOLEAN
testmode = False

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300 = tiprack_300_position
labwarePositions.ab_plate = ab_plate_position

###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):

    if 'thermosheath' in omnistainer_type and labwarePositions.omnistainer>9:
        raise Exception("Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_300])
    pipette.flow_rate.dispense = default_flow_rate
    pipette.flow_rate.aspirate = default_flow_rate
    pipette.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos - 1]

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    trough_wells = trough12.wells_by_name()

    buffers = Object()
    if dewax:
        buffers.dewax = trough_wells['A1']
        buffers.EtOH_100 = trough_wells['A2']
        buffers.EtOH_95 = trough_wells['A3']
        buffers.EtOH_70 = trough_wells['A4']

    buffers.PBS = trough_wells['A5']
    buffers.ER1 = trough_wells['A6']
    buffers.ER2 = trough_wells['A7']
    buffers.water = trough_wells['A8']
    wash_buffer = trough_wells['A11']

    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_plate, '96-well-plate')

    wells = Object()
    wells.block =           reagents_96plate.rows()[0][:num_samples]
    wells.primary_ab =      reagents_96plate.rows()[1][:num_samples]
    wells.secondary_ab =    reagents_96plate.rows()[2][:num_samples]
    wells.ligation =        reagents_96plate.rows()[3][:num_samples]
    wells.amp =             reagents_96plate.rows()[4][:num_samples]
    wells.post_block =      reagents_96plate.rows()[5][:num_samples]
    wells.detection =       reagents_96plate.rows()[6][:num_samples]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################


    protocol.home()
    closeShutter(protocol, pipette, omnistainer)
    puncture_wells(pipette, vars(buffers).values())


    if baking:
        protocol.comment("baking at: " + str(baking_temp))
        temp_mod.quick_temp(baking_temp)
        safe_delay(protocol, minutes=baking_time, msg="Baking")

    if dewax:

        dewax_equilib_delay = 5
        protocol.comment("adjusting temp to {}C for dewaxing".format(dewax_temp))
        temp_mod.quick_temp(dewax_temp)

        safe_delay(protocol, minutes=dewax_equilib_delay, msg = "equilibrating temp for to {}C for dewaxing".format(dewax_temp))

        openShutter(protocol, pipette, omnistainer)

        protocol.comment("dewaxing")

        #ultra-slow dispensing in order to fill the chamber without bubbles
        global sample_flow_rate
        sample_flow_rate /= dispense_slowdown_factor
        washSamples(pipette, buffers.dewax, sample_chambers, wash_volume, 3, keep_tip=True)
        sample_flow_rate *= dispense_slowdown_factor

        alc_wash_temp = 50
        temp_mod.quick_temp(alc_wash_temp)

        washSamples(pipette, buffers.EtOH_100, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 100% EtOH")
        washSamples(pipette, buffers.EtOH_100, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 100% EtOH")
        washSamples(pipette, buffers.EtOH_95, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 95% EtOH")
        washSamples(pipette, buffers.EtOH_70, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in 70% EtOH")

        washSamples(pipette, buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in PBS")
        pipette.drop_tip()

        washSamples(pipette, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)

    if agr:
        if 'ER1' in ER_buffer:
            er_buff_well = buffers.ER1
        else:
            er_buff_well = buffers.ER2

        openShutter(protocol, pipette, omnistainer)

        washSamples(pipette, er_buff_well, sample_chambers, wash_volume, 2, keep_tip=True)

        closeShutter(protocol, pipette, omnistainer)

        temp_mod.set_temp(retrieval_temp)

        #According to the exp calibration, 20 minutes is enough to reach 99C from 50C (alc wash temp)
        reps = 4
        for i in range (reps):
            safe_delay(protocol, minutes=5, msg = "heating up to "+str(retrieval_temp)+", topping off ER buffer as we go " + str(i+1) +"/"+ str(reps))
            openShutter(protocol, pipette, omnistainer)
            distribute_between_samples(pipette, er_buff_well, sample_chambers, wash_volume/2, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer)

        safe_delay(protocol, minutes=retrieval_time, msg = "HIER in progress")

        overshot = 10
        target_temp = room_temp-overshot
        temp_mod.set_temp(target_temp)

        cooldown_delay_min = 20
        topoff_every_min = 5

        for i in range(int(cooldown_delay_min/topoff_every_min)):
            safe_delay(protocol, minutes=topoff_every_min, msg = "adjusting temp to " + str(target_temp) + ", topping off ER buffer to prevent evap")
            openShutter(protocol, pipette, omnistainer)
            distribute_between_samples(pipette, er_buff_well, sample_chambers, wash_volume/2, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer)

        temp_mod.set_temp(room_temp)

        safe_delay(protocol, minutes=5, msg= "post-HIER equilibration")

        protocol.comment("washing in PBS")

        openShutter(protocol, pipette, omnistainer)

    if 'thermosheath' in omnistainer_type:
        openShutter(protocol, pipette, omnistainer)

        for i in range(2):
            washSamples(pipette, buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)
            safe_delay(protocol, minutes=5, msg="Incubating in PBS #" + str(i))

    if do_navinci:
        num_reps = 2 if double_add else 1

        temp_mod.quick_temp(incubation_temp)
        apply_and_incubate(protocol, pipette, wells.block, "Block", sample_chambers, stain_volume, 1, 60)
        apply_and_incubate(protocol, pipette, wells.primary_ab, "Primary abs", sample_chambers, stain_volume, 1, 60, new_tip='always')
        apply_and_incubate(protocol, pipette, wash_buffer, "Wash", sample_chambers, wash_volume, 3, wash_incubation_time)
        apply_and_incubate(protocol, pipette, wells.secondary_ab, "Navenibodies", sample_chambers, stain_volume, num_reps, 60)
        apply_and_incubate(protocol, pipette, wash_buffer, "Wash", sample_chambers, wash_volume, num_washes_post_NAB, wash_incubation_time, puncture=False)
        apply_and_incubate(protocol, pipette, wells.ligation, "Ligation", sample_chambers, stain_volume, 1, 30)
        apply_and_incubate(protocol, pipette, wash_buffer, "Wash", sample_chambers, wash_volume, 2, wash_incubation_time, puncture=False)
        temp_mod.quick_temp(amp_temp)
        apply_and_incubate(protocol, pipette, wells.amp, "Amplifiсation", sample_chambers, stain_volume, num_reps, 45)
        apply_and_incubate(protocol, pipette, wash_buffer, "Wash", sample_chambers, wash_volume, 2, wash_incubation_time, puncture=False)
        temp_mod.quick_temp(incubation_temp)
        apply_and_incubate(protocol, pipette, wells.post_block, "Post-block", sample_chambers, stain_volume, num_reps, 15)
        apply_and_incubate(protocol, pipette, wells.detection, "Detection", sample_chambers, stain_volume, 1, 30)
        temp_mod.quick_temp(room_temp)
        apply_and_incubate(protocol, pipette, wash_buffer, "Wash", sample_chambers, wash_volume, 3, wash_incubation_time, puncture=False)

    if storage_mode:
        if 'thermosheath' in omnistainer_type:
            closeShutter(protocol, pipette, omnistainer)
        protocol.comment(f"cooling down to {storage_temp} deg for storage. The protocol will pause next")
        temp_mod.set_temp(storage_temp)
        protocol.pause(
            msg=f"Protocol is paused for {storage_temp} C storage. "
                f"Hit Resume to end the protocol and turn off the thermal module")

    temp_mod.temp_off()
    protocol.comment(f"Protocol done - temperature module has been turned off")
    protocol.home()