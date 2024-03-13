import serial.tools.list_ports
import time
from notification import notification

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portsList = []

for onePort in ports:
    portsList.append(str(onePort))
    print(str(onePort))

val = input("Select Port: COM")

for x in range(0,len(portsList)):
    if portsList[x].startswith("COM" + str(val)):
        portVar = "COM" + str(val)
        print(portVar)
 

serialInst.baudrate = 9600
serialInst.port = portVar
serialInst.open()

while True:
    if serialInst.in_waiting:
        packet = serialInst.readline()
        data = packet.decode('utf').rstrip('\n')
        print(data)
        
        try:
            number = float(data)
            if number > 6:
                notification()
                time.sleep(10)
        except ValueError:
            print("Dato recibido no es un número válido:", data)
    
        serialInst.reset_input_buffer()