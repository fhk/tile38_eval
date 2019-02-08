import os

import geopandas as gpd
import pandas as pd
import fiona


def main():
    # Addresses
    add_tx_url = "https://s3.amazonaws.com/data.openaddresses.io/openaddr-collected-us_south.zip"
    os.system('curl -LO %s'%add_tx_url)

    os.system(
        'mkdir "tx" && \
        unzip openaddr-collected-us_south.zip us/tx/*')

    # Join the data
    os.system('sed -n 1p ./us/tx/anderson.csv > all_tx.csv')
    os.system('sed 1d ./us/tx/*.csv >> all_tx.csv')

    # Load the data
    address_df = pd.read_csv("all_tx.csv")

    # Streets
    tx_streets = "https://download.geofabrik.de/north-america/us/texas-latest-free.shp.zip"
    os.system('curl -LO %s'%tx_streets)

    os.system('unzip -o "texas-latest-free.shp.zip" -d "tx"')

    streets = fiona.open("./tx/gis_osm_roads_free_1.shp")


if __name__ == "__main__":
    main()
