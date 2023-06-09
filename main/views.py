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


def attractions(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.method == 'POST':
        request.user.destinations.add(Destination.objects.get(id=id))
        return HttpResponseRedirect(reverse("index"))

    city = Destination.objects.get(id=id).city
    country = Destination.objects.get(id=id).country
    place = city + ", " + country
    response = gmaps.find_place(f"{city}, {country}", "textquery", fields=[
                                "geometry/location", "photos"])
    photo = response['candidates'][0]['photos'][0]['photo_reference']
    # print(response)
    lat, lon = response['candidates'][0]['geometry']['location'].values()
    loc = (lat, lon)
    eat = gmaps.places_nearby(location=loc, radius=20000, type="restaurant")[
        'results'][:6]
    # places = gmaps.places_nearby(location=loc, radius=50000, type="tourist_attraction")['results'][:6]
    places = gmaps.places_nearby(
        location=loc, radius=20000, keyword="Things to Do")['results'][:6]
    try:
        shoppingResponse = amadeus.shopping.activities.get(latitude=lat, longitude=lon).result
        if shoppingResponse['meta']['count'] == 0:
            shopping = False
        else:
            shopping = []
            for result in shoppingResponse['data']:
                if len(result['pictures']) > 0 and len(result['shortDescription']) < 200: 
                    shopping.append(result)
                if len(shopping) >= 3:
                    break
        # print(shopping)
    except ResponseError:
        shopping = False
    try:
        safe = amadeus.safety.safety_rated_locations.get(latitude=lat, longitude=lon).result
        # print(safe)
        safetyScores = {'lgbtq': 0, 'medical': 0, 'overall': 0, 'physicalHarm': 0, 'politicalFreedom': 0, 'theft': 0, 'women': 0}
        c = 0
        for score in safe['data']:
            for a,b in score['safetyScores'].items():
                safetyScores[a] += b
            c += 1
        if c == 0:
            safetyScores = False
        else:
            for a,b in safetyScores.items():
                safetyScores[a] = round(b/c)
    except (ResponseError,KeyError):
        safetyScores = False
    # print(eat,places)

    return render(request, "main/attractions.html", {
        "place": place,
        "photo": photo,
        "eat": eat,
        "places": places,
        "api": maps_api,
        "dbid": id,
        "shopping": shopping,
        "safetyScores": safetyScores
    })


def plans(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.user.is_authenticated:
        places = Destination.objects.filter(booker=request.user)
        city, country, db = [], [], []
        for place in places:
            city.append(place.city)
            country.append(place.country)
            db.append(place.id)
        # try:
        #     response = amadeus.reference_data.locations.cities.get(
        #         keyword=city).result
        #     # response = {'meta': {'count': 1, 'links': {'self': 'https://test.api.amadeus.com/v1/reference-data/locations/cities?keyword=Hong+Kong&max=1000'}}, 'data': [{'type': 'location', 'subType': 'city', 'name': 'Hong Kong', 'iataCode': 'HKG', 'address': {'countryCode': 'HK', 'stateCode': 'HK-ZZZ'}, 'geoCode': {'latitude': 22.27832, 'longitude': 114.17469}}]}
        #     lat, lon = response['data'][0]['geoCode'].values()
        #     # print(lat, lon)
        # except ResponseError as error:
        #     response = "Couldn't find the city: " + city
        spots = []
        for cit, con, dbid in zip(city, country, db):
            response = gmaps.find_place(f"{cit}, {con}", "textquery", fields=[
                                        "price_level", "geometry/location", "place_id", "rating", "photos"])
            # print(response)
            lat, lon = response['candidates'][0]['geometry']['location'].values(
            )
            photo = response['candidates'][0]['photos'][0]['photo_reference']
            id = response['candidates'][0]['place_id']
            spots.append((dbid, id, cit, con, lat, lon, photo))

        return render(request, "main/plans.html", {
            "spots": spots,
            "api": maps_api
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    places = Destination.objects.all()
    city, country, db = [], [], []
    for i in range(15):
        city.append(places[i].city)
        country.append(places[i].country)
        db.append(places[i].id)
    # try:
    #     response = amadeus.reference_data.locations.cities.get(
    #         keyword=city).result
    #     # response = {'meta': {'count': 1, 'links': {'self': 'https://test.api.amadeus.com/v1/reference-data/locations/cities?keyword=Hong+Kong&max=1000'}}, 'data': [{'type': 'location', 'subType': 'city', 'name': 'Hong Kong', 'iataCode': 'HKG', 'address': {'countryCode': 'HK', 'stateCode': 'HK-ZZZ'}, 'geoCode': {'latitude': 22.27832, 'longitude': 114.17469}}]}
    #     lat, lon = response['data'][0]['geoCode'].values()
    #     # print(lat, lon)
    # except ResponseError as error:
    #     response = "Couldn't find the city: " + city
    spots = []
    for cit, con, dbid in zip(city, country, db):
        response = gmaps.find_place(f"{cit}, {con}", "textquery", fields=[
                                    "price_level", "geometry/location", "place_id", "rating", "photos"])
        # print(response)
        lat, lon = response['candidates'][0]['geometry']['location'].values()
        photo = response['candidates'][0]['photos'][0]['photo_reference']
        id = response['candidates'][0]['place_id']
        spots.append((dbid, id, cit, con, lat, lon, photo))

    return render(request, "main/index.html", {
        "spots": spots,
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
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]

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


# def attractions(request):
#     return render(request, "main/attractions.html")

def intro(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    return render(request, "main/intro.html")
