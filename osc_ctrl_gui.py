import tkinter as tk
from PIL import Image, ImageTk
import osc_ctrl_logic as ocl

channel_on_states = [False, False, False, False]
scope_running = False

canvas = None
sel_listbox = None
sel_osc_grps_box = None; sel_oscs_box = None


# ─────────────────────────────
#  Callbacks
# ─────────────────────────────
def default():
    print("Default settings applied!\n")

def proficiency_test():
    print("Proficiency test settings applied!\n")

def rescan_oscs():
    print("Re-scanning for oscilloscopes...\n")
    scan_connected_oscs()

def autoset():
    print("Oscilloscope auto-set done!\n")

def toggle_sel_listbox():
    #print(f"Radio button {sel_listbox.get()} is clicked.")
    if sel_listbox.get() == 1:
        if sel_osc_grps_box['state'] == tk.DISABLED:
            sel_osc_grps_box.config(state=tk.NORMAL)
        if sel_oscs_box['state'] == tk.NORMAL:
            sel_oscs_box.config(state=tk.DISABLED)

    elif sel_listbox.get() == 2:
        if sel_oscs_box['state'] == tk.DISABLED:
            sel_oscs_box.config(state=tk.NORMAL)
        if sel_osc_grps_box['state'] == tk.NORMAL:
            sel_osc_grps_box.config(state=tk.DISABLED)

def toggle_run_stop(button):
    global scope_running

    try:
        if scope_running:
            button.config(text="Stop", bg="#e32727")
            print("Oscilloscope has stopped running.\n")
        else:
            button.config(text="Run", bg="#57d459")
            print("Oscilloscope is running.\n")

        scope_running = not scope_running
    except Exception as e:
        print("Error toggling run/stop:", e)

def toggle_channel(ch_index, button):
    global channel_on_states

    try:
        if channel_on_states[ch_index-1]:
            button.config(bg="lightgray")
            print(f"Channel {ch_index} is OFF.\n")
        else:
            button.config(bg="#57d459")
            print(f"Channel {ch_index} is ON.\n")

        channel_on_states[ch_index-1] = not channel_on_states[ch_index-1]
    except Exception as e:
        print(f"Error toggling channel {ch_index}:", e)


# ─────────────────────────────
#  GUI facilitators
# ─────────────────────────────
def create_channel_button(ch_index, x, y):
    label = f"CH {ch_index}"

    btn = tk.Button(root, text=label, bg="lightgray", relief="raised", width=8)
    btn.config(command=lambda: toggle_channel(ch_index, btn))
    canvas.create_window(x, y, window=btn)
    return btn

# --- Place invisible buttons on top of the image ---
def add_button(x, y, label, command, color):
    #x, y positions are relative to the button center point
    btn = tk.Button(root, text=label, command=command, bg=color, relief="raised", width=8)
    canvas.create_window(x, y, window=btn)

def add_label(x, y, value, fontsize, fg_color, bg_color):
    #x, y positions are relative to the text label center point
    label = tk.Label(root, text=value, font=("Arial", fontsize), fg=fg_color, bg=bg_color)
    canvas.create_window(x, y, window=label)

# ─────────────────────────────
#  GUI construction
# ─────────────────────────────
def init_gui_vars():
    global sel_listbox
    sel_listbox = tk.IntVar()

def build_background(root):
    global canvas
    canvas = tk.Canvas(root, width=1203, height=650)
    canvas.pack()

    # Load and place background image
    bg_image = Image.open("GWInstekMDO.png")
    canvas.image = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, anchor=tk.NW, image=canvas.image)

def build_osc_buttons(root):
    #create autoset, run and default buttons
    run_btn = tk.Button(root, text="Run", command=lambda: toggle_run_stop(run_btn), bg="lightgray", relief="raised", width=8)
    canvas.create_window(1150, 90, window=run_btn)

    add_button(1150, 180, "Default", default, "lightgray")
    add_button(1150, 50, "Autoset", autoset, "lightgray")

    #create the ch1 to ch4 buttons
    create_channel_button(1, 720, 379)
    create_channel_button(2, 830, 379)
    create_channel_button(3, 938, 379)
    create_channel_button(4, 1047, 379)

def build_widgets(root):
    #oscilloscope groups selection
    osc_grps_frame = tk.Frame(root, width=370, height=80)
    osc_grps_frame.pack_propagate(False) # Prevent frame from resizing to content
    canvas.create_window(300, 580, window=osc_grps_frame)

    sel_osc_grps_radio = tk.Radiobutton(osc_grps_frame, text="Select Oscilloscope Groups", variable=sel_listbox, value=1, command=lambda: toggle_sel_listbox())
    sel_osc_grps_radio.grid(row=0, column=0)
    sel_oscs_radio = tk.Radiobutton(osc_grps_frame, text="Select Oscilloscopes", variable=sel_listbox, value=2, command=lambda: toggle_sel_listbox())
    sel_oscs_radio.grid(row=0, column=1)

    global sel_osc_grps_box, sel_oscs_box
    sel_osc_grps_box = tk.Listbox(osc_grps_frame, width=30, height=4, selectmode=tk.MULTIPLE, state=tk.DISABLED)
    sel_osc_grps_box.grid(row=1, column=0)
    sel_oscs_box = tk.Listbox(osc_grps_frame, width=30, height=4, selectmode=tk.MULTIPLE, state=tk.DISABLED)
    sel_oscs_box.grid(row=1, column=1, padx=5)

    add_button(65, 585, "Re-Scan\noscillo-\nscopes", rescan_oscs, "lightgray")

    #macro panel
    add_label(300, 450, "Preset Macro Settings", 15, "white", "#453A42")
    add_button(88, 485, "Proficiency", proficiency_test, "orange")

# ────────────────────────────────
#  Scan connected oscilloscopes for first time and subsequently
# ────────────────────────────────
def scan_connected_oscs():
    connected_oscs_grps = ocl.scan_Oscs_grps()
    oscs_frm_connected_grps = ocl.scan_Oscs(connected_oscs_grps)

    if (len(connected_oscs_grps) != 0):
        print("Found connected oscilloscope groups!\n")
        sel_osc_grps_box.config(state=tk.NORMAL); sel_oscs_box.config(state=tk.NORMAL)

        sel_osc_grps_box.delete(0, tk.END); sel_oscs_box.delete(0, tk.END)
        sel_osc_grps_box.insert(tk.END, *connected_oscs_grps)
        sel_oscs_box.insert(tk.END, *oscs_frm_connected_grps)

        sel_osc_grps_box.config(state=tk.DISABLED); sel_oscs_box.config(state=tk.DISABLED)
    
# ─────────────────────────────
#  Program main function
# ─────────────────────────────
def main() -> None:
    global root
    root = tk.Tk()
    root.title("GW Instek Oscilloscope Control")
    init_gui_vars()
    build_background(root)
    build_osc_buttons(root)
    build_widgets(root)
    scan_connected_oscs() 
    root.mainloop()

if __name__ == "__main__":
    main()