import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import HelloSerializer
from django.shortcuts import render
from dotenv import load_dotenv
import os

load_dotenv()  # Ensure to load environment variables if not already loaded

IPREGISTRY_API_KEY = os.getenv('IPREGISTRY_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

def name_form(request):
    return render(request, 'name_data/form.html')

def get_location(ip):
    try:
        url = f'https://api.ipregistry.co/{ip}?key={IPREGISTRY_API_KEY}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['location']['city'], data['location']['country']['name']
    except requests.RequestException as e:
        print(f"Error retrieving location: {e}")
        return None, None

def get_temperature(city):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['main']['temp']
    except requests.RequestException as e:
        print(f"Error retrieving temperature: {e}, Response: {response.text}")
        return None

@api_view(['GET'])
def hello(request):
    visitor_name = request.GET.get('visitor_name', 'Visitor')

    # Get the client's IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    client_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else x_real_ip
    print(client_ip)

    if not client_ip:
        client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

    # Handle local testing
    if client_ip == '127.0.0.1':
        client_ip = '8.8.8.8'  # Example IP address for testing

    city, country = get_location(client_ip)
    if city and country:
        temperature = get_temperature(city)
        if temperature is not None:
            greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"
        else:
            greeting = f"Hello, {visitor_name}!, we could not retrieve the temperature for {city}"
    else:
        greeting = f"Hello, {visitor_name}!, we could not determine your location."

    data = {
        "client_ip": client_ip,
        "location": f"{city}" if city else "Unknown location",
        "greeting": greeting
    }
    serializer = HelloSerializer(data)
    return Response(serializer.data)
