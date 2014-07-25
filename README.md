LaserBots

To use:
run server.py on the laptop (python server.py)
run client.py on each raspberry pi with laptop IP (sudo python client.py 192.168.#.#)

This requires the WiringPi library and ServoBlaster user daemon
for wiringpi:
sudo pip install wiringpi2

for ServoBlaster:
git clone https://github.com/richardghirst/PiBits.git
cd ServoBlaster/user
make servod
sudo make install
sudo ./servod --pcm

The --pcm is necessary so it does not use PWM hardware (which we need for the victor)