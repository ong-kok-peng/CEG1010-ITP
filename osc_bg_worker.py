import requests
import labels #all the oscilloscope and oscilloscope groups definitions
import queue as queue
from time import sleep

taskStatus = {"SCAN OSCILLOSCOPES": "stopped", "AUTOSET": "stopped", "DEFAULT": "stopped", "PROFICIENCY": "stopped"}
taskStatusQueue = queue.Queue()
previousTask = ""

selected_oscs = {}

def scan_connected_oscs(functionName):
    #scan for oscilloscope groups that are connected
    taskStatus[functionName] = "running"
    oscilloscopes = {"oscilloscope groups": [], "oscilloscope ids": []}
    available_Osc_grps = list(labels.PI_IPS.keys())
    
    connected_oscilloscope_groups = ["row1", "row3", "row8"]

    if len(connected_oscilloscope_groups) != 0:
        taskStatusQueue.put((functionName, "Scanning for oscilloscope(s)...\n"))
        for group in connected_oscilloscope_groups:
            taskStatusQueue.put((functionName, f"Found oscilloscope group {group}!\n"))

            oscilloscopes["oscilloscope groups"].append(group)
            for osc_id in labels.SERIAL_TO_LABEL[group].values():
                osc_id_string = f"{osc_id} ({group})"
                oscilloscopes["oscilloscope ids"].append(osc_id_string)
            sleep(1.5)

        taskStatusQueue.put((functionName, oscilloscopes))
        taskStatusQueue.put((functionName, "Finished scanning for oscilloscope(s)!\n"))
    else:
        taskStatusQueue.put((functionName, "No connected oscilloscope groups found!\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def autoset(functionName):
    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying AUTOSET for oscilloscope(s)...\n"))
        for osc_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"{selected_oscs[osc_grp]} in {osc_grp}\n"))

            sleep(5)
            #autoset control code
            taskStatusQueue.put((functionName, "Finished applying AUTOSET for oscilloscope(s)!\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"


def default(functionName):
    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying DEAFULT for oscilloscope(s)...\n"))
        for osc_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"{selected_oscs[osc_grp]} in {osc_grp}\n"))

            sleep(5)
            #autoset control code
            taskStatusQueue.put((functionName, "Finished applying DEFAULT for oscilloscope(s)!\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def proficiency_test(functionName):
    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying proficiency test macro settings for oscilloscope(s)...\n"))
        for osc_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"{selected_oscs[osc_grp]} in {osc_grp}\n"))

            sleep(5)
            #autoset control code
            taskStatusQueue.put((functionName, "Finished applying proficiency test macro settings for oscilloscope(s)!\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"