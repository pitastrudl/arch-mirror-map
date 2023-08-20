#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers import *
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
unknown_countries = {}
unknown_countries['New Caledonia'] =  { 'latitude': '-21.1332', 'longitude' : '165.3772' }
savedir = "savedres/"
print(unknown_countries)


# fun for checking if dns resolves to multiple addresses
def check_dns_for_multiip():
    true = true 
    return 1



def get_all_tier2():
    j = requests.get("https://www.archlinux.org/mirrors/status/tier/2/json/").json()
    selected_pairs = dict(list(filter(lambda x: x[0].startswith("url"), j.items()))[:5])
    return selected_pairs

def get_all_tier1():
    json_tier1 = requests.get("https://www.archlinux.org/mirrors/status/tier/1/json/").json()

    for i, res in enumerate(json_tier1["urls"]):
        # Add a new key-value pair to the `res` dictionary
        res["upstream_shortname"] = res["details"].split("/")[4]
        json_tier1["urls"][i] = res
        # print (json_tier1["urls"][i])

    return json_tier1 

def locate_mirror(url,reader):
    mirror_loc={}
    if url["protocol"] == "http" or url["protocol"] == "https" :
        domain = re.match('^https?://([^/]+)(?:/.*)?$', url['url']).group(1)
        
        try:
            for ip in sorted(set([i[4][0] for i in socket.getaddrinfo(domain, None)])):
                print("ip loop in mirrorloc:\n",ip)
                if ip_is_saved(ip):
                    loaded_mirror_loc = {}
                    lat_ip, lng_ip = load_saved_ip(ip)
                    loaded_mirror_loc['location'] = {'latitude' : lat_ip,
                                             'longitude' : lng_ip}
                    loaded_mirror_loc["ip"]= ip
                    return loaded_mirror_loc
                else:
                    print("trying domain: ", domain , ", finding for ip:" + ip)
                    mirror_loc = reader.get(ip)
                    print(mirror_loc)
                    if mirror_loc is not None and 'location' in mirror_loc and mirror_loc['location']:
                        mirror_loc["ip"]= ip
                        save_ip(ip, {"latitude": mirror_loc['location']['latitude'],"longitude": mirror_loc['location']['longitude']} )
                    else:
                        print("my_object is None, cannot assign value")
                    
        except socket.gaierror:
            print("got exception for " + domain)
            pass
        
    return mirror_loc

def get_lat_long_nominatim(country):
    if country_is_saved(country):
        latitude, longitude = load_saved_country(country)
        return latitude, longitude
    else:
        geolocator = Nominatim(user_agent="my-app")
        locs = geolocator.geocode(country, exactly_one=True)
        latitude, longitude = locs.latitude, locs.longitude

        time.sleep(random.uniform(0.6, 1.2))
        save_country(country, {"latitude":latitude,"longitude":longitude})
        return latitude, longitude


def get_lat_long_kamoot(country):
    if country_is_saved(country):
        latitude, longitude = load_saved_country(country)
        return latitude, longitude
    else:
        try:
            j = requests.get("https://photon.komoot.io/api/?q="+ country + "&layer=country").json()
            print(j)
            if "coordinates" in j:
                lng = j["features"][0]["geometry"]["coordinates"][1]
                lat = j["features"][0]["geometry"]["coordinates"][0]
                save_country(country, {"latitude":lat,"longitude":lng})
                return lat, lng
        except requests.exceptions.RequestException as e:
            print("Request error:", e)
        return None, None
    
def tier_to_markers_on_map(m,tier,iconcolor,reader,tiername):
    for i, res in enumerate(tier["urls"]):
        print("res from tier urls: \n", res)
        location = locate_mirror(res,reader)  # outputs data from geoip
        if not location or 'location' not in  location:
            print("could not locate with func,checking in json:")
            print(res["country"])

            # getting lat long for the country
            latitude = ""
            longitude = ""
            latitude, longitude = get_lat_long_kamoot(res["country"])
            if not isinstance(latitude, str)  and not isinstance(longitude, str)  :
                print("trying with nominatim!!!")
                latitude, longitude = get_lat_long_nominatim(res["country"])
            elif res["country"] in  unknown_countries:
                print(unknown_countries)
                latitude = unknown_countries[res["country"]]["latitude"]
                longitude =  unknown_countries[res["country"]]["longitude"]
            else:
                print("ehh, didnt find ip for country")
            print(f"Latitude: {latitude}, Longitude: {longitude}")
            res['latitude'] = latitude
            res['longitude'] = longitude
            if tiername == "tier2":
                res['upstream'] = get_upstream_from_tier2(res['details'])

            folium.Marker(location=[res['latitude'], res['longitude']],popup=res, icon=folium.Icon(color=iconcolor)).add_to(m)

        elif 'location' in location:
            print ("assigning new info")
            print(location)
            res['latitude'] = location['location']['latitude']
            res['longitude'] = location['location']['longitude']
            tier["urls"][i] = res 
            print(tier["urls"][i])
            if tiername == "tier2":
                res['upstream'] = get_upstream_from_tier2(res['details'])
                folium.Marker(location=[res['latitude'] + random.uniform(0.10, 0.15), res['longitude'] + random.uniform(0.10, 0.15)],popup=location["ip"] + res['upstream'],icon=folium.Icon(color=iconcolor)).add_to(m)
            else:
                folium.Marker(location=[res['latitude'] + random.uniform(0.10, 0.15), res['longitude'] + random.uniform(0.10, 0.15)],popup=location["ip"],icon=folium.Icon(color=iconcolor)).add_to(m)
        else:
            print("didnt find loc!!! exiting and dumping data:\n",location,i,res)
            sys.exit()
        print("__________________")

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

    url = 'https://www.archlinux.org/mirrors/status/tier/2/json/'
    # results = get_upstream_from_tier2_paralel(url)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_upstream_from_tier2_paralel(url))
    print(result)
    print("finished")
    sys.exit()
    tier1=get_all_tier1()
    # result=
    tier2=get_all_tier2()
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
