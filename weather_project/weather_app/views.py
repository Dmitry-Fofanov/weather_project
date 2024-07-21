import logging
from datetime import datetime

import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)


def weather_view(request):
    if request.method == 'POST':
        city = request.POST['city']
        try:
            response = requests.get(
                'https://geocoding-api.open-meteo.com/v1/search',
                params={
                    'name': city,
                    'count': 1,
                    'language': 'ru',
                    'format': 'json',
                },
                timeout=5,
            )
            city_data = response.json()['results'][0]
            response = requests.get(
                'https://api.open-meteo.com/v1/forecast',
                params={
                    'latitude': city_data['latitude'],
                    'longitude': city_data['longitude'],
                    'current': 'temperature_2m',
                    'hourly': 'temperature_2m',
                },
                timeout=5,
            )
            data = response.json()
        except Exception as e:
            logger.error(e)
            return render(request, 'weather_app/error.html')

        times = [
            datetime.fromisoformat(timestamp)
            for timestamp in data['hourly']['time']
        ]
        times = [
            timestamp.strftime('%H:%M') if timestamp.hour != 0
            else timestamp.strftime('%d.%m %H:%M')
            for timestamp in times
        ]
        weather_data = {
            'city': city_data['name'],
            'country': city_data['country'],
            'current_temperature': data['current']['temperature_2m'],
            'temperatures': data['hourly']['temperature_2m'],
            'times': times,
        }
        return render(
            request,
            'weather_app/weather.html',
            {'data': weather_data}
        )

    return render(request, 'weather_app/search.html')
