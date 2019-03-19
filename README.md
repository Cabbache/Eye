# Eye
get live camera feed

### What is it ###
It's a python script that retrieves live stream from cameras on the skyline network and displays the image.

### How it works ###
It scans the skyline website for links to the cameras, then it asks the users in which country they would like to see.
Then it will obtain a live stream from a specified number of cameras in that area and display them in separate windows.

A problem developed when the rate at which the live stream is downloaded exceeded the rate at which video is displayed, causing the hardisk to be filled.

### Dependencies ###

for python:
* openCV
* urllib
* requests

This script will become outdated if the skyline website undergoes major changes.
It was last tested on Debian 4.19.20-1kali1 (2019-02-14) on 19th March, 2019.
