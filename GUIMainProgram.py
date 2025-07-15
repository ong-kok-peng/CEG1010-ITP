from GUIWindow import App
import GUICallBacks as callbacks  # import once; we’ll monkey-patch methods

# GUI callback events binding
App.toggleChannel = callbacks.toggle_channel
App.toggleSelListbox = callbacks.toggle_sel_listbox
App.addOscSelection = callbacks.add_oscs_selection
App.runOscFunction = callbacks.run_osc_function
App.checkFunctionOutput = callbacks.checkFunctionOutput
App.confirmWindowClose = callbacks.confirmWindowClose

if __name__ == "__main__":
    App().mainloop()