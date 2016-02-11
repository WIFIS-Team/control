import serial
import time
import csv

def open_serial_port(ser_temp,ser_pressure):
    ser_temp.port = "/dev/ttyUSB0"
    ser_temp.baudrate = 57600 
    ser_temp.bytesize = serial.SEVENBITS
    ser_temp.stopbits=serial.STOPBITS_ONE
    ser_temp.parity=serial.PARITY_ODD
    ser_temp.timeout=0
    ser_temp.open()
    if ser_temp.isOpen():
        print 'Serial port opened - Lakeshore'
    else:
        print 'Unable to open serial port - Lakeshore'
        
    ser_pressure.port = '/dev/ttyUSB1'
    ser_pressure.baudrate = 9600
    ser_pressure.timeout=0
    ser_pressure.open()
    time.sleep(5)
    if ser_pressure.isOpen():
        print 'Serial port opened - MKS'
    else:
        print 'Unable to open serial port - MKS'

def read_pressure(ser_pressure):
    ser_pressure.write('@253PR4?;FF')
    time.sleep(1)
    result = ser_pressure.read(18)
    pressure = result[7:15]

    ser_pressure.flush()
    
    return pressure

def sendPacket(ser_temp,packetString): #send query message to T-controller and wait for response
    ser_temp.write(packetString)
    time.sleep(0.05)
    response = ser_temp.read(10)
    time.sleep(0.05)
    return response

def read_temperature(ser_temp):  
    currentTime = time.time()

    sensorList = ['A', 'B','C','D1','D2'] #name of inputs

    returnedString = []
    returnedString.append(time.asctime())
    returnedString.append(time.time())
    for sensor in sensorList:
        queryString = 'KRDG? '+sensor +'\n'
        result = sendPacket(ser_temp,queryString).replace('\r\n', '')
        returnedString.append(result)  
    
    return returnedString

ser_temp = serial.Serial()
ser_pressure = serial.Serial()

open_serial_port(ser_temp,ser_pressure)

fname = 'warmup02062016.csv'
outFileHeader = ['#Time Stamp','seconds since epoch', 'Input A',  'Input B','Input C','Input D1', 'Input D2','Pressure']

f = open(fname, 'wb')
outData = csv.writer(f, dialect='excel')
outData.writerow(outFileHeader)

while(True):
    outval = read_temperature(ser_temp)
    outval.append(read_pressure(ser_pressure))

    outData.writerow(outval)
    f.flush()
    print(outval)
    
f.close()    
