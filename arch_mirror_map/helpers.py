import json, re, requests,sys
ips = ""
countries= ""


def check_dns_for_multiip():
    true = true 
    return 1

def get_all_tier2(num_pairs=None):
    j = requests.get("https://www.archlinux.org/mirrors/status/tier/2/json/").json()

    selected_pairs = j['urls']
    
    # If num_pairs is specified, limit the number of pairs
    if num_pairs is not None:
        selected_pairs = selected_pairs[:num_pairs]
        
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


def get_upstream_from_tier2(tier_details_url):
    pattern = r'^(https?://[^/]+/[^/]+)/[^/]+/'
    match = re.match(pattern, tier_details_url)
    if match:
        new_url = match.group(0) + 'json'
        print(new_url)
        mirror_details = requests.get(new_url).json()
        if "upstream" not in mirror_details.keys():
            return "no_upstream"
        else:
            print("mirror upstream is:\n",mirror_details["upstream"])
            return mirror_details["upstream"]
    else:
        print("did not find upstream url, missing info! ask Arch team to fix")
        sys.exit()

def ip_is_saved(ip):
    global ips
    if ips == "":
        try:
            with open('ips.json') as f:
                ips = json.load(f)
            return ip in ips if ips else False
        except FileNotFoundError:
            return False
    else:
        print("found ip in cache")
        return ip in ips if ips else False

def load_saved_ip(ip):
    global ips
    if ips == "":
        with open('ips.json') as f:
            data = json.load(f)
            ip = data[ip]
        return ip["latitude"], ip["longitude"]
    else:
        print("loading ip from cache")
        return ips[ip]["latitude"], ips[ip]["longitude"]

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

def country_is_saved(arg_country):
    country = arg_country.strip()
    global countries 
    if country in countries:
        return country in countries if countries else False
    else:
        try:
            with open('countries.json') as f:
                data = json.load(f)
            return country in data if data else False
        except FileNotFoundError:
            return False

def load_saved_country(country):
    global countries
    if countries == "":
        with open('countries.json') as f:
            countries = json.load(f)
            country = countries[country]
        return country["latitude"], country["longitude"]
    else:
        return countries[country]["latitude"], countries[country]["longitude"]


def save_country(country_name, country_data):
    global countries
    if country_name in countries:
        print("Country already exists in JSON file")
        return False
    else:
        try:
            with open('countries.json') as f:
                countries = json.load(f)
        except FileNotFoundError:
            countries = {}
    try:
        countries[country_name] = country_data
    except Exception as e:
        print(f"Failed to add new country: {e}")
        return False

    with open('countries.json', 'w') as f:
        json.dump(countries, f)

    return True