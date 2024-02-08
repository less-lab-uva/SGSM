# Scene Graph Safety Monitoring (SGSM)

This repository contains the code for the paper "Specifying and Monitoring Safe Driving Properties with Scene Graphs". The code is written in Python and requires [conda](https://docs.anaconda.com/free/anaconda/install/linux/) and [7z](https://www.7-zip.org/download.html) to be installed. The code was tested using Ubuntu 20.04.

## Installation
To install everything needed to run the code, execute the following command:
```bash
./install.sh
```
The installation script will do the following:
1) Create a conda environment called 'sg_monitor'.
2) Install the python packages specified in requirements.txt.
3) Install [mona](https://www.brics.dk/mona/) using the `install_mona.sh` script

## Usage
To reproduce the results of the paper, execute the following command:
```bash
./run.sh
```
This script will do the following:
1) Activate the conda environment 'sg_monitor'.
2) Pull the images and scene graphs collected from the CARLA simulator using [TCP](https://github.com/OpenDriveLab/TCP), [Interfuser](https://github.com/opendilab/InterFuser?tab=readme-ov-file), and [LAV](https://github.com/dotchen/LAV).
3) Check the properties specified in the paper, located in the properties.py file, using the scene graphs and the SG Monitor.
4) Generate tables that show the property violations of the 3 Systems Under Test (SUTs) per Route and a Summary table that shows the total number of property violations per SUT.

