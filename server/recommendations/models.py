from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Favourite(models.Model):
    farmerName = models.CharField(max_length=255)  # Farmer's name from local storage
    crop_name = models.CharField(max_length=255)
    crop_translation = models.CharField(max_length=255)
    user_entered_values = models.JSONField(null=True, blank=True)  # Store all user inputs as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmerName} - {self.crop_name}"

    
class Fertilizer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    npk_ratio = models.CharField(max_length=50, blank=True, null=True)  # Example: "46-0-0"
    standard_quantity_per_hectare = models.FloatField(default=50)  # Default value
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(default="https://example.com/default_fertilizer.jpg")
    buy_link = models.URLField(default="https://example.com/fertilizers")

    def __str__(self):
        return self.name
