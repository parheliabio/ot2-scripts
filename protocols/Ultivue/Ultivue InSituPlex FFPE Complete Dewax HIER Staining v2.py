### VERAO GLOBAL
from global_functions import *
### END VERAO GLOBAL

metadata = {
    'protocolName': 'Ultivue InSituPlex Parhelia Dewax HIER Ultivue InSituPlex v2',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia Dewax HIER Postfix v6.0 + Ultivue InSituPlex Omnivue 4-plex v2.1',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['omni_stainer_s12_slides_with_thermosheath_on_coldplate']
omnistainer_type = 'omni_stainer_s12_slides_with_thermosheath_on_coldplate'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
type_of_96well_plate = 'parhelia_skirted_96'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='C5'
num_samples = 2

### VERAO VAR NAME='Baking?' TYPE=BOOLEAN EXCEL_POSITION='F1'
baking_prepping = True

### VERAO VAR NAME='Dewax?' TYPE=BOOLEAN EXCEL_POSITION='F2'
dewax_prepping = True

### VERAO VAR NAME='Antigen Retrieval HIER?' TYPE=BOOLEAN EXCEL_POSITION='F3'
hier_prepping = True

### VERAO VAR NAME='Preblock? (Antibody Diluent step)?' TYPE=BOOLEAN EXCEL_POSITION='F6'
preblock_staining = True

### VERAO VAR NAME='Primary Ab staining?' TYPE=BOOLEAN EXCEL_POSITION='C1'
primary_staining = True

### VERAO VAR NAME='Secondary Ab staining?' TYPE=BOOLEAN EXCEL_POSITION='C2'
secondary_staining = True

### VERAO VAR NAME='Reporters + nuclear counterstain?' TYPE=BOOLEAN EXCEL_POSITION='D2'
probe_staining = True

# if both raise issue

### VERAO VAR NAME='Storage mode?' TYPE=BOOLEAN
storage_mode = True

### VERAO VAR NAME='Baking temperature (C)' TYPE=NUMBER LBOUND=50 UBOUND=70 DECIMAL=TRUE INCREMENT=0.1
baking_temp = 65

### VERAO VAR NAME='Baking time (minutes)' TYPE=NUMBER LBOUND=10 UBOUND=180 DECIMAL=FALSE
baking_time = 10

### VERAO VAR NAME='Dewaxing temperature (C)' TYPE=NUMBER LBOUND=60 UBOUND=80 DECIMAL=TRUE INCREMENT=0.1
dewax_temp = 72

### VERAO VAR NAME='Dewaxing time (min)' TYPE=NUMBER LBOUND=1 UBOUND=360 DECIMAL=FALSE
dewax_time = 10

### VERAO VAR NAME='Dewax fill slowdown factor' TYPE=NUMBER LBOUND=1 UBOUND=20 DECIMAL=FALSE
dispense_slowdown_factor = 3

### VERAO VAR NAME='Dewax dispensing Z-offset' TYPE=NUMBER LBOUND=0 UBOUND=2 DECIMAL=FALSE
dewax_disp_offset = 2

### VERAO VAR NAME='Retrival Temperature (C)' TYPE=NUMBER LBOUND=60.0 UBOUND=99.9 DECIMAL=TRUE INCREMENT=0.1
retrieval_temp = 98

### VERAO VAR NAME='Retrival Time (min)' TYPE=NUMBER LBOUND=1 UBOUND=480 DECIMAL=FALSE
retrieval_time = 40

### VERAO VAR NAME='ER buffer' TYPE=CHOICE OPTIONS=['ER1','ER2'] EXCEL_POSITION='C8'
ER_buffer = 'ER2'

### VERAO VAR NAME='Amplification temp (standard is 30.0) (C)' TYPE=NUMBER LBOUND=10 UBOUND=50 DECIMAL=TRUE INCREMENT=0.1
amp_temp = 30

### VERAO VAR NAME='Room temp (C)' TYPE=NUMBER LBOUND=15 UBOUND=25 DECIMAL=TRUE INCREMENT=0.1
room_temp = 22.5

### VERAO VAR NAME='Preblock (Antibody Diluent) incubation time (min)' TYPE=NUMBER LBOUND=10 UBOUND=120 DECIMAL=FALSE
antibody_diluent_incubation_min = 15

### VERAO VAR NAME='Primary Antibody incubation time (min)' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
primary_ab_incubation = 60

### VERAO VAR NAME='Amplification Pretreatment time (min)' TYPE=NUMBER LBOUND=5 UBOUND=120 DECIMAL=FALSE
amp_pretreatment_incubation = 30

### VERAO VAR NAME='Amplification time (min)' TYPE=NUMBER LBOUND=5 UBOUND=600 DECIMAL=FALSE
amp_incubation = 90

### VERAO VAR NAME='Nuclear Counterstain incubation time (min)' TYPE=NUMBER LBOUND=5 UBOUND=600 DECIMAL=FALSE
counterstain_incubation = 15

### VERAO VAR NAME='Fluorescent Probe incubation time (min)' TYPE=NUMBER LBOUND=30 UBOUND=120 DECIMAL=FALSE
fluor_probe_incubation = 60

### VERAO VAR NAME='PBS wash incubation time' TYPE=NUMBER LBOUND=1 UBOUND=30 DECIMAL=FALSE
wash_incubation = 5

### VERAO VAR NAME='Storage temperature' TYPE=NUMBER LBOUND=2 UBOUND=25 DECIMAL=TRUE INCREMENT=0.1
storage_temp = 4

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE EXCEL_POSITION='C7'
wash_volume = 150

### VERAO VAR NAME='Antibody staining volume' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE EXCEL_POSITION='C6'
ab_volume = 110

### VERAO VAR NAME='Double add (uses 2x reagents, but may improve uniformity on large tissues)' TYPE=BOOLEAN EXCEL_POSITION='C4'
double_add = False

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_location = 'left'

### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_GEN = 'GEN2'

if pipette_GEN == 'GEN2':
    pipette_type = 'p300_single_gen2'
else:
    pipette_type = 'p300_single'

### VERAO VAR NAME='Deck position: 12-trough buffers reservoir' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='B19'
buffers_plate_position = 7

### VERAO VAR NAME='Deck position: Parhelia Omni-stainer S12 module' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='B13'
omnistainer_position = 1

### VERAO VAR NAME='Deck position: Antibody Reagent plate' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
ab_plate_position = 8

### VERAO VAR NAME='Deck position: Tiprack 1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='B11'
tiprack_300_1_position = 10

### VERAO VAR NAME='Tip type for tiprack 1' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type_tiprack_1 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1

### VERAO VAR NAME='Deck position: Tiprack 22' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE EXCEL_POSITION='B11'
tiprack_300_2_position = 11

### VERAO VAR NAME='Tip type for tiprack 2' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tip_type_tiprack_2 = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='TEST MODE (ALL INCUBATION DELAYS WILL BE SKIPPED)' TYPE=BOOLEAN
testmode = False

### VERAO VAR NAME='temp_mod number (usually it is 0, keep at 0 unless you get "/dev/ttyUSB*" error)' TYPE=NUMBER LBOUND=0 UBOUND=9 DECIMAL=FALSE
temp_mod_number = 0

labwarePositions = Object()
labwarePositions.buffers_plate = buffers_plate_position
labwarePositions.ab_plate = ab_plate_position
labwarePositions.omnistainer = omnistainer_position
labwarePositions.tiprack_300_1 = tiprack_300_1_position
labwarePositions.tiprack_300_2 = tiprack_300_2_position


###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    if 'thermosheath' in omnistainer_type and labwarePositions.omnistainer > 9:
        raise Exception("Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')
    #Tiprack
    tiprack_1 = protocol.load_labware(tip_type_tiprack_1, labwarePositions.tiprack_300_1,
                                      'tiprack 200/300ul 1')
    tiprack_2 = protocol.load_labware(tip_type_tiprack_2, labwarePositions.tiprack_300_2,
                                      'tiprack 200/300ul 2')

    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_1, tiprack_2])
    pipette.flow_rate.dispense = default_flow_rate
    pipette.flow_rate.aspirate = default_flow_rate
    pipette.starting_tip = tiprack_1.wells()[tiprack_300_starting_pos-1]

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')
    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.ab_plate, '96-well-plate')


    antibody_diluent_wells = reagents_96plate.rows()[0][:num_samples]
    primary_ab_wells = reagents_96plate.rows()[1][:num_samples]
    pre_amp_wells = reagents_96plate.rows()[2][:num_samples]
    amp_wells = reagents_96plate.rows()[3][:num_samples]
    counterstain_wells = reagents_96plate.rows()[4][:num_samples]
    fluor_probe_wells = reagents_96plate.rows()[5][:num_samples]
    fluor_probe_2_wells = reagents_96plate.rows()[6][:num_samples]


    HIER_wells = trough12.wells_by_name()

    buffers = Object()

    buffers.dewax = HIER_wells['A1']
    buffers.EtOH_100 = HIER_wells['A2']
    buffers.EtOH_95 = HIER_wells['A3']

    buffers.PBS = [HIER_wells['A4'], HIER_wells['A11'], HIER_wells['A12']]

    buffers.ER1 = HIER_wells['A5']
    buffers.ER2 = HIER_wells['A6']
    buffers.water = HIER_wells['A7']

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    pbs_wells_list = []

    step_reps = 1

    dispense_reps = 2 if double_add else 1

    #################PROTOCOL####################

    protocol.comment("Starting the "+ metadata["protocolName"] +" for samples:" + str(sample_chambers))
    protocol.home()


    pbs = buffers.PBS

    delattr(buffers, "PBS")

    puncture_wells(pipette, vars(buffers).values(), keep_tip=True)

    puncture_wells(pipette, pbs, keep_tip=True)

    buffers.PBS = pbs


    ##assigning each sample to its own PBS well
    for i in range(num_samples):
        pbs_wells_list.append(buffers.PBS[int(i/4)])
    buffers.PBS = pbs_wells_list


    ## never repeat yourself!
    def wash():
        apply_and_incubate(protocol, pipette, buffers.PBS, "1x PBS Wash", sample_chambers, wash_volume, 2,
                           wash_incubation, dispense_repeats=2)

    closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=False)

    # if baking:
    if baking_prepping:
        protocol.comment("baking at: " + str(baking_temp))
        temp_mod.quick_temp(baking_temp)
        safe_delay(protocol, minutes=baking_time, msg="Baking")

    if dewax_prepping:
        protocol.comment("adjusting temp to {}C for dewaxing".format(dewax_temp))
        temp_mod.quick_temp(dewax_temp)

        safe_delay(protocol, minutes=10, msg="Allowing paraffin to melt")

        protocol.comment("dewaxing")

        #ultra-slow dispensing in order to fill the chamber without bubbles
        global sample_flow_rate
        sample_flow_rate /= dispense_slowdown_factor

        for i in range(2):
            openShutter(protocol, pipette, omnistainer)
            washSamples(pipette, buffers.dewax, sample_chambers, wash_volume, 1, keep_tip=True, dispensing_offset = -dewax_disp_offset)
            closeShutter(protocol, pipette, omnistainer)
            safe_delay(protocol, minutes=dewax_time, msg="Dewaxing")

        sample_flow_rate *= dispense_slowdown_factor

    if hier_prepping:
        alc_wash_temp = 50
        temp_mod.quick_temp(alc_wash_temp)

        for buf in ['EtOH_100', 'EtOH_100', 'EtOH_95', 'PBS', 'water', ER_buffer]:
            openShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
            apply_and_incubate(protocol, pipette, vars(buffers)[buf],  buf, sample_chambers, wash_volume, step_repeats=1, incubation_time=0, dispense_repeats=1)
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
            safe_delay(protocol, minutes=1, msg = "incubating in " + buf)

        er_buff_well = vars(buffers)[ER_buffer]

        temp_mod.set_temp(retrieval_temp)

        #According to the exp calibration, 20 minutes is enough to reach 99C from 50C (alc wash temp)
        reps = 4
        for i in range (reps):
            safe_delay(protocol, minutes=5, msg = "heating up to "+str(retrieval_temp)+", topping off ER buffer as we go" + str(i+1) +"/"+ str(reps))
            openShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
            distribute_between_samples(pipette, er_buff_well, sample_chambers, wash_volume/2, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)

        safe_delay(protocol, minutes=retrieval_time, msg = "HIER in progress")

        pbs_wash_temp = room_temp

        #how much to overshoot the temp by initially in order to hasten the temp equilibration
        overshot = 10

        target_temp = room_temp-overshot
        temp_mod.set_temp(target_temp)

        ### according to the calibration, it takes about 20 min to cool off from 99C to RT
        cooldown_delay_min = 20
        topoff_every_min = 5

        for i in range(int(cooldown_delay_min/topoff_every_min)):
            safe_delay(protocol, minutes=topoff_every_min, msg = "adjusting temp to " + str(target_temp) + ", topping off ER buffer to prevent evap")
            openShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)
            distribute_between_samples(pipette, er_buff_well, sample_chambers, wash_volume/2, 1, keep_tip=True)
            closeShutter(protocol, pipette, omnistainer, use_tip=True, keep_tip=True)

        protocol.comment("washing in PBS")
        wash()

        temp_mod.set_temp(room_temp)

        safe_delay(protocol, minutes=10, msg= "post-HIER equilibration")

    protocol.comment(f"Moving on to Ultivue InSituPlex")
    openShutter(protocol, pipette, omnistainer)

    if preblock_staining:
        apply_and_incubate(protocol, pipette, antibody_diluent_wells, "Antibody Diluent (Block)", sample_chambers,
                           ab_volume, step_reps, antibody_diluent_incubation_min, dispense_repeats=dispense_reps)

    if primary_staining:
        apply_and_incubate(protocol, pipette, primary_ab_wells, "1x (Primary) Ab solution", sample_chambers, ab_volume,
                           step_reps, primary_ab_incubation, dispense_repeats=dispense_reps)
        wash()

    if secondary_staining:
        apply_and_incubate(protocol, pipette, pre_amp_wells, "Pre-Amp Mix", sample_chambers, ab_volume, step_reps,
                           amp_pretreatment_incubation, dispense_repeats=dispense_reps)
        wash()

        closeShutter(protocol, pipette, omnistainer)
        temp_mod.quick_temp(amp_temp)
        openShutter(protocol, pipette, omnistainer)
        apply_and_incubate(protocol, pipette, amp_wells, "1x Amp Solution", sample_chambers, ab_volume, step_repeats=1,
                           incubation_time=0,  dispense_repeats=1)
        closeShutter(protocol, pipette, omnistainer)
        safe_delay(protocol, minutes=amp_incubation, msg="Amplification in progress")
        openShutter(protocol, pipette, omnistainer)
        temp_mod.quick_temp(room_temp)
        wash()

    if probe_staining:
        apply_and_incubate(protocol, pipette, counterstain_wells, "1x Nuclear Counterstain", sample_chambers, ab_volume,
                           2 if double_add else 1, counterstain_incubation)
        wash()
        apply_and_incubate(protocol, pipette, fluor_probe_wells, "Fluorescent Probe", sample_chambers, ab_volume,
                           2 if double_add else 1, fluor_probe_incubation - 1)
        if double_add:
            apply_and_incubate(protocol, pipette, fluor_probe_2_wells, "Fluorescent Probe", sample_chambers, ab_volume,
                               2 if double_add else 1, fluor_probe_incubation - 1)
        wash()

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