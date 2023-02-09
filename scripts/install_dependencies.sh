#!/bin/bash

packages=(
  automake
  doxygen
  graphviz
  libconfig-dev
  libcurl4-openssl-dev
  libglib2.0-dev
  libjansson-dev
  liblua5.3-dev
  libmicrohttpd-dev
  libogg-dev
  libopus-dev
  libsofia-sip-ua-dev
  libsrtp-dev
  libssl-dev
  libtool
  ninja-build
  pkg-config
)

sudo apt-get install ${packages[@]}
sudo snap install cmake --classic
