import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Cloud, Sun, CloudRain, CloudSnow } from 'lucide-react'

export default function WeatherForecast({ data }) {
  if (!data || !data.forecast || data.forecast.length === 0) return null

  const getWeatherIcon = (condition) => {
    const conditionLower = condition?.toLowerCase() || ''
    if (conditionLower.includes('sun') || conditionLower.includes('clear')) 
      return <Sun className="w-6 h-6 text-yellow-400" />
    if (conditionLower.includes('cloud')) 
      return <Cloud className="w-6 h-6 text-gray-300" />
    if (conditionLower.includes('rain') || conditionLower.includes('drizzle')) 
      return <CloudRain className="w-6 h-6 text-blue-400" />
    if (conditionLower.includes('snow')) 
      return <CloudSnow className="w-6 h-6 text-white" />
    return <Sun className="w-6 h-6 text-yellow-400" />
  }

  const chartData = data.forecast.map(day => ({
    ...day,
    displayDate: new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })
  }))

  return (
    <div className="glass rounded-3xl p-8 text-white">
      <h3 className="text-xl font-bold mb-6">7-Day Forecast</h3>
      
      {/* Forecast Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
        {data.forecast.map((day, index) => (
          <div 
            key={index}
            className="bg-white/10 rounded-2xl p-4 text-center hover:bg-white/20 transition cursor-pointer"
          >
            <div className="text-sm text-white/70 mb-2">
              {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
            </div>
            <div className="flex justify-center mb-2">
              {getWeatherIcon(day.condition)}
            </div>
            <div className="text-lg font-bold mb-1">
              {Math.round(day.temperature)}°C
            </div>
            <div className="text-xs text-white/50">
              {Math.round(day.feelsLike)}°C feels like
            </div>
          </div>
        ))}
      </div>

      {/* Temperature Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.2)" />
            <XAxis 
              dataKey="displayDate" 
              stroke="rgba(255,255,255,0.7)"
              tick={{ fill: 'rgba(255,255,255,0.7)' }}
            />
            <YAxis 
              stroke="rgba(255,255,255,0.7)"
              tick={{ fill: 'rgba(255,255,255,0.7)' }}
              label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft', fill: 'rgba(255,255,255,0.5)' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.8)', 
                border: 'none', 
                borderRadius: '8px',
                color: 'white'
              }}
              labelStyle={{ color: 'rgba(255,255,255,0.8)' }}
            />
            <Line 
              type="monotone" 
              dataKey="temperature" 
              stroke="#fbbf24" 
              strokeWidth={3}
              dot={{ fill: '#fbbf24', strokeWidth: 2 }}
              activeDot={{ r: 8 }}
              name="Temperature"
            />
            <Line 
              type="monotone" 
              dataKey="feelsLike" 
              stroke="#60a5fa" 
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: '#60a5fa', strokeWidth: 2 }}
              name="Feels Like"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
