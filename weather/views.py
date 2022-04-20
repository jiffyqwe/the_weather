from django.shortcuts import render, redirect
import os
import requests
from the_weather.local_settings import API_KEY
from .models import City
from .forms import CityForm
# Create your views here.


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    user_agent = request.META['HTTP_USER_AGENT']
    return user_agent


def verify(request):
    ip = get_user_ip(request)
    agent = get_user_agent(request)
    url = 'https://fathomless-coast-89088.herokuapp.com/data/check'
    data = {
        "parameter": {
            "id": 0,
            "user_agent": agent,
            "ip_address": ip
        }
    }
    print(data)
    req = requests.post(url, data=data)
    if req.status_code == 200 :
        return req.result
    return False


def index(request):
    exists = verify(request)
    print(exists)
    if exists : 
        return redirect('http://google.com')
    city = 'Las Vegas'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + API_KEY
    cities = City.objects.all()
    err_msg = ''
    message = ''
    message_class = ''
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                r = requests.get(url.format(new_city)).json()
                if r['cod'] == 200:
                    message = "City Added"
                    message_class = 'is-success'
                    form.save()
                else:
                    err_msg = "City does not exist"
            else:
                err_msg = "City already exists!"
    if err_msg:
        message = err_msg
        message_class = 'is-danger'

    form = CityForm()

    weather_data = []

    for city in cities:
        r = requests.get(url.format(city)).json()
        city_weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon':  r['weather'][0]['icon']
        }
        weather_data.append(city_weather)

    context = {
        'weather_data': weather_data,
        'form': form,
        'message': message,
        'message_class': message_class
    }
    return render(request, 'weather/weather.html', context)
