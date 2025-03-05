sudo chmod 777 /dev/ttyACM0
source /home/$USER/minibot_pi_interface/install/setup.bash
ros2 launch tb3_hw_interface tb3_hw.launch.py use_lidar:='false' use_rsp:='false'