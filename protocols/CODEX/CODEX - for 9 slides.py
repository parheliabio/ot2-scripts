from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 CODEX',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX coverslip staining protocol for EA PAR2 instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'

}


####################MODIFIABLE RUN PARAMETERS#########################

# !!! IMPORTANT !!! Select the right PAR2 type by uncommenting one of the lines below
par2_type= 'par2s_9slides'
#par2_type= 'PAR2c_30coverslips'

#The initial 1.6% PFA fixation is skipped for FFPE tissues
FFPE = False

"""
Antibody screening involves additional rendering step at the end, where the tissue is cleared and then 
fluorescent detection probes are applied to the tissue directly in the PAR2 device. 
If this option is enabled, make sure that 
    1) detector oligo mixes have been added to the 96-well plate 2)
"""
Antibody_Screening = True

""" !!! IMPORTANT !!! Specify the PAR2 positions where your specimens are located,
starting with A1 (A0 is reserved for calibration and should not be used for staining)
PAR2 'A' row positions 1-4 correspond to wells A1-A4, whereas 'B' and 'C' row positions 1-4 
correspond to wells B1-4 and C1-4, respectively """
wellslist = ['A2','A3']

# !!! IMPORTANT !!! Specify the first non-empty position in the tip rack
tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

### change these as necessary
ab_incubation_time_minutes = 180
wash_volume = 25000
ab_volume=200
extra_bottom_gap=0

#Creating a dummy class
class Object:
    pass

####################LABWARE LAYOUT ON DECK#########################
pipette_300_location='right'
pipette_300_GEN = 'GEN1'

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
sample_flow_rate = 0.4

####################! FUNCTIONS - DO NOT MODIFY !######################### 
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, dispense_bottom_gap=0, keep_tip = False):

    try:
        iter(samples)
        #print('samples are iterable')
    except TypeError:
        #print('samples arent iterable')
        samples = [samples]

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



    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette_300 = protocol.load_instrument('p300_single_gen2' if pipette_300_GEN == 'GEN2' else 'p300_single', pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.well(tiprack_starting_pos['tiprack_300'])

    par2 = protocol.load_labware(par2_type, labwarePositions.par2, 'PAR2')
    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    black_96 = protocol.load_labware('parhelia_black_96', labwarePositions.antibodies_plate, '96-well-plate')

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

    preblock_wells = black_96.rows()[0]
    antibody_wells = black_96.rows()[1]
    reagent_F_wells = black_96.rows()[2]
    rendering_wells = black_96.rows()[3]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    #################PROTOCOL####################
    protocol.comment("Starting the CODEX staining protocol for samples:" + str(sample_chambers))

    if not FFPE:
        #WASHING SAMPLES WITH PFA
        protocol.comment("first fix")
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, buffers.Hydration_PFA_1pt6pct, 0,1,extra_bottom_gap)
        washSamples(pipette_300, buffers.Hydration_PFA_1pt6pct, sample_chambers, wash_volume,1,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=10, msg = "first fix incubation")

    #WASHING SAMPLES WITH S2
    protocol.comment("washing in S2")
    washSamples(pipette_300, buffers.Staining, buffers.Staining, 0, 1,extra_bottom_gap)
    washSamples(pipette_300, buffers.Staining, sample_chambers, wash_volume, 2,extra_bottom_gap)

    #WASHING SAMPLES WITH PREBLOCK
    protocol.comment("preblocking")
    for i in range (len(wellslist)):
        washSamples(pipette_300, preblock_wells[i], sample_chambers[i], wash_volume,1,extra_bottom_gap)
    #INCUBATE
    protocol.delay(minutes=15, msg = "preblocking incubation")

    #APPLYING ANTIBODY COCKTAILS TO SAMPLES
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
    washSamples(pipette_300, buffers.Storage_PFA_4pct, buffers.Storage_PFA_4pct, 0,1,extra_bottom_gap)
    washSamples(pipette_300, buffers.Storage_PFA_4pct, sample_chambers, wash_volume,1,extra_bottom_gap)
    #INCUBATE
    protocol.delay(minutes=5, msg="incubation with fixative")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, buffers.PBS, 0,2,extra_bottom_gap)
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2,extra_bottom_gap)

    # FIXING SAMPLES WITH Methanol
    washSamples(pipette_300, buffers.MeOH, buffers.MeOH, 0,1,extra_bottom_gap)
    for i in range(2):
        protocol.comment("applying MeOH")
        washSamples(pipette_300, buffers.MeOH, sample_chambers, wash_volume,1,extra_bottom_gap)
        # INCUBATE
        protocol.delay(minutes=2.5, msg="First MeOH incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2,extra_bottom_gap)

    #DILUTING AND APPLYING THE FIXATIVE
    for i in range (len(wellslist)):
        dilute_and_apply_fixative(pipette_300, reagent_F_wells[i], buffers.PBS, sample_chambers[i], 150)

    protocol.comment("third fix incubation")
    protocol.delay(minutes=10, msg = "Reagent F incubation")

    #WASHING SAMPLES WITH PBS
    protocol.comment("PBS wash")
    washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume,2,extra_bottom_gap)

    if Antibody_Screening:
        washSamples(pipette_300, buffers.Stripping_buffer, buffers.Stripping_buffer, 0,1,extra_bottom_gap)
        washSamples(pipette_300, buffers.Screening_Buffer, buffers.Screening_Buffer, 0,1,extra_bottom_gap)
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
        for i in range (len(wellslist)):
            washSamples(pipette_300, rendering_wells[i], sample_chambers[i], wash_volume,1,extra_bottom_gap)
        #INCUBATE
        protocol.delay(minutes=10, msg = "rendering hybridization")

        #WASH SAMPLES IN 1x CODEX buffer
        protocol.comment("Washing with rendering buffer")
        washSamples(pipette_300, buffers.Screening_Buffer, sample_chambers, wash_volume,2,extra_bottom_gap)

    #STORAGE, washing samples every hour for 100 hours 
    washSamples(pipette_300, buffers.storage, buffers.storage, 0,1,extra_bottom_gap)
    for i in range(10):
        washSamples(pipette_300, buffers.storage, sample_chambers, wash_volume/3,1,extra_bottom_gap, keep_tip=True)
        protocol.delay(minutes=90, msg = "storing samples in storage buffer")