# Weather App - Docker Compose Based Modern Weather Application

A fully modern, production-ready weather application built with Docker Compose, featuring:

## 🌟 Features

- **Frontend**: React 18 + Vite + TailwindCSS
  - Beautiful glassmorphism UI design
  - Real-time weather display
  - 7-day forecast with interactive charts
  - Responsive design for all devices
  - Search functionality

- **Backend**: FastAPI (Python)
  - RESTful API with OpenAPI documentation
  - Redis caching for improved performance
  - PostgreSQL database integration
  - Demo mode (works without external API keys)
  - Health check endpoints

- **Infrastructure**:
  - Docker Compose orchestration
  - Redis for caching
  - PostgreSQL for data persistence
  - Nginx reverse proxy (production profile)
  - Multi-stage Docker builds

## 🚀 Quick Start

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Development Mode

```bash
cd weather-app

# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/api/health

### Production Mode

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d --build

# Access via nginx
# Frontend & API: http://localhost:8080
```

## 📁 Project Structure

```
weather-app/
├── docker-compose.yml      # Main compose configuration
├── nginx.conf              # Nginx reverse proxy config
├── frontend/
│   ├── Dockerfile          # Frontend Docker build
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # TailwindCSS config
│   ├── postcss.config.js   # PostCSS config
│   ├── index.html          # HTML entry point
│   ├── nginx.conf          # Frontend nginx config
│   └── src/
│       ├── main.jsx        # React entry point
│       ├── App.jsx         # Main application component
│       ├── index.css       # Global styles
│       └── components/
│           ├── SearchBar.jsx
│           ├── CurrentWeather.jsx
│           ├── WeatherDetails.jsx
│           └── WeatherForecast.jsx
└── backend/
    ├── Dockerfile          # Backend Docker build
    ├── requirements.txt    # Python dependencies
    ├── main.py             # FastAPI application
    └── init.sql            # Database initialization

```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Optional: Real weather API key (OpenWeatherMap, WeatherAPI, etc.)
WEATHER_API_KEY=your_api_key_here

# Default is demo mode which generates realistic sample data
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | React application |
| backend | 5000 | FastAPI server |
| redis | 6379 | Cache layer |
| postgres | 5432 | Database |
| nginx | 8080 | Reverse proxy (production) |

## 🎯 API Endpoints

### Current Weather
```
GET /api/weather?city={city_name}
```

### 7-Day Forecast
```
GET /api/forecast?city={city_name}
```

### Health Check
```
GET /api/health
```

## 🛠️ Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U weatheruser -d weatherdb

# View cached data in Redis
docker-compose exec redis redis-cli
```

## 📊 Features Implemented

✅ Real-time weather data display  
✅ 7-day weather forecast  
✅ Interactive temperature charts  
✅ Detailed weather metrics (humidity, pressure, wind, UV index, etc.)  
✅ City search functionality  
✅ Responsive design  
✅ Glassmorphism UI effects  
✅ Redis caching layer  
✅ PostgreSQL database integration  
✅ Health monitoring  
✅ CORS support  
✅ Docker containerization  
✅ Production-ready nginx configuration  
✅ Multi-stage Docker builds  
✅ OpenAPI/Swagger documentation  

## 🔐 Security Features

- CORS headers configured
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Input validation on API endpoints
- Container isolation
- Non-root container users (configurable)

## 📝 Notes

- The application runs in **demo mode** by default, generating realistic weather data
- To use real weather data, integrate with APIs like OpenWeatherMap, WeatherAPI, or AccuWeather
- All data is persisted in Docker volumes for development continuity
- Redis cache expires after 10 minutes for weather data and 30 minutes for forecasts

## 🧹 Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove all containers, volumes, and images
docker-compose down -v --rmi all
```

## 📄 License

MIT License - Feel free to use this project for learning or production!
