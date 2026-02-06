'use client'

import { useState } from 'react'

export interface Preferences {
  dietary: string[]
  budget: number          // $/day, 50–1000 step 50
  tripType: string
  companionType: string   // solo | romantic | family | friends | business
  startDate: string
  endDate: string
}

const DIETARY_OPTIONS = [
  { id: 'none',        label: 'None' },
  { id: 'vegetarian', label: 'Vegetarian' },
  { id: 'vegan',      label: 'Vegan' },
  { id: 'halal',      label: 'Halal' },
  { id: 'kosher',     label: 'Kosher' },
  { id: 'gluten-free',label: 'Gluten-Free' },
]

const COMPANION_TYPES = [
  { id: 'solo',     label: '🧍 Solo',     color: 'border-brutal-blue/40 text-brutal-blue' },
  { id: 'romantic', label: '💑 Romantic', color: 'border-brutal-pink/40 text-brutal-pink' },
  { id: 'family',   label: '👨‍👩‍👧 Family',  color: 'border-brutal-yellow/40 text-brutal-yellow' },
  { id: 'friends',  label: '👯 Friends',  color: 'border-brutal-green/40 text-brutal-green' },
  { id: 'business', label: '💼 Business', color: 'border-brutal-purple/40 text-brutal-purple' },
]

const TRIP_TYPES = [
  { id: 'adventure',  label: '🧗 Adventure',  color: 'border-brutal-green/40 text-brutal-green' },
  { id: 'relaxation', label: '🏖️ Relaxation', color: 'border-brutal-blue/40 text-brutal-blue' },
  { id: 'cultural',   label: '🏛️ Cultural',   color: 'border-brutal-purple/40 text-brutal-purple' },
  { id: 'food',       label: '🍜 Food Tour',  color: 'border-brutal-orange/40 text-brutal-orange' },
]

const BUDGET_MIN  = 50
const BUDGET_MAX  = 1000
const BUDGET_STEP = 50

function budgetFillPercent(val: number) {
  return ((val - BUDGET_MIN) / (BUDGET_MAX - BUDGET_MIN)) * 100
}

export default function PreferencePanel({ value, onChange }: {
  value: Preferences
  onChange: (p: Preferences) => void
}) {
  const [expanded, setExpanded] = useState(true)

  const toggleDiet = (id: string) => {
    const next = value.dietary.includes(id)
      ? value.dietary.filter(d => d !== id)
      : [...value.dietary, id]
    onChange({ ...value, dietary: next })
  }

  return (
    <div className="card-brutal mb-4 border-glow-orange">
      {/* Toggle Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-left"
      >
        <span className="font-mono font-bold text-sm text-brutal-orange uppercase tracking-wider">
          ⚙️ Travel Preferences
        </span>
        <span className="text-white/50 text-sm transition-transform" style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
          ▼
        </span>
      </button>

      {/* Collapsed summary badges */}
      {!expanded && (
        <div className="mt-2 pt-2 border-t border-white/10 flex flex-wrap gap-2">
          {value.companionType && (
            <span className="badge-brutal text-xs border-glow-pink text-brutal-pink">
              {COMPANION_TYPES.find(c => c.id === value.companionType)?.label}
            </span>
          )}
          {value.dietary.length > 0 && value.dietary.map(d => (
            <span key={d} className="badge-brutal text-xs border-glow-orange text-brutal-orange">{d}</span>
          ))}
          {value.tripType && (
            <span className="badge-brutal text-xs border-glow-pink text-brutal-pink">
              {TRIP_TYPES.find(t => t.id === value.tripType)?.label}
            </span>
          )}
          <span className="badge-brutal text-xs border-glow-orange text-brutal-orange">${value.budget}/day</span>
        </div>
      )}

      {expanded && (
        <div className="mt-4 pt-4 border-t border-white/10 space-y-5">

          {/* ── Who's Travelling ── */}
          <div>
            <label className="block font-mono text-xs text-white/50 uppercase mb-2">Who's Travelling</label>
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
              {COMPANION_TYPES.map(c => {
                const active = value.companionType === c.id
                return (
                  <button
                    key={c.id}
                    onClick={() => onChange({ ...value, companionType: c.id })}
                    className={`px-2 py-2 font-mono text-xs font-bold border transition-all text-center rounded-xl
                      ${active
                        ? `bg-black/60 ${c.color} border-current`
                        : 'bg-black/30 border-white/15 text-white/50 hover:border-white/30 hover:text-white'
                      }`}
                  >
                    {c.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* ── Dietary Tabs ── */}
          <div>
            <label className="block font-mono text-xs text-white/50 uppercase mb-2">Dietary Needs</label>
            <div className="flex flex-wrap gap-2">
              {DIETARY_OPTIONS.map(opt => {
                const active = value.dietary.includes(opt.id)
                return (
                  <button
                    key={opt.id}
                    onClick={() => toggleDiet(opt.id)}
                    className={`px-3 py-1 font-mono text-xs font-bold uppercase border transition-all rounded-lg
                      ${active
                        ? 'bg-brutal-orange/15 border-brutal-orange/50 text-brutal-orange'
                        : 'bg-black/40 border-white/15 text-white/50 hover:border-white/30 hover:text-white'
                      }`}
                  >
                    {opt.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* ── Trip Style ── */}
          <div>
            <label className="block font-mono text-xs text-white/50 uppercase mb-2">Trip Style</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {TRIP_TYPES.map(t => {
                const active = value.tripType === t.id
                return (
                  <button
                    key={t.id}
                    onClick={() => onChange({ ...value, tripType: t.id })}
                    className={`px-3 py-2 font-mono text-xs font-bold border transition-all text-left rounded-xl
                      ${active
                        ? `bg-black/60 ${t.color} border-current`
                        : 'bg-black/30 border-white/15 text-white/50 hover:border-white/30 hover:text-white'
                      }`}
                  >
                    {t.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* ── Budget Slider ($/day) ── */}
          <div>
            <label className="block font-mono text-xs text-white/50 uppercase mb-2">
              Budget — <span className="text-brutal-orange font-bold text-sm">${value.budget}<span className="text-white/35 text-xs font-normal">/day</span></span>
            </label>
            <div className="relative">
              <input
                type="range"
                min={BUDGET_MIN}
                max={BUDGET_MAX}
                step={BUDGET_STEP}
                value={value.budget}
                onChange={e => onChange({ ...value, budget: Number(e.target.value) })}
                className="w-full h-2 appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #FF9F43 0%, #FF6B9D ${budgetFillPercent(value.budget)}%, rgba(255,255,255,0.1) ${budgetFillPercent(value.budget)}%, rgba(255,255,255,0.1) 100%)`,
                  borderRadius: '8px',
                }}
              />
              {/* Tick labels */}
              <div className="flex justify-between mt-1.5">
                {[50, 250, 500, 750, 1000].map(tick => (
                  <span
                    key={tick}
                    className={`text-[10px] font-mono ${value.budget === tick ? 'text-brutal-orange' : 'text-white/30'}`}
                  >
                    ${tick}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* ── Date Range ── */}
          <div>
            <label className="block font-mono text-xs text-white/50 uppercase mb-2">Travel Dates</label>
            <div className="flex flex-wrap gap-3 items-center">
              <div className="flex-1 min-w-[140px]">
                <span className="text-[10px] font-mono text-white/35 uppercase">From</span>
                <input
                  type="date"
                  value={value.startDate}
                  onChange={e => onChange({ ...value, startDate: e.target.value })}
                  className="input-brutal w-full text-sm mt-0.5"
                />
              </div>
              <span className="text-white/30 font-mono text-sm mt-4">→</span>
              <div className="flex-1 min-w-[140px]">
                <span className="text-[10px] font-mono text-white/35 uppercase">To</span>
                <input
                  type="date"
                  value={value.endDate}
                  min={value.startDate}
                  onChange={e => onChange({ ...value, endDate: e.target.value })}
                  className="input-brutal w-full text-sm mt-0.5"
                />
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  )
}
