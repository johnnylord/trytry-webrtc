#!/bin/bash

git clone https://gitlab.freedesktop.org/libnice/libnice
cd libnice

python3 -m pip install -U pip
python3 -m pip install meson

meson --prefix=/usr build && ninja -C build && sudo ninja -C build install

cd .. && rm -rf libnice
