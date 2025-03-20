from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .auth_views import signup, login, logout , auth_status
from .views import get_labs 
from .save_view import  favourite,get_favourite,delete_favourite
from .api_views import get_external_data,get_user_location

urlpatterns = [
    path('crop/', views.crop_recommendation, name='crop_recommendation'),
    path('fertilizer/', views.fertilizer_recommendation, name='fertilizer_recommendation'),
    path('crop-yield/', views.crop_yield_prediction, name='crop_yield_prediction'),
    path("labs/", get_labs, name="get_labs"),


    # Authetication Urls
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('auth_status/', auth_status, name="auth_status"),


    #Save Crop Urls
    path('favourite/', favourite, name='favourite'),
    path('get_favourite/<str:farmerName>/', get_favourite, name='get_favourite'),
    path('delete_favourite/<str:farmerName>/<str:crop_name>/<str:created_at>/',delete_favourite,name='delete_favourite'),


    #External API Urls
    path('market-price/', get_external_data, name='get_external_data'),
    path("user-location/",get_user_location, name="get_user_location"),
]

if settings.DEBUG:                          
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])