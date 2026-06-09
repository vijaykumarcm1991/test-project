import { MapPin, Calendar } from 'lucide-react'

export default function CurrentWeather({ data, icon, location }) {
  if (!data) return null

  return (
    <div className="glass rounded-3xl p-8 text-white h-full">
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-5 h-5" />
            <h2 className="text-2xl font-bold">
              {data.city}, {data.country}
            </h2>
          </div>
          <div className="flex items-center gap-2 text-white/70">
            <Calendar className="w-4 h-4" />
            <span className="text-sm">{data.date}</span>
          </div>
        </div>
        <div className="animate-fade-in">
          {icon}
        </div>
      </div>

      <div className="mb-6">
        <div className="text-6xl md:text-7xl font-bold mb-2">
          {Math.round(data.temperature)}°C
        </div>
        <div className="text-xl text-white/80 capitalize">{data.condition}</div>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/20">
        <div>
          <div className="text-white/60 text-sm mb-1">Feels Like</div>
          <div className="text-xl font-semibold">{Math.round(data.feelsLike)}°C</div>
        </div>
        <div>
          <div className="text-white/60 text-sm mb-1">Humidity</div>
          <div className="text-xl font-semibold">{data.humidity}%</div>
        </div>
      </div>
    </div>
  )
}
