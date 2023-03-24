from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
#app.url_for('static', filename='style.css')

@app.route('/')
def index():
  return render_template("index.html")