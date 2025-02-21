# recommendations/serializers.py
from rest_framework import serializers
from .models import CropRecommendation, FertilizerRecommendation, CropYieldPrediction

class FertilizerRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FertilizerRecommendation
        fields = '__all__'

class CropYieldPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropYieldPrediction
        fields = '__all__'

class CropRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropRecommendation
        fields = '__all__'
