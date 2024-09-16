
metadata = {
    'protocolName': 'Parhelia Dewax + H&E Skylab v1.1',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Parhelia Dewax + H&E Skylab protocol with runtime variables exposed through Opentrons UI',
    'apiLevel': '2.18'
}

def add_parameters(parameters):
    
    parameters.add_str(
    variable_name="omnistainer_type",
    display_name="Staining module type",
    choices=[
        {"display_name": "S12 slide stainer on deck/RT", "value": "omni_stainer_s12_slides"},
        {"display_name": "S12 slide stainer on Temp Mod", "value": "omni_stainer_s12_slides_with_thermosheath_on_coldplate"},
        {"display_name": "C12 coverslip stainer on deck", "value": "omni_stainer_c12_cslps"},
    ],
    default="omni_stainer_s12_slides_with_thermosheath_on_coldplate"
    )
    
    parameters.add_str(
    variable_name="type_of_96well_plate",
    display_name="Well plate type",
    choices=[
        {"display_name": "96-well PCR plate (300ul)", "value": "parhelia_skirted_96"},
        {"display_name": "Parhelia Skylab strip holder", "value": "parhelia_skirted_96_with_strips"}
    ],
    default="parhelia_skirted_96_with_strips"
    )
    
    ### VERAO VAR NAME='Well plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96', 'parhelia_skirted_96_with_strips']
    type_of_96well_plate = 'parhelia_skirted_96_with_strips'

    parameters.add_int(
        variable_name="num_samples",
        display_name="Number of samples",
        description="Number of input tissue samples",
        default=3,
        minimum=1,
        maximum=12
    )
    
    parameters.add_bool(
        variable_name="baking_prepping",
        display_name="Baking?",
        description="Bake the samples before dewaxing to improve the sample adhesion",
        default=False
    )
    
    parameters.add_int(
        variable_name="baking_temp",
        display_name="Baking temperature (C)",
        description="Baking temperature to melt the paraffin",
        default=65,
        minimum=60,
        maximum=75,
        unit="°C"
    )
    
    parameters.add_int(
        variable_name="baking_delay",
        display_name="Baking time (min)",
        description="Brining up to temp for dewaxing solution",
        default=30,
        minimum=1,
        maximum=3600,
        unit="min"
    )
    
    parameters.add_bool(
        variable_name="dewax_prepping",
        display_name="Dewaxing?",
        description="Dewaxing FFPE samples with Parhelia dewax at 72C (temp module only)",
        default=True
    )
    
    parameters.add_int(
        variable_name="dewax_temp",
        display_name="Dewaxing temperature (C)",
        description="Brining up to temp for dewaxing solution",
        default=72,
        minimum=60,
        maximum=75,
        unit="°C"
    )
    
    parameters.add_int(
        variable_name="dewax_delay",
        display_name="Dewaxing delay (minutes)",
        default=10,
        minimum=1,
        maximum=30,
        unit="min"
    )
    
    parameters.add_int(
        variable_name="alc_temp",
        display_name="Alcohol temperature (C)",
        default=50,
        minimum=20,
        maximum=60,
        unit="°C"
    )
    
    parameters.add_int(
        variable_name="room_temp",
        display_name="Room temperature (C)",
        default=22,
        minimum=20,
        maximum=25,
        unit="°C"
    )
    
    parameters.add_int(
        variable_name="wash_volume",
        display_name="Wash volume (uL)",
        default=150,
        minimum=100,
        maximum=300,
        unit = "µL"
    )
    
    parameters.add_float(
    variable_name="sample_flow_rate",
    display_name="Sample dispense flow rate",
    description="Use 0.4 for chamfered/0.2 for regular coverpads, 0.05 for imaging coverpads/coverslips",
    default=0.2,
    minimum=0.05,
    maximum=0.5
    )
   
    parameters.add_int(
        variable_name="tiprack_300_starting_pos",
        display_name="Tip Rack Start Postion",
        default=1,
        minimum=1,
        maximum=84
    )
    
    parameters.add_int(
        variable_name="hematox_delay",
        display_name="Hematoxylin Incubation Time",
        default=2,
        minimum=1,
        maximum=5,
        unit = "min"
    )
    
    parameters.add_int(
        variable_name="eosin_delay",
        display_name="Eosin Incubation Time",
        default=1,
        minimum=1,
        maximum=5,
        unit = "min"
    )
    
    parameters.add_float(
        variable_name="eosin_diff_time",
        display_name="Eosin Diff Time in Water",
        default=0.5,
        minimum=0.1,
        maximum=5,
        unit = "min"
    )
    
    parameters.add_int(
        variable_name="omnistainer_position",
        display_name="Deck Location: Stainer Module",
        default=3,
        minimum=1,
        maximum=9
    )
    
    parameters.add_int(
        variable_name="strip_plate_position",
        display_name="Parhelia Skylab strip holder",
        default=1,
        minimum=1,
        maximum=12
    )
    
    parameters.add_int(
        variable_name="tiprack_300_1_position",
        display_name="200/300 tip rack position",
        default=9,
        minimum=1,
        maximum=12
    )
    
    parameters.add_str(
    variable_name="tip_type",
    display_name="Tip type",
    choices=[
        {"display_name": "300 µL", "value": "opentrons_96_tiprack_300ul"},
        {"display_name": "200 µL filtered", "value": "opentrons_96_filtertiprack_200ul"},
    ],
    default="opentrons_96_filtertiprack_200ul"
    )
    
    parameters.add_str(
    variable_name="pipette_type",
    display_name="P300 Pipette Type",
    choices=[
        {"display_name": "P300 Single-channel (GEN2)", "value": "p300_single_gen2"},
        {"display_name": "P300 Single-channel (GEN1)", "value": "p300_single"}
    ],
    default="p300_single_gen2"
    )
    
    parameters.add_str(
    variable_name="pipette_location",
    display_name="P300 Pipette Mounting",
    choices=[
        {"display_name": "Left", "value": "left"},
        {"display_name": "Right", "value": "right"},
    ],
    default="left"
    )
    
    parameters.add_bool(
        variable_name="testmode",
        display_name="Test mode?",
        description="All delays reduced to 5 sec",
        default=False
    )
    
    
###########################LABWARE SETUP#################################

def run(protocol: protocol_api.ProtocolContext):
    
    #############EXTRACTING RUNTIME VARIABLES################################

    omnistainer_type = protocol.params.omnistainer_type

    type_of_96well_plate = protocol.params.type_of_96well_plate

    num_samples  = protocol.params.num_samples

    baking_prepping  = protocol.params.baking_prepping
    
    baking_temp = protocol.params.baking_temp

    baking_delay = protocol.params.baking_delay
 
    dewax_prepping = protocol.params.dewax_prepping
    
    dewax_temp = protocol.params.dewax_temp

    dewax_delay =  protocol.params.dewax_delay

    alc_temp =  protocol.params.alc_temp

    room_temp =  protocol.params.room_temp

    wash_volume =  protocol.params.wash_volume

    tiprack_300_starting_pos =  protocol.params.tiprack_300_starting_pos
    
    global sample_flow_rate
    sample_flow_rate =  protocol.params.sample_flow_rate

    hematox_delay =  protocol.params.hematox_delay

    eosin_delay =  protocol.params.eosin_delay

    eosin_diff_time = protocol.params.eosin_diff_time
    
    labwarePositions = Object()
    labwarePositions.strip_plate_position = protocol.params.strip_plate_position 
    labwarePositions.omnistainer = protocol.params.omnistainer_position
    labwarePositions.tiprack_300 = protocol.params.tiprack_300_1_position

    tip_type =  protocol.params.tip_type

    pipette_location =  protocol.params.pipette_location

    pipette_type =  protocol.params.pipette_type
    
    testmode =  protocol.params.testmode

    ###########################LABWARE SETUP#################################

    if 'thermosheath' in omnistainer_type and labwarePositions.omnistainer > 9:
        raise Exception("Omni-Stainer module with a thermal sheath on cannot be placed in the last row of the deck because the shutter ear will be unreachable by the pipette due to the gantry travel limits")

    if 'coldplate' in omnistainer_type:
        temp_mod = ColdPlateSlimDriver(protocol)

    omnistainer = protocol.load_labware(omnistainer_type, labwarePositions.omnistainer, 'Omni-stainer')

    tiprack_300 = protocol.load_labware(tip_type, labwarePositions.tiprack_300, 'tiprack 300ul')

    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_300])
    pipette.flow_rate.dispense = default_flow_rate*sample_flow_rate
    pipette.flow_rate.aspirate = default_flow_rate
    pipette.starting_tip = tiprack_300.wells()[tiprack_300_starting_pos - 1]

    reagents_96plate = protocol.load_labware(type_of_96well_plate, labwarePositions.strip_plate_position, '96-well-plate')
    
    buffers = Object()
    
    buffers.dewax = reagents_96plate.rows()[0][:num_samples]
    buffers.EtOH_100 = reagents_96plate.rows()[1][:num_samples]
    buffers.EtOH_70 = reagents_96plate.rows()[2][:num_samples]
    buffers.Water = reagents_96plate.rows()[3][:num_samples]
    buffers.Hematoxylin = reagents_96plate.rows()[4][:num_samples]
    buffers.Blueing = reagents_96plate.rows()[5][:num_samples]
    buffers.Eosin = reagents_96plate.rows()[6][:num_samples]
    buffers.Water_2 = reagents_96plate.rows()[7][:num_samples]

    sample_chambers = getOmnistainerWellsList(omnistainer, num_samples)

    #################PROTOCOL####################

    protocol.comment("Starting the "+ metadata["protocolName"] +" for samples:" + str(sample_chambers))
    protocol.home()
    
    closeShutter(protocol, pipette, omnistainer)
    
    # if baking:
    if baking_prepping:
        protocol.comment("baking at: " + str(baking_temp))
        temp_mod.quick_temp(baking_temp)
        safe_delay(protocol, minutes=baking_delay, msg="Baking")

    if dewax_prepping:
        dispense_slowdown_factor = 3.0
        protocol.comment("adjusting temp to {}C for dewaxing".format(dewax_temp))
        temp_mod.quick_temp(dewax_temp)

        safe_delay(protocol, minutes=dewax_delay, msg="Allowing paraffin to melt")

        protocol.comment("dewaxing")
        
        openShutter(protocol, pipette, omnistainer)

        #ultra-slow dispensing in order to fill the chamber without bubbles
        sample_flow_rate /= dispense_slowdown_factor
        
        apply_and_incubate(protocol, pipette,
        buffers.dewax, "Dewax",
        sample_chambers, wash_volume, 
        step_repeats = 2, incubation_time = dewax_delay,
        dispense_repeats=1, puncture=True, new_tip='once')

        temp_mod.quick_temp(alc_temp)
        
        protocol.comment("Alcohol washes")
        
        apply_and_incubate(protocol, pipette,
        buffers.EtOH_100, "Ethanol 100%",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = 1,
        dispense_repeats=1, puncture=True, new_tip='once')
        
        apply_and_incubate(protocol, pipette,
        buffers.EtOH_70, "Ethanol 70%",
        sample_chambers, wash_volume, 
        step_repeats = 2, incubation_time = 1,
        dispense_repeats=1, puncture=True, new_tip='once')
        
        sample_flow_rate *= dispense_slowdown_factor
        
        temp_mod.quick_temp(room_temp)
        
        apply_and_incubate(protocol, pipette,
        buffers.Water, "Water",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = 1,
        dispense_repeats=1, puncture=True, new_tip='once')
        
        protocol.comment("Hematoxylin staining")
        
        apply_and_incubate(protocol, pipette,
        buffers.Hematoxylin, "Hematoxylin",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = hematox_delay,
        dispense_repeats=2, puncture=True, new_tip='once')
        
        apply_and_incubate(protocol, pipette,
        buffers.Blueing, "Blueing",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = 1,
        dispense_repeats=2, puncture=True, new_tip='once')
        
        apply_and_incubate(protocol, pipette,
        buffers.Water, "Water",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = 1,
        dispense_repeats=1, puncture=True, new_tip='once')
        
        sample_flow_rate /= dispense_slowdown_factor
        
        apply_and_incubate(protocol, pipette,
        buffers.Eosin, "Eosin",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = eosin_delay,
        dispense_repeats=2, puncture=True, new_tip='once')
        
        apply_and_incubate(protocol, pipette,
        buffers.Water_2, "Water_2",
        sample_chambers, wash_volume,
        step_repeats = 1, incubation_time = eosin_diff_time,
        dispense_repeats=1, puncture=True, new_tip='once')
        
        apply_and_incubate(protocol, pipette,
        buffers.Water_2, "Water_2",
        sample_chambers, wash_volume,
        step_repeats = 1, incubation_time = 0,
        dispense_repeats=1, puncture=False, new_tip='once')
        
        apply_and_incubate(protocol, pipette,
        buffers.EtOH_100, "Ethanol 100%",
        sample_chambers, wash_volume, 
        step_repeats = 1, incubation_time = 0,
        dispense_repeats=1, puncture=False, new_tip='once')
        
    temp_mod.temp_off()
    protocol.comment(f"Protocol done - temperature module has been turned off")
    protocol.home()
