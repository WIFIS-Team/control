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
