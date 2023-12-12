# geojpg
[![Pylint](https://github.com/baidakovil/geojpg/actions/workflows/pylint.yml/badge.svg)](https://github.com/baidakovil/geojpg/actions/workflows/pylint.yml) [![Testing](https://github.com/baidakovil/geojpg/actions/workflows/python-pytest-flake8.yml/badge.svg)](https://github.com/baidakovil/geojpg/actions/workflows/python-pytest-flake8.yml)


Utility for inserting **gpx** geodata into a **jpg** files.  
Helpful when your DSLR camera **have no gps**, but your phone **have**. 

  
## How it works

![start_track](docs/geojpg-how-to-1.jpg)
![start_track](docs/arrow.png)
![start_track](docs/geojpg-how-to-2.jpg)


## What you need?

* Python 3
* Library **piexif** in your Python installation  
* Your phone and camera must be **time-synchronized**


## Todo list

*  Earth hemispheres detecting  
note: now North and East are hard-coded  
*  One-digit deegree support in longtitude/lattitude  
*  App for Windows/Mac/Linux  
*  Parameter for copy/rewrite jpg files  
