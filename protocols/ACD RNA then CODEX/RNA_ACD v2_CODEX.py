from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 RNA',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX coverslip staining protocol for EA PAR2 instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

# The type of Parhelia Omni-Stainer
### VERAO VAR NAME='Device type' TYPE=CHOICE OPTIONS=['PAR2c_12coverslips', 'PAR2s_9slides','PAR2c_12coverslips_gray']
omniStainer_type = 'PAR2c_12coverslips_gray'


#The initial 1.6% PFA fixation is skipped for FFPE tissues
### VERAO VAR NAME='FFPE' TYPE=BOOLEAN
FFPE = True

### VERAO VAR NAME='Temp lag for adjusting the temp' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALS
templag=15
"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then
fluorescent detection probes are applied to the tissue directly in the PAR2 device.
If this option is enabled, make sure that
    1) detector oligo mixes have been added to the 96-well plate
    2) hybridization and stripping buffers have been added to the 12-trough
    see labware_layout.xlsx for details
"""
### VERAO VAR NAME='Antibody Screening Mode' TYPE=BOOLEAN
Antibody_Screening = True

### VERAO VAR NAME='Lid on the box' TYPE=CHOICE OPTIONS=['yes', 'no']
lid = 'no'

### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_black_96', 'parhelia_red_96', 'parhelia_red_96_with_strip']
type_of_96well_plate = 'parhelia_red_96_with_strip'

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 3

### VERAO VAR NAME='Tiprack starting position' TYPE=NUMBER LBOUND=1 UBOUND=95 DECIMAL=FALSE
tiprack_300_starting_pos = 1


### VERAO VAR NAME='RNA_hybridization time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
hybridization_time_minutes = 600

### VERAO VAR NAME='Antibody incubation time (minutes)' TYPE=NUMBER LBOUND=30 UBOUND=360 DECIMAL=FALSE
ab_incubation_time_minutes = 480

### VERAO VAR NAME='Sample wash volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
wash_volume = 150

### VERAO VAR NAME='Antibody mix volume' TYPE=NUMBER LBOUND=50 UBOUND=350 DECIMAL=FALSE
ab_volume = 100

### VERAO VAR NAME='Extra bottom gap (um, for calibration debugging)' TYPE=NUMBER LBOUND=0 UBOUND=100 DECIMAL=FALSE
extra_bottom_gap = 0

### VERAO VAR NAME='Sample flow rate' TYPE=NUMBER LBOUND=0.05 UBOUND=1 DECIMAL=TRUE INCREMENT=0.05
sample_flow_rate = 0.2

#Creating a dummy class
class Object:
    pass

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'right'


### VERAO VAR NAME='P300 model' TYPE=CHOICE OPTIONS=['GEN2', 'GEN1']
pipette_300_GEN = 'GEN1'

labwarePositions = Object()
labwarePositions.buffers_plate = 1
labwarePositions.rna_reagents_plate = 3
labwarePositions.codex_reagents_plate = 2
labwarePositions.tiprack_300_1 = 6
labwarePositions.tiprack_300_2 = 9

labwarePositions.heatmodule = 7

####################GENERAL SETUP################################

stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5

####################! FUNCTIONS - DO NOT MODIFY !#########################
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, dispense_bottom_gap=0, keep_tip = False):

    try:
        iter(samples)
        print('samples are iterable')
    except TypeError:
        print('samples arent iterable')
        samples = [samples]

    print ('Samples are:')
    print (samples)

    if not pipette.has_tip:
        pipette.pick_up_tip()

#    if(len(samples)==0):
#       samples = [samples]
#    print("Replacing solution on samples:" +str(samples) + " len=" + str(len(samples)))
    for i in range(0, num_repeats):
        print ("Iteration:"+ str(i))
        for s in samples:
            print(s)
            print ("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(dispense_bottom_gap), rate=sample_flow_rate).blow_out()
            stats.volume += volume

    if not keep_tip: pipette.drop_tip()
    if keep_tip: pipette.move_to(samples[len(samples)-1].bottom(60))

def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    if not pipette.has_tip: pipette.pick_up_tip()

    if(len(samples)==0):
        samples = [samples]

    for s in samples:
    #Diluting fixative:
        pipette.aspirate(volume+50, dilutant_buffer_well, rate=well_flow_rate)
        pipette.dispense(volume+50, sourceSolutionWell, rate=well_flow_rate)
        for iterator in range(0, 3):
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    #Applying fixative to sample:
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, s, rate=sample_flow_rate).blow_out()
        stats.volume += volume

    pipette.drop_tip()

def mix(pipette, sourceSolutionWell, volume, num_repeats):

    if not pipette.has_tip: pipette.pick_up_tip()

    #print ("Mixing solution in samples:" +str(sourceSolutionWell))
    for i in range(0, num_repeats):
    #    print ("Iteration:"+ str(i))
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)

    pipette.drop_tip()


#####################CUSTOM LABWARE_DEFINITION###################

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):
    ###########################LABWARE SETUP#################################

    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_1, 'tiprack 300ul 1')
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300_2, 'tiprack 300ul 2')

    pipette_300 = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single', pipette_300_location, tip_racks = [tiprack_300_1,tiprack_300_2])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300_1.wells()[tiprack_300_starting_pos-1]

    temp_mod = protocol.load_module('temperature module', labwarePositions.heatmodule)

    par2 = temp_mod.load_labware(omniStainer_type)
    wellslist=list(par2.wells_by_name().keys())
    wellslist = wellslist[1:num_samples+1]
    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    RNA_reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.rna_reagents_plate, '96-well-plate')
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

    buffers.washbuffer05 = buffer_wells['A10']
    buffers.water = buffer_wells['A11']

    preblock_wells = CODEX_reagents_96plate.rows()[0]
    antibody_wells = CODEX_reagents_96plate.rows()[1]
    reagent_F_wells = CODEX_reagents_96plate.rows()[2]
    rendering_wells = CODEX_reagents_96plate.rows()[3]




    H2O2wash1_wells = RNA_reagents_96plate.columns()[0]
    H2O2wash2_wells = RNA_reagents_96plate.columns()[1]
    avidinblock_wells = RNA_reagents_96plate.columns()[2]
    biotinblock_wells = RNA_reagents_96plate.columns()[3]
    probe_wells = RNA_reagents_96plate.columns()[4]
    amp1_wells = RNA_reagents_96plate.columns()[5]
    amp2_wells = RNA_reagents_96plate.columns()[6]
    amp3_wells = RNA_reagents_96plate.columns()[7]
    HRPC1_wells = RNA_reagents_96plate.columns()[8]
    substrate_wells = RNA_reagents_96plate.columns()[9]
    DAB_wells = RNA_reagents_96plate.columns()[10]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    print("wellslist is:")
    print(wellslist)
    print("par2.wells_by_name are:")
    print(par2.wells_by_name())
    print ("sample_chambers are:")
    print (sample_chambers)

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if not FFPE:
        #WASHING SAMPLES WITH PFA
        protocol.comment("first fix")
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, buffers.Hydration_PFA_1pt6pct, 2,1,extra_bottom_gap+21)
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume,1,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=10, msg = "first fix incubation")

    temp_mod.set_temperature(40)
    protocol.delay(minutes=templag)

    #PRE-HYB WASHING SAMPLES WITH PEROXIDE
    #First peroxide prewash
    print("puncturing avi-block wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, H2O2wash1_wells[i], H2O2wash1_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, H2O2wash1_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("avidin block incubation: 15 min")
    protocol.delay(minutes=2)


    #Second peroxide prewash
    print("puncturing avi-block wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, H2O2wash2_wells[i], H2O2wash2_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, H2O2wash2_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("avidin block incubation: 15 min")
    protocol.delay(minutes=2)



    temp_mod.set_temperature(25)
    protocol.delay(minutes=templag)

    #PRE-HYB WASHING SAMPLES WITH water at room temperature
    protocol.comment("washing in S2")
    #puncturing the foil
    washSamples(pipette_300, buffers.water, buffers.water, 2, 1,extra_bottom_gap+21)

    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")

    #AVIDIN block
    print("puncturing avi-block wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, avidinblock_wells[i], avidinblock_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, avidinblock_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("avidin block incubation: 15 min")
    protocol.delay(minutes=15)


    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2,extra_bottom_gap)


    #BIOTIN block
    print("puncturing avi-block wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, biotinblock_wells[i], biotinblock_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, biotinblock_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=15)


    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 2,extra_bottom_gap)
    
    #readjusting the heat module temp
    temp_mod.set_temperature(40)
    protocol.delay(minutes=templag)

    # APPLYING probe COCKTAILS TO SAMPLES

    print("puncturing and applying abs")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, probe_wells[i], probe_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
        washSamples(pipette_300, probe_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap)

    print("staining incubation: " + str(hybridization_time_minutes) + "min")
    protocol.delay(minutes=hybridization_time_minutes)

    
    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")
    #puncturing the foil
    washSamples(pipette_300, buffers.washbuffer05, buffers.washbuffer05, 0, 1,extra_bottom_gap)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")


    #AMP 1
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp1_wells[i], amp1_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp1_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=30)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")
    #puncturing the foil
    washSamples(pipette_300, buffers.washbuffer05, buffers.washbuffer05, 0, 1,extra_bottom_gap)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")


    #AMP 2
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp2_wells[i], amp2_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp2_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=15)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")
    #puncturing the foil
    washSamples(pipette_300, buffers.washbuffer05, buffers.washbuffer05, 0, 1,extra_bottom_gap)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")

    #AMP 3
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp3_wells[i], amp3_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, amp3_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=30)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")
    #puncturing the foil
    washSamples(pipette_300, buffers.washbuffer05, buffers.washbuffer05, 0, 1,extra_bottom_gap)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")


    #HRP-C1 aka V2-amp4.1
    print("puncturing amp1 wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, HRPC1_wells[i], HRPC1_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying the preblock")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, HRPC1_wells[i], sample_chambers[i], ab_volume, 1, extra_bottom_gap, keep_tip=True)
    pipette_300.drop_tip()
    print("biotin block incubation: 15 min")
    protocol.delay(minutes=15)

    #WASHING WITH 0.5 WASH BUFFER
    protocol.comment("washing in 0.5 wash buffer")
    #puncturing the foil
    washSamples(pipette_300, buffers.washbuffer05, buffers.washbuffer05, 0, 1,extra_bottom_gap)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "first wash with water")
    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 2,extra_bottom_gap)
    protocol.delay(minutes=2, msg = "second wash with water")


    temp_mod.set_temperature(25)
    protocol.delay(minutes=templag)


    # DILUTING AND APPLYING THE DAB
    print("puncturing the DAB wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, DAB_wells[i], DAB_wells[i], 2, 1, extra_bottom_gap + 21)
    print("puncturing the substrate wells")
    for i in range(len(wellslist)):
        washSamples(pipette_300, substrate_wells[i], substrate_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    print("applying DAB")
    for i in range(len(wellslist)):
        dilute_and_apply_fixative(pipette_300, DAB_wells[i], substrate_wells[i], sample_chambers[i], ab_volume+20)

    print("developing substrate")

    protocol.delay(minutes=10)

    washSamples(pipette_300, buffers.washbuffer05, sample_chambers, wash_volume, 5,extra_bottom_gap)

    washSamples(pipette_300, buffers.water, buffers.water, 2, 1, extra_bottom_gap + 21)
    washSamples(pipette_300, buffers.water, sample_chambers, wash_volume, 5, extra_bottom_gap)



    #CODEX PROTOCOL STARTS HERE



    if not FFPE:
        #WASHING SAMPLES WITH PFA
        protocol.comment("first fix")
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, buffers.Hydration_PFA_1pt6pct, 2,1,extra_bottom_gap+21)
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume,1,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=10, msg = "first fix incubation")

    #WASHING SAMPLES WITH S2
    protocol.comment("washing in S2")
    washSamples(pipette_300, buffers.Staining, buffers.Staining, 2, 1,extra_bottom_gap+21)
    washSamples(pipette_300, buffers.Staining, sample_chambers, wash_volume, 2,extra_bottom_gap)

    #WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    print("puncturing pre-block wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, preblock_wells[i], preblock_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    for i in range (len(wellslist)):
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], ab_volume,1,extra_bottom_gap)
    #INCUBATE
    protocol.delay(minutes=15, msg = "preblocking incubation")

    #APPLYING ANTIBODY COCKTAILS TO SAMPLES

    protocol.comment("preblocking")
    print("puncturing antibody wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, antibody_wells[i], antibody_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()

    protocol.comment("applying antibodies")
    for i in range (len(wellslist)):
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume,1,extra_bottom_gap)
    #INCUBATE
    protocol.delay(minutes=ab_incubation_time_minutes, msg = "staining incubation")

    for i in range(2):
        #WASHING SAMPLES WITH Staining buffer
        protocol.comment("first washing with Staining buffer")
        washSamples(pipette_300, buffers.Staining, sample_chambers, wash_volume,2,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=5, msg = "first incubation in Staining Buffer")


    #POST STAINING FIXING SAMPLES WITH PFA
    protocol.comment("second fix")
    washSamples(pipette_300, buffers.Storage_PFA_4pct, buffers.Storage_PFA_4pct, 2,1,extra_bottom_gap+21)
    washSamples(pipette_300, buffers.Storage_PFA_4pct, sample_chambers, wash_volume,1,extra_bottom_gap)
    #INCUBATE
    protocol.delay(minutes=5, msg="incubation with fixative")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, buffers.PBS, 2,2,extra_bottom_gap)
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2,extra_bottom_gap)

    # FIXING SAMPLES WITH Methanol
    washSamples(pipette_300, buffers.MeOH, buffers.MeOH, 2,1,extra_bottom_gap+21)
    for i in range(2):
        protocol.comment("applying MeOH")
        washSamples(pipette_300, buffers.MeOH, sample_chambers, wash_volume,1,extra_bottom_gap)
        # INCUBATE
        protocol.delay(minutes=2.5, msg="First MeOH incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2,extra_bottom_gap)

    #DILUTING AND APPLYING THE FIXATIVE
    print("puncturing reagent F wells")
    for i in range(len(wellslist)):
        print(i)
        washSamples(pipette_300, reagent_F_wells[i], reagent_F_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
    pipette_300.drop_tip()
    for i in range (len(wellslist)):
        dilute_and_apply_fixative(pipette_300, reagent_F_wells[i], buffers.PBS, sample_chambers[i], wash_volume)

    protocol.comment("third fix incubation")
    protocol.delay(minutes=10, msg = "Reagent F incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2,extra_bottom_gap)

    if Antibody_Screening:
        washSamples(pipette_300, buffers.Stripping_buffer, buffers.Stripping_buffer, 2,1,extra_bottom_gap+21)
        washSamples(pipette_300, buffers.Screening_Buffer, buffers.Screening_Buffer, 2,1,extra_bottom_gap+21)
        #PRE-CLEARING THE TISSUE
        for i in range (3):
            protocol.comment("tissue clearing round" + str(i+1))
            washSamples(pipette_300, buffers.Stripping_buffer, sample_chambers, wash_volume,2,extra_bottom_gap)
            protocol.delay(seconds=30)
            washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,1,extra_bottom_gap)
            washSamples(pipette_300, buffers.CODEX_buffer_1x, sample_chambers, wash_volume,1,extra_bottom_gap)

        #Equilibration in rendering buffer
        protocol.comment("Equilibration in rendering buffer")
        washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,1,extra_bottom_gap)

        #RENDERING
        protocol.comment("Applying rendering solution to wells")
        print("puncturing wells with rendering mixture")
        for i in range(len(wellslist)):
            print(i)
            washSamples(pipette_300, rendering_wells[i], rendering_wells[i], 2, 1, extra_bottom_gap + 21, keep_tip=True)
        pipette_300.drop_tip()

        for i in range (len(wellslist)):
            washSamples(pipette_300, rendering_wells[i], sample_chambers[i], ab_volume,1,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=10, msg = "rendering hybridization")

        #WASH SAMPLES IN 1x CODEX buffer
        protocol.comment("Washing with rendering buffer")
        washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,2,extra_bottom_gap)

    #STORAGE, washing samples every hour for 100 hours
    washSamples(pipette_300, buffers.storage, buffers.storage, 2,1,extra_bottom_gap+21)
    washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume,1,extra_bottom_gap, keep_tip=True)

    for i in range(10):
        washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume/3,1,extra_bottom_gap, keep_tip=True)
        protocol.delay(minutes=90, msg = "storing samples in storage buffer")
