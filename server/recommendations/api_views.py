import requests
from django.http import JsonResponse
import os

def get_external_data(request):
    # Get parameters from request
    state = request.GET.get("state", "Maharashtra")  # Default: Maharashtra
    district = request.GET.get("district", "Akola")  # Default: Akola
    commodity = request.GET.get("commodity", "Sunflower")  # Default: Sunflower
    arrival_date = request.GET.get("arrival_date", "01/01/2025")  # Default: Sample date

    # External API URL
    url = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
    
    # Parameters for API
    params = {
        "api-key": os.environ.get('MARKET_API'),
        "format": "json",
        "filters[State.keyword]": state,
        "filters[District.keyword]": district,
        "filters[Commodity.keyword]": commodity,
        "filters[Arrival_Date]": arrival_date,
    }

    # Fetch data from API
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": "Failed to fetch data"}, status=500)


def get_user_location(request):
    API_KEY = os.environ.get('LOCATION_API_KEY')  

    try:
        response = requests.get(f"https://ipinfo.io/json?token={API_KEY}")
        
        if response.status_code == 200:
            data = response.json()
            location_data = {
                "state": data.get("region", "Unknown"),
                "district": data.get("city", "Unknown"),
            }
            return JsonResponse(location_data)
        else:
            return JsonResponse({"error": "Failed to fetch location"}, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)