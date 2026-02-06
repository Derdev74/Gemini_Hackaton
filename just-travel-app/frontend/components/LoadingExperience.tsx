'use client'

import { useState, useEffect, Fragment } from 'react'

const STAGES = [
  { id: 'profiler',  label: 'Profiler',   emoji: '👤', enterAt: 0,    color: 'text-brutal-orange',  border: 'border-brutal-orange/50', glow: 'rgba(255,159,67,0.3)' },
  { id: 'parallel',  label: 'Exploring', emoji: '🔍', enterAt: 1500, color: 'text-brutal-orange',    border: 'border-brutal-orange/50',   glow: 'rgba(255,159,67,0.3)' },
  { id: 'optimizer', label: 'Optimizing',emoji: '⚡', enterAt: 4000, color: 'text-brutal-purple',  border: 'border-brutal-purple/50', glow: 'rgba(185,103,255,0.3)' },
  { id: 'creative',  label: 'Creating',  emoji: '🎨', enterAt: 6500, color: 'text-brutal-pink',    border: 'border-brutal-pink/50',   glow: 'rgba(255,107,157,0.3)' },
]

const DESTINATIONS = [
  { name: 'Tokyo, Japan',      desc: 'Cherry blossoms & neon nights',  bg: 'from-[#1a0520] via-[#3d1040] to-[#0f0f23]' },
  { name: 'Santorini, Greece', desc: 'Sun-drenched island paradise',   bg: 'from-[#051520] via-[#0d3060] to-[#0f1a23]' },
  { name: 'Kyoto, Japan',      desc: 'Ancient temples & zen gardens',  bg: 'from-[#051a10] via-[#0d4030] to-[#0f2315]' },
  { name: 'Paris, France',     desc: 'Lights of the city of love',     bg: 'from-[#200e05] via-[#503010] to-[#1a0f0a]' },
  { name: 'Bali, Indonesia',   desc: 'Tropical serenity awaits',       bg: 'from-[#150520] via-[#3d1060] to-[#0a0f1a]' },
]

export default function LoadingExperience() {
  const [elapsed, setElapsed] = useState(0)
  const [idx, setIdx] = useState(0)

  useEffect(() => {
    const tick = setInterval(() => setElapsed(e => e + 100), 100)
    return () => clearInterval(tick)
  }, [])

  useEffect(() => {
    const carousel = setInterval(() => setIdx(i => (i + 1) % DESTINATIONS.length), 2800)
    return () => clearInterval(carousel)
  }, [])

  const activeIdx = STAGES.reduce((acc, s, i) => (elapsed >= s.enterAt ? i : acc), 0)
  const dest = DESTINATIONS[idx]

  return (
    <div className="space-y-4">
      {/* ── Agent Pipeline ── */}
      <div className="flex items-center justify-center gap-1 flex-wrap">
        {STAGES.map((stage, i) => {
          const done    = i < activeIdx
          const active  = i === activeIdx
          return (
            <Fragment key={stage.id}>
              <div
                className={`flex items-center gap-1.5 px-3 py-1.5 border text-xs font-mono font-bold transition-all duration-500
                  ${done   ? `bg-black/60 ${stage.border} ${stage.color} opacity-60` :
                    active ? `bg-black/70 ${stage.border} ${stage.color}`           :
                             'bg-black/30 border-white/10 text-white/25'}`}
                style={active ? { boxShadow: `0 0 10px ${stage.glow}` } : {}}
              >
                <span>{done ? '✓' : active ? stage.emoji : '○'}</span>
                {stage.label}
              </div>
              {i < STAGES.length - 1 && (
                <span className={`text-xs ${done || active ? 'text-white/30' : 'text-white/10'}`}>→</span>
              )}
            </Fragment>
          )
        })}
      </div>

      {/* ── Destination Carousel ── */}
      <div className={`relative overflow-hidden border border-white/10 bg-gradient-to-br ${dest.bg}`} style={{ height: '140px' }}>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-4">
          <p className="text-[10px] font-mono text-white/40 uppercase tracking-widest mb-2 animate-glow-pulse">Exploring</p>
          <h3 className="text-xl font-mono font-bold text-white">{dest.name}</h3>
          <p className="text-sm text-white/55 mt-1">{dest.desc}</p>
        </div>
        {/* Dots */}
        <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-1.5">
          {DESTINATIONS.map((_, i) => (
            <div key={i} className={`w-1.5 h-1.5 rounded-full transition-all ${i === idx ? 'bg-white' : 'bg-white/25'}`} />
          ))}
        </div>
      </div>

      {/* ── Spinner ── */}
      <div className="flex items-center justify-center gap-2">
        <div className="spinner-brutal"></div>
        <span className="font-mono text-sm text-white/55">Your AI agents are working...</span>
      </div>
    </div>
  )
}
