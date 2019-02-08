# The GOAL: Lets get all the data in one place

Have you ever wondered how Google, Apple et al. create their maps and make them searchable? Me too!

With that goal in mind we want to find a solution that lets us easily perform ETL (Export, Transform, Load) as well as more complex geospatial queries like intersect. So the current scale is maybe hard to estimate, back of the envelope:

1. We want to insert all the OpenAddress.io address points - [523,263,177](http://results.openaddresses.io)
2. We want to insert all of OSM linestring street data - [130,511,321](https://wiki.openstreetmap.org/wiki/Key:highway)
3. We want to insert all of the OSM building data - [329,466,771](https://wiki.openstreetmap.org/wiki/Key:building)

So this is alot, how is anyone even handling this? One technique involves [quadtrees](https://people.cs.vt.edu/~shaffer/Papers/SamePR84.pdf) and perhaps making shards of data from this. But what would the best tree structure be? [Here](https://candu.github.io/blog/2013/02/21/quadtree-cartography/) is a neat exploration. There is even a [post](https://medium.com/@tidwall/faster-geospatial-queries-in-tile38-f771e2f6b1bd) for tile38. Then how do you handle the requests? Oh and lets make it affordable...

OK, so the whole area is in too hard bucket for now! If anyone has ideas please reach out. Looks like I'll just have to pick my data and download it manually. Let's perhaps start with the state of Texas in the USA. Can we measure the perfomance the data set in a store to examine if its fit for purpose?

There are a number of potential options, but we like new tech...

I recently saw a great [demo](https://geonames.tile38.com) and [post](https://medium.com/@s32x/mapping-11m-geonames-points-with-tile38-c9d326461b23) on Tile38, this might fit the requirements?

## New GOAL: Test the scalability of a single machine for insertion and querying of Texas

## 1. Get the data

```
    add_tx_url = "https://s3.amazonaws.com/data.openaddresses.io/openaddr-collected-us_south.zip"
    os.system(f'curl -LO {add_tx_url}')

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
    os.system(f'curl -LO {tx_streets}')

    os.system('unzip -o "texas-latest-free.shp.zip" -d "tx"')

    streets = fiona.open("./tx/gis_osm_roads_free_1.shp")
```


## 2. Set up

Goto - https://github.com/tidwall/tile38

Optional - Setup a machine on AWS - https://hackernoon.com/running-docker-on-aws-ec2-83a14b780c56

ssh into your machine of choice or run locally. In this case its just a ubuntu instance, be sure to open the correct ports.

Follow the docker instructions:

### Remote

```docker pull tile38/tile38```

### Local

```conda create -n tile38 python=3.6```

```source activate tile38```

```conda install redis```

Now lets test it out:

```curl --data "set fleet truck3 point 33.4762 -112.10923" your.ip.address.here:80```

You should see a response:

```{"ok":true,"elapsed":"331.8µs"}```

## 3. Run

So my first attempt was to do this over the internet... Not so lucky...

Script "insert_data.py"

- note: Its probably better to use pipelines but I couldn't get it to work.

From this I learnt that you'll need to make sure to use square brackets and double quotes when inserting objects.

So we'll have to get tile38 running on the instance and then run the code directly there.

Lets ssh into our instance.

```
sudo yum install git

git clone https://github.com/tidwall/tile38.git

sudo yum install go

cd tile38

make

make test

nohup ./tile38-server > /dev/null 2>&1 &

sudo iptables -I INPUT -p tcp --dport 9851 --syn -j ACCEPT
```

Now lets test that we can connect

```
curl --data "set fleet truck3 point 33.4762 -112.10923" your.ip.add.here:9851
```

Success?

Next step lets get that data local by transfering the code. I'm using MC (Midnight Commander) to just


## 4. Compare

## 5. Future

There are a number of other approaches that might be valid:

1. POSTGIS - multi machine
2. GeoSpark
3. Hadoop - GIS tools for hadoop
4. osmlab/atlas
5. BigTable
6. Redis
7. ... more

# Other

- Further analysis - https://medium.com/@frederic.rodrigo/pbf2redis-eae7fcada735
- Fast processing - http://matthewrocklin.com/blog/work/2017/09/21/accelerating-geopandas-1
- Cython Geopandas - https://jorisvandenbossche.github.io/blog/2017/09/19/geopandas-cython/
- Aurora AWS - https://aws.amazon.com/blogs/database/amazon-aurora-under-the-hood-indexing-geospatial-data-using-z-order-curves/


