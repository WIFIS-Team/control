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

try:
    import FLI
except (ImportError, RuntimeError):
    print "FLI cannot be imported"

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
        
        try:
            self.cam, self.foc, self.flt = load_FLIDevices()
        except (ImportError, RuntimeError, NameError):
            self.cam, self.foc, self.flt = [[],[],[]]
 
        self.initialize()

    def initialize(self):
        self.grid()


        ### Filter Wheel Settings ###
         
        if len(self.flt) == 0:
            fltbg = 'red'
        else:
            fltbg = 'green'
         
        label = _tk.Label(self, text='Filter Settings', \
            anchor="center", fg = "black", bg=fltbg,font=("Helvetica", 20))
        label.grid(column=0,row=0,columnspan=2, sticky='EW')

        label = _tk.Label(self, text='Filter Position', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=1, sticky='EW')

        self.filterNumText = _tk.StringVar()        
        label = _tk.Label(self, textvariable=self.filterNumText, \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=2, sticky='EW')
        self.writeFilterNum()

        _tk.Button(self, text=u"Filter 1",command=self.gotoFilter1).grid(column = 1, row = 1, sticky='EW')
        _tk.Button(self, text=u"Filter 2",command=self.gotoFilter2).grid(column = 1, row = 2, sticky='EW')
        _tk.Button(self, text=u"Filter 3",command=self.gotoFilter3).grid(column = 1, row = 3, sticky='EW')
        _tk.Button(self, text=u"Filter 4",command=self.gotoFilter4).grid(column = 1, row = 4, sticky='EW')
        _tk.Button(self, text=u"Filter 5",command=self.gotoFilter5).grid(column = 1, row = 5, sticky='EW')




        ### Focuser Settings ###

        if len(self.foc) == 0:
            focbg = 'red'
        else:
            focbg = 'green'

        label = _tk.Label(self, text='Focuser Settings', \
            anchor="center", fg = "black", bg=focbg,font=("Helvetica", 20))
        label.grid(column=2,row=0,columnspan=2, sticky='EW')

        label = _tk.Label(self, text='Step Value', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=2,row=1, sticky='EW')

        self.entryfocVariable = _tk.StringVar()
        self.entryfoc = _tk.Entry(self, width = 10, textvariable=self.entryfocVariable)
        self.entryfoc.grid(column=2, row=2, sticky='EW')
        self.entryfocVariable.set(u"1")

        label = _tk.Label(self, text='Step Position', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=2,row=3, sticky='EW')

        self.stepNumText = _tk.StringVar()        
        label = _tk.Label(self, textvariable=self.stepNumText, \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=2,row=4, sticky='EW')
        self.writeStepNum()

        _tk.Button(self, text=u"Home Focuser",command=self.homeFocuser).grid(column = 3, row = 1, sticky='EW')
        _tk.Button(self, text=u"Step Forward",command=self.stepForward).grid(column = 3, row = 2, sticky='EW')
        _tk.Button(self, text=u"Step Backward",command=self.stepBackward).grid(column = 3, row = 3, sticky='EW')




        ## Camera Settings

        if len(self.cam) == 0:
            cambg = 'red'
        else:
            cambg = 'green'

        label = _tk.Label(self, text='Camera Settings', \
            anchor="center", fg = "black", bg=cambg,font=("Helvetica", 20))
        label.grid(column=1,row=6,columnspan=2, sticky='EW')


        label = _tk.Label(self, text='Exposure Time', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=1,row=7, sticky='EW')

        self.entryExpVariable = _tk.StringVar()
        self.entryExp = _tk.Entry(self, width=10,textvariable=self.entryExpVariable)
        self.entryExp.grid(column=1, row=8, sticky='EW')
        self.entryExpVariable.set(u"1")


        label = _tk.Label(self, text='Set Temperature', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=1,row=9, sticky='EW')

        self.entryCamTempVariable = _tk.StringVar()
        self.entryCamTemp = _tk.Entry(self, width=10, textvariable=self.entryCamTempVariable)
        self.entryCamTemp.grid(column=1, row=10, sticky='EW')
        self.entryCamTempVariable.set(u"24")


        label = _tk.Label(self, text='CCD Temperature', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=9, sticky='EW')

        self.ccdTempText = _tk.StringVar()        
        label = _tk.Label(self, textvariable=self.ccdTempText, \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=10, sticky='EW')
        self.getCCDTemp()


        label = _tk.Label(self, text='Image Filepath', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=7, sticky='EW')

        self.entryFilepathVariable = _tk.StringVar()
        self.entryFilepath = _tk.Entry(self, width=20, textvariable=self.entryFilepathVariable)
        self.entryFilepath.grid(column=0, row=8, sticky='EW')
        self.entryFilepathVariable.set(u"/home/UTOPEA/test.fits")


        _tk.Button(self, text=u"Take Image",command=self.takeImage).grid(column = 2, \
            row = 8, sticky='EW')
        _tk.Button(self, text=u"Set Temperature",command=self.setTemperature).grid(column = 2, \
            row = 10, sticky='EW')
 

        #self.grid_columnconfigure(0,weight=1)
        #self.resizable(True, False)

        #METACODE [Put function here that continuously updates labelVariable with currently selected
        #filter]

    def gotoFilter1(self):
        #self.flt.set_filter_pos(0)
        pass
    
    def gotoFilter2(self):
        #self.flt.set_filter_pos(1)
        pass

    def gotoFilter3(self):
        #self.flt.set_filter_pos(2)
        pass
    
    def gotoFilter4(self):
        #self.flt.set_filter_pos(3)
        pass

    def gotoFilter5(self):
        #self.flt.set_filter_pos(4)
        pass
        
    def writeFilterNum(self):
        #self.filterNumText.set(str(self.flt.get_filter_pos()))
        pass

    def homeFocuser(self):
        #self.foc.home_focuser()
        pass
    
    def stepForward(self):
        #self.foc.step_motor(int(self.entryfocVariable.get()))
        pass
        
    def stepBackward(self):
        #self.foc.step_motor(-1*int(self.entryfocVariable.get()))    
        pass

    def writeStepNum(self):
        #self.stepNumText.set(str(self.foc.get_stepper_position()))
        pass

    def takeImage(self):
        #self.cam.set_exposure(int(self.entryExpVariable.get()))
        #img = self.cam.take_photo()  
        #hdu = fits.PrimaryHDU(hdu)
        #hdu.writeto(self.entryFilepathVariable.get())
        pass

    def setTemperature(self):
        #self.foc.step_motor(-1*int(self.entryfocVariable.get()))    
        pass

    def getCCDTemp(self):
        #self.ccdTempText.set(str(self.cam.get_stepper_position()))        
        pass

if __name__ == "__main__":
    app = FLIApplication(None)
    app.title("WIFIS FLI Controller")
    app.mainloop()


