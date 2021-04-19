from opentrons import protocol_api
import json

metadata = {
    'protocolName': 'PAR2 CODEX coverslip staining protocol',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'CODEX coverslip staining protocol for EA PAR2 instrument - from tissue rehydration to single-cycle rendering',
    'apiLevel': '2.7'
}

####################MODIFIABLE RUN PARAMETERS#########################

### !!! IMPORTANT !!! Select the right PAR2 type by uncommenting one of the lines below
par2_type= 'PAR2(s)_9slides_v1'
#par2_type= 'PAR2(s)_12coverslips_v1'

### !!! IMPORTANT !!! Specify the PAR2 positions where your specimens are located
wellslist = ['A2','A3','A4']

### !!! IMPORTANT !!! Specify the first non-empty position in the tip rack
tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

## Feel free to play with this setting and see what is the smallest volume required to get acceptably clean sample washing
wash_volume = 200

####################LABWARE LAYOUT#########################
class Object:
    pass

pipette_300_location='right'

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
sample_flow_rate = 0.2

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

    pipette_300 = protocol.load_instrument('p300_single', pipette_300_location, tip_racks = [tiprack_300])
    pipette_300.flow_rate.dispense = default_flow_rate
    pipette_300.flow_rate.aspirate = default_flow_rate
    pipette_300.starting_tip = tiprack_300.well(tiprack_starting_pos['tiprack_300'])

    par2 = protocol.load_labware(par2_type, labwarePositions.par2, 'PAR2(c)')
    trough12 = protocol.load_labware('Parhelia_12well_trough', labwarePositions.buffers_plate, '12-trough buffers reservoir')

    buffer_wells = trough12.wells_by_name()

    buffers = Object()
    buffers.White =  buffer_wells['A2']
    buffers.Blue=  buffer_wells['A1']

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    #################PROTOCOL####################
    protocol.comment("Starting the DEMO BLUE DYE protocol for samples:" + str(sample_chambers))

    print("applying the blue dye")
    #WASH SAMPLES IN WHITE BUFFER
    protocol.comment("Washing with white buffer")
    washSamples(pipette_300, buffers.White, sample_chambers,wash_volume,num_repeats=1)

    #WASH SAMPLES IN BLUE BUFFER
    protocol.comment("Washing with blue buffer")
    washSamples(pipette_300, buffers.Blue, sample_chambers,wash_volume,num_repeats=1)

    #WASH SAMPLES IN WHITE BUFFER
    protocol.comment("Washing with white buffer")
    washSamples(pipette_300, buffers.White, sample_chambers,wash_volume,num_repeats=2)


