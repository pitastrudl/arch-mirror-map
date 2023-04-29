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
unknown_countries = {}
unknown_countries['New Caledonia'] =  { 'latitude': '-21.1332', 'longitude' : '165.3772' }
savedir = "savedres/"
print(unknown_countries)
def get_all_tier2():
    j = requests.get("https://www.archlinux.org/mirrors/status/tier/2/json/").json()
    selected_pairs = dict(list(filter(lambda x: x[0].startswith("url"), j.items()))[:5])
    return selected_pairs

# fun for checking if dns resolves to multiple addresses
def check_dns_for_multiip():
    true = true 
    return 1

# save ip loc results to json 
def save_ip_loc(json_data, file_name):
    try:
        with open(file_name, 'w') as file:
            json.dump(json_data, file)
    except Exception as e:
        raise Exception(f"Could not save file: {e}")

# get ip loc results to json if exists
def load_ip_loc(file_name):
    try:
        with open(file_name, 'r') as file:
            json_data = json.load(file)
        return json_data
    except Exception as e:
        raise Exception(f"Could not load file: {e}")


def get_all_tier1():
    json_tier1 = requests.get("https://www.archlinux.org/mirrors/status/tier/1/json/").json()

    for i, res in enumerate(json_tier1["urls"]):
        # Add a new key-value pair to the `res` dictionary
        res["upstream_shortname"] = res["details"].split("/")[4]
        json_tier1["urls"][i] = res
        # print (json_tier1["urls"][i])

    return json_tier1 

def locate_mirror(url):
    mirror_loc={}
    if url["protocol"] == "http" or url["protocol"] == "https" :
        domain = re.match('^https?://([^/]+)(?:/.*)?$', url['url']).group(1)
        reader = geolite2.reader()

        try:
            for ip in sorted(set([i[4][0] for i in socket.getaddrinfo(domain, None)])):
                print("trying domain: ", domain , ", finding for ip:" + ip)
                mirror_loc = reader.get(ip)
                print(mirror_loc)
                if mirror_loc is not None:
                    mirror_loc["ip"]= ip
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

def country_is_saved(country):
    try:
        with open('countries.json') as f:
            data = json.load(f)
        return country in data if data else False
    except FileNotFoundError:
        return False

def load_saved_country(country):
    with open('countries.json') as f:
        data = json.load(f)
        country = data[country]
    return country["latitude"], country["longitude"]


def save_country(country_name, country_data):
    try:
        with open('countries.json') as f:
            countries = json.load(f)
    except FileNotFoundError:
        countries = {}

    if country_name in countries:
        print("Country already exists in JSON file")
        return False

    try:
        countries[country_name] = country_data
    except Exception as e:
        print(f"Failed to add new country: {e}")
        return False

    with open('countries.json', 'w') as f:
        json.dump(countries, f)
    
    return True

def ip_is_saved(ip):
    try:
        with open('ips.json') as f:
            data = json.load(f)
        return ip in data if data else False
    except FileNotFoundError:
        return False

def load_saved_ip(ip):
    with open('ips.json') as f:
        data = json.load(f)
        ip = data[ip]
    return ip["latitude"], ip["longitude"]


def save_ip(ip, ip_data):
    try:
        with open('ips.json') as f:
            ips = json.load(f)
    except FileNotFoundError:
        ips = {}

    if ip in ips:
        print("Country already exists in JSON file")
        return False

    try:
        ips[ip] = ip_data
    except Exception as e:
        print(f"Failed to add new country: {e}")
        return False

    with open('ips.json', 'w') as f:
        json.dump(ips, f)
        
    return True

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

    # last_executed_time = time.time()
    # current_time = time.time()
    # if current_time - last_executed_time > 1.0:  # check if more than 1 second has passed
    #     # do something
    #     print("Function executed more than 1 second ago.")
    #     last_executed_time = current_time  # update the last executed time


    tier1=get_all_tier1()
    # result=
    tier2=get_all_tier2()
    # for mirror in tier2["urls"]:
    m = folium.Map(location=[0, 0], zoom_start=2)
    loc_res=[]
    for i, res in enumerate(tier2["urls"]):
        location = locate_mirror(res)  # outputs data from geoip
        if not location:
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
            folium.Marker(location=[res['latitude'], res['longitude']], popup=res).add_to(m)
            # nomi = pgeocode.Nominatim(res["country_code"])
            # print(nomi)
            # print(nomi.query_longitude + " " + nomi.latitude)
            # save_ip_loc(res, res["country"])
        elif 'location' in location:
            print ("assigning new info")
            print(location)
            res['latitude'] = location['location']['latitude']
            res['longitude'] = location['location']['longitude']
            tier2["urls"][i] = res 
            print(tier2["urls"][i])
            folium.Marker(location=[res['latitude'], res['longitude']], popup=location["ip"]).add_to(m)
        else:
            print("didnt find loc!!! ",location,i,res)
            sys.exit()
        print("__________________")
        
        # print (json_tier1["urls"][i])
    m.save('map.html')
    sys.exit()






    countries = []
    ips = []
    m = folium.Map(location=[0, 0], zoom_start=2)
    offset=0.0
    missingips= []
    maincnt=0
    limit=5
    for mirror in tier2["urls"]:
        if mirror["protocol"] == "http":
            countries.append(mirror["country"])
            domain = re.match('^https?://([^/]+)(?:/.*)?$', mirror['url']).group(1)
            reader = geolite2.reader()
            # doing the upstream retrevial
            print(mirror) 
            new_url = "/".join(mirror["details"].split("/")[:-2]) + "/json"
            k = requests.get(new_url).json()
            print("upstream for: ", new_url, " is :", k["upstream"])
            
            try:
                for ip in sorted(set([i[4][0] for i in socket.getaddrinfo(domain, None)])):
                    print("finding for ip:" + ip)
                    json_str = reader.get(ip)
                    print(json_str)
                    if not json_str:
                        continue

                    if 'location' in json_str:
                        print("got ip "+ip + " "  + str(json_str['location']['latitude']) + " " +  str(json_str['location']['longitude']))
                        ips.append((ip,json_str['location']['latitude'],json_str['location']['longitude']))
                        folium.Marker(location=[json_str['location']['latitude'], json_str['location']['longitude']], popup=ip).add_to(m)
                    
                    else:
                        offset+=1
                        folium.Marker(location=[offset,0.0], popup=ip).add_to(m)
                        missingips.append(ip)
                    print("___________________")
            except socket.gaierror:
                print("got exception for "+domain)
                pass
        maincnt+=1
        print("main cnt is: ",maincnt)
        if maincnt > limit:
            print(maincnt)
            print("limit reached")
            break 
    
    m.save('map.html')
    print(missingips)
    # m = toMap()
    # m.setMap(countries, ips, "mirror-map.svg")

main()
