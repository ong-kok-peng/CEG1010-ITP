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
    
    connected_oscilloscope_groups_count = 0
    taskStatusQueue.put((functionName, "Scanning for oscilloscope row(s)...\n"))

    for group in labels.PI_IPS.keys():
        try:
            res = requests.get(f"{labels.PI_IPS[group]}/", timeout=2)
            if res.status_code == 200:
                row_name = res.json().get("osc_row", "?")
                taskStatusQueue.put((functionName, f"✅ Found oscilloscope group {group}: {row_name}!\n"))

                oscilloscopes["oscilloscope groups"].append(group)
                for osc_id in labels.SERIAL_TO_LABEL[group].values():
                    osc_id_string = f"{osc_id} ({group})"
                    oscilloscopes["oscilloscope ids"].append(osc_id_string)
                
                connected_oscilloscope_groups_count += 1
            else:
                taskStatusQueue.put((functionName, f"{group}: ❌ Server check failed with status code {res.status_code}.\n"))
        except Exception:
            taskStatusQueue.put((functionName, f"{group}: ❌ Server not reachable.\n"))

    if connected_oscilloscope_groups_count > 0:
        taskStatusQueue.put((functionName, oscilloscopes))
        taskStatusQueue.put((functionName, f"{connected_oscilloscope_groups_count} oscilloscope group(s) found!\n"))
    else:
        taskStatusQueue.put((functionName, "Finished scanning; no connected oscilloscope groups found!\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def autoset(functionName):
    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying AUTOSET for oscilloscope(s)...\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"In group {oscilloscope_grp}:\n"))

            for oscilloscope_label in selected_oscs[oscilloscope_grp]:
                try:
                    res = requests.get(f"{labels.PI_IPS[oscilloscope_grp]}/autoset", params={"label": oscilloscope_label}, timeout=3)
                    
                    if res.json().get("status", "?") == "success":
                        taskStatusQueue.put((functionName, f"✅ AUTOSET command sent to {oscilloscope_label} successfully!\n"))
                    elif res.json().get("status", "?") == "error":
                        err_msg = res.json().get("message", "?")
                        taskStatusQueue.put((functionName, f"❌ Unable to AUTOSET {oscilloscope_label} because {err_msg}.\n"))

                except Exception:
                    taskStatusQueue.put((functionName, f"🚫: An exception occured when sending AUTOSET to {oscilloscope_label}.\n"))
            taskStatusQueue.put((functionName, "\n")) # print newline in the console after every group is done

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