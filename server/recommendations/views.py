import pickle
import os
from django.conf import settings
from django.http import JsonResponse
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Fertilizer
import pandas as pd
import gdown


# Google Drive File IDs for models
file_ids = {
    "crop_model": "1CZQoCicOE8wj10cik7aLKLjAcyH1_KEd",
    "fertilizer_model": "1ETwwudB0gAsOIopfUg76fQKMo_cykvBR",
    # "crop_yield_model": "1gYxsnvimVHCqGo0ofF_3SAeWY5FkRvlW"
}

# Directory to store downloaded models
models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

# Function to download model files if not already downloaded
def download_model(file_id, filename):
    output_path = os.path.join(models_dir, filename)
    if not os.path.exists(output_path):  # Check if file already exists
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"Downloading {filename}...")
        gdown.download(url, output_path, quiet=False)
    else:
        print(f"{filename} already exists. Skipping download.")
    return output_path

# Download models only if they are not present
model_paths = {
    name: download_model(file_id, f"{name}.pkl")
    for name, file_id in file_ids.items()
}

# Load models
with open(model_paths["crop_model"], "rb") as f:
    crop_model = pickle.load(f)

with open(model_paths["fertilizer_model"], "rb") as f:
    fertilizer_model = pickle.load(f)

# with open(model_paths["crop_yield_model"], "rb") as f:
#    classifier = pickle.load(f)
    


# Dictionary mapping ML prediction to fertilizer details
fertilizer_info = {
    0: {"name": "10-26-26", "api_id": "123", "application_rate": 90},
    1: {"name": "14-35-14", "api_id": "124", "application_rate": 80},
    2: {"name": "17-17-17", "api_id": "125", "application_rate": 100},
    3: {"name": "20-20", "api_id": "126", "application_rate": 85},
    4: {"name": "28-28", "api_id": "127", "application_rate": 70},
    5: {"name": "DAP", "api_id": "128", "application_rate": 120},
    6: {"name": "Urea", "api_id": "129", "application_rate": 110}
}
@csrf_exempt
def fertilizer_recommendation(request):
    try:
        # Get parameters from request
        soil_type = request.GET.get('soil_type')
        crop_type = request.GET.get('crop_type')
        land_area = float(request.GET.get('land_area', 1))  # Default 1 hectare

        if soil_type is None or crop_type is None:
            return JsonResponse({'error': 'Missing soil_type or crop_type'}, status=400)

        soil_type = int(soil_type)
        crop_type = int(crop_type)

        temperature = float(request.GET.get('temperature', 0))
        humidity = float(request.GET.get('humidity', 0))
        moisture = float(request.GET.get('moisture', 0))
        nitrogen = float(request.GET.get('nitrogen', 0))
        phosphorous = float(request.GET.get('phosphorous', 0))
        potassium = float(request.GET.get('potassium', 0))

        # ML Model Prediction
        features = np.array([[temperature, humidity, moisture, soil_type, crop_type, nitrogen, phosphorous, potassium]])
        predicted_index = int(fertilizer_model.predict(features)[0])  # Ensure integer output

        # Convert numerical prediction to fertilizer name
        if predicted_index not in fertilizer_info:
            return JsonResponse({"error": "Invalid prediction from ML model"}, status=400)

        predicted_fertilizer = fertilizer_info[predicted_index]["name"]
        application_rate = fertilizer_info[predicted_index]["application_rate"]  # Access application rate

        # Fetch fertilizer details from the database
        fertilizer = Fertilizer.objects.filter(name=predicted_fertilizer).first()

        if not fertilizer:
            return JsonResponse({"error": "Fertilizer not found in database"}, status=404)

        # Calculate required quantity based on land area
        required_qty = application_rate * land_area  # Use application rate from dictionary

        response_data = {
            "fertilizer": fertilizer.name,
            "npk_ratio": fertilizer.npk_ratio,
            "buy_link": fertilizer.buy_link,
            "description": fertilizer.description or "Usage details not available",
            "land_area": land_area,
            "application_rate": application_rate,  # Include application rate in response
            "recommended_quantity_kg": round(required_qty, 2)
        }

        return JsonResponse(response_data)
    
    except ValueError as e:
        return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
def crop_yield_prediction(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)

            # Extract features from the request
            area = data.get('Area')
            item = data.get('Item')
            average_rain_fall_mm_per_year = data.get('average_rain_fall_mm_per_year')
            pesticides_tonnes = data.get('pesticides_tonnes')
            avg_temp = data.get('avg_temp')

            # Prepare the input for the model
            features = np.array([[area, item, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp]])

            # Make prediction
            prediction = classifier.predict(features)

            # Return the prediction as JSON
            return JsonResponse({'predicted_yield': prediction[0]})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
def crop_recommendation(request):
    try:
        # Get input parameters from the request
        N = float(request.GET.get('N', 0))
        P = float(request.GET.get('P', 0))
        K = float(request.GET.get('K', 0))
        temperature = float(request.GET.get('temperature', 0))
        humidity = float(request.GET.get('humidity', 0))
        ph = float(request.GET.get('ph', 0))
        rainfall = float(request.GET.get('rainfall', 0))

        # Prepare features for prediction
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

        # Make prediction
        prediction = crop_model.predict(features)[0]
        print("Predicted crop : ",prediction)

        # Crop info dictionary with corrected relative image paths
        crop_info = {
    1: {
        "name": "Rice",
        "translation": "चावल",
        "image": "crop_images/Rice.jpg",
        "soil_type": "Clayey, Loamy",
        "conditions": "Requires standing water, humid climate, high rainfall."  
    },
    2: {
        "name": "Maize",
        "translation": "मक्का",
        "image": "crop_images/Maize.jpg",
        "soil_type": "Well-drained, Sandy loam",
        "conditions": "Grows well in warm, temperate climate, needs moderate rainfall."
    },
    3: {
        "name": "Jute",
        "translation": "जूट",
        "image": "crop_images/Jute.jpg",
        "soil_type": "Alluvial, Loamy",
        "conditions": "Requires warm and humid climate, plenty of water."
    },
    4: {
        "name": "Cotton",
        "translation": "कपास",
        "image": "crop_images/Cotton.jpg",
        "soil_type": "Black, Well-drained Loamy",
        "conditions": "Requires warm climate, moderate rainfall, and good drainage."
    },
    5: {
        "name": "Coconut",
        "translation": "नारियल",
        "image": "crop_images/Coconut.jpg",
        "soil_type": "Sandy loam, Coastal soil",
        "conditions": "Needs hot, humid climate, high moisture retention."
    },
    6: {
        "name": "Papaya",
        "translation": "पपीता",
        "image": "crop_images/Papaya.jpg",
        "soil_type": "Well-drained Loamy, Sandy",
        "conditions": "Thrives in warm, tropical climate, well-drained soil."
    },
    7: {
        "name": "Orange",
        "translation": "संतरा",
        "image": "crop_images/Oranges.jpg",
        "soil_type": "Sandy loam, Well-drained",
        "conditions": "Needs warm, dry climate with irrigation support."
    },
    8: {
        "name": "Apple",
        "translation": "सेब",
        "image": "crop_images/Apple.jpg",
        "soil_type": "Well-drained Loamy",
        "conditions": "Requires cold climate, moderate rainfall, good drainage."
    },
    9: {
        "name": "Muskmelon",
        "translation": "खरबूजा",
        "image": "crop_images/Muskmelon.jpeg",
        "soil_type": "Sandy loam, Well-drained",
        "conditions": "Requires warm temperature, dry climate, moderate irrigation."
    },
    10: {
        "name": "Watermelon",
        "translation": "तरबूज",
        "image": "crop_images/Watermelon.jpg",
        "soil_type": "Sandy loam, Well-drained",
        "conditions": "Thrives in hot, dry climate with minimal irrigation."
    },
    11: {
        "name": "Grapes",
        "translation": "अंगूर",
        "image": "crop_images/Grapes.jpg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Requires hot and dry climate, needs less water."
    },
    12: {
        "name": "Soyachuncks",
        "translation": "सोयाबीन",
        "image": "crop_images/Soyachuncks.jpg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Requires moderate rainfall and warm temperature."
    },
    13: {
        "name": "Banana",
        "translation": "केला",
        "image": "crop_images/Banana.jpg",
        "soil_type": "Clayey, Loamy",
        "conditions": "Needs warm, humid climate, well-drained soil."
    },
    14: {
        "name": "Pomegranate",
        "translation": "अनार",
        "image": "crop_images/Pomegranate.jpg",
        "soil_type": "Sandy loam, Well-drained",
        "conditions": "Thrives in semi-arid conditions, requires less water."
    },
    15: {
        "name": "Lentil",
        "translation": "दाल",
        "image": "crop_images/Lentil.jpeg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Requires cool climate, moderate irrigation."
    },
    16: {
        "name": "Blackgram",
        "translation": "उड़द",
        "image": "crop_images/Blackgram.jpg",
        "soil_type": "Sandy loam, Well-drained",
        "conditions": "Needs warm, semi-arid climate, moderate irrigation."
    },
    17: {
        "name": "Mungbean",
        "translation": "मूंग",
        "image": "crop_images/Mungbean.jpg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Thrives in warm temperature, needs moderate rainfall."
    },
    18: {
        "name": "Mothbeans",
        "translation": "मोठ",
        "image": "crop_images/Mothbeans.jpeg",
        "soil_type": "Sandy, Well-drained",
        "conditions": "Requires dry climate, high sunlight exposure."
    },
    19: {
        "name": "Pigeonpeas",
        "translation": "अरहर",
        "image": "crop_images/Pigeonpeas.jpeg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Requires warm temperature, moderate rainfall."
    },
    20: {
        "name": "Kidneybeans",
        "translation": "राजमा",
        "image": "crop_images/Kidneybeans.jpeg",
        "soil_type": "Sandy loam, Well-drained",
        "conditions": "Grows well in warm climate, moderate water needs."
    },
    21: {
        "name": "Chickpea",
        "translation": "चने",
        "image": "crop_images/Chickpea.jpeg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Needs cool climate, less water, requires dry spells."
    },
    22: {
        "name": "Coffee",
        "translation": "कॉफी",
        "image": "crop_images/Coffee.jpg",
        "soil_type": "Volcanic, Loamy",
        "conditions": "Thrives in humid, high-altitude regions, moderate rainfall."
    },
}


        # Get crop details or return "Unknown"
        crop_data = crop_info.get(prediction, {"name": "Unknown", "translation": "Unknown", "image": "default.jpg","soil_type":"Unknown","conditions":"Unknown"})

        # Construct full image URL using the static directory
        image_url = request.build_absolute_uri(f"{settings.STATIC_URL}{crop_data['image']}")
        print("Image",image_url)

        # Return the response as JSON
        return JsonResponse({
            'crop': crop_data['name'],
            'translation': crop_data['translation'],
            'image': image_url,
            'soil_type':crop_data['soil_type'],
            'conditions':crop_data['conditions']

        })

    except Exception as e:
        return JsonResponse({'error': f'Internal Server Error: {str(e)}'}, status=500)
    
@csrf_exempt
def get_labs(request):
    state = request.GET.get("state")
    district = request.GET.get("district")

    if not state or not district:
        return JsonResponse({"error": "State and District required"}, status=400)

    # Get XLSX file path
    file_path = os.path.join(settings.BASE_DIR, "recommendations/static/soil_testing_labs.xlsx")

    if not os.path.exists(file_path):
        return JsonResponse({"error": "Dataset not found"}, status=404)

    # Read the dataset
    df = pd.read_excel(file_path)

    # Convert columns & input to lowercase for better matching
    df["State"] = df["State"].astype(str).str.lower().str.strip()
    df["District"] = df["District"].astype(str).str.lower().str.strip()
    
    state = state.lower().strip()
    district = district.lower().strip()

    # Filter data
    filtered_data = df[(df["State"] == state) & (df["District"] == district)]

    if filtered_data.empty:
        return JsonResponse({"message": "No labs found for this location"}, status=404)

    labs = filtered_data.to_dict(orient="records")
    return JsonResponse({"labs": labs}, safe=False)







