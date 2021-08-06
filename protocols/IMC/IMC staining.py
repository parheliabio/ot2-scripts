from opentrons import protocol_api

metadata = {
    'protocolName': 'PAR2 IMC staining',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'IMC staining protocol for PAR2 instrument',
    'apiLevel': '2.7'
}

class Object:
    pass

####################MODIFIABLE RUN PARAMETERS#########################

# !!! IMPORTANT !!! Select the right PAR2 type by uncommenting one of the lines below
par2_type= 'par2s_9slides'
#par2_type= 'par2c_12coverslips'

Manual_4C = True

# !!! IMPORTANT !!! Specify the PAR2 positions where your specimens are located,
# starting with A1 (A0 is reserved for calibration and should not be used for staining)
wellslist = ['A2','A3','A4']

# !!! IMPORTANT !!! Specify the first non-empty position in the tip rack
tiprack_starting_pos = {
    "tiprack_10": 'A1',
    "tiprack_300": 'A1'
}

### change these as necessary
ab_incubation_time_minutes = 360
wash_volume = 150
ab_volume = 120

####################LABWARE LAYOUT ON DECK#########################
pipette_300_location='right'
pipette_300_GEN = 'GEN2'

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
sample_flow_rate = 0.1

####################! FUNCTIONS - DO NOT MODIFY !#########################
def washSamples(pipette, sourceSolutionWell, samples, volume, num_repeats=1, keep_tip=False):
    try:
        iter(samples)
    except TypeError:
        samples = [samples]

    if not pipette.has_tip: pipette.pick_up_tip()

    if len(samples) == 0:
        samples = [samples]

    for i in range(0, num_repeats):
        for s in samples:
            # Washing sample:
            pipette.aspirate(volume, sourceSolutionWell, rate=well_flow_rate)
            pipette.dispense(volume, s, rate=sample_flow_rate).blow_out()
            stats.volume += volume

    if not keep_tip: pipette.drop_tip()
    if keep_tip: pipette.move_to(samples[len(samples) - 1].bottom(60))

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
    buffers.PBS_Triton =  buffer_wells['A1']
    buffers.PBS =  buffer_wells['A2']
    buffers.diH20 = buffer_wells['A3']

    blocking_wells = black_96.rows()[0]
    antibody_wells = black_96.rows()[1]
    nuclear_wells = black_96.rows()[2]
    RuO4_wells = black_96.rows()[3]

    sample_chambers = []

    for well in wellslist:
        sample_chambers.append(par2.wells_by_name()[well])

    #################PROTOCOL####################
    protocol.comment("Starting the IMC staining protocol for samples:" + str(sample_chambers))

    # STEP
    protocol.comment("Washing with diH2O")
    for i in range(2):
        washSamples(pipette_300, buffers.diH20, sample_chambers, wash_volume)

    # STEP
    protocol.comment("Washing with PBS")
    for i in range(10):
        washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume)
        protocol.delay(minutes=1, msg="wash incubation")

    # STEP
    protocol.comment("blocking")
    for i in range(len(wellslist)):
        washSamples(pipette_300, blocking_wells[i], sample_chambers[i], ab_volume)
        protocol.delay(minutes=45, msg="wash incubation")

    # STEP
    protocol.comment("applying antibodies")
    for i in range(len(wellslist)):
        washSamples(pipette_300, antibody_wells[i], sample_chambers[i], ab_volume)

    if(Manual_4C):
        protocol.pause("Please move the box to 4C fridge")
    else:
        protocol.delay(minutes=ab_incubation_time_minutes, msg="staining incubation")

    # STEP
    protocol.comment("Washing with PBS Triton")
    for i in range(10):
        washSamples(pipette_300, buffers.PBS_Triton, sample_chambers, wash_volume)
        protocol.delay(minutes=1, msg="wash incubation")

    # STEP
    protocol.comment("Washing with PBS")
    for i in range(10):
        washSamples(pipette_300, buffers.PBS, sample_chambers, wash_volume)
        protocol.delay(minutes=1, msg="wash incubation")

    # STEP
    protocol.comment("applying the nuclear stain")
    for i in range(len(wellslist)):
        washSamples(pipette_300, nuclear_wells[i], sample_chambers[i], ab_volume)
    protocol.delay(minutes=40, msg="nuclear staining incubation")

    # STEP
    protocol.comment("Washing with diH2O")
    for i in range(5):
        washSamples(pipette_300, buffers.diH20, sample_chambers, wash_volume)
        protocol.delay(minutes=1, msg="wash incubation")

    # STEP
    protocol.comment("applying RuO4 counterstain")
    for i in range(len(wellslist)):
        washSamples(pipette_300, RuO4_wells[i], sample_chambers[i], ab_volume)
    protocol.delay(minutes=3, msg="RuO4 staining incubation")

    # STEP
    protocol.comment("Washing with diH2O")
    for i in range(2):
        washSamples(pipette_300, buffers.diH20, sample_chambers, wash_volume)

    #STORAGE, washing samples every hour for 10 hours
    for i in range(10):
        washSamples(pipette_300, buffers.diH20, sample_chambers, wash_volume/3, keep_tip=True)
        protocol.delay(minutes=90, msg="storing samples in storage buffer")