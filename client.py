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
        res = requests.get(f"{labels.PI_IPS[target]}/idn", params={"scope": index}, timeout=3)
        res_json = res.json()
        if res_json.get("status") == "success":
            idn = res_json.get("id", "")
            serial = idn.split(",")[2].strip() if "," in idn and len(idn.split(",")) > 2 else None
            # print(f"[DEBUG] Scope {index} Serial: {serial}")  # Debug line
            return labels.SERIAL_TO_LABEL[target].get(serial, labels.FALLBACK_SCOPE_LABELS[target][index])
    except Exception as e:
        print(f"[ERROR] Could not resolve label for scope {index}: {e}")
    return labels.FALLBACK_SCOPE_LABELS[target][index]


def get_idn():
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    targets = labels.PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(f"{labels.PI_IPS[target]}/idn", params={"scope": i}, timeout=3)
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
    targets = labels.PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(f"{labels.PI_IPS[target]}/autoset", params={"scope": i}, timeout=3)
                res_json = res.json()
                print(f"{target} - {label}: {res_json.get('message', 'No response')}")
            except Exception:
                print(f"{target} - {label} 🚫: Failed to send AUTOSET.")

def set_coupling():
    row = input("Select row (row1, row2 ,row3,row4, row5 or all): ").strip()
    scope_indices = get_scope_selection()
    ch = input("Enter channel (1-4): ").strip()
    mode = input("Enter mode (DC/AC/GND): ").strip().upper()
    targets = labels.PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(
                    f"{labels.PI_IPS[target]}/set_coupling",
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
    targets = labels.PI_IPS.keys() if row == 'all' else [row]

    for target in targets:
        if not check_server(target):
            continue
        for i in scope_indices:
            label = resolve_label_from_id(target, i)
            try:
                res = requests.get(
                    f"{labels.PI_IPS[target]}/get_coupling",
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