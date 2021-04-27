from opentrons import protocol_api


metadata = {
    'protocolName': 'Opentrons Logo',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.9'
    }


def run(protocol):
    tips = [protocol.load_labware('opentrons_96_tiprack_300ul', '1', 'Opentrons Tips')]

    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=tips)

    pipette.well_bottom_clearance.dispense = 5

    # create plates and pattern list
    output = protocol.load_labware('parhelia_black_96', '3', 'Destination Plate')

    dye_container = protocol.load_labware('parhelia_12trough', '2', 'Dye Source')

    # Well Location set-up
    dye1_wells = ['A5', 'A6', 'A8', 'A9', 'B4', 'B10', 'C3', 'C11', 'D3',
                  'D11', 'E3', 'E11', 'F3', 'F11', 'G4', 'G10',
                  'H5', 'H6', 'H7', 'H8', 'H9']

    dye2_wells = ['C7', 'D6', 'D7', 'D8', 'E5', 'E6', 'E7', 'E8',
                  'E9', 'F5', 'F6', 'F7', 'F8', 'F9', 'G6', 'G7', 'G8']

    dye2 = dye_container['A1']
    dye1 = dye_container['A2']

    dye_vol = 50

    pipette.distribute(
        dye_vol,
        dye1,
        [output.wells_by_name()[well_name] for well_name in dye1_wells],
        new_tip='once')

    pipette.distribute(
        dye_vol,
        dye2,
        [output.wells_by_name()[well_name] for well_name in dye2_wells],
        new_tip='once')
