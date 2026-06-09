import { Wind, Droplets, Eye, Gauge, Sunrise, Sunset, ThermometerSun } from 'lucide-react'

export default function WeatherDetails({ data }) {
  if (!data) return null

  const details = [
    {
      icon: <Wind className="w-6 h-6" />,
      label: 'Wind Speed',
      value: `${data.windSpeed} km/h`,
      subtext: `Direction: ${data.windDirection}`
    },
    {
      icon: <Droplets className="w-6 h-6" />,
      label: 'Humidity',
      value: `${data.humidity}%`,
      subtext: `Dew Point: ${data.dewPoint}°C`
    },
    {
      icon: <Eye className="w-6 h-6" />,
      label: 'Visibility',
      value: `${data.visibility} km`,
      subtext: data.visibility > 10 ? 'Excellent' : 'Moderate'
    },
    {
      icon: <Gauge className="w-6 h-6" />,
      label: 'Pressure',
      value: `${data.pressure} hPa`,
      subtext: data.pressure > 1013 ? 'High' : 'Low'
    },
    {
      icon: <ThermometerSun className="w-6 h-6" />,
      label: 'UV Index',
      value: data.uvIndex,
      subtext: getUVDescription(data.uvIndex)
    },
    {
      icon: <Sunrise className="w-6 h-6" />,
      label: 'Sunrise',
      value: data.sunrise,
      subtext: ''
    },
    {
      icon: <Sunset className="w-6 h-6" />,
      label: 'Sunset',
      value: data.sunset,
      subtext: ''
    }
  ]

  return (
    <div className="glass rounded-3xl p-8 text-white h-full">
      <h3 className="text-xl font-bold mb-6">Weather Details</h3>
      <div className="grid grid-cols-2 gap-4">
        {details.map((detail, index) => (
          <div 
            key={index}
            className="bg-white/10 rounded-2xl p-4 hover:bg-white/20 transition cursor-pointer"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="text-white/70">{detail.icon}</div>
              <span className="text-sm text-white/70">{detail.label}</span>
            </div>
            <div className="text-2xl font-bold mb-1">{detail.value}</div>
            {detail.subtext && (
              <div className="text-xs text-white/50">{detail.subtext}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function getUVDescription(uvIndex) {
  if (uvIndex <= 2) return 'Low'
  if (uvIndex <= 5) return 'Moderate'
  if (uvIndex <= 7) return 'High'
  if (uvIndex <= 10) return 'Very High'
  return 'Extreme'
}
