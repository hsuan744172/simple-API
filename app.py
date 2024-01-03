import flask
from flask_cors import CORS
import json
import requests
app=flask.Flask(__name__)
CORS(app)
@app.route('/',methods=['POST'])
def rout():
    body=flask.requests.data.decode('utf-8')
    url=json.loads(body)['url']
    result=requests.get(url)
    return result.text
