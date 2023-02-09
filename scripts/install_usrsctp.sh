#!/bin/bash

git clone https://github.com/sctplab/usrsctp
cd usrsctp
./bootstrap
if [ $? -ne 0 ]; then
  ./bootstrap && rm ../../ltmain.sh
fi
./configure --prefix=/usr --libdir=/usr/lib64
make && sudo make install
cd .. && rm -rf usrsctp
