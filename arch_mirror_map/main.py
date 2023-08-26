#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys,os
import requests
import json
import math
import geoip2.database
import re
import socket
import folium
from geolite2 import geolite2  #maxminddb-geolite2
from urllib.parse import urlparse
import pycountry_convert as pc
import pgeocode
import time, random
from geopy.geocoders import Nominatim

from .helpers import *


unknown_countries = {}
unknown_countries['New Caledonia'] =  { 'latitude': '-21.1332', 'longitude' : '165.3772' }
savedir = "savedres/"
print(unknown_countries)


# fun for checking if dns resolves to multiple addresses
def main():
    # - get all tier1 mirrors 
    # - put markers on map, save all markers to array 
    # - in a loop:
    #     - get tier2 mirror url 
    #     - extract country and get lat/long of mirror 
    #     - make marker and put it on map
    #     - associate with upstream marker 
    #     - save association to a dict?
    # - connect all markers? 
    # also check if it's active
    # but first:
    # get all tier1 mirrors 
    # loop:
    #     get tier2 mirror url 
    #     extract country and get lat/long 
    #     associate with upstream details 
    #     save association to dict? 


    tier1=get_all_tier1()
    # result=
    tier2=get_all_tier2(10)
    # for mirror in tier2["urls"]:
    m = folium.Map(location=[0, 0], zoom_start=2)
    reader = geolite2.reader()
    tier1_color="red"
    tier2_color="green"
    tier_to_markers_on_map(m,tier1,tier1_color,reader,"tier1")
    tier_to_markers_on_map(m,tier2,tier2_color,reader,"tier2")
        


    print("writng map to disk")
    m.save('map2.html')
    sys.exit()

main()
