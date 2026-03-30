import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'

interface Event {
  id: string
  title: string
  latitude: number
  longitude: number
  magnitude: number | null
  category: string | null
  type: string
}

interface Props {
  events: Event[]
  selectedId: string | null
  onSelectEvent: (id: string) => void
}

export default function DisasterMap({ events, selectedId, onSelectEvent }: Props) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const markers = useRef<Record<string, maplibregl.Marker>>({})

  useEffect(() => {
    if (map.current || !mapContainer.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/dark',
      center: [0, 20],
      zoom: 2,
    })

    map.current.addControl(new maplibregl.NavigationControl())
  }, [])

  useEffect(() => {
    if (!map.current) return

    // remove old markers not in current events
    Object.keys(markers.current).forEach(id => {
      if (!events.find(e => e.id === id)) {
        markers.current[id].remove()
        delete markers.current[id]
      }
    })

    // add new markers
    events.forEach(event => {
      if (markers.current[event.id]) return

      const isEarthquake = event.type === 'earthquake'
      const mag = event.magnitude || 0

      // marker color by severity
      const color = isEarthquake
        ? mag >= 5 ? '#ef4444' : mag >= 3.5 ? '#f97316' : '#eab308'
        : '#3b82f6'

      const el = document.createElement('div')
      el.style.cssText = `
        width: ${isEarthquake ? Math.max(10, mag * 4) : 14}px;
        height: ${isEarthquake ? Math.max(10, mag * 4) : 14}px;
        background: ${color};
        border-radius: 50%;
        border: 2px solid white;
        cursor: pointer;
        opacity: 0.85;
      `

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([event.longitude, event.latitude])
        .setPopup(
          new maplibregl.Popup({ offset: 10 })
            .setHTML(`
      <div style="
        font-family: sans-serif;
        padding: 6px 8px;
        background: #111827;
          color: #f9fafb;
          border-radius: 6px;
          font-size: 12px;
          min-width: 160px;
        ">
          <div style="font-weight:600;margin-bottom:4px;color:#ffffff">
            ${event.title}
          </div>
          <div style="color:#9ca3af">
            ${isEarthquake
                ? `Magnitude: <span style="color:#fca5a5">${event.magnitude}</span>`
                : `<span style="color:#93c5fd">${event.category || 'Natural Event'}</span>`
              }
          </div>
          <div style="color:#6b7280;font-size:11px;margin-top:3px">
            ${event.latitude.toFixed(3)}, ${event.longitude.toFixed(3)}
          </div>
        </div>
      `)
        )
        .addTo(map.current!)

      el.addEventListener('click', () => onSelectEvent(event.id))
      markers.current[event.id] = marker
    })
  }, [events])

  // fly to selected event
  useEffect(() => {
    if (!map.current || !selectedId) return
    const event = events.find(e => e.id === selectedId)
    if (!event) return
    map.current.flyTo({
      center: [event.longitude, event.latitude],
      zoom: 6,
      duration: 1500,
    })
    markers.current[selectedId]?.togglePopup()
  }, [selectedId])

  return <div ref={mapContainer} className="w-full h-full" />
}