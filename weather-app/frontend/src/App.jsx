import { useState, useEffect } from 'react'
import axios from 'axios'
import CurrentWeather from './components/CurrentWeather'
import WeatherForecast from './components/WeatherForecast'
import WeatherDetails from './components/WeatherDetails'
import SearchBar from './components/SearchBar'
import { Sun, Cloud, CloudRain, CloudSnow, Wind, Droplets, Thermometer, Eye, Gauge, Sunrise, Sunset } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

function App() {
  const [weatherData, setWeatherData] = useState(null)
  const [forecastData, setForecastData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState({ city: 'London', country: 'UK' })

  const fetchWeatherData = async (city) => {
    try {
      setLoading(true)
      setError(null)
      
      const [weatherRes, forecastRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/weather?city=${encodeURIComponent(city)}`),
        axios.get(`${API_BASE_URL}/forecast?city=${encodeURIComponent(city)}`)
      ])
      
      setWeatherData(weatherRes.data)
      setForecastData(forecastRes.data)
      setLocation({ city: weatherRes.data.city, country: weatherRes.data.country })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch weather data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWeatherData(location.city)
  }, [])

  const handleSearch = (query) => {
    if (query.trim()) {
      fetchWeatherData(query)
    }
  }

  const getWeatherIcon = (condition) => {
    const conditionLower = condition?.toLowerCase() || ''
    if (conditionLower.includes('sun') || conditionLower.includes('clear')) return <Sun className="w-16 h-16 text-yellow-400" />
    if (conditionLower.includes('cloud')) return <Cloud className="w-16 h-16 text-gray-300" />
    if (conditionLower.includes('rain') || conditionLower.includes('drizzle')) return <CloudRain className="w-16 h-16 text-blue-400" />
    if (conditionLower.includes('snow')) return <CloudSnow className="w-16 h-16 text-white" />
    return <Sun className="w-16 h-16 text-yellow-400" />
  }

  if (loading && !weatherData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-2xl animate-pulse">Loading weather data...</div>
      </div>
    )
  }

  if (error && !weatherData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass rounded-2xl p-8 text-white text-center">
          <div className="text-2xl mb-4">⚠️</div>
          <div className="text-xl mb-4">{error}</div>
          <button 
            onClick={() => fetchWeatherData(location.city)}
            className="bg-white text-primary-600 px-6 py-2 rounded-lg hover:bg-opacity-90 transition"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
            Weather App
          </h1>
          <p className="text-white text-opacity-80 text-lg">
            Real-time weather forecasts for any location
          </p>
        </header>

        {/* Search Bar */}
        <div className="mb-8 animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <SearchBar onSearch={handleSearch} loading={loading} />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Current Weather */}
          <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <CurrentWeather 
              data={weatherData} 
              icon={getWeatherIcon(weatherData?.condition)}
              location={location}
            />
          </div>

          {/* Weather Details */}
          <div className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <WeatherDetails data={weatherData} />
          </div>
        </div>

        {/* Forecast */}
        <div className="mt-6 animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <WeatherForecast data={forecastData} />
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-white text-opacity-60 text-sm">
          <p>Data updated: {weatherData?.lastUpdated || 'N/A'}</p>
          <p className="mt-1">Powered by modern weather APIs</p>
        </footer>
      </div>
    </div>
  )
}

export default App
