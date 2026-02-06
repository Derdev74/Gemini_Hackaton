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
import { useSession, signIn, signOut } from "next-auth/react"
import { ItineraryView } from '../components/ItineraryView'
import PreferencePanel, { Preferences } from '../components/PreferencePanel'
import LoadingExperience from '../components/LoadingExperience'
import { useOnlineStatus } from '../hooks/useOnlineStatus'
import { offlineStorage } from '../lib/offline-storage'
import { syncManager } from '../lib/sync-manager'

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
  uploadedImage?: string
  creativeData?: any
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
  message?: string
  profile?: unknown
  data?: { itinerary?: any }
  creative?: { poster_url?: string; video_url?: string }
  type?: 'optimization_update' | 'standard_chat'  // Chatbot response types
}

/**
 * Main page component - Orchestrator Bridge
 */
export default function HomePage() {
  const { data: session } = useSession()
  const isOnline = useOnlineStatus()
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [isLoginMode, setIsLoginMode] = useState(true)
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authName, setAuthName] = useState('')
  const [authError, setAuthError] = useState('')

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
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set())
  const [pendingSave, setPendingSave] = useState<Message | null>(null)
  const [panelPrefs, setPanelPrefs] = useState<Preferences>({
    dietary: [], budget: 200, tripType: '', companionType: '', startDate: '', endDate: ''
  })
  const [notification, setNotification] = useState<string>('')  // For chatbot update notifications
  const [latestItinerary, setLatestItinerary] = useState<any>(null)  // Track latest itinerary for context

  // Sync Google Session with Backend
  useEffect(() => {
    // @ts-ignore
    if (session?.id_token) {
      // Exchange token
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Fix: Ensure cookies are set
        // @ts-ignore
        body: JSON.stringify({ id_token: session.id_token })
      }).then(async res => {
        if (res.ok) {
          const data = await res.json()
          console.log("Synced with Backend via Google")
          setCurrentUser(data.user) // Update local state for UI feedback
          setAuthModalOpen(false)
          // Force a refresh of next-auth session if needed, but we rely on cookies mostly now
        } else {
          const errData = await res.json().catch(() => ({}))
          console.error("Google Sync Failed:", res.status, errData)
        }
      }).catch(err => {
        console.error("Google Sync Fetch Error:", err)
      })
    }
  }, [session])

  // UI State for Local User
  const [currentUser, setCurrentUser] = useState<{ email: string, full_name?: string } | null>(null)

  // Check valid session on mount
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
      credentials: 'include'
    }).then(async res => {
      if (res.ok) {
        const user = await res.json()
        setCurrentUser(user)
      }
    }).catch(() => { })
  }, [])

  // Auto-sync pending saves when connection is restored
  useEffect(() => {
    if (isOnline && syncManager.hasPendingSaves()) {
      console.log('🔄 Connection restored, syncing pending saves...')
      syncManager.syncPending(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
        .then(() => {
          if (syncManager.hasPendingSaves() === false) {
            setMessages(prev => [...prev, {
              id: `sys-${Date.now()}`,
              role: 'assistant',
              content: '✅ All offline saves have been synced!',
              timestamp: new Date(),
              agentSource: 'system'
            }])
          }
        })
        .catch(err => {
          console.error('Sync failed:', err)
        })
    }
  }, [isOnline])

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setAuthError('')

    const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register'
    const body = isLoginMode
      ? { email: authEmail, password: authPassword }
      : { email: authEmail, password: authPassword, full_name: authName }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Fix: Ensure cookies are set
        body: JSON.stringify(body)
      })

      if (res.ok) {
        const data = await res.json()
        const loggedInUser = data.user || { email: authEmail, full_name: authName }
        setCurrentUser(loggedInUser)
        setAuthModalOpen(false)
        setAuthEmail('')
        setAuthPassword('')
        // If user was trying to save a plan before logging in, do it now
        if (pendingSave) {
          const msg = pendingSave
          setPendingSave(null)
          setTimeout(() => savePlan(msg), 100)
        }
      } else {
        const data = await res.json()
        setAuthError(data.detail || 'Authentication failed')
      }
    } catch (err) {
      setAuthError('Connection error')
    }
  }

  const savePlan = async (message: Message) => {
    if (!currentUser) {
      setPendingSave(message)
      setAuthModalOpen(true)
      return
    }
    const itinerary = message.itineraryData

    try {
      // ALWAYS save to IndexedDB first (works offline)
      await offlineStorage.saveItinerary({
        id: message.id,
        destination: itinerary?.destination || 'Unknown',
        summary: itinerary?.summary || '',
        itinerary_data: itinerary || {},
        creative_assets: message.creativeData || {}
      })

      setSavedIds(prev => new Set(prev).add(message.id))

      // If online, also sync to backend
      if (isOnline) {
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/itinerary/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              destination: itinerary?.destination || 'Unknown',
              summary: itinerary?.summary || '',
              itinerary_data: itinerary || {},
              creative_assets: message.creativeData || {},
              media_task_id: message.creativeData?.task_id
            })
          })

          if (res.ok) {
            setMessages(prev => [...prev, {
              id: `sys-${Date.now()}`,
              role: 'assistant',
              content: '✅ Your itinerary has been saved to your account!',
              timestamp: new Date(),
              agentSource: 'system'
            }])
          } else {
            throw new Error('Backend save failed')
          }
        } catch (backendError) {
          console.error('Backend save failed, queuing for sync:', backendError)
          // Queue for sync when back online
          syncManager.addPendingSave({
            id: message.id,
            data: {
              destination: itinerary?.destination || 'Unknown',
              summary: itinerary?.summary || '',
              itinerary_data: itinerary || {},
              creative_assets: message.creativeData || {},
              media_task_id: message.creativeData?.task_id
            }
          })
          setMessages(prev => [...prev, {
            id: `sys-${Date.now()}`,
            role: 'assistant',
            content: '💾 Saved offline. Will sync when connection is restored.',
            timestamp: new Date(),
            agentSource: 'system'
          }])
        }
      } else {
        // Offline - queue for sync
        syncManager.addPendingSave({
          id: message.id,
          data: {
            destination: itinerary?.destination || 'Unknown',
            summary: itinerary?.summary || '',
            itinerary_data: itinerary || {},
            creative_assets: message.creativeData || {},
            media_task_id: message.creativeData?.task_id
          }
        })
        setMessages(prev => [...prev, {
          id: `sys-${Date.now()}`,
          role: 'assistant',
          content: '💾 Saved offline. Will sync when you\'re back online.',
          timestamp: new Date(),
          agentSource: 'system'
        }])
      }
    } catch (e) {
      console.error('Save failed:', e)
      setMessages(prev => [...prev, {
        id: `sys-${Date.now()}`,
        role: 'assistant',
        content: '❌ Failed to save itinerary. Please try again.',
        timestamp: new Date(),
        agentSource: 'system'
      }])
    }
  }

  // Refs
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    if ((!inputValue.trim() && !selectedFile) || isLoading) return

    let uploadedUrl = ''

    // 1. Handle File Upload if present
    if (selectedFile) {
      try {
        const formData = new FormData()
        formData.append('file', selectedFile)

        const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/upload`, {
          method: 'POST',
          body: formData
        })

        if (uploadRes.ok) {
          const data = await uploadRes.json()
          uploadedUrl = data.url
        } else {
          console.error("Upload failed")
        }
      } catch (e) {
        console.error("Upload error", e)
      }
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
      uploadedImage: uploadedUrl
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setSelectedFile(null)
    setIsLoading(true)


    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Important for Cookies
        body: JSON.stringify({
          message: inputValue,
          preferences: {
            ...preferences,
            dietary: panelPrefs.dietary,
            budget_per_day_usd: panelPrefs.budget,
            trip_type: panelPrefs.tripType,
            companion_type: panelPrefs.companionType || undefined,
            travel_dates: panelPrefs.startDate && panelPrefs.endDate
              ? { start: panelPrefs.startDate, end: panelPrefs.endDate }
              : undefined,
            existing_itinerary: latestItinerary || undefined,  // Pass context for chatbot
          },
          uploaded_file: uploadedUrl || undefined
        })
      })

      if (!res.ok) throw new Error('API request failed')

      const response: AgentResponse = await res.json()

      // Handle chatbot optimization updates
      if (response.type === 'optimization_update') {
        setNotification('✅ Your itinerary has been updated based on your request!')
        setTimeout(() => setNotification(''), 5000)  // Clear notification after 5s
      }

      // Track latest itinerary for context in follow-up messages
      if (response.data?.itinerary) {
        setLatestItinerary(response.data.itinerary)
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message || 'I received your request.',
        timestamp: new Date(),
        agentSource: response.agent,
        itineraryData: response.data?.itinerary,
        creativeData: response.creative
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
        content: "We're having trouble reaching our travel experts right now. Please try again in a moment.",
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
      <section className="relative overflow-hidden border-b border-white/10 bg-gradient-to-br from-[#0f0f23] via-[#1a1035] to-[#0f1a23]">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-7xl font-mono font-bold mb-6 text-white text-stroke">
              PLAN YOUR
              <span className="block bg-black/60 backdrop-blur-sm text-brutal-yellow px-4 py-2 mt-2 inline-block rotate-brutal border border-yellow-500/20">
                PERFECT TRIP
              </span>
            </h1>
            <p className="text-xl md:text-2xl font-mono mb-8 max-w-2xl mx-auto text-white/70">
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
            <span className="bg-black/60 backdrop-blur-sm px-4 py-2 border border-brutal-orange/40 text-brutal-orange" style={{boxShadow:'0 0 16px rgba(0,212,255,0.2)'}}>
              FEATURES
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Feature 1 */}
            <div className="card-brutal border-glow-yellow rotate-brutal hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🍽️</div>
              <h3 className="text-xl font-mono font-bold mb-2 text-brutal-yellow">Dietary Aware</h3>
              <p className="text-white/70">
                Respects your dietary restrictions - vegetarian, vegan, halal,
                kosher, and allergen-free options.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card-brutal border-glow-green rotate-brutal-reverse hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-mono font-bold mb-2 text-brutal-green">Trend Analysis</h3>
              <p className="text-white/70">
                Discovers trending destinations and hidden gems from social
                media and travel communities.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card-brutal border-glow-pink rotate-brutal hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🗺️</div>
              <h3 className="text-xl font-mono font-bold mb-2 text-brutal-purple">Smart Routing</h3>
              <p className="text-white/70">
                Optimizes your daily itinerary to minimize travel time and
                maximize experiences.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="card-brutal border-glow-orange rotate-brutal-reverse hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🏨</div>
              <h3 className="text-xl font-mono font-bold mb-2 text-brutal-orange">Curated Stays</h3>
              <p className="text-white/70">
                Finds accommodations that match your budget and preferences
                with verified reviews.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="card-brutal border-glow-pink rotate-brutal hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-mono font-bold mb-2 text-brutal-pink">AI Agents</h3>
              <p className="text-white/70">
                Five specialized AI agents work together to create your
                perfect travel experience.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="card-brutal border-glow-orange rotate-brutal-reverse hover:rotate-0 transition-transform">
              <div className="text-4xl mb-4">📅</div>
              <h3 className="text-xl font-mono font-bold mb-2 text-brutal-orange">Dynamic Planning</h3>
              <p className="text-white/70">
                Generates day-by-day itineraries that adapt to weather,
                crowds, and your energy levels.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Chat Section */}
      <section id="chat" className="py-16 md:py-24 bg-black/60">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-mono font-bold text-center mb-12">
            <span className="bg-black/60 backdrop-blur-sm px-4 py-2 border border-brutal-yellow/40 text-brutal-yellow" style={{boxShadow:'0 0 16px rgba(255,225,53,0.2)'}}>
              START PLANNING
            </span>
          </h2>

          {/* Chat Interface */}
          <div className="max-w-4xl mx-auto">
            <PreferencePanel value={panelPrefs} onChange={setPanelPrefs} />

            {/* Notification Banner */}
            {notification && (
              <div className="mb-4 p-4 rounded-2xl bg-brutal-green/10 border border-brutal-green/30 backdrop-blur-xl animate-slide-up" style={{boxShadow: '0 0 12px rgba(0,255,133,0.2)'}}>
                <p className="font-mono text-sm text-white text-center">{notification}</p>
              </div>
            )}

            <div className="card-brutal p-0 overflow-hidden">
              {/* Chat Header */}
              <div className="bg-black/50 border-b border-white/10 p-4 flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${currentUser ? 'bg-brutal-green' : 'bg-red-500'}`} style={{boxShadow: currentUser ? '0 0 6px #00FF85' : '0 0 6px #FF4757'}}></div>
                <span className="font-mono font-bold text-white">AI Travel Assistant</span>

                <div className="ml-auto flex items-center gap-4">
                  <span className="text-sm font-mono text-white/40 hidden md:inline">
                    {preferences.destination && `Destination: ${preferences.destination}`}
                  </span>
                  {currentUser ? (
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-bold text-white/90 border-b border-white/30">{currentUser.full_name || currentUser.email}</span>
                      <button
                        onClick={async () => {
                          await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/logout`, { method: 'POST', credentials: 'include' });
                          setCurrentUser(null);
                          signOut({ redirect: false });
                        }}
                        className="text-xs font-mono text-white/60 hover:text-red-400 underline"
                      >
                        LOGOUT
                      </button>
                      <button
                        onClick={async () => {
                          if (!window.confirm('Delete your account and all saved itineraries? This cannot be undone.')) return
                          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/account`, { method: 'DELETE', credentials: 'include' })
                          if (res.ok) {
                            setCurrentUser(null)
                            signOut({ redirect: false })
                          }
                        }}
                        className="text-xs font-mono text-red-400 hover:text-red-300 underline"
                      >
                        DELETE
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setAuthModalOpen(true)}
                      className="btn-brutal px-2 py-1 text-xs border-glow-orange"
                    >
                      LOGIN
                    </button>
                  )}
                </div>
              </div>

              {/* Messages Container */}
              <div
                ref={chatContainerRef}
                className="h-[400px] overflow-y-auto p-4 space-y-4 bg-black/40 scrollbar-hide"
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
                        <div className="badge-brutal border-glow-orange mb-2 text-xs text-brutal-orange">
                          {message.agentSource}
                        </div>
                      )}
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <span className="text-xs opacity-50 mt-2 block" suppressHydrationWarning>
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {message.uploadedImage && (
                        <div className="mt-2">
                          <img src={message.uploadedImage} alt="Uploaded" className="max-h-48 rounded border border-white/20" />
                        </div>
                      )}

                      {message.creativeData && (
                        <div className="mt-4 w-full space-y-4">
                          {message.creativeData.poster_url && (
                            <div className="card-brutal p-2">
                              <p className="font-bold font-mono mb-1 text-brutal-pink">🎬 Trip Poster</p>
                              <img src={message.creativeData.poster_url} alt="Trip Poster" className="w-full rounded" />
                            </div>
                          )}
                          {message.creativeData.video_url && (
                            <div className="card-brutal p-2">
                              <p className="font-bold font-mono mb-1 text-brutal-purple">🎥 Teaser Trailer</p>
                              <video controls src={message.creativeData.video_url} className="w-full rounded" />
                            </div>
                          )}
                        </div>
                      )}

                      {message.itineraryData && (
                        <div className="mt-4 w-full">
                          <ItineraryView
                            itinerary={message.itineraryData.daily_itinerary || message.itineraryData.itinerary}
                            summary={message.itineraryData}
                          />
                          {!savedIds.has(message.id) && (
                            <button
                              onClick={() => savePlan(message)}
                              className="btn-brutal-green mt-3 text-sm"
                            >
                              💾 Save This Plan
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                  <div className="animate-slide-up">
                    <LoadingExperience />
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t border-white/10 p-4 bg-black/50">
                <div className="flex flex-col gap-2">
                  {selectedFile && (
                    <div className="text-xs bg-black/60 text-brutal-yellow p-1 border border-brutal-yellow/30 inline-block self-start">
                      📎 {selectedFile.name}
                      <button onClick={() => setSelectedFile(null)} className="ml-2 text-red-400 font-bold">X</button>
                    </div>
                  )}
                  <div className="flex gap-3">
                    <input
                      type="file"
                      ref={fileInputRef}
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files?.[0]) setSelectedFile(e.target.files[0])
                      }}
                      accept="image/*"
                    />
                    <button
                      className="btn-brutal px-3"
                      onClick={() => fileInputRef.current?.click()}
                      title="Upload Image"
                    >
                      📎
                    </button>
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={!isOnline ? "You're offline - chat unavailable" : "Tell me about your dream trip..."}
                      className="input-brutal flex-1"
                      disabled={isLoading || !isOnline}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={isLoading || !isOnline || (!inputValue.trim() && !selectedFile)}
                      className="btn-brutal-green disabled:opacity-50 disabled:cursor-not-allowed"
                      title={!isOnline ? "Chat unavailable offline" : "Send message"}
                    >
                      {isLoading ? '...' : !isOnline ? '📡' : 'SEND'}
                    </button>
                  </div>
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
                      className="badge-brutal cursor-pointer hover:bg-white/10 transition-colors text-white/60 hover:text-white"
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
            <span className="bg-black/60 backdrop-blur-sm px-4 py-2 border border-brutal-green/40 text-brutal-green" style={{boxShadow:'0 0 16px rgba(0,255,133,0.2)'}}>
              HOW IT WORKS
            </span>
          </h2>

          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {/* Step 1 */}
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 bg-black/60 backdrop-blur-sm border border-brutal-yellow/40 flex items-center justify-center font-mono font-bold text-2xl shrink-0 text-brutal-yellow" style={{boxShadow:'0 0 12px rgba(255,225,53,0.25)'}}>
                  1
                </div>
                <div className="card-brutal flex-1">
                  <h3 className="text-xl font-mono font-bold mb-2 text-brutal-yellow">Share Your Preferences</h3>
                  <p className="text-white/70">
                    Tell us about your dietary restrictions, travel style, budget,
                    and interests. Our Profiler Agent captures everything.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 bg-black/60 backdrop-blur-sm border border-brutal-pink/40 flex items-center justify-center font-mono font-bold text-2xl shrink-0 text-brutal-pink" style={{boxShadow:'0 0 12px rgba(255,107,157,0.25)'}}>
                  2
                </div>
                <div className="card-brutal flex-1">
                  <h3 className="text-xl font-mono font-bold mb-2 text-brutal-pink">AI Agents Collaborate</h3>
                  <p className="text-white/70">
                    Five specialized agents work together - analyzing trends,
                    finding destinations, filtering restaurants, and more.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 bg-black/60 backdrop-blur-sm border border-brutal-orange/40 flex items-center justify-center font-mono font-bold text-2xl shrink-0 text-brutal-orange" style={{boxShadow:'0 0 12px rgba(0,212,255,0.25)'}}>
                  3
                </div>
                <div className="card-brutal flex-1">
                  <h3 className="text-xl font-mono font-bold mb-2 text-brutal-orange">Get Your Perfect Plan</h3>
                  <p className="text-white/70">
                    Receive a personalized, day-by-day itinerary optimized for
                    your preferences, with all dietary needs respected.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Auth Modal */}
      {authModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="card-brutal max-w-md w-full animate-slide-up relative bg-[rgba(20,20,40,0.92)]">
            <button
              onClick={() => setAuthModalOpen(false)}
              className="absolute top-2 right-2 text-xl font-bold text-white/60 hover:text-brutal-pink"
            >
              ✕
            </button>
            <h2 className="text-2xl font-mono font-bold mb-6 text-center text-white">
              {isLoginMode ? 'WELCOME BACK' : 'JOIN THE TRIP'}
            </h2>

            <form onSubmit={handleAuth} className="space-y-4">
              {!isLoginMode && (
                <div>
                  <label className="block font-mono font-bold text-sm mb-1 text-white/70">FULL NAME</label>
                  <input
                    type="text"
                    required={!isLoginMode}
                    value={authName}
                    onChange={e => setAuthName(e.target.value)}
                    className="input-brutal w-full"
                    placeholder="John Doe"
                  />
                </div>
              )}

              <div>
                <label className="block font-mono font-bold text-sm mb-1 text-white/70">EMAIL</label>
                <input
                  type="email"
                  required
                  value={authEmail}
                  onChange={e => setAuthEmail(e.target.value)}
                  className="input-brutal w-full"
                  placeholder="traveler@example.com"
                />
              </div>

              <div>
                <label className="block font-mono font-bold text-sm mb-1 text-white/70">PASSWORD</label>
                <input
                  type="password"
                  required
                  value={authPassword}
                  onChange={e => setAuthPassword(e.target.value)}
                  className="input-brutal w-full"
                  placeholder="••••••••"
                />
              </div>

              {authError && (
                <div className="bg-red-900/30 border border-red-500/50 text-red-400 p-2 font-mono text-xs">
                  {authError}
                </div>
              )}

              <button type="submit" className="btn-brutal-yellow w-full">
                {isLoginMode ? 'LOGIN' : 'REGISTER'}
              </button>
            </form>

            <div className="my-6 flex items-center gap-2 opacity-40">
              <div className="h-px bg-white flex-1"></div>
              <span className="font-mono text-xs text-white">OR</span>
              <div className="h-px bg-white flex-1"></div>
            </div>

            <button
              onClick={() => signIn('google')}
              className="btn-brutal w-full flex items-center justify-center gap-2 border-glow-orange"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
              </svg>
              Sign in with Google
            </button>

            <div className="mt-4 text-center">
              <button
                onClick={() => setIsLoginMode(!isLoginMode)}
                className="text-sm font-mono underline text-white/60 hover:text-brutal-pink"
              >
                {isLoginMode ? 'Need an account? Register' : 'Already have an account? Login'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
