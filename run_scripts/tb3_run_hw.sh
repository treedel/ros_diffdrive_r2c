sudo chmod 777 /dev/ttyACM0
sudo chmod 777 /dev/ttyUSB0
source /home/$USER/minibot_pi_interface/install/setup.bash
ros2 launch tb3_hw_interface tb3_hw.launch.py use_rsp:='false'