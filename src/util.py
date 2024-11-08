import json

from cachetools import cached, TTLCache
import requests
from bs4 import BeautifulSoup


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_route_dict():
    """
    Fetches the route list from the specified URL and returns a dictionary
    mapping route names to their corresponding route IDs.

    Returns:
        dict: A dictionary where keys are route names and values are route IDs.
    """
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
    routes_name = list(route_dict.keys())

    return routes_name


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_station_dict(route_id: str, go: bool = True):
    url = f"https://pda.5284.gov.taipei/MQS/route.jsp?rid={route_id}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")

    station_dict = {}
    selector = "tr.ttego1, tr.ttego2" if go else "tr.tteback1, tr.tteback2"
    for tr in soup.select(selector):
        a = tr.find("a")
        if a:
            station_dict[a.text] = a.get("href").split("=")[1]
     
    return station_dict


@cached(cache=TTLCache(maxsize=1, ttl=60 * 10))
def get_stations_name(route_name: str, go: bool = True):
    route_id = get_route_dict().get(route_name)
    if not route_id:
        return []
    station_dict = get_station_dict(route_id, go)
    stations_name = [station_name for station_name in station_dict.keys()]
    for station_name in station_dict.keys():
        stations_name.append(station_name)

    return stations_name


@cached(cache=TTLCache(maxsize=1, ttl=5))
def get_stations_remain_dict(route_id: str):
    url = f"https://pda.5284.gov.taipei/MQS/RouteDyna?routeid={route_id}"
    html = requests.get(url).text
    data = json.loads(html)

    stations_remain_dict = {}
    for stop in data["Stop"]:
        n1_split = stop["n1"].split(",")
        if len(n1_split) > 7:
            stations_remain_dict[str(stop["id"])] = n1_split[7]
        else:
            stations_remain_dict[str(stop["id"])] = None

    return stations_remain_dict


def get_remain_time(route_name: str, station_name: str, go: bool = True):
    route_dict = get_route_dict()
    if route_name not in route_dict:
        return None
    route_id = route_dict[route_name]

    station_dict = get_station_dict(route_id, go)
    if station_name not in station_dict:
        return None
    station_id = station_dict[station_name]

    stations_remain_dict = get_stations_remain_dict(route_id)
    return stations_remain_dict.get(station_id, None)

def get_all_station_time(route_name: str, go: bool = True):
    """
    Fetches the remaining time for all stations on a given route.

    Args:
        route_name (str): The name of the route.
        go (bool): Direction of the route, True for go and False for return.

    Returns:
        dict: A dictionary where keys are station names and values are remaining times.
    """
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
