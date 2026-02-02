/**
 * Just Travel - Main Page (Orchestrator Bridge)
 * ==============================================
 *
 * This is the main entry page for the Just Travel application.
 * It serves as the orchestrator bridge to the Python ADK backend,
 * providing a chat interface for users to interact with the AI agents.
 *
 * Features:
 * - Neo-brutalist design aesthetic
 * - Chat interface for travel planning
 * - Real-time communication with backend agents
 * - Display of travel recommendations and itineraries
 */

'use client'

import { useState, useRef, useEffect } from 'react'
import { ItineraryView } from '../components/ItineraryView'

/**
 * Message type definition for chat messages
 */
interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agentSource?: string
  itineraryData?: any
}

/**
 * Travel preferences captured from user
 */
interface TravelPreferences {
  destination?: string
  dates?: { start: string; end: string }
  dietary?: string[]
  budget?: string
  interests?: string[]
}

/**
 * API response type from backend
 */
interface AgentResponse {
  agent: string
  status: string
  results?: unknown
  profile?: unknown
  itinerary?: unknown
  message?: string
}

/**
 * Main page component - Orchestrator Bridge
 */
export default function HomePage() {
  // State management
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Welcome to Just Travel! I'm your AI travel planning assistant.

I can help you plan the perfect trip based on your preferences, dietary requirements, and interests.

To get started, tell me:
- Where would you like to travel?
- Do you have any dietary restrictions? (vegetarian, halal, kosher, etc.)
- What's your travel style? (adventure, relaxation, cultural, etc.)

Just type your preferences and I'll create a personalized travel plan for you!`,
      timestamp: new Date(),
      agentSource: 'system'
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [preferences, setPreferences] = useState<TravelPreferences>({})

  // Refs
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages])

  /**
   * Send message to backend and get response
   */
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputValue,
          preferences: preferences
        })
      })

      if (!res.ok) throw new Error('API request failed')

      const response: AgentResponse = await res.json()

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message || 'I received your request.',
        timestamp: new Date(),
        agentSource: response.agent,
        itineraryData: response.itinerary
      }

      setMessages(prev => [...prev, assistantMessage])

      // Update preferences if extracted
      if (response.profile) {
        setPreferences(prev => ({ ...prev, ...response.profile as TravelPreferences }))
      }

    } catch (error) {
      console.error(error)
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error connecting to the agent. Make sure the backend endpoint is running at http://localhost:8000.',
        timestamp: new Date(),
        agentSource: 'system'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  /**
   * Handle keyboard events (Enter to send)
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-brutal-pink border-b-4 border-brutal-black">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-7xl font-mono font-bold mb-6 text-stroke">
              PLAN YOUR
              <span className="block bg-brutal-black text-brutal-yellow px-4 py-2 mt-2 inline-block rotate-brutal">
                PERFECT TRIP
              </span>
            </h1>
            <p className="text-xl md:text-2xl font-mono mb-8 max-w-2xl mx-auto">
              AI-powered travel planning that respects your dietary needs,
              budget, and travel style.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <a href="#chat" className="btn-brutal-yellow">
                Start Planning
              </a>
              <a href="#features" className="btn-brutal">
                Learn More
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-mono font-bold text-center mb-12">
            <span className="bg-brutal-blue px-4 py-2 border-4 border-brutal-black shadow-brutal">
              FEATURES
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Feature 1 */}
            <div className="card-brutal bg-brutal-yellow rotate-brutal hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🍽️</div>
              <h3 className="text-xl font-mono font-bold mb-2">Dietary Aware</h3>
              <p>
                Respects your dietary restrictions - vegetarian, vegan, halal,
                kosher, and allergen-free options.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card-brutal bg-brutal-green rotate-brutal-reverse hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-mono font-bold mb-2">Trend Analysis</h3>
              <p>
                Discovers trending destinations and hidden gems from social
                media and travel communities.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card-brutal bg-brutal-purple rotate-brutal hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🗺️</div>
              <h3 className="text-xl font-mono font-bold mb-2">Smart Routing</h3>
              <p>
                Optimizes your daily itinerary to minimize travel time and
                maximize experiences.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="card-brutal bg-brutal-orange rotate-brutal-reverse hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🏨</div>
              <h3 className="text-xl font-mono font-bold mb-2">Curated Stays</h3>
              <p>
                Finds accommodations that match your budget and preferences
                with verified reviews.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="card-brutal bg-brutal-pink rotate-brutal hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-mono font-bold mb-2">AI Agents</h3>
              <p>
                Five specialized AI agents work together to create your
                perfect travel experience.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="card-brutal bg-brutal-blue rotate-brutal-reverse hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">📅</div>
              <h3 className="text-xl font-mono font-bold mb-2">Dynamic Planning</h3>
              <p>
                Generates day-by-day itineraries that adapt to weather,
                crowds, and your energy levels.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Chat Section */}
      <section id="chat" className="py-16 md:py-24 bg-brutal-black">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-mono font-bold text-center mb-12 text-brutal-white">
            <span className="bg-brutal-yellow px-4 py-2 border-4 border-brutal-white shadow-brutal text-brutal-black">
              START PLANNING
            </span>
          </h2>

          {/* Chat Interface */}
          <div className="max-w-4xl mx-auto">
            <div className="card-brutal p-0 overflow-hidden">
              {/* Chat Header */}
              <div className="bg-brutal-yellow border-b-4 border-brutal-black p-4 flex items-center gap-3">
                <div className="w-3 h-3 bg-brutal-green border-2 border-brutal-black rounded-full"></div>
                <span className="font-mono font-bold">AI Travel Assistant</span>
                <span className="ml-auto text-sm font-mono opacity-60">
                  {preferences.destination && `Destination: ${preferences.destination}`}
                </span>
              </div>

              {/* Messages Container */}
              <div
                ref={chatContainerRef}
                className="h-[400px] overflow-y-auto p-4 space-y-4 bg-background scrollbar-hide"
              >
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`animate-slide-up ${message.role === 'user' ? 'flex justify-end' : 'flex justify-start'
                      }`}
                  >
                    <div
                      className={
                        message.role === 'user'
                          ? 'chat-bubble-user'
                          : 'chat-bubble-assistant'
                      }
                    >
                      {message.agentSource && message.role === 'assistant' && (
                        <div className="badge-brutal bg-brutal-blue mb-2 text-xs">
                          {message.agentSource}
                        </div>
                      )}
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <span className="text-xs opacity-50 mt-2 block">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {message.itineraryData && (
                        <div className="mt-4 w-full">
                          <ItineraryView
                            itinerary={message.itineraryData.daily_itinerary || message.itineraryData.itinerary}
                            summary={message.itineraryData}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                  <div className="flex justify-start animate-slide-up">
                    <div className="chat-bubble-assistant">
                      <div className="flex items-center gap-2">
                        <div className="spinner-brutal"></div>
                        <span className="font-mono text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t-4 border-brutal-black p-4 bg-brutal-white">
                <div className="flex gap-3">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Tell me about your dream trip..."
                    className="input-brutal flex-1"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputValue.trim()}
                    className="btn-brutal-green disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? '...' : 'SEND'}
                  </button>
                </div>

                {/* Quick action buttons */}
                <div className="flex flex-wrap gap-2 mt-3">
                  {[
                    'Vegetarian options',
                    'Budget travel',
                    'Adventure trip',
                    'Cultural experience'
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setInputValue(suggestion)}
                      className="badge-brutal bg-brutal-white hover:bg-brutal-yellow transition-colors cursor-pointer"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-mono font-bold text-center mb-12">
            <span className="bg-brutal-green px-4 py-2 border-4 border-brutal-black shadow-brutal">
              HOW IT WORKS
            </span>
          </h2>

          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {/* Step 1 */}
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 bg-brutal-yellow border-4 border-brutal-black shadow-brutal flex items-center justify-center font-mono font-bold text-2xl shrink-0">
                  1
                </div>
                <div className="card-brutal flex-1">
                  <h3 className="text-xl font-mono font-bold mb-2">Share Your Preferences</h3>
                  <p>
                    Tell us about your dietary restrictions, travel style, budget,
                    and interests. Our Profiler Agent captures everything.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 bg-brutal-pink border-4 border-brutal-black shadow-brutal flex items-center justify-center font-mono font-bold text-2xl shrink-0">
                  2
                </div>
                <div className="card-brutal flex-1">
                  <h3 className="text-xl font-mono font-bold mb-2">AI Agents Collaborate</h3>
                  <p>
                    Five specialized agents work together - analyzing trends,
                    finding destinations, filtering restaurants, and more.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 bg-brutal-blue border-4 border-brutal-black shadow-brutal flex items-center justify-center font-mono font-bold text-2xl shrink-0">
                  3
                </div>
                <div className="card-brutal flex-1">
                  <h3 className="text-xl font-mono font-bold mb-2">Get Your Perfect Plan</h3>
                  <p>
                    Receive a personalized, day-by-day itinerary optimized for
                    your preferences, with all dietary needs respected.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
