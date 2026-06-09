from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import redis
import json
import os
import httpx
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://weatheruser:weatherpass@localhost:5432/weatherdb")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "demo")
WEATHER_API_PROVIDER = os.getenv("WEATHER_API_PROVIDER", "openweathermap")
OPENWEATHERMAP_URL = os.getenv("OPENWEATHERMAP_URL", "https://api.openweathermap.org/data/2.5")
WEATHERAPI_URL = os.getenv("WEATHERAPI_URL", "https://api.weatherapi.com/v1")

# Initialize FastAPI app
app = FastAPI(
    title="Weather API",
    description="Modern Weather API with caching and database support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Models
class WeatherData(BaseModel):
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: str
    condition: str
    visibility: float
    dew_point: float
    uv_index: float
    sunrise: str
    sunset: str
    date: str
    last_updated: str

class ForecastDay(BaseModel):
    date: str
    temperature: float
    feels_like: float
    humidity: int
    condition: str
    wind_speed: float

class ForecastData(BaseModel):
    city: str
    country: str
    forecast: List[ForecastDay]

# Demo weather data generator (for development/testing without API key)
def generate_demo_weather(city: str) -> Dict[str, Any]:
    """Generate realistic demo weather data"""
    conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Thunderstorm', 'Snow']
    wind_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    
    # Seed based on city name for consistent results
    seed_value = sum(ord(c) for c in city.lower())
    random.seed(seed_value)
    
    base_temp = random.uniform(5, 30)
    
    return {
        "city": city.title(),
        "country": random.choice(['UK', 'USA', 'Canada', 'Australia', 'Germany', 'France', 'Japan']),
        "temperature": round(base_temp, 1),
        "feels_like": round(base_temp + random.uniform(-3, 3), 1),
        "humidity": random.randint(40, 90),
        "pressure": random.randint(995, 1025),
        "wind_speed": round(random.uniform(5, 35), 1),
        "wind_direction": random.choice(wind_directions),
        "condition": random.choice(conditions),
        "visibility": round(random.uniform(5, 20), 1),
        "dew_point": round(base_temp - random.uniform(5, 15), 1),
        "uv_index": round(random.uniform(1, 10), 1),
        "sunrise": f"{random.randint(5, 7):02d}:{random.randint(0, 59):02d}",
        "sunset": f"{random.randint(17, 20):02d}:{random.randint(0, 59):02d}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_demo_forecast(city: str) -> List[Dict[str, Any]]:
    """Generate 7-day forecast demo data"""
    conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Thunderstorm', 'Snow']
    forecast = []
    
    seed_value = sum(ord(c) for c in city.lower())
    random.seed(seed_value + 100)
    
    base_temp = random.uniform(5, 30)
    
    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        temp_variation = random.uniform(-5, 5)
        
        forecast.append({
            "date": date,
            "temperature": round(base_temp + temp_variation, 1),
            "feels_like": round(base_temp + temp_variation + random.uniform(-3, 3), 1),
            "humidity": random.randint(40, 90),
            "condition": random.choice(conditions),
            "wind_speed": round(random.uniform(5, 35), 1)
        })
    
    return forecast

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Weather API",
        "version": "1.0.0",
        "endpoints": {
            "weather": "/api/weather?city={city_name}",
            "forecast": "/api/forecast?city={city_name}"
        }
    }

async def fetch_openweathermap_data(city: str) -> Dict[str, Any]:
    """Fetch weather data from OpenWeatherMap API"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Current weather
        weather_url = f"{OPENWEATHERMAP_URL}/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        response = await client.get(weather_url, params=params)
        response.raise_for_status()
        weather = response.json()
        
        # Forecast
        forecast_url = f"{OPENWEATHERMAP_URL}/forecast"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        response = await client.get(forecast_url, params=params)
        response.raise_for_status()
        forecast = response.json()
        
        # Parse current weather
        current = weather
        temp = current["main"]["temp"]
        
        # Map weather condition
        condition_map = {
            "Clear": "Sunny",
            "Clouds": "Partly Cloudy",
            "Rain": "Light Rain",
            "Drizzle": "Light Rain",
            "Thunderstorm": "Thunderstorm",
            "Snow": "Snow",
            "Mist": "Foggy",
            "Haze": "Foggy"
        }
        condition = condition_map.get(current["weather"][0]["main"], "Partly Cloudy")
        
        # Wind direction conversion
        wind_deg = current["wind"].get("deg", 0)
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        wind_dir = directions[int((wind_deg + 22.5) / 45) % 8]
        
        return {
            "city": current["name"],
            "country": current["sys"].get("country", ""),
            "temperature": round(temp, 1),
            "feels_like": round(current["main"]["feels_like"], 1),
            "humidity": current["main"]["humidity"],
            "pressure": current["main"]["pressure"],
            "wind_speed": round(current["wind"]["speed"] * 3.6, 1),  # m/s to km/h
            "wind_direction": wind_dir,
            "condition": condition,
            "visibility": round(current["visibility"] / 1000, 1),
            "dew_point": round(temp - ((100 - current["main"]["humidity"]) / 5), 1),
            "uv_index": round(random.uniform(1, 10), 1),  # UV not in free API
            "sunrise": datetime.fromtimestamp(current["sys"]["sunrise"]).strftime("%H:%M"),
            "sunset": datetime.fromtimestamp(current["sys"]["sunset"]).strftime("%H:%M"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

async def fetch_weatherapi_data(city: str) -> Dict[str, Any]:
    """Fetch weather data from WeatherAPI.com"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"{WEATHERAPI_URL}/current.json"
        params = {"key": WEATHER_API_KEY, "q": city}
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        current = data["current"]
        location = data["location"]
        
        return {
            "city": location["name"],
            "country": location["country"],
            "temperature": round(current["temp_c"], 1),
            "feels_like": round(current["feelslike_c"], 1),
            "humidity": current["humidity"],
            "pressure": current["pressure_mb"],
            "wind_speed": round(current["wind_kph"], 1),
            "wind_direction": current["wind_dir"],
            "condition": current["condition"]["text"],
            "visibility": round(current["vis_km"], 1),
            "dew_point": round(current["dewpoint_c"], 1),
            "uv_index": round(current["uv"], 1),
            "sunrise": datetime.strptime(data["astronomy"]["astro"]["sunrise"], "%I:%M %p").strftime("%H:%M"),
            "sunset": datetime.strptime(data["astronomy"]["astro"]["sunset"], "%I:%M %p").strftime("%H:%M"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

@app.get("/api/weather", response_model=WeatherData)
async def get_weather(city: str = Query(..., description="City name")):
    """Get current weather data for a city"""
    
    # Check Redis cache first
    cache_key = f"weather:{city.lower()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        # Use real API if key is provided and not 'demo'
        if WEATHER_API_KEY and WEATHER_API_KEY != "demo" and WEATHER_API_KEY != "your_api_key_here":
            try:
                if WEATHER_API_PROVIDER == "weatherapi":
                    weather_data = await fetch_weatherapi_data(city)
                else:  # openweathermap (default)
                    weather_data = await fetch_openweathermap_data(city)
                
                # Cache for 10 minutes
                redis_client.setex(cache_key, 600, json.dumps(weather_data))
                
                # Store in database
                db = SessionLocal()
                try:
                    # Save to database (implementation depends on your schema)
                    pass
                finally:
                    db.close()
                
                return weather_data
            except httpx.HTTPError as e:
                # Fall back to demo data if API fails
                print(f"API request failed: {e}, using demo data")
        
        # Generate demo data as fallback
        weather_data = generate_demo_weather(city)
        
        # Cache for 10 minutes
        redis_client.setex(cache_key, 600, json.dumps(weather_data))
        
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

async def fetch_openweathermap_forecast(city: str) -> List[Dict[str, Any]]:
    """Fetch 7-day forecast from OpenWeatherMap API"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        forecast_url = f"{OPENWEATHERMAP_URL}/forecast"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        response = await client.get(forecast_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Group by day and get one forecast per day (noon)
        daily_forecasts = {}
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in daily_forecasts and "12:00:00" in item["dt_txt"]:
                condition_map = {
                    "Clear": "Sunny",
                    "Clouds": "Partly Cloudy",
                    "Rain": "Light Rain",
                    "Drizzle": "Light Rain",
                    "Thunderstorm": "Thunderstorm",
                    "Snow": "Snow"
                }
                daily_forecasts[date] = {
                    "date": date,
                    "temperature": round(item["main"]["temp"], 1),
                    "feels_like": round(item["main"]["feels_like"], 1),
                    "humidity": item["main"]["humidity"],
                    "condition": condition_map.get(item["weather"][0]["main"], "Partly Cloudy"),
                    "wind_speed": round(item["wind"]["speed"] * 3.6, 1)
                }
        
        return list(daily_forecasts.values())[:7]

async def fetch_weatherapi_forecast(city: str) -> List[Dict[str, Any]]:
    """Fetch 7-day forecast from WeatherAPI.com"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"{WEATHERAPI_URL}/forecast.json"
        params = {"key": WEATHER_API_KEY, "q": city, "days": 7}
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        forecast = []
        for day in data["forecast"]["forecastday"]:
            forecast.append({
                "date": day["date"],
                "temperature": round(day["day"]["avgtemp_c"], 1),
                "feels_like": round(day["day"]["avgtemp_c"], 1),
                "humidity": day["day"]["avghumidity"],
                "condition": day["day"]["condition"]["text"],
                "wind_speed": round(day["day"]["maxwind_kph"], 1)
            })
        
        return forecast

@app.get("/api/forecast", response_model=ForecastData)
async def get_forecast(city: str = Query(..., description="City name")):
    """Get 7-day weather forecast for a city"""
    
    # Check Redis cache first
    cache_key = f"forecast:{city.lower()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        # Use real API if key is provided and not 'demo'
        if WEATHER_API_KEY and WEATHER_API_KEY != "demo" and WEATHER_API_KEY != "your_api_key_here":
            try:
                if WEATHER_API_PROVIDER == "weatherapi":
                    forecast_list = await fetch_weatherapi_forecast(city)
                    country = ""
                else:  # openweathermap (default)
                    forecast_list = await fetch_openweathermap_forecast(city)
                    country = ""
                
                forecast_data = {
                    "city": city.title(),
                    "country": country,
                    "forecast": forecast_list
                }
                
                # Cache for 30 minutes
                redis_client.setex(cache_key, 1800, json.dumps(forecast_data))
                
                return forecast_data
            except httpx.HTTPError as e:
                # Fall back to demo data if API fails
                print(f"Forecast API request failed: {e}, using demo data")
        
        # Generate demo forecast data as fallback
        forecast_data = {
            "city": city.title(),
            "country": "Demo",
            "forecast": generate_demo_forecast(city)
        }
        
        # Cache for 30 minutes
        redis_client.setex(cache_key, 1800, json.dumps(forecast_data))
        
        return forecast_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast data: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "up",
            "redis": "unknown",
            "database": "unknown"
        }
    }
    
    # Check Redis
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "up"
    except:
        health_status["services"]["redis"] = "down"
    
    # Check Database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["services"]["database"] = "up"
    except:
        health_status["services"]["database"] = "down"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
