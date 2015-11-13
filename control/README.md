# WIFIS System Control Scripts

## WIFIS Motor Controller
This is a GUI module used to control the motors for WIFIS. Three motors are currently installed.

### How to use
#### Starting up
Using the terminal, clone the repository, then navigate to the directory containing the module (under `/wherever_you_keep_your_code/WIFIS-Code/control/`). Enter the command

> ```python motor_controller.py```

to start up the GUI module. Immediately, you should see three columns of buttons – one for each motor.

#### Moving the motors
The first thing to remember is that the position and movement of motors is measured in *steps*, where **1000 steps equals one revolution**. Positive steps are in the clockwise direction, negative in the counterclockwise direction (e.g., –1000 steps equals one counterclockwise revolution). Position 0 is the initial position of the motor when it was powered on (also called the *home* position).

The various buttons are pretty straightforward:
* **Set** | sets the speed of revolution at the selected rate entered in the field above (default = 1000)
* **Step** | moves the motor by the selected number of steps (1 revolution = 1000 steps)
* **Home** | returns the motor to the home position (i.e., position 0)
* **Fwd** | (Forward) continuously rotates the motor clockwise at the determined speed
* **Rev** | (Reverse) continuously rotates the motor counterclockwise at the determined speed
* **Stop** | ceases the motor's operation, but keeps it on
* **Off** | turns the motor off

At a given moment, each motor can be in one of four states: **ON**, **MOVE**, **HOME**, or **OFF**. Note that the motor will not execute any "move" commands while it is already in a MOVE or HOME state. Click the Stop button to return it to the ON state prior to sending additional commands.

#### Exiting
Simply close the module – no special commands required`*`. Remember to shut off the power!

`*`*Optional*: you may wish to return the motor to the home position before exiting. This ensures that position 0 – the home position – is in the same place every time the motor is powered on. **There is no way to save the position internally**.

## WIFIS FLI Controller

### Dependencies

* Chimera
* Chimera-FLI
* Python-FLI
* FLI Linux Drivers
* FLI SDK

Install the FLI Linux Drivers and FLI SDK from FLI first. Then clone the repos of Chimera, Python-FLI, and Chimera-FLI and install in that order. The GUI should then work.

### Starting

To start the GUI navigate to WIFIS-Code/control and run,

> '''python fli_controller.py'''

### Operation Notes

* The focuser has a maximum extent of 7000 steps or roughly a 1/3 inch
* The CCD can get hot quickly so minimize operation time when not being cooled:


## Web Power Switch Control
This is a gui to control the two web power bars that will be powering most componants of WIFIS. NOTE: these can also be controled via a web browser on the control computer by going to their IP addresses (currently 192.168.0.110 for Power Control #1 and 192.168.0.120 for Power Control #2)

### How to use
Make sure you have both ''power_control.py'' and ''dlipower.py''. Both are saved in the directory ''Power_Control''

Run ''power_control.py''.

A gui window will apear, listing each of the plugs by a number and what should be plugged into it. Each plug has a button that toggles the power to that plug on and off. The status should update after a pause if the power is toggled elsewhere (example ''calibration_control_toplevel.py'' described later does this).

IMPORTANT NOTE: This code lags a bit so be sure to wait a few seconds after toggling the power for it to actually take effect. 


## Calibration Unit Control
This is a gui that can be used to easily perform calibration functions. Specifically it controls the two flip mirrors in the calibration unit, the arc-lamp and Integrating sphere power supplies and turns on and off the plugs powering each componant as needed. NOTE: currently this turns the sphere on and off by controling the power, I will update this soon to use a second arduino instead. 

### How to use

Make sure have both ''calibration_control_toplevel.py'' and ''dlipower.py'' (which can be found in the directories 'Calibration_Control' and 'Power_Control' respectively).

The Gui is split vertically into two halves. The left contains a series of buttons which should be used to conrol the calibration unit in most scenarios. Buttons apear eather depressed or raised, this shows which buttons should be pushed at any given time. The Right half is used to monitor the status of and control individual elements should this be needed. NOTE: for normal operations one shouldn't need to control elements using the buttons on the right. 

####The function of the various buttons is descirbed below:
#####Left Side
* **Enter Calibration Mode** | This is the first button that should be pushed. Turns on power to the flippers, turns on power to the Integrating sphere (doesn't currently do this but should in a soon updated version), moved the mirror mounted on WIFIS into the calibration position that feeds light from the calibration unit into the instrument and blocks light from the telescope. 
* **Prepare to take Flats ** | moves the mirror in the calibration box to feed light from the integrating sphere into WIFIS, turns on the integrating sphere (right now does this by the power control, but will update to use ttl)
* **Finished taking Flats** | turns off the integrating sphere (right now does this by the power control, but will update to use ttl)
* **Prepare to take Arcs** | moves mirror in calibration box to feed light from arc lamp into WIFIS, turns arc lamp on.
* **Finished taking Arcs* | turns the arc lamp off
* **Exit Calibration Mode** | moves the mirror on WIFIS into observation mode (not blocking light from telescope) makes sure everything else off (flippers, integrating sphere (both at ttl and power) arc lamp)

#####Right Side:
The 'On/Off' buttons in the Integrating Sphere and Arc Lamp boxes toggle the power to the respective light sources (I will probably add another button to the sphere part to turn the sphere on / off with ttl. The status of each is also displayed (on or off)

Mirror Flippers: the status at the top is if power is being supplied to the flippers.  There are two buttons for each flipper that control what position they are, each is labeled to describe what positon that is, the depressed button is the current position of the mirror. The text to the right says if the mirror is currently in motion or not. 

### If things aren't running correctly:
The main places that I forsee things going wrong are with the arduinos and the flippers internal programing.

In the directory "Calibration_Control" are the codes to be programed into the two arduinos (for the integrating sphere and mirror flippers). Make sure they are both loaded on and onto the right one. 

For the flippers themselves if misbehaving need to be plugged into a computer with windos via usb with the control softwear from Thorlabs installed. They need to have a specific set of instructions told to them to interperet their SMA signals. I'll update what these settings are here later. 



