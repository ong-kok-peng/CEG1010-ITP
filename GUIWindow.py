import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import OscilloscopeBgWorkers as obw
# from GUICallBacks import shutdownSelectedRow

class App(tk.Tk):
    def build_background(self):
        self.canvas = tk.Canvas(self, width=1203, height=650)
        self.canvas.pack()

        # Load and place background image
        bg_image = Image.open("GWInstekMDO.png")
        self.canvas.image = ImageTk.PhotoImage(bg_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)

    def build_osc_buttons(self):
        #NOTE: All buttons position bounds are based on center point

        #create autoset and default buttons
        self.autosetBtn = tk.Button(self, text="Autoset", fg="white", command=lambda: self.runOscFunction("AUTOSET", obw.autoset), bg="#0041C2", relief="raised", width=8)
        self.canvas.create_window(1150, 47, window=self.autosetBtn)

        self.defaultBtn = tk.Button(self, text="Default", fg="white", command=lambda: self.runOscFunction("DEFAULT", obw.default), bg="#575757", relief="raised", width=8)
        self.canvas.create_window(1150, 180, window=self.defaultBtn)

        #create the ch1 to ch4 buttons
        self.ch1Btn = tk.Button(self, text="CH 1", bg="lightgray", relief="raised", width=8, command=lambda: self.toggleChannel(1, self.ch1Btn))
        self.canvas.create_window(720, 379, window=self.ch1Btn)

        self.ch2Btn = tk.Button(self, text="CH 2", bg="lightgray", relief="raised", width=8, command=lambda: self.toggleChannel(2, self.ch2Btn))
        self.canvas.create_window(830, 379, window=self.ch2Btn)

        self.ch3Btn = tk.Button(self, text="CH 3", bg="lightgray", relief="raised", width=8, command=lambda: self.toggleChannel(3, self.ch3Btn))
        self.canvas.create_window(938, 379, window=self.ch3Btn)

        self.ch4Btn = tk.Button(self, text="CH 4", bg="lightgray", relief="raised", width=8, command=lambda: self.toggleChannel(4, self.ch4Btn))
        self.canvas.create_window(1047, 379, window=self.ch4Btn)


    def build_widgets(self):
        #NOTE: All UI widgets position bounds are based on center point

        #screen text console (overlay of oscilloscope screen)
        self.screen_console_frame = tk.Frame(self, width=470, height=200)
        self.screen_console_frame.pack_propagate(False) # Prevent frame from resizing to content
        self.canvas.create_window(300, 320, window=self.screen_console_frame)

        self.screen_console = tk.Text(self.screen_console_frame, state=tk.DISABLED)
        self.screen_console.pack()

        #macro panel
        self.macroPanelLabel = tk.Label(self, text="Preset Macro Settings", font=("Arial", 15), fg="white", bg="#453A42")
        self.canvas.create_window(300, 450, window=self.macroPanelLabel)

        self.proficiencyBtn = tk.Button(self, text="Proficiency\n", bg="lightgray", relief="raised", width=8, command=lambda: self.runOscFunction("PROFICIENCY", obw.proficiency_test))
        self.canvas.create_window(88, 485, window=self.proficiencyBtn)

        self.idnBtn = tk.Button(self, text="IDN\n", bg="#4A90E2", relief="raised", width=8, command=lambda: self.runOscFunction("IDN", obw.get_idn))
        self.canvas.create_window(162, 485, window=self.idnBtn)

        self.scrambleBtn = tk.Button(self, text="Scramble\n", bg="#FFA500", relief="raised", width=8, command=lambda: self.runOscFunction("SCRAMBLE", obw.scramble))
        self.canvas.create_window(235, 485, window=self.scrambleBtn)


        self.shutdownBtn = tk.Button(self, text="Shutdown\nRow", fg="white", bg="#c21807", relief="raised", width=8, command=lambda: self.runOscFunction("SHUTDOWN", obw.shutdown_oscs))
        self.canvas.create_window(530, 585, window=self.shutdownBtn)

        #oscilloscope groups selection
        self.osc_grps_frame = tk.Frame(self, width=370, height=80)
        self.osc_grps_frame.pack_propagate(False) # Prevent frame from resizing to content
        self.canvas.create_window(300, 580, window=self.osc_grps_frame)

        self.sel_osc_grps_radio = tk.Radiobutton(self.osc_grps_frame, text="Select Oscilloscope Groups", variable=self.selected_listbox, value="oscilloscope groups", command=lambda: self.toggleSelListbox())
        self.sel_osc_grps_radio.grid(row=0, column=0)

        self.sel_oscs_radio = tk.Radiobutton(self.osc_grps_frame, text="Select Oscilloscopes", variable=self.selected_listbox, value="oscilloscopes", command=lambda: self.toggleSelListbox())
        self.sel_oscs_radio.grid(row=0, column=1)

        #NOTE: the listbox binding events are only added in the toggle_sel_listbox callback
        self.osc_grps_listbox = tk.Listbox(self.osc_grps_frame, width=30, height=4, selectmode=tk.MULTIPLE, state=tk.DISABLED)
        self.osc_grps_listbox.grid(row=1, column=0)

        self.oscs_listbox = tk.Listbox(self.osc_grps_frame, width=30, height=4, selectmode=tk.MULTIPLE, state=tk.DISABLED)
        self.oscs_listbox.grid(row=1, column=1, padx=5)

        # custom circular scan oscilloscopes button
        self.scanOscsBtn = self.canvas.create_oval(30, 550, 100, 620, fill="lightgray", outline="gray", width=2)
        # Add label inside the circle
        self.scanOscsBtnText = self.canvas.create_text(65, 585, text="Scan\noscillo-\nscopes", font=("Arial", 8), justify="center")

        # Bind mouse events to simulate button press
        for tag in [self.scanOscsBtn, self.scanOscsBtnText]:
            self.canvas.tag_bind(tag, "<Button-1>", self.scanOscsBtn_on_press)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.scanOscsBtn_on_release)


    def __init__(self):
        super().__init__()
        self.title("GW Instek Oscilloscope Control")
        self.resizable(False, False)

        #shared variables
        self.selected_listbox = tk.StringVar(value="nil")
        self.channel_on_states = [False, False, False, False]

        self.build_background()
        self.build_osc_buttons()
        self.build_widgets()
        self.after(100, self.checkFunctionOutput)
        self.protocol("WM_DELETE_WINDOW", self.confirmWindowClose)