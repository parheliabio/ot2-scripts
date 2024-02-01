from collections import defaultdict

class Table:
    def __init__(self, rows, columns, values):
        self.rows = rows
        self.columns = columns
        self.values = values
        self.populate_wells_dict()

    def __init__(self, text):
        lines = text.splitlines()
        #deleting the first line if it's empty
        if not lines[0]:
            lines.pop(0)
        #print ('lines:')
        #print(lines)
        columns = lines[0].split()
        #print ('columns:')
        #print(columns)
        lines.pop(0)
        #print ('lines after pop(0):')
        #print(lines)
        lines = [x.split() for x in lines]
        #print ('lines after splitting:')
        #print(lines)
        rows = [x.pop(0) for x in lines]
        #print ('rows:')
        #print(rows)

        values  = [[(None if y == "." else y.split("|")) for y in x] for x in lines]
        #print ('values:')
        #print(values)
        self.rows       = rows
        self.columns    = columns
        self.values     = values
        self.populate_wells_dict()

    def populate_wells_dict(self):
        self.key_vals = defaultdict()
        for i in range (len(self.rows)):
            for j in range (len(self.columns)):
                key_val = self.values[i][j]
                if key_val is None: continue
                key = key_val[0]
                if key in self.key_vals: raise Exception("Duplicate key: " + key)
                self.key_vals[key]=(i,j)

metadata = {
    'protocolName': 'Antibody panel mixing + black plate prep v0',
    'author': 'Parhelia Bio <info@parheliabio.com>',
    'description': 'Antibody panel mixing + black plate prep v0',
    'apiLevel': '2.14'
}

####################MODIFIABLE RUN PARAMETERS#########################

### VERAO VAR NAME='Panel name' TYPE=STRING
panel_name = 'test panel for PhenoCycler Fusion'

### VERAO VAR NAME='Panel source plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96']
panel_source_plate_type = 'parhelia_skirted_96'

### VERAO VAR NAME='Panel source plate position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
panel_source_plate_position = 4

### VERAO VAR NAME='Panel destination plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96']
panel_dest_plate_type = 'parhelia_skirted_96'

### VERAO VAR NAME='Panel dest plate position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
panel_dest_plate_position = 1

### VERAO VAR NAME='Reporter source plate type' TYPE=CHOICE OPTIONS=['parhelia_skirted_96']
reporter_source_plate_type = 'parhelia_skirted_96'

### VERAO VAR NAME='Reporter source plate position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
reporter_source_plate_position = 5

### VERAO VAR NAME='Reporter destination plate type' TYPE=CHOICE OPTIONS=['axygen_deepwell_96']
reporter_dest_plate_type = 'axygen_deepwell_96'

### VERAO VAR NAME='Reporter destination plate position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
reporter_dest_plate_position = 2

### VERAO VAR NAME='Buffers reservoir type' TYPE=CHOICE OPTIONS=['parhelia_12trough']
buffers_reservoir_type = 'parhelia_12trough'

### VERAO VAR NAME='Buffers reservoir position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
buffers_reservoir_position = 3

### VERAO VAR NAME='Number of Samples' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
num_samples = 4

### VERAO VAR NAME='Final ab cocktail volume per sample' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
ab_cocktail_vol_per_sample = 200

### VERAO VAR NAME='Reporter mix volume per sample per well' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
reporter_mix_volume = 200

### VERAO VAR NAME='Reporter mix volume per well' TYPE=NUMBER LBOUND=50 UBOUND=300 DECIMAL=FALSE
reporter_mix_volume = 200

####################LABWARE LAYOUT ON DECK#########################
### VERAO VAR NAME='P300 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_location = 'left'

### VERAO VAR NAME='P20 pipette mounting' TYPE=CHOICE OPTIONS=['right', 'left']
pipette_20_location = 'right'

### VERAO VAR NAME='Tip type for P300 tiprack' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_300ul', 'opentrons_96_filtertiprack_200ul']
tiprack_300_tip_type = 'opentrons_96_tiprack_300ul'

### VERAO VAR NAME='P300 tiprack position' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_position = 6

### VERAO VAR NAME='Tip type for P20 tiprack' TYPE=CHOICE OPTIONS=['opentrons_96_tiprack_20ul', 'opentrons_96_filtertiprack_20ul']
tiprack_20_tip_type = 'opentrons_96_tiprack_20ul'

### VERAO VAR NAME='P20 tiprack pos1' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 10

### VERAO VAR NAME='P20 tiprack pos2' TYPE=NUMBER LBOUND=1 UBOUND=12 DECIMAL=FALSE
tiprack_300_1_position = 10

### VERAO VAR NAME='TEST MODE (ALL INCUBATION DELAYS WILL BE SKIPPED)' TYPE=BOOLEAN
testmode = True

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
A   001|Cy3   003|Cy5   003|Cy7   007|Cy3   011|Cy5   002|Cy7   020|Cy3   019|Cy5   017|Cy7   012|Cy3   016|Cy5   045|Cy5
B   031|Cy7   044|Cy3   041|Cy5   008|Cy7   108|Cy3   .         .         .         .         .         .         .      
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
1    HLA-DR|1    CD8|0.7     CD7|0.5  
2    CD11b|1     CD9|1       CD15|1   
3    CD32|1      CD64|1      CD69|1.7 
4    CD28|0.5    CD54|1      FcRIe|2  
5    HLA-ABC|1   CD66|1.5    CD5|0.5  
6    PD-1|1      .           .        
7    .           .           .        
8    .           .           .        
9    .           .           .        
10   .           .           .        
11   .           .           .        
12   .           .           .        
13   .           .           .        
14   .           .           .        
15   .           .           .        
16   .           .           .        
"""


# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):

    ###########################LABWARE SETUP#################################
    #Tiprack
    tiprack_300 = protocol.load_labware(tiprack_300_tip_type, tiprack_300_position,
                                        'tiprack 200/300ul 1')
    #Pipette
    pipette_type = 'p300_single_gen2'
    pipette = protocol.load_instrument(pipette_type, pipette_location, tip_racks=[tiprack_300])

    buffers_trough = protocol.load_labware(buffers_reservoir_type, buffers_reservoir_position,
                                           '12-trough PBS reservoir')
    antibody_source_plate = protocol.load_labware(panel_source_plate_type, panel_source_plate_position,
                                               '96-well-plate')

    panel_dest_plate = protocol.load_labware(panel_dest_plate_type, panel_source_plate_position,
                                             '96-well-plate')

    reporter_source_plate = protocol.load_labware(panel_source_plate_type, reporter_source_plate_position,
                                                  '96-well-plate')

    reporter_dest_plate = protocol.load_labware(panel_dest_plate_type, reporter_dest_plate_position,
                                                '96-well-plate')

    panel_dest_tube = buffers_trough.wells_by_name()['A12']

    ##parse the panel
    panel_tab = Table(panel_layout)

    ##parse the reporter plate layout
    reporters = Table(reporter_source_plate_layout)

    ##parse the source plate layout
    antibody_plate_tab = Table(antibody_plate_layout)

    #mixing the panel
    ab_volumes = []
    ab_wells = []

    reporter_volumes = []
    reporter_wells = []

    for i in range(len(panel_tab.rows)):
        row = panel_tab.values[i]

        for j in range(len(row)):
            ab_titer = row[j]
            if ab_titer is None: continue
            ab      = ab_titer[0]
            titer   = float(ab_titer[1])
            if not ab in antibody_plate_tab.key_vals: raise Exception("Antibody not found in the source plate: " + ab)
            xy = antibody_plate_tab.key_vals[ab]
            ab_well = antibody_source_plate.rows()[xy[0]][xy[1]]
            ab_vol = titer * num_samples
            ab_volumes.append(ab_vol)
            ab_wells.append(ab_well)

    #################PROTOCOL####################
    protocol.comment("Starting the "+ metadata["protocolName"] +" for panel" + panel_name)

    pipette.transfer(ab_volumes, ab_wells, panel_dest_tube)
