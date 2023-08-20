import json, re, requests,sys,ssl
import httpx
import asyncio
ips = ""
countries= ""
async def fetch_data(url):
    if isinstance(url, httpx.URL):
        url = str(url)
    if isinstance(url, dict):
        url = url["details"]
        pattern = r'^(https?://[^/]+/[^/]+)/[^/]+/'
        match = re.match(pattern, url)
        if match:
            url = match.group(0) + 'json'
            print(url)
            url

    if not url.startswith("http://") and not url.startswith("https://"):
        # If the URL doesn't start with "http://" or "https://", we return None
        return None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 301:
                url = response.headers["Location"]
                response = await client.get(url)
            json_data = response.json()
            urls = json_data['urls']
            tasks = [fetch_data(details) for details in urls if details.startswith("http://") or details.startswith("https://")]
            results = await asyncio.gather(*tasks)
            return results
    except ssl.SSLError as e:
        print(f"SSL error occurred while fetching {url}: {e}")
        return []
    except Exception as e:
        print(f"An error occurred while fetching {url}: {e}")
        return []

async def get_upstream_from_tier2_paralel(url):
    if isinstance(url, httpx.URL):
        url = str(url)
    if isinstance(url, dict):
        url = url["url"]
    if not url.startswith("http://") and not url.startswith("https://"):
        # If the URL doesn't start with "http://" or "https://", we return None
        return None
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 301:
            url = response.headers["Location"]
            response = await client.get(url)
        json_data = response.json()
        urls = json_data['urls']
        tasks = [fetch_data(details) for details in urls]
        results = await asyncio.gather(*tasks)
        return results


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
            print("checking if ip is saved in file")
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
        print("reading saved ips from file")
        with open('ips.json') as f:
            data = json.load(f)
            ip = data[ip]
        return ip["latitude"], ip["longitude"]
    else:
        print("loading ip from cache")
        return ips[ip]["latitude"], ips[ip]["longitude"]

def save_ip(ip, ip_data):
    try:
        print("saving ip to file")
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

    print("saving ip to file")
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
            print("this is country:\n",country)
            print("checking saved country in file")
            with open('countries.json') as f:
                data = json.load(f)
            return country in data if data else False
        except FileNotFoundError:
            return False

def load_saved_country(country):
    global countries
    if countries == "":
        print("loading saved country from file")
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
        print("saving country to file")
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

    print("saving country to file")
    with open('countries.json', 'w') as f:
        json.dump(countries, f)

    return True