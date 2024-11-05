from html import escape
from flask import Flask, request
from flask_cors import CORS

import src.util as util

app = Flask(__name__)
CORS(app)


@app.route("/api/routesName", methods=["GET"])
def routesName():
    routes_name = util.get_routes_name()
    return {"routes_name": routes_name}

@app.route("/", methods=["HEAD","OPTIONS"])  
def index() -> Response:
    return Response("OK", 200)
@app.route("/api/routeStationsName", methods=["POST"])
def routeStationsName():
    route_name = str(escape(request.json["route_name"])).strip()
    go = bool(request.json["go"])
    stations_name = util.get_stations_name(route_name, go)
    
    return {"stations_name": stations_name}


@app.route("/api/routeStationRemainTime", methods=["POST"])
def routeStationRemainTime():
    route_name = str(escape(request.json["route_name"])).strip()
    station_name = str(escape(request.json["station_name"])).strip()
    go = bool(request.json["go"])
    remain_time = util.get_remain_time(route_name, station_name, go)
    
    return {"remain_time": remain_time}


@app.route("/api/routeStationsRemainTime", methods=["POST"])
def routeStationsRemainTime():
    route_name = str(escape(request.json["route_name"])).strip()
    go = bool(request.json["go"])
    remain_times = util.get_all_station_time(route_name, go)
    remain_times = [{'name': k, 'time': v} for k, v in remain_times.items() if v is not None]
    
    return {"remain_times": remain_times}  
