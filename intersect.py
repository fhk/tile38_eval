import requests

import redis
import fiona

CITY = "Austin, TX"


def get_poly(city=CITY):
    response = requests.get("https://nominatim.openstreetmap.org/search.php?q=austin+texas&polygon_geojson=1&format=json")
    return response.json()[0]['geojson']


def get_result(poly):
    redIs = redis.Redis(host='your.ip.address.here', port=9851)
    geojson = str(poly)
    geojson = geojson.replace(' ', '')
    geojson = geojson.replace('(', '[')
    geojson = geojson.replace(')', ']')
    add_result = redIs.execute_command("INTERSECTS", "address", "OBJECT", geojson)
    st_result = redIs.execute_command("INTERSECTS", "street", "OBJECT", geojson)
    import pdb; pdb.set_trace()


def main():
    poly = get_poly()
    result = get_result(poly)

if __name__ == "__main__":
    main()
