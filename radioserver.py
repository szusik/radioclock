from flask import Flask, jsonify, request, render_template
from flasgger import Swagger
from modules.clock import runClock, clearScreen
import os
import string
import logging
import threading
import time
from modules.statusanswer import statusAnswer
from modules.stoppableThread import StoppableThread,ExeContext
import subprocess
from modules.radio import playRadio, killMusic,playLulaby
from modules.soundvolume import getSoundVolume, setSoundVolume

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

# Create swagger definition
swagger = Swagger(app) 

@app.route('/')
@app.route('/index.html')
def index():
  return render_template("index.html")

@app.route('/manifest.json')
def manifest():
  return render_template("manifest.json")

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
    brightness = request.args.get('brightness', '')
    if brightness == '': 
      brightness = 0.1
    if ExeContext.displayThread is not None:
      ExeContext.displayThread.stop()
    ExeContext.displayThread = StoppableThread(target=runClock, args=(brightness,))
    ExeContext.displayThread.start()
    return statusAnswer("Clock started")
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
    if ExeContext.displayThread is not None:
        ExeContext.displayThread.stop()
    return statusAnswer("Clock stopped")
@app.route('/api/radio/start')
def radioStart():
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
    killMusic()
    radio = threading.Thread(target=playRadio, args=())
    radio.start()
    return statusAnswer("Radio started")
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
    killMusic()
    return statusAnswer("Music stopped")
@app.route('/api/lulaby/start')
def lulabyStart():
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
    killMusic()
    radio = threading.Thread(target=playLulaby, args=())
    radio.start()
    return statusAnswer("Lulaby playing")
@app.route('/api/volume/down')
def volumeDown():
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
    volume = getSoundVolume()
    volume -= 10
    if volume<0:
      volume = 0
    status = setSoundVolume(volume)
    return statusAnswer(status)
@app.route('/api/volume/up')
def volumeUp():
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
    volume = getSoundVolume()
    volume +=10
    if volume>100:
      volume = 100
    status = setSoundVolume(volume)
    return statusAnswer(status)
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
    volume = getSoundVolume()
    return statusAnswer(volume)
ExeContext.displayThread = StoppableThread(target=runClock, args=(0.1,))
ExeContext.displayThread.start()
if __name__ == '__main__':
    app = create_app()
    app.run()    
