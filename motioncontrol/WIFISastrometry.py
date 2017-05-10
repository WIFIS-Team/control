import matplotlib.pyplot as mpl
import numpy as np
import urllib as url
from astropy.io import fits

def grabUNSOfield(ra, dec):
    """Takes an ra and dec as grabbed from the telemetry and returns a field
    from UNSO for use in solving the guider field"""
    
    ra_offset = '000000.00'
    dec_offset = '000000.00'

    ra_deg = ra_conv(ra)
    dec_deg = dec_conv(dec)

    fov_am =5.1
    name, rad, ded, rmag = unso(ra_deg,dec_deg, fov_am)
    
    return [name, rad, ded, rmag]

def centroid_finder(img, plot = False):

    imgsize = img.shape

    #find bright pixels
    imgmean = np.mean(img)
    imgstd = np.std(img)
    brightpix = np.where(img >= imgmean + 2.5* imgstd)
    new_img = np.zeros(imgsize)
    for i in range(len(brightpix[0])):
        new_img[brightpix[0][i],brightpix[1][i]] = 1.0

    #mpl.imshow(new_img)
    #mpl.show()

    stars = []
    for x in range(imgsize[0]):
        for y in range(imgsize[1]):
            if new_img[x,y] == 1:
                new_star, new_img = explore_region(x,y,new_img)
                stars.append(new_star)
    
    centroidx, centroidy, Iarr, Isat = [],[],[],[]
    for star in stars:
        xsum, ysum, Isum = 0.,0.,0.
        sat = False
        for i in range(len(star[0])):
            x = star[0][i]
            y = star[1][i]
            I = img[x,y]
            xsum += x*I
            ysum += y*I
            Isum += I
            if I == 65536:
                sat = True
        
        if sat == True:
            Isat.append(1)
        else:
            Isat.append(0)
        centroidx.append(xsum/Isum)
        centroidy.append(ysum/Isum)
        Iarr.append(Isum)
        
    if plot:
        mpl.imshow(img, cmap = 'gray', interpolation='none')
        mpl.plot(centroidy, centroidx, 'ro', markeredgecolor = 'r', markerfacecolor='none',\
            markersize = 5)
        mpl.show()
        mpl.close()

    return [centroidx,centroidy,Iarr, Isat]

def explore_region(x,y, img):
 
    xreg = [x]
    yreg = [y]
    img[x,y] = 0
    imgcopy = np.array(img)

    for k,x in enumerate(xreg):
        y = yreg[k]
        for i in range(-1,2):
            for j in range(-1,2):
                if (x+i > 0 and x+i < img.shape[0]) and (y+j > 0 and y+j < img.shape[1])\
                    and (img[x+i,y+j] == 1):
                    xreg.append(x+i)
                    yreg.append(y+j)
                    img[x+i,y+j] = 0

    region = np.array([np.array(xreg), np.array(yreg)])
    
    return region, img

def determine_brightest():

def write_telemetry(telemDict):

    f = open('/home/utopea/WIFIS-Team/controlcode/BokTelemetry.txt', 'w')
    
    for key in telemDict:
        
        f.write()




def check_focus(img, sideregions = 3):

    imgshape = img.shape
    
    regionx = imgshape[0]/sideregions
    regiony = imgshape[1]/sideregions
    
    for xreg in range(sideregions):
        for yreg in range(sideregions):
            imgregion = img[regionx*xreg:regionx*(xreg+1), regiony*yreg:regiony*(yreg+1)]
            centroidarr = centroid_finder(imgregion)

def unso(radeg,decdeg,fovam): # RA/Dec in decimal degrees/J2000.0 FOV in arc min. import urllib as url
    
    str1 = 'http://webviz.u-strasbg.fr/viz-bin/asu-tsv/?-source=USNO-B1'
    str2 = '&-c.ra={:4.6f}&-c.dec={:4.6f}&-c.bm={:4.7f}/{:4.7f}&-out.max=unlimited'.format(radeg,decdeg,fovam,fovam)

    # Make sure str2 does not have any spaces or carriage returns/line feeds when you # cut and paste into your code
    URLstr = str1+str2
    f = url.urlopen(URLstr)
    # Read from the object, storing the page's contents in 's'.
    s = f.read()
    f.close()
   
    sl = s.splitlines()
    sl = sl[45:-1]
    name = np.array([])
    rad = np.array([])
    ded = np.array([])
    rmag = np.array([])
    for k in sl:
        kw = k.split('\t')
        name = np.append(name,kw[0])
        rad = np.append(rad,float(kw[1]))
        ded = np.append(ded,float(kw[2]))
        if kw[12] != '     ': # deal with case where no mag is reported
            rmag = np.append(rmag,float(kw[12]))
        else:
            rmag = np.append(rmag,np.nan) 
        
    return name,rad,ded,rmag

def ra_conv(ra, degrees=True):

    if degrees:
        h = float(ra[0:2])
        m = float(ra[2:4])
        s = float(ra[4:9])

        deg = (h/24 + m/24/60 + s/24/60/60)*360

        return deg

    if not degrees:
        ra = float(ra)
        h = int(np.floor(ra / 360 * 24))
        m = int(np.floor((ra - h/24*360)/360 * 24 * 60))
        s = round(float((ra*24*60/360 - h*60 - m) * 60),2)

        hms_out = str(h) + str(m) + str(s)

        return hms_out

def dec_conv(dec, degrees=True):

    if degrees:
        sign = np.sign(float(dec[0:3]))
        deg = float(dec[0:3]) + sign*float(dec[3:5])/60. + sign*float(dec[5:])/3600.
        return deg

def ra_adjust(ra, d_ra, action = 'add'):
    '''Adjusts RA by the specified amount and returns a single string.
    Inputs are hhmmss.ss. Can add or sub. Default is add.'''
    
    h = float(ra[0:2])
    m = float(ra[2:4])
    s = float(ra[4:9])

    ra_l = np.array([h,m,s])

    dh = float(d_ra[0:2])
    dm = float(d_ra[2:4])
    ds = float(d_ra[4:9])

    dra_l = np.array([dh,dm,ds])

    if action == 'add':
        new_ra = ra_l + dra_l
        
        if new_ra[2] >= 60.0:
            new_ra[1] += 1.0
            new_ra[2] -= 60.0
            if new_ra[1] >= 60.0:
                new_ra[0] += 1.0
                new_ra[1] -= 60.0
                if new_ra[0] >= 24.0:
                    new_ra[0] -= 24.0

    if action == 'sub':
        new_ra = ra_l - dra_l

        if new_ra[2] < 0.0:
            new_ra[1] -= 1.0
            new_ra[2] += 60.0
            if new_ra[1] < 0.0:
                new_ra[0] -= 1.0
                new_ra[1] += 60.0
                if new_ra[0] <= 0.0:
                    new_ra[0] += 24.0

    
    return str(new_ra[0]) + str(new_ra[1]) + str(round(new_ra[2],2))


if __name__ == '__main__':

    f = fits.open('/Users/relliotmeyer/Desktop/imgtest.fits')
    img = f[0].data

    x = centroid_finder(img) 