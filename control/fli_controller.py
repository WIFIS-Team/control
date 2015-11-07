# -*- coding: utf-8 -*-
#
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
#

import numpy as np
import FLI
from astropy.io import fits
import matplotlib.pyplot as mpl
import Tkinter as Tk


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

def MainApplicaiton(Frame): 

