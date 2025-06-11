import requests

PI_IPS = {
    "row1": "http://172.18.82.5:5000",
    "row2": "http://172.18.82.6:5000",
    "row4": "http://172.18.82.4:5000",
    "row5": "http://172.18.82.7:5000"
}

FALLBACK_SCOPE_LABELS = {
    "row1": ["Scope 0", "Scope 1", "Scope 2", "Scope 3"],
    "row2": ["Scope 0", "Scope 1", "Scope 2", "Scope 3"],
    "row4": ["Scope 0", "Scope 1", "Scope 2", "Scope 3"],
    "row5": ["Scope 0", "Scope 1", "Scope 2", "Scope 3"]
}

# Updated serial to label mapping
SERIAL_TO_LABEL = {
    "row1": {
        "GEY180247": "H5",
        "GEY180248": "H6",
        "GEY180255": "G5",
        "GES141341": "G6"
    },
    "row2": {
        "GEY180245": "H3",
        "GEY180251": "G3",
        "GEY180246": "H4",
        "GEY180252": "G4"
    },
    "row4": {
        "GES854611": "F5",
        "GES854606": "E5",
        "GES854615": "F6",
        "GES854612": "E6"
    },
    "row5": {
        "GES141338": "F3",
        "GES141335": "E3",
        "GES854607": "F4",
        "GES141334": "E4"
    },
}

def check_server(target):
    try:
        res = requests.get(f"{PI_IPS[target]}/", timeout=2)
        if res.status_code == 200:
            row_name = res.json().get("osc_row", "?")
            print(f"{target}: ✅ {row_name} is active.")
            return True
        else:
            print(f"{target}: ❌ Root check failed with status code {res.status_code}.")
            return False
    except Exception:
        print(f"{target}: ❌ Server not reachable.")
        return False

def get_scope_selection():
    scope = input("Enter scope number (0, 1, 2, 3 or 'all'): ").strip()
    if scope == 'all':
        return list(range(4))
    try:
        return [int(scope)]
    except ValueError:
        print("[!] Invalid scope input.")
        return []
    
def send_command(command_name):
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    targets = PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(f"{PI_IPS[target]}/{command_name}", params={"scope": i}, timeout=3)
                res_json = res.json()
                print(f"{target} - {label}: {res_json.get('message', 'No response')}")
            except Exception:
                print(f"{target} - {label} 🚫: Failed to send {command_name.upper()} command.")


def resolve_label_from_id(target, index):
    try:
        res = requests.get(f"{PI_IPS[target]}/idn", params={"scope": index}, timeout=3)
        res_json = res.json()
        if res_json.get("status") == "success":
            idn = res_json.get("id", "")
            serial = idn.split(",")[2].strip() if "," in idn and len(idn.split(",")) > 2 else None
            # print(f"[DEBUG] Scope {index} Serial: {serial}")  # Debug line
            return SERIAL_TO_LABEL[target].get(serial, FALLBACK_SCOPE_LABELS[target][index])
    except Exception as e:
        print(f"[ERROR] Could not resolve label for scope {index}: {e}")
    return FALLBACK_SCOPE_LABELS[target][index]


def get_idn():
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    targets = PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(f"{PI_IPS[target]}/idn", params={"scope": i}, timeout=3)
                res_json = res.json()
                if res_json.get("status") == "success":
                    # print(f"{target} - {label}: {res_json.get('id', '')}")
                    idn = res_json.get("id", "")
                    serial = idn.split(",")[2].strip() if "," in idn and len(idn.split(",")) > 2 else None
                    print(f"{target} - {label}: {serial} is active ✅")  # Debug line
                else:
                    print(f"{target} - {label} : {label} is unavailable ❌")
            except Exception:
                print(f"{target} - {label} 🚫: Oscilloscope not detected.")

def autoset():
    row = input("Select row (row1,row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    targets = PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(f"{PI_IPS[target]}/autoset", params={"scope": i}, timeout=3)
                res_json = res.json()
                print(f"{target} - {label}: {res_json.get('message', 'No response')}")
            except Exception:
                print(f"{target} - {label} 🚫: Failed to send AUTOSET.")

def set_coupling():
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    ch = input("Enter channel (1-4): ").strip()
    mode = input("Enter mode (DC/AC/GND): ").strip().upper()
    targets = PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(
                    f"{PI_IPS[target]}/set_coupling",
                    params={"scope": i, "channel": ch, "mode": mode}, timeout=3
                )
                res_json = res.json()
                print(f"{target} - {label}: {res_json.get('message', 'No response')}")
            except Exception:
                print(f"{target} - {label} 🚫: Failed to send coupling.")

def get_coupling():
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    ch = input("Enter channel (1-4): ").strip()
    targets = PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(
                    f"{PI_IPS[target]}/get_coupling",
                    params={"scope": i, "channel": ch}, timeout=3
                )
                res_json = res.json()
                print(f"{target} - {label}: Coupling = {res_json.get('coupling', 'unknown')}")
            except Exception:
                print(f"{target} - {label} 🚫: Failed to query coupling.")

def main():
    while True:
        print("1. IDN (identify)")
        print("2. AUTOSET")
        print("3. SET COUPLING")
        print("4. GET COUPLING")
        print("5. DEFAULT SETTINGS")
        print("6. PROFICIENCY TEST")
        print("7. EXIT")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            get_idn()
        elif choice == '2':
            autoset()
        elif choice == '3':
            set_coupling()
        elif choice == '4':
            get_coupling()
        elif choice == '5':
            send_command("default")
        elif choice == '6':
            send_command("proficiency")
        elif choice == '7':
            print("Exiting.")
            break

        else:
            print("[!] Option not recognized.")

if __name__ == "__main__":
    main()