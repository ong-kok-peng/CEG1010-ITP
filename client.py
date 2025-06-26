import requests
import labels

def check_server(target):
    try:
        res = requests.get(f"{labels.PI_IPS[target]}/", timeout=2)
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

def get_scope_selection(row):
    available_labels = labels.FALLBACK_SCOPE_LABELS.get(row, [])
    scope_input = input(f"Enter label(s): {', '.join(available_labels)} or 'all'): ").strip().upper()

    if scope_input == 'ALL':
        return available_labels
    
    return [s.strip() for s in scope_input.split(",")]
    
def send_command(command_name):
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    targets = labels.PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(f"{labels.PI_IPS[target]}/{command_name}", params={"scope": i}, timeout=3)
                res_json = res.json()
                print(f"{target} - {label}: {res_json.get('message', 'No response')}")
            except Exception:
                print(f"{target} - {label} 🚫: Failed to send {command_name.upper()} command.")


def resolve_label_from_id(target, index):
    try:
        res = requests.get(f"{labels.PI_IPS[target]}/idn", params={"label": labels.FALLBACK_SCOPE_LABELS[target][index]}, timeout=3)
        res_json = res.json()
        if res_json.get("status") == "success":
            idn = res_json.get("id", "")
            serial = idn.split(",")[2].strip() if "," in idn and len(idn.split(",")) > 2 else None
            return labels.SERIAL_TO_LABEL[target].get(serial, labels.FALLBACK_SCOPE_LABELS[target][index])
    except Exception:
        pass
    return labels.FALLBACK_SCOPE_LABELS[target][index]


def get_idn():
    row = input("Select row (e.g. row4): ").strip()
    if row not in labels.PI_IPS:
        print("[!] Invalid row.")
        return
    if not check_server(row):
        return
    labels_list = get_scope_selection(row)
    for label in labels_list:
        try:
            res = requests.get(f"{labels.PI_IPS[row]}/idn", params={"label": label}, timeout=3)
            res_json = res.json()
            if res_json.get("status") == "success":
                serial = res_json.get("id", "Unknown").split(",")[2].strip()
                print(f"{row} - {label}: {serial} is active ✅")
            else:
                print(f"{row} - {label}: {res_json.get('message')}")
        except Exception:
            print(f"{row} - {label} 🚫: Oscilloscope not detected.")


def autoset():
    row = input("Select row (e.g. row4): ").strip()
    if row not in labels.PI_IPS:
        print("[!] Invalid row.")
        return
    if not check_server(row):
        return
    labels_list = get_scope_selection(row)
    for label in labels_list:
        try:
            res = requests.get(f"{labels.PI_IPS[row]}/autoset", params={"label": label}, timeout=3)
            print(f"{row} - {label}: {res.json().get('message', 'No response')}")
        except Exception:
            print(f"{row} - {label} 🚫: Failed to send AUTOSET.")

def set_coupling():
    row = input("Select row (e.g. row4): ").strip()
    if row not in labels.PI_IPS:
        print("[!] Invalid row.")
        return
    if not check_server(row):
        return
    labels_list = get_scope_selection(row)
    ch = input("Enter channel (1-4): ").strip()
    mode = input("Enter mode (DC/AC/GND): ").strip().upper()
    for label in labels_list:
        try:
            res = requests.get(f"{labels.PI_IPS[row]}/set_coupling", params={"label": label, "channel": ch, "mode": mode}, timeout=3)
            print(f"{row} - {label}: {res.json().get('message', 'No response')}")
        except Exception:
            print(f"{row} - {label} 🚫: Failed to set coupling.")


def get_coupling():
    row = input("Select row (e.g. row4): ").strip()
    if row not in labels.PI_IPS:
        print("[!] Invalid row.")
        return
    if not check_server(row):
        return
    labels_list = get_scope_selection(row)
    ch = input("Enter channel (1-4): ").strip()
    for label in labels_list:
        try:
            res = requests.get(f"{labels.PI_IPS[row]}/get_coupling", params={"label": label, "channel": ch}, timeout=3)
            print(f"{row} - {label}: Coupling = {res.json().get('coupling', 'unknown')}")
        except Exception:
            print(f"{row} - {label} 🚫: Failed to get coupling.")

def send_command(endpoint):
    row = input("Select row (e.g. row4): ").strip()
    if row not in labels.PI_IPS:
        print("[!] Invalid row.")
        return
    if not check_server(row):
        return
    labels_list = get_scope_selection(row)
    for label in labels_list:
        try:
            res = requests.get(f"{labels.PI_IPS[row]}/{endpoint}", params={"label": label}, timeout=3)
            print(f"{row} - {label}: {res.json().get('message', 'No response')}")
        except Exception:
            print(f"{row} - {label} 🚫: Command failed.")

def main():
    while True:
        print("\n--- Oscilloscope Control ---")
        print("1. IDN (identify)")
        print("2. AUTOSET")
        print("3. SET COUPLING")
        print("4. GET COUPLING")
        print("5. DEFAULT SETTINGS")
        print("6. PROFICIENCY TEST")
        print("7. EXIT")

        choice = input("Enter choice: ").strip()

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
            print("[!] Invalid choice.")

if __name__ == "__main__":
    main()