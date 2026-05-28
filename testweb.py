from flask import Flask, jsonify, request, render_template
from modules.clock2 import runClock, clearScreen
from modules.stoppableThread import StoppableThread
from modules.weather import getWeather,displayClear,getWeatherSched, getTempHumid

#setup background thread
clockThread = StoppableThread(target=runClock, args=(1,))
weatherThread = StoppableThread(target=getWeatherSched)

app = Flask(__name__)
#app.url_for('static', filename='style.css')

@app.route('/')
def index():
  return render_template("index.html")

clockThread.start()
weatherThread.start()

if __name__ == '__main__':
    app = create_app()
    app.run()    