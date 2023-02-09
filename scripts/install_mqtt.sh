#!/bin/bash

git clone https://github.com/eclipse/paho.mqtt.c.git
cd paho.mqtt.c
make
sudo make install
if [ $? -ne 0 ]; then
  sudo rm -rf /usr/local/lib/libpaho-mqtt*
  sudo make install
fi
cd .. && rm -rf paho.mqtt.c
