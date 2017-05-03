#gui that controls all of the calibration unit componants

#I tried to make it so that there are a few simple buttons that will do all the
#stpes needed to take calibration images and that the user can contorl the impo
#rtant componanats seperatly if desired. Also no matter how gui is exited 
#should make sure everything gets turned off

#NOTE: the statuses of the componants displayed by this app won't be updated if
#their power is disrupted through other sources, keep this in mine (could add 
#this function by adding an update_status() function like in power_control.py 
#but this would probably cause the whole code to lag annoyingly. 

# Miranda Jarvis Oct 2015
# Updated by Elliot Meyer Jan 2016, May 2017

from pylab import * 
import serial
from time import *
from Tkinter import *
import ttk
import dlipower
import sys
import signal

#GUI OUTLINE
#button 1: initiate calibration mode
#   turn on sphere plug
#   turn on flipper plug
#   move on wifis flipper to blocking pos

#button 2: set up for flats
#   move mirror in calibratoin box to right positon
#   turn on integrating sphere via ttl

#button 3: done flats
#   turn off sphere via ttl

#button 4: set up for wavelength
#   move mirror in calibration box to right position
#   turn on plug for arc lamp 

#button 5: done wavelelgnth
#   turn of plug for arc lamp 

#button 6: done calibration
#   move flipper on wifis to not blocking mode
#   turn off plug for flippers
#   turn off plug for sphere



###################################################
def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        result = default
    finally:
        signal.alarm(0)

    return result

# Assign your port and speed for sphere arduino
def connect_sphere(fport, sport):
    ser2 = None
    try: ser2 = serial.Serial(sport, 9600)
    except: 
        print 'Warning: unable to conect to arduino at'+sport
        try: ser2 = serial.Serial(fport, 9600)
        except: 
            print 'Warning: unable to conect to arduino at'+fport
    return ser2

# Function that reads the board
def clear_out(ser):
    a=ser.readline()
    return a
    
def setup_arduinos(fport,sport):
    """Connect to both arduinos. Ensure the USB hub is powered. 
    Returns the two arduino serial variables."""

    sphere = connect_sphere(fport,sport)
    print("Resetting Sphere Arduino")
    sleep(3) 
    
    out = None
    if sphere:
        sphere.write(bytes('L'))
        out=timeout(sphere.readline)

        if not out:
            print 'Port may be wrong for arduino, trying other port...'
            fport,sport=sport,fport
            sphere=connect_sphere(fport, sport)
            print("Resetting Sphere Arduino")
            sleep(3)
        elif out.split('\r')[0] != 'OFF':
            print 'Port may be wrong for arduino, trying other port...'
            fport,sport=sport,fport
            sphere=connect_sphere(fport,sport)
            print("Resetting Sphere Arduino")
            sleep(3)
        
    #Now connecting to the flipper Arduino
    try: ser = serial.Serial(fport, 9600)
    except: 
        print 'Warning: unable to conect to arduino at'+fport
        ser = None
    print("Resetting Flipper Arduino")
    sleep(3) 

    #put each pin to low mode (won't move flippers if power is off which could 
    #cause some problems)
    if ser:
        ser.write(bytes('L'))
        ser.write(bytes('M'))

    #first check to make sure there aren't any messages cached on the arduino 
    #as this will mess everything up read off until there are none since 
    #reading a message when none there causes the code to hang, 
    #defined timeout() above to stop it after a few seconds 
    
    if ser:
        #funtion that reads the board
        out='0' #initialize loop parameter

        #loop until out = None if function times out rather than finishing will 
        #return NONE instead of whatever was written on the board
        while out!=None:     
            #read off the board until empty   
            out=timeout(clear_out,args=(ser),timeout_duration=5) 

        #do same thing for sphere arduino 
        out='0' #initialize loop parameter

        while out!=None:
            #read off the board until empty   
            out=timeout(clear_out,args=(ser2),timeout_duration=5) 

        #put pin to low mode
        ser2.write(bytes('L'))

    return ser, ser2#, switch1, switch2

class MainApplication(Frame): 
    '''this class holds all of the gui into and button functions for the 
    calibration unit control GUI.'''

    def __init__(self,master,ser,ser2):#,switch1,switch2): #setup basic gui stuff
        Frame.__init__(self, master)
        self.grid()
        self.ser = ser
        self.ser2 = ser2
        self.create_widgets()


    def create_widgets(self): #create all the buttons and labesl and stuff
        #create dividing lines to keep gui clean (sticky makes them extend all 
        #the way)
        
        #ttk.Separator(self,orient=VERTICAL).grid(rowspan=12, column=1, \
        #    sticky="ns")
        
        #ttk.Separator(self,orient=HORIZONTAL).grid(row=2, column=2, \
        #    columnspan=3, sticky="ew")
        #ttk.Separator(self,orient=HORIZONTAL).grid(row=5, column=2, \
        #    columnspan=3, sticky="ew")

        ######################################################################
        #Sphere stuff (label if spehre's on or off allows user to turn it on 
        #and off by itself)
        ######################################################
        Label(self, text="Integrating Sphere", font='bold').grid(row=0, \
            column=1, padx=15)

        Button(self, text="On/Off", command=self.toggle_sphere, width=5).grid(\
            row=0, column=3)
        Label(self, text="Status:").grid(row=0, column=4)
        
        #this will update if sphere turned on by top level controls or by the 
        #button in this section NOT if changed elsewhere
        self.status_sphere = Label(self, text='OFF', fg ='red' ) 
        self.status_sphere.grid(row=0, column=4)

        Label(self, text="Flipper 1 (In Calibration Box)", font='bold',\
            anchor=W).grid(row=2, column=1,columnspan=2, padx=15,sticky="ew")
        self.b1=Button(self, text="Pos1 (Integrating Sphere)", \
            command=self.flip1pos1,relief=SUNKEN)
        self.b1.grid(row=2, column=3)
        self.b2=Button(self, text="Pos2 (Arc Lamp)", command=self.flip1pos2, \
            relief=RAISED)
        self.b2.grid(row=2, column=4)
        self.s1 = Label(self, text='in position', fg ='green' )
        self.s1.grid(row=2, column=5, padx=15)


        Label(self, text="Flipper 2 (On WIFIS)", font='bold',anchor=W).grid(\
            row=3, column=1,columnspan=2, padx=15,sticky="ew")
        self.b3=Button(self, text="Pos1 (Observation Mode)", \
            command=self.flip2pos1, relief=SUNKEN)
        self.b3.grid(row=3, column=3)
        self.b4=Button(self, text="Pos2 (Calibration Mode)", \
            command=self.flip2pos2, relief=RAISED)
        self.b4.grid(row=3, column=4)
        self.s2 = Label(self, text='in position', fg ='green' )
        self.s2.grid(row=3, column=5, padx=15)
        

#Top level control (each button does a series of steps to do calibratoin and 
#clean up afterward)
######################################################
    def f1(self): #(enter calibration mode)


#   move on wifis flipper to blocking pos   
        self.flip2pos2()

#   put buttons into arangement to show which are possible now
        self.c1['relief']=SUNKEN
        self.c2['relief']=RAISED
        self.c4['relief']=RAISED
        self.c6['relief']=RAISED
        self.update()

    def f2(self): #prepare to take flats
        if self.c2['relief']==RAISED:

            #   move mirror in calibratoin box to right positon
            self.flip1pos1()
            #   turn on integrating sphere 
            self.ser2.readline()
            self.ser2.write(bytes('H'))
            self.status_sphere["text"] = "ON"
            self.status_sphere["fg"] = "green"

            #   put buttons into arangement to show which are possible now
            self.c2['relief']=SUNKEN
            self.c3['relief']=RAISED
            self.c4['relief']=SUNKEN


    def f3(self): # done flats
#   turn off sphere 
        self.ser2.readline()
        self.ser2.write(bytes('L'))
        self.status_sphere['text']='OFF'
        self.status_sphere['fg']='red'
        

#   put buttons into arangement to show which are possible now
        self.c3['relief']=SUNKEN
        self.c2['relief']=RAISED
        self.c4['relief']=RAISED    

    def f4(self): #set up for wavelength
        if self.c4['relief']==RAISED:
#   move mirror in calibration box to right position
            self.flip1pos2()
#   turn on plug for arc lamp 
            self.status_arc['text']='ON'
            self.status_arc['fg']='green'

#   put buttons into arangement to show which are possible now
            self.c4['relief']=SUNKEN
            self.c5['relief']=RAISED
            self.c2['relief']=SUNKEN

    def f5(self): #done wavelelgnth
#   turn of plug for arc lamp 
        self.status_arc['text']='OFF'
        self.status_arc['fg']='red'

#   put buttons into arangement to show which are possible now
        self.c5['relief']=SUNKEN
        self.c4['relief']=RAISED
        self.c2['relief']=RAISED
        
    def f6(self): #done calibration
#   move flipper on wifis to not blocking mode
        self.flip2pos1()

#   put flipper arduino into low mode
        self.flip1pos1()

#   turn off arc lamp plugs in case left on
        self.status_arc['text']='OFF'
        self.status_arc['fg']='red'

#   turn off plug for flippers
        self.status_flippers['text']='OFF'
        self.status_flippers['fg']='red'
#   turn off sphere and plug for sphere 
        self.ser2.write(bytes('L'))
        self.status_sphere['text']='OFF'
        self.status_sphere['fg']='red'

#  make sure sphere arduino pins in low mode
        ser2.write(bytes('L'))
        
#   put buttons into arangement to show which are possible now
        self.c1['relief']=RAISED
        self.c2['relief']=SUNKEN
        self.c3['relief']=SUNKEN
        self.c4['relief']=SUNKEN
        self.c5['relief']=SUNKEN
        self.c6['relief']=SUNKEN

#Sphere stuff (button turns sphere on or off and update status), right now 
#using ttl, but might change this to just use the plug)
######################################################
    def toggle_sphere(self):
        #to toggle by arduino
        #print 'get the thing'
        message=self.ser2.readline()[0:3]
        #print message

        if message=='ON-':
            self.ser2.write(bytes('L'))
            self.status_sphere["text"] = "OFF"
            self.status_sphere["fg"] = "red"    
    
        if message=='OFF':
            self.ser2.write(bytes('H'))
            self.status_sphere["text"] = "ON"
            self.status_sphere["fg"] = "green"
        
#Flipper stuff (see flipper_gui.py for explenations of theses) tells flippers 
#to move to a given positoin and shows when it's moving and when its stopped 
######################################################
    def flip1pos2(self):
        self.ser.write(bytes('N'))
        self.s1['text']='in motion'
        self.s1['fg']='red'
        self.update()
        q='1'
        while q=='1':
            self.ser.write(bytes('V'))
            q=self.ser.readline()[0]
            sleep(0.1)
        self.s1["text"] = "in position"
        self.s1["fg"] = "green" 
        self.b2['relief']=SUNKEN
        self.b1['relief']=RAISED


    def flip1pos1(self):
        self.ser.write(bytes('M'))
        self.s1["text"] = "in motion"
        self.s1["fg"] = "red"
        self.update()
        q='1'
        while q=='1':
            self.ser.write(bytes('V'))
            q=self.ser.readline()[0]
            sleep(0.1)
        self.s1["text"] = "in position"
        self.s1["fg"] = "green"
        self.b1['relief']=SUNKEN
        self.b2['relief']=RAISED


    def flip2pos2(self):
        self.ser.write(bytes('H'))
        self.s2['text']='in motion'
        self.s2['fg']='red'
        self.update()
        q='1'
        while q=='1':
            self.ser.write(bytes('R'))
            q=self.ser.readline()[0]
            sleep(0.1)
        self.s2["text"] = "in position"
        self.s2["fg"] = "green" 
        self.b4['relief']=SUNKEN
        self.b3['relief']=RAISED


    def flip2pos1(self):
        self.ser.write(bytes('L'))
        self.s2["text"] = "in motion"
        self.s2["fg"] = "red"
        self.update()
        q='1'
        while q=='1':
            self.ser.write(bytes('R'))
            q=self.ser.readline()[0]
            sleep(0.1)
        self.s2["text"] = "in position"
        self.s2["fg"] = "green"
        self.b3['relief']=SUNKEN
        self.b4['relief']=RAISED

def run_calib_gui(tkroot,mainloop = False):

    #port for flipper arduino
    fport='/dev/ttyACM0'

    #port for sphere arduino
    sport='/dev/ttyACM1'

    ser,ser2 = setup_arduinos(fport,sport)
    
    if (ser == None) and (ser2 == None):
        print "THE ARDUINOS ARE NOT PROPERLY CONNECTED. PLEASE CHECK THEM AND RESTART THIS SCRIPT"
    
    print 'Activating Calibration GUI'

    root = Toplevel(tkroot) #gui set up stuff
    root.title("Calibration Unit Control") #gui name
    root.geometry("700x400") #gui size

    app = MainApplication(root,ser,ser2) #set up gui class

    return ser, ser2

def run_calib_gui_standalone():

    #port for flipper arduino
    fport='/dev/ttyACM2'

    #port for sphere arduino
    sport='/dev/ttyACM3'

    ser,ser2 = setup_arduinos(fport,sport)
   
    if (ser == None) and (ser2 == None):
        print "THE ARDUINOS ARE NOT PROPERLY CONNECTED. PLEASE CHECK THEM AND RESTART THIS SCRIPT"

    print 'activating gui'
    root = Tk() #gui set up stuff
    root.title("Calibration Unit Control") #gui name
    #root.geometry("700x400") #gui size

    app = MainApplication(root,ser,ser2) #set up gui class

    root.mainloop() #run gui loop
    
    #clean up in case user didn't hit exit calibration mode button: 
    #make sure all arduino pins in low mode
    if ser:
        ser.write(bytes('L'))
        ser.write(bytes('M'))
    #ser2.write(bytes('L'))

if __name__ == '__main__':
    run_calib_gui_standalone()
