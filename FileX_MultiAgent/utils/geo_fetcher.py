import os
import requests

def geo_coordinates_search(location_name: str, max_rows: int = 10, username: str | None = None, fuzzy: float = 0.6,) -> None:
    """
    Searches GeoNames for a location name and prints the returned details (JSON).

    You MUST have a GeoNames username:
      - pass it in as `username=...`, OR
      - set env var GEONAMES_USERNAME

    
    fuzzy:
      - float between 0.0 and 1.0 (e.g. 0.6) controls fuzzy search strength
    """
    if not location_name or not location_name.strip():
        raise ValueError("location_name cannot be empty")


    if not username:
        raise ValueError("GeoNames username is required. Pass username=... or set GEONAMES_USERNAME.")
    
    if not (0.0 <= fuzzy <= 1.0):
        raise ValueError("fuzzy must be between 0.0 and 1.0")


    url = "http://api.geonames.org/searchJSON"
    params = {
        "q": location_name,     # search over all attributes
        "maxRows": max_rows,
        "username": username,
        "fuzzy": fuzzy,  
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    geonames = data.get("geonames", [])
    if not geonames:
        raise LookupError(f"No results found for: {location_name}")

    top = geonames[0]
    lat = top.get("lat")
    lng = top.get("lng")
    country = top.get("countryName") or top.get("countryCode")

    if lat is None or lng is None:
        raise KeyError(f"Missing lat/lng in GeoNames response for: {location_name}")
    if not country:
        raise KeyError(f"Missing countryName/countryCode in GeoNames response for: {location_name}")

    return float(lat), float(lng), str(country)


# Example:
