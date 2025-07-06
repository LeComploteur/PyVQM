# 

## What is PyVQM

PyVQM is aimed to provide a cross-platform GUI to assess quality of video encode.


### Features 

- SSIM,PSNR & VMAF 
- Cross platform (`Windows`,`MacOS`,`Linux`)
- RealTime plotting of values as they get computed (SSIM & PSNR only)
- Compare multiple encodes at the same time

## Install

Clone this repo, cd into the directory and run 
```bash
pip install -r ./requirements.txt
```

You may prefer to use a venv 

You will need python3 (v3.12.3 used while dev)

## Usage

Cd into this directory and simply run 

```bash
python3 ./app.py
```
And the GUI will run

## TODOS

- Make it compatible with windows (For now, there is file selection problems that i need to work on)
- Add VMAF support
- Improve UI
- Improve plotting style
- Add more pens to support more graphs
- Improve ListView to support more infos


## Maybe

- Add a save system to store projects on the long run

