from threading import Thread
import queue, tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import osc_bg_worker as obw
import labels #all the oscilloscope and oscilloscope groups definitions

#global variables limited to within the oscilloscope gui only

channel_on_states = [False, False, False, False]

canvas = None
selected_listbox = None
osc_grps_listbox = None; oscs_listbox = None
screen_console = None

# ─────────────────────────────
#  GUI Callbacks
# ─────────────────────────────
def run_osc_function(functionName, fn):
    # if task is already running
    if obw.taskStatus[functionName] == "running":  
        messagebox.showinfo(title="Information", message=f"{functionName} is currently running.")
        return
    # prevent other tasks from running if still scanning oscilloscopes
    # also prevent scanning oscilloscopes from running if other tasks are running
    if obw.previousTask != "" and functionName != obw.previousTask:
        if obw.previousTask == "SCAN OSCILLOSCOPES" and obw.taskStatus[obw.previousTask] == "running":
            messagebox.showerror(title="Operation not allowed", message="Program is still scanning for oscilloscopes, please wait for it to finish.")
            return
        elif functionName == "SCAN OSCILLOSCOPES" and obw.taskStatus[obw.previousTask] == "running":
            messagebox.showerror(title="Operation not allowed", message="Program is running other functions, please wait for them to finish before scanning for oscilloscopes.")
            return

    newThread = Thread(target=fn, args=(functionName,), daemon=True)
    newThread.start()
    screen_console.config(state=tk.NORMAL); screen_console.delete("1.0", tk.END) # clear screen whenever any thread is to begin
    obw.previousTask = functionName

def checkFunctionOutput():
    try:
        while True:
            functionName, output = obw.taskStatusQueue.get_nowait()

            if functionName == "SCAN OSCILLOSCOPES":
                if type(output) is str:
                    if output == "done": screen_console.config(state=tk.DISABLED) #when function finishes disable the screen console
                    else: screen_console.insert(tk.END, output); screen_console.see(tk.END)
                elif type(output) is dict:
                    osc_grps_listbox.config(state=tk.NORMAL); oscs_listbox.config(state=tk.NORMAL)

                    osc_grps_listbox.delete(0, tk.END); oscs_listbox.delete(0, tk.END) #reset both select listboxes
                    osc_grps_listbox.insert(tk.END, *output["oscilloscope groups"]) #populate the individual oscilloscope groups
                    oscs_listbox.insert(tk.END, *output["oscilloscope ids"]) #populate the individual oscilloscopes

                    osc_grps_listbox.config(state=tk.DISABLED); oscs_listbox.config(state=tk.DISABLED)

            elif functionName == "AUTOSET" or functionName == "DEFAULT" or functionName == "PROFICIENCY":
                if type(output) is str:
                    if output == "done": screen_console.config(state=tk.DISABLED) #when function finishes disable the screen console
                    else: screen_console.insert(tk.END, output)
    except queue.Empty:
        pass # No message in the queue
    finally:
        root.after(100, checkFunctionOutput) # Poll again in 100ms

def confirmWindowClose():
    if "running" in obw.taskStatus.values():
        if messagebox.askyesno(title="Confirm closing application?", message="There are still task(s) running in the application, they will terminate if closed. Are you sure you want to close?"):
            root.destroy()
    else:
        root.destroy()

def add_oscs_selection(event):
    obw.selected_oscs = {}
    oscilloscope_listbox = event.widget
    selected_indices = oscilloscope_listbox.curselection()

    if selected_listbox.get() == 1 and len(selected_indices) > 0:
        #append all the oscilloscopes of selected groups
        for index in selected_indices:
            osc_grp_id = oscilloscope_listbox.get(index)

            obw.selected_oscs[osc_grp_id] = [] #put each group first as key
            for osc_id in labels.SERIAL_TO_LABEL[osc_grp_id].values():
                obw.selected_oscs[osc_grp_id].append(osc_id) #put all the oscilloscope ids into each group

    elif selected_listbox.get() == 2 and len(selected_indices) > 0:
        #append selected oscilloscopes of the respective groups
        for index in selected_indices:
            osc_id = oscilloscope_listbox.get(index)

            osc_id = osc_id[0:osc_id.find('(')-1] #removes the space before and brackets substring from the selected value
            for osc_grp_id in labels.SERIAL_TO_LABEL.keys():
                if osc_id in labels.SERIAL_TO_LABEL[osc_grp_id].values(): #find the corresponding group of the selected oscilloscope
                    if osc_grp_id not in obw.selected_oscs: obw.selected_oscs[osc_grp_id] = [] #if key not exist create the group key
                    obw.selected_oscs[osc_grp_id].append(osc_id)   

    #print(obw.selected_oscs) 

def toggle_sel_listbox():
    if selected_listbox.get() == 1:
        #select oscilloscope groups
        if osc_grps_listbox['state'] == tk.DISABLED:
            osc_grps_listbox.config(state=tk.NORMAL); osc_grps_listbox.bind('<<ListboxSelect>>', add_oscs_selection)
        if oscs_listbox['state'] == tk.NORMAL:
            oscs_listbox.selection_clear(0, tk.END)
            oscs_listbox.config(state=tk.DISABLED); oscs_listbox.unbind('<<ListboxSelect>>')

    elif selected_listbox.get() == 2:
        #select oscilliscopes individually 
        if oscs_listbox['state'] == tk.DISABLED:
            oscs_listbox.config(state=tk.NORMAL); oscs_listbox.bind('<<ListboxSelect>>', add_oscs_selection)
        if osc_grps_listbox['state'] == tk.NORMAL:
            osc_grps_listbox.selection_clear(0, tk.END)
            osc_grps_listbox.config(state=tk.DISABLED); osc_grps_listbox.unbind('<<ListboxSelect>>')

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
    global selected_listbox
    selected_listbox = tk.IntVar()

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
    add_button(1150, 180, "Default", lambda: run_osc_function("DEFAULT", obw.default), "lightgray")
    add_button(1150, 50, "Autoset", lambda: run_osc_function("AUTOSET", obw.autoset), "lightgray")

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
    add_button(88, 485, "Proficiency", lambda: run_osc_function("PROFICIENCY", obw.proficiency_test), "orange")

    #oscilloscope groups selection
    osc_grps_frame = tk.Frame(root, width=370, height=80)
    osc_grps_frame.pack_propagate(False) # Prevent frame from resizing to content
    canvas.create_window(300, 580, window=osc_grps_frame)

    sel_osc_grps_radio = tk.Radiobutton(osc_grps_frame, text="Select Oscilloscope Groups", variable=selected_listbox, value=1, command=lambda: toggle_sel_listbox())
    sel_osc_grps_radio.grid(row=0, column=0)
    sel_oscs_radio = tk.Radiobutton(osc_grps_frame, text="Select Oscilloscopes", variable=selected_listbox, value=2, command=lambda: toggle_sel_listbox())
    sel_oscs_radio.grid(row=0, column=1)

    global osc_grps_listbox, oscs_listbox
    osc_grps_listbox = tk.Listbox(osc_grps_frame, width=30, height=4, selectmode=tk.MULTIPLE, state=tk.DISABLED)
    osc_grps_listbox.grid(row=1, column=0)

    oscs_listbox = tk.Listbox(osc_grps_frame, width=30, height=4, selectmode=tk.MULTIPLE, state=tk.DISABLED)
    oscs_listbox.grid(row=1, column=1, padx=5)

    add_button(65, 585, "Re-Scan\noscillo-\nscopes", lambda: run_osc_function("SCAN OSCILLOSCOPES", obw.scan_connected_oscs), "lightgray")
    
# ─────────────────────────────
#  Program main function
# ─────────────────────────────
def main() -> None:
    global root
    root = tk.Tk()
    root.title("GW Instek Oscilloscope Control")
    root.resizable(False, False)
    init_gui_vars()
    build_background(root)
    build_osc_buttons(root)
    build_widgets(root)
    root.after(100, checkFunctionOutput)
    root.protocol("WM_DELETE_WINDOW", confirmWindowClose)
    root.mainloop()

if __name__ == "__main__":
    main()