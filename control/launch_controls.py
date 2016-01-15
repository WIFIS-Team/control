import calibration_control_toplevel as calib
import power_control as pc
import fli_controller as flic
import time

#Start power control GUI as main GUI & switch on USB hub
root,switch1,switch2= pc.run_power_gui()

#Allow for time for arduinos to connect
time.sleep(3)

#Turn on Calib GUI
calib.run_calib_gui(root)
#Turn on FLI/Guider Control GUI
flic.run_fli_gui(root)

#Run GUIs
root.mainloop()

#Need code to send off signal to arduino pins 

switch2[1].state = 'OFF'
switch2[2].state = 'OFF'
switch2[3].state = 'OFF'
