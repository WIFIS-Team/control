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
import matplotlib.pyplot as mpl
import Tkinter as _tk
import WIFISastrometry as WA
from sys import exit

try:
    import FLI
except (ImportError, RuntimeError):
    print "FLI cannot be imported"

class Formatter(object):
    def __init__(self, im):
        self.im = im
    def __call__(self, x, y):
        z = self.im.get_array()[int(y), int(x)]
        return 'x={:.01f}, y={:.01f}, z={:.01f}'.format(x, y, z)


###########################################################
def load_FLIDevices():
    '''Loads the FLI devices into variables and sets the 
    default parameters'''
    
    camSN = 'ML0240613'
    focSN = 'PDF0184509'
    fltSN = 'CFW-1-5-001'

    ## Load the FLI devices into variables ##

    cam = FLI.USBCamera.locate_device(camSN)
    foc = FLI.USBFocuser.locate_device(focSN)
    flt = FLI.USBFilterWheel.locate_device(fltSN)
    
    ## Set default parameters for the FLI devices and ensure 
    if flt != None:
        flt.set_filter_pos(0)
    if foc != None:
        #foc.home_focuser()
        pass

    # ??? any other default params ???
   
    return [cam, foc, flt]

def measure_focus(img, sideregions = 2, fitwidth = 10, plot=False):

    imgshape = img.shape

    regionx = imgshape[0]/sideregions
    regiony = imgshape[1]/sideregions

    starsx = np.array([])
    starsy = np.array([])
    for i in range(sideregions):
        for j in range(sideregions):
            imgregion = img[regionx*i:regionx*(i+1),regiony*j:regiony*(j+1)]
            centroids = WA.centroid_finder(imgregion, plot=False)
            imgregionshape = imgregion.shape
            brightstar = WA.bright_star(centroids, imgregionshape)
            if brightstar:
                #print "BRIGHTSTAR: %f %f %f" % (centroids[0][brightstar], \
                #    centroids[1][brightstar], centroids[2][brightstar])
                cx = centroids[0][brightstar]
                cy = centroids[1][brightstar]
                star_x = imgregion[cx-fitwidth:cx+fitwidth+1, cy]
                star_y = imgregion[cx, cy-fitwidth:cy+fitwidth+1]
                xs = np.arange(len(star_x)) 

                if plot: 
                    mpl.imshow(imgregion, origin='lower')
                    mpl.plot(cy,cx, 'rx')
                    mpl.show()

                popt, pcov = WA.gaussian_fit(xs, star_x, [30000., 3.0, 10.0])
                starsx = np.append(starsx,popt[1])
                popt, pcov = WA.gaussian_fit(xs, star_y, [30000., 3.0, 10.0])
                starsy = np.append(starsy,popt[1])
    
    xavg = np.mean(starsx)
    yavg = np.mean(starsy)

    return np.mean([xavg, yavg])

################################################################################
class FLIApplication(_tk.Frame): 
    '''Creates the FLI GUI window and also contains a number of 
    functions for controlling the Filter Wheel, Focuser, and
    Camera.'''

    def __init__(self,parent):
        '''Initialize the GUI and load the Devices into memory'''

        _tk.Frame.__init__(self,parent)
        self.parent = parent
        
        #Try to import FLI devices
        try:
            self.cam, self.foc, self.flt = load_FLIDevices()
        except (ImportError, RuntimeError, NameError):
            self.cam, self.foc, self.flt = [None,None,None]
 
        self.initialize()

        # Call the functions to continuously update the reporting fields    
        # An error will most likely appear after you close the window as
        # the mainloop will still attempt to run these commands.
        self.writeFilterNum()
        self.getCCDTemp()
        self.writeStepNum()

    def initialize(self):
        '''Creates the actual GUI elements as well as run the various
        tasks'''

        self.grid()

        ##### Filter Wheel Settings #####
         
        # Check if FW is connected & colour label appropriately
        if self.flt == None:
            fltbg = 'red3'
        else:
            fltbg = 'green3'
         
        label = _tk.Label(self, text='Filter Settings', relief='ridge',\
            anchor="center", fg = "black", bg=fltbg,font=("Helvetica", 20))
        label.grid(column=0,row=0,columnspan=2, sticky='EW')
    
        # Filter position report label
        label = _tk.Label(self, text='Filter Position', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=1, sticky='EW')

        self.filterNumText = _tk.StringVar()        
        label = _tk.Label(self, textvariable=self.filterNumText, \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=2, sticky='EW')
        
        # Change filter buttons
        _tk.Button(self, text=u"Z",\
            command=self.gotoFilter1).grid(column = 1,row = 1, sticky='EW')
        _tk.Button(self, text=u"I",\
            command=self.gotoFilter2).grid(column = 1,row = 2, sticky='EW')
        _tk.Button(self, text=u"R",\
            command=self.gotoFilter3).grid(column = 1,row = 3, sticky='EW')
        _tk.Button(self, text=u"G",\
            command=self.gotoFilter4).grid(column = 1,row = 4, sticky='EW')
        _tk.Button(self, text=u"H-Alpha",\
            command=self.gotoFilter5).grid(column = 1,row = 5, sticky='EW')

        ##### Focuser Settings #####

        #Check to see if Focuser is connected & colour label appropriately
        if self.foc == None:
            focbg = 'red3'
        else:
            focbg = 'green3'

        label = _tk.Label(self, text='Focuser Settings', relief='ridge',\
            anchor="center", fg = "black", bg=focbg,font=("Helvetica", 20))
        label.grid(column=2,row=0,columnspan=2, sticky='EW')

        # Focuser step value setting entry field
        label = _tk.Label(self, text='Step Value', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=2,row=1, sticky='EW')

        self.entryfocVariable = _tk.StringVar()
        self.entryfoc = _tk.Entry(self, width = 10,\
            textvariable=self.entryfocVariable)
        self.entryfoc.grid(column=2, row=2, sticky='EW')
        self.entryfocVariable.set(u"100")

        # Focuser step position report label
        label = _tk.Label(self, text='Step Position', \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=2,row=3, sticky='EW')

        self.stepNumText = _tk.StringVar()        
        label = _tk.Label(self, textvariable=self.stepNumText, \
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=2,row=4, sticky='EW')
        self.writeStepNum()

        # Buttons for focuser
        _tk.Button(self, text=u"Home Focuser",\
            command=self.homeFocuser).grid(column = 3, row = 1, sticky='EW')
        _tk.Button(self, text=u"Step Forward",\
            command=self.stepForward).grid(column = 3, row = 2, sticky='EW')
        _tk.Button(self, text=u"Step Backward",\
            command=self.stepBackward).grid(column = 3, row = 3, sticky='EW')

        ##### Camera Settings #####

        # Check to see if Camera is connected & colour label appropriately
        if self.cam == None:
            cambg = 'red3'
        else:
            cambg = 'green3'

        label = _tk.Label(self, text='Camera Settings', relief='ridge',\
            anchor="center", fg = "black", bg=cambg,font=("Helvetica", 20))
        label.grid(column=1,row=6,columnspan=2, sticky='EW')

        # Exposure time set entry field
        label = _tk.Label(self, text='Exposure Time', relief='ridge',\
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=1,row=7, sticky='EW')

        self.entryExpVariable = _tk.StringVar()
        self.entryExp = _tk.Entry(self, width=10,\
            textvariable=self.entryExpVariable)
        self.entryExp.grid(column=1, row=8, sticky='EW')
        self.entryExpVariable.set(u"3000")

        # CCD temperature set entry field
        label = _tk.Label(self, text='Set Temperature',  relief='ridge',\
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=1,row=9, sticky='EW')

        self.entryCamTempVariable = _tk.StringVar()
        self.entryCamTemp = _tk.Entry(self, width=10,\
            textvariable=self.entryCamTempVariable)
        self.entryCamTemp.grid(column=1, row=10, sticky='EW')
        self.entryCamTempVariable.set(u"-20")

        # CCD Temp reporting label
        label = _tk.Label(self, text='CCD Temperature',  relief='ridge',\
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=9, sticky='EW')

        self.ccdTempText = _tk.StringVar()        
        label = _tk.Label(self, textvariable=self.ccdTempText, relief='ridge',\
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=10, sticky='EW')

        # Image filepath set entry field
        label = _tk.Label(self, text='Image Filepath',  relief='ridge',\
            anchor="center", fg = "black", bg="white",font=("Helvetica", 12))
        label.grid(column=0,row=7, sticky='EW')

        self.entryFilepathVariable = _tk.StringVar()
        self.entryFilepath = _tk.Entry(self, width=30, \
            textvariable=self.entryFilepathVariable)
        self.entryFilepath.grid(column=0, row=8, sticky='EW')
        self.entryFilepathVariable.set(u"/home/utopea/Desktop/test.fits")

        # Camera buttons
        _tk.Button(self, text=u"Take Image",\
            command=self.takeImage).grid(column = 2, row = 8, sticky='EW')
        _tk.Button(self, text=u"Set Temperature",\
            command=self.setTemperature).grid(column = 2, row = 10,\
            sticky='EW')
        _tk.Button(self, text=u"Check Focus",\
            command=self.checkFocus).grid(column = 3, row = 7, sticky='EW')
        _tk.Button(self, text=u"Focus Camera",\
            command=self.focusCamera).grid(column = 3, row = 8, sticky='EW')

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_columnconfigure(3,weight=1)
        #self.resizable(True, False)

    ## Functions to perform the above actions ##

    ## Filter Wheel Functions
    def gotoFilter1(self):
        if self.flt:
            self.flt.set_filter_pos(0)

    def gotoFilter2(self):
        if self.flt:
            self.flt.set_filter_pos(1)

    def gotoFilter3(self):
        if self.flt:
            self.flt.set_filter_pos(2)

    def gotoFilter4(self):
        if self.flt:
            self.flt.set_filter_pos(3)

    def gotoFilter5(self):
        if self.flt:
            self.flt.set_filter_pos(4)

    def writeFilterNum(self):
        if self.flt:
            filterpos = (self.flt.get_filter_pos() + 1)
            if filterpos == 1:
                self.filterNumText.set("Z")
            if filterpos == 2:
                self.filterNumText.set("I")
            if filterpos == 3:
                self.filterNumText.set("R")
            if filterpos == 4:
                self.filterNumText.set("G")
            if filterpos == 5:
                self.filterNumText.set("H-Alpha")
            self.after(500,self.writeFilterNum)


    ## Focuser Functions
    def homeFocuser(self):
        if self.foc:
            self.foc.home_focuser()

    def stepForward(self):
        if self.foc:
            self.foc.step_motor(int(self.entryfocVariable.get()))

    def stepBackward(self):
        if self.foc:
            self.foc.step_motor(-1*int(self.entryfocVariable.get()))    

    def writeStepNum(self):
        if self.foc:
            self.stepNumText.set(str(self.foc.get_stepper_position()))
            self.after(500, self.writeStepNum)

    ## Camera Functions
    def takeImage(self):
        if self.cam:
            self.cam.set_exposure(int(self.entryExpVariable.get()))
            img = self.cam.take_photo()  
            hdu = fits.PrimaryHDU(img)
            hdu.writeto(self.entryFilepathVariable.get(),clobber=True)

    def setTemperature(self):
        if self.cam:
            self.cam.set_temperature(int(self.entryCamTempVariable.get()))    

    def getCCDTemp(self):
        if self.cam:
            self.ccdTempText.set(str(self.cam.get_temperature()))
            self.after(1000,self.getCCDTemp)        
    
    def checkFocus(self):
        if self.cam and self.foc:
            self.cam.set_exposure(int(self.entryExpVariable.get()))
            img = self.cam.take_photo()
    
            mpl.close()
            #img_rot = np.rot90(img, k=3)
            fig = mpl.figure()
            ax = fig.add_subplot(1,1,1)
            im = ax.imshow(np.log10(img), interpolation='none', cmap='gray', origin='lower')
            ax.format_coord = Formatter(im)
            fig.colorbar(im)
            mpl.show()

    def focusCamera(self):

        current_focus = self.foc.get_stepper_position() 
        step = 200

        self.cam.set_exposure(3000)
        img = self.cam.take_photo()
        focus_check1 = measure_focus(img)
        direc = 1 #forward

        #plotting
        mpl.ion()
        fig, ax = mpl.subplots(1,1)
        
        #ax.hold(True)
        #mpl.show(False)
        #mpl.draw()

        #background = fig.canvas.copy_from_bbox(ax.bbox)
        imgplot = ax.imshow(img, interpolation = 'none', cmap='gray')
        fig.canvas.draw()

        while step > 5:
            print "\nSTEP IS: %i\nPOS IS: %i" % (step,current_focus)
            self.foc.step_motor(direc*step)
            img = self.cam.take_photo()

            #plotting
            ax.clear()
            imgplot = ax.imshow(img, interpolation = 'none', cmap='gray')
            fig.canvas.draw()
            #fig.canvas.restore_region(background)
            #ax.draw_artist(imgplot)
            #fig.canvas.blit(ax.bbox)

            focus_check2 = measure_focus(img)

            print "Old Focus: %f, New Focus: %f" % (focus_check1, focus_check2)
            #if focus gets go back to beginning, change direction and reduce step
            if focus_check2 > focus_check1:
                direc = direc*-1
                self.foc.step_motor(direc*step)
                step = int(step / 2)
                print "Focus is worse: changing direction!"
            
            focus_check1 = focus_check2
            current_focus = self.foc.get_stepper_position() 
        
        print "### FINISHED FOCUSING ####"

    
def run_fli_gui(tkroot):

    root = _tk.Toplevel(tkroot)
    root.title("WIFIS FLI Controller")
    
    app = FLIApplication(root)

def run_fli_gui_standalone():

    root = _tk.Tk()
    root.title("WIFIS FLI Controller")
    
    app = FLIApplication(root)

    root.mainloop()

def focusCamera():

    camSN = 'ML0240613'
    focSN = 'PDF0184509'
    foc = FLI.USBFocuser.locate_device(focSN)
    cam = FLI.USBCamera.locate_device(camSN)
    
    current_focus = foc.get_stepper_position() 
    step = 200

    cam.set_exposure(3000)
    img = cam.take_photo()
    focus_check1 = measure_focus(img)
    direc = 1 #forward

    #fig, ax = mpl.subplots(1,1)
    #imgplot = ax.imshow(img, interpolation = 'none', cmap='Greys')
    #mpl.show()
    #exit()

    #plotting
    fig, ax = mpl.subplots(1,1)
    
    ax.hold(True)
    mpl.show(False)
    mpl.draw()

    background = fig.canvas.copy_from_bbox(ax.bbox)
    imgplot = ax.imshow(img, interpolation = 'none', cmap='gray')

    while step > 5:
        print "\nSTEP IS: %i\nPOS IS: %i" % (step,current_focus)
        foc.step_motor(direc*step)
        img = cam.take_photo()

        #plotting
        fig.canvas.restore_region(background)
        ax.draw_artist(imgplot)
        fig.canvas.blit(ax.bbox)

        focus_check2 = measure_focus(img)
        print "Old Focus: %f, New Focus: %f" % (focus_check1, focus_check2)
        #if focus gets go back to beginning, change direction and reduce step
        if focus_check2 > focus_check1:
            direc = direc*-1
            foc.step_motor(direc*step)
            step = int(step / 2)
            print "Focus is worse: changing direction!"
        
        focus_check1 = focus_check2
        current_focus = foc.get_stepper_position() 
    print bright_stars
        
if __name__ == "__main__":
    run_fli_gui_standalone()

