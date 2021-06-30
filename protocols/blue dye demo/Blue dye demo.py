from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 CODEX coverslip staining protocol',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia Demo protocol that iteratively exchanges trypan blue dye and clear buffer on one or several samples',
    'apiLevel': '2.9'
}

####################MODIFIABLE RUN PARAMETERS#########################

# !!! IMPORTANT !!! Select the right PAR2 type by uncommenting one of the lines below
#par2_type= 'par2s_9slides'
par2_type= 'par2c_12coverslips'

# !!! IMPORTANT !!! Specify the PAR2 positions where your specimens are located,
# starting with A1 (A0 is reserved for calibration and should not be used for staining)
wellslist = ['A1','A2','A3']

# !!! IMPORTANT !!! Specify the first non-empty position in the tip rack
tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

## Feel free to play with this setting and see what is the smallest volume required to get acceptably clean sample washing
wash_volume = 200

####################LABWARE LAYOUT#########################
class Object:
    pass

pipette_300_location='left'
pipette_300_GEN = 'GEN2'

labwarePositions = Object()
labwarePositions.buffers_plate = 1
labwarePositions.par2 = 2
labwarePositions.tiprack_300 = 6

####################GENERAL SETUP################################
stats = Object()
stats.volume = 0
debug = False

####################FIXED RUN PARAMETERS#########################
default_flow_rate = 50
well_flow_rate = 5
sample_flow_rate = 0.1

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
    if keep_tip: pipette.move_to(samples[len(samples)-1].bottom(60))


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

    buffer_wells = trough12.wells_by_name()

    buffers = Object()

    buffers.clear=  buffer_wells['A1']
    buffers.blue =  buffer_wells['A2']

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    #################PROTOCOL####################
    protocol.comment("Starting the DEMO BLUE DYE protocol for samples:" + str(sample_chambers))

    #WASH SAMPLES WITH BLUE BUFFER
    protocol.comment("Washing with blue buffer")
    washSamples(pipette_300, buffers.blue, sample_chambers, wash_volume, num_repeats=1)

    #WASH SAMPLES WITH CLEAR BUFFER
    protocol.comment("Washing with clear buffer")
    washSamples(pipette_300, buffers.clear, sample_chambers, wash_volume, num_repeats=2)

    #WASH SAMPLES WITH BLUE BUFFER
    protocol.comment("Washing with blue buffer")
    washSamples(pipette_300, buffers.blue, sample_chambers, wash_volume, num_repeats=1)

    #WASH SAMPLES WITH CLEAR BUFFER
    protocol.comment("Washing with blue buffer")
    washSamples(pipette_300, buffers.clear, sample_chambers, wash_volume, num_repeats=1)

