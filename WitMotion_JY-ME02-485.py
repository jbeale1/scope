# Read out WitMotion JY-ME02-485 absolute angle encoder
# J.Beale 9/15/2024

# Witmotion Encoder command (9600 bps using USB-RS485 converter)
# Send this hex byte string:  50 03 00 04 00 20 08 52
# Receive 69 bytes back. B29,B30 are the 15-bit angle value, B28 is rotation #
# Receive string always starts with (B0...B5):
# 50 03 40 00 02 00 
# encoder resolves 360 degree angular position into 15-bit word: 0000 to 32767
# data packet also includes angular rate and sensor temperature


import serial
import time
import struct # unpack bytes to int

averages = 94  # how many readings to average together
maxCounts = 32768 # number of counts from 15-bit sensor (0..maxCounts-1)
degPerCount = 360.0 / (maxCounts) # angular scale factor of sensor

if __name__ == "__main__":
    port = 'COM6'  # or '/dev/ttyUSB0' etc. on Linux
    baudrate = 9600
    recLen = 69   # number of bytes expected from device
    # command to encoder to readout angle and angular rate
    cmd_bytes = bytes.fromhex('50 03 00 04 00 20 08 52')               

    with serial.Serial(port, baudrate, timeout=0.3) as ser:        
        junk = ser.read(200) # clear out existing data in serial buffer

        while True:
            angleSum = 0 # accumulated sum of angle readings
            validReads = 0 # how many good readings so far
            while (validReads < averages):            
                ser.write(cmd_bytes)
                recData = ser.read(recLen)
                recCount = len(recData)
                if (recCount != recLen): # got all expected data?
                    continue
                angleR = recData[29:31]
                angle = struct.unpack('>H', angleR)[0] # convert to 16-bit integer
                if (angle > (3*maxCounts)/4):  # put split at -90deg
                    angle = angle-maxCounts
                angleSum += angle
                validReads += 1

            angleDeg = degPerCount * (angleSum / validReads) # angle in degrees
            tEpoch = time.time()
            print("%0.1f, %5.3f" % (tEpoch,angleDeg))
