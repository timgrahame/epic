
# DSCOVR:EPIC Image Viewer (Weather and Clock)

This is a fork from Matt Gray's excellent NASA Epic image viewer.  This adds the current weather for your location and a clock to the display.

you will need an api key from http://openweathermap.org (register for an account)  this key then needs placing in the api_key = "<api key>" section under main loop
Change the location to the location and country you are in.

This script looks for new [images from the Earth Polychromatic Imaging Camera](https://epic.gsfc.nasa.gov/) on NASA's [Deep Space Climate Observatory](https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/dscovr-deep-space-climate-observatory) satellite, and displays them on screen.

This is designed for a [2.1" Hyperpixel Round Touch display from Pimoroni](https://shop.pimoroni.com/products/hyperpixel-round), with a [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/).

It displays each image for 20s then moves to the next one.

It currently checks the [EPIC "Blue Marble" API](https://epic.gsfc.nasa.gov/about/api) for new images every 120 mins, but I think they only upload new images once a day, so it probably doesn't need to be this often.

This is programmed using Python3 and PyGame.

# Running It
I've been fiddling with this for over a year now, so I've never followed these instructions in order. They're more of a guessed guideline.

## Raspberry Pi Setup
I'll assume you've already followed Pimoroni's instructions for getting the Hyperpixel Round screen going.

1. Use the terminal or log in as your username via ssh.
2. Create the directory `mkdir -p /root/code/epic/`
3. Go into the directory `cd /root/code/epic/`
4. Copy the code from this repository in
	* `git clone https://github.com/timgrahame/epic/epic.git .`
5. make sure `start-epic.sh` is executable (`chmod +x start-epic.sh`)
6. Copy the epic.service file to /etc/systemd/system
7. enable the service: systemctl enable epic
8. Install any python requirements `pip3 install -r requirements.txt`
9. Copy the epic.service file to /etc/systemd/system
10. enable the service: systemctl enable epic
11. Start the service: systemctl start epic
12. Test you can run it `./start-epic.sh`
	* If that doesn't work, test you can run it directly `python3 -u epic.py`
	* If it still doesn't work check the output for errors, and google them.
13. If the test works, kill it with CTRL+C
14. Reboot and hope it runs automatically `sudo reboot`


