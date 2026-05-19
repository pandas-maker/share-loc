import re
import math
import aiohttp
from datetime import datetime, timedelta

def generate_location_link(bot_username, user_id):
    """Generate a unique link for location requests"""
    # Format: https://t.me/bot_username?start=loc_req_123456789
    return f"https://t.me/{bot_username}?start=loc_req_{user_id}"

def extract_requester_id(link_data):
    """Extract requester ID from link data"""
    # Match patterns like: loc_req_123456789
    match = re.search(r'loc_req_(\d+)', link_data)
    return match.group(1) if match else None

async def get_address_from_coords(lat, lon):
    """Reverse geocoding - Get address from coordinates"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=18&addressdetails=1"
            async with session.get(url, headers={'User-Agent': 'LocationBot/1.0'}) as response:
                data = await response.json()
                if data.get('display_name'):
                    # Shorten address for display
                    address = data['display_name'].split(',')
                    if len(address) > 3:
                        return ', '.join(address[:3])
                    return data['display_name']
                return f"Lat: {lat:.4f}, Lon: {lon:.4f}"
    except Exception as e:
        print(f"Geocoding error: {e}")
        return f"Lat: {lat:.4f}, Lon: {lon:.4f}"

async def calculate_distance_directions(from_lat, from_lon, to_lat, to_lon):
    """Calculate distance, duration, and directions between two points"""
    
    # Calculate straight-line distance (Haversine formula)
    straight_distance = calculate_haversine_distance(from_lat, from_lon, to_lat, to_lon)
    
    # Try to get driving directions from OSRM
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://router.project-osrm.org/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}?overview=simplified&steps=true"
            async with session.get(url) as response:
                data = await response.json()
                
                if data.get('code') == 'Ok':
                    route = data['routes'][0]
                    distance_km = route['distance'] / 1000
                    duration_min = route['duration'] / 60
                    
                    # Extract turn-by-turn steps
                    steps = []
                    for leg in route['legs']:
                        for step in leg['steps']:
                            # Clean up the instruction
                            instruction = step['maneuver']['instruction']
                            # Remove HTML tags if any
                            instruction = re.sub(r'<[^>]+>', '', instruction)
                            steps.append(instruction)
                    
                    # Get route summary
                    summary = f"🚗 {distance_km:.1f} km • {duration_min:.0f} min"
                    
                    return {
                        'distance_km': round(distance_km, 1),
                        'distance_miles': round(distance_km * 0.621371, 1),
                        'duration_min': round(duration_min),
                        'duration_hours': round(duration_min / 60, 1),
                        'straight_distance_km': round(straight_distance, 1),
                        'steps': steps[:15],  # First 15 steps
                        'summary': summary,
                        'eta': calculate_eta(duration_min),
                        'map_url': f"https://www.google.com/maps/dir/{from_lat},{from_lon}/{to_lat},{to_lon}"
                    }
    except Exception as e:
        print(f"Directions API error: {e}")
    
    # Fallback if OSRM fails
    return {
        'distance_km': round(straight_distance, 1),
        'distance_miles': round(straight_distance * 0.621371, 1),
        'duration_min': round(straight_distance * 2),  # Rough estimate: 2 min per km
        'duration_hours': round(straight_distance * 2 / 60, 1),
        'straight_distance_km': round(straight_distance, 1),
        'steps': [],
        'summary': f"📍 {straight_distance:.1f} km straight-line distance",
        'eta': calculate_eta(straight_distance * 2),
        'map_url': f"https://www.google.com/maps/dir/{from_lat},{from_lon}/{to_lat},{to_lon}"
    }

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def calculate_eta(duration_minutes):
    """Calculate estimated arrival time"""
    now = datetime.now()
    eta = now + timedelta(minutes=duration_minutes)
    
    if eta.date() == now.date():
        return eta.strftime("%I:%M %p")
    else:
        return eta.strftime("%I:%M %p on %b %d")