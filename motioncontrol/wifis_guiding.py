import matplotlib.pyplot as mpl
import time
import socket
import numpy as np
#import fli_controller as flic
import urllib as url
try:
    import FLI
except:
    pass    
import WIFISastrometry as WA
from glob import glob
from astropy.io import fits


# !!IMPORTANT!!: Before guiding can work we need to characterize the offset of the 
#                guiding field from the primary field.

###########################
### SIMPLE GUIDING PLAN ###
# SETUP
# NEED: 
#   1)  Offset from the guiding field to the primary field
#   2)  Rotation angle from the star
#   3)  Rough estimate of the plate scale of the guide camera
#
# PLAN:
#   1)  To get the offset we need to point the telescope at a star field
#           and then determine the location of stars in the guide field.
#           Both of these need the ability to download UNSO data.
#   2)  Rotation angle can be pulled from the telemetry
#   3)  Estimate of the plate scale take two images and then calculate the distance
#           travelled as a function of RA and DEC
################

# Use the command RADECGUIDE X.XX X.XX to move the telescope. X.XX in arcsec

f = open('/home/utopea/elliot/ipguiding.txt','r')
lines = f.readlines()

IPADDR = lines[0][:-1]
PORT = int(lines[1][:-1])

TELID = "BOK"
REF_NUM = 123
REQUEST = "ALL"

keyList = ["ID"            ,
        "SYS"           ,
        "REF_NUM"       ,
        "MOT"           ,
        "RA"            ,
        "DEC"           ,
        "HA"            ,
        "ST"            ,
        "EL"            ,
        "AZ"            ,
        "SECZ"          ,
        "EQ"            ,
        "JD"            ,
        "WOBBLE"        ,
        "DOME"          ,
        "UT"            ,
        "IIS"]

def connect_to_telescope():
    #instantiate the socket class
    telSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    telSock.settimeout(0.5)

    #IPADDR = telSock.gethostbyname(HOST)
    telSock.connect((IPADDR,PORT)) #Open the socket

    return telSock

def query_telescope(telSock, reqString):
    """Sends a query or a command to the telescope and returns the telescope 
    response"""

    print("QUERYING: %s" % (reqString))
    
    telSock.send(reqString)
    resp = ""
    test = True

    #Grab 100 bytes at a time from the socket and check for timeouts.
    while test:
        try:
            inStuff = telSock.recv(100)
        except socket.timeout:
            if resp:
                print("###\tDONE RECEIVING TELEMETRY\t###")
            test = False
            break

        if inStuff:
            resp += inStuff
        else:
            test = False
    
    #Turn string into list, separated by whitespace
    resp = resp.split(' ')
    cleanResp = []

    #Remove empty elements and newlines
    for char in resp:
        if char != '' and not char.endswith("\n"):
            cleanResp.append(char)
        elif char.endswith("\n"):
            cleanResp.append(char[:-1])

    return cleanResp
    
def get_telemetry(telSock):
    """Inititates connection to telescope and gets all telemetry data"""

    reqString = "%s TCS %i REQUEST ALL" % (TELID, REF_NUM)

    cleanResp = query_telescope(telSock, reqString)
    
    #gather the telemetry into a dict
    telemDict = {}
    II = 0
    for key in keyList:
        telemDict[key] = cleanResp[II]
        II += 1

    return telemDict


def check_moving(telSock):

    reqString = "%s TCS %i REQUEST MOT" % (TELID, REF_NUM)
    
    resp = query_telescope(telSock, reqString)
    mov = resp[-1]
    sleep(1)
    
    return mov

def clean_telem(telemDict):

    #print telemetry data in a clean way
    print "\n"
    print "|\t  BOK TELEMETRY       \t"
    for (key, value) in telemDict.iteritems():
        print "|%s\t|\t%s|" % (key.ljust(10), value.ljust(12))

def write_telemetry(telemDict):

    f = open('/home/utopea/WIFIS-Team/controlcode/BokTelemetry.txt', 'w')
    f.write('Timestamp: %s\n' % (time.ctime(time.time())))
    for (key,value) in telemDict.iteritems():
        f.write("%s:\t\t%s\n" % (key, value))
    
    f.close()

def wifis_simple_guiding(telSock):

    #Some constants that need defining
    plate_scale = 0.2988 #"/pixel
    exptime = 1000

    telemDict = get_telemetry(telSock)
    write_telemetry(telemDict)
    rotangle = telemDict['IIS']
  
    
    camSN = "ML0240613"
    #Take image with guider (with shutter open)
    cam = FLI.USBCamera.locate_device(camSN)
    cam.set_exposure(exptime, frametype="dark")
    dark = cam.take_photo()

    cam.set_exposure(exptime, frametype="normal")
    cam.end_exposure()
    img1 = cam.take_photo()
    img1size = img1.shape
   
    img1 = img1 - dark

    #check positions of stars    
    centroidx, centroidy, Iarr, Isat = WA.centroid_finder(img1, plot=False)
    bright_stars = np.argsort(Iarr)[::-1]
  
    #Choose the star to track
    guiding_star = bright_stars[0]
    for star in bright_stars:
        if (centroidx[star] > 50 and centroidx[star] < 950) and \
            (centroidy[star] > 50 and centroidy[star] < 950):
            if Isat[star] != 1:
                guiding_star = star
                break 
    
    stary1 = centroidx[guiding_star]
    starx1 = centroidy[guiding_star] 

    check_guidestar = True
    if check_guidestar:
        mpl.imshow(img1, cmap = 'gray',interpolation='none', origin='lower')
        mpl.plot(starx1, stary1, 'ro', markeredgecolor = 'r', markerfacecolor='none', markersize = 5)
        mpl.show()

    #LOOP: 
        #Take image, same frame, calculate new position
        #calculate distance in xy and convert to ra,dec
        #send command to telescope
        #sleep for a few seconds?
    while True:
        img = cam.take_photo(shutter='open')
        boxsize = 30
        imgbox = img[stary1-boxsize:stary1+boxsize, starx1-boxsize:starx1+boxsize]
        
        mpl.imshow(imgbox)
        mpl.show()
        
        centroidx, centroidy, Iarr, Isat = WA.centroid_finder(imgbox, plot=False)
        new_loc = np.argmax(Iarr)
        newy = centroidx[new_loc]
        newx = centroidy[new_loc]

        dx = newx - boxsize 
        dy = newy - boxsize

        print dx, dy
        
        ###do the conversion to a delta RA and delta DEC
        #ra_adj = ??
        #dec_adj = ??
        
        ###Send the movement to the telescope
        #reqString = "%s TCS %i RADECGUIDE %.2f %.2f" % (TELID, REF_NUM, ra_adj, dec_adj)
        #resp = query_telescope(telSock, reqString)
        #print "Moving the telescope: %.2f %.2f" % (ra_adj, dec_ajd)
     
    #resp = query_telescope(telSock, reqString)


    #Remember to close the shutter
    return starx1, stary1
    
def wifis_guiding_test():
    #Some constants that need defining
    plate_scale = 1.0
    exptime = 500

    #Take image with guider (with shutter open)
    f = fits.open('/Users/relliotmeyer/Desktop/imgtest.fits')
    img1 = f[0].data
    img1size = img1.shape

    #check positions of stars    
    centroidx, centroidy, Iarr, Isat = WA.centroid_finder(img1)
    bright_stars = np.argsort(Iarr)
    
    #Choose the star to track
    guiding_star = bright_stars[0]
    for star in bright_stars:
        if (centroidx[star] > 30 and centroidx[star] < 240) and \
            (centroidy[star] > 30 and centroidy[star] < 240):
            if Isat[star] != 1:
                guiding_star = star
                
    starx1 = centroidx[guiding_star]
    stary1 = centroidy[guiding_star]
    
    #LOOP: 
        #Take image, same frame, calculate new position
        #calculate distance in xy and convert to ra,dec
        #send command to telescope
        #sleep for a few seconds?
    #while True:
    images = glob("/Users/relliotmeyer/Desktop/guidingtest/*.fits")
    for img2f in images:
        
        img2fl = fits.open(img2f)
        img2 = img2fl[0].data
        
        #img2 = cam.take_photo()
        starx1int = int(starx1)
        stary1int = int(stary1)
        xcorr = starx1 % starx1int
        ycorr = stary1 % stary1int
        boxsize = 40
        imgbox = img2[starx1int-boxsize:starx1int+boxsize, stary1int-boxsize:stary1int+boxsize]

        centroidx, centroidy, Iarr, Isat = WA.centroid_finder(imgbox)
        new_loc = np.argmax(Iarr)

        newx = centroidx[new_loc]
        newy = centroidy[new_loc]
    
        dx = newx - boxsize - xcorr
        dy = newy - boxsize - ycorr

        print starx1, stary1, newx, newy, dx, dy

        ###do the conversion to a delta RA and delta DEC
        #ra_adj = ??
        #dec_adj = ??
        
        ###Send the movement to the telescope
        #reqString = "%s TCS %i RADECGUIDE %.2f %.2f" % (TELID, REF_NUM, ra_adj, dec_adj)
        #resp = query_telescope(telSock, reqString)
        #print "Moving the telescope: %.2f %.2f" % (ra_adj, dec_ajd)
        
    #resp = query_telescope(telSock, reqString)

    
if __name__ == '__main__':

    telSock = connect_to_telescope()
    
    telemDict = get_telemetry(telSock)
    print(clean_telem(telemDict))
    
    wifis_simple_guiding(telSock) 

    #ra_adj = 9.00
    #dec_adj = 9.00
    
    #reqString = "%s TCS %i RADECGUIDE %.2f %.2f" % (TELID, REF_NUM, ra_adj, dec_adj)
    
    #resp = query_telescope(telSock, reqString)
    #print(resp)
    
    #while check_moving(telSock) != '0':
    #    sleep(5)
    #    continue
    
    #telemDict = get_telemetry(telSock)
    #print(clean_telem(telemDict))

