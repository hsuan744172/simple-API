import json
from cachetools import cached, TTLCache
import requests
from bs4 import BeautifulSoup


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_route_dict():
    url = "https://pda.5284.gov.taipei/MQS/routelist.jsp"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")

    route_dict = {}
    for option in soup.find_all("option"):
        if option["value"]:
            route_dict[option.text] = option["value"]

    return route_dict


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_routes_name():
    route_dict = get_route_dict()
    routes_name = []
    for route_name in route_dict.keys():
        routes_name.append(route_name)

    return routes_name


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_station_dict(route_id: str, go: bool = True):
    url = "https://pda.5284.gov.taipei/MQS/route.jsp?rid={}".format(route_id)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")

    station_dict = {}
    for tr in soup.select("tr.ttego1, tr.ttego2" if go else "tr.tteback1, tr.tteback2"):
        a = tr.find("a")
        station_dict[a.text] = a.get("href").split("=")[1]
     
    return station_dict


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_stations_name(route_name: str, go: bool = True):
    route_id = get_route_dict()[route_name]
    station_dict = get_station_dict(route_id, go)
    stations_name = []
    for station_name in station_dict.keys():
        stations_name.append(station_name)

    return stations_name


@cached(cache=TTLCache(maxsize=1, ttl=5))
def get_stations_remain_dict(route_id: str):
    url = "https://pda.5284.gov.taipei/MQS/RouteDyna?routeid={}".format(route_id)
    html = requests.get(url).text
    data = json.loads(html)

    stations_remain_dict = {}
    for stop in data["Stop"]:
        stations_remain_dict[str(stop["id"])] = stop["n1"].split(",")[7]

    return stations_remain_dict


def get_remain_time(route_name: str, station_name: str, go: bool = True):
    route_dict = get_route_dict()
    if route_name not in route_dict:
        return None
    route_id = route_dict[route_name]

    station_dict = get_station_dict(route_id, go)
    if station_name not in station_dict:
        return None
    station_id = station_dict[station_name] if station_name in station_dict else None

    stations_remain_dict = get_stations_remain_dict(route_id)
    return (
        stations_remain_dict[station_id] if station_id in stations_remain_dict else None
    )

def get_all_station_time(route_name: str, go: bool = True):
    route_id = get_route_dict().get(route_name)
    if not route_id:
        return None
    
    stations_remain_dict = get_stations_remain_dict(route_id)
    if not stations_remain_dict:
        return None
    
    bus_stations = get_station_dict(route_id, go)

    station_times = {}
    for station_name, station_id in bus_stations.items():
        station_times[station_name] = stations_remain_dict.get(station_id)

    return station_times
