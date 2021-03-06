
import serial,time #You need the pyserial library
import struct,sys

#windows:
#ser = serial.Serial('COM3', 38400, timeout=0.01)

#linux:
try:
    ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=0.01)
except :
    print("Could not open serial port, please make sure \nthe board is connected and port number is correct")
    sys.exit()


#time.sleep(10);#my arduino bugs if data is written to the port after opening it
#filename='sonic.bin'#name of the rom, bin format
#f=open(name,'rb');
#with open(filename,'rb') as f:


print(" _____________________                                      ")
print("|     ______________  |__                                   ")
print("|    /              \    |          _               _       ")
print("|    \______________/    |      ___| |_ ___ ___ ___| |_      ")
print("|    ________________    |     | . | . |  _| .'|  _|  _|    ")
print("|    |              |    |     |_  |___|___|__,|_| |_|      ")
print("|    |              |    |     |___|                        ")
print("|    |              |    |                                  ")
print("|    |              |    |     A tool for reading data from ")
print("|    |              |    |     Game Boy cartridges.         ")
print("|    |______________|    |                 Robson Couto 2016")
print("|________________________|         www.dragaosemchama.com.br")

while True:
    print("===========================================")
    print("           What do you want do do?         ")
    print("                                           ")
    print("              1-dump                       ")
    print("              2-read save                  ")
    print("              3-burn save                  ")
    print("              5-cart info                  ")
    print("              7-restart                    ")
    print("              9-exit                       ")
    print("                                           ")
    print("===========================================")
    option=int(input())
    ramsize=32*1024
    print(option);
    if(option==1):
        name=input("What the name of the file?")
        romsize=int(input("What the size of the rom in KB?"))
        romsize=romsize*1024
        ser.flushInput()
        ser.write(bytes("a","ASCII"))
        ser.write(bytes("b","ASCII"))
        ser.write(bytes("c","ASCII"))
        numBytes=0
        f = open(name, 'wb')
        while (numBytes<romsize):
            while ser.inWaiting()==0:
                print("waiting...\n",numBytes)
                time.sleep(0.1)
            data = ser.read(1)#must read the bytes and put in a file
            f.write(data)
            numBytes=numBytes+1
        f.close()
    if(option==2):
        ser.flushInput()
        ser.write(bytes("a","ASCII"))
        ser.write(bytes("b","ASCII"))
        ser.write(bytes("y","ASCII"))
        time.sleep(1)
        numBytes=0
        name=input("What the name of the file?")
        f = open(name, 'wb')#yes, that simple
        timeout=20
        while (numBytes<ramsize and timeout>0):
            timeout=20
            while ser.inWaiting()==0:
                print("waiting...\n",numBytes)
                time.sleep(0.1)
                timeout=timeout-1
                print("timeout:",timeout)
                if(timeout==0):
                    break
            data = ser.read(1)#must read the bytes and put in a file
            f.write(data)
            numBytes=numBytes+1
        f.close()

    if(option==3):
        name=input("What's the name of the file?")
        ramsize=int(input("Please insert the size of RAM file in kB?"))
        ramsize=1024*ramsize
        numblocks=ramsize/128;
        print(name)
        print(numblocks)
        f = open(name, 'rb')
        for i in range(int(numblocks)):
            ser.flushInput()
            ser.write(bytes("a","ASCII"))
            ser.write(bytes("b","ASCII"))
            ser.write(bytes("k","ASCII"))
            time.sleep(0.001)
            ser.write(struct.pack(">B",i>>8))
            CHK=i>>8
            time.sleep(0.001)
            ser.write(struct.pack(">B",i&0xFF))
            CHK^=i&0xFF
            time.sleep(0.001)
            data=f.read(128);
            #print(data)
            for j in range(len(data)):
                 CHK=CHK^data[j]
            time.sleep(0.001)
            print("CHK:", CHK)
            response=~CHK
            while response!=CHK:
                #print("sending data")
                print("Writing data. Current porcentage:{:.2%}\n".format(i/numblocks),end='\r')
                ser.write(data)
                """When there was no delay between the two calls to ser.write, the board would glitch
                at 6.25%. The reason is unknown. Always at the same  point. Please if you understand
                why this works, send me a comment or message. Thanks"""
                time.sleep(0.001)
                ser.write(struct.pack(">B",CHK&0xFF))
                time.sleep(0.001)
                timeout=30
                while ser.inWaiting()==0:
                    time.sleep(0.01)
                    timeout=timeout-1
                    #print("timeout",timeout)
                    if timeout==0:
                        print("could not get a response, please start again\n")
                        break
                if(ser.inWaiting()>0):
                    response=ord(ser.read(1))
                    if response!=CHK:
                        print("wrong checksum, sending chunk again\n")
        f.close()


    if(option==4):
        name=input("What's the name of the file?")
        romsize=int(input("Please insert the size of ROM file in kB?"))
        romsize=1024*romsize
        MBC=int(input("Sorry, as the cartridge should be empty, there is no\n mean of knowning the memory controller type. \nCould you please insert the MCB number (1,2,3 or 5)?"))

        numblocks=romsize/128;
        print(name)
        print(numblocks)
        f = open(name, 'rb')
        for i in range(int(numblocks)):
            ser.flushInput()
            ser.write(bytes("a","ASCII"))
            ser.write(bytes("b","ASCII"))
            ser.write(bytes("b","ASCII"))
            time.sleep(0.001)
            ser.write(struct.pack(">B",i>>8))
            CHK=i>>8
            time.sleep(0.001)
            ser.write(struct.pack(">B",i&0xFF))
            CHK^=i&0xFF
            time.sleep(0.001)
            data=f.read(128);
            #print(data)
            for j in range(len(data)):
                 CHK=CHK^data[j]
            time.sleep(0.001)
            CHK^=MBC&0xFF
            print("CHK:", CHK)
            response=~CHK
            while response!=CHK:
                #print("sending data")
                print("Writing data. Current porcentage:{:.2%}\n".format(i/numblocks),end='\r')
                ser.write(data)
                time.sleep(0.001)

                ser.write(struct.pack(">B",MBC&0xFF))
                time.sleep(0.001)
                ser.write(struct.pack(">B",CHK&0xFF))
                time.sleep(0.001)
                timeout=300
                while ser.inWaiting()==0:
                    time.sleep(0.01)
                    timeout=timeout-1
                    #print("timeout",timeout)
                    if timeout==0:
                        print("could not get a response, please start again\n")
                        break
                if(ser.inWaiting()>0):
                    response=ord(ser.read(1))
                    if response!=CHK:
                        print("wrong checksum, sending chunk again\n")
        f.close()

    if(option==5):
        ser.flushInput()
        ser.write(bytes("a","ASCII"))
        ser.write(bytes("b","ASCII"))
        ser.write(bytes("d","ASCII"))
        time.sleep(1)
        while ser.inWaiting()>0:
            data = ser.readline()
            print(data.decode("ASCII"))#or utf-8
    if(option==6):
        ser.write(bytes("a","ASCII"))
        ser.write(bytes("b","ASCII"))
        ser.write(bytes("e","ASCII"))
        while ser.inWaiting()==0:
            print("waiting for reponse")
            time.sleep(1)
        data = ser.readline()
        print(data.decode("ASCII"))#or utf-8
    if(option==7):
        ser.flushInput()
        ser.write(bytes("a","ASCII"))
        ser.write(bytes("b","ASCII"))
        ser.write(bytes("r","ASCII"))
        time.sleep(1)
        while ser.inWaiting()>0:
            data = ser.readline()
            print(data.decode("ASCII"))#or utf-8
    if(option==8):
        while True:
            print("===========================================")
            print("In this mode, you can read and write bytes ")
            print("directly to the cartridge, select an option")
            print("below.                                     ")
            print("              1-read bytes                 ")
            print("              2-write byte                 ")
            print("              3-cancel                     ")
            print("                                           ")
            print("===========================================")
            option=int(input("Please, insert your option"))
            if(option==1):
                adr=int(input("Which byte?"),16)
                num=int(input("How many bytes (255 max)?"))
                print(num)
                print(adr)
                ser.flushInput()

                ser.write(bytes("a","ASCII"))
                ser.write(bytes("b","ASCII"))
                ser.write(bytes("f","ASCII"))
                ser.write(struct.pack(">B",adr&0xFF))
                ser.write(struct.pack(">B",adr>>8))
                ser.write(struct.pack(">B",num))
                time.sleep(1)
                #print("Byte")
                numBytes=0
                timeout=20
                while (numBytes<=num and timeout>0) or ser.inWaiting()>0:
                    timeout=20
                    while ser.inWaiting()==0:
                        time.sleep(0.1)
                        timeout=timeout-1
                        print("timeout:",timeout)
                        if(timeout==0):
                            break
                    data = ser.read()
                    #print(data.decode("ASCII"))
                    print(data)
                    numBytes=numBytes+1
            if(option==2):
                adr=int(input("Address?"),16)
                value=int(input("insert the byte you want to write?"),16)
                print(value)
                print(adr)
                ser.flushInput()

                ser.write(bytes("a","ASCII"))
                ser.write(bytes("b","ASCII"))
                ser.write(bytes("g","ASCII"))
                ser.write(struct.pack(">B",adr&0xFF))
                ser.write(struct.pack(">B",adr>>8))
                ser.write(struct.pack(">B",value))
                time.sleep(1)
                #print("Byte")
                while ser.inWaiting()>0:
                    data = ser.readline()
                    #print(data.decode("ASCII"))
                    print(data)
    if(option==9):
        break
    #ser.write(bytes(option));
    #time.sleep(0.05);#
