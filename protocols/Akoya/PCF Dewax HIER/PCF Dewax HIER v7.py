## VERAO GLOBAL
from global_functions import *
### END VERAO GLOBAL

metadata = {
    'protocolName': 'Parhelia Dewax/HIER for PCF v7 quick_temp',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia Dewax/HIER for PCF, optimized for speed using the new quick_temp function',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate','omni_stainer_c12_cslps_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='D3'
num_samples = 1

### VERAO VAR NAME='Baking' TYPE=BOOLEAN
baking = False

### VERAO VAR NAME='Baking time (minutes)' TYPE=NUMBER LBOUND=10 UBOUND=180 DECIMAL=FALSE
baking_time = 30

### VERAO VAR NAME='Baking temperature (C)' TYPE=NUMBER LBOUND=50 UBOUND=70 DECIMAL=FALSE
baking_temp = 65

### VERAO VAR NAME='Dewax' TYPE=BOOLEAN EXCEL_POSITION='D2'
dewax = True

### VERAO VAR NAME='Dewaxing temperature (C)' TYPE=NUMBER LBOUND=60 UBOUND=80 DECIMAL=FALSE
dewax_temp = 72

### VERAO VAR NAME='Dewax fill slowdown factor' TYPE=NUMBER LBOUND=1 UBOUND=20 DECIMAL=FALSE 
dispense_slowdown_factor = 3

### VERAO VAR NAME='Antigen Retrieval Buffer' TYPE=CHOICE OPTIONS=['ER1','ER2'] EXCEL_POSITION='D5'
ER_buffer = 'ER2'

### VERAO VAR NAME='Retrival Temperature (C)' TYPE=NUMBER LBOUND=60 UBOUND=99 DECIMAL=FALSE
retrieval_temp = 98

### VERAO VAR NAME='Retrival Time (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
retrieval_time = 40

### VERAO VAR NAME='Room temp (C)' TYPE=NUMBER LBOUND=15 UBOUND=99 DECIMAL=FALSE
room_temp = 22

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1.0 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

### VERAO VAR NAME='Sample wash volume (ul)' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE EXCEL_POSITION='D4'
wash_volume = 150

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
buffers_plate_position = 3
### VERAO VAR NAME='labwarePositions.omnistainer' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
omnistainer_position = 1

### VERAO VAR NAME='labwarePositions.tiprack_300' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 9

### VERAO VAR NAME='Test mode (all delays reduced to 5s)' TYPE=BOOLEAN
testmode = False

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300 = tiprack_300_position


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

    HIER_wells = trough12.wells_by_name()

    buffers = Object()
    if dewax:
        buffers.dewax = HIER_wells['A1']
        buffers.EtOH_100 = HIER_wells['A2']
        buffers.EtOH_95 = HIER_wells['A3']
        
    buffers.PBS = HIER_wells['A4']
    buffers.ER1 = HIER_wells['A5']
    buffers.ER2 = HIER_wells['A6']
    buffers.water = HIER_wells['A7']


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
        washSamples(pipette, buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=1, msg = "incubating in PBS")
        pipette.drop_tip()

        washSamples(pipette, buffers.water, sample_chambers, wash_volume, 2, keep_tip=True)

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
        safe_delay(protocol, minutes=5, msg = "heating up to "+str(retrieval_temp)+", topping off ER buffer as we go" + str(i+1) +"/"+ str(reps))
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

    for i in range (2):
        washSamples(pipette, buffers.PBS, sample_chambers, wash_volume, 2, keep_tip=True)
        safe_delay(protocol, minutes=5, msg = "Incubating in PBS #" + str(i))

    if 'thermosheath' in omnistainer_type:
        closeShutter(protocol, pipette, omnistainer)
    if storage_mode:
        protocol.comment(f"cooling down to {storage_temp} deg for storage. The protocol will pause next")
        temp_mod.set_temp(storage_temp)
        protocol.pause(
            msg=f"Protocol is paused for {storage_temp} C storage. "
                f"Hit Resume to end the protocol and turn off the thermal module")
        
    temp_mod.temp_off()
    protocol.comment(f"Protocol done - temperature module has been turned off")
    protocol.home()




