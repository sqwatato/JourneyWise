from amadeus import Client, ResponseError
import googlemaps
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *

# import requests
import environ
env = environ.Env()
environ.Env.read_env()
maps_api = env('MAP_API_KEY')

gmaps = googlemaps.Client(key=maps_api)

amadeus = Client(client_id=env('AMADEUS_API_KEY'),
                 client_secret=env('AMADEUS_SECRET_KEY'))


def index(request):
    city = Destination.objects.get(id=1).city
    country = Destination.objects.get(id=1).country
    try:
        response = amadeus.reference_data.locations.cities.get(
            keyword=city).result
        # response = {'meta': {'count': 1, 'links': {'self': 'https://test.api.amadeus.com/v1/reference-data/locations/cities?keyword=Hong+Kong&max=1000'}}, 'data': [{'type': 'location', 'subType': 'city', 'name': 'Hong Kong', 'iataCode': 'HKG', 'address': {'countryCode': 'HK', 'stateCode': 'HK-ZZZ'}, 'geoCode': {'latitude': 22.27832, 'longitude': 114.17469}}]}
        lat, lon = response['data'][0]['geoCode'].values()
        # print(lat, lon)
    except ResponseError as error:
        response = "Couldn't find the city: " + city

    loc = (lat, lon)
    eat = gmaps.places_nearby(location=loc, radius=20000, type="restaurant")[
        'results'][:6]
    # places = gmaps.places_nearby(location=loc, radius=50000, type="tourist_attraction")['results'][:6]
    places = gmaps.places_nearby(
        location=loc, radius=20000, keyword="Things to Do")['results'][:6]
    # print(eat,places)

    return render(request, "main/index.html", {
        "eat": eat,
        "places": places,
        "api": maps_api
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "main/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "main/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "main/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "main/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "main/register.html")


def attractions(request):
    return render(request, "main/attractions.html")

def intro(request):
    return render(request, "main/intro.html")
