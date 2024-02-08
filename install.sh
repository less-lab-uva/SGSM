#!/bin/bash

conda create -n sg_monitor python=3.9.17 -y
conda activate sg_monitor
pip install -r requirements.txt

. ./install_mona.sh