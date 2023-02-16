#!/bin/bash

wget https://github.com/cisco/libsrtp/archive/v2.2.0.tar.gz
tar xfv v2.2.0.tar.gz
cd libsrtp-2.2.0

./configure --prefix=/usr --libdir=/usr/lib64 --enable-openssl
make shared_library && sudo make install

./configure --prefix=/usr --enable-openssl
make shared_library && sudo make install

cd .. && rm -rf libsrtp-2.2.0 v2.2.0.tar.gz

