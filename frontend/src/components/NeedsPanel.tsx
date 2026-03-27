import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

interface Need {
  id: string
  name: string
  description: string
  category: string
  latitude: number
  longitude: number
  is_resolved: boolean
  created_at: string
}

interface Resource {
  id: string
  name: string
  description: string
  category: string
  latitude: number
  longitude: number
  is_available: boolean
  created_at: string
}

const API = import.meta.env.VITE_API_URL

const CATEGORIES = ['water', 'food', 'medical', 'shelter', 'rescue', 'other']

export default function NeedsPanel() {
  const [needs, setNeeds] = useState<Need[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [tab, setTab] = useState<'needs' | 'resources' | 'post'>('needs')
  const [postType, setPostType] = useState<'need' | 'resource'>('need')
  const [matches, setMatches] = useState<Resource[] | null>(null)
  const [selectedNeed, setSelectedNeed] = useState<string | null>(null)
  const [form, setForm] = useState({
    name: '', description: '', category: 'water',
    latitude: '', longitude: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadNeeds()
    loadResources()

    // realtime subscription for needs
    const channel = supabase
      .channel('needs-resources')
      .on('postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'needs' },
        (payload) => setNeeds(prev => [payload.new as Need, ...prev])
      )
      .on('postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'resources' },
        (payload) => setResources(prev => [payload.new as Resource, ...prev])
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [])

  async function loadNeeds() {
    const { data } = await supabase
      .from('needs')
      .select('*')
      .eq('is_resolved', false)
      .order('created_at', { ascending: false })
    setNeeds(data || [])
  }

  async function loadResources() {
    const { data } = await supabase
      .from('resources')
      .select('*')
      .eq('is_available', true)
      .order('created_at', { ascending: false })
    setResources(data || [])
  }

  async function handleSubmit() {
    if (!form.name || !form.description || !form.latitude || !form.longitude) {
      setMessage('Please fill all fields')
      return
    }
    setSubmitting(true)
    setMessage('')

    try {
      const endpoint = postType === 'need' ? '/api/needs' : '/api/resources'
      const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          description: form.description,
          category: form.category,
          latitude: parseFloat(form.latitude),
          longitude: parseFloat(form.longitude),
        })
      })

      if (res.ok) {
        setMessage(`${postType === 'need' ? 'Need' : 'Resource'} posted successfully`)
        setForm({ name: '', description: '', category: 'water', latitude: '', longitude: '' })
      } else {
        const err = await res.text()
        setMessage(`Error: ${err}`)
      }
    } catch (err: any) {
      setMessage(`Network error: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  async function findMatches(needId: string) {
    setSelectedNeed(needId)
    const res = await fetch(`${API}/api/match/${needId}`)
    const data = await res.json()
    setMatches(data.matches || [])
    setTab('needs')
  }

  return (
    <div className="flex flex-col h-full">
      {/* tabs */}
      <div className="flex border-b border-gray-800 shrink-0">
        {(['needs', 'resources', 'post'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2 text-xs capitalize transition-colors ${
              tab === t
                ? 'text-white border-b-2 border-white'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {t === 'needs' ? `Needs (${needs.length})`
              : t === 'resources' ? `Resources (${resources.length})`
              : 'Post'}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto">

        {/* needs tab */}
        {tab === 'needs' && (
          <div>
            {needs.length === 0 && (
              <p className="text-xs text-gray-600 p-4">No active needs posted</p>
            )}
            {needs.map(need => (
              <div key={need.id}
                className={`p-3 border-b border-gray-800 ${selectedNeed === need.id ? 'bg-gray-900' : ''}`}
              >
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <p className="text-xs font-medium text-white">{need.description}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {need.name} · {need.category}
                    </p>
                    <p className="text-xs text-gray-600">
                      {need.latitude.toFixed(3)}, {need.longitude.toFixed(3)}
                    </p>
                  </div>
                  <button
                    onClick={() => findMatches(need.id)}
                    className="text-xs px-2 py-1 border border-gray-700 rounded hover:border-gray-500 text-gray-400 hover:text-white shrink-0"
                  >
                    Match
                  </button>
                </div>
                {selectedNeed === need.id && matches !== null && (
                  <div className="mt-2 pt-2 border-t border-gray-800">
                    <p className="text-xs text-gray-500 mb-1">
                      {matches.length} resource{matches.length !== 1 ? 's' : ''} nearby
                    </p>
                    {matches.map((r: any) => (
                      <div key={r.id} className="text-xs text-green-400 py-0.5">
                        {r.description} — {r.distance_km}km away
                      </div>
                    ))}
                    {matches.length === 0 && (
                      <p className="text-xs text-gray-600">No matches within 50km</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* resources tab */}
        {tab === 'resources' && (
          <div>
            {resources.length === 0 && (
              <p className="text-xs text-gray-600 p-4">No resources posted</p>
            )}
            {resources.map(resource => (
              <div key={resource.id} className="p-3 border-b border-gray-800">
                <p className="text-xs font-medium text-white">{resource.description}</p>
                <p className="text-xs text-gray-500 mt-0.5">
                  {resource.name} · {resource.category}
                </p>
                <p className="text-xs text-gray-600">
                  {resource.latitude.toFixed(3)}, {resource.longitude.toFixed(3)}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* post tab */}
        {tab === 'post' && (
          <div className="p-4 flex flex-col gap-3">
            <div className="flex gap-2">
              {(['need', 'resource'] as const).map(t => (
                <button
                  key={t}
                  onClick={() => setPostType(t)}
                  className={`flex-1 py-1.5 text-xs rounded border transition-colors ${
                    postType === t
                      ? 'bg-white text-gray-950 border-white'
                      : 'border-gray-700 text-gray-400'
                  }`}
                >
                  {t === 'need' ? 'I need help' : 'I can help'}
                </button>
              ))}
            </div>

            <input
              placeholder="Your name"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-gray-500"
            />

            <textarea
              placeholder="Describe what you need or can offer"
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              rows={2}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-gray-500 resize-none"
            />

            <select
              value={form.category}
              onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-gray-500"
            >
              {CATEGORIES.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <div className="flex gap-2">
              <input
                placeholder="Latitude"
                value={form.latitude}
                onChange={e => setForm(f => ({ ...f, latitude: e.target.value }))}
                className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-gray-500"
              />
              <input
                placeholder="Longitude"
                value={form.longitude}
                onChange={e => setForm(f => ({ ...f, longitude: e.target.value }))}
                className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-gray-500"
              />
            </div>

            <p className="text-xs text-gray-600">
              Tip: right-click on the map to get coordinates
            </p>

            {message && (
              <p className={`text-xs ${message.includes('success') ? 'text-green-400' : 'text-red-400'}`}>
                {message}
              </p>
            )}

            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="py-2 text-xs bg-white text-gray-950 rounded hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {submitting ? 'Posting...' : `Post ${postType}`}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}