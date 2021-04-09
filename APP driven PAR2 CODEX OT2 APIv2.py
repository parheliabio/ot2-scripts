from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 CODEX coverslip staining protocol',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX coverslip staining protocol for EA PAR2 instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

class Object:
    pass

####################MODIFIABLE RUN PARAMETERS#########################
wellslist = ['A1','A2','A3','A4','B1','B2']

tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

pipette_300_location='right'

ab_incubation_time_minutes = 90

wash_volume = 150
ab_volume=100
par2_type="par2_cslp_metal_v1"
#par2_type="par2_slides_v1"

####################LABWARE LAYOUT ON DECK#########################
labwarePositions = Object()
labwarePositions.buffers_plate = 1
labwarePositions.par2 = 2
labwarePositions.antibodies_plate = 3
labwarePositions.tiprack_300 = 6

####################GENERAL SETUP################################
stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.2
wash_volume = 150
ab_volume=100

####################! FUNCTIONS - DO NOT MODIFY !######################### 
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, keep_tip = False):

    try:
        iter(samples)
        #print('samples are iterable')
    except TypeError:
        #print('samples arent iterable')
        samples = [samples]
    
    if not pipette.has_tip: pipette.pick_up_tip()
    
    if len(samples)==0:
        samples = [samples]
    #print("Replacing solution on samples:" +str(samples) + " len=" + str(len(samples)))
    for i in range(0, num_repeats):
    #    print("Iteration:"+ str(i))
        for s in samples:
    #        print("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s, rate=sample_flow_rate).blow_out()
            stats.volume += volume
    
    if not keep_tip: pipette.drop_tip()
    if keep_tip: pipette.move_to(sourceSolutionWell[length(sourceSolutionWell)-1].bottom(60))
    
def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]
    
    if not pipette.has_tip: pipette.pick_up_tip()
    
    if(len(samples)==0):
        samples = [samples]
    #print ("Applying fixative to samples:" +str(samples) + " len=" + str(len(samples)))
 
    for s in samples:
    #    print ("Diluting fixative: " + str(s))
        pipette.aspirate(volume+50, dilutant_buffer_well, rate=well_flow_rate)
        pipette.dispense(volume+50, sourceSolutionWell, rate=well_flow_rate)
        for iterator in range(0, 3):
    #        print ("Mixing: " + str(iterator+1))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
    #    print ("Applying fixative to sample: " + str(s))
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

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument('p300_single', pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.well(tiprack_starting_pos['tiprack_300'])


    #par2 = protocol.load_labware('par2_plastic_wide_cslps', labwarePositions.par2, 'PAR2')
    par2 = protocol.load_labware(par2_type, labwarePositions.par2, 'PAR2')
    trough12 = protocol.load_labware('axygen_12well_trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    custom_96 = protocol.load_labware('black_96', labwarePositions.antibodies_plate, '96-well-plate')

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.S1_PFA =  buffer_wells['A1']
    buffers.S2 =  buffer_wells['A2']
    buffers.PFA_S4 = buffer_wells['A3']
    buffers.MeOH =  buffer_wells['A4']
    buffers.PBS = buffer_wells['A5']
    buffers.H2 = buffer_wells['A6']
    buffers.pinkbuffer = buffer_wells['A7']
    buffers.bluebuffer = buffer_wells['A8']
    buffers.storage =  buffer_wells['A9'] 

#   biorad96 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', labwarePositions.antibodies_plate, 'biorad96')

    preblock_wells = custom_96.rows()[0]
    antibody_wells = custom_96.rows()[1]    
    BS3_wells = custom_96.rows()[2]
    rendering_wells = custom_96.rows()[3]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    #WASHING SAMPLES WITH PFA
    protocol.comment("first fix")
    washSamples(pipette_300, buffers.S1_PFA, sample_chambers, wash_volume)
    #INCUBATE FOR 10 MIN
    protocol.delay(minutes=10, msg = "first fix incubation")

    #WASHING SAMPLES WITH S2
    protocol.comment("washing in S2")
    washSamples(pipette_300, buffers.S2, sample_chambers, wash_volume, num_repeats=2)

    #WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    for i in range (len(wellslist)):
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], wash_volume)
    #INCUBATE 15 MIN
    protocol.delay(minutes=15, msg = "preblocking incubation")

    #APPLYING ANTIBODY COCKTAILS TO SAMPLES
    protocol.comment("applying antibodies")
    for i in range (len(wellslist)):
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume)
    #INCUBATING
    protocol.delay(minutes=90, msg = "staining incubation")

    #WASHING SAMPLES WITH S2
    #three individual repeats below is because they need particular incubation time between them
    protocol.comment("first washing with s2")
    washSamples(pipette_300, buffers.S2, sample_chambers, wash_volume, num_repeats=2)
    #INCUBATE FOR 10 MIN
    protocol.delay(minutes=5, msg = "first incubation in s2")

    #WASHING SAMPLES WITH S2
    #three individual repeats below is because they need particular incubation time between them
    protocol.comment("second washing with s2")
    washSamples(pipette_300, buffers.S2, sample_chambers, wash_volume, num_repeats=2)
    #INCUBATE FOR 10 MIN
    protocol.delay(minutes=5, msg = "first incubation in s2")

    #POST STAINING FIXING SAMPLES WITH PFA
    protocol.comment("second fix")
    washSamples(pipette_300, buffers.PFA_S4, sample_chambers, wash_volume)
    #INCUBATE FOR 10 MIN
    protocol.delay(minutes=5, msg="second fix incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume, num_repeats=2)

    #FIXING SAMPLES WITH Methanol
    protocol.comment("applying MeOH")
    washSamples(pipette_300, buffers.MeOH, sample_chambers, wash_volume, num_repeats=1)
    #INCUBATE FOR 5 MIN
    protocol.delay(minutes=2.5, msg="MeOH incubation")

    #FIXING SAMPLES WITH Methanol
    protocol.comment("applying MeOH")
    washSamples(pipette_300, buffers.MeOH, sample_chambers, wash_volume, num_repeats=1)
    #INCUBATE FOR 5 MIN
    protocol.delay(minutes=2.5, msg="MeOH incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume, num_repeats=2)

    #DILUTING AND APPLYING THE FIXATIVE
    for i in range (len(wellslist)):
        dilute_and_apply_fixative(pipette_300, BS3_wells[i], buffers.PBS, sample_chambers[i], wash_volume)

    protocol.comment("third fix incubation: 10min")
    protocol.delay(minutes=10, msg = "third fix incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume, 2)

    #PRE-CLEARING THE TISSUE
    for i in range (3):
        protocol.comment("tissue clearing round" + str(i+1))
        washSamples(pipette_300, buffers.bluebuffer, sample_chambers, wash_volume, num_repeats=2)
        protocol.delay(seconds=30)
        washSamples(pipette_300, buffers.pinkbuffer, sample_chambers, wash_volume, num_repeats=1)
        washSamples(pipette_300, buffers.H2, sample_chambers, wash_volume, num_repeats=1)


    #Equilibration in rendering buffer
    protocol.comment("Equilibration in rendering buffer")
    washSamples(pipette_300, buffers.pinkbuffer, sample_chambers, wash_volume)

    #RENDERING
    protocol.comment("Applying rendering solution to wells")
    for i in range (len(wellslist)):
        washSamples(pipette_300, rendering_wells[i], sample_chambers[i], wash_volume)
    #INCUBATE FOR 10 MIN
    protocol.delay(minutes=10, msg = "rendering hybridization")

    #WASH SAMPLES IN PINK BUFFER
    protocol.comment("Washing with rendering buffer")
    washSamples(pipette_300, buffers.pinkbuffer, sample_chambers, wash_volume, num_repeats=2)

    #STORAGE, washing samples every hour for 100 hours 
    for i in range(10):
        washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume/3, keep_tip=True)
        protocol.delay(minutes=90, msg = "storing samples in S4")


