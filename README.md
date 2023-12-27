# geojpg
[![Pylint](https://github.com/baidakovil/geojpg/actions/workflows/pylint.yml/badge.svg)](https://github.com/baidakovil/geojpg/actions/workflows/pylint.yml) [![Testing](https://github.com/baidakovil/geojpg/actions/workflows/python-pytest-flake8.yml/badge.svg)](https://github.com/baidakovil/geojpg/actions/workflows/python-pytest-flake8.yml)


Utility for inserting **gpx** geodata into a **jpg** files.  
Helpful when your DSLR camera **have no gps**, but your phone **have**   
📱 + 📷 = 🗺

  
## How it works

![start_track](docs/geojpg-how-to-1.jpg)
![start_track](docs/arrow.png)
![start_track](docs/geojpg-how-to-2.jpg)

## Built with

**[Python]** - Language to work quickly and integrate systems more effectively, since 1991 **|** *GPL compatible*    
**[pyexif]** - Python wrapping for the `exiftool` library, since 2011 **|** *Apache 2*  

[pyexif]: https://pypi.org/project/pyexif/
[Python]: https://www.python.org/

## What I need to run?

* Make sure you have `Python 3`
* Install library `pyexif` in your Python installation, typically `pip install pyexif`  
* Your phone and camera should be **time-synchronized** for app to work out-of-box  
If not, you can adjust time with `HOURS_UTC_OFFSET_GPX`, `HOURS_UTC_OFFSET_JPG` values
* 

## Todo list

*  Earth hemispheres detecting  
_NOTE: now North and East are hard-coded, so you can't use this app out-of-box in western/southest hemisphere... sorry, it is not discrimination. If you really want this feature in your hemisphere, just open the issue -> I add this quickly_
*  One-digit deegree support in longtitude/lattitude  
*  App for Windows/Mac/Linux **OR service?** 
*  Parameter for copy/rewrite jpg files  
