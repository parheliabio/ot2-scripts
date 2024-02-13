metadata = {
    'protocolName': 'Antibody panel mixing + black plate prep v3',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Antibody panel mixing + black plate prep v3',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Panel mixing?' TYPE=BOOLEAN
do_panel_mixing = True

### VERAO VAR NAME='Reporter plate prep?' TYPE=BOOLEAN
do_reporter_plate_prep = True

### VERAO VAR NAME='Buffers reservoir type' TYPE=CHOICE OPTIONS=['parhelia_12trough','nest_12_reservoir_15ml']
buffers_reservoir_type = 'parhelia_12trough'

### VERAO VAR NAME='Buffers reservoir position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_reservoir_position = 6

### VERAO VAR NAME='Panel source plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96']
antibody_source_plate_type = 'parhelia_skirted_96'


### VERAO VAR NAME='Panel source plate position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
panel_source_plate_position = 1

### VERAO VAR NAME='Reporter source plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96']
reporter_source_plate_type = 'parhelia_skirted_96'

### VERAO VAR NAME='Reporter source plate position on deck' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
reporter_source_plate_position = 5

### VERAO VAR NAME='Reporter destination plate type' TYPE=CHOICE OPTIONS=['parhelia_black_96']
reporter_dest_plate_type = 'parhelia_black_96'

### VERAO VAR NAME='Reporter destination plate position on deck' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
reporter_dest_plate_position = 3

### VERAO VAR NAME='Panel destination reservoir type' TYPE=CHOICE OPTIONS=['opentrons_24_aluminumblock_nest_1.5ml_snapcap']
panel_dest_plate_type = 'opentrons_24_aluminumblock_nest_1.5ml_snapcap'

### VERAO VAR NAME='Panel destination reservoir position on deck' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
panel_dest_plate_position = 2

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 2

### VERAO VAR NAME='Reporter volume (ul)' TYPE=NUMBER LBOUND=0.1 UBOUND=10 DECIMAL=TRUE
reporter_volume = 5

### VERAO VAR NAME='Final ab cocktail volume per sample' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
ab_cocktail_vol_per_sample = 150

### VERAO VAR NAME='Reporter mix volume per well' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
reporter_mix_volume = 250

### VERAO VAR NAME='First reporter row' TYPE=CHOICE OPTIONS=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
reporter_row = 'A'

### VERAO VAR NAME='Blank row' TYPE=CHOICE OPTIONS=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
blank_row = 'H'

### VERAO VAR NAME='P20 excess volumne' TYPE=NUMBER LBOUND=0 UBOUND=1 DECIMAL=TRUE
pipette_excess_vol = 0.5

### VERAO VAR NAME='P20 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_20_location = 'right'

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_300_location = 'left'

### VERAO VAR NAME='Tip type for P300 tiprack' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tiprack_300_tip_type = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='P300 tiprack position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 9

### VERAO VAR NAME='Tip type for P20 tiprack' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_20ul', 'opentrons_96_filtertiprack_20ul']
tiprack_20_tip_type = 'opentrons_96_tiprack_20ul'

### VERAO VAR NAME='P20 tiprack pos1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_20_1_position = 4

### VERAO VAR NAME='P20 tiprack pos2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_20_2_position = 7

### VERAO VAR NAME='Antibody plate' TYPE=TABLE
antibody_plate_layout = """
    1             2             3             4             5             6             7             8             9             10            11            12         
A   HLA-DR|001    CD8|003       CD7|005       CD79a|007     CD9|011       CD15|002      CD32|020      CD64|019      CD69|018      CD28|017      CD54|012      FcRIe|016  
B   PD-1|031      HLA-ABC|044   CD66|041      CD5|008       CD11b|108     .             .             .             .             .             .             .          
C   .             .             .             .             .             .             .             .             .             .             .             .          
D   .             .             .             .             .             .             .             .             .             .             .             .          
E   .             .             .             .             .             .             .             .             .             .             .             .          
F   .             .             .             .             .             .             .             .             .             .             .             .          
G   .             .             .             .             .             .             .             .             .             .             .             .          
H   .             .             .             .             .             .             .             .             .             .             .             .          
"""

### VERAO VAR NAME='Reporter plate' TYPE=TABLE
reporter_source_plate_layout = """
    1         2         3         4         5         6         7         8         9         10        11        12     
A   001|Cy3   003|Cy5   005|Cy7   007|Cy3   011|Cy5   002|Cy7   020|Cy3   019|Cy5   017|Cy3   012|Cy5   016|Cy7   045|Cy5
B   031|Cy3   044|Cy3   041|Cy5   008|Cy7   108|Cy3   018|Cy7   .         .         .         .         .         .      
C   .         .         .         .         .         .         .         .         .         .         .         .      
D   .         .         .         .         .         .         .         .         .         .         .         .      
E   .         .         .         .         .         .         .         .         .         .         .         .      
F   .         .         .         .         .         .         .         .         .         .         .         .      
G   .         .         .         .         .         .         .         .         .         .         .         .      
H   .         .         .         .         .         .         .         .         .         .         .         .      
"""

### VERAO VAR NAME='Panel' TYPE=TABLE
panel_layout = """
    Cy3         Cy5         Cy7      
1   .           .           .        
2   HLA-DR|1    CD8|0.7     CD7|0.5  
3   CD11b|1     CD9|1       CD15|1   
4   CD32|1      CD64|1      CD69|1.7 
5   CD28|0.5    CD54|1      FcRIe|2  
6   HLA-ABC|1   CD66|1.5    CD5|0.5  
7   PD-1|1      .           .        
8   .           .           .        
"""

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):

    ###########################LABWARE SETUP#################################
    #Tiprack
    tiprack_300 = protocol.load_labware(tiprack_300_tip_type, tiprack_300_position, 'tiprack 200/300ul')

    tiprack_20_1 = protocol.load_labware(tiprack_20_tip_type, tiprack_20_1_position, 'tiprack 20ul #1')
    tiprack_20_2 = protocol.load_labware(tiprack_20_tip_type, tiprack_20_2_position, 'tiprack 20ul #2')

    #Pipette P20
    pipette_20_type = 'p20_single_gen2'
    pipette_20 = protocol.load_instrument(pipette_20_type, pipette_20_location, tip_racks=[tiprack_20_1, tiprack_20_2])

    #Pipette P300
    pipette_300_type = 'p300_single_gen2'
    pipette_300 = protocol.load_instrument(pipette_300_type, pipette_300_location, tip_racks=[tiprack_300])

    buffers_trough = protocol.load_labware(buffers_reservoir_type, buffers_reservoir_position, '12-trough buffers reservoir')

    antibody_source_plate = protocol.load_labware(antibody_source_plate_type, panel_source_plate_position, 'Antibody source plate')

    panel_dest_plate = protocol.load_labware(panel_dest_plate_type, panel_dest_plate_position, 'Panel destination plate')

    reporter_source_plate = protocol.load_labware(reporter_source_plate_type, reporter_source_plate_position, 'Reporter source plate')

    reporter_dest_plate = protocol.load_labware(reporter_dest_plate_type, reporter_dest_plate_position, 'Reporter destination plate')

    row_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    #flattening the rows list of lists in order to get a list of wells ordered by row
    black_plate_wells = list(chain.from_iterable(reporter_dest_plate.rows()[row_names.index(reporter_row):]))

    #flattening the rows list of lists in order to get a list of wells ordered by row
    blank_wells = list(chain.from_iterable(reporter_dest_plate.rows()[row_names.index(blank_row):]))[0:2]

    panel_dest_tube = panel_dest_plate.wells_by_name()['A1']

    reporter_buffer = buffers_trough.wells_by_name()['A1']

    ##parse the panel
    panel_tab = Table(panel_layout)


    black_plate_wells = black_plate_wells[:len(panel_tab.rows)]

    ##parse the reporter plate layout
    reporter_plate_tab = Table(reporter_source_plate_layout)

    ##parse the source plate layout
    antibody_plate_tab = Table(antibody_plate_layout)

    #mixing the panel
    ab_volumes = []
    ab_wells = []

    reporter_source_wells = []
    reporter_dest_wells = []
    reporter_mix_volumes_per_well = []

    for cyc in range(len(panel_tab.rows)):
        row = panel_tab.values[cyc]
        reporter_mix_volumes_per_well.append(reporter_mix_volume)
        for ch in range(len(row)):
            ab_titer = row[ch]
            if ab_titer is None: continue
            ab      = ab_titer[0]

            
            if len(ab_titer)==1:
                 raise Exception("Titer is missing for the antibody in the panel: " + ab)
            
            titer   = float(ab_titer[1])
            if ab not in antibody_plate_tab.xy_index:
                raise Exception("Antibody not found in the source plate: " + ab)


            x,y = antibody_plate_tab.xy_index[ab]
            ab_well = antibody_source_plate.rows()[x][y]
            ab_vol = titer * num_samples - pipette_excess_vol
            ab_volumes.append(ab_vol)
            ab_wells.append(ab_well)

            if len(antibody_plate_tab.values[x][y])==1:
                 raise Exception("Barcode not specified for the antibody: " + ab)

            barcode = antibody_plate_tab.values[x][y][1]

            if barcode not in reporter_plate_tab.xy_index:
                raise Exception("Barcode not found in the reporter plate: " + barcode)
            x,y = reporter_plate_tab.xy_index[barcode]

            if len(reporter_plate_tab.values[x][y])==1:
                 raise Exception("Fluor not specified for the barcode: " + barcode)
            
            fluor = reporter_plate_tab.values[x][y][1]

            if fluor != panel_tab.columns[ch]:
                raise Exception("Antibody assigned to the wrong channel: " + ab + ", fluor: " + fluor + ", barcode:"
                                + barcode + ", ch:" + panel_tab.columns[ch])

            reporter_source_wells.append(reporter_source_plate.rows()[x][y])
            reporter_dest_wells.append(black_plate_wells[cyc])
            reporter_mix_volumes_per_well[cyc]-=reporter_mix_volume


    #################PROTOCOL####################
    protocol.comment("Starting the "+ metadata["protocolName"] )


    if do_panel_mixing:
        protocol.comment("Puncturing the antibody wells")
        puncture_wells(pipette_300, ab_wells)
        protocol.comment("Sampling the antibodies")
        pipette_20.transfer(ab_volumes, ab_wells, panel_dest_tube, new_tip="always", mix_after=(3, 10), disposal_vol=0)

    if do_reporter_plate_prep:
        protocol.comment("Dispensing the reporter buffer into the black plate")
        pipette_300.transfer(reporter_mix_volumes_per_well, reporter_buffer, black_plate_wells, new_tip="once", disposal_vol=0)
        protocol.comment("Filling the blanks")
        pipette_300.transfer(reporter_mix_volume, reporter_buffer, blank_wells, new_tip="once", disposal_vol=0)
        protocol.comment("Puncturing the wells")
        puncture_wells(pipette_300, reporter_source_wells)
        protocol.comment("Pipetting the reporters")
        pipette_20.transfer(reporter_volume-pipette_excess_vol, reporter_source_wells, reporter_dest_wells, new_tip="always", disposal_vol=0)
        protocol.comment("Mixing the reporters")
        pipette_300.transfer(reporter_mix_volume/2, black_plate_wells, black_plate_wells, mix_before=(2, reporter_mix_volume/2), new_tip="always", disposal_vol=0)

