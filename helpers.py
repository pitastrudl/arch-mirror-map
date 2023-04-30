import json
ips = ""
# append or create to json with ip and lat/long coords
def save_ip_loc(json_data, file_name):
    try:
        with open(file_name, 'w') as file:
            json.dump(json_data, file)
    except Exception as e:
        raise Exception(f"Could not save file: {e}")

# Loads ip location 
def load_ip_loc(file_name):
    try:
        with open(file_name, 'r') as file:
            json_data = json.load(file)
        return json_data
    except Exception as e:
        raise Exception(f"Could not load file: {e}")


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