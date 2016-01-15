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

from pylab import * 
import serial
from time import *
from Tkinter import *
import ttk
import dlipower
import sys

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
#I took this form the internet so won't comment it cuase I don't really know 
#how it works stops a function after waiting a time set by timeout_duration. 
def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import signal

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
    try: ser2 = serial.Serial(sport, 9600)
    except: 
        print 'Warning: unable to conect to arduino at'+sport
        try: ser2 = serial.Serial(fport, 9600)
        except: 
            print 'Warning: unable to conect to arduino at'+fport
            sys.exit()
    return ser2

# Function that reads the board
def clear_out(ser):
    a=ser.readline()
    #print a[0]
    return a
    
def setup_arduinos(fport,sport):
    ser2=connect_sphere(fport,sport)
    print("Reset Sphere Arduino")
    sleep(3) #not sure why does this
    ser2.write(bytes('L'))
    answ=timeout(ser2.readline)

    if not answ:
        print 'gave wrong port for sphere arduino, switching ports'
        fport,sport=sport,fport
        ser2=connect_sphere(fport, sport)
        print("Reset Sphere Arduino")
        sleep(3)
    elif answ.split('\r')[0] != 'OFF':
        print 'gave wrong port for sphere arduino, switching ports' 
        fport,sport=sport,fport
        ser2=connect_sphere(fport,sport)
        print("Reset Sphere Arduino")
        sleep(3)
        

    # assign your port and speed for flipper arduino
    try: ser = serial.Serial(fport, 9600)
    except: print 'Warning: unable to conect to arduino at'+\
        fport;sys.exit()
    print("Reset Flipper Arduino")
    sleep(3) #not sure why does this

    #put each pin to low mode (won't move flippers if power is off which could 
    #cause some problems)
    ser.write(bytes('L'))
    ser.write(bytes('M'))

    #connect to both power switches 
    print('Connecting to a DLI PowerSwitch at http://192.168.0.120 and'+\
        'another at http://192.168.0.110 ')
    switch2 = dlipower.PowerSwitch(hostname="192.168.0.120", userid="admin",\
        password='9876')
    switch1=dlipower.PowerSwitch(hostname="192.168.0.110", userid="admin",\
        password='9876')
    exit=0

    #see if power switches connected:
    try: c1=switch2[3].state
    except: print 'Warning: power control #2 failed to connect'; exit=1

    try: c1=switch1[3].state
    except: print 'Warning: power control #1 failed to connect'; exit=1

    if exit==1: sys.exit()

    #first check to make sure there aren't any messages cached on the arduino 
    #as this will mess everything up read off until there are none since 
    #reading a message when none there causes the code to hang, 
    #defined timeout() above to stop it after a few seconds 

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

    return ser, ser2

class MainApplication(Frame): 
    '''this class holds all of the gui into and button functions for the 
    calibration unit control GUI.'''

    def __init__(self,master,ser,ser2): #setup basic gui stuff
        Frame.__init__(self, master)
        self.grid()
        self.ser = ser
        self.ser2 = ser2
        self.create_widgets()


    def create_widgets(self): #create all the buttons and labesl and stuff
        #create dividing lines to keep gui clean (sticky makes them extend all 
        #the way)
        ttk.Separator(self,orient=VERTICAL).grid(rowspan=12, column=1, \
            sticky="ns")

        ttk.Separator(self,orient=HORIZONTAL).grid(row=2, column=2, \
            columnspan=3, sticky="ew")
        ttk.Separator(self,orient=HORIZONTAL).grid(row=5, column=2, \
            columnspan=3, sticky="ew")

        #Top level control (buttons that do multiple things each leads to 
        #function bellow)
        ######################################################

        #Label(self, text="Enter Calibration Mode", font='bold').grid(row=0, \
            #column=0, padx=15)

        self.c1=Button(self, text="Enter Calibration Mode", command=self.f1,\
            relief=RAISED)
        self.c1.grid(row=0, column=0, padx=15)  
    
        #Label(self, text="Prepare to take Flats", font='bold').grid(row=2, 
            #column=0, padx=15)

        self.c2=Button(self, text="Prepare to take Flats", command=self.f2, \
            relief=SUNKEN)
        self.c2.grid(row=3, column=0, padx=15)

        #Label(self, text="Finished taking Flats", font='bold').grid(row=4, \
            #column=0, padx=15)

        self.c3=Button(self, text="Finished taking Flats", command=self.f3, \
            relief=SUNKEN)
        self.c3.grid(row=5, column=0, padx=15)

        #Label(self, text="Prepare to take Arcs", font='bold').grid(row=6, \
            #column=0, padx=15)

        self.c4=Button(self, text="Prepare to take Arcs", command=self.f4,\
            relief=SUNKEN)
        self.c4.grid(row=7, column=0, padx=15)

        #Label(self, text="Finished taking Arcs", font='bold').grid(row=8, \
            #column=0, padx=15)

        self.c5=Button(self, text="Finished taking Arcs", command=self.f5, \
            relief=SUNKEN)
        self.c5.grid(row=9, column=0, padx=15)

        #Label(self, text="Exit Calibration Mode", font='bold').grid(row=10, \
            #column=0, padx=15)

        self.c6=Button(self, text="Exit Calibration Mode", command=self.f6, \
            relief=SUNKEN)
        self.c6.grid(row=11, column=0, padx=15)


        #Sphere stuff (label if spehre's on or off allows user to turn it on 
        #and off by itself)
        ######################################################
        Label(self, text="Integrating Sphere", font='bold').grid(row=0, \
            column=2, padx=15)

        Button(self, text="On/Off", command=self.toggle_sphere, width=5).grid(\
            row=1, column=2)
        Label(self, text="Status:").grid(row=1, column=3)
        
        #this will update if sphere turned on by top level controls or by the 
        #button in this section NOT if changed elsewhere
        self.status_sphere = Label(self, text='OFF', fg ='red' ) 
        self.status_sphere.grid(row=1, column=4)

        #Arc Lamp stuff (labels if arc lamp on or off lets user turn it on and 
        #off individually)
        
        ######################################################
        Label(self, text="Arc Lamp", font='bold').grid(row=3, column=2, \
            padx=15)

        Button(self, text="On/Off", command=self.toggle_arc, width=5).grid(\
            row=4, column=2)
        Label(self, text="Status:").grid(row=4, column=3)
        
        #this will update if arc lamp turned on by top level controls or by the
        #button in this section
        self.status_arc = Label(self, text='OFF', fg ='red' ) 
        self.status_arc.grid(row=4, column=4)       

        #Flipper stuff (this is pretty much identical to flipper_gui.py, 
        #see that code for comments...) 
        ######################################################
        Label(self, text='Mirror Flippers', font='bold',anchor=W).grid(row=6,\
            column=2, padx=15,sticky="ew")
        Label(self, text="Status:").grid(row=6, column=3)
        state=switch2[3].state
        if state=='OFF': c='red'
        else: c='green'
        self.status_flippers=Label(self, text=state, fg =c )
        self.status_flippers.grid(row=6, column=4)      

        Button(self, text="On/Off", command=self.fliponoff,width=5).grid(\
            row=7,column=2)
        
        Label(self, text="Flipper 1 (In Calibration Box)", font='bold',\
            anchor=W).grid(row=8, column=2,columnspan=2, padx=15,sticky="ew")
        
        self.b1=Button(self, text="Pos1 (Integrating Sphere)", \
            command=self.flip1pos1,relief=SUNKEN)
        self.b1.grid(row=9, column=2)

        self.b2=Button(self, text="Pos2 (Arc Lamp)", command=self.flip1pos2, \
            relief=RAISED)
        self.b2.grid(row=9, column=3)

        self.s1 = Label(self, text='in position', fg ='green' )
        self.s1.grid(row=9, column=4, padx=15)


        Label(self, text="Flipper 2 (On WIFIS)", font='bold',anchor=W).grid(\
            row=10, column=2,columnspan=2, padx=15,sticky="ew")

        self.b3=Button(self, text="Pos1 (Observation Mode)", \
            command=self.flip2pos1, relief=SUNKEN)
        self.b3.grid(row=11, column=2)

        self.b4=Button(self, text="Pos2 (Calibration Mode)", \
            command=self.flip2pos2, relief=RAISED)
        self.b4.grid(row=11, column=3)

        self.s2 = Label(self, text='in position', fg ='green' )
        self.s2.grid(row=11, column=4, padx=15)
        

#Top level control (each button does a series of steps to do calibratoin and 
#clean up afterward)
######################################################
    def f1(self): #(enter calibration mode)



#   turn on flipper plug
        if switch2[3].state == 'OFF':
            switch2[3].state='ON'
            self.status_flippers['text']='ON'
            self.status_flippers['fg']='green'

#   move on wifis flipper to blocking pos   
        self.flip2pos2()

#   put buttons into arangement to show which are possible now
        self.c1['relief']=SUNKEN
        self.c2['relief']=RAISED
        self.c4['relief']=RAISED
        self.c6['relief']=RAISED
        self.update()

#   turn on sphere power
        switch2[1].state='ON'

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
            switch2[2].state='ON'
            self.status_arc['text']='ON'
            self.status_arc['fg']='green'

#   put buttons into arangement to show which are possible now
            self.c4['relief']=SUNKEN
            self.c5['relief']=RAISED
            self.c2['relief']=SUNKEN

    def f5(self): #done wavelelgnth
#   turn of plug for arc lamp 
        switch2[2].state='OFF'
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
        switch2[2].state='OFF'
        self.status_arc['text']='OFF'
        self.status_arc['fg']='red'

#   turn off plug for flippers
        switch2[3].state='OFF'
        self.status_flippers['text']='OFF'
        self.status_flippers['fg']='red'
#   turn off sphere and plug for sphere 
        self.ser2.write(bytes('L'))
        switch2[1].state='OFF'
        self.status_sphere['text']='OFF'
        self.status_sphere['fg']='red'

##  make sure sphere arduino pins in low mode
        #ser2.write(bytes('L'))
        
#   put buttons into arangement to show which are possible now
        self.c1['relief']=RAISED
        self.c2['relief']=SUNKEN
        self.c3['relief']=SUNKEN
        self.c4['relief']=SUNKEN
        self.c5['relief']=SUNKEN
        self.c6['relief']=SUNKEN

    def fliponoff(self):
        status =switch2[3].state
        if status=='ON':
             switch2[3].state='OFF'
             self.status_flippers["text"] = "OFF"
             self.status_flippers["fg"] = "red"
        else:
             switch2[3].state='ON'
             self.status_flippers["text"] = "ON"
             self.status_flippers["fg"] = "green"


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
        
        #to toggle by power
        #n=2
        #status=switch2[n].state
        #if status=='ON': 
        #   switch2[n].state='OFF'
        #   self.status_sphere["text"] = "OFF"
        #   self.status_sphere["fg"] = "red"
        #else: 
        #   switch2[n].state='ON'
        #   self.status_sphere["text"] = "ON"
        #   self.status_sphere["fg"] = "green"  


#Arc Lamp stuff (turns lamp on or off using outlet, updates status) 
######################################################
    def toggle_arc(self):
        n=2
        status=switch2[n].state
        if status=='ON': 
            switch2[n].state='OFF'
            self.status_arc["text"] = "OFF"
            self.status_arc["fg"] = "red"
        else: 
            switch2[n].state='ON'
            self.status_arc["text"] = "ON"
            self.status_arc["fg"] = "green"


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
    
    print 'activating gui'
    root = Toplevel(tkroot) #gui set up stuff
    root.title("Calibration Unit Control") #gui name
    root.geometry("700x400") #gui size

    app = MainApplication(root,ser,ser2) #set up gui class

    if mainloop:
        root.mainloop() #run gui loop
        
        #clean up in case user didn't hit exit calibration mode button: 
        #make sure all arduino pins in low mode
        ser.write(bytes('L'))
        ser.write(bytes('M'))
        #ser2.write(bytes('L'))

        #make sure all plugs used just for calibration are now off
        switch2[1].state='OFF'
        switch2[2].state='OFF'
        switch2[3].state='OFF'


def run_calib_gui_standalone():

    #port for flipper arduino
    fport='/dev/ttyACM0'

    #port for sphere arduino
    sport='/dev/ttyACM1'

    setup_arduinos(fport,sport)
    
    print 'activating gui'
    root = Tk() #gui set up stuff
    root.title("Calibration Unit Control") #gui name
    root.geometry("700x400") #gui size

    app = MainApplication(root) #set up gui class

    root.mainloop() #run gui loop
    
    #clean up in case user didn't hit exit calibration mode button: 
    #make sure all arduino pins in low mode
    ser.write(bytes('L'))
    ser.write(bytes('M'))
    #ser2.write(bytes('L'))

    #make sure all plugs used just for calibration are now off
    switch2[1].state='OFF'
    switch2[2].state='OFF'
    switch2[3].state='OFF'

if __name__ == '__main__':
    #run_calib_gui()
    pass
