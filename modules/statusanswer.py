from flask import jsonify

def statusAnswer(statusText):
    result = { 'status': str(statusText) }
    return jsonify(result)
