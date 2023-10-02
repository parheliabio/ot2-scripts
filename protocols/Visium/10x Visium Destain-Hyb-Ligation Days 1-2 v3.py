
metadata = {
    'protocolName': '10x Visium CytAssist prep, Day 1 and 2, v3',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia protocol for 10x Visium CytAssist prep, Day 1 and 2',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Destaining Temperature (C)' TYPE=NUMBER LBOUND=35 UBOUND=50 DECIMAL=FALSE
destaining_temp = 42

### VERAO VAR NAME='Destaining (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
destaining_time = 15

### VERAO VAR NAME='Decrosslinking Temperature (C)' TYPE=NUMBER LBOUND=90 UBOUND=99 DECIMAL=FALSE
retrieval_temp = 95

### VERAO VAR NAME='Decrosslinking Time (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
retrieval_time = 60

### VERAO VAR NAME='Hybridization temperature' TYPE=NUMBER LBOUND=40 UBOUND=60 DECIMAL=FALSE
hyb_temp = 50

### VERAO VAR NAME='Ligation Temperature (C)' TYPE=NUMBER LBOUND=30 UBOUND=45 DECIMAL=FALSE
ligation_temp = 37

### VERAO VAR NAME='Ligation Time (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
ligation_time = 60

### VERAO VAR NAME='Post-Ligation Wash Temperature (C)' TYPE=NUMBER LBOUND=50 UBOUND=70 DECIMAL=FALSE
post_ligation_temp = 57


### VERAO VAR NAME='Room temp (C)' TYPE=NUMBER LBOUND=60 UBOUND=99 DECIMAL=FALSE
room_temp = 22

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96_with_strips'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 1

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1


### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

### VERAO VAR NAME='Probe hyb volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
probe_volume = 200

### VERAO VAR NAME='Sample wash volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Ligation mix volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
lig_volume = 150

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
buffers_plate_position = 10

### VERAO VAR NAME='labwarePositions.buffers_plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
probes_plate_position = 7

### VERAO VAR NAME='labwarePositions.omnistainer' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='labwarePositions.tiprack_300' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 6

### VERAO VAR NAME='labwarePositions.tiprack_300_2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position_2 = 9

### VERAO VAR NAME='Test mode (all delays reduced to 30sec)' TYPE=BOOLEAN
testmode = False

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.probes_plate = probes_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300 = tiprack_300_position
labwarePositions.tiprack_300_2 = tiprack_300_position_2

###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

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

    buffer_wells = trough12.wells_by_name()

    buffers = Object()

    buffers.destain = buffer_wells['A1']
    buffers.decrosslinking = buffer_wells['A2']
    buffers.SSC = buffer_wells['A3']
    buffers.Eosin = buffer_wells['A4']
    buffers.PBS = buffer_wells['A5']

    probes_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.probes_plate, '96-well-plate')

    wells = Object()

    wells.prehyb         = probes_96plate.rows()[0][:num_samples]
    wells.probe_hyb      = probes_96plate.rows()[1][:num_samples]
    wells.post_hyb_wash1 = probes_96plate.rows()[2][:num_samples]
    wells.post_hyb_wash2 = probes_96plate.rows()[3][:num_samples]
    wells.ligation       = probes_96plate.rows()[4][:num_samples]
    wells.post_lig_wash1 = probes_96plate.rows()[5][:num_samples]
    wells.post_lig_wash2 = probes_96plate.rows()[6][:num_samples]


    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    overshot = 10
    time_increment = 10

    #################PROTOCOL####################

    puncture_wells(pipette, vars(buffers).values())

    openShutter(protocol, pipette, omnistainer)
    washSamples(pipette, buffers.destain, sample_chambers, wash_volume, 2, keep_tip=True)
    closeShutter(protocol, pipette, omnistainer)

    #adding an overshot
    temp_mod.set_temp(destaining_temp+overshot)
    delay_seconds = 120
    safe_delay(protocol, seconds=120, msg = "adjusting temp to " + str(destaining_temp+10))

    temp_mod.set_temp(destaining_temp)

    safe_delay(protocol, minutes=15, msg = "destaining at " + str(destaining_temp))

    target_temp = room_temp-overshot
    delay_seconds = 420
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to " + str(target_temp))

    temp_mod.set_temp(room_temp)

    openShutter(protocol, pipette, omnistainer)

    washSamples(pipette, buffers.decrosslinking, sample_chambers, wash_volume, 2, keep_tip=True)

    closeShutter(protocol, pipette, omnistainer)

    target_temp = 99.9
    delay_seconds = 25*60
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to " + str(target_temp))

    temp_mod.set_temp(retrieval_temp)

    safe_delay(protocol, minutes=retrieval_time, msg = "HIER in progress at " + str(retrieval_temp))

    target_temp = room_temp-overshot
    temp_mod.set_temp(target_temp)
    topoff_every_X_deg = 10

    delay_seconds = 20*60
    prevTemp = temp_mod.get_temp()
    temp_mod.set_temp(target_temp)

    for i in range(int(delay_seconds/time_increment)):
        currTemp = temp_mod.get_temp()
        safe_delay(protocol, seconds=time_increment, msg = "adjusting temp to " + str(target_temp))
        if(prevTemp-currTemp>topoff_every_X_deg):
            openShutter(protocol, pipette, omnistainer)
            distribute_between_samples(pipette, buffers.decrosslinking, sample_chambers, wash_volume, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer)
            prevTemp = currTemp
    temp_mod.set_temp(room_temp)

    safe_delay(protocol, minutes=10, msg = "Equilibrating")

    puncture_wells(pipette, wells.prehyb,keep_tip=True)

    openShutter(protocol, pipette, omnistainer)

    for i in range (num_samples):
        washSamples(pipette, wells.prehyb[i], sample_chambers[i], probe_volume, 1, keep_tip=True)

    safe_delay(protocol, minutes=10, msg = "Pre-hyb")

    puncture_wells(pipette, wells.probe_hyb, keep_tip=True)

    for i in range (num_samples):
        washSamples(pipette, wells.probe_hyb[i], sample_chambers[i], probe_volume, 1, keep_tip=True)

    closeShutter(protocol, pipette, omnistainer)

    target_temp = hyb_temp+overshot
    delay_seconds = 5*60
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to "+str(target_temp))
    temp_mod.set_temp(hyb_temp)

    protocol.pause(msg = "Paused for 16-24h Hybridization. Prepare the ligation mix and wash buffers and place them in the strip tube plate, then press Resume to continue the protocol")

    puncture_wells(pipette, wells.post_hyb_wash1+wells.post_hyb_wash2,keep_tip=True)

    for phw in [wells.post_hyb_wash1,wells.post_hyb_wash1,wells.post_hyb_wash2]:
        openShutter(protocol, pipette, omnistainer)
        for i in range (num_samples):
            washSamples(pipette, phw[i], sample_chambers[i], wash_volume, 1, keep_tip=True)
        closeShutter(protocol, pipette, omnistainer)
        safe_delay(protocol, minutes=5, msg="post hyb wash at " + str(hyb_temp))

    target_temp = room_temp-overshot
    delay_seconds = 480
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to " + str(target_temp))
    temp_mod.set_temp(room_temp)

    openShutter(protocol, pipette, omnistainer)

    for i in range (num_samples):
        washSamples(pipette, buffers.SSC, sample_chambers[i], probe_volume, 2, keep_tip=True)
    safe_delay(protocol, minutes=5, msg="post hyb wash at room temp")

    closeShutter(protocol, pipette, omnistainer)

    target_temp = ligation_temp+overshot
    delay_seconds = 120
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to " + str(target_temp))
    temp_mod.set_temp(ligation_temp)

    puncture_wells(pipette, wells.ligation,keep_tip=True)

    protocol.comment("Applying the ligation mix")
    openShutter(protocol, pipette, omnistainer)
    for i in range (num_samples):
        washSamples(pipette, wells.ligation[i], sample_chambers[i], lig_volume, 1, keep_tip=True)
    safe_delay(protocol, minutes=ligation_time, msg = "ligating at " + str(ligation_temp))
    closeShutter(protocol, pipette, omnistainer)

    target_temp = post_ligation_temp+overshot
    delay_seconds = 120
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to " + str(target_temp))
    temp_mod.set_temp(post_ligation_temp)

    protocol.comment("Post-Ligation Wash at " + str(post_ligation_temp))
    puncture_wells(pipette, wells.post_lig_wash1+wells.post_lig_wash2,keep_tip=True)

    for plw in [wells.post_lig_wash1,wells.post_lig_wash2]:
        openShutter(protocol, pipette, omnistainer)
        for i in range (num_samples):
            washSamples(pipette, plw[i], sample_chambers[i], probe_volume, 1, keep_tip=True)
        safe_delay(protocol, minutes=5, msg="post ligation wash at " + str(post_ligation_temp))
        closeShutter(protocol, pipette, omnistainer)

    target_temp = room_temp-overshot
    delay_seconds = 520
    temp_mod.set_temp(target_temp)
    safe_delay(protocol, seconds=delay_seconds, msg = "adjusting temp to " + str(target_temp))
    temp_mod.set_temp(room_temp)

    openShutter(protocol, pipette, omnistainer)
    for rep in range(2):
        for i in range (num_samples):
            washSamples(pipette, buffers.SSC, sample_chambers[i], wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=5, msg="SSC wash  at room temp #" + str(rep))

    for i in range (num_samples):
        washSamples(pipette, buffers.Eosin, sample_chambers[i], wash_volume, 1, keep_tip=True)
        safe_delay(protocol, minutes=1, msg="Eosin staining")

    for rep in range(3):
        for i in range (num_samples):
            washSamples(pipette, buffers.PBS, sample_chambers[i], wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=5, msg="PBS wash #" + str(rep))
    temp_mod.temp_off()
