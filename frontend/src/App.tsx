import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'
import DisasterMap from './components/DisasterMap'
import NeedsPanel from './components/NeedsPanel'

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
  const [sidebarTab, setSidebarTab] = useState<'disasters' | 'community'>('disasters')
  const [events, setEvents] = useState<DisasterEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'earthquake' | 'natural_event'>('all')

  useEffect(() => {
    async function loadEvents() {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .order('event_time', { ascending: false })
        .limit(200)

      if (!error) setEvents(data || [])
      setLoading(false)
    }

    loadEvents()

    const channel = supabase
      .channel('events-channel')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'events' },
        (payload) => {
          setEvents(prev => [payload.new as DisasterEvent, ...prev])
        }
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [])

  const filtered = filter === 'all'
    ? events
    : events.filter(e => e.type === filter)

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-950 text-white overflow-hidden">

      {/* header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-800 shrink-0">
        <div>
          <h1 className="text-lg font-bold">Disaster Alert System</h1>
          <p className="text-xs text-gray-500">Live global monitoring · {events.length} events</p>
        </div>
        <div className="flex gap-2">
          {(['all', 'earthquake', 'natural_event'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${filter === f
                  ? 'bg-white text-gray-950 border-white'
                  : 'border-gray-700 text-gray-400 hover:border-gray-500'
                }`}
            >
              {f === 'all' ? 'All' : f === 'earthquake' ? 'Earthquakes' : 'Natural Events'}
            </button>
          ))}
        </div>
      </div>

      {/* main content */}
      <div className="flex flex-1 overflow-hidden">

        {/* map */}
        <div className="flex-1 relative">
          <DisasterMap
            events={filtered}
            selectedId={selectedId}
            onSelectEvent={setSelectedId}
          />
          <div className="absolute bottom-4 left-4 flex gap-3 text-xs bg-gray-950/80 px-3 py-2 rounded-lg border border-gray-800">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-red-500 inline-block"></span>M5+</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-orange-500 inline-block"></span>M3.5+</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-yellow-500 inline-block"></span>M2.5+</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-blue-500 inline-block"></span>Event</span>
          </div>
        </div>

        {/* sidebar */}
        <div className="w-80 border-l border-gray-800 flex flex-col overflow-hidden">
          {/* sidebar tab switcher */}
          <div className="flex border-b border-gray-800 shrink-0">
            <button
              onClick={() => setSidebarTab('disasters')}
              className={`flex-1 py-2.5 text-xs transition-colors ${sidebarTab === 'disasters'
                  ? 'text-white border-b-2 border-white'
                  : 'text-gray-500 hover:text-gray-300'
                }`}
            >
              Disasters
            </button>
            <button
              onClick={() => setSidebarTab('community')}
              className={`flex-1 py-2.5 text-xs transition-colors ${sidebarTab === 'community'
                  ? 'text-white border-b-2 border-white'
                  : 'text-gray-500 hover:text-gray-300'
                }`}
            >
              Community
            </button>
          </div>

          {sidebarTab === 'disasters' ? (
            <>
              <div className="px-4 py-2 border-b border-gray-800 text-xs text-gray-500">
                {loading ? 'Loading...' : `${filtered.length} events`}
              </div>
              <div className="flex-1 overflow-y-auto">
                {filtered.map(event => (
                  <div
                    key={event.id}
                    onClick={() => setSelectedId(event.id)}
                    className={`px-4 py-3 border-b border-gray-800 cursor-pointer transition-colors hover:bg-gray-900 ${selectedId === event.id ? 'bg-gray-900 border-l-2 border-l-white' : ''
                      }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-xs text-white leading-snug">{event.title}</span>
                      {event.magnitude && (
                        <span className={`text-xs px-1.5 py-0.5 rounded shrink-0 ${event.magnitude >= 5 ? 'bg-red-900 text-red-300' :
                            event.magnitude >= 3.5 ? 'bg-orange-900 text-orange-300' :
                              'bg-yellow-900 text-yellow-300'
                          }`}>M{event.magnitude}</span>
                      )}
                      {event.category && (
                        <span className="text-xs px-1.5 py-0.5 rounded shrink-0 bg-blue-900 text-blue-300">
                          {event.category}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {new Date(event.event_time).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <NeedsPanel />
          )}
        </div>

      </div>
    </div>
  )
}

export default App