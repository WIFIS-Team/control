import calibration_control_toplevel as calib
import power_control as pc
import fli_controller as flic
import time

#Start power control GUI as main GUI & switch on USB hub
root,switch1,switch2= pc.run_power_gui()

#Allow for time for arduinos to connect
time.sleep(30)

#Set up Calib GUI
ser, ser2 = calib.run_calib_gui(root)
#Set up FLI/Guider Control GUI
flic.run_fli_gui(root)

#Run GUIs
root.mainloop()

#Cleaning up
ser.write(bytes('L'))
ser.write(bytes('M'))
switch1[2].state = 'OFF'
switch2[1].state = 'OFF'
switch2[2].state = 'OFF'
switch2[3].state = 'OFF'
