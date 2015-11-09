# -*- coding: utf-8 -*-
#
#----------------------------------------------------------
# Name:     fli_controller.py
# Purpose:  Provide control interface for the FLI devices
# Author:   Elliot Meyer
# Email:    meyer@astro.utoronto.ca
# Date:     November 2015
#----------------------------------------------------------
#
#

import numpy as np
from astropy.io import fits
#import matplotlib.pyplot as mpl
import Tkinter as _tk
#import FLI

def load_FLIDevices():
    '''Loads the FLI devices into variables and sets the 
    default parameters'''
    
    camSN = 000000
    focSN = 000000
    fltSN = 00000

   ## Load the FLI devices into variables ##

    cam = FLI.USBCamera.locate_device(camSN)
    foc = FLI.USBFocuser.locate_device(focSN)
    flt = FLI.USBFilterWheel.locate_device(fltSN)

   ## Set default parameters for the FLI devices and ensure 

    flt.set_filter_pos(0)
    foc.home_focuser()

   # ??? other default params ???
   
    return [cam, foc, flt]

class FLIApplication(_tk.Tk): 

    def __init__(self,parent):
        _tk.Tk.__init__(self,parent)
        self.parent = parent
        #self.cam, self.foc, self.flt = load_FLIDevices()
        self.initialize()

    def initialize(self):
        self.grid()

        self.entry = _tk.Entry(self)
        self.entry.grid(column=0, row=0, sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        
        _tk.Button(self, text=u"Filter 1",command=self.gotoFilter1).grid(column = 1, row = 0)
        _tk.Button(self, text=u"Filter 2",command=self.gotoFilter2).grid(column = 1, row = 1)
        _tk.Button(self, text=u"Filter 3",command=self.gotoFilter3).grid(column = 1, row = 2)
        _tk.Button(self, text=u"Filter 4",command=self.gotoFilter4).grid(column = 1, row = 3)
        _tk.Button(self, text=u"Filter 5",command=self.gotoFilter5).grid(column = 1, row = 4)

        label = _tk.Label(self, anchor="w", fg = "white", bg="orange")
        label.grid(column=0,row=6,columnspan=2, sticky='EW')

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True, False)


    def gotoFilter1(self):
        #self.flt.set_filter_pos(0)
        print "Selecting Filter 1"
    
    def gotoFilter2(self):
        #self.flt.set_filter_pos(1)
        print "Selecting Filter 2"

    def gotoFilter3(self):
        #self.flt.set_filter_pos(2)
        print "Selecting Filter 3"
    
    def gotoFilter4(self):
        #self.flt.set_filter_pos(3)
        print "Selecting Filter 4"

    def gotoFilter5(self):
        #self.flt.set_filter_pos(4)
        print "Selecting Filter 5"

    def OnPressEnter(self, event):
        "You pressed enter !"

if __name__ == "__main__":
    app = FLIApplication(None)
    app.title("WIFIS FLI Controller")
    app.mainloop()


