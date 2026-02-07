"use client";

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
    summary?: {
        total_days: number
        total_activities: number
        estimated_total_cost: number
        day_themes: string[]
    }
}

export function ItineraryView({ itinerary, summary }: ItineraryProps) {
    const [activeDay, setActiveDay] = React.useState(1)

    if (!itinerary || itinerary.length === 0) return null

    // Derive stats from itinerary if summary not provided
    const totalDays = summary?.total_days || itinerary.length
    const totalActivities = summary?.total_activities || itinerary.reduce((sum, day) => sum + (day.time_slots?.length || 0), 0)
    const totalCost = summary?.estimated_total_cost || itinerary.reduce((sum, day) => sum + (day.estimated_cost || 0), 0)

    const currentDay = itinerary.find(d => d.day_number === activeDay) || itinerary[0]

    return (
        <div className="space-y-6 mt-4 animate-slide-up">
            {/* Summary Card */}
            <div className="bg-brutal-white p-6 rounded-2xl border-4 border-brutal-black shadow-brutal">
                <h3 className="text-2xl font-mono font-bold mb-4 bg-brutal-yellow inline-block px-3 py-1 border-2 border-brutal-black">
                    TRIP SUMMARY
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="p-3 border-2 border-brutal-black bg-brutal-blue text-center shadow-brutal-hover">
                        <span className="block text-2xl font-bold text-brutal-black">{totalDays}</span>
                        <span className="text-xs font-mono uppercase">Days</span>
                    </div>
                    <div className="p-3 border-2 border-brutal-black bg-brutal-green text-center shadow-brutal-hover">
                        <span className="block text-2xl font-bold text-brutal-black">{totalActivities}</span>
                        <span className="text-xs font-mono uppercase">Activities</span>
                    </div>
                    <div className="p-3 border-2 border-brutal-black bg-brutal-pink text-center shadow-brutal-hover">
                        <span className="block text-2xl font-bold text-brutal-black">${totalCost}</span>
                        <span className="text-xs font-mono uppercase">Est. Cost</span>
                    </div>
                    <div className="p-3 border-2 border-brutal-black bg-brutal-orange text-center shadow-brutal-hover">
                        <span className="block text-2xl font-bold text-brutal-black">Many</span>
                        <span className="text-xs font-mono uppercase">Memories</span>
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
                            flex-shrink-0 px-4 py-2 font-mono font-bold border-2 border-brutal-black transition-all
                            ${activeDay === day.day_number
                                ? 'bg-brutal-black text-brutal-white shadow-brutal translate-x-[2px] translate-y-[2px]'
                                : 'bg-brutal-white hover:bg-gray-100'}
                        `}
                    >
                        Day {day.day_number}
                    </button>
                ))}
            </div>

            {/* Daily Schedule */}
            <div className="bg-brutal-white p-6 rounded-2xl border-4 border-brutal-black shadow-brutal">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-2 border-b-4 border-brutal-black pb-4">
                    <div>
                        <span className="text-sm font-mono opacity-60 block">
                            {new Date(currentDay.date + 'T00:00:00').toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}
                        </span>
                        <h2 className="text-3xl font-bold font-mono uppercase">
                            Day {currentDay.day_number}
                        </h2>
                    </div>
                    <div className="bg-brutal-purple text-brutal-white px-3 py-1 font-mono font-bold text-sm border-2 border-brutal-black transform -rotate-2 shadow-brutal-hover">
                        {currentDay.theme}
                    </div>
                </div>

                <div className="space-y-4">
                    {currentDay.time_slots.map((slot, index) => (
                        <div key={index} className="flex gap-4 group hover:bg-gray-50 p-2 rounded transition-colors border-b-2 border-dashed border-gray-200 last:border-0">
                            {/* Time Column */}
                            <div className="w-16 flex-shrink-0 font-mono text-sm font-bold pt-1">
                                {slot.start_time}
                            </div>

                            {/* Timeline Dot */}
                            <div className="relative flex flex-col items-center">
                                <div className={`w-4 h-4 rounded-full border-2 border-brutal-black z-10
                                    ${slot.activity_type === 'meal' ? 'bg-brutal-orange' :
                                    slot.activity_type === 'transport' ? 'bg-gray-400' : 'bg-brutal-blue'}`}
                                />
                                <div className="w-1 h-full bg-black absolute top-4 opacity-10 group-last:hidden" />
                            </div>

                            {/* Content Column */}
                            <div className="flex-1 pb-4">
                                <div className="flex justify-between items-start">
                                    <h4 className="font-bold text-lg leading-none mb-1">
                                        {slot.activity.name || slot.activity_type}
                                    </h4>
                                    <span className="text-xs font-mono bg-brutal-black text-white px-2 py-0.5 ml-2">
                                        {slot.end_time}
                                    </span>
                                </div>

                                <p className="text-sm text-gray-600 mb-1 font-mono">
                                    📍 {slot.location}
                                </p>

                                {slot.notes && (
                                    <div className="text-sm italic bg-yellow-50 p-2 border-l-4 border-brutal-yellow mt-2">
                                        {slot.notes}
                                    </div>
                                )}

                                {/* Tags */}
                                <div className="flex gap-2 mt-2">
                                    <span className="text-[10px] uppercase font-bold border border-black px-1">
                                        {slot.activity_type}
                                    </span>
                                    {slot.activity.price_level !== undefined && slot.activity.price_level > 0 && (
                                        <span className="text-[10px] uppercase font-bold border border-black px-1 text-green-700">
                                            {Array(slot.activity.price_level).fill('$').join('')}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Day Footer */}
                <div className="mt-6 pt-4 border-t-4 border-brutal-black flex justify-between items-center bg-gray-50 p-4 -mb-6 -mx-6 rounded-b-xl">
                    <div className="font-mono text-xs">
                        Est. Day Cost: <span className="font-bold text-lg">${currentDay.estimated_cost}</span>
                    </div>
                    <div className="font-mono text-xs">
                        Travel Time: <span className="font-bold">{currentDay.total_travel_time}m</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
