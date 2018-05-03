import numpy as np
from numpy import ones,vstack
from numpy.linalg import lstsq
import cv2
import serial
import pygame
from pygame.locals import *
import socket
import time
import os
from statistics import mean
from threading import Thread

class ClientSendThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.ip = '192.168.1.24' #Client IP
        self.port = 8001
        self.MESSAGE = ''
        self.BUFFER_SIZE = 2000
        self.tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.tcpClientA.connect((self.ip, self.port))
        BUFFER_SIZE = 2000
        #while self.MESSAGE != 'exit':
            #print "--------------Sending left MESSAGE!!!!!!!!------------"
            #self.tcpClientA.send(self.MESSAGE)
            #data = self.tcpClientA.recv(self.BUFFER_SIZE)
            #print " Client2 received data:", data
            #MESSAGE = raw_input("tcpClientA: Enter message to continue/ Enter exit:")

        #tcpClientA.close()

    def setMessage(self, mess):
        self.tcpClientA.send(mess)


class RecCam(object):

    def __init__(self):
        #bluetooth module finding
        #print "performing inquiry..."
        #nearby_devices = discover_devices(lookup_names = True)
        #print "found %d devices" % len(nearby_devices)
        #for name, addr in nearby_devices:
             #print " %s - %s" % (addr, name)

        self.newthread = ClientSendThread()
        self.newthread.start()

        #Networking
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8003)) #Host ip
        self.server_socket.listen(0)

        # accept a single connection
        self.connection = self.server_socket.accept()[0].makefile('rb')

        # connect to a seral port
        #self.ser = serial.Serial('/dev/tty.usbmodem1421', 115200, timeout=1)
        #self.send_inst = True

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        pygame.init()
        self.collect_image()

    def collect_image(self):
        valid = False
        remoteActive = False
        while not valid:
            userInput = raw_input("Will you be controlling the car manually? (y/n) ")
            if userInput == "y" or userInput == "Y":
                valid = True
                remoteActive = True
            elif userInput == "n" or userInput == "N":
                valid = True
                remoteActive = False
            else:
                valid = False
                print "Invalid input, please try again."

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print 'Camera Feed Streaming.'
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')

        # stream video frames one by one
        try:
            stream_bytes = ' '
            frame = 1
            while 1:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

                    # select lower half of the image
                    roi = image[120:240, :]

                    # save streamed images
                    #cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), image)

                    #cv2.imshow('roi_image', roi)
                    white,orig, m1, m2 = process_img(image)
                    cv2.imshow('image', white)
                    cv2.imshow('window2', orig)
                    # reshape the roi image into one row array
                    temp_array = roi.reshape(1, 38400).astype(np.float32)
                    #temp_array = roi.reshape(1, 98400).astype(np.float32)


                    #------------- Controls!!! ---------------
                    if remoteActive:
                        # get input from human driver
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_UP:
                                    self.newthread.setMessage("forward")
                                elif event.key == pygame.K_DOWN:
                                    self.newthread.setMessage("reverse")
                                elif event.key == pygame.K_LEFT:
                                    self.newthread.setMessage("left")
                                elif event.key == pygame.K_RIGHT:
                                    self.newthread.setMessage("right")
                            elif event.type == pygame.KEYUP:
                                self.newthread.setMessage("stop")
                    else:
                        #Determine slopes here!
                        if m1 < 0 and m2 < 0:
                            self.newthread.setMessage("right")
                        elif m1 > 0 and m2 > 0:
                            self.newthread.setMessage("left")
                        else:
                            self.newthread.setMessage("stop")

                    frame += 1
                    total_frame += 1

                    # get input from human driver
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            key_input = pygame.key.get_pressed()

                            # complex orders

            # save training images and labels
            train = image_array[1:, :]
            train_labels = label_array[1:, :]

            # save training data as a numpy file
            file_name = str(int(time.time()))
            directory = "training_data"
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                np.savez(directory + '/' + file_name + '.npz', train=train, train_labels=train_labels)
            except IOError as e:
                print(e)

            e2 = cv2.getTickCount()
            # calculate streaming duration
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print 'Streaming duration:', time0

            print(train.shape)
            print(train_labels.shape)
            print 'Total frame:', total_frame
            print 'Saved frame:', saved_frame
            print 'Dropped frame', total_frame - saved_frame

        finally:
            self.connection.close()
            self.server_socket.close()

def process_img(image):
    #Cam Res = 320x240
    vertices = np.array([[0,320],[0,70],[40,40],[90,40],[75,200],[235,200],[230,40],[280,40],[320,70],[320,240],], np.int32)
    #vertices = np.array([[0,240],[0,50],[20,50],[120,200],[240,200],[300,50],[320,50],[320,240],], np.int32)
    high_thresh, thresh_im = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lowThresh = 0.5*high_thresh
    #print "High Thresh: " + str(high_thresh)
    #print "Low Thresh: " + str(lowThresh)
    #high_thresh = 120
    #lowThresh = 60
    processed_img = cv2.Canny(image, lowThresh, high_thresh)
    processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
    processed_img = MyROI(processed_img, [vertices])
    #parameters for HoughlinesP: image, rho, theta, threshold, min_length, max_length
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 60, 5, 50)
    draw_lines(processed_img,lines)
    m1 = 0
    m2 = 0
    try:
        l1, l2, m1, m2 = draw_lanes(image,lines)
        cv2.line(image, (l1[0], l1[1]), (l1[2], l1[3]), [0,255,0], 10)
        cv2.line(image, (l2[0], l2[1]), (l2[2], l2[3]), [0,255,0], 10)
    except Exception as e:
        #print(str(e)) none iterable error. To print error.
        pass
    try:
        for coords in lines:
            coords = coords[0]
            try:
                cv2.line(processed_img, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 3)


            except Exception as e:
                print(str(e))
    except Exception as e:
        pass

    return processed_img, image, m1, m2

def draw_lines(img,lines):
    try:
        for line in lines:
            coords = line[0]
            cv2.line(img, (coords[0],coords[1]), (coords[2],coords[3]), [255,255,255], 3)
    except:
        print 'faulty @ line 202'

def draw_lanes(img, lines, color=[0, 255, 255], thickness=3):

    # if this fails, go with some default line
    try:

        # finds the maximum y value for a lane marker
        # (since we cannot assume the horizon will always be at the same point.)

        ys = []
        for i in lines:
            for ii in i:
                ys += [ii[1],ii[3]]
        min_y = min(ys)
        max_y = 600
        new_lines = []
        line_dict = {}

        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = vstack([x_coords,ones(len(x_coords))]).T
                m, b = lstsq(A, y_coords)[0]

                # Calculating our new, and improved, xs
                x1 = (min_y-b) / m
                x2 = (max_y-b) / m

                line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
                new_lines.append([int(x1), min_y, int(x2), max_y])

        final_lanes = {}

        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2]

            if len(final_lanes) == 0:
                final_lanes[m] = [ [m,b,line] ]

            else:
                found_copy = False

                for other_ms in final_lanes_copy:

                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                final_lanes[other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [ [m,b,line] ]

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]

        def average_lane(lane_data):
            x1s = []
            y1s = []
            x2s = []
            y2s = []
            for data in lane_data:
                x1s.append(data[2][0])
                y1s.append(data[2][1])
                x2s.append(data[2][2])
                y2s.append(data[2][3])
            return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s))

        l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
        l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

        return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2], lane1_id, lane2_id
    except Exception as e:
        pass
        #print(str(e))

def MyROI(img, vertices):

    #blank mask:
    mask = np.zeros_like(img)

    #filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, 255)

    #returning the image only where mask pixels are nonzero
    masked = cv2.bitwise_and(img, mask)
    return masked

if __name__ == '__main__':
    RecCam()
