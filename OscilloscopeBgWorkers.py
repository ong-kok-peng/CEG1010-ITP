import requests
import OscilloscopeLabels as labels #all the oscilloscope and oscilloscope groups definitions
import queue as queue
from time import sleep

taskStatus = {"SCAN OSCILLOSCOPES": "stopped", "AUTOSET": "stopped", "DEFAULT": "stopped", "PROFICIENCY": "stopped", "SHUTDOWN": "stopped", "IDN": "stopped", "SCRAMBLE": "stopped"}
taskStatusQueue = queue.Queue()
previousTask = ""

selected_oscs = {}

def scan_connected_oscs(functionName):
    # thread to scan for oscilloscope groups that are connected, and return connected groups with all their 4 respective oscilloscope IDs

    taskStatus[functionName] = "running"
    oscilloscopes = {"oscilloscope groups": [], "oscilloscope ids": []}

    #uncomment the below to test the oscilloscope functions if scanning oscilloscopes is impossible (bypass the scanning)
    #oscilloscopes_test = {"oscilloscope groups": ["row1", "row5"], 
    #                      "oscilloscope ids": ["A1 (row1)", "A2 (row1)", "B1 (row1)", "B2 (row1)",
    #                                           "C3 (row5)", "C4 (row5)", "D3 (row5)", "D4 (row5)"]}
    
    taskStatusQueue.put((functionName, "Scanning for oscilloscope group(s)...\n\n"))

    for group in labels.PI_IPS.keys(): # loop through all the 13 group IPs, and check if their HTTP server respond
        try:
            res = requests.get(f"{labels.PI_IPS[group]}/", timeout=2)
            if res.status_code == 200:
                #row_name = res.json().get("osc_row", "?") #oscilloscope IDs for the connected group i.e. A1-"A2-B1-B2
                taskStatusQueue.put((functionName, f"✅ Oscilloscope group {group} is connected!\n"))

                oscilloscopes["oscilloscope groups"].append(group)
                for osc_id in labels.SERIAL_TO_LABEL[group].values():
                    osc_id_string = f"{osc_id} ({group})"
                    oscilloscopes["oscilloscope ids"].append(osc_id_string)
                
            else:
                taskStatusQueue.put((functionName, f"❌ Oscilloscope group {group} is not connected; with error {res.status_code}.\n"))
        except Exception:
            taskStatusQueue.put((functionName, f"❌ Oscilloscope group {group} is not connected; connection timed out.\n"))

    if len(oscilloscopes["oscilloscope groups"]) > 0:
        taskStatusQueue.put((functionName, oscilloscopes))
        taskStatusQueue.put((functionName, f"{len(oscilloscopes["oscilloscope groups"])} oscilloscope group(s) found!\n"))
    else:
        taskStatusQueue.put((functionName, "Finished scanning; no connected oscilloscope groups found!\n"))
        #taskStatusQueue.put((functionName, oscilloscopes_test)) #uncomment this if bypassing scanning to test oscilloscope functions

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def shutdown_oscs(functionName):
    # thread to shutdown the selected oscilloscope groups' raspberry pi server 

    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Shutting down the oscilloscope group(s)...\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            try:
                res = requests.post(f"{labels.PI_IPS[oscilloscope_grp]}/shutdown", timeout=2)
                if res.status_code == 200:
                    taskStatusQueue.put((functionName, f"✅ Successfully shutdown {oscilloscope_grp}!\n"))
                else:
                    err_msg = res.json().get("message", "?")
                    taskStatusQueue.put((functionName, f"❌ Failed to shutdown {oscilloscope_grp} because {err_msg}.\n"))
            except Exception:
                taskStatusQueue.put((functionName, f"🚫: Exception occured when shutting down {oscilloscope_grp}.\n"))

        taskStatusQueue.put((functionName, "Finished shutting down the oscilloscope group(s)!\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscope gorups selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def autoset(functionName):
    # thread to set "autoset" to the selected oscilloscopes

    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying AUTOSET for oscilloscope(s)...\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"In group {oscilloscope_grp}:\n")) # print this at the start of processing every group

            for oscilloscope_label in selected_oscs[oscilloscope_grp]:
                try:
                    res = requests.get(f"{labels.PI_IPS[oscilloscope_grp]}/autoset", params={"label": oscilloscope_label}, timeout=3)
                    
                    if res.json().get("status", "?") == "success":
                        taskStatusQueue.put((functionName, f"✅ AUTOSET command sent to {oscilloscope_label} successfully!\n"))
                    elif res.json().get("status", "?") == "error":
                        err_msg = res.json().get("message", "?")
                        taskStatusQueue.put((functionName, f"❌ Failed to send AUTOSET to {oscilloscope_label} because {err_msg}.\n"))

                except Exception:
                    taskStatusQueue.put((functionName, f"🚫: Exception occured when sending AUTOSET to {oscilloscope_label}.\n"))
            taskStatusQueue.put((functionName, "\n")) # print newline in the console after every group is done

        taskStatusQueue.put((functionName, "Finished applying AUTOSET for oscilloscope(s)!\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"


def default(functionName):
    # thread to set "default" to the selected oscilloscopes

    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying DEFAULT for oscilloscope(s)...\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"In group {oscilloscope_grp}:\n")) # print this at the start of processing every group

            for oscilloscope_label in selected_oscs[oscilloscope_grp]:
                try:
                    res = requests.get(f"{labels.PI_IPS[oscilloscope_grp]}/default", params={"label": oscilloscope_label}, timeout=3)
                    
                    if res.json().get("status", "?") == "success":
                        taskStatusQueue.put((functionName, f"✅ DEFAULT command sent to {oscilloscope_label} successfully!\n"))
                    elif res.json().get("status", "?") == "error":
                        err_msg = res.json().get("message", "?")
                        taskStatusQueue.put((functionName, f"❌ Failed to send DEFAULT to {oscilloscope_label} because {err_msg}.\n"))

                except Exception:
                    taskStatusQueue.put((functionName, f"🚫: Exception occured when sending DEFAULT to {oscilloscope_label}.\n"))
            taskStatusQueue.put((functionName, "\n")) # print newline in the console after every group is done

        taskStatusQueue.put((functionName, "Finished applying DEFAULT for oscilloscope(s)!\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def proficiency_test(functionName):
    # thread to set "proficiency test" to the selected oscilloscopes

    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Applying proficiency test macro for oscilloscope(s)...\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"In group {oscilloscope_grp}:\n")) # print this at the start of processing every group

            for oscilloscope_label in selected_oscs[oscilloscope_grp]:
                try:
                    res = requests.get(f"{labels.PI_IPS[oscilloscope_grp]}/proficiency", params={"label": oscilloscope_label}, timeout=3)
                    
                    if res.json().get("status", "?") == "success":
                        taskStatusQueue.put((functionName, f"✅ Proficiency test set to {oscilloscope_label} successfully!\n"))
                    elif res.json().get("status", "?") == "error":
                        err_msg = res.json().get("message", "?")
                        taskStatusQueue.put((functionName, f"❌ Failed to set proficiency test to {oscilloscope_label} because {err_msg}.\n"))

                except Exception:
                    taskStatusQueue.put((functionName, f"🚫: Exception occured when setting proficiency test to {oscilloscope_label}.\n"))
            taskStatusQueue.put((functionName, "\n")) # print newline in the console after every group is done

        taskStatusQueue.put((functionName, "Finished applying proficiency test macro for oscilloscope(s)!\n"))


    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def get_idn(functionName):
    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0:
        taskStatusQueue.put((functionName, "Showing IDN for following scope(s) . . .\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"In group {oscilloscope_grp}:\n"))

            for oscilloscope_label in selected_oscs[oscilloscope_grp]:
                try:
                    res = requests.get(f"{labels.PI_IPS[oscilloscope_grp]}/idn", params={"label": oscilloscope_label}, timeout=3)

                    if res.json().get("status", "?") == "success":
                        scope_id = res.json().get("id", "?")
                        taskStatusQueue.put((functionName, f"🔹 {oscilloscope_label}: {scope_id}\n"))
                    elif res.json().get("status", "?") == "error":
                        err_msg = res.json().get("message", "?")
                        taskStatusQueue.put((functionName, f"❌ {oscilloscope_label}: {err_msg}\n"))

                except Exception:
                    taskStatusQueue.put((functionName, f"🚫 {oscilloscope_label}: Timeout or no response.\n"))

            taskStatusQueue.put((functionName, "\n"))

        taskStatusQueue.put((functionName, "Finished retrieving IDN info.\n"))

    else: taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

def scramble(functionName):
    taskStatus[functionName] = "running"
    if len(selected_oscs) != 0: 
        taskStatusQueue.put((functionName, "Scrambling oscilloscope(s)...\n\n"))

        for oscilloscope_grp in selected_oscs.keys():
            taskStatusQueue.put((functionName, f"In group {oscilloscope_grp}:\n"))

            for oscilloscope_label in selected_oscs[oscilloscope_grp]:
                try:
                    res = requests.get(f"{labels.PI_IPS[oscilloscope_grp]}/scramble", params={"label": oscilloscope_label}, timeout=3)
                    if res.json().get("status") == "success":
                        taskStatusQueue.put((functionName, f"✅ Scrambled {oscilloscope_label} successfully!\n"))
                    else:
                        taskStatusQueue.put((functionName, f"❌ Failed to scramble {oscilloscope_label}: {res.json().get('message')}\n"))

                except Exception:
                    taskStatusQueue.put((functionName, f"🚫 Exception while scrambling {oscilloscope_label}.\n"))
            taskStatusQueue.put((functionName, "\n"))

        taskStatusQueue.put((functionName, "Scrambling done!\n"))

    else:
        taskStatusQueue.put((functionName, "No oscilloscopes selected.\n"))

    taskStatusQueue.put((functionName, "done"))
    taskStatus[functionName] = "stopped"

