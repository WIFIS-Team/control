# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Name:     motor_controller.py
# Purpose:  Motor control interface for WIFIS
# Authors:  Jason Leung
# Date:     July 2015
#------------------------------------------------------------------------------
"""
This is a GUI module used to control the motors for WIFIS
"""

# initialize a serial RTU client instance
from pymodbus.client.sync import ModbusSerialClient as ModbusClient  

from Tkinter import *

class MainApplication(Frame):
    """
    Main GUI application to control motor
    """

    def __init__(self, master,client):
        Frame.__init__(self, master)
        self.grid()

        self.client = client
        self.status1 = self.status2 = self.status3 = None
        #self.position1 = self.position2 = self.position3 = None
        self.pos1 = StringVar()
        self.pos2 = StringVar()
        self.pos3 = StringVar()
        self.pos1.set(0)
        self.pos2.set(0)
        self.pos3.set(0)
        self.motor_position = 0
        self.speed1 = self.speed2 = self.speed3 = None
        self.motor_speed1 = StringVar()
        self.motor_speed1.set(10)
        self.motor_speed2 = StringVar()
        self.motor_speed2.set(500)
        self.motor_speed3 = StringVar()
        self.motor_speed3.set(1000)
        self.step1 = self.step2 = self.step3 = None
        self.motor_step1 = StringVar()
        self.motor_step1.set(10)
        self.motor_step2 = StringVar()
        self.motor_step2.set(100)
        self.motor_step3 = StringVar()
        self.motor_step3.set(100)

        self.create_widgets()

        for i in range(3):
            self.get_position(i+1)

    def create_widgets(self):
        """
        Creates the widgets that form the interface. Includes the information 
        panel, which details the status, position, and speed of the motor; as 
        well as the control buttons Step, Fwd, Rev, Home, Stop, Off.
        
        The status of the motor can be ON, MOVE, HOME, OFF.
        
        Note: The motor will not execute any "move" commands while it is 
        already in a MOVE or HOME state. Click the Stop button to return it to 
        the ON state prior to sending additional commands.
        
        Step moves the motor by the selected number of steps. (1 revolution = 
        1000 steps) Home returns the motor to the home position.
        
        Fwd (Forward) continuously rotates the motor clockwise at the 
            determined speed.
        Rev (Reverse) continuously rotates the motor counterclockwise at the 
            determined speed.
        
        Stop ceases the motor's operation, but keeps it on.
        
        Off turns the motor off.
        """
        Label(self, text="Motor 1").grid(row=0, column=0, padx=15)
        Label(self, text="Motor 2").grid(row=0, column=1, padx=15)
        Label(self, text="Motor 3").grid(row=0, column=2, padx=15)

        self.status1 = Label(self, text="OFF")
        self.status1.grid(row=1, column=0)
        self.status2 = Label(self, text="OFF")
        self.status2.grid(row=1, column=1)
        self.status3 = Label(self, text="OFF")
        self.status3.grid(row=1, column=2)

        Label(self, text="Position:").grid(row=2, column=0, sticky=W)

        self.position1 = Label(self, textvariable=self.pos1)
        self.position1.grid(row=3, column=0)
        self.position2 = Label(self, textvariable=self.pos2)
        self.position2.grid(row=3, column=1)
        self.position3 = Label(self, textvariable=self.pos3)
        self.position3.grid(row=3, column=2)

        Label(self, text="Speed:").grid(row=4, column=0, sticky=W)

        self.speed1 = Entry(self, textvariable=self.motor_speed1, width=5)
        self.speed1.grid(row=5, column=0)
        self.speed2 = Entry(self, textvariable=self.motor_speed2, width=5)
        self.speed2.grid(row=5, column=1)
        self.speed3 = Entry(self, textvariable=self.motor_speed3, width=5)
        self.speed3.grid(row=5, column=2)

        Label(self, text="Step:").grid(row=7, column=0, sticky=W)

        self.step1 = Entry(self, textvariable=self.motor_step1, width=5)
        self.step1.grid(row=8, column=0)
        self.step2 = Entry(self, textvariable=self.motor_step2, width=5)
        self.step2.grid(row=8, column=1)
        self.step3 = Entry(self, textvariable=self.motor_step3, width=5)
        self.step3.grid(row=8, column=2)

        # Motor 1 buttons
        Button(self, text="Set", command=self.m1_speed, width=5).grid(row=6, column=0)
        Button(self, text="Step", command=self.m1_step, width=5).grid(row=9, column=0)
        Button(self, text="Home", command=self.m1_home, width=5).grid(row=10, column=0)
        Button(self, text="Fwd", command=self.m1_forward, width=5).grid(row=11, column=0)
        Button(self, text="Rev", command=self.m1_reverse, width=5).grid(row=12, column=0)
        Button(self, text="Stop", command=self.m1_stop, width=5).grid(row=13, column=0)
        Button(self, text="Off", command=self.m1_off, width=5).grid(row=14, column=0)

        # Motor 2 buttons
        Button(self, text="Set", command=self.m2_speed, width=5).grid(row=6, column=1)
        Button(self, text="Step", command=self.m2_step, width=5).grid(row=9, column=1)
        Button(self, text="Home", command=self.m2_home, width=5).grid(row=10, column=1)
        Button(self, text="Fwd", command=self.m2_forward, width=5).grid(row=11, column=1)
        Button(self, text="Rev", command=self.m2_reverse, width=5).grid(row=12, column=1)
        Button(self, text="Stop", command=self.m2_stop, width=5).grid(row=13, column=1)
        Button(self, text="Off", command=self.m2_off, width=5).grid(row=14, column=1)

        # Motor 3 buttons
        Button(self, text="Set", command=self.m3_speed, width=5).grid(row=6, column=2)
        Button(self, text="Step", command=self.m3_step, width=5).grid(row=9, column=2)
        Button(self, text="Home", command=self.m3_home, width=5).grid(row=10, column=2)
        Button(self, text="Fwd", command=self.m3_forward, width=5).grid(row=11, column=2)
        Button(self, text="Rev", command=self.m3_reverse, width=5).grid(row=12, column=2)
        Button(self, text="Stop", command=self.m3_stop, width=5).grid(row=13, column=2)
        Button(self, text="Off", command=self.m3_off, width=5).grid(row=14, column=2)

    def get_position(self, unit):
        temp = self.client.read_holding_registers(0x0118, 2, unit=unit)
        self.motor_position = (temp.registers[0] << 16) + temp.registers[1]
        if self.motor_position >= 2**31:
            self.motor_position -= 2**32
        #position_labels = [self.position1, self.position2, self.position3]
        #position_labels[unit-1]["text"] = str(self.motor_position)
        position_labels = [self.pos1,self.pos2,self.pos3]
        poslabel = position_labels[unit-1]
        poslabel.set(str(self.motor_position))

    def stepping_operation(self, value, unit):
        step = int(value)
        if step < 0:
            step += 2**32
        upper = step >> 16
        lower = step & 0xFFFF
        self.client.write_register(0x001E, 0x2000, unit=unit)
        self.client.write_registers(0x0402, [upper, lower], unit=unit)
        status_labels = [self.status1, self.status2, self.status3]
        status_labels[unit-1]["text"] = "MOVE"
        self.client.write_register(0x001E, 0x2101, unit=unit)
        self.get_position(unit)
        
    # Motor 1 methods
    def m1_speed(self):
        speed = int(self.motor_speed1.get())
        upper = speed >> 16
        lower = speed & 0xFFFF
        self.client.write_registers(0x0502, [upper, lower], unit=0x01)

    def m1_step(self):
        self.stepping_operation(self.motor_step1.get(), unit=0x01)

    def m1_home(self):
        self.client.write_register(0x001E, 0x2800, unit=0x01)
        self.status1["text"] = "HOME"

    def m1_forward(self):
        self.client.write_register(0x001E, 0x2201, unit=0x01)
        self.status1["text"] = "MOVE"

    def m1_reverse(self):
        self.client.write_register(0x001E, 0x2401, unit=0x01)
        self.status1["text"] = "MOVE"

    def m1_stop(self):
        self.client.write_register(0x001E, 0x2000, unit=0x01)
        self.status1["text"] = "ON"
        self.get_position(unit=0x01)

    def m1_off(self):
        self.client.write_register(0x001E, 0x0000, unit=0x01)
        self.status1["text"] = "OFF"

    # Motor 2 methods
    def m2_speed(self):
        speed = int(self.motor_speed2.get())
        upper = speed >> 16
        lower = speed & 0xFFFF
        self.client.write_registers(0x0502, [upper, lower], unit=0x02)

    def m2_step(self):
        self.stepping_operation(self.motor_step2.get(), unit=0x02)

    def m2_home(self):
        self.client.write_register(0x001E, 0x2800, unit=0x02)
        self.status2["text"] = "HOME"

    def m2_forward(self):
        self.client.write_register(0x001E, 0x2201, unit=0x02)
        self.status2["text"] = "MOVE"

    def m2_reverse(self):
        self.client.write_register(0x001E, 0x2401, unit=0x02)
        self.status2["text"] = "MOVE"

    def m2_stop(self):
        self.client.write_register(0x001E, 0x2000, unit=0x02)
        self.status2["text"] = "ON"
        self.get_position(unit=0x02)

    def m2_off(self):
        self.client.write_register(0x001E, 0x0000, unit=0x02)
        self.status2["text"] = "OFF"

    # Motor 3 methods
    def m3_speed(self):
        speed = int(self.motor_speed3.get())
        upper = speed >> 16
        lower = speed & 0xFFFF
        self.client.write_registers(0x0502, [upper, lower], unit=0x03)

    def m3_step(self):
        self.stepping_operation(self.motor_step3.get(), unit=0x03)

    def m3_home(self):
        self.client.write_register(0x001E, 0x2800, unit=0x03)
        self.status3["text"] = "HOME"

    def m3_forward(self):
        self.client.write_register(0x001E, 0x2201, unit=0x03)
        self.status3["text"] = "MOVE"

    def m3_reverse(self):
        self.client.write_register(0x001E, 0x2401, unit=0x03)
        self.status3["text"] = "MOVE"

    def m3_stop(self):
        self.client.write_register(0x001E, 0x2000, unit=0x03)
        self.status3["text"] = "ON"
        self.get_position(unit=0x03)

    def m3_off(self):
        self.client.write_register(0x001E, 0x0000, unit=0x03)
        self.status3["text"] = "OFF"

def run_motor_gui_standalone():

    client = ModbusClient(method="rtu", port="/dev/ttyUSB2", stopbits=1, \
        bytesize=8, parity='E', baudrate=9600, timeout=0.1)

    # connect to the serial modbus server
    connection = client.connect()
    print("Connection = " + str(connection))
    
    # Create and set up the GUI object
    root = Tk()
    root.title("WIFIS Motor Controller")
    root.geometry("250x375")

    app = MainApplication(root,client)

    root.mainloop()

    # closes the underlying socket connection
    client.close()

def run_motor_gui(tkroot):

    client = ModbusClient(method="rtu", port="/dev/ttyUSB2", stopbits=1, \
        bytesize=8, parity='E', baudrate=9600, timeout=0.1)

    # connect to the serial modbus server
    connection = client.connect()
    print("Connection = " + str(connection))
    
    # Create and set up the GUI object
    root = Toplevel(tkroot)
    root.title("WIFIS Motor Controller")
    root.geometry("250x375")

    app = MainApplication(root,client)

    return client

if __name__ == '__main__':
    run_motor_gui_standalone()
