#!/bin/bash
ROOT=${PWD}/`dirname $0`/../
PYTHON=python
cd ${ROOT}

nohup ${PYTHON} limit_server.py &
nohup ${PYTHON} ad_server.py &
rm -rf nohup.out
