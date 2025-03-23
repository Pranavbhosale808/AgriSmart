import pickle
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Fertilizer
import gdown
import pandas as pd
import numpy as np


# Google Drive File IDs for models
file_ids = {
    "crop_model": "1CZQoCicOE8wj10cik7aLKLjAcyH1_KEd",
    "fertilizer_model": "1ETwwudB0gAsOIopfUg76fQKMo_cykvBR",
    "crop_yield_model": "1BCK-elhagCyH0tW5eoKvVYkkBNMrfLm3"
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

with open(model_paths["crop_yield_model"], "rb") as f:
   crop_yield_model = pickle.load(f)


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

        # Validation for each parameter
        if not (0 <= N <= 140):
            return JsonResponse({'error': 'N value out of range (0-140)'}, status=400)

        if not (5 <= P <= 145):
            return JsonResponse({'error': 'P value out of range (5-145)'}, status=400)

        if not (5 <= K <= 205):
            return JsonResponse({'error': 'K value out of range (5-205)'}, status=400)

        if not (8.825674745 <= temperature <= 43.67549305):
            return JsonResponse({'error': 'Temperature value out of range (8.82 - 43.67)'}, status=400)

        if not (14.25803981 <= humidity <= 99.98187601):
            return JsonResponse({'error': 'Humidity value out of range (14.25 - 99.98)'}, status=400)

        if not (3.504752314 <= ph <= 10):  # Ensuring max is 10
            return JsonResponse({'error': 'pH value out of range (3.5 - 10)'}, status=400)

        if not (20.21126747 <= rainfall <= 298.5601175):
            return JsonResponse({'error': 'Rainfall value out of range (20.21 - 298.56)'}, status=400)

        # Prepare features for prediction
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

        # Get top 3 predictions
        predictions = crop_model.predict_proba(features)[0]
        top_indices = np.argsort(predictions)[-3:][::-1]  # Top 3 crops
        
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
        "name": "Potato",
        "translation": "आलू",
        "image": "crop_images/Potato.jpg",
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
        "name": "Water Melon",
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
        "name": "Soyabean",
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
        "name": "Black Gram",
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
        "name": "Matki",
        "translation": "मोठ",
        "image": "crop_images/Mothbeans.jpeg",
        "soil_type": "Sandy, Well-drained",
        "conditions": "Requires dry climate, high sunlight exposure."
    },
    19: {
        "name": "Pegeon Pea (Arhar Fali)",
        "translation": "अरहर",
        "image": "crop_images/Pigeonpeas.jpeg",
        "soil_type": "Loamy, Well-drained",
        "conditions": "Requires warm temperature, moderate rainfall."
    },
    20: {
        "name": "Kidneybeans",
        "translation": "राजमा",
        "image": "crop_images/Kidneybeans.jpg",
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
        "name": "Sugarcane",
        "translation": "गन्ना",
        "image": "crop_images/Sugarcane.jpg",
        "soil_type": "Volcanic, Loamy",
        "conditions": "Thrives in humid, high-altitude regions, moderate rainfall."
    },
}

        
        # Construct response data for top crops
        top_crops = []
        for idx in top_indices:
            crop_data = crop_info.get(idx + 1, {"name": "Unknown", "translation": "Unknown", "image": "default.jpg", "soil_type": "Unknown", "conditions": "Unknown"})
            image_url = request.build_absolute_uri(f"{settings.STATIC_URL}{crop_data['image']}")
            top_crops.append({
                'crop': crop_data['name'],
                'translation': crop_data['translation'],
                'image': image_url,
                'soil_type': crop_data['soil_type'],
                'conditions': crop_data['conditions']
            })

        # Return the response as JSON
        return JsonResponse({'recommendations': top_crops})
    except Exception as e:
        return JsonResponse({'error': f'Internal Server Error: {str(e)}'}, status=500)


#################################################### CROP YIELD ####################################

# Encoding mappings
state_mapping = {
    'Andhra Pradesh': 0, 'Arunachal Pradesh': 1, 'Assam': 2, 'Bihar': 3, 'Chhattisgarh': 4, 'Delhi': 5,
    'Goa': 6, 'Gujarat': 7, 'Haryana': 8, 'Himachal Pradesh': 9, 'Jammu and Kashmir': 10, 'Jharkhand': 11,
    'Karnataka': 12, 'Kerala': 13, 'Madhya Pradesh': 14, 'Maharashtra': 15, 'Manipur': 16, 'Meghalaya': 17,
    'Mizoram': 18, 'Nagaland': 19, 'Odisha': 20, 'Puducherry': 21, 'Punjab': 22, 'Sikkim': 23, 'Tamil Nadu': 24,
    'Telangana': 25, 'Tripura': 26, 'Uttar Pradesh': 27, 'Uttarakhand': 28, 'West Bengal': 29
}

season_mapping = {
    'Autumn': 0, 'Kharif': 1, 'Rabi': 2, 'Summer': 3, 'Whole Year': 4, 'Winter': 5
}

crop_mapping = {
    'Arecanut': 0, 'Arhar/Tur': 1, 'Bajra': 2, 'Banana': 3, 'Barley': 4, 'Black pepper': 5, 'Cardamom': 6, 
    'Cashewnut': 7, 'Castor seed': 8, 'Coconut': 9, 'Coriander': 10, 'Cotton(lint)': 11, 'Cowpea(Lobia)': 12,
    'Dry chillies': 13, 'Garlic': 14, 'Ginger': 15, 'Gram': 16, 'Groundnut': 17, 'Guar seed': 18, 'Horse-gram': 19,
    'Jowar': 20, 'Jute': 21, 'Khesari': 22, 'Linseed': 23, 'Maize': 24, 'Masoor': 25, 'Mesta': 26, 'Moong(Green Gram)': 27,
    'Moth': 28, 'Niger seed': 29, 'Oilseeds total': 30, 'Onion': 31, 'Other Rabi pulses': 32, 'Other Cereals': 33, 
    'Other Kharif pulses': 34, 'Other Summer Pulses': 35, 'Peas & beans (Pulses)': 36, 'Potato': 37, 'Ragi': 38,
    'Rapeseed &Mustard': 39, 'Rice': 40, 'Safflower': 41, 'Sannhamp': 42, 'Sesamum': 43, 'Small millets': 44, 
    'Soyabean': 45, 'Sugarcane': 46, 'Sunflower': 47, 'Sweet potato': 48, 'Tapioca': 49, 'Tobacco': 50, 
    'Turmeric': 51, 'Urad': 52, 'Wheat': 53, 'other oilseeds': 54
}

@csrf_exempt
def crop_yield_prediction(request):
    try:
        # Extracting input parameters safely
        state = request.GET.get('state', '').strip()
        season = request.GET.get('season', '').strip()
        crop = request.GET.get('crop', '').strip()
        crop_year = request.GET.get('crop_year', '').strip()
        area = request.GET.get('area', '').strip()
        production = request.GET.get('production', '').strip()
        annual_rainfall = request.GET.get('annual_rainfall', '').strip()
        fertilizer = request.GET.get('fertilizer', '').strip()
        pesticide = request.GET.get('pesticide', '').strip()

        # Encoding categorical variables
        state_encoded = state_mapping.get(state, -1)
        season_encoded = season_mapping.get(season, -1)
        crop_encoded = crop_mapping.get(crop, -1)

         # Validate input values
        if -1 in [state_encoded, season_encoded, crop_encoded, crop_year]:
            return JsonResponse({'error': 'Invalid input values'}, status=400)

        # Prepare features for prediction
        features = np.array([[crop_encoded, crop_year, season_encoded, state_encoded, area, production, annual_rainfall, fertilizer, pesticide]])
        print(features)

        # Predict yield
        predicted_yield = crop_yield_model.predict(features)[0]

        # Construct response
        return JsonResponse({'predicted_yield': predicted_yield})

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

# Load the trained model & encoders
with open("recommendations/static/models/fertilizer_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("recommendations/static/models/encoder.pkl", "rb") as encoder_file:
    label_encoders = pickle.load(encoder_file)

def recommend_organic_fertilizer(request):
    try:
        crop = request.GET.get("crop")
        soil = request.GET.get("soil")
        rainfall = float(request.GET.get("rainfall"))
        weather = request.GET.get("weather")
        ph_level = float(request.GET.get("ph"))

        # Encode categorical values
        if crop in label_encoders["Crop Type"].classes_:
            crop_encoded = label_encoders["Crop Type"].transform([crop])[0]
        else:
            return JsonResponse({"error": "Invalid crop type"}, status=400)

        if soil in label_encoders["Soil Type"].classes_:
            soil_encoded = label_encoders["Soil Type"].transform([soil])[0]
        else:
            return JsonResponse({"error": "Invalid soil type"}, status=400)

        if weather in label_encoders["Weather Condition"].classes_:
            weather_encoded = label_encoders["Weather Condition"].transform([weather])[0]
        else:
            return JsonResponse({"error": "Invalid weather condition"}, status=400)

        # Prepare input array
        input_data = np.array([[crop_encoded, soil_encoded, rainfall, weather_encoded, ph_level]])

        # Predict Fertilizer
        predicted_label = model.predict(input_data)[0]
        predicted_fertilizer = label_encoders["Recommended Organic Fertilizer"].inverse_transform([predicted_label])[0]

        # Get top 3 similar fertilizers (based on probabilities)
        probabilities = model.predict_proba(input_data)[0]
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_fertilizers = label_encoders["Recommended Organic Fertilizer"].inverse_transform(top_3_indices)

        return JsonResponse({
            "recommended_fertilizers": list(top_3_fertilizers)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
