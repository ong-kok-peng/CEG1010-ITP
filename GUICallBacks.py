from threading import Thread
import queue as queue
import tkinter as tk
from tkinter import messagebox
import OscilloscopeBgWorkers as obw
import OscilloscopeLabels as labels #all the oscilloscope and oscilloscope groups definitions
# from OscilloscopeBgWorkers import shutdown_server

def toggle_channel(self, ch_index, button):
    if self.channel_on_states[ch_index-1]:
        button.config(bg="lightgray")
        print(f"Channel {ch_index} is OFF.\n")
    else:
        button.config(bg="#57d459")
        print(f"Channel {ch_index} is ON.\n")

    self.channel_on_states[ch_index-1] = not self.channel_on_states[ch_index-1]

def add_oscs_selection(self, event):
    obw.selected_oscs = {}
    oscilloscope_listbox = event.widget
    selected_indices = oscilloscope_listbox.curselection()

    if self.selected_listbox.get() == "oscilloscope groups" and len(selected_indices) > 0:
        #append all the oscilloscopes of selected groups
        for index in selected_indices:
            osc_grp_id = oscilloscope_listbox.get(index)

            obw.selected_oscs[osc_grp_id] = [] #put each group first as key
            for osc_id in labels.SERIAL_TO_LABEL[osc_grp_id].values():
                obw.selected_oscs[osc_grp_id].append(osc_id) #put all the oscilloscope ids into each group

    elif self.selected_listbox.get() == "oscilloscopes" and len(selected_indices) > 0:
        #append selected oscilloscopes of the respective groups
        for index in selected_indices:
            osc_id = oscilloscope_listbox.get(index)

            osc_id = osc_id[0:osc_id.find('(')-1] #removes the space before and brackets substring from the selected value
            for osc_grp_id in labels.SERIAL_TO_LABEL.keys():
                if osc_id in labels.SERIAL_TO_LABEL[osc_grp_id].values(): #find the corresponding group of the selected oscilloscope
                    if osc_grp_id not in obw.selected_oscs: obw.selected_oscs[osc_grp_id] = [] #if key not exist create the group key
                    obw.selected_oscs[osc_grp_id].append(osc_id)   

    #print(obw.selected_oscs) 

def toggle_sel_listbox(self):
    if self.selected_listbox.get() == "oscilloscope groups":
        #select oscilloscope groups
        if self.osc_grps_listbox['state'] == tk.DISABLED:
            self.osc_grps_listbox.config(state=tk.NORMAL); self.osc_grps_listbox.bind('<<ListboxSelect>>', self.addOscSelection)
        if self.oscs_listbox['state'] == tk.NORMAL:
            self.oscs_listbox.selection_clear(0, tk.END)
            self.oscs_listbox.config(state=tk.DISABLED); self.oscs_listbox.unbind('<<ListboxSelect>>')

    elif self.selected_listbox.get() == "oscilloscopes":
        #select oscilliscopes individually 
        if self.oscs_listbox['state'] == tk.DISABLED:
            self.oscs_listbox.config(state=tk.NORMAL); self.oscs_listbox.bind('<<ListboxSelect>>', self.addOscSelection)
        if self.osc_grps_listbox['state'] == tk.NORMAL:
            self.osc_grps_listbox.selection_clear(0, tk.END)
            self.osc_grps_listbox.config(state=tk.DISABLED); self.osc_grps_listbox.unbind('<<ListboxSelect>>')

def run_osc_function(self, functionToRun, fn):
    # if task is already running
    if obw.taskStatus[functionToRun] == "running":  
        messagebox.showinfo(title="Information", message=f"{functionToRun} is currently running.")
        return
    # prevent other tasks from running if still scanning oscilloscopes
    # also prevent scanning oscilloscopes from running if other tasks are running
    if obw.previousTask != "" and functionToRun != obw.previousTask:
        if obw.previousTask == "SCAN OSCILLOSCOPES" and obw.taskStatus[obw.previousTask] == "running":
            messagebox.showerror(title="Operation not allowed", message="Program is still scanning for oscilloscopes, please wait for it to finish.")
            return
        elif functionToRun == "SCAN OSCILLOSCOPES" and obw.taskStatus[obw.previousTask] == "running":
            messagebox.showerror(title="Operation not allowed", message="Program is running other functions, please wait for them to finish before scanning for oscilloscopes.")
            return

    newThread = Thread(target=fn, args=(functionToRun,), daemon=True)
    newThread.start()
    self.screen_console.config(state=tk.NORMAL); self.screen_console.delete("1.0", tk.END) # clear screen whenever any thread is to begin
    obw.previousTask = functionToRun

def checkFunctionOutput(self):
    try:
        while True:
            functionRunning, output = obw.taskStatusQueue.get_nowait()

            if functionRunning == "SCAN OSCILLOSCOPES":
                if type(output) is str:
                    if output == "done": self.screen_console.config(state=tk.DISABLED) #when function finishes disable the screen console
                    else: self.screen_console.insert(tk.END, output); self.screen_console.see(tk.END)
                elif type(output) is dict:
                    self.osc_grps_listbox.config(state=tk.NORMAL); self.oscs_listbox.config(state=tk.NORMAL)

                    self.osc_grps_listbox.delete(0, tk.END); self.oscs_listbox.delete(0, tk.END) #reset both select listboxes
                    self.osc_grps_listbox.insert(tk.END, *output["oscilloscope groups"]) #populate the individual oscilloscope groups
                    self.oscs_listbox.insert(tk.END, *output["oscilloscope ids"]) #populate the individual oscilloscopes

                    self.osc_grps_listbox.config(state=tk.DISABLED); self.oscs_listbox.config(state=tk.DISABLED)

            elif functionRunning == "AUTOSET" or functionRunning == "DEFAULT" or functionRunning == "PROFICIENCY":
                if type(output) is str:
                    if output == "done": self.screen_console.config(state=tk.DISABLED) #when function finishes disable the screen console
                    else: self.screen_console.insert(tk.END, output)

            elif functionRunning == "SHUTDOWN":
                if type(output) is str:
                    self.screen_console.insert(tk.END, output)
    except queue.Empty:
        pass # No message in the queue
    finally:
        self.after(100, self.checkFunctionOutput) # Poll again in 100ms

def confirmWindowClose(self):
    if "running" in obw.taskStatus.values():
        if messagebox.askyesno(title="Confirm closing application?", message="There are still task(s) running in the application, they will terminate if closed. Are you sure you want to close?"):
            self.destroy()
    else:
        self.destroy()

# def shutdownSelectedRow(self):
#     selected_indices = app.osc_grps_listbox.curselection()
#     if not selected_indices:
#         app.screen_console.config(state="normal")
#         app.screen_console.insert("end", "[!] No row selected for shutdown.\n")
#         app.screen_console.config(state="disabled")
#         return

#     selected_row = app.osc_grps_listbox.get(selected_indices[0])
#     confirm = msgbox.askyesno("Shutdown Confirmation", f"Are you sure you want to shutdown {selected_row}?")

#     if confirm:
#         threading.Thread(target=shutdown_server, args=(selected_row,), daemon=True).start()
#         app.screen_console.config(state="normal")
#         app.screen_console.insert("end", f"[→] Sending shutdown to {selected_row}...\n")
#         app.screen_console.config(state="disabled")