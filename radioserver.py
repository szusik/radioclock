from flask import Flask, jsonify, request
from flasgger import Swagger
#import modules.clock
import os
import string


app = Flask(__name__)
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Projekt Ariadne",
    "specs": [
        {
            "version": "0.0.1",
            "title": "Api v1",
            "endpoint": 'v1_spec',
            "description": 'This is the version 1 of our API',
            "route": '/v1/spec',
        }
    ]
}
# Create swagger definition
swagger = Swagger(app) 

@app.route('/hello')
def hello():
    """Hello world endpoint
    ---
    responses:
      200:
        description: Status answer
        schema:
            type: object
            properties:
              worte:
                type: integer
                description: Hello answer.
    """ 
    location = os.path.dirname(os.path.realpath(__file__))
    return 'Hello, World '+location 
if __name__ == '__main__':
    app = create_app()
    app.run()    
