import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'

interface DisasterEvent {
  id: string
  type: string
  title: string
  magnitude: number | null
  category: string | null
  latitude: number
  longitude: number
  event_time: string
  source: string
}

function App() {
  const [events, setEvents] = useState<DisasterEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // fetch existing events on load
    async function loadEvents() {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .order('event_time', { ascending: false })
        .limit(100)

      if (error) {
        console.error('Error loading events:', error)
      } else {
        setEvents(data || [])
      }
      setLoading(false)
    }

    loadEvents()

    // subscribe to new events in real time
    const channel = supabase
      .channel('events-channel')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'events' },
        (payload) => {
          console.log('New event received:', payload.new)
          setEvents(prev => [payload.new as DisasterEvent, ...prev])
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <h1 className="text-2xl font-bold mb-2">Disaster Alert System</h1>
      <p className="text-gray-400 mb-6">Live global disaster monitoring</p>

      {loading && <p className="text-gray-400">Loading events...</p>}

      <div className="grid gap-3">
        {events.map(event => (
          <div key={event.id} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-white">{event.title}</span>
              {event.magnitude && (
                <span className="text-xs bg-red-900 text-red-300 px-2 py-1 rounded">
                  M{event.magnitude}
                </span>
              )}
              {event.category && (
                <span className="text-xs bg-orange-900 text-orange-300 px-2 py-1 rounded">
                  {event.category}
                </span>
              )}
            </div>
            <div className="text-xs text-gray-500">
              {event.source} · {event.latitude.toFixed(2)}, {event.longitude.toFixed(2)} · {new Date(event.event_time).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App