import httpx
from fastapi import FastAPI , HTTPException

# ----------- Function Geocoding   ---------
# Out source 

async def geocode_address(address: str) -> tuple[float, float]:

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q" : address, "format": "json", "limit": 1}

    headers = {"User-Agent": "taxipred-student-project"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status() # trow an error if status != 2xx
        data = response.json()  # convert in list/dict

        if not data:
            raise HTTPException(status_code=400, detail=f"Address not found: {address}")
        
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon 

async def osrm_route_metrics(
    start_lat: float, start_lon: float, end_lat: float, end_lon: float
    ) -> tuple[float, float, list[list[float]]]:
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {"overview": "full", "geometries": "geojson"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise HTTPException(status_code=400, detail="Routing failed with OSRM.")
        # convert from mt in km and from sec in min 
        route = data["routes"][0]
        distance_km = route["distance"] / 1000.0
        duration_min = route["duration"] / 60.0
        # convert in [lat, lon] 
        coords_lonlat = route["geometry"]["coordinates"]

        # list comparehension
        route_latlon = [[lat,lon] for lon , lat in coords_lonlat]           


        return distance_km, duration_min, route_latlon
