import React from 'react'

interface Activity {
    name: string
    type: string
    location: string | object
    duration: number
    price_level?: number
    notes?: string
}

interface TimeSlot {
    start_time: string
    end_time: string
    activity_type: string
    activity: Activity
    location: string
    notes: string
}

interface DayPlan {
    date: string
    day_number: number
    theme: string
    time_slots: TimeSlot[]
    total_travel_time: number
    estimated_cost: number
}

interface ItineraryProps {
    itinerary: DayPlan[]
    summary?: unknown
}

export function ItineraryView({ itinerary }: ItineraryProps) {
    const [activeDay, setActiveDay] = React.useState(1)

    if (!itinerary || itinerary.length === 0) return null

    // Derive stats directly from the itinerary data
    const totalDays = itinerary.length
    const totalActivities = itinerary.reduce((sum, day) => sum + (day.time_slots?.length || 0), 0)
    const totalCost = itinerary.reduce((sum, day) => sum + (day.estimated_cost || 0), 0)

    const currentDay = itinerary.find(d => d.day_number === activeDay) || itinerary[0]

    return (
        <div className="space-y-6 mt-4 animate-slide-up">
            {/* Summary Card */}
            <div className="card-brutal">
                <h3 className="text-2xl font-mono font-bold mb-4 text-brutal-yellow border-b border-brutal-yellow/30 inline-block pb-1">
                    TRIP SUMMARY
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="p-2 border border-brutal-blue/40 bg-black/40 text-center" style={{boxShadow:'0 0 8px rgba(0,212,255,0.12)'}}>
                        <span className="block text-2xl font-bold text-brutal-blue">{totalDays}</span>
                        <span className="text-xs font-mono uppercase text-white/50">Days</span>
                    </div>
                    <div className="p-2 border border-brutal-green/40 bg-black/40 text-center" style={{boxShadow:'0 0 8px rgba(0,255,133,0.12)'}}>
                        <span className="block text-2xl font-bold text-brutal-green">{totalActivities}</span>
                        <span className="text-xs font-mono uppercase text-white/50">Activities</span>
                    </div>
                    <div className="p-2 border border-brutal-pink/40 bg-black/40 text-center" style={{boxShadow:'0 0 8px rgba(255,107,157,0.12)'}}>
                        <span className="block text-2xl font-bold text-brutal-pink">${totalCost}</span>
                        <span className="text-xs font-mono uppercase text-white/50">Est. Cost</span>
                    </div>
                    <div className="p-2 border border-brutal-orange/40 bg-black/40 text-center" style={{boxShadow:'0 0 8px rgba(255,159,67,0.12)'}}>
                        <span className="block text-2xl font-bold text-brutal-orange">Many</span>
                        <span className="text-xs font-mono uppercase text-white/50">Memories</span>
                    </div>
                </div>
            </div>

            {/* Day Tabs */}
            <div className="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
                {itinerary.map((day) => (
                    <button
                        key={day.day_number}
                        onClick={() => setActiveDay(day.day_number)}
                        className={`
              flex-shrink-0 px-4 py-2 font-mono font-bold border transition-all
              ${activeDay === day.day_number
                                ? 'bg-black/80 text-brutal-blue border-glow-cyan'
                                : 'bg-black/30 border-white/15 text-white/60 hover:border-white/30 hover:text-white'}
            `}
                    >
                        Day {day.day_number}
                    </button>
                ))}
            </div>

            {/* Daily Schedule */}
            <div className="card-brutal">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-2 border-b border-white/10 pb-4">
                    <div>
                        <span className="text-sm font-mono text-white/50 block">
                            {new Date(currentDay.date + 'T00:00:00').toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}
                        </span>
                        <h2 className="text-3xl font-bold font-mono uppercase text-white">
                            Day {currentDay.day_number}
                        </h2>
                    </div>
                    <div className="badge-brutal border-glow-purple text-brutal-purple text-sm transform -rotate-2">
                        {currentDay.theme}
                    </div>
                </div>

                <div className="space-y-4">
                    {currentDay.time_slots.map((slot, index) => (
                        <div key={index} className="flex gap-4 group hover:bg-white/5 p-2 transition-colors border-b border-white/8 last:border-0">
                            {/* Time Column */}
                            <div className="w-16 flex-shrink-0 font-mono text-sm font-bold pt-1 text-white/80">
                                {slot.start_time}
                            </div>

                            {/* Timeline Dot */}
                            <div className="relative flex flex-col items-center">
                                <div
                                    className={`w-4 h-4 rounded-full z-10
                  ${slot.activity_type === 'meal' ? 'bg-brutal-orange' :
                                        slot.activity_type === 'transport' ? 'bg-gray-500' : 'bg-brutal-blue'}`}
                                    style={{boxShadow: slot.activity_type === 'meal' ? '0 0 6px #FF9F43' : slot.activity_type === 'transport' ? '0 0 4px #6B7280' : '0 0 6px #00D4FF'}}
                                />
                                <div className="w-px h-full bg-white absolute top-4 opacity-15 group-last:hidden" />
                            </div>

                            {/* Content Column */}
                            <div className="flex-1 pb-4">
                                <div className="flex justify-between items-start">
                                    <h4 className="font-bold text-lg leading-none mb-1 text-white">
                                        {slot.activity.name || slot.activity_type}
                                    </h4>
                                    <span className="text-xs font-mono bg-black/60 border border-white/15 text-white/70 px-2 py-0.5 ml-2">
                                        {slot.end_time}
                                    </span>
                                </div>

                                <p className="text-sm text-white/50 mb-1 font-mono">
                                    📍 {slot.location}
                                </p>

                                {slot.notes && (
                                    <div className="text-sm italic bg-black/40 p-2 border-l-2 border-brutal-yellow/60 mt-2 text-white/70">
                                        {slot.notes}
                                    </div>
                                )}

                                {/* Tags */}
                                <div className="flex gap-2 mt-2">
                                    <span className="text-[10px] uppercase font-bold border border-white/20 px-1 text-white/60">
                                        {slot.activity_type}
                                    </span>
                                    {slot.activity.price_level !== undefined && (
                                        <span className="text-[10px] uppercase font-bold border border-brutal-green/30 px-1 text-brutal-green">
                                            {Array(slot.activity.price_level).fill('$').join('')}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Day Footer */}
                <div className="mt-6 pt-4 border-t border-white/10 flex justify-between items-center bg-black/40 p-4 -mb-6 -mx-6">
                    <div className="font-mono text-xs text-white/50">
                        Est. Day Cost: <span className="font-bold text-lg text-brutal-green">${currentDay.estimated_cost}</span>
                    </div>
                    <div className="font-mono text-xs text-white/50">
                        Travel Time: <span className="font-bold text-white">{currentDay.total_travel_time}m</span>
                    </div>
                </div>

            </div>
        </div>
    )
}
