import time
import serial

def uart_communication_angle(angle):
    print ("[INFO]Enviando comando para posicionar o angulo da jogada")
    ser = serial.Serial('/dev/ttyS0', baudrate=9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS
                        )
    try:
        #data1 = input("Enter the data to be sent: ")
        #ser.write(bytes('1', 'UTF-8'))
        #ser.write(bytes(position, 'UTF-8'))
        ser.write(bytes(angle, 'UTF-8'))
        #ser.write(position)
        print ("[UART]Posicionando lancador no angulo da jogada")
        #time.sleep(10)
        
        while True:
            if ser.inWaiting()>0:
                data = ser.read()
                #data = data.decode('utf-8')
                print(data)
                if((data.decode('utf-8')) == "Y"):
                    print("[INFO]Confirmacao recebida")
                    return True
            
    except KeyboardInterrupt:
        print ("Exiting program")

    except:
        print ("Error Occurs, Exiting program")

    finally:
        ser.close()
        pass



def uart_communication_position(position):
    print ("[INFO]Enviando comando para posicionar no trilho")
    print(position)
    ser = serial.Serial('/dev/ttyS0', baudrate=9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS
                        )
    try:
        #data1 = input("Enter the data to be sent: ")
        #ser.write(bytes('1', 'UTF-8'))
        #ser.write(bytes(position, 'UTF-8'))
        ser.write(bytes(position, 'UTF-8'))
        #ser.write(position)
        print ("[UART]Posicionando lancador no trilho - Aguardando confirmacao")

        #time.sleep(10)
        
        while True:
            if ser.inWaiting()>0:
                data = ser.read()
                #data = data.decode('utf-8')
                print(data)
                if((data.decode('utf-8')) == "Y"):
                    print("[INFO]Confirmacao recebida")
                    return True
            
    except KeyboardInterrupt:
        print ("Exiting program")

    except:
        print ("Error Occurs, Exiting program")

    finally:
        ser.close()
        pass


def uart_communication_shot(play):
    print ("[INFO]Enviando comando para realizar jogada")

    ser = serial.Serial('/dev/ttyS0', baudrate=9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS
                        )
    try:
        #data1 = input("Enter the data to be sent: ")
        ser.write(bytes(play, 'UTF-8'))
        print ("[UART]Jogada enviada - Aguardando confirmacao de realizacao")

        #time.sleep(10)
        
        while True:
            if ser.inWaiting()>0:
                data = ser.read()
                #data = data.decode('utf-8')
                if((data.decode('utf-8')) == "Y"):
                    print("[INFO]Confirmacao recebida")
                    return True        
        while True:
            if ser.inWaiting()>0:
                data = ser.read()
                #data = data.decode('utf-8')
                if((data.decode('utf-8')) == "Y"):
                    return True
            
    except KeyboardInterrupt:
        print ("Exiting program")

    except:
        print ("Error Occurs, Exiting program")

    finally:
        ser.close()
        pass

def sendPlays(play):
    responseShot = uart_communication_shot(play)
    if(responseShot == True):
        return True
    else:
        sendPlays(play)
"""
if __name__ == '__main__':
    responsePosition = uart_communication_position('2')
        
    if(responsePosition == True):
        for i in range(1,11):
            #print(listO)
            print("Mandando a jogada",i)
            sendPlays('a')
            time.sleep(3)
    
    uart_communication_position('2')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    uart_communication_shot('a')
    time.sleep(3)
    """
