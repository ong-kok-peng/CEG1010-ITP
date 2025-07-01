import tkinter as tk
from PIL import Image, ImageTk
import osc_ctrl_logic as ocl
import labels #all the oscilloscope and oscilloscope groups definitions

#global variables limited to within the oscilloscope gui only

channel_on_states = [False, False, False, False]

canvas = None
sel_listbox = None
sel_osc_grps_box = None; sel_oscs_box = None
screen_console = None

# ─────────────────────────────
#  Callbacks
# ─────────────────────────────
def autoset():
    screen_console.config(state=tk.NORMAL); screen_console.delete("1.0", tk.END)
    
    if len(ocl.selected_oscs) != 0: screen_console.insert(tk.END, "Appling AUTOSET for oscilloscope(s)...\n")
    else: screen_console.insert(tk.END, "No oscilliscopes selected.\n")

    for osc_grp in ocl.selected_oscs.keys():
        screen_console.insert(tk.END, f"{ocl.selected_oscs[osc_grp]} in {osc_grp}\n")

    #autoset control logic code

    screen_console.config(state=tk.DISABLED)


def default():
    screen_console.config(state=tk.NORMAL); screen_console.delete("1.0", tk.END)
    
    if len(ocl.selected_oscs) != 0: screen_console.insert(tk.END, "Appling default settings for oscilloscope(s)...\n")
    else: screen_console.insert(tk.END, "No oscilliscopes selected.\n")

    for osc_grp in ocl.selected_oscs.keys():
        screen_console.insert(tk.END, f"{ocl.selected_oscs[osc_grp]} in {osc_grp}\n")

    #default control logic code

    screen_console.config(state=tk.DISABLED)

def proficiency_test():
    screen_console.config(state=tk.NORMAL); screen_console.delete("1.0", tk.END)
    
    if len(ocl.selected_oscs) != 0: screen_console.insert(tk.END, "Appling Proficiency Test settings macro for oscilloscope(s)...\n")
    else: screen_console.insert(tk.END, "No oscilliscopes selected.\n")

    for osc_grp in ocl.selected_oscs.keys():
        screen_console.insert(tk.END, f"{ocl.selected_oscs[osc_grp]} in {osc_grp}\n")

    #proficiency test control logic code

    screen_console.config(state=tk.DISABLED)

def scan_connected_oscs():
    screen_console.config(state=tk.NORMAL); screen_console.delete("1.0", tk.END)

    screen_console.insert(tk.END, "Scanning connected oscilloscope groups...\n")
    connected_oscs_grps = ocl.scan_Oscs_grps()
    oscs_frm_connected_grps = ocl.scan_Oscs(connected_oscs_grps)

    if (len(connected_oscs_grps) != 0):
        screen_console.insert(tk.END, "Found connected oscilloscope groups!\n")
        sel_osc_grps_box.config(state=tk.NORMAL); sel_oscs_box.config(state=tk.NORMAL)

        sel_osc_grps_box.delete(0, tk.END); sel_oscs_box.delete(0, tk.END) #reset both select listboxes

        sel_osc_grps_box.insert(tk.END, *connected_oscs_grps) #populate the individual oscilloscope groups
        sel_oscs_box.insert(tk.END, *oscs_frm_connected_grps) #populate the individual oscilloscopes

        sel_osc_grps_box.config(state=tk.DISABLED); sel_oscs_box.config(state=tk.DISABLED)
    else:
        screen_console.insert(tk.END, "No oscilloscope groups found!\n")
    screen_console.config(state=tk.DISABLED)

def add_oscs_selection(event):
    ocl.selected_oscs = {}
    select_box = event.widget
    selected_indices = select_box.curselection()

    if sel_listbox.get() == 1 and len(selected_indices) > 0:
        #append all the oscilloscopes of selected groups
        for index in selected_indices:
            osc_grp_id = select_box.get(index)
            ocl.selected_oscs[osc_grp_id] = [] #put each group first as key
            for osc_id in labels.SERIAL_TO_LABEL[osc_grp_id].values():
                ocl.selected_oscs[osc_grp_id].append(osc_id) #put all the oscilloscope ids into each group

    elif sel_listbox.get() == 2 and len(selected_indices) > 0:
        #append selected oscilloscopes of the respective groups
        for index in selected_indices:
            osc_id = select_box.get(index)
            osc_id = osc_id[0:osc_id.find('(')-1] #removes the space before and brackets substring from the selected value
            for osc_grp_id in labels.SERIAL_TO_LABEL.keys():
                if osc_id in labels.SERIAL_TO_LABEL[osc_grp_id].values(): #find the corresponding group of the selected oscilloscope
                    if osc_grp_id not in ocl.selected_oscs: ocl.selected_oscs[osc_grp_id] = [] #if key not exist create the group key
                    ocl.selected_oscs[osc_grp_id].append(osc_id)   

    #print(ocl.selected_oscs) 

def toggle_sel_listbox():
    if sel_listbox.get() == 1:
        #select oscilloscope groups
        if sel_osc_grps_box['state'] == tk.DISABLED:
            sel_osc_grps_box.config(state=tk.NORMAL); sel_osc_grps_box.bind('<<ListboxSelect>>', add_oscs_selection)
        if sel_oscs_box['state'] == tk.NORMAL:
            sel_oscs_box.selection_clear(0, tk.END)
            sel_oscs_box.config(state=tk.DISABLED); sel_oscs_box.unbind('<<ListboxSelect>>')

    elif sel_listbox.get() == 2:
        #select oscilliscopes individually 
        if sel_oscs_box['state'] == tk.DISABLED:
            sel_oscs_box.config(state=tk.NORMAL); sel_oscs_box.bind('<<ListboxSelect>>', add_oscs_selection)
        if sel_osc_grps_box['state'] == tk.NORMAL:
            sel_osc_grps_box.selection_clear(0, tk.END)
            sel_osc_grps_box.config(state=tk.DISABLED); sel_osc_grps_box.unbind('<<ListboxSelect>>')

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
    #NOTE: All buttons position bounds are based on center point

    #create autoset and default buttons
    add_button(1150, 180, "Default", default, "lightgray")
    add_button(1150, 50, "Autoset", autoset, "lightgray")

    #create the ch1 to ch4 buttons
    create_channel_button(1, 720, 379)
    create_channel_button(2, 830, 379)
    create_channel_button(3, 938, 379)
    create_channel_button(4, 1047, 379)

def build_widgets(root):
    #NOTE: All UI widgets position bounds are based on center point

    #screen text console (overlay of oscilloscope screen)
    global screen_console
    screen_console_frame = tk.Frame(root, width=470, height=200)
    screen_console_frame.pack_propagate(False) # Prevent frame from resizing to content
    canvas.create_window(300, 320, window=screen_console_frame)

    screen_console = tk.Text(screen_console_frame, state=tk.DISABLED)
    screen_console.pack()

    #macro panel
    add_label(300, 450, "Preset Macro Settings", 15, "white", "#453A42")
    add_button(88, 485, "Proficiency", proficiency_test, "orange")

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

    add_button(65, 585, "Re-Scan\noscillo-\nscopes", scan_connected_oscs, "lightgray")
    
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
    scan_connected_oscs() #scan oscilloscopes for first time
    root.mainloop()

if __name__ == "__main__":
    main()