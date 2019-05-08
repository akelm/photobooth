# The Photobooth

The Photobooth was created as an exposition of ["Fraktal"
 Students Scienfitic Association](https://www.facebook.com/fraktal.UKSW)
 at 
  for 23rd Science Picnic organized jointly by Polish Radio and 
  the Copernicus Science Centre (Warsaw). The project was inspired 
  by ["EB Photo Booth"](https://www.hackster.io/ericBcreator/photo-booth-powered-by-a-raspberry-pi-23b491).
Shortly, the Photobooth takes photos and sends them by e-mail.

![alt text](misc/fotobudka.jpg "Fotobudka")

# Authorship
 Anna Kelm, Agnieszka Jamrozik, and Karol Chyliński
# Hardware
* RaspberryPi (here: 3 model B)
* RaspberryPi Camera (here: V2)
* Display, best if touchscreen (here: Waveshare 5'' TFT)
* Pushbutton with LED (both press detection and LED  controlled with RaspberryPi GPIO)
* Other stuff (box, light...)

# Python scripts
## Prerequisites
The scripts were written in Python3 and used on 2019-04-08-raspbian-stretch-full image. 
The following extra Python modules has to be downloaded in this scenario: 
* PyYAML >= 5.1 (```pip3 install PyYAML```)
* PyQt5 >= xx (on Raspbian Stretch: ```sudo apt install python-pyqt5 -y``` )

Other packages from outside standard Python3 (3.5 used here) library are:
* RPi >= xx (on Raspbian Stretch ```sudo apt-get install python3-rpi.gpio```)
* picamera >= xx(```pip3 install picamera```)
* PIL >= xx (on Raspbian Stretch ```sudo apt-get install python3-pil```)


## Download
Type:
```
git clone https://github.com/gittower/git-crash-course.git
```
Modify file permissions:
```
chmod +x photobooth.py
chmod +x photoboothQt.py
chmod +x sendphotos.py
chmod +x photobooth_run.sh
```
## Run
### Complete Photobooth with e-mail:
First, setup SMTP e-mail config (```photoconfig.yaml```). 
```
./photobooth_run.sh
```
### Photobooth without e-mail:
```
./photobooth.py
```
# Licence
2019 "Fraktal" Students Scientific Association at 
Faculty of Mathematics and Natural Sciences. School of Exact Sciences.,
Cardinal Wyszyński University in Warsaw

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.