#!/usr/bin/python
import serial, os, time, sys, datetime, csv

def logfilename():
    now = datetime.datetime.now()
    #Colon is not alowed in filenames so we have to include a lookalike char 
    return 'CO2LOG-%0.4d-%0.2d-%0.2d-%0.2d%s%0.2d%s%0.2d.csv' % \
            (now.year, now.month, now.day, now.hour, \
            u'ua789',now.minute, u'ua789', now.second)

#Function to calculate MH-Z19 crc according to datasheet
def crc8(a):
    crc=0x00
    count=1
    b=bytearray(a)
    while count<8:
        crc+=b[count]
        count=count+1
    #Truncate to 8 bit
    crc%=256
    #Invert number with xor
    crc=~crc&0xFF
    crc+=1
    return crc

    # try to open serial port
port='/dev/ttyS0'
sys.stderr.write('Trying port %s..' % port)

try:
    # try to read a line of data from the serial port and parse    
    with serial.Serial(port, 9600, timeout=2.0) as ser:
        # 'warm up' with reading one input
        result=ser.write("xffx01x86x00x00x00x00x00x79")
        time.sleep(0.1)
        s=ser.read(9)
        z=bytearray(s)
        # Calculate crc
        crc=crc8(s) 
        if crc != z[8]:
            sys.stderr.write('CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %dn' % (crc, z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[8]))
        else:
            sys.stderr.write('Logging data on %s to %sn' % (port, logfilename()))
        # log data
        outfname = logfilename()
        with open(outfname, 'a') as f:
        # loop will exit with Ctrl-C, which raises a KeyboardInterrupt
            while True:
                #Send "read value" command to MH-Z19 sensor
                result=ser.write("xffx01x86x00x00x00x00x00x79")
                time.sleep(0.1)
                s=ser.read(9)
                z=bytearray(s)
                crc=crc8(s)
                #Calculate crc
                if crc != z[8]:
                    sys.stderr.write('CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %dn' % (crc, z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[8]))
                else:
                    if s[0] == "xff" and s[1] == "x86":
                        print "co2=", ord(s[2])*256 + ord(s[3])
                co2value=ord(s[2])*256 + ord(s[3])
                now=time.ctime()
                parsed=time.strptime(now)
                lgtime=time.strftime("%Y %m %d %H:%M:%S")
                row=[lgtime,co2value]
                w=csv.writer(f)
                w.writerow(row)
                #Sample every minute, synced to local time
                t=datetime.datetime.now()
                sleeptime=60-t.second
                time.sleep(sleeptime)
except Exception as e:
    f.close()
    ser.close()
    sys.stderr.write('Error reading serial port %s: %sn' % (type(e).__name__, e))
except KeyboardInterrupt as e:
    f.close()
    ser.close()
    sys.stderr.write('nCtrl+C pressed, exiting log of %s to %sn' % (port, outfname))
