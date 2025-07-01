import requests
import labels #all the oscilloscope and oscilloscope groups definitions

#general global variables

selected_oscs = {}

#logic functions

def scan_Oscs_grps():
    #scan for oscilloscope groups that are connected
    connected_Osc_grps = []
    available_Osc_grps = list(labels.PI_IPS.keys())
    
    connected_Osc_grps.append(available_Osc_grps[1])
    connected_Osc_grps.append(available_Osc_grps[3])
    connected_Osc_grps.append(available_Osc_grps[8])
    connected_Osc_grps.append(available_Osc_grps[9])

    return connected_Osc_grps

def scan_Oscs(connected_Osc_grps):
    #obtain all the 4 oscilloscopes from each connected group. dont need check if they are connected
    available_Oscs = []

    for row_id in connected_Osc_grps:
        for osc_id in labels.SERIAL_TO_LABEL[row_id].values():
            osc_id_string = f"{osc_id} ({row_id})"
            available_Oscs.append(osc_id_string)

    return available_Oscs