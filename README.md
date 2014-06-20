LaserBots
=========

Our 2014 summer project: a pair of laser-fighting cars controlled by raspberry pis in communication with a laptop.
There are 5 main components:
The server and the client communicate between the laptop and the pis on the cars. The server runs on the laptop; each pi is a client.
The server and client are responsible solely for ferrying data between the laptop and the pi.
Actual processing is done by the CarController (on the server side) and the Car (on the client side)
The CarController handles all controller input; the Car runs on the pi and controls the different components based on the data sent by the controller.
There will be one instance of both for each car.
The GUI is the graphical interface that displays on the laptop while the cars are running. 
It will show information such as the time remaining and how much health each car has.
The GUI will communicate with the CarController for each car.
