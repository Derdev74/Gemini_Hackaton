/**
 * Offline Page - Fallback page when navigating while offline
 * Shows friendly message and link to saved itineraries
 */

'use client'

export default function OfflinePage() {
  const handleRetry = () => {
    window.location.reload()
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="card-brutal bg-brutal-dark/80 backdrop-blur-xl border-brutal-orange p-12 text-center max-w-md shadow-glow-orange">
        {/* Airplane Icon */}
        <div className="text-8xl mb-8 animate-bounce">✈️</div>

        {/* Title */}
        <h1 className="text-4xl font-black text-brutal-orange mb-4 uppercase tracking-wider">
          You're Offline
        </h1>

        {/* Message */}
        <p className="text-brutal-text/80 text-lg mb-8">
          No internet connection detected. Your saved itineraries are still available!
        </p>

        {/* Actions */}
        <div className="flex flex-col gap-4">
          <button
            onClick={handleRetry}
            className="btn-brutal bg-brutal-orange text-white px-6 py-3 text-lg font-bold hover:scale-105 transition-transform"
          >
            TRY AGAIN
          </button>

          <a
            href="/my-itineraries"
            className="btn-brutal bg-brutal-dark border-brutal-orange text-brutal-orange px-6 py-3 text-lg font-bold hover:scale-105 transition-transform"
          >
            VIEW SAVED TRIPS
          </a>

          <a
            href="/"
            className="text-brutal-text/60 hover:text-brutal-orange transition-colors mt-2"
          >
            Go to Home
          </a>
        </div>
      </div>
    </div>
  )
}
