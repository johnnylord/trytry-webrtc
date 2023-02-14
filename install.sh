#!/bin/bash

mkdir -p log

# Prerequisites
# ===============================================
bash ./scripts/install_dependencies.sh | tee log/install_dependencies.log
# STUN and TURN
bash ./scripts/install_libnice.sh | tee log/install_libnice.log
# Media encryption
bash ./scripts/install_libsrtp.sh | tee log/install_libsrtp.log
# Data channel encryption
bash ./scripts/install_usrsctp.sh | tee log/install_usrsctp.log
# Transport Protocol between plugins and Janus
bash ./scripts/install_libwebsocket.sh | tee log/install_libwebsocket.log
bash ./scripts/install_mqtt.sh | tee log/install_mqtt.log

# Setup Janus
# ==============================================
bash ./scripts/install_janus.sh | tee log/install_janus.log
