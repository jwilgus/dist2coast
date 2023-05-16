#!/usr/bin/env python
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from shapely.ops import unary_union
from haversine import haversine, Unit
import geoplot as gplt
import matplotlib.pyplot as plt

debug = True
# point coordinates for testing
lat = 35.08 # ~ ABQ locs
lon = -106.65
p0 = Point(lon,lat)

#--- Extract NA coastline geometry
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))#built in dataset
NA = world[world['continent']=='North America'].dissolve(by='continent') #choose coastline
NA_boundaries = unary_union(NA['geometry']) #Extract lat and lon info

#--- clip 10 m coastline to NA geometry
coastline = gpd.clip(gpd.read_file('ne_10m_coastline/ne_10m_coastline.shp')
                    ,NA_boundaries).to_crs('EPSG:4326')
coastline_union = unary_union(coastline.geometry)
# for geom in coastline_union.geoms: #--> plots for debugging
#     xs, ys = geom.xy
#     print(xs,ys)
#     plt.plot(xs, ys,'r-')
# coastline.plot()
# plt.show()

#--- determine closest point along coastline
p1, p0 = nearest_points(coastline_union, p0)
print(list(p1.coords))
nearest_lon, nearest_lat = (p1.coords)[0]

#--- determine distance between points
dist = haversine([lat, lon],[nearest_lat, nearest_lon]) #points in lat,lon form


if debug:
    #--- Create geopandas dataframes for starting point and nearest coastline point
    df_start = pd.DataFrame({'Latitude': [lat],'Longitude': [lon]})
    start = gpd.GeoDataFrame(df_start,
            geometry=gpd.points_from_xy(df_start.Longitude, df_start.Latitude))
    df_nearest = pd.DataFrame({'Latitude': [nearest_lat],'Longitude': [nearest_lon]})
    nearest = gpd.GeoDataFrame(df_nearest,
              geometry=gpd.points_from_xy(df_nearest.Longitude, df_nearest.Latitude))

    #plot input point (red) and "closest point" (blue) on coastline
    ax = gplt.polyplot(gpd.GeoSeries(NA_boundaries), figsize=(8, 5))
    start.plot(ax = ax, color = 'red')
    nearest.plot(ax = ax, color = 'blue')
    plt.title('starting loc '+str(np.round(lat,2))+','+str(np.round(lon,2))+'  closest coast loc '+
               str(np.round(nearest_lat,2))+','+str(np.round(nearest_lon,2))+' --> '+str(np.round(dist,2))+' [km]')
    plt.show()
    plt.close()
