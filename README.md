# DISCLAIMER

THIS IS MY FIRST JOURNEY INTO PYTHON on RPI
IT WORKS FOR ME SINCE FEW YEARS - DOES NOT HAVE TO FOR YOU.

# Introduction 
My old radioclock died and I had Raspberry Pi Zero laying around looking for project to be used.
So I thought it would be great moment to learn how to progam all those displays, temp sensors etc. and have "smart" radio clock.
![Smart radioclock!](/images/radioclock.png)
This is how it came to life.

# What is does

Normally it displays time (wow!) and weather data.
Then, under the buttons I have few songs I own or radio streams I like.
It runs web server with Progressive Web App and Swagger UI for API endpoints.

# Dependencies

All of known to me for now deps are in requirements.txt so one could apply those with
> pip install -r requirements.tx

# Running

`localscripts` directory delivers scripting for Systemd service, one can however run it directly like:
> waitress-serve --listen *:8000 radioserver:app

# Configuration
Configuration should land in config.json file in root directory.
I am looking there for API Token for Openweather and longitude/latitude to be able to get some decent forecast data.

# Components used

DHT 11 - temperature and humidity sensor (with 10k Ohm resistor)
TM1637 - 7 Segment, 4 Elements LED display
0.91 inch OLED I2C Display 128 x 32 pixels 

# Connection schema

![Connections!](/images/diagram.png)