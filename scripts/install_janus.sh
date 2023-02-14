#!/bin/bash

git clone https://github.com/meetecho/janus-gateway.git
cd janus-gateway
sh autogen.sh
./configure --prefix=/opt/janus
make -j`nproc`
sudo make install
sudo make configs
cd .. && rm -rf janus-gateway
