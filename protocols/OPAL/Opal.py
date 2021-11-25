
from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 Opal',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Opal staining protocol for EA PAR2 instrument',
    'apiLevel': '2.7'

}
####################MODIFIABLE RUN PARAMETERS#########################    

wellslist=['A2','B2']

tiprack_starting_pos ={
    "tiprack_10" : 'A1',
    "tiprack_300" : 'A1'
}

#Antibody incubation time
ab_incubation_time_minutes = 90

#debug mode skips all incubations, prints out additional info
debug = False

####################FIXED RUN PARAMETERS######################### 

API_VERSION= '2.7'
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.2
wash_volume = 150
USE_TROUGH = True

class Object:
    pass

####################LABWARE LAYOUT ON DECK#########################    
labwarePositions = Object()
labwarePositions.buffers_reservoir = 1
labwarePositions.par2 = 2
labwarePositions.antibodies_plate = 3
labwarePositions.tiprack_300 = 6
####################GENERAL SETUP################################

stats = Object()
stats.volume = 0

####################! FUNCTIONS - DO NOT MODIFY !######################### 
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1):

    try:
        iter(samples)
        #print('samples are iterable')
    except TypeError:
        #print('samples arent iterable')
        samples = [samples]
    
    if not pipette.has_tip:
        pipette.pick_up_tip()
    
    if(len(samples)==0):
        samples = [samples]
    print("Replacing solution on samples:" +str(samples) + " len=" + str(len(samples)))
    for i in range(0, num_repeats):
        print ("Iteration:"+ str(i))
        for s in samples:
            print ("Washing sample:" + str(s))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s.bottom(-4), rate=sample_flow_rate).blow_out()
            stats.volume += volume
    
    pipette.drop_tip()
    
def dilute_and_apply_fixative(pipette, sourceSolutionWell, dilutant_buffer_well, samples, volume):
    try:
        iter(samples)
        #print('samples are iterable')
    except TypeError:
        #print('samples arent iterable')
        samples = [samples]
    
    pipette.pick_up_tip()
    
    if(len(samples)==0):
        samples = [samples]
    print("Applying fixative to samples:" +str(samples) + " len=" + str(len(samples)))
 
    for s in samples:
        print ("Diluting fixative: " + str(s))
        pipette.aspirate(volume+50, dilutant_buffer_well, rate=well_flow_rate)
        pipette.dispense(volume+50, sourceSolutionWell, rate=well_flow_rate)
        for iterator in range(0, 3):
            print ("Mixing: " + str(iterator+1))
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, sourceSolutionWell, rate=well_flow_rate)
        print ("Applying fixative to sample: " + str(s))
        pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
        pipette.dispense(volume, s, rate=sample_flow_rate).blow_out()
        stats.volume += volume
    
    pipette.drop_tip()
    
def mix(pipette, sourceSolutionWell, volume, num_repeats):
   
    pipette.pick_up_tip()
    
    print("Mixing solution in samples:" +str(sourceSolutionWell))
    for i in range(0, num_repeats):
        print ("Iteration:"+ str(i))
        pipette.aspirate(volume, sourceSolutionWell, rate=2)
        pipette.dispense(volume, sourceSolutionWell, rate=2)
    
    pipette.drop_tip()


###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):

    if debug: print(protocol)

    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', labwarePositions.tiprack_300, "tiprack 300ul")

    if debug: print(tiprack_300)

    pipette_300 =  protocol.load_instrument('p300_single', 'right', tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.well(tiprack_starting_pos['tiprack_300'])

    if debug: print(pipette_300)

    par2_slides = protocol.load_labware('par2s_9slides_blue_v2', labwarePositions.par2, 'par2s_9slides_blue_v2')

#    trough12_def = json.loads(AXYGEN_12well_plate_DEF_JSON)

#    trough12 = protocol.load_labware_from_definition(trough12_def, labwarePositions.buffers_reservoir, '12-trough buffers reservoir')

#    custom_96_def = json.loads(CUSTOM_96well_plate_DEF_JSON)


    custom_96 = protocol.load_labware('parhelia_black_96', labwarePositions.antibodies_plate, 'parhelia_black_96')

    trough12 = protocol.load_labware('parhelia_12trough', labwarePositions.buffers_reservoir, 'parhelia_12trough')

    temp_mod = protocol.load_module('temperature module', '8')

    par2_on_heat_module=temp_mod.load_labware('par2s_9slides_blue_v2')


    if debug: print(par2)
    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.retreaval =  buffer_wells['A1']
    buffers.TBS_wash =  buffer_wells['A2']
    buffers.water =  buffer_wells['A3']
    buffers.storage = buffer_wells['A4']


    preblock_wells_cycle1 = custom_96.rows()[0]
    antibody_wells_cycle1 = custom_96.rows()[1]
    opal_polymer_cycle1 = custom_96.rows()[2]
    opal_fluorophore1 = custom_96.rows()[3]
    preblock_wells_cycle2 = custom_96.rows()[4]
    antibody_wells_cycle2 = custom_96.rows()[5]
    opal_polymer_cycle2 = custom_96.rows()[6]
    opal_fluorophore2 = custom_96.rows()[7]



    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2_on_heat_module.wells_by_name()[well])

    if debug: print(sample_chambers)

#################PROTOCOL####################
    protocol.home()

###-------------------- FIRST ROUND

#WASHING SAMPLES WITH TBS
    print("washing in TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
#    protocol.delay(minutes=5)

    print("preblocking")
    for i in range (len(wellslist)):
        washSamples(pipette_300, preblock_wells_cycle1[i], sample_chambers[i], wash_volume)
#INCUBATE 15 MIN
    print("preblocking incubation: 15 min")
    protocol.delay(minutes=15)


#    protocol.delay(minutes=60)

#APPLYING ANTIBODY COCKTAILS TO SAMPLES
    print("applying antibodies")
    for i in range (len(wellslist)):
        washSamples(pipette_300, antibody_wells_cycle1[i], sample_chambers[i], wash_volume)

#INCUBATE 90 MIN
    print("staining incubation 1.5h")
    protocol.delay(minutes=90)

#    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)

#WASHING SAMPLES WITH TBS
#three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=3)

#APPLYING OPAL polymer HRP
    print("applying opal secondary")
    for i in range (len(wellslist)):
     washSamples(pipette_300, opal_polymer_cycle1[i], sample_chambers[i], wash_volume)

#INCUBATE 10 MIN
    print("opal secondary for 10min")
    protocol.delay(minutes=10)

#three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)
    protocol.delay(minutes=3)

#Opal Signal generation
    print("Opal Signal generation")
    for i in range (len(wellslist)):
        washSamples(pipette_300, opal_fluorophore1[i], sample_chambers[i], wash_volume)

#INCUBATE 10 MIN
    print("opal fluorophore1 10min" )
    protocol.delay(minutes=10)

#WASHING SAMPLES WITH TBS
    print("washing in TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)

    washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, num_repeats=3)
    protocol.delay(minutes=3)

    temp_mod.set_temperature(95)

    print("retreaval")
    protocol.delay(minutes=40)

    temp_mod.set_temperature(25)

#    temp_mod.deactivate()

    print("cooling down")
    protocol.delay(minutes=20)

###--------cycle 2

#WASHING SAMPLES WITH TBS
    print("washing in TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
#    protocol.delay(minutes=5)

#    pipette_300.drop_tip()

    print("preblocking")
    for i in range (len(wellslist)):
        washSamples(pipette_300, preblock_wells_cycle2[i], sample_chambers[i], wash_volume)
#INCUBATE 15 MIN
    print("preblocking incubation: 15 min")
    protocol.delay(minutes=15)


#    protocol.delay(minutes=60)

#APPLYING ANTIBODY COCKTAILS TO SAMPLES
    print("applying antibodies")
    for i in range (len(wellslist)):
        washSamples(pipette_300, antibody_wells_cycle2[i], sample_chambers[i], wash_volume)

#INCUBATE 90 MIN
    print("staining incubation 1.5h")
    protocol.delay(minutes=90)

#    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)

#WASHING SAMPLES WITH TBS
#three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=3)

#APPLYING OPAL polymer HRP
    print("applying hrpsecondaryab")
    for i in range (len(wellslist)):
        washSamples(pipette_300, opal_polymer_cycle2[i], sample_chambers[i], wash_volume)

#INCUBATE 10 MIN
    print("opal secondary for 10min")
    protocol.delay(minutes=10)

#three individual repeats below is because they need particular incubation time between them
    print("washing with TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)
    protocol.delay(minutes=3)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=1)
    protocol.delay(minutes=3)

#Opal Signal generation
    print("Opal Signal generation")
    for i in range (len(wellslist)):
        washSamples(pipette_300, opal_fluorophore2[i], sample_chambers[i], wash_volume)

#INCUBATE 10 MIN
    print("opal fluorophore1 10min" )
    protocol.delay(minutes=10)

#WASHING SAMPLES WITH TBS
    print("washing in TBS")
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)
    washSamples(pipette_300, buffers.TBS_wash, sample_chambers, wash_volume, num_repeats=2)
    protocol.delay(minutes=2)
    washSamples(pipette_300, buffers.retreaval, sample_chambers, wash_volume, num_repeats=3)
    protocol.delay(minutes=3)

    temp_mod.set_temperature(95)

    print("retreaval")
    protocol.delay(minutes=40)

    temp_mod.set_temperature(25)

    temp_mod.deactivate()

    print("cooling down")
    protocol.delay(minutes=20)

#STORAGE, washing samples every hour
    for i in range (48):
        washSamples(pipette_300, buffers.storage,sample_chambers, 100)
        protocol.delay(minutes=60)
        print("total dispensed volume: ", str(stats.volume))