from flask import Flask, jsonify, request, render_template
from flasgger import Swagger
from flask.helpers import make_response
from modules.clock2 import runClock, clearScreen
import os
import string
import logging
import logging.config
import threading
import time
from modules.statusanswer import statusAnswer
from modules.stoppableThread import StoppableThread
import subprocess
from modules.radio import playRadio, killMusic,playLulaby
from modules.soundvolume import getSoundVolume, volumeUp, volumeDown
from modules.weather import getWeather,displayClear,getWeatherSched
from modules.buttons import setupButtons
import sys
import schedule

app = Flask(__name__)
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Radio CLOCK APIServer",
    "specs": [
        {
            "version": "0.0.1",
            "title": "Radio Clock Api v1",
            "endpoint": 'v1_spec',
            "description": 'This is the version 1 of radio clock API',
            "route": '/v1/spec',
        }
    ]
}
#Setup logger
logging.basicConfig(filename='/var/log/radioclock.log',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Create swagger definition
swagger = Swagger(app) 
#setup background thread
clockThread = StoppableThread(target=runClock, args=(0.1,))
weatherThread = StoppableThread(target=getWeatherSched)
buttonsThread = StoppableThread(target=setupButtons)
@app.route('/')
@app.route('/index.html')
def index():
  return render_template("index.html")

@app.route('/manifest.json')
def manifest():
  filename = "static/manifest.json"
  with open(filename) as f:
    content = f.readlines()
  resp = make_response('\n'.join(content))
  resp.headers.add_header("Content-type","application/json")
  return resp

@app.route('/sw.js')
def sw():
  filename = "static/sw.js"
  with open(filename) as f:
    content = f.readlines()
  resp = make_response('\n'.join(content))
  resp.headers.add_header("Content-type","application/javascript; charset=utf-8")
  return resp

@app.route('/api/hello')
def hello():
  """Hello world endpoint
  ---
  responses:
    200:
      description: Status answer
      schema:
          type: object
          properties:
            status:
              type: string
              description: Hello answer.
  """ 
  location = os.path.dirname(os.path.realpath(__file__))
  return statusAnswer('Hello, World '+location)
@app.route('/api/clock/start')
def clockStart():
    """Start displaying clock
    ---
    parameters:
      - name: brightness
        in: query
        type: string
        required: false 
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    global clockThread
    global weatherThread
    try:
      brightness = request.args.get('brightness', '')
      if brightness == '': 
        brightness = 0.1
      logging.info("Starting clock")
      if clockThread is not None:
        clockThread.stop()
      clockThread = StoppableThread(target=runClock, args=(brightness,))
      clockThread.start()
      logging.info("Starting weather")
      if weatherThread is not None:
        weatherThread.stop()
      weatherThread = StoppableThread(target=getWeather)
      weatherThread.start()
      return statusAnswer("Clock started")
    except:
      err = str(sys.exc_info())
      logging.error("Got clock start error known as:",str(err))
@app.route('/api/clock/stop')
def clockStop():
    """Stop displaying clock
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    global clockThread
    global weatherThread
    try:
      logging.info("Clear and stop clock")
      if clockThread is not None:
        clockThread.stop()
      clearScreen()
      logging.info("Clear and stop weather display")
      if weatherThread is not None:
        weatherThread.stop()
      displayClear()
      return statusAnswer("Clock stopped")
    except:
      err = str(sys.exc_info())
      logging.error("Got error known as:",str(err))
      return statusAnswer("Clock stopped error")
@app.route('/api/radio/start/<radio_id>')
def radioStart(radio_id):
    """Start playing radio
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    try:
      killMusic()
      radio = threading.Thread(target=playRadio, args=(radio_id,))
      radio.start()
      return statusAnswer("Radio started")
    except:
      err = str(sys.exc_info())
      logging.error("Got error known as:",str(err))
      return statusAnswer("Radio start error")
@app.route('/api/music/stop')
def radioStop():
    """Stop playing music
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    try:
      killMusic()
      return statusAnswer("Music stopped")
    except:
      err = str(sys.exc_info())
      logging.error("Got error known as:",str(err))
      return statusAnswer("Kill music error")
@app.route('/api/lulaby/start/<lul_id>')
def lulabyStart(lul_id):
    """Start playing lulaby
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    try:
      killMusic()
      radio = threading.Thread(target=playLulaby, args=(lul_id,))
      radio.start()
      return statusAnswer("Lulaby playing")
    except:
      err = str(sys.exc_info())
      logging.error("Got error known as:",str(err))
      return statusAnswer("Lulaby error")
@app.route('/api/volume/down')
def volDown():
    """Volume down by 10%
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    try:
      status = volumeDown()
      return statusAnswer(status)
    except:
      err = str(sys.exc_info())
      logging.error("Got volDown error known as:",str(err))
@app.route('/api/volume/up')
def volUp():
    """Volume UP by 10%
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    try:
      status = volumeUp()
      return statusAnswer(status)
    except:
      err = str(sys.exc_info())
      logging.error("Got error known as:",str(err))
      return statusAnswer("Vol up error")
@app.route('/api/volume/level')
def volumeLevel():
    """Volume level check
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              status:
                type: string
                description: Status answer.
    """
    try:
      volume = getSoundVolume()
      return statusAnswer(volume)
    except:
      err = str(sys.exc_info())
      logging.error("Got error known as:",str(err))
      return statusAnswer("Get sound volume error")
logging.info("Starting clock")

clockThread.start()
logging.info("Starting weather")

weatherThread.start()
logging.info("Starting buttons")
buttonsThread.start()
#setupButtons()
logging.info("All done")
if __name__ == '__main__':
    app = create_app()
    app.run()    
