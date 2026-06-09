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

@app.get("/api/weather", response_model=WeatherData)
async def get_weather(city: str = Query(..., description="City name")):
    """Get current weather data for a city"""
    
    # Check Redis cache first
    cache_key = f"weather:{city.lower()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Generate demo data (in production, you would call a real weather API)
    try:
        weather_data = generate_demo_weather(city)
        
        # Cache for 10 minutes
        redis_client.setex(cache_key, 600, json.dumps(weather_data))
        
        # Store in database asynchronously (simplified for demo)
        db = SessionLocal()
        try:
            # Here you would save to database
            pass
        finally:
            db.close()
        
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@app.get("/api/forecast", response_model=ForecastData)
async def get_forecast(city: str = Query(..., description="City name")):
    """Get 7-day weather forecast for a city"""
    
    # Check Redis cache first
    cache_key = f"forecast:{city.lower()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Generate demo forecast data
    try:
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
