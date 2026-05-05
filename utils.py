import requests

def get_weather_advice():
    try: 
        url = "https://api.open-meteo.com/v1/forecast?latitude=56.95&longitude=24.10&current_weather=true"
        response = requests.get(url, timeout=10)
        data = response.json()
        temp = data['current_weather']['temperature']
        
        if temp > 7:
                advice = f"It's {temp}°C. Ticks are active - use tick/flea prevention!"
        elif temp < 0:
            advice = f"It's {temp}°C. Careful of road salt causing irritation on pet paws!"
        else:
            advice = f"It's {temp}°C. Standard health checks recommended."
        return advice

    except Exception:
        return "Weather service unavailable. Ensure pets are up to date on vaccinations."