import redis
import fiona
import pandas


def read():
    lyr = fiona.open("./tx/gis_osm_roads_free_1.shp")
    df = pandas.read_csv("all_tx.csv")

    return lyr, df

def load(lyr, df):
    redIs = redis.Redis(host='127.0.0.1', port=9851)
    for i, f in enumerate(lyr):
        geojson = f['geometry']
        geojson = str(geojson).replace("'", '"')
        geojson = geojson.replace(' ', '')
        geojson = geojson.replace('(', '[')
        geojson = geojson.replace(')', ']')

        redIs.execute_command("SET", "street", i, "OBJECT", geojson)

   for i, r in enumerate(df.iterrows()):
       lon = float(r[1].LON)
       lat = float(r[1].LAT)
       geojson = {
           "type":"Point",
           "coordinates":[lon,lat]
           }

       geojson = str(geojson).replace("'", '"')
       geojson = geojson.replace('(', '[')
       geojson = geojson.replace(')', ']')

       redIs.execute_command("SET", "address", i, "OBJECT", geojson)


def main():
    lyr, df = read()
    load(lyr, df)


if __name__ == '__main__':
    main()
