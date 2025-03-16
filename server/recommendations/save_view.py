from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Favourite
from .serializers import FavouriteSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@api_view(['POST'])
def favourite(request):
    # Extract farmer name from frontend (local storage)
    farmerName = request.data.get("farmerName", None)

    if not farmerName:
        return Response({"error": "Farmer name is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Save crop details
    serializer = FavouriteSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_favourite(request, farmerName):
    crops = Favourite.objects.filter(farmerName=farmerName)
    serializer = FavouriteSerializer(crops, many=True)
    return Response(serializer.data)

@csrf_exempt 
def delete_favourite(request, farmerName, crop_name, created_at):
    if request.method == "DELETE":
        try:
            # Since created_at is now passed in the URL, no need to extract from the body.
            print(f"Deleting crop with crop_name: {crop_name}, farmerName: {farmerName}, created_at: {created_at}")

            # Find the crop using farmerName, crop_name, and created_at
            crop = Favourite.objects.get(farmerName=farmerName, crop_name=crop_name, created_at=created_at)
            print(f"Deleting Crop: {crop.crop_name}, Farmer: {crop.farmerName}, Date: {crop.created_at}")

            crop.delete()
            return JsonResponse({"message": "Deleted successfully"}, status=200)

        except Favourite.DoesNotExist:
            return JsonResponse({"error": "Crop not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)


