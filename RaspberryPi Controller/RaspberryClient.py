"""
Reference:
PiCamera documentation
https://picamera.readthedocs.org/en/release-1.10/recipes2.html

"""

import io
import socket
import struct
import time
import picamera
from threading import Thread
import serial

class ServerStart(Thread):
    def __init__(self,ip):
        Thread.__init__(self)
        self.ip = ip
        self.ip = 8001
        print 'Starting Server '+ ip + ':'+str(port)
        self.usbCom = serial.Serial('/dev/ttyACM0', 9600)
	if not self.usbCom.isOpen():
            self.usbCom.open()
        
    def run(self):
        while True:
            data = conn.recv(2048)
            print 'Server received data: ', data
            if data == "":
                break
            elif data == 'forward':
                self.usbCom.write('1')
            elif data == 'left':
                self.usbCom.write('2')
            elif data == 'right':
                self.usbCom.write('3')
            elif data == 'reverse':
                self.usbCom.write('4')
            else:
                self.usbCom.write('0')
            #If I needa send data back!
            #MESSAGE = raw_input('MTPS: Response from Server/Enter exit:')
            #if MESSAGE == 'exit':
                #break
            #conn.send(MESSAGE) #echo
                
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind(('0.0.0.0',8001))
tcpServer.listen(1)
print 'Waiting for a Stevens Mac... '
(conn, (ip,port)) = tcpServer.accept()
newThread = ServerStart(ip)
newThread.start()
time.sleep(2)


print 'Sending video feed...'
# create socket and bind host
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.1.5', 8003)) #Server connecting tos' ip
connection = client_socket.makefile('wb')

try:
    with picamera.PiCamera() as camera:
	camera.vflip = True
	#camera.resolution = (820, 480)
        camera.resolution = (320, 240)      # pi camera resolution
        camera.framerate = 10               # 10 frames/sec
        time.sleep(2)                       # give 2 secs for camera to initilize
        start = time.time()
        stream = io.BytesIO()
        
        # send jpeg format video stream
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            if time.time() - start > 600:
                break
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
