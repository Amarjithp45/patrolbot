#!/bin/bash
set -e

echo "=============================================="
echo " Starting ROS 2 Humble & Robotics Setup on Ubuntu 22.04"
echo "=============================================="

# 1. Set locale
sudo apt update && sudo apt install -y locales curl gnupg2 lsb-release software-properties-common
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 2. Add ROS 2 Repository
sudo add-apt-repository -y universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3. Update & Install ROS 2 Desktop + Tools
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-dev-tools \
  python3-colcon-common-extensions \
  python3-rosdep

# 4. Install Gazebo, Nav2, SLAM Toolbox & TurtleBot3 Simulation
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-msgs \
  ros-humble-turtlebot3-simulations

# 5. Initialize rosdep
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi
rosdep update || true

# 6. Configure environment in ~/.bashrc
BASHRC="$HOME/.bashrc"
if ! grep -q "source /opt/ros/humble/setup.bash" "$BASHRC"; then
    echo "source /opt/ros/humble/setup.bash" >> "$BASHRC"
fi

if ! grep -q "export TURTLEBOT3_MODEL=" "$BASHRC"; then
    echo "export TURTLEBOT3_MODEL=waffle" >> "$BASHRC"
fi

if ! grep -q "GAZEBO_MODEL_PATH" "$BASHRC"; then
    echo "export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models" >> "$BASHRC"
fi

echo "=============================================="
echo " Setup Complete! ROS 2 Humble & Nav2 installed."
echo "=============================================="
