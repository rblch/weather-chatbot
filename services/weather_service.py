# Import necessary modules
import requests
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from config import openweathermap_api_key

class WeatherService:
    def __init__(self, api_key=openweathermap_api_key, cache_validity_period=timedelta(hours=1)):
        """
        Initialize the WeatherService with an API key and cache validity period.
        """
        self.api_key = api_key
        self.cache_validity_period = cache_validity_period
        self.weather_cache = {}
        self.locations = set()
        self.weather_forecasts = {}

    def clear_data(self):
        """
        Clear the cached weather data and locations.
        """
        self.weather_cache = {}
        self.locations = set()
        self.weather_forecasts = {}

    def get_coordinates(self, city_name):
        """
        Get the geographical coordinates (latitude and longitude) for a given city name.
        """
        geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': city_name,
            'appid': self.api_key,
            'limit': 1
        }
        
        response = requests.get(geocode_url, params=params)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    return data[0]['lat'], data[0]['lon']
                else:
                    return None, None
            except ValueError:
                print("Error: Unable to parse JSON response from geocode API")
                return None, None
        else:
            print(f"Error: Received status code {response.status_code}")
            return None, None

    def fetch_weather(self, cities):
        """
        Fetch weather data for a list of cities, using cache if valid, otherwise fetching from API.
        """
        city_forecasts = {}

        for city_name in cities:
            # Check cache first
            if city_name in self.weather_cache:
                cached_data, timestamp = self.weather_cache[city_name]
                if datetime.now() - timestamp < self.cache_validity_period:
                    city_forecasts[city_name] = cached_data
                    continue

            # If not in cache or cache is invalid, fetch from API
            lat, lon = self.get_coordinates(city_name)
            if lat is None or lon is None:
                city_forecasts[city_name] = {"error": "Invalid city name or coordinates could not be retrieved"}
                continue

            base_url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                try:
                    data = response.json()
                    city_forecasts[city_name] = data
                    self.weather_cache[city_name] = (data, datetime.now())
                except ValueError:
                    print("Error: Unable to parse JSON response from API")
                    city_forecasts[city_name] = {"error": "Invalid JSON response from API"}
            else:
                print(f"Error: Received status code {response.status_code} from weather API")
                city_forecasts[city_name] = {"error": response.status_code, "message": response.text}

        return city_forecasts
        

    def parse_weather_data(self, data):
        """
        Parse weather data to extract and organize weather information by date and time period.
        """
        # Define time blocks for different parts of the day
        time_blocks = {
            "morning": (6, 12),
            "afternoon": (12, 18),
            "night": (18, 24)
        }

        # Initialize a defaultdict to store daily weather data
        daily_data = defaultdict(lambda: {
            "temps": [],
            "feels_like": [],
            "pressure": [],
            "humidity": [],
            "cloudiness": [],
            "wind_speed": [],
            "wind_gust": [],
            "wind_deg": [],
            "visibility": [],
            "weather_descriptions": [],
            "pop_day": [],
            "pop_night": [],
            "rain": {"morning": 0.0, "afternoon": 0.0, "night": 0.0},
            "snow": {"morning": 0.0, "afternoon": 0.0, "night": 0.0}
        })

        # Iterate through the weather data entries
        for entry in data.get("list", []):
            dt = datetime.strptime(entry["dt_txt"], '%Y-%m-%d %H:%M:%S')
            date_str = dt.strftime('%Y-%m-%d')
            hour = dt.hour

            # Determine the period of the day based on the hour
            period = "morning" if time_blocks["morning"][0] <= hour < time_blocks["morning"][1] else \
                    "afternoon" if time_blocks["afternoon"][0] <= hour < time_blocks["afternoon"][1] else \
                    "night"

            # Append weather data to the corresponding lists
            daily_data[date_str]["temps"].append(entry["main"]["temp"])
            daily_data[date_str]["feels_like"].append(entry["main"]["feels_like"])
            daily_data[date_str]["pressure"].append(entry["main"]["pressure"])
            daily_data[date_str]["humidity"].append(entry["main"]["humidity"])
            daily_data[date_str]["cloudiness"].append(entry["clouds"]["all"])
            daily_data[date_str]["wind_speed"].append(entry["wind"]["speed"])
            daily_data[date_str]["wind_gust"].append(entry["wind"].get("gust", 0))
            daily_data[date_str]["wind_deg"].append(entry["wind"]["deg"])
            daily_data[date_str]["visibility"].append(entry["visibility"])
            daily_data[date_str]["weather_descriptions"].append(entry["weather"][0]["description"])

            # Append probability of precipitation data
            if entry["sys"]["pod"] == 'd':
                daily_data[date_str]["pop_day"].append(entry["pop"] * 100)
            else:
                daily_data[date_str]["pop_night"].append(entry["pop"] * 100)

            # Add rain and snow data
            daily_data[date_str]["rain"][period] += entry.get("rain", {}).get("3h", 0)
            daily_data[date_str]["snow"][period] += entry.get("snow", {}).get("3h", 0)

        return daily_data

    def summarize_daily_forecast(self, daily_data):
        """
        Summarize the daily weather forecast data into a llm-friendly format.
        """
        city_daily_forecasts = {}
        today = datetime.now().date()

        # Iterate through the daily data to create a summary
        for date_str, values in daily_data.items():
            forecast_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            day_name = forecast_date.strftime('%A')
            delta_days = (forecast_date - today).days

            # Determine the relative date description
            if delta_days == 0:
                relative_date = "today"
            elif delta_days == 1:
                relative_date = "tomorrow"
            elif delta_days == 2:
                relative_date = "in two days"
            elif delta_days == 3:
                relative_date = "in three days"
            else:
                relative_date = ""

            # Calculate average and most common values
            pop_day_avg = sum(values['pop_day']) / len(values['pop_day']) if values['pop_day'] else 0.0
            pop_night_avg = sum(values['pop_night']) / len(values['pop_night']) if values['pop_night'] else 0.0

            city_daily_forecasts[date_str] = {
                "Day of the week": day_name,
                "Relative Date": relative_date,
                "Weather Description": Counter(values["weather_descriptions"]).most_common(1)[0][0],
                "Minimum Temperature": f"{round(min(values['temps']))} °C",
                "Maximum Temperature": f"{round(max(values['temps']))} °C",
                "Feels Like Temperature": f"{round(sum(values['feels_like'])/len(values['feels_like']))} °C",
                "Pressure": f"{sum(values['pressure'])/len(values['pressure']):.2f} hPa",
                "Humidity": f"{round(sum(values['humidity']) / len(values['humidity']))} %",
                "Cloudiness": f"{round(sum(values['cloudiness']) / len(values['cloudiness']))} %",
                "Wind Speed": f"{sum(values['wind_speed'])/len(values['wind_speed']):.2f} m/s",
                "Wind Gust": f"{max(values['wind_gust']):.2f} m/s",
                "Wind Direction": f"{round(sum(values['wind_deg'])/len(values['wind_deg']))} °",
                "Visibility": f"{sum(values['visibility'])/len(values['visibility']):.2f} m",
                "Probability of Precipitation (Day)": f"{round(pop_day_avg)} %",
                "Probability of Precipitation (Night)": f"{round(pop_night_avg)} %",
                "Precipitation": {
                    "Morning": {
                        "Total Rain": f"{values['rain']['morning']:.2f} mm",
                        "Total Snow": f"{values['snow']['morning']:.2f} mm"
                    },
                    "Afternoon": {
                        "Total Rain": f"{values['rain']['afternoon']:.2f} mm",
                        "Total Snow": f"{values['snow']['afternoon']:.2f} mm"
                    },
                    "Night": {
                        "Total Rain": f"{values['rain']['night']:.2f} mm",
                        "Total Snow": f"{values['snow']['night']:.2f} mm"
                    }
                }
            }

        return city_daily_forecasts

    def get_weather_forecasts(self, cities):
        if isinstance(cities, str):
            cities = [cities]

        new_cities = [city for city in cities if city not in self.locations]
        self.locations.update(new_cities)

        if new_cities:
            new_forecasts = self.fetch_weather(new_cities)
            for city, data in new_forecasts.items():
                if "error" in data:
                    self.weather_forecasts[city] = {"error": data["error"]}
                else:
                    daily_data = self.parse_weather_data(data)
                    city_daily_forecasts = self.summarize_daily_forecast(daily_data)
                    sunrise_time = datetime.fromtimestamp(data["city"]["sunrise"]).strftime('%Y-%m-%d %H:%M')
                    sunset_time = datetime.fromtimestamp(data["city"]["sunset"]).strftime('%Y-%m-%d %H:%M')
                    self.weather_forecasts[city] = {
                        "Sunrise": sunrise_time,
                        "Sunset": sunset_time,
                        "Daily Forecasts": city_daily_forecasts
                    }
        

        return self.weather_forecasts


    def get_accumulated_data(self):
        return list(self.locations), self.weather_forecasts