from django.db import models
from django.contrib.auth.models import User

class FertilizerRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)  # Crop for which the fertilizer is recommended
    recommended_fertilizer = models.TextField()  # The recommended fertilizer
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation

    def __str__(self):
        return f"{self.crop} - {self.recommended_fertilizer}"

class CropYieldPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)  # Crop for which the yield is predicted
    predicted_yield = models.FloatField()  # Predicted yield value
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation

    def __str__(self):
        return f"{self.crop} - {self.predicted_yield}"

class CropRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop_name = models.CharField(max_length=100)  # Name of the recommended crop
    fertilizer_recommendation = models.TextField()  # Recommended fertilizer for the crop
    yield_prediction = models.FloatField()  # Predicted yield for the crop
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation

    def __str__(self):
        return self.crop_name


class Fertilizer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    npk_ratio = models.CharField(max_length=50, blank=True, null=True)  # Example: "46-0-0"
    standard_quantity_per_hectare = models.FloatField(default=50)  # Default value
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(default="https://example.com/default_fertilizer.jpg")
    buy_link = models.URLField(default="https://example.com/fertilizers")

    def __str__(self):
        return self.name
