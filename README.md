# Arduino-RaspberryPi-Car
This project uses a RaspberryPi to talk to the arduino, sending it commands such as stop, go, left right, etc. These commands are based either on user input or autonomous. If it is on autonomous mode, the Raspberry pi will capture video input to detect the bottom of the walls. This is done by sending a live video feed to your pc as the server. The Raspberry Pi and serer must have connection so the computations can be done on your pc. The wall detection is done by OpenCV using edge detection and I am currently working on implementing people detection with tensorflow to make it more robust.

<img width="924" alt="screen shot 2018-05-03 at 5 25 13 pm" src="https://user-images.githubusercontent.com/3750077/39606166-84ab7014-4ef9-11e8-9d7a-b75ee1e7a4bf.png">

The program works by trying to detect the longest lines in the stream and staying in between them. It draws lines and determines their slopes. If the line on the left has a smaller slopes, it turns a bit left to accomodate it. Same for the right to ensure both lines stay in the video stream. The Raspberry Pi communicates to the arduino through the serial bus.
This is very much a work in progress as well as updating this whenever I have time.

<img width="209" alt="screen shot 2018-05-03 at 6 36 11 pm" src="https://user-images.githubusercontent.com/3750077/39607488-e7dcb4ac-4f00-11e8-8b24-477a5b4fe530.png">
