import requests

#general global variables

PI_IPS = {
    "Row G5-H5-G6-H6": "http://172.18.82.6:5000",
    "Row G3-H3-G4-H4": "http://172.18.82.5:5000",
    "Row F5-E5-F6-E6": "http://172.18.82.4:5000",
    "Row F3-E3-F4-E4": "http://172.18.82.7:5000"
}

# Updated serial to label mapping
SERIAL_TO_LABEL = {
    "Row G5-H5-G6-H6": {
        "GEY180247": "H5",
        "GEY180248": "H6",
        "GEY180255": "G5",
        "GES141341": "G6"
    },
    "Row G3-H3-G4-H4": {
        "GEY180245": "H3",
        "GEY180251": "G3",
        "GEY180246": "H4",
        "GEY180252": "G4"
    },
    "Row F5-E5-F6-E6": {
        "GES854611": "F5",
        "GES854606": "E5",
        "GES854615": "F6",
        "GES854612": "E6"
    },
    "Row F3-E3-F4-E4": {
        "GES141338": "F3",
        "GES141335": "E3",
        "GES854607": "F4",
        "GES141334": "E4"
    },
}

def scan_Oscs_grps():
    #scan for oscilloscope groups that are connected
    connected_Osc_grps = []
    available_Osc_grps = list(PI_IPS.keys())
    
    connected_Osc_grps.append(available_Osc_grps[1])
    connected_Osc_grps.append(available_Osc_grps[3])

    return connected_Osc_grps

def scan_Oscs(connected_Osc_grps):
    #obtain all the 4 oscilloscopes from each connected group. dont need check if they are connected
    available_Oscs = []

    for row_id in connected_Osc_grps:
        for osc_id in SERIAL_TO_LABEL[row_id]:
            available_Oscs.append(SERIAL_TO_LABEL[row_id][osc_id])

    return available_Oscs