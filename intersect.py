import requests
import json

import redis
import fiona
from fiona.crs import from_epsg

CITY = "Austin, TX"

POLY_SCHEMA = {
    'geometry': 'Polygon',
    'properties': {'id': 'int'}
}

ADDRESS_SCHEMA = {
        'geometry': 'Point',
        'properties': {'id': 'int'}
}

STREET_SCHEMA = {
        'geometry': 'LineString',
        'properties': {'id': 'int'}
}

def get_poly(city=CITY):
    response = requests.get("https://nominatim.openstreetmap.org/search.php?q=austin+texas&polygon_geojson=1&format=json")
    return response.json()[0]['geojson']


def get_result(poly):
    redIs = redis.Redis(host='your.ip.address.here', port=9851)
    geojson = str(poly).replace("'", '"')
    geojson = geojson.replace(' ', '')
    geojson = geojson.replace('(', '[')
    geojson = geojson.replace(')', ']')
    add_count, add_result = redIs.execute_command("INTERSECTS", "address", "LIMIT", 9999999, "OBJECT", geojson)
    st_count, st_result = redIs.execute_command("INTERSECTS", "street", "LIMIT", 9999999, "OBJECT", geojson)
    print(f"Found {add_count} address points")
    print(f"Found {st_count} streets lines")
    return add_result, st_result


def write_shp(poly, add_result, st_result):
    with fiona.open(
        "query_polygon.shp",
        'w',
        crs=from_epsg(4326),
        driver='ESRI Shapefile',
        schema=POLY_SCHEMA) as lyr:
        lyr.write({'geometry': poly, 'properties': {'id': 1}})
    with fiona.open(
        "address_data.shp",
        'w',
        crs=from_epsg(4326),
        driver='ESRI Shapefile',
        schema=ADDRESS_SCHEMA) as lyr:
        for i, feat in enumerate(add_result):
            lyr.write({'geometry': json.loads(feat[1]), 'properties': {'id': int(feat[0])}})

    with fiona.open(
        "street_data.shp",
        'w',
        crs=from_epsg(4326),
        driver='ESRI Shapefile',
        schema=STREET_SCHEMA) as lyr:
        for i, feat in enumerate(st_result):
            lyr.write({'geometry': json.loads(feat[1]), 'properties': {'id': int(feat[0])}})


def main():
    poly = get_poly()
    add_result, st_result = get_result(poly)
    write_shp(poly, add_result, st_result)


if __name__ == "__main__":
    main()
